# Visualization

## Looker Studio Dashboard setup

Looker Studio (formerly Google Data Studio) is used for visualizing the logs analyzed in BigQuery.

### Steps to create the dashboard:
1. Go to [Looker Studio](https://lookerstudio.google.com/).
2. Create a **Blank Report**.
3. Add a **Data Source** and select **BigQuery**.
4. Choose your project -> `logs_dataset` -> `error_logs` table.
5. Add the following visualizations:
   - **Time Series Chart**: X-axis = `timestamp`, Y-axis = Record Count (to see error spikes over time).
   - **Bar Chart**: Dimension = `service`, Metric = Record Count (to see which service has the most errors).
   - **Table**: Show `timestamp`, `service`, `message`, and `trace_id` for recent critical logs.
