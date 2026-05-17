# Architecture Overview

## System Overview
The "Distributed Log Analytics for Cloud Infrastructure" project is designed to handle high-throughput log ingestion, real-time stream processing, batch processing, and advanced analytics on Google Cloud Platform (GCP). It enables real-time monitoring and anomaly detection for microservices.

## Data Flow
1. **Generation:** Services or simulated scripts generate JSON-formatted logs.
2. **Ingestion:** Logs are published to Google Cloud Pub/Sub, acting as a highly available message broker.
3. **Stream Processing:** Apache Beam (via Dataflow) consumes the Pub/Sub stream, filters for errors or critical events, and writes them to BigQuery for real-time analysis.
4. **Batch Processing:** Apache Spark (via Dataproc) reads raw logs stored in Cloud Storage (archived from Pub/Sub) to perform complex aggregations, like error counts per service over time.
5. **Storage:** BigQuery serves as the enterprise data warehouse, while Cloud Storage acts as a data lake for raw logs.
6. **Analytics & Alerting:** SQL queries analyze BigQuery data. A Python-based anomaly detection script runs periodically, triggering Cloud Functions for alerting when thresholds are breached.
7. **Visualization:** Looker Studio connects to BigQuery to present real-time dashboards.

## Component Mapping to GCP Services
- **Message Broker:** Cloud Pub/Sub
- **Stream Processing:** Dataflow (Apache Beam)
- **Batch Processing:** Dataproc (Apache Spark)
- **Data Warehouse:** BigQuery
- **Data Lake:** Cloud Storage
- **Serverless Compute (Alerting):** Cloud Functions
- **BI/Visualization:** Looker Studio
