from google.cloud import bigquery
from google.cloud import dataproc_v1
from google.cloud import storage


class BigQueryRepository:
    def __init__(self, project_id):
        self.project_id = project_id
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = bigquery.Client(project=self.project_id)
        return self._client

    def query(self, sql, parameters=None, maximum_bytes_billed=None):
        config = bigquery.QueryJobConfig()
        if parameters:
            config.query_parameters = parameters
        if maximum_bytes_billed:
            config.maximum_bytes_billed = maximum_bytes_billed
        job = self.client.query(sql, job_config=config)
        rows = job.result()
        return {
            "rows": [dict(row.items()) for row in rows],
            "job_id": job.job_id,
            "total_bytes_processed": job.total_bytes_processed or 0,
            "total_bytes_billed": job.total_bytes_billed or 0,
            "cache_hit": bool(job.cache_hit),
        }

    def table_metadata(self, dataset, table):
        return self.client.get_table(f"{self.project_id}.{dataset}.{table}")

    def list_tables(self, dataset):
        return list(self.client.list_tables(f"{self.project_id}.{dataset}"))

    def bucket_metadata(self, bucket_name):
        client = storage.Client(project=self.project_id)
        blobs = list(client.list_blobs(bucket_name))
        return {
            "name": bucket_name,
            "bytes": sum(blob.size or 0 for blob in blobs),
            "objects": len(blobs),
        }

    def dataproc_cluster(self, region, cluster_name):
        client = dataproc_v1.ClusterControllerClient(
            client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
        )
        cluster = client.get_cluster(
            request={"project_id": self.project_id, "region": region, "cluster_name": cluster_name}
        )
        workers = cluster.config.worker_config.num_instances if cluster.config.worker_config else 0
        machine_type = cluster.config.worker_config.machine_type_uri.split("/")[-1] if cluster.config.worker_config else ""
        return {
            "cluster_name": cluster.cluster_name,
            "status": dataproc_v1.ClusterStatus.State(cluster.status.state).name,
            "region": region,
            "worker_count": workers,
            "machine_type": machine_type,
        }

    def dataproc_jobs(self, region, limit=10):
        client = dataproc_v1.JobControllerClient(
            client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
        )
        jobs = client.list_jobs(request={"project_id": self.project_id, "region": region})
        result = []
        for job in jobs:
            result.append(
                {
                    "job_id": job.reference.job_id,
                    "status": dataproc_v1.JobStatus.State(job.status.state).name,
                    "driver_output_uri": job.driver_output_resource_uri,
                }
            )
            if len(result) >= limit:
                break
        return result
