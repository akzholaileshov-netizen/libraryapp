"""SQLite дерекқор қабаты."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import current_app, g


SAMPLE_BOOKS = [
    ("Абай жолы", "Мұхтар Әуезов", 1942, "Роман"),
    ("Қан мен тер", "Әбдіжәміл Нұрпейісов", 1970, "Роман"),
    ("Көшпенділер", "Ілияс Есенберлин", 1969, "Тарихи"),
    ("Оян, қазақ!", "Міржақып Дулатұлы", 1909, "Публицистика"),
    ("Менің атым Қожа", "Бердібек Соқпақбаев", 1957, "Балалар әдебиеті"),
]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db_path = Path(current_app.root_path).parent / current_app.config["DATABASE"]
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_: Any = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


def seed_books() -> None:
    db = get_db()
    count = db.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]
    if count > 0:
        return
    db.executemany(
        "INSERT INTO books (title, author, year, genre) VALUES (?, ?, ?, ?)",
        SAMPLE_BOOKS,
    )
    db.commit()


def get_all_books(query: str | None = None) -> list[sqlite3.Row]:
    db = get_db()
    if query:
        like = f"%{query.strip()}%"
        return db.execute(
            """
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
            ORDER BY title COLLATE NOCASE
            """,
            (like, like, like),
        ).fetchall()
    return db.execute(
        "SELECT * FROM books ORDER BY title COLLATE NOCASE"
    ).fetchall()


def get_book(book_id: int) -> sqlite3.Row | None:
    return (
        get_db()
        .execute("SELECT * FROM books WHERE id = ?", (book_id,))
        .fetchone()
    )


def create_book(title: str, author: str, year: int, genre: str) -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO books (title, author, year, genre) VALUES (?, ?, ?, ?)",
        (title, author, year, genre),
    )
    db.commit()
    return int(cur.lastrowid)


def update_book(
    book_id: int, title: str, author: str, year: int, genre: str
) -> bool:
    db = get_db()
    cur = db.execute(
        """
        UPDATE books
        SET title = ?, author = ?, year = ?, genre = ?
        WHERE id = ?
        """,
        (title, author, year, genre, book_id),
    )
    db.commit()
    return cur.rowcount > 0


def delete_book(book_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    return cur.rowcount > 0
