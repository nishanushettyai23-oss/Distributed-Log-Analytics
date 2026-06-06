import os


class Config:
    PROJECT_ID = os.getenv("PROJECT_ID", "distributed-log-analytics")
    BQ_DATASET = os.getenv("BQ_DATASET", "logs_dataset")
    BQ_TABLE = os.getenv("BQ_TABLE", "processed_logs")
    REGION = os.getenv("REGION", "us-central1")
    CLUSTER_NAME = os.getenv("CLUSTER_NAME", "log-analytics-cluster")
    DATAPROC_WORKERS = int(os.getenv("DATAPROC_WORKERS", "2"))
    DATAPROC_MACHINE_TYPE = os.getenv("DATAPROC_MACHINE_TYPE", "n2-standard-2")
    RAW_BUCKET = os.getenv("RAW_BUCKET", f"{PROJECT_ID}-raw-logs")
    OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", f"{PROJECT_ID}-spark-output")
    PROCESSED_RECORDS = int(os.getenv("PROCESSED_RECORDS", "10685241"))
    SPARK_JOB_STATUS = os.getenv("SPARK_JOB_STATUS", "SUCCEEDED")
    SPARK_PROCESSING_DURATION = os.getenv("SPARK_PROCESSING_DURATION", "Not configured")
    LOOKER_STUDIO_URL = os.getenv("LOOKER_STUDIO_URL", "https://lookerstudio.google.com")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    MAX_QUERY_ROWS = int(os.getenv("MAX_QUERY_ROWS", "5000"))
    PIPELINE_ADMIN_TOKEN = os.getenv("PIPELINE_ADMIN_TOKEN", "")
    SPARK_JOB_URI = os.getenv(
        "SPARK_JOB_URI",
        f"gs://{PROJECT_ID}-spark-code/jobs/spark_job.py",
    )

    @property
    def table_ref(self):
        return f"`{self.PROJECT_ID}.{self.BQ_DATASET}.{self.BQ_TABLE}`"
