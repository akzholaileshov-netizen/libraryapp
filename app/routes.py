"""Маршруттар мен пішін валидациясы."""

from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.db import (
    create_book,
    delete_book,
    get_all_books,
    get_book,
    update_book,
)

bp = Blueprint("main", __name__)


def validate_book_form(form) -> tuple[dict | None, list[str]]:
    """Бос өрістерді және жылдың бүтін сан екенін тексеру."""
    title = (form.get("title") or "").strip()
    author = (form.get("author") or "").strip()
    year_raw = (form.get("year") or "").strip()
    genre = (form.get("genre") or "").strip()

    errors: list[str] = []
    data = {
        "title": title,
        "author": author,
        "year": year_raw,
        "genre": genre,
    }

    if not title:
        errors.append("Атауы бос болмауы керек.")
    if not author:
        errors.append("Авторы бос болмауы керек.")
    if not year_raw:
        errors.append("Жыл бос болмауы керек.")
    if not genre:
        errors.append("Жанр бос болмауы керек.")

    year: int | None = None
    if year_raw:
        try:
            year = int(year_raw)
        except ValueError:
            errors.append("Жыл бүтін сан болуы керек.")

    if errors:
        return None, errors

    return {
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
    }, []


@bp.route("/")
def index():
    query = (request.args.get("q") or "").strip()
    books = get_all_books(query or None)
    return render_template(
        "index.html",
        books=books,
        query=query,
    )


@bp.route("/books/new", methods=["GET", "POST"])
def add_book():
    form_data = {"title": "", "author": "", "year": "", "genre": ""}

    if request.method == "POST":
        data, errors = validate_book_form(request.form)
        form_data = {
            "title": (request.form.get("title") or "").strip(),
            "author": (request.form.get("author") or "").strip(),
            "year": (request.form.get("year") or "").strip(),
            "genre": (request.form.get("genre") or "").strip(),
        }
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "book_form.html",
                mode="add",
                form_data=form_data,
            ), 400

        create_book(data["title"], data["author"], data["year"], data["genre"])
        flash("Кітап сәтті қосылды.", "success")
        return redirect(url_for("main.index"))

    return render_template(
        "book_form.html",
        mode="add",
        form_data=form_data,
    )


@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id: int):
    book = get_book(book_id)
    if book is None:
        flash("Кітап табылмады.", "warning")
        return redirect(url_for("main.index"))

    form_data = {
        "title": book["title"],
        "author": book["author"],
        "year": str(book["year"]),
        "genre": book["genre"],
    }

    if request.method == "POST":
        data, errors = validate_book_form(request.form)
        form_data = {
            "title": (request.form.get("title") or "").strip(),
            "author": (request.form.get("author") or "").strip(),
            "year": (request.form.get("year") or "").strip(),
            "genre": (request.form.get("genre") or "").strip(),
        }
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "book_form.html",
                mode="edit",
                book_id=book_id,
                form_data=form_data,
            ), 400

        update_book(
            book_id,
            data["title"],
            data["author"],
            data["year"],
            data["genre"],
        )
        flash("Кітап жаңартылды.", "success")
        return redirect(url_for("main.index"))

    return render_template(
        "book_form.html",
        mode="edit",
        book_id=book_id,
        form_data=form_data,
    )


@bp.route("/books/<int:book_id>/delete", methods=["POST"])
def remove_book(book_id: int):
    if delete_book(book_id):
        flash("Кітап жойылды.", "success")
    else:
        flash("Кітап табылмады.", "warning")
    return redirect(url_for("main.index"))
