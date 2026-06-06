# Windows Quick Start

Use [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md) for the current Windows-compatible deployment commands.

The final workflow is:

1. Build the Docker image.
2. Place the full HDFS dataset at `dataset/HDFS_full/HDFS.log`.
3. Run `deployment/prepare_large_dataset.py` inside Docker to validate and upload the dataset.
4. Upload `batch_processing/spark_job.py` to GCS.
5. Run the PySpark job on Dataproc.
6. Verify GCS, BigQuery, and Looker Studio outputs.
7. Run the Dockerized Flask API and React observability platform on Compute Engine.

This project uses large-scale batch processing only.
