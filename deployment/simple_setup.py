"""
Simple setup pointer for the final large batch GCP deployment.
"""


def main():
    project_id = input("Enter GCP Project ID [distributed-log-analytics]: ").strip()
    if not project_id:
        project_id = "distributed-log-analytics"

    print(
        f"""
Use docs/GCP_DEPLOYMENT_GUIDE.md for the complete command sequence.

Project ID: {project_id}

Required flow:
1. docker build -t distributed-log-analytics:latest .
2. Put the full HDFS dataset at dataset/HDFS_full/HDFS.log
3. python deployment/prepare_large_dataset.py --local-path dataset/HDFS_full/HDFS.log --gcs-path gs://{project_id}-raw-logs/loghub/hdfs/full/HDFS.log
4. gsutil cp batch_processing/spark_job.py gs://{project_id}-spark-code/jobs/spark_job.py
5. Submit the Dataproc job from docs/GCP_DEPLOYMENT_GUIDE.md
"""
    )


if __name__ == "__main__":
    main()
