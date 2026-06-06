from datetime import datetime, timezone

from cachetools import TTLCache, cachedmethod
from google.cloud import bigquery


ALLOWED_COLUMNS = {
    "timestamp",
    "level",
    "service",
    "component",
    "block_id",
    "node_id",
    "error_code",
    "hour",
    "message",
    "source_file",
}


class AnalyticsService:
    def __init__(self, repository, config):
        self.repository = repository
        self.config = config
        self.cache = TTLCache(maxsize=32, ttl=config.CACHE_TTL_SECONDS)

    @property
    def table(self):
        return f"`{self.config.PROJECT_ID}.{self.config.BQ_DATASET}.{self.config.BQ_TABLE}`"

    @cachedmethod(lambda self: self.cache)
    def overview(self):
        sql = f"""
        WITH base AS (
          SELECT level, component, node_id, error_code, hour
          FROM {self.table}
        )
        SELECT
          COUNT(*) AS total_logs,
          COUNT(DISTINCT NULLIF(component, '')) AS total_components,
          COUNT(DISTINCT NULLIF(node_id, '')) AS total_nodes,
          COUNT(DISTINCT NULLIF(error_code, '')) AS total_error_codes,
          COUNTIF(UPPER(level) IN ('ERROR', 'FATAL', 'CRITICAL')) AS failure_logs,
          COUNTIF(UPPER(level) IN ('WARN', 'WARNING')) AS warning_logs,
          SAFE_DIVIDE(
            COUNTIF(UPPER(level) IN ('ERROR', 'FATAL', 'CRITICAL')),
            COUNT(*)
          ) * 100 AS error_density
        FROM base
        """
        result = self.repository.query(sql)
        metrics = result["rows"][0] if result["rows"] else {}
        total = metrics.get("total_logs") or self.config.PROCESSED_RECORDS
        error_density = float(metrics.get("error_density") or 0)
        metrics.update(
            {
                "total_logs": total,
                "dataproc_workers": self.config.DATAPROC_WORKERS,
                "processing_duration": self.config.SPARK_PROCESSING_DURATION,
                "last_spark_job_status": self.config.SPARK_JOB_STATUS,
                "system_stability_index": max(0, round(100 - error_density, 2)),
                "processing_efficiency": round(total / max(self.config.DATAPROC_WORKERS, 1), 0),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        try:
            table = self.repository.table_metadata(self.config.BQ_DATASET, self.config.BQ_TABLE)
            metrics["bigquery_table_size_bytes"] = table.num_bytes or 0
            metrics["bigquery_rows"] = table.num_rows or total
        except Exception:
            metrics["bigquery_table_size_bytes"] = None
            metrics["bigquery_rows"] = total
        return {"metrics": metrics, "query": result}

    @cachedmethod(lambda self: self.cache)
    def dashboard_charts(self):
        queries = {
            "hourly_activity": f"""
                SELECT hour, COUNT(*) AS logs,
                  COUNTIF(UPPER(level) IN ('ERROR','FATAL','CRITICAL')) AS failures
                FROM {self.table}
                WHERE hour IS NOT NULL
                GROUP BY hour ORDER BY hour
            """,
            "levels": f"""
                SELECT COALESCE(NULLIF(UPPER(level), ''), 'UNKNOWN') AS name, COUNT(*) AS value
                FROM {self.table} GROUP BY name ORDER BY value DESC
            """,
            "components": f"""
                SELECT COALESCE(NULLIF(component, ''), 'unknown') AS name, COUNT(*) AS value,
                  COUNTIF(UPPER(level) IN ('ERROR','FATAL','CRITICAL')) AS failures
                FROM {self.table}
                GROUP BY name ORDER BY value DESC LIMIT 12
            """,
            "nodes": f"""
                SELECT COALESCE(NULLIF(node_id, ''), 'unknown') AS name, COUNT(*) AS value
                FROM {self.table}
                GROUP BY name ORDER BY value DESC LIMIT 12
            """,
            "error_codes": f"""
                SELECT COALESCE(NULLIF(error_code, ''), 'unclassified') AS name, COUNT(*) AS value
                FROM {self.table}
                WHERE NULLIF(error_code, '') IS NOT NULL
                GROUP BY name ORDER BY value DESC LIMIT 12
            """,
        }
        return {name: self.repository.query(sql)["rows"] for name, sql in queries.items()}

    @cachedmethod(lambda self: self.cache)
    def anomalies(self):
        sql = f"""
        WITH component_hour AS (
          SELECT component, hour, node_id, error_code, COUNT(*) AS event_count
          FROM {self.table}
          GROUP BY component, hour, node_id, error_code
        ),
        scored AS (
          SELECT *,
            AVG(event_count) OVER() AS mean_count,
            STDDEV_POP(event_count) OVER() AS stddev_count
          FROM component_hour
        )
        SELECT component, hour, node_id, error_code, event_count,
          ROUND(SAFE_DIVIDE(event_count - mean_count, NULLIF(stddev_count, 0)), 3) AS anomaly_score,
          CASE
            WHEN SAFE_DIVIDE(event_count - mean_count, NULLIF(stddev_count, 0)) >= 4 THEN 'critical'
            WHEN SAFE_DIVIDE(event_count - mean_count, NULLIF(stddev_count, 0)) >= 3 THEN 'high'
            ELSE 'medium'
          END AS severity
        FROM scored
        WHERE SAFE_DIVIDE(event_count - mean_count, NULLIF(stddev_count, 0)) >= 2
        ORDER BY anomaly_score DESC
        LIMIT 500
        """
        rows = self.repository.query(sql)["rows"]
        scores = [float(row.get("anomaly_score") or 0) for row in rows]
        return {
            "summary": {
                "anomaly_count": len(rows),
                "risk_score": min(100, round(max(scores, default=0) * 20, 1)),
                "critical": sum(1 for row in rows if row.get("severity") == "critical"),
                "high": sum(1 for row in rows if row.get("severity") == "high"),
            },
            "items": rows,
        }

    def explore(self, args):
        page = max(int(args.get("page", 1)), 1)
        page_size = min(max(int(args.get("page_size", 50)), 1), 250)
        sort_by = args.get("sort_by", "timestamp")
        sort_direction = "ASC" if args.get("sort_direction", "desc").lower() == "asc" else "DESC"
        if sort_by not in ALLOWED_COLUMNS:
            sort_by = "timestamp"

        filters = []
        parameters = []
        for field in ("component", "node_id", "error_code", "level"):
            value = args.get(field)
            if value:
                filters.append(f"{field} = @{field}")
                parameters.append(bigquery.ScalarQueryParameter(field, "STRING", value))
        if args.get("hour"):
            filters.append("hour = @hour")
            parameters.append(bigquery.ScalarQueryParameter("hour", "INT64", int(args["hour"])))
        if args.get("search"):
            filters.append("LOWER(message) LIKE @search")
            parameters.append(bigquery.ScalarQueryParameter("search", "STRING", f"%{args['search'].lower()}%"))

        where = f"WHERE {' AND '.join(filters)}" if filters else ""
        offset = (page - 1) * page_size
        sql = f"""
          SELECT timestamp, level, service, component, block_id, node_id,
                 error_code, hour, message, source_file
          FROM {self.table}
          {where}
          ORDER BY {sort_by} {sort_direction}
          LIMIT {page_size} OFFSET {offset}
        """
        count_sql = f"SELECT COUNT(*) AS total FROM {self.table} {where}"
        rows = self.repository.query(sql, parameters)["rows"]
        total = self.repository.query(count_sql, parameters)["rows"][0]["total"]
        return {"items": rows, "page": page, "page_size": page_size, "total": total}

    @cachedmethod(lambda self: self.cache)
    def filter_options(self):
        sql = f"""
        SELECT
          ARRAY_AGG(DISTINCT component IGNORE NULLS LIMIT 100) AS components,
          ARRAY_AGG(DISTINCT node_id IGNORE NULLS LIMIT 100) AS nodes,
          ARRAY_AGG(DISTINCT error_code IGNORE NULLS LIMIT 100) AS error_codes,
          ARRAY_AGG(DISTINCT level IGNORE NULLS LIMIT 20) AS levels
        FROM {self.table}
        """
        rows = self.repository.query(sql)["rows"]
        return rows[0] if rows else {}

    @cachedmethod(lambda self: self.cache)
    def infrastructure(self):
        tables = []
        try:
            for item in self.repository.list_tables(self.config.BQ_DATASET):
                metadata = self.repository.table_metadata(self.config.BQ_DATASET, item.table_id)
                tables.append(
                    {
                        "name": item.table_id,
                        "rows": metadata.num_rows,
                        "bytes": metadata.num_bytes,
                    }
                )
        except Exception:
            tables = []
        try:
            dataproc = self.repository.dataproc_cluster(self.config.REGION, self.config.CLUSTER_NAME)
            jobs = self.repository.dataproc_jobs(self.config.REGION)
        except Exception:
            dataproc = {
                "cluster_name": self.config.CLUSTER_NAME,
                "status": self.config.SPARK_JOB_STATUS,
                "region": self.config.REGION,
                "worker_count": self.config.DATAPROC_WORKERS,
                "machine_type": self.config.DATAPROC_MACHINE_TYPE,
            }
            jobs = []

        storage_info = []
        for bucket_name in (self.config.RAW_BUCKET, self.config.OUTPUT_BUCKET):
            try:
                storage_info.append(self.repository.bucket_metadata(bucket_name))
            except Exception:
                storage_info.append({"name": bucket_name, "bytes": None, "objects": None})

        return {
            "dataproc": dataproc,
            "storage": {"buckets": storage_info},
            "bigquery": {
                "dataset": self.config.BQ_DATASET,
                "tables": tables,
            },
            "processing": {
                "last_job": self.config.SPARK_JOB_STATUS,
                "duration": self.config.SPARK_PROCESSING_DURATION,
                "records_processed": self.config.PROCESSED_RECORDS,
                "job_history": jobs,
            },
        }
