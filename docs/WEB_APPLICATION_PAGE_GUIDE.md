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
2. Allow an administrator to upload a `.log`, `.txt`, or `.json` dataset into the raw GCS bucket.
3. Submit only the successfully stored GCS object to the Dataproc PySpark job.

The interface reports the GCS object URI, byte size, generation, Dataproc job ID, and output URI. These identifiers provide evidence that storage and processing are real cloud operations.

Ordinary visitors do not need an administrator token to view the deployed LogHub dataset, explore its processed records, or inspect analytics. The Dataset page includes **Use deployed sample dataset** beside the upload controls. The token is required only for actions that change cloud resources: uploading a new object or starting a billable Dataproc job.

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

Use the Dataset page for files up to the configured 2 GB limit. Select the file, enter the administrator token, and complete the two separate actions:

1. **Upload and store in GCS**
2. **Process with Dataproc PySpark**

For very large files or unstable browser connections, upload from the project directory:

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

The VM service account needs permission to create raw-bucket objects and submit Dataproc jobs. Grant narrowly scoped roles from an authorized Cloud Shell:

```bash
VM_SERVICE_ACCOUNT=$(gcloud compute instances describe log-analytics-platform \
  --zone=us-central1-a \
  --format='get(serviceAccounts[0].email)')

gcloud storage buckets add-iam-policy-binding \
  gs://distributed-log-analytics-raw-logs \
  --member="serviceAccount:${VM_SERVICE_ACCOUNT}" \
  --role="roles/storage.objectCreator"

gcloud projects add-iam-policy-binding distributed-log-analytics \
  --member="serviceAccount:${VM_SERVICE_ACCOUNT}" \
  --role="roles/dataproc.editor"
```

The Spark job writes result tables in overwrite mode. When a submitted job completes, the dashboard and explorers represent the newly processed dataset. Refresh the application after the Dataproc job reaches `DONE`.

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
