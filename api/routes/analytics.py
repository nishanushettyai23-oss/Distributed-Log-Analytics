from flask import Blueprint, current_app, jsonify, request


analytics_bp = Blueprint("analytics", __name__, url_prefix="/api")


def service():
    return current_app.extensions["analytics_service"]


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
