import re
import time
from collections import deque


BLOCKED_SQL = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|MERGE|TRUNCATE|GRANT|REVOKE|CALL|EXPORT)\b", re.I)


class QueryService:
    def __init__(self, repository, config):
        self.repository = repository
        self.config = config
        self.history = deque(maxlen=25)

    def validate(self, sql):
        normalized = sql.strip().rstrip(";").strip()
        if not normalized:
            raise ValueError("Query is empty")
        if ";" in normalized:
            raise ValueError("Only one SELECT statement is allowed")
        if not re.match(r"^(SELECT|WITH)\b", normalized, re.I):
            raise ValueError("Only SELECT queries are allowed")
        if BLOCKED_SQL.search(normalized):
            raise ValueError("Mutating or administrative SQL is blocked")
        return normalized

    def execute(self, sql):
        normalized = self.validate(sql)
        limited = f"SELECT * FROM ({normalized}) LIMIT {self.config.MAX_QUERY_ROWS}"
        started = time.perf_counter()
        result = self.repository.query(limited, maximum_bytes_billed=10 * 1024**3)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        item = {
            "sql": normalized,
            "duration_ms": duration_ms,
            "returned_rows": len(result["rows"]),
            "job_id": result["job_id"],
            "bytes_processed": result["total_bytes_processed"],
            "cache_hit": result["cache_hit"],
        }
        self.history.appendleft(item)
        return {**item, "rows": result["rows"]}
