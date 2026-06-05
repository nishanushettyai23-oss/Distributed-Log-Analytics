# GCP Deployment Guide: Large Dataset + Docker

This project uses large-scale batch processing only.

Final architecture:

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
Dataproc Apache Spark Cluster
        |
        v
Spark Feature Extraction and Anomaly Detection
        |
        +----------------------+
        |                      |
        v                      v
GCS Parquet Output       BigQuery Analytics Tables
                               |
                               v
                        Looker Studio Dashboard

Optional evidence layer:
Compute Engine VM -> Dockerized Flask Status Page
```

## 1. Set Variables

Linux/macOS/Git Bash:

```bash
export PROJECT_ID="distributed-log-analytics"
export REGION="us-central1"
export ZONE="us-central1-a"
export CLUSTER_NAME="log-analytics-cluster"
export RAW_BUCKET="${PROJECT_ID}-raw-logs"
export CODE_BUCKET="${PROJECT_ID}-spark-code"
export OUTPUT_BUCKET="${PROJECT_ID}-spark-output"
export BQ_DATASET="logs_dataset"
export IMAGE_NAME="distributed-log-analytics:latest"
export LARGE_LOCAL_PATH="dataset/HDFS_full/HDFS.log"
export LARGE_GCS_PATH="gs://${RAW_BUCKET}/loghub/hdfs/full/HDFS.log"
```

Windows PowerShell:

```powershell
$env:PROJECT_ID="distributed-log-analytics"
$env:REGION="us-central1"
$env:ZONE="us-central1-a"
$env:CLUSTER_NAME="log-analytics-cluster"
$env:RAW_BUCKET="$env:PROJECT_ID-raw-logs"
$env:CODE_BUCKET="$env:PROJECT_ID-spark-code"
$env:OUTPUT_BUCKET="$env:PROJECT_ID-spark-output"
$env:BQ_DATASET="logs_dataset"
$env:IMAGE_NAME="distributed-log-analytics:latest"
$env:LARGE_LOCAL_PATH="dataset/HDFS_full/HDFS.log"
$env:LARGE_GCS_PATH="gs://$env:RAW_BUCKET/loghub/hdfs/full/HDFS.log"
```

## 2. Prepare the Large Dataset

Download the full LogHub HDFS dataset and place it at:

```text
dataset/HDFS_full/HDFS.log
```

Keep this file out of Git. The repository ignores `dataset/HDFS_full/`.

Use the small included dataset only for a quick smoke test:

```text
dataset/HDFS_2k/HDFS_2k.log
```

## 3. Build Docker Image

```bash
docker build -t distributed-log-analytics:latest .
```

Run the status page locally:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8080
```

Screenshot this page for Docker evidence.

## 4. Enable GCP APIs

```bash
gcloud config set project $PROJECT_ID
gcloud services enable dataproc.googleapis.com storage.googleapis.com bigquery.googleapis.com compute.googleapis.com logging.googleapis.com monitoring.googleapis.com
```

## 5. Create Buckets and BigQuery Dataset

```bash
gsutil mb -l $REGION gs://$RAW_BUCKET
gsutil mb -l $REGION gs://$CODE_BUCKET
gsutil mb -l $REGION gs://$OUTPUT_BUCKET
bq --location=US mk --dataset $PROJECT_ID:$BQ_DATASET
```

If a bucket or dataset already exists, continue to the next command.

## 6. Validate and Upload Dataset with Docker

For final demo, the script rejects files smaller than 100,000 lines.

Linux/macOS/Git Bash with a service account key:

```bash
docker run --rm \
  -v "$PWD:/app" \
  -v "$PWD/service-account.json:/tmp/key.json:ro" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/key.json \
  -e PROJECT_ID=$PROJECT_ID \
  distributed-log-analytics:latest \
  python deployment/prepare_large_dataset.py \
  --local-path $LARGE_LOCAL_PATH \
  --gcs-path $LARGE_GCS_PATH
```

Windows PowerShell with a service account key:

```powershell
docker run --rm `
  -v "${PWD}:/app" `
  -v "${PWD}\service-account.json:/tmp/key.json:ro" `
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/key.json `
  -e PROJECT_ID=$env:PROJECT_ID `
  distributed-log-analytics:latest `
  python deployment/prepare_large_dataset.py `
  --local-path $env:LARGE_LOCAL_PATH `
  --gcs-path $env:LARGE_GCS_PATH
```

Smoke-test validation with `HDFS_2k`:

```bash
docker run --rm -v "$PWD:/app" distributed-log-analytics:latest \
  python deployment/prepare_large_dataset.py \
  --local-path dataset/HDFS_2k/HDFS_2k.log \
  --gcs-path gs://$RAW_BUCKET/loghub/hdfs/smoke/HDFS_2k.log \
  --allow-small \
  --skip-upload
```

Verify upload:

```bash
gsutil ls -lh $LARGE_GCS_PATH
```

## 7. Upload Spark Job to GCS

```bash
gsutil cp batch_processing/spark_job.py gs://$CODE_BUCKET/jobs/spark_job.py
```

## 8. Create Dataproc Cluster

Use 1 master and 2 workers for the demo.

```bash
gcloud dataproc clusters create $CLUSTER_NAME \
  --region=$REGION \
  --single-node=false \
  --master-machine-type=n2-standard-2 \
  --worker-machine-type=n2-standard-2 \
  --num-workers=2 \
  --image-version=2.2-debian12 \
  --project=$PROJECT_ID
```

## 9. Submit Large Batch Spark Job

```bash
gcloud dataproc jobs submit pyspark gs://$CODE_BUCKET/jobs/spark_job.py \
  --cluster=$CLUSTER_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --properties=spark.jars.packages=com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.42.1 \
  -- \
  --input gs://$RAW_BUCKET/loghub/hdfs/full/HDFS.log \
  --output gs://$OUTPUT_BUCKET/results/hdfs_full \
  --project-id $PROJECT_ID \
  --bq-dataset $BQ_DATASET \
  --output-partitions 8 \
  --write-bigquery
```

The job writes:

```text
logs_dataset.processed_logs
logs_dataset.error_frequency
logs_dataset.level_distribution
logs_dataset.component_failures
logs_dataset.temporal_analysis
logs_dataset.anomalies
```

## 10. Verify Cloud Execution

```bash
gcloud dataproc jobs list --region=$REGION
gcloud dataproc jobs describe JOB_ID --region=$REGION
gsutil ls -r gs://$OUTPUT_BUCKET/results/hdfs_full
bq ls $PROJECT_ID:$BQ_DATASET
bq head $PROJECT_ID:$BQ_DATASET.processed_logs
```

Capture screenshots of:

- Docker image build.
- Docker status page.
- GCS full HDFS dataset.
- Dataproc cluster with 1 master and 2 workers.
- Dataproc job details and driver logs.
- GCS processed Parquet output.
- BigQuery populated tables.
- Looker Studio dashboard.

## 11. Build Looker Studio Dashboard

Connect Looker Studio to BigQuery table `logs_dataset.processed_logs`.

Recommended charts:

- Bar chart: `component` vs warning/error count.
- Pie chart: `level` distribution.
- Time series: `hour` vs warning/error count.
- Table: `logs_dataset.anomalies`.
- Scorecards: total logs, total warnings/errors, total anomalies, distinct components.

## 12. Deploy Dockerized Status Page on Compute Engine

Create a VM:

```bash
gcloud compute instances create log-analytics-docker-vm \
  --zone=$ZONE \
  --machine-type=e2-micro \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --tags=http-server \
  --project=$PROJECT_ID
```

Allow HTTP:

```bash
gcloud compute firewall-rules create allow-log-analytics-status-8080 \
  --allow tcp:8080 \
  --target-tags=http-server \
  --project=$PROJECT_ID
```

SSH into the VM, install Docker, copy the project, and run:

```bash
docker build -t distributed-log-analytics:latest .
docker run -d --name log-analytics-status \
  -p 8080:8080 \
  -e PROJECT_ID=distributed-log-analytics \
  -e REGION=us-central1 \
  -e RAW_BUCKET=distributed-log-analytics-raw-logs \
  -e OUTPUT_BUCKET=distributed-log-analytics-spark-output \
  -e BQ_DATASET=logs_dataset \
  -e LOOKER_STUDIO_URL=https://lookerstudio.google.com \
  distributed-log-analytics:latest
```

Open:

```text
http://VM_EXTERNAL_IP:8080
```

## 13. Clean Up

```bash
gcloud dataproc clusters delete $CLUSTER_NAME --region=$REGION --quiet
gcloud compute instances delete log-analytics-docker-vm --zone=$ZONE --quiet
```

Delete buckets only after saving screenshots and report evidence.
