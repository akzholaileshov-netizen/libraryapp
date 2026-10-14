"""Электронды кітапхана Flask қолданбасы."""

import os
from pathlib import Path

from flask import Flask

from app.db import close_db, init_db, seed_books
from app.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "library-dev-secret-change-in-production"
    )

    # Absolute path works on ephemeral hosts (Render/Railway/Fly).
    default_db = Path(app.root_path).parent / "instance" / "library.db"
    db_path = Path(os.environ.get("DATABASE_PATH", str(default_db))).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str(db_path)

    app.register_blueprint(bp)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
        seed_books()

    return app
