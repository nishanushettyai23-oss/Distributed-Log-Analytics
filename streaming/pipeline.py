"""
Apache Beam Pipeline for real-time log processing.
Reads from Pub/Sub, parses logs, filters errors, and writes to BigQuery.
"""

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions
import json

# Configuration Placeholders
PROJECT_ID = "your-project-id"
SUBSCRIPTION = f"projects/{PROJECT_ID}/subscriptions/infrastructure-logs-sub"
BQ_TABLE = f"{PROJECT_ID}:logs_dataset.error_logs"

class ParseLogFn(beam.DoFn):
    """Parses JSON log strings into dictionaries."""
    def process(self, element):
        try:
            # element is a bytes object from Pub/Sub
            log_dict = json.loads(element.decode('utf-8'))
            yield log_dict
        except Exception as e:
            # Handle parsing errors (e.g., dead-letter queue)
            pass

def run():
    options = PipelineOptions(
        streaming=True, # Enable streaming mode
        project=PROJECT_ID,
        runner='DataflowRunner', # Use Dataflow for execution
        job_name='log-analytics-streaming'
    )
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as p:
        (
            p
            # 1. Read messages from Pub/Sub
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription=SUBSCRIPTION)
            
            # 2. Parse JSON logs
            | "ParseJSON" >> beam.ParDo(ParseLogFn())
            
            # 3. Filter only ERROR level logs for real-time dashboarding
            | "FilterErrors" >> beam.Filter(lambda log: log.get('level') == 'ERROR')
            
            # 4. Write resulting errors to BigQuery
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                BQ_TABLE,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER
            )
        )

if __name__ == '__main__':
    run()
