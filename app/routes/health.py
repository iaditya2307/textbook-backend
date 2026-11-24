from flask import Blueprint, jsonify
from pymongo.errors import PyMongoError

from app.db import get_db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    try:
        get_db().command("ping")
        db_ok = True
    except (RuntimeError, PyMongoError):
        db_ok = False
    status = 200 if db_ok else 503
    return jsonify({"status": "ok" if db_ok else "degraded", "database": db_ok}), status