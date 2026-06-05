"""
Validate a large HDFS log dataset and upload it to Google Cloud Storage.

This script validates a file-based batch dataset before cloud processing.
"""

import argparse
import os
from pathlib import Path
from typing import Tuple

DEFAULT_LOCAL_PATH = "dataset/HDFS_full/HDFS.log"
DEFAULT_GCS_PATH = "gs://distributed-log-analytics-raw-logs/loghub/hdfs/full/HDFS.log"
DEFAULT_MIN_LINES = 100_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and upload the large HDFS log dataset")
    parser.add_argument("--local-path", default=DEFAULT_LOCAL_PATH, help="Local HDFS.log path")
    parser.add_argument("--gcs-path", default=DEFAULT_GCS_PATH, help="Destination gs://bucket/object path")
    parser.add_argument("--min-lines", type=int, default=DEFAULT_MIN_LINES, help="Minimum line count for final demo")
    parser.add_argument("--allow-small", action="store_true", help="Allow small files for smoke testing")
    parser.add_argument("--skip-upload", action="store_true", help="Validate only; do not upload to GCS")
    return parser.parse_args()


def parse_gcs_path(gcs_path: str) -> Tuple[str, str]:
    if not gcs_path.startswith("gs://"):
        raise ValueError("GCS path must start with gs://")

    path_without_scheme = gcs_path[5:]
    bucket, _, blob_name = path_without_scheme.partition("/")
    if not bucket or not blob_name:
        raise ValueError("GCS path must include both bucket and object name")

    return bucket, blob_name


def count_lines(path: Path) -> int:
    line_count = 0
    with path.open("rb") as file:
        for _ in file:
            line_count += 1
    return line_count


def validate_hdfs_log(path: Path, min_lines: int, allow_small: bool) -> Tuple[int, int]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Dataset path is not a file: {path}")

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise ValueError("Dataset file is empty")

    line_count = count_lines(path)
    if line_count == 0:
        raise ValueError("Dataset file has no log records")

    if line_count < min_lines and not allow_small:
        raise ValueError(
            f"Dataset has {line_count:,} lines, below the {min_lines:,} line final-demo threshold. "
            "Use --allow-small only for HDFS_2k smoke testing."
        )

    return line_count, size_bytes


def upload_to_gcs(local_path: Path, gcs_path: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = parse_gcs_path(gcs_path)
    client = storage.Client(project=os.getenv("PROJECT_ID") or None)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(str(local_path))


def main() -> None:
    args = parse_args()
    local_path = Path(args.local_path)

    print("Large HDFS dataset preparation")
    print(f"Local path: {local_path}")
    print(f"GCS path: {args.gcs_path}")

    line_count, size_bytes = validate_hdfs_log(local_path, args.min_lines, args.allow_small)
    size_mb = size_bytes / (1024 * 1024)
    print(f"Validated dataset: {line_count:,} lines, {size_mb:.2f} MB")

    if args.skip_upload:
        print("Upload skipped by --skip-upload")
        return

    upload_to_gcs(local_path, args.gcs_path)
    print(f"Uploaded dataset to {args.gcs_path}")


if __name__ == "__main__":
    main()
