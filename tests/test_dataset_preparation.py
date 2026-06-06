import tempfile
import unittest
from pathlib import Path

from deployment.prepare_large_dataset import parse_gcs_path, validate_hdfs_log


class DatasetPreparationTests(unittest.TestCase):
    def test_parse_gcs_path(self):
        bucket, object_name = parse_gcs_path("gs://raw-bucket/loghub/HDFS.log")
        self.assertEqual(bucket, "raw-bucket")
        self.assertEqual(object_name, "loghub/HDFS.log")

    def test_validate_small_smoke_dataset_when_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "HDFS.log"
            path.write_text("081109 203518 143 INFO dfs.DataNode: message\n", encoding="ascii")
            lines, size = validate_hdfs_log(path, min_lines=100_000, allow_small=True)
            self.assertEqual(lines, 1)
            self.assertGreater(size, 0)

    def test_reject_empty_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "HDFS.log"
            path.write_bytes(b"")
            with self.assertRaises(ValueError):
                validate_hdfs_log(path, min_lines=1, allow_small=False)


if __name__ == "__main__":
    unittest.main()
