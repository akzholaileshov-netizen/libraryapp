"""Электронды кітапхана Flask қолданбасы."""

from flask import Flask

from app.db import close_db, init_db, seed_books
from app.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "library-dev-secret-change-in-production"
    app.config["DATABASE"] = "instance/library.db"

    app.register_blueprint(bp)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
        seed_books()

    return app
