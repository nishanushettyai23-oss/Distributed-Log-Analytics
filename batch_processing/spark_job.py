"""
Dataproc Spark job for distributed log analytics and anomaly detection.

The job is designed to run on Google Cloud Dataproc. It reads raw LogHub or
JSON logs from Google Cloud Storage, performs distributed Spark processing, and
writes analytics outputs to GCS and optionally BigQuery.
"""

import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    concat,
    input_file_name,
    lit,
    regexp_extract,
    to_timestamp,
    when,
)
from pyspark.sql.types import IntegerType, StringType, StructField, StructType


DEFAULT_PROJECT_ID = "distributed-log-analytics"
DEFAULT_BQ_DATASET = "logs_dataset"


HDFS_LOG_SCHEMA = StructType(
    [
        StructField("date", StringType(), True),
        StructField("time", StringType(), True),
        StructField("pid", StringType(), True),
        StructField("level", StringType(), True),
        StructField("component", StringType(), True),
        StructField("message", StringType(), True),
    ]
)


def parse_args():
    parser = argparse.ArgumentParser(description="Distributed log analytics on Dataproc")
    parser.add_argument("--input", required=True, help="Input path, for example gs://bucket/loghub/hdfs/HDFS_2k.log")
    parser.add_argument("--output", required=True, help="Output GCS path for Parquet results")
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--bq-dataset", default=DEFAULT_BQ_DATASET)
    parser.add_argument("--output-partitions", type=int, default=8, help="Parquet output partitions per result")
    parser.add_argument("--write-bigquery", action="store_true", help="Write result tables to BigQuery")
    return parser.parse_args()


def build_spark():
    return (
        SparkSession.builder.appName("DistributedLogAnalyticsDataproc")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )


def read_logs(spark, input_path):
    if input_path.endswith(".json") or ".json" in input_path:
        raw_df = spark.read.json(input_path)
        return (
            raw_df.withColumn("timestamp", to_timestamp(col("timestamp")))
            .withColumn("level", col("level").cast(StringType()))
            .withColumn("service", col("service").cast(StringType()))
            .withColumn("component", col("node").cast(StringType()))
            .withColumn("message", col("message").cast(StringType()))
            .withColumn("source_file", input_file_name())
        )

    raw_text = spark.read.text(input_path)
    parsed_df = raw_text.select(
        regexp_extract(col("value"), r"^(\d{6})\s+(\d{6})\s+(\d+)\s+(\w+)\s+([^:]+):\s+(.*)$", 1).alias("date"),
        regexp_extract(col("value"), r"^(\d{6})\s+(\d{6})\s+(\d+)\s+(\w+)\s+([^:]+):\s+(.*)$", 2).alias("time"),
        regexp_extract(col("value"), r"^(\d{6})\s+(\d{6})\s+(\d+)\s+(\w+)\s+([^:]+):\s+(.*)$", 3).alias("pid"),
        regexp_extract(col("value"), r"^(\d{6})\s+(\d{6})\s+(\d+)\s+(\w+)\s+([^:]+):\s+(.*)$", 4).alias("level"),
        regexp_extract(col("value"), r"^(\d{6})\s+(\d{6})\s+(\d+)\s+(\w+)\s+([^:]+):\s+(.*)$", 5).alias("component"),
        regexp_extract(col("value"), r"^(\d{6})\s+(\d{6})\s+(\d+)\s+(\w+)\s+([^:]+):\s+(.*)$", 6).alias("message"),
        input_file_name().alias("source_file"),
    )

    return (
        parsed_df.filter(col("message") != "")
        .withColumn("timestamp", to_timestamp(concat(col("date"), col("time")), "yyMMddHHmmss"))
        .withColumn("service", regexp_extract(col("component"), r"([A-Za-z]+)", 1))
    )


def extract_features(logs_df):
    return (
        logs_df.dropna(subset=["level", "message"])
        .dropDuplicates(["timestamp", "level", "component", "message"])
        .withColumn("level", col("level").cast(StringType()))
        .withColumn("service", when(col("service") == "", lit("hdfs")).otherwise(col("service")))
        .withColumn("block_id", regexp_extract(col("message"), r"(blk_-?\d+)", 1))
        .withColumn("node_id", regexp_extract(col("message"), r"(\d+\.\d+\.\d+\.\d+:\d+)", 1))
        .withColumn("error_code", regexp_extract(col("message"), r"(ERROR|WARN|Exception|failed|failure)", 1))
        .withColumn("hour", regexp_extract(col("timestamp").cast("string"), r"\s(\d{2}):", 1).cast(IntegerType()))
        .select(
            "timestamp",
            "level",
            "service",
            "component",
            "block_id",
            "node_id",
            "error_code",
            "hour",
            "message",
            "source_file",
        )
    )


def build_analytics(features_df):
    total_records = max(features_df.count(), 1)
    error_frequency = (
        features_df.filter(col("level").isin("ERROR", "FATAL", "WARN"))
        .groupBy("service")
        .agg(count("*").alias("error_count"))
        .orderBy(col("error_count").desc())
    )

    level_distribution = (
        features_df.groupBy("level")
        .agg(count("*").alias("count"))
        .withColumn("percentage", col("count") * 100.0 / total_records)
        .orderBy(col("count").desc())
    )

    component_failures = (
        features_df.filter(col("level").isin("ERROR", "FATAL", "WARN"))
        .groupBy("component")
        .agg(count("*").alias("failure_count"))
        .orderBy(col("failure_count").desc())
    )

    temporal_analysis = (
        features_df.filter(col("level").isin("ERROR", "FATAL", "WARN"))
        .groupBy("hour")
        .agg(count("*").alias("hourly_errors"))
        .orderBy("hour")
    )

    return {
        "processed_logs": features_df,
        "error_frequency": error_frequency,
        "level_distribution": level_distribution,
        "component_failures": component_failures,
        "temporal_analysis": temporal_analysis,
    }


def detect_anomalies(features_df, error_frequency):
    service_count = max(features_df.select("service").distinct().count(), 1)
    total_errors = error_frequency.agg(count("*").alias("services_with_errors")).collect()[0]["services_with_errors"]
    avg_errors = features_df.filter(col("level").isin("ERROR", "FATAL", "WARN")).count() / service_count
    threshold = avg_errors * 2

    return (
        error_frequency.filter(col("error_count") > threshold)
        .withColumn("threshold", lit(float(threshold)))
        .withColumn("severity", when(col("error_count") > threshold * 2, lit("CRITICAL")).otherwise(lit("HIGH")))
        .withColumn("status", lit("ANOMALY_DETECTED"))
        .withColumn("services_with_errors", lit(int(total_errors)))
    )


def write_outputs(results, output_path, project_id, bq_dataset, write_bigquery, output_partitions):
    for name, df in results.items():
        target = f"{output_path.rstrip('/')}/{name}"
        output_df = df.repartition(output_partitions) if output_partitions > 0 else df
        output_df.write.mode("overwrite").parquet(target)
        print(f"Saved {name} to {target}")

        if write_bigquery:
            table = f"{project_id}:{bq_dataset}.{name}"
            output_df.write.format("bigquery").option("table", table).mode("overwrite").save()
            print(f"Wrote {name} to BigQuery table {table}")


def main():
    args = parse_args()
    spark = build_spark()

    try:
        print("Starting Dataproc distributed log analytics job")
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")

        raw_logs = read_logs(spark, args.input)
        features = extract_features(raw_logs).cache()
        print(f"Records after parsing and feature extraction: {features.count()}")

        results = build_analytics(features)
        results["anomalies"] = detect_anomalies(features, results["error_frequency"])

        write_outputs(
            results,
            args.output,
            args.project_id,
            args.bq_dataset,
            args.write_bigquery,
            args.output_partitions,
        )
        print("Dataproc Spark analytics job completed successfully")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
