# Project Summary

The final project is a Distributed Log Analytics and Anomaly Detection System using Apache Spark on Google Cloud Platform.

Final architecture:

```text
Large LogHub HDFS Dataset
  -> Docker Dataset Prep Tool
  -> Google Cloud Storage
  -> Dataproc Apache Spark
  -> BigQuery
  -> Looker Studio
  -> Dockerized Flask API + React Observability Platform on Compute Engine
```

Key implementation points:

- Large-scale batch processing is the final demo mode.
- Docker is used for dataset preparation and status-page deployment.
- Dataproc executes the Spark job on cloud infrastructure.
- BigQuery stores processed analytics tables.
- Looker Studio visualizes operational insights and anomalies.
- The included `HDFS_2k` dataset is only for smoke testing.

The final implementation uses large-scale batch processing on Dataproc.
