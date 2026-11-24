from flask import Flask, current_app, g
from pymongo import MongoClient
from pymongo.database import Database


def get_client() -> MongoClient:
    if "mongo_client" not in g:
        uri = current_app.config["MONGODB_URI"]
        if not uri:
            raise RuntimeError("MONGODB_URI is not set. Copy .env.example to .env")
        g.mongo_client = MongoClient(uri)
    return g.mongo_client


def get_db() -> Database:
    if "mongo_db" not in g:
        name = current_app.config["MONGODB_DB_NAME"]
        g.mongo_db = get_client()[name]
    return g.mongo_db


def init_db(app: Flask) -> None:
    @app.cli.command("ensure-indexes")
    def ensure_indexes_command() -> None:
        with app.app_context():
            db = get_db()
            db.users.create_index("email", unique=True)
            db.books.create_index([("user_id", 1), ("id", 1)], unique=True)
            print("Indexes OK")


def close_db(_exc: BaseException | None = None) -> None:
    client = g.pop("mongo_client", None)
    if client is not None:
        client.close()
    g.pop("mongo_db", None)