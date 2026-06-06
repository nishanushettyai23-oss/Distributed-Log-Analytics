# Distributed Log Analytics and Anomaly Detection on GCP

## Description

This project analyzes the LogHub HDFS dataset using Apache Spark on Google Cloud Dataproc. More than 10.6 million processed records are stored in BigQuery and exposed through a modular Flask REST API to a React/TypeScript enterprise observability platform.

This project uses large-scale batch processing only.

## Architecture

```text
Large LogHub HDFS Dataset
        |
        v
Docker Dataset Prep Tool
        |
        v
Google Cloud Storage
        |
        v
Dataproc Apache Spark
        |
        v
Spark Feature Extraction and Anomaly Detection
        |
        +----------------------+
        |                      |
        v                      v
GCS Parquet Output       BigQuery Warehouse
                               |
                               v
                        Flask REST API
                               |
                               v
                   React Observability Platform
```

## Main Components

- `batch_processing/spark_job.py`: Dataproc PySpark job for parsing, feature extraction, analytics, anomaly detection, GCS output, and BigQuery writes.
- `deployment/prepare_large_dataset.py`: Docker-friendly validator/uploader for the full HDFS dataset.
- `api/`: Flask blueprints, service layer, repository layer, BigQuery analytics, read-only SQL, cloud metadata, and exports.
- `frontend/`: React, TypeScript, Tailwind, React Query, Recharts, Framer Motion, Monaco, and React Flow application.
- `docs/GCP_DEPLOYMENT_GUIDE.md`: Step-by-step GCP execution guide.
- `docs/GCP_CLOUD_EXECUTION_PLAN.md`: Report outline aligned with the cloud deployment rubric.

## Dataset

The final demo should use the full LogHub HDFS dataset stored locally at:

```text
dataset/HDFS_full/HDFS.log
```

This large dataset is ignored by Git and should be uploaded to:

```text
gs://distributed-log-analytics-raw-logs/loghub/hdfs/full/HDFS.log
```

The included `dataset/HDFS_2k/HDFS_2k.log` file is only for quick smoke testing.

## Docker Quick Start

Build and run both production containers:

```bash
docker compose up --build
```

Open:

```text
http://localhost:3000
```

Validate a small smoke-test dataset without upload:

```bash
docker run --rm -v "$PWD:/app" distributed-log-analytics-api:latest \
  python deployment/prepare_large_dataset.py \
  --local-path dataset/HDFS_2k/HDFS_2k.log \
  --gcs-path gs://distributed-log-analytics-raw-logs/loghub/hdfs/smoke/HDFS_2k.log \
  --allow-small \
  --skip-upload
```

## GCP Execution Summary

1. Download the full LogHub HDFS dataset to `dataset/HDFS_full/HDFS.log`.
2. Build the Docker image.
3. Use the Docker dataset prep tool to validate and upload the large dataset to GCS.
4. Upload `batch_processing/spark_job.py` to the GCS code bucket.
5. Create a Dataproc cluster with 1 master and 2 workers.
6. Submit the PySpark job on Dataproc.
7. Verify output in GCS and BigQuery.
8. Build Looker Studio charts from BigQuery tables.
9. Deploy the Docker Compose API and React platform on Compute Engine.

Primary command:

```bash
gcloud dataproc jobs submit pyspark gs://distributed-log-analytics-spark-code/jobs/spark_job.py \
  --cluster=log-analytics-cluster \
  --region=us-central1 \
  --project=distributed-log-analytics \
  --properties=spark.jars.packages=com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.42.1 \
  -- \
  --input gs://distributed-log-analytics-raw-logs/loghub/hdfs/full/HDFS.log \
  --output gs://distributed-log-analytics-spark-output/results/hdfs_full \
  --project-id distributed-log-analytics \
  --bq-dataset logs_dataset \
  --output-partitions 8 \
  --write-bigquery
```

Full instructions are in [docs/GCP_DEPLOYMENT_GUIDE.md](docs/GCP_DEPLOYMENT_GUIDE.md).

## BigQuery Outputs

The Spark job writes:

- `logs_dataset.processed_logs`
- `logs_dataset.error_frequency`
- `logs_dataset.level_distribution`
- `logs_dataset.component_failures`
- `logs_dataset.temporal_analysis`
- `logs_dataset.anomalies`

## Evidence for Evaluation

Capture screenshots of:

- Docker image build.
- React executive dashboard and Flask API health.
- GCS bucket containing the full `HDFS.log`.
- Dataproc cluster with 1 master and 2 workers.
- Dataproc job details and driver logs.
- GCS processed Parquet output.
- BigQuery populated tables.
- Looker Studio dashboard.
- Compute Engine VM running the Dockerized full-stack platform.

## Application Pages

- Executive Dashboard
- Log Analytics
- Anomaly Detection
- Dataset Explorer
- BigQuery Explorer
- Infrastructure
- Architecture
- Reports

The application queries the real table `logs_dataset.processed_logs` with columns:
`timestamp`, `level`, `service`, `component`, `block_id`, `node_id`,
`error_code`, `hour`, `message`, and `source_file`.

## References

- Google Cloud Dataproc: https://cloud.google.com/dataproc/docs
- Google Cloud Storage: https://cloud.google.com/storage/docs
- BigQuery: https://cloud.google.com/bigquery/docs
- Compute Engine: https://cloud.google.com/compute/docs
- Docker: https://docs.docker.com/
- Apache Spark: https://spark.apache.org/docs/latest/
- LogHub: https://github.com/logpai/loghub
