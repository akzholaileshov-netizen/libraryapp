"""Электронды кітапхана Flask қолданбасы."""

import os
from pathlib import Path

from flask import Flask

from app.db import close_db, init_db, resolve_cover_url, seed_books
from app.routes import bp


def _resolve_database_path(app: Flask) -> Path:
    """SQLite жолы: Vercel-де /tmp (read-only filesystem), жергілікті — instance/."""
    if os.environ.get("DATABASE_PATH"):
        return Path(os.environ["DATABASE_PATH"]).expanduser()

    # Vercel serverless: жоба каталогы тек оқуға арналған.
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        return Path("/tmp/libraryapp/library.db")

    return Path(app.root_path).parent / "instance" / "library.db"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "library-dev-secret-change-in-production"
    )

    db_path = _resolve_database_path(app)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str(db_path)

    app.register_blueprint(bp)
    app.teardown_appcontext(close_db)
    app.jinja_env.globals["book_cover"] = resolve_cover_url

    # Кестелерді (және бос болса seed) іске қосу кезінде құру — /tmp ішінде де.
    with app.app_context():
        init_db()
        seed_books()

    return app
