-- Creates the BigQuery dataset and table for storing error logs

-- Create Dataset
CREATE SCHEMA IF NOT EXISTS `your-project-id.logs_dataset`
  OPTIONS (
    location = 'US',
    description = 'Dataset containing application infrastructure logs'
  );

-- Create Table with partitioning and clustering for query performance
CREATE TABLE IF NOT EXISTS `your-project-id.logs_dataset.error_logs` (
    timestamp TIMESTAMP NOT NULL,
    service STRING NOT NULL,
    level STRING NOT NULL,
    message STRING NOT NULL,
    trace_id STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY service, level;
