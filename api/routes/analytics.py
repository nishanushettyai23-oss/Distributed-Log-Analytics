import hmac

from flask import Blueprint, current_app, jsonify, request


analytics_bp = Blueprint("analytics", __name__, url_prefix="/api")


def service():
    return current_app.extensions["analytics_service"]


def require_admin():
    expected = str(current_app.config.get("PIPELINE_ADMIN_TOKEN") or "")
    supplied = request.headers.get("X-Admin-Token", "")
    if not expected:
        return jsonify({"error": "Dataset administration is disabled until PIPELINE_ADMIN_TOKEN is configured."}), 503
    if not hmac.compare_digest(expected, supplied):
        return jsonify({"error": "Invalid administrator token."}), 403
    return None


@analytics_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "distributed-log-analytics-api"})


@analytics_bp.get("/overview")
def overview():
    return jsonify(service().overview())


@analytics_bp.get("/analytics")
def analytics():
    return jsonify(service().dashboard_charts())


@analytics_bp.get("/anomalies")
def anomalies():
    return jsonify(service().anomalies())


@analytics_bp.get("/logs")
def logs():
    return jsonify(service().explore(request.args))


@analytics_bp.get("/filters")
def filters():
    return jsonify(service().filter_options())


@analytics_bp.get("/infrastructure")
def infrastructure():
    return jsonify(service().infrastructure())


@analytics_bp.post("/admin/verify")
def verify_admin():
    denied = require_admin()
    if denied:
        return denied
    return jsonify({"valid": True, "message": "Administrator access verified."})


@analytics_bp.post("/pipeline/submit")
def submit_pipeline():
    denied = require_admin()
    if denied:
        return denied

    payload = request.get_json(silent=True) or {}
    return jsonify(
        service().submit_pipeline(
            str(payload.get("input_uri") or "").strip(),
            str(payload.get("output_name") or "").strip(),
        )
    ), 202


@analytics_bp.post("/datasets/upload")
def upload_dataset():
    denied = require_admin()
    if denied:
        return denied
    if request.content_length and request.content_length > current_app.config["MAX_UPLOAD_BYTES"]:
        return jsonify({"error": "Dataset exceeds the configured upload limit."}), 413
    dataset = request.files.get("dataset")
    if not dataset:
        return jsonify({"error": "Multipart field 'dataset' is required."}), 400
    return jsonify(service().store_dataset(dataset)), 201
