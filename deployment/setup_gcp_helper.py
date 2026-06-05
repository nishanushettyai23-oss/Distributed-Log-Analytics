"""
Batch-only GCP setup helper.

The detailed deployment commands live in docs/GCP_DEPLOYMENT_GUIDE.md. This
helper prints the final execution sequence so older entry points no longer
point to obsolete ingestion steps.
"""


def main():
    project_id = input("Enter GCP Project ID [distributed-log-analytics]: ").strip()
    if not project_id:
        project_id = "distributed-log-analytics"

    print(
        f"""
GCP setup path for {project_id}

1. Build the Docker image:
   docker build -t distributed-log-analytics:latest .

2. Place the full HDFS dataset at:
   dataset/HDFS_full/HDFS.log

3. Validate and upload the large dataset:
   python deployment/prepare_large_dataset.py \\
     --local-path dataset/HDFS_full/HDFS.log \\
     --gcs-path gs://{project_id}-raw-logs/loghub/hdfs/full/HDFS.log

4. Upload the Dataproc Spark job:
   gsutil cp batch_processing/spark_job.py gs://{project_id}-spark-code/jobs/spark_job.py

5. Create the Dataproc cluster, submit the Spark job, and verify BigQuery:
   docs/GCP_DEPLOYMENT_GUIDE.md
"""
    )


if __name__ == "__main__":
    main()
