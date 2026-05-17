"""
Apache Spark Batch Job for Log Analytics.
Reads raw logs from Cloud Storage, aggregates errors by service, and outputs results.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

# Configuration Placeholders
GCS_INPUT_PATH = "gs://your-project-id-raw-logs/logs/*/*.json"
GCS_OUTPUT_PATH = "gs://your-project-id-analytics/daily-error-summary/"

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("LogBatchAnalytics") \
        .getOrCreate()

    print("Spark Session created successfully.")

    # Read JSON logs from Cloud Storage
    # Assuming logs are periodically archived from Pub/Sub to GCS
    logs_df = spark.read.json(GCS_INPUT_PATH)

    # Filter for ERROR logs and group by service
    error_summary_df = logs_df \
        .filter(col("level") == "ERROR") \
        .groupBy("service") \
        .agg(count("*").alias("error_count"))

    # Show results in standard output (for debugging)
    error_summary_df.show()

    # Write aggregated results back to GCS as Parquet or CSV
    error_summary_df.write \
        .mode("overwrite") \
        .csv(GCS_OUTPUT_PATH, header=True)

    print(f"Aggregation complete. Results saved to {GCS_OUTPUT_PATH}")

    spark.stop()

if __name__ == "__main__":
    main()
