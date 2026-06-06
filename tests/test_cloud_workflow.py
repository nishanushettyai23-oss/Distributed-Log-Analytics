import unittest
from io import BytesIO
from types import SimpleNamespace

from api.services.analytics_service import AnalyticsService


class RepositoryStub:
    def __init__(self):
        self.upload = None

    def query(self, _sql, _parameters=None):
        return {
            "rows": [
                {
                    "components": [{"name": "DataNode", "value": "DataNode"}, "NameNode"],
                    "nodes": [{"value": "10.0.0.1:50010"}],
                    "error_codes": [None, "WARN"],
                    "levels": ["INFO", {"name": "ERROR"}],
                }
            ]
        }

    def submit_pyspark_job(self, region, cluster_name, main_python_file_uri, args):
        return {
            "job_id": "job-123",
            "region": region,
            "cluster_name": cluster_name,
            "status": "SUBMITTED",
            "main_python_file_uri": main_python_file_uri,
            "args": args,
        }

    def upload_dataset(self, bucket_name, object_name, stream, content_type):
        self.upload = {
            "bucket": bucket_name,
            "object": object_name,
            "content": stream.read(),
            "content_type": content_type,
        }
        return {
            "bucket": bucket_name,
            "object": object_name,
            "gcs_uri": f"gs://{bucket_name}/{object_name}",
            "size_bytes": len(self.upload["content"]),
            "generation": "123",
            "stored": True,
        }


def config():
    return SimpleNamespace(
        PROJECT_ID="distributed-log-analytics",
        BQ_DATASET="logs_dataset",
        BQ_TABLE="processed_logs",
        RAW_BUCKET="distributed-log-analytics-raw-logs",
        OUTPUT_BUCKET="distributed-log-analytics-spark-output",
        REGION="us-central1",
        CLUSTER_NAME="log-analytics-cluster",
        SPARK_JOB_URI="gs://distributed-log-analytics-spark-code/jobs/spark_job.py",
        CACHE_TTL_SECONDS=60,
        table_ref="`distributed-log-analytics.logs_dataset.processed_logs`",
    )


class CloudWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.repository = RepositoryStub()
        self.service = AnalyticsService(self.repository, config())

    def test_filter_options_are_plain_strings(self):
        options = self.service.filter_options()
        self.assertEqual(options["components"], ["DataNode", "NameNode"])
        self.assertEqual(options["nodes"], ["10.0.0.1:50010"])
        self.assertEqual(options["levels"], ["ERROR", "INFO"])

    def test_pipeline_submission_returns_cloud_identifiers(self):
        result = self.service.submit_pipeline(
            "gs://distributed-log-analytics-raw-logs/loghub/hdfs/full/HDFS.log",
            "hdfs-full",
        )
        self.assertEqual(result["job_id"], "job-123")
        self.assertEqual(
            result["output_uri"],
            "gs://distributed-log-analytics-spark-output/results/hdfs-full",
        )

    def test_pipeline_normalizes_accidental_backslashes(self):
        result = self.service.submit_pipeline(
            r"gs://distributed-log-analytics-raw-logs\loghub\hdfs\full\HDFS.log",
            "hdfs-full",
        )
        self.assertEqual(
            result["input_uri"],
            "gs://distributed-log-analytics-raw-logs/loghub/hdfs/full/HDFS.log",
        )

    def test_pipeline_rejects_objects_outside_raw_bucket(self):
        with self.assertRaises(ValueError):
            self.service.submit_pipeline("gs://another-bucket/HDFS.log", "hdfs-full")

    def test_dataset_is_stored_in_raw_bucket_before_processing(self):
        dataset = SimpleNamespace(
            filename="sample HDFS.log",
            stream=BytesIO(b"081109 203518 143 INFO dfs.DataNode: message\n"),
            mimetype="text/plain",
        )
        result = self.service.store_dataset(dataset)
        self.assertTrue(result["stored"])
        self.assertEqual(self.repository.upload["bucket"], "distributed-log-analytics-raw-logs")
        self.assertTrue(self.repository.upload["object"].endswith("/sample-HDFS.log"))
        self.assertEqual(self.repository.upload["content_type"], "text/plain")


if __name__ == "__main__":
    unittest.main()
