from flask import Blueprint, current_app, jsonify, request, send_file
import io


reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.get("/<format_name>")
def report(format_name):
    analytics = current_app.extensions["analytics_service"]
    exporter = current_app.extensions["export_service"]
    overview = analytics.overview()["metrics"]
    charts = analytics.dashboard_charts()
    rows = charts.get("components", [])

    if format_name == "csv":
        payload = exporter.csv_bytes(rows)
        return send_file(io.BytesIO(payload), mimetype="text/csv", as_attachment=True, download_name="component-analytics.csv")
    if format_name == "xlsx":
        payload = exporter.xlsx_bytes(rows)
        return send_file(
            io.BytesIO(payload),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="log-analytics-report.xlsx",
        )
    if format_name == "pdf":
        payload = exporter.pdf_bytes(
            "Distributed Log Analytics Report",
            [
                ("Total logs", overview.get("total_logs")),
                ("Components", overview.get("total_components")),
                ("Unique nodes", overview.get("total_nodes")),
                ("Error codes", overview.get("total_error_codes")),
                ("Stability index", overview.get("system_stability_index")),
                ("Spark status", overview.get("last_spark_job_status")),
            ],
        )
        return send_file(io.BytesIO(payload), mimetype="application/pdf", as_attachment=True, download_name="log-analytics-report.pdf")
    return jsonify({"error": "Unsupported format"}), 400
