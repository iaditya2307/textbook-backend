import time
from functools import wraps

import jwt
from bson import ObjectId
from flask import current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def create_token(user_id: ObjectId, email: str, name: str) -> str:
    now = int(time.time())
    expiry = current_app.config["JWT_EXPIRY_SECONDS"]
    payload = {
        "sub": str(user_id),
        "email": email,
        "name": name,
        "iat": now,
        "exp": now + expiry,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def require_auth(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        payload = decode_token(header[7:].strip())
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        user = get_db().users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            return jsonify({"error": "User not found"}), 401
        g.current_user = user
        return f(*args, **kwargs)

    return wrapped


def user_public(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }