# Web Application Page Guide

## Purpose

The application demonstrates how Big Data Technologies and Cloud Computing services can process and analyze a large system-log dataset. It is not a live-streaming system. The deployed workflow is:

`LogHub HDFS logs -> Google Cloud Storage -> Dataproc PySpark batch -> BigQuery and GCS output -> Flask API -> React dashboard`

The displayed analytics come from `distributed-log-analytics.logs_dataset.processed_logs`, which contains 10,685,241 parsed records. Infrastructure evidence is read from GCS, Dataproc, and BigQuery APIs.

## Role of each page

### Distributed Log Analytics

This is the project overview and results summary. It explains the problem, the cloud processing path, the scale of the deployed dataset, and the main analytical outcomes. KPI values are queried from BigQuery rather than generated in the browser.

### Log Analytics

This page presents aggregate results derived from the processed records: log-level distribution, component activity, hourly trends, active nodes, and error-code frequency. These aggregations demonstrate Spark feature extraction and BigQuery analytical queries.

### Anomaly Detection

This page applies a statistical z-score analysis to component, hour, node, and error-code groups. A result of zero anomalies means no group exceeded the configured threshold of 2.0. It is a valid result and does not mean that the page failed.

### Dataset and Batch Processing

This page has two responsibilities:

1. Explore the ten-column `processed_logs` BigQuery table with search, filters, and pagination.
2. Allow an administrator to submit another log file already stored in the raw GCS bucket to the Dataproc PySpark job.

Public browser uploads are intentionally disabled because large datasets should not pass through Flask or the public VM. Upload them directly to GCS with the preparation script, then enter the resulting `gs://` URI in the page.

### BigQuery Explorer

This is a read-only SQL workspace for verifying the stored output. It blocks data-changing SQL and shows the BigQuery job ID, rows returned, execution time, and bytes processed.

### Infrastructure

This page provides deployment evidence: Dataproc cluster state, worker count, GCS object counts and sizes, BigQuery tables, processed row counts, and recent Dataproc job IDs. This is the main page for demonstrating that cloud resources exist and were used.

### Architecture

This page explains both paths:

- Batch path: GCS -> Dataproc/Spark -> BigQuery/GCS.
- Serving path: HTTPS/Caddy -> Nginx/React -> Flask -> BigQuery and GCP metadata APIs.

It connects the implementation to distributed processing, object storage, managed analytics, virtual machines, containers, IAM, and secure networking.

### Reports

This page creates PDF, Excel, and CSV evidence files from the same BigQuery-backed analytics used by the dashboard. Download status and generation errors are shown in the interface.

## Upload and process another dataset

Upload a large local file from the project directory:

```bash
docker compose run --rm api python deployment/prepare_large_dataset.py \
  --local-path dataset/HDFS_full/HDFS.log \
  --gcs-path gs://distributed-log-analytics-raw-logs/loghub/hdfs/full/HDFS.log
```

Configure an administrator token in `.env` on the VM:

```text
PIPELINE_ADMIN_TOKEN=use-a-long-random-secret
```

Restart the API:

```bash
docker compose up -d --build api frontend caddy
```

On the Dataset page, enter:

- GCS input URI
- A short output name
- The administrator token

The response contains the real Dataproc job ID. Track it with:

```bash
gcloud dataproc jobs describe JOB_ID \
  --region=us-central1 \
  --project=distributed-log-analytics
```

## Docker Desktop

Docker Desktop can show local images and containers, but it cannot directly display containers running on the remote Compute Engine VM.

For local use:

1. Start Docker Desktop.
2. Open **Images** to view `distributed-log-analytics-api`, `distributed-log-analytics-web`, and `caddy`.
3. Run `docker compose up -d --build` in the project terminal.
4. Open **Containers** and select the `distributed-log-analytics` Compose project.
5. Select a container to inspect its logs, environment, ports, and health status.

For the GCP VM, use:

```bash
docker compose ps
docker compose images
docker compose logs --tail=100 api frontend caddy
```

Healthy output should show the API as healthy, Nginx running, and Caddy serving the configured HTTPS hostname.

## Subject relevance

**Big Data Technologies:** Apache Spark, distributed executors, parallel parsing, feature extraction, large-scale aggregation, statistical anomaly detection, Parquet, and fault-tolerant batch processing.

**Cloud Computing and Architectures:** GCS object storage, managed Dataproc compute, BigQuery analytical storage, Compute Engine, Docker containers, reverse proxies, HTTPS, IAM permissions, cloud APIs, and separation of storage, compute, application, and presentation layers.
