import io

from flask import Blueprint, current_app, jsonify, request, send_file


query_bp = Blueprint("query", __name__, url_prefix="/api/query")


@query_bp.post("")
def execute():
    payload = request.get_json(silent=True) or {}
    sql = payload.get("sql", "")
    return jsonify(current_app.extensions["query_service"].execute(sql))


@query_bp.get("/history")
def history():
    return jsonify(list(current_app.extensions["query_service"].history))


@query_bp.post("/export/<format_name>")
def export_query(format_name):
    payload = request.get_json(silent=True) or {}
    result = current_app.extensions["query_service"].execute(payload.get("sql", ""))
    exporter = current_app.extensions["export_service"]
    if format_name == "csv":
        data = exporter.csv_bytes(result["rows"])
        return send_file(io.BytesIO(data), mimetype="text/csv", as_attachment=True, download_name="bigquery-results.csv")
    if format_name == "xlsx":
        data = exporter.xlsx_bytes(result["rows"])
        return send_file(
            io.BytesIO(data),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="bigquery-results.xlsx",
        )
    return jsonify({"error": "Unsupported format"}), 400
