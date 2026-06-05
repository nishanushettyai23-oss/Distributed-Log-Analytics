# Architecture Explanation

## Overview

The Distributed Log Analytics and Anomaly Detection System is a large-scale batch analytics platform for cloud and system logs. It uses Docker for reproducible dataset preparation and status-page deployment, Google Cloud Storage for raw and processed log storage, Dataproc for Apache Spark distributed computation, BigQuery for analytics tables, and Looker Studio for dashboards.

The demonstration is focused on large batch processing with Spark on cloud infrastructure.

## Architecture Flow

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
Spark Parsing, Feature Extraction, Analytics, Anomaly Detection
        |
        +----------------------+
        |                      |
        v                      v
GCS Parquet Output       BigQuery Analytics Tables
                               |
                               v
                        Looker Studio Dashboard

Compute Engine VM
        |
        v
Dockerized Flask Status Page
```

## Component Roles

- Docker packages the dataset validator/uploader and Flask status page.
- Google Cloud Storage stores the full HDFS dataset, Spark job file, and processed Parquet outputs.
- Dataproc runs Apache Spark across one master node and two worker nodes.
- Spark parses HDFS log lines, extracts block/component/time features, computes analytics, and detects anomalies.
- BigQuery stores `processed_logs`, `error_frequency`, `level_distribution`, `component_failures`, `temporal_analysis`, and `anomalies`.
- Looker Studio visualizes trends, distributions, failures, and anomaly counts.
- Compute Engine optionally hosts the Dockerized status page for cloud deployment evidence.

## Big Data Concepts Demonstrated

- Distributed processing through Spark executors on Dataproc worker nodes.
- Parallel file reads from GCS.
- Batch transformations and aggregations over a large HDFS log dataset.
- Fault tolerance through Spark partition recomputation.
- Scalable output storage through GCS and BigQuery.
- Statistical anomaly detection over aggregated log behavior.

## Cloud Computing Concepts Demonstrated

- Managed compute with Dataproc.
- Virtual machines through Dataproc nodes and Compute Engine.
- Object storage with GCS.
- Managed data warehouse with BigQuery.
- Containerization with Docker.
- IAM-controlled access between compute, storage, and analytics services.
- Monitoring and logging through Dataproc job logs and Cloud Monitoring.
