"""
Dockerized status page for the cloud batch log analytics project.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, render_template_string


app = Flask(__name__)


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def dataset_status() -> dict:
    path = Path(env("DATASET_LOCAL_PATH", "dataset/HDFS_full/HDFS.log"))
    if not path.exists():
        return {"label": "Not mounted in this container", "detail": str(path), "size": "0 MB"}

    size_mb = path.stat().st_size / (1024 * 1024)
    return {"label": "Available", "detail": str(path), "size": f"{size_mb:.2f} MB"}


@app.route("/")
def index():
    project_id = env("PROJECT_ID", "distributed-log-analytics")
    region = env("REGION", "us-central1")
    raw_bucket = env("RAW_BUCKET", f"{project_id}-raw-logs")
    output_bucket = env("OUTPUT_BUCKET", f"{project_id}-spark-output")
    bq_dataset = env("BQ_DATASET", "logs_dataset")
    looker_url = env("LOOKER_STUDIO_URL", "https://lookerstudio.google.com")
    dataset_gcs_path = env("DATASET_GCS_PATH", f"gs://{raw_bucket}/loghub/hdfs/full/HDFS.log")

    tables = [
        "processed_logs",
        "error_frequency",
        "level_distribution",
        "component_failures",
        "temporal_analysis",
        "anomalies",
    ]

    html = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Distributed Log Analytics Status</title>
      <style>
        :root {
          color-scheme: light;
          --ink: #1f2937;
          --muted: #667085;
          --line: #d0d5dd;
          --panel: #f8fafc;
          --accent: #2563eb;
          --ok: #047857;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          font-family: Arial, Helvetica, sans-serif;
          color: var(--ink);
          background: #ffffff;
        }
        header {
          padding: 32px 24px 20px;
          border-bottom: 1px solid var(--line);
          background: #f9fafb;
        }
        main {
          max-width: 1120px;
          margin: 0 auto;
          padding: 24px;
        }
        h1 {
          margin: 0 0 8px;
          font-size: 30px;
          letter-spacing: 0;
        }
        h2 {
          margin: 0 0 12px;
          font-size: 18px;
          letter-spacing: 0;
        }
        p { color: var(--muted); line-height: 1.5; }
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 16px;
        }
        .card {
          border: 1px solid var(--line);
          border-radius: 8px;
          padding: 16px;
          background: #ffffff;
        }
        .metric {
          font-size: 24px;
          font-weight: 700;
          color: var(--accent);
          overflow-wrap: anywhere;
        }
        .label {
          color: var(--muted);
          font-size: 13px;
          margin-top: 6px;
        }
        .flow {
          padding: 16px;
          border: 1px solid var(--line);
          border-radius: 8px;
          background: var(--panel);
          overflow-x: auto;
          white-space: pre;
          line-height: 1.45;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 14px;
        }
        td, th {
          padding: 10px 8px;
          border-bottom: 1px solid var(--line);
          text-align: left;
        }
        a { color: var(--accent); }
        .ok { color: var(--ok); font-weight: 700; }
      </style>
    </head>
    <body>
      <header>
        <main>
          <h1>Distributed Log Analytics and Anomaly Detection</h1>
          <p>Large-scale batch processing on Google Cloud. No Pub/Sub and no live streaming are used.</p>
        </main>
      </header>
      <main>
        <section class="grid">
          <div class="card"><h2>Project</h2><div class="metric">{{ project_id }}</div><div class="label">GCP project</div></div>
          <div class="card"><h2>Region</h2><div class="metric">{{ region }}</div><div class="label">Dataproc and storage region</div></div>
          <div class="card"><h2>Dataset</h2><div class="metric">{{ dataset.label }}</div><div class="label">{{ dataset.detail }} | {{ dataset.size }}</div></div>
          <div class="card"><h2>Mode</h2><div class="metric">Batch</div><div class="label">Docker + GCS + Dataproc Spark + BigQuery</div></div>
        </section>

        <section class="card" style="margin-top:16px">
          <h2>Architecture</h2>
          <div class="flow">Large LogHub HDFS Dataset
  -> Docker Dataset Prep Tool
  -> Google Cloud Storage
  -> Dataproc Apache Spark
  -> BigQuery
  -> Looker Studio
  -> Dockerized Flask Status Page on Compute Engine</div>
        </section>

        <section class="grid" style="margin-top:16px">
          <div class="card">
            <h2>Cloud Storage</h2>
            <p><strong>Raw dataset:</strong><br>{{ dataset_gcs_path }}</p>
            <p><strong>Processed output:</strong><br>gs://{{ output_bucket }}/results/hdfs_full</p>
          </div>
          <div class="card">
            <h2>Dataproc</h2>
            <p class="ok">Expected cluster: log-analytics-cluster</p>
            <p>Run the documented PySpark job to process the full HDFS dataset on cloud worker nodes.</p>
          </div>
          <div class="card">
            <h2>Looker Studio</h2>
            <p><a href="{{ looker_url }}" target="_blank" rel="noreferrer">Open dashboard</a></p>
            <p>Connect charts to BigQuery table outputs.</p>
          </div>
        </section>

        <section class="card" style="margin-top:16px">
          <h2>BigQuery Tables</h2>
          <table>
            <thead><tr><th>Dataset</th><th>Table</th><th>Purpose</th></tr></thead>
            <tbody>
              {% for table in tables %}
              <tr><td>{{ bq_dataset }}</td><td>{{ table }}</td><td>Cloud-generated analytics output</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </section>

        <p>Last rendered: {{ rendered_at }}</p>
      </main>
    </body>
    </html>
    """

    return render_template_string(
        html,
        project_id=project_id,
        region=region,
        raw_bucket=raw_bucket,
        output_bucket=output_bucket,
        bq_dataset=bq_dataset,
        looker_url=looker_url,
        dataset_gcs_path=dataset_gcs_path,
        dataset=dataset_status(),
        tables=tables,
        rendered_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(env("PORT", "8080")))
