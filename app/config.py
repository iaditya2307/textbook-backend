import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-in-production")
    MONGODB_URI = os.environ.get("MONGODB_URI", "")
    MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "textbook")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    JWT_EXPIRY_SECONDS = int(os.environ.get("JWT_EXPIRY_SECONDS", "604800"))  # 7 days