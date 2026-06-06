import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import Config
from .repositories.bigquery_repository import BigQueryRepository
from .routes import analytics_bp, query_bp, reports_bp
from .services.analytics_service import AnalyticsService
from .services.export_service import ExportService
from .services.query_service import QueryService


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_BYTES
    CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    config = Config()
    repository = BigQueryRepository(config.PROJECT_ID)
    app.extensions["analytics_service"] = AnalyticsService(repository, config)
    app.extensions["query_service"] = QueryService(repository, config)
    app.extensions["export_service"] = ExportService()

    app.register_blueprint(analytics_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(reports_bp)

    @app.get("/")
    def index():
        return jsonify(
            {
                "service": "Distributed Log Analytics API",
                "status": "running",
                "health": "/api/health",
            }
        )

    @app.errorhandler(Exception)
    def handle_error(error):
        if isinstance(error, HTTPException):
            return jsonify(
                {
                    "error": error.name,
                    "message": error.description,
                    "status": error.code,
                }
            ), error.code

        logging.exception("API request failed")
        status = 400 if isinstance(error, ValueError) else 503
        return jsonify(
            {
                "error": str(error),
                "status": status,
                "hint": "Verify Google Application Default Credentials and BigQuery access.",
            }
        ), status

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
