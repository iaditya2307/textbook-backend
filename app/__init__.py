from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.db import close_db, init_db


def create_app(config: type[Config] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config or Config)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    init_db(app)
    app.teardown_appcontext(close_db)

    from app.routes.auth import auth_bp
    from app.routes.books import books_bp
    from app.routes.health import health_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(books_bp, url_prefix="/api/books")

    return app