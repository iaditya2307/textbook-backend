from flask import Blueprint, jsonify, request

from app.auth_utils import create_token, hash_password, user_public, verify_password
from app.db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400
    if not name:
        local = email.split("@")[0] or "learner"
        name = local[:1].upper() + local[1:]

    db = get_db()
    if db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists"}), 409

    doc = {
        "email": email,
        "name": name,
        "password_hash": hash_password(password),
    }
    result = db.users.insert_one(doc)
    doc["_id"] = result.inserted_id

    token = create_token(doc["_id"], email, name)
    return jsonify({"user": user_public(doc), "token": token}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = get_db().users.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_token(user["_id"], user["email"], user["name"])
    return jsonify({"user": user_public(user), "token": token})