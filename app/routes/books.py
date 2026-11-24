from flask import Blueprint, g, jsonify, request
from pymongo import ReturnDocument

from app.auth_utils import require_auth
from app.db import get_db

books_bp = Blueprint("books", __name__)

BOOK_FIELDS = (
    "id",
    "title",
    "subject",
    "author",
    "pages",
    "progress",
    "difficulty",
    "cover",
    "lastOpened",
    "tags",
    "hasPdf",
)


def serialize_book(doc: dict) -> dict:
    out = {k: doc.get(k) for k in BOOK_FIELDS if k in doc}
    out.setdefault("tags", [])
    out.setdefault("progress", 0)
    out.setdefault("difficulty", 0)
    out.setdefault("hasPdf", False)
    return out


@books_bp.get("")
@require_auth
def list_books():
    user_id = g.current_user["_id"]
    cursor = get_db().books.find({"user_id": user_id}).sort("lastOpened", -1)
    return jsonify({"books": [serialize_book(b) for b in cursor]})


@books_bp.get("/<book_id>")
@require_auth
def get_book(book_id: str):
    user_id = g.current_user["_id"]
    doc = get_db().books.find_one({"user_id": user_id, "id": book_id})
    if not doc:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"book": serialize_book(doc)})


@books_bp.post("")
@require_auth
def create_book():
    data = request.get_json(silent=True) or {}
    book_id = (data.get("id") or "").strip()
    title = (data.get("title") or "").strip()
    if not book_id or not title:
        return jsonify({"error": "id and title are required"}), 400

    user_id = g.current_user["_id"]
    db = get_db()
    if db.books.find_one({"user_id": user_id, "id": book_id}):
        return jsonify({"error": "Book with this id already exists"}), 409

    doc = {
        "user_id": user_id,
        "id": book_id,
        "title": title,
        "subject": data.get("subject", ""),
        "author": data.get("author", ""),
        "pages": int(data.get("pages") or 0),
        "progress": int(data.get("progress") or 0),
        "difficulty": int(data.get("difficulty") or 0),
        "cover": data.get("cover", "from-[#191919] to-[#6b6b66]"),
        "lastOpened": data.get("lastOpened", ""),
        "tags": data.get("tags") or [],
        "hasPdf": bool(data.get("hasPdf", False)),
    }
    db.books.insert_one(doc)
    return jsonify({"book": serialize_book(doc)}), 201


@books_bp.patch("/<book_id>")
@require_auth
def update_book(book_id: str):
    data = request.get_json(silent=True) or {}
    user_id = g.current_user["_id"]
    db = get_db()

    allowed = {k: data[k] for k in BOOK_FIELDS if k in data and k != "id"}
    if not allowed:
        return jsonify({"error": "No valid fields to update"}), 400

    result = db.books.find_one_and_update(
        {"user_id": user_id, "id": book_id},
        {"$set": allowed},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"book": serialize_book(result)})


@books_bp.delete("/<book_id>")
@require_auth
def delete_book(book_id: str):
    user_id = g.current_user["_id"]
    result = get_db().books.delete_one({"user_id": user_id, "id": book_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"ok": True})