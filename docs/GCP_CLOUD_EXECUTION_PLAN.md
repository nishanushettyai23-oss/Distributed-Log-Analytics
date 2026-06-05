# Cloud Execution Plan and Report Outline

## 1. Project Overview

The Distributed Log Analytics and Anomaly Detection System is deployed on Google Cloud Platform to analyze a large LogHub HDFS dataset using cloud-based distributed batch processing. The project addresses the difficulty of manually inspecting high-volume system logs by automatically parsing log records, extracting operational metrics, and detecting abnormal failure patterns.

The intended users are cloud administrators, DevOps engineers, SRE teams, and students demonstrating Big Data Technologies and Cloud Computing Architecture concepts. The system uses Docker for reproducible dataset preparation and a containerized status page, Google Cloud Storage for raw and processed storage, Dataproc for Apache Spark computation, BigQuery for analytics storage, and Looker Studio for visualization.

The cloud computation is large-scale batch processing on Dataproc.

## 2. Cloud Deployment Objectives

The main objective is to prove that the core computation executes on cloud infrastructure. Dataproc runs Spark parsing, cleaning, feature extraction, aggregation, and anomaly detection across cloud worker nodes.

Cloud deployment demonstrates scalability, distributed computation, object storage, managed analytics, containerization, IAM-controlled access, monitoring, logging, and service integration. Docker supports reproducible deployment artifacts, while GCP services host the storage, computation, query, and visualization layers.

## 3. Cloud Architecture Design

```text
Large LogHub HDFS Dataset
        |
        v
Docker Dataset Prep Tool
        |
        v
Google Cloud Storage - raw log bucket
        |
        v
Dataproc Cluster - Apache Spark distributed processing
        |
        v
Spark analytics and anomaly detection job
        |
        +----------------------+
        |                      |
        v                      v
GCS processed output      BigQuery analytics tables
                               |
                               v
                        Looker Studio dashboard

Compute Engine VM
        |
        v
Dockerized Flask Status Page
```

Data flow:

1. Store the full HDFS dataset locally outside Git.
2. Build the Docker image.
3. Run the Docker dataset prep tool to validate line count, report file size, and upload `HDFS.log` to GCS.
4. Upload the Spark job to a GCS code bucket.
5. Submit the PySpark job to Dataproc.
6. Spark reads the large dataset from GCS and processes it across Dataproc worker nodes.
7. Spark writes Parquet evidence to GCS and analytics tables to BigQuery.
8. Looker Studio reads BigQuery tables for dashboards.
9. Compute Engine optionally hosts the Dockerized Flask status page for deployment evidence.

## 4. Cloud Services Utilized

| Service | Category | Purpose | Integration |
|---|---|---|---|
| Docker | Containerization | Packages the dataset prep tool and Flask status page | Builds a reproducible image for local testing and Compute Engine deployment |
| Google Cloud Storage | Object Storage | Stores full raw HDFS logs, Spark job files, and processed Parquet output | Docker uploads raw data; Dataproc reads/writes through `gs://` paths |
| Dataproc | Managed Big Data Processing | Runs Apache Spark on cloud infrastructure | Executes `batch_processing/spark_job.py` as a distributed PySpark job |
| BigQuery | Managed Data Warehouse | Stores processed logs, error frequencies, level distributions, component failures, time trends, and anomalies | Spark writes result tables using the Spark BigQuery connector |
| Looker Studio | Visualization | Displays charts for error trends, log levels, anomaly counts, and component failures | Connects directly to BigQuery |
| Compute Engine | Virtual Machines | Hosts the Dockerized Flask status page | Demonstrates VM hosting and container runtime on GCP |
| IAM | Security | Controls service access for GCS, Dataproc, BigQuery, and Compute Engine | Uses user or service-account permissions |
| Cloud Logging and Monitoring | Observability | Captures Dataproc job logs and cluster metrics | Provides proof that Spark executed in the cloud |

## 5. Deployment Process

1. Download the full LogHub HDFS dataset to `dataset/HDFS_full/HDFS.log`.
2. Build Docker image `distributed-log-analytics:latest`.
3. Run Docker locally to validate the dataset and upload it to GCS.
4. Enable GCP APIs for Dataproc, Storage, BigQuery, Compute Engine, Logging, and Monitoring.
5. Create raw, code, and output GCS buckets.
6. Create BigQuery dataset `logs_dataset`.
7. Upload `batch_processing/spark_job.py` to the GCS code bucket.
8. Create Dataproc cluster with 1 master node and 2 worker nodes.
9. Submit the Spark job with full HDFS GCS input, GCS output, BigQuery dataset, and `--write-bigquery`.
10. Build Looker Studio charts from BigQuery.
11. Deploy the Dockerized Flask status page on a Compute Engine VM.

The exact commands are in [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md).

## 6. Evidence of Cloud Deployment

Include screenshots with captions:

| Screenshot | Caption |
|---|---|
| Docker image build | Container image created for dataset prep and status dashboard |
| Docker container running | Flask status page running from the project image |
| GCS raw bucket with `HDFS.log` | Large LogHub HDFS dataset stored in cloud object storage |
| Dataset prep output | Dataset line count and file size validated before upload |
| Dataproc cluster details | Managed Spark cluster with 1 master and 2 workers |
| Dataproc job list and details | PySpark analytics job executed on cloud infrastructure |
| Dataproc driver logs | Spark parsing, feature extraction, analytics, and anomaly detection stages completed |
| GCS processed output folder | Distributed Spark outputs written back to cloud storage |
| BigQuery `logs_dataset` tables | Processed analytics loaded into managed data warehouse |
| BigQuery table preview | Cloud-generated results available for querying |
| Looker Studio dashboard | Visual insights for error trends, component failures, and anomalies |
| Compute Engine VM | Dockerized Flask status page hosted on cloud VM |

## 7. Cloud Features Demonstrated

- Virtual Machines: Dataproc cluster nodes and Compute Engine VM.
- Object Storage: GCS stores raw logs, job code, and processed output.
- Managed Data Warehouse: BigQuery stores analytics tables.
- Containerization: Docker packages dataset preparation and project status UI.
- IAM and Security: GCP permissions control access between Docker, GCS, Dataproc, BigQuery, and users.
- Monitoring and Logging: Dataproc job logs and Cloud Monitoring prove cloud execution.
- Scalability: Dataproc workers distribute Spark tasks across the large dataset.
- Fault Tolerance: Spark can recompute failed partitions and Dataproc manages cluster resources.
- Data-driven Decision Making: BigQuery and Looker Studio expose trends and anomalies for operational action.

## 8. Conclusion

The deployment preserves the existing Big Data analytics project while strengthening the cloud architecture. The final system uses Docker for reproducible tooling and a containerized frontend, GCS for large dataset storage, Dataproc for distributed Spark computation, BigQuery for analytical querying, and Looker Studio for dashboards. This satisfies Big Data Technologies requirements through large-scale Spark analytics and Cloud Computing Architecture requirements through integrated managed cloud services.

## 9. References

- Google Cloud Dataproc documentation: https://cloud.google.com/dataproc/docs
- Google Cloud Storage documentation: https://cloud.google.com/storage/docs
- BigQuery documentation: https://cloud.google.com/bigquery/docs
- Compute Engine documentation: https://cloud.google.com/compute/docs
- Docker documentation: https://docs.docker.com/
- Looker Studio help: https://support.google.com/looker-studio
- Apache Spark documentation: https://spark.apache.org/docs/latest/
- LogHub datasets: https://github.com/logpai/loghub
