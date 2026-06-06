# RV College of Engineering
## Department of Artificial Intelligence and Machine Learning
### Cloud Computing Technology and Architectures (AI364TA)

**Activity 1 - Cloud-Based Project Deployment and Demonstration**

| Field | Details |
|---|---|
| **Project Title** | Distributed Log Analytics and Anomaly Detection System using Apache Spark on Google Cloud |
| **Student 1** | `[Shreyas Bharadwaj] - [1RV23AI096]` |
| **Student 2** | `[Preetham R] - [1RV23AI075]` |
| **Student 3** | `[Nishan U Shetty] - [1RV23AI068  ]` |

| **Project Deployment Link** | `[Insert Compute Engine public URL, for example: http://STATIC_IP:3000]` |

## 1. Project Overview

The project is a cloud-based platform for analysing large system-log datasets. Manual inspection of millions of entries is slow and makes recurring failures and unusual activity difficult to identify. The application processes the LogHub HDFS dataset using Apache Spark on Google Cloud Dataproc.

Raw logs are stored in Google Cloud Storage. The processed results are written to `logs_dataset.processed_logs` in BigQuery, which contains 10,685,241 records. A Flask API supplies data to a React interface for dashboards, log exploration, anomaly analysis, infrastructure status, and report exports. The intended users are cloud administrators, DevOps engineers, site reliability engineers, and system analysts.

## 2. Cloud Deployment Objectives

The objective was to move storage, distributed computation, analytics, and application hosting to Google Cloud. The deployment demonstrates:

- distributed computation using Apache Spark worker nodes on Dataproc;
- scalable object storage using Google Cloud Storage;
- managed analytical querying through BigQuery;
- virtual-machine hosting through Compute Engine;
- containerised deployment of the Flask and React applications using Docker;
- controlled access to cloud resources through IAM service accounts; and
- deployment verification through Dataproc logs and container health checks.

The managed services support a dataset much larger than the local smoke-test data and reduce manual administration of Spark, storage, and database infrastructure.

## 3. Cloud Architecture Design

Dataproc reads HDFS logs from Cloud Storage. Spark parses each record, extracts component, node, error-code, and hour fields, and writes the results to BigQuery. The Flask API provides read-only analytical access, while Nginx serves the React frontend and forwards `/api` requests to Flask.

### Cloud Architecture Diagram

> **Insert architecture diagram here.**  
> The diagram should show:  
> `LogHub HDFS Dataset -> Cloud Storage -> Dataproc/Spark -> BigQuery -> Flask API -> React Frontend`  
> Also show the Docker containers running on the Compute Engine VM.

<br><br><br><br><br><br>

**Figure 1: Cloud architecture and data flow of the distributed log analytics platform.**

<div style="page-break-after: always;"></div>

## 4. Cloud Services Utilized

| Service | Category | Purpose and Integration |
|---|---|---|
| **Cloud Storage** | Object storage | Stores the HDFS file, Spark code, and Parquet output accessed through `gs://` paths. |
| **Dataproc** | Distributed computing | Runs the managed Spark cluster for parsing, feature extraction, aggregation, and anomaly detection. |
| **BigQuery** | Data warehouse | Stores processed records and executes analytical SQL used by the Flask API. |
| **Compute Engine** | Virtual machine | Hosts the Docker Compose deployment for Flask and React/Nginx. |
| **IAM** | Security | Allows the VM service account to query BigQuery and view Dataproc and Storage resources. |
| **Cloud Logging** | Monitoring | Provides Dataproc job status and driver output for verification. |
| **Docker Compose** | Containerisation | Builds and runs the backend and frontend consistently. |

## 5. Deployment Process

The deployment was performed in the following sequence:

1. Enable the Compute Engine, Dataproc, BigQuery, Storage, IAM, Logging, and Monitoring APIs.
2. Create GCS buckets for raw logs, Spark code, and processed output.
3. Upload the full HDFS dataset and PySpark job to GCS.
4. Create a Dataproc cluster with one master and two workers.
5. Submit the Spark job with GCS input and BigQuery/GCS outputs.
6. Verify the `processed_logs` table and Dataproc driver logs.
7. Create a least-privilege VM service account.
8. Create a Compute Engine VM using that service account.
9. Install Docker Compose, clone the GitHub repository, and run `docker compose up -d --build`.
10. Allow port `3000` and access the React application through the VM's public address.

### Deployment Workflow

> **Insert deployment workflow diagram here.**  
> Suggested flow:  
> `Provision GCP Resources -> Upload Dataset -> Run Dataproc Job -> Verify BigQuery -> Create VM -> Deploy Docker Containers -> Access Public URL`

<br><br><br><br>

**Figure 2: Sequence followed to deploy and verify the application on GCP.**

<div style="page-break-after: always;"></div>

## 6. Evidence of Cloud Deployment

Insert these screenshots after deployment. Each should show the project or resource name.

| Evidence | Screenshot Space and Caption |
|---|---|
| **Compute** | `[Dataproc cluster screenshot]` **Figure 3:** Master and worker configuration. |
| **Storage** | `[GCS HDFS.log screenshot]` **Figure 4:** Dataset stored in Cloud Storage. |
| **Database** | `[BigQuery row-count screenshot]` **Figure 5:** Processed analytical records. |
| **Job** | `[Dataproc job screenshot]` **Figure 6:** Spark job and driver output. |
| **Application** | `[React dashboard screenshot]` **Figure 7:** Application accessed through the public VM URL. |
| **Containers** | `[docker compose ps screenshot]` **Figure 8:** API and frontend containers. |

## 7. Cloud Features Demonstrated

- **Virtual machines:** Compute Engine hosts the application; Dataproc manages Spark nodes.
- **Object storage:** GCS stores raw logs, code, and processed output.
- **Managed warehouse:** BigQuery executes scalable analytics without database-server administration.
- **Containerisation:** Docker isolates Flask and React and supports repeatable deployment.
- **IAM:** A dedicated service account receives only required viewer and query roles.
- **Monitoring:** Dataproc, API health, and Docker logs support verification and troubleshooting.
- **Scalability and fault tolerance:** Spark distributes work and can recompute failed partitions.

Kubernetes, load balancing, DNS routing, and CI/CD are not included in the current deployment and are therefore not claimed as implemented features.

## 8. Conclusion

The project demonstrates an integrated cloud deployment for large-scale log analytics. GCS stores the data, Dataproc runs distributed Spark processing, BigQuery provides analytical storage, and Compute Engine hosts the Dockerised Flask and React application. The activity demonstrated managed services, virtual machines, containerisation, IAM, monitoring, and cloud service integration.

## 9. References

1. Google Cloud, **Dataproc Documentation**: https://cloud.google.com/dataproc/docs  
2. Google Cloud, **Cloud Storage Documentation**: https://cloud.google.com/storage/docs  
3. Google Cloud, **BigQuery Documentation**: https://cloud.google.com/bigquery/docs  
4. Google Cloud, **Compute Engine Documentation**: https://cloud.google.com/compute/docs  
5. Google Cloud, **IAM Documentation**: https://cloud.google.com/iam/docs  
6. Apache Software Foundation, **Apache Spark Documentation**: https://spark.apache.org/docs/latest/  
7. Docker, **Docker Engine Documentation**: https://docs.docker.com/engine/  
8. LogPAI, **LogHub Dataset Repository**: https://github.com/logpai/loghub
