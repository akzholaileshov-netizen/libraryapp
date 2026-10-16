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
from app.i18n import set_lang, t

bp = Blueprint("main", __name__)


def validate_book_form(form) -> tuple[dict | None, list[str]]:
    title = (form.get("title") or "").strip()
    author = (form.get("author") or "").strip()
    year_raw = (form.get("year") or "").strip()
    genre = (form.get("genre") or "").strip()
    cover_url = (form.get("cover_url") or "").strip()
    content = (form.get("content") or "").strip()
    title_en = (form.get("title_en") or "").strip()
    title_ru = (form.get("title_ru") or "").strip()
    genre_en = (form.get("genre_en") or "").strip()
    genre_ru = (form.get("genre_ru") or "").strip()
    content_en = (form.get("content_en") or "").strip()
    content_ru = (form.get("content_ru") or "").strip()

    errors: list[str] = []

    if not title:
        errors.append(t("err_title"))
    if not author:
        errors.append(t("err_author"))
    if not year_raw:
        errors.append(t("err_year_empty"))
    if not genre:
        errors.append(t("err_genre"))

    year: int | None = None
    if year_raw:
        try:
            year = int(year_raw)
        except ValueError:
            errors.append(t("err_year_int"))

    if errors:
        return None, errors

    return {
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
        "cover_url": cover_url,
        "content": content,
        "title_en": title_en,
        "title_ru": title_ru,
        "genre_en": genre_en,
        "genre_ru": genre_ru,
        "content_en": content_en,
        "content_ru": content_ru,
    }, []


def _form_snapshot(form) -> dict:
    keys = (
        "title", "author", "year", "genre", "cover_url", "content",
        "title_en", "title_ru", "genre_en", "genre_ru", "content_en", "content_ru",
    )
    return {k: (form.get(k) or "").strip() for k in keys}


def _empty_form() -> dict:
    return {k: "" for k in (
        "title", "author", "year", "genre", "cover_url", "content",
        "title_en", "title_ru", "genre_en", "genre_ru", "content_en", "content_ru",
    )}


@bp.route("/lang/<code>")
def set_language(code: str):
    set_lang(code)
    nxt = request.args.get("next") or request.referrer or url_for("main.index")
    return redirect(nxt)


@bp.route("/")
def index():
    query = (request.args.get("q") or "").strip()
    books = get_all_books(query or None)
    return render_template("index.html", books=books, query=query)


@bp.route("/books/<int:book_id>")
def read_book(book_id: int):
    book = get_book(book_id)
    if book is None:
        flash(t("flash_not_found"), "warning")
        return redirect(url_for("main.index"))
    return render_template("reader.html", book=book)


@bp.route("/books/new", methods=["GET", "POST"])
def add_book():
    form_data = _empty_form()

    if request.method == "POST":
        data, errors = validate_book_form(request.form)
        form_data = _form_snapshot(request.form)
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "book_form.html", mode="add", form_data=form_data
            ), 400

        create_book(**data)
        flash(t("flash_added"), "success")
        return redirect(url_for("main.index"))

    return render_template("book_form.html", mode="add", form_data=form_data)


@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id: int):
    book = get_book(book_id)
    if book is None:
        flash(t("flash_not_found"), "warning")
        return redirect(url_for("main.index"))

    form_data = {
        "title": book["title"],
        "author": book["author"],
        "year": str(book["year"]),
        "genre": book["genre"],
        "cover_url": book["cover_url"] or "",
        "content": book["content"] or "",
        "title_en": book["title_en"] if "title_en" in book.keys() else "",
        "title_ru": book["title_ru"] if "title_ru" in book.keys() else "",
        "genre_en": book["genre_en"] if "genre_en" in book.keys() else "",
        "genre_ru": book["genre_ru"] if "genre_ru" in book.keys() else "",
        "content_en": book["content_en"] if "content_en" in book.keys() else "",
        "content_ru": book["content_ru"] if "content_ru" in book.keys() else "",
    }

    if request.method == "POST":
        data, errors = validate_book_form(request.form)
        form_data = _form_snapshot(request.form)
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "book_form.html",
                mode="edit",
                book_id=book_id,
                form_data=form_data,
            ), 400

        update_book(book_id, **data)
        flash(t("flash_updated"), "success")
        return redirect(url_for("main.index"))

    return render_template(
        "book_form.html", mode="edit", book_id=book_id, form_data=form_data
    )


@bp.route("/books/<int:book_id>/delete", methods=["POST"])
def remove_book(book_id: int):
    if delete_book(book_id):
        flash(t("flash_deleted"), "success")
    else:
        flash(t("flash_not_found"), "warning")
    return redirect(url_for("main.index"))
