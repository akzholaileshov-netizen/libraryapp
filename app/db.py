"""SQLite дерекқор қабаты."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import current_app, g, url_for


# Мұқабалар: Wikimedia Commons (PD / CC) — жергілікті көшірме app/static/covers/
# Мәтін: оқуға арналған үзінділер (көркем шығармалардың толық мәтіні емес).
SAMPLE_BOOKS = [
    {
        "title": "Абай жолы",
        "author": "Мұхтар Әуезов",
        "year": 1942,
        "genre": "Роман",
        "cover_url": "covers/abai-zholy.jpg",
        "content": """АБАЙ ЖОЛЫ
Мұхтар Әуезов

— Үзінді (оқу үшін үлгі) —

Күздің бір салқын күнінде Шыңғыстаудың етегіндегі ауыл тыныш жатты. Таңертеңгі шық шөп басын майлап, алыстағы тау жоталары көкшіл тұманға оранған. Жаңа ғана оянған бала Абай аулаға шығып, алысқа көз жіберді.

Әкесі Құнанбайдың үйі ауыл ортасында еді. Кіреберісте аттар байлаулы, сыртта адамдар ақырын сөйлесіп тұр. Абайдың жүрегінде бір тыныш күдік пен құштарлық араласқан сезім бар еді: «Мен кім боламын? Жол қайда?»

Кейіннен сол баланың жолы — білімге, әділдікке, халыққа қызметке қарай бет бұрды. Абай сөздің құдіретін түсінді: сөз — қару да, ем де, жарық та.

Ол жастық шағындағы кездесулерді, дос-жаранды, мұң мен қуанышты жүрекпен өлшеді. Әрбір оқиға оны тереңірек ойлауға жетеледі. Адамгершілік, білім, еңбек — осы үшеуі оның өмір компасы болды.

Кеш батқанда ауылдың үстінде жұлдыздар жарқырайды. Абай дала үнін тыңдап, өлең жолдарын ішінен қайталайды. Сол сәтте ол өз жолын анық сезгендей болды: халқының жүрегіне жол табу.

(Бұл үзінді — кітапхана демосы үшін қысқартылған оқу мәтіні.)
""",
    },
    {
        "title": "Қан мен тер",
        "author": "Әбдіжәміл Нұрпейісов",
        "year": 1970,
        "genre": "Роман",
        "cover_url": "covers/kan-men-ter.jpg",
        "content": """ҚАН МЕН ТЕР
Әбдіжәміл Нұрпейісов

— Үзінді (оқу үшін үлгі) —

Аралдың жағасында жел қатты еді. Толқындар құмды жалап, қайықшылардың дауысы алыстан естілетін. Ел тіршілігі теңізбен байланысты: балық, тұз, тер, күрес.

Еламан күн шыға бере жағаға шықты. Қолындағы тор ауыр, иығы қажыған. Бірақ ол тоқтауды білмейтін. «Адамның күші — еңбегінде», — деп ішінен қайталайтын.

Ауылда әңгіме көп: біреулердің үміті, біреулердің қайғысы. Соғыс пен бейбіт күннің арасындағы адам тағдыры осында айқын көрінеді. Қан төгілген күндер, тер төгілген күндер — бәрі тарихтың бір парағы.

Кешке от басында отырып, адамдар өткенді еске алады. Балалар тыңдайды. Қарттар үнсіз. Теңіз шуылы сол сәтте де үзілмейді.

(Бұл үзінді — кітапхана демосы үшін қысқартылған оқу мәтіні.)
""",
    },
    {
        "title": "Көшпенділер",
        "author": "Ілияс Есенберлин",
        "year": 1969,
        "genre": "Тарихи",
        "cover_url": "covers/koshpendiler.jpg",
        "content": """КӨШПЕНДІЛЕР
Ілияс Есенберлин

— Үзінді (оқу үшін үлгі) —

Ұлы дала — шексіз көкжиек. Киіз үйлердің түтіні аспанға ырғып, жылқынын кісінеуі алысқа тарайды. Бұл — көшпенділердің мекені, еркіндіктің мекені.

Хан ордасында кеңес жүріп жатыр. Біреулер соғысты айтады, біреулер бейбітшілікті. Жас батырдың жүрегі дауылдай соғады: елдің бірлігінен артық қазына жоқ.

Көш жолдары — тарихтың тамыры. Әрбір қоныс, әрбір шайқас, әрбір жыр — халықтың жадын сақтайды. Дала заңы қатал, бірақ әділ болуға тырысады.

Түнде от жанында жыршы жырлайды. Тыңдаушылардың көзінде от жарқырайды. Сол жыр арқылы өткен батырлар қайта тірілгендей.

(Бұл үзінді — кітапхана демосы үшін қысқартылған оқу мәтіні.)
""",
    },
    {
        "title": "Оян, қазақ!",
        "author": "Міржақып Дулатұлы",
        "year": 1909,
        "genre": "Публицистика",
        "cover_url": "covers/oyan-kazak.jpg",
        "content": """ОЯН, ҚАЗАҚ!
Міржақып Дулатұлы

— Оқу мәтіні (үлгі үзінді) —

Оян, қазақ, көзіңді аш,
Қараңғыны қашан жарарсың?
Жер кетті, дін кетті, мал кетті —
Енді неге қарап отырасың?

Білім — жарық, надандық — түн.
Кітап оқы, еңбек қыл, ізден.
Өз тіліңді, өз тарихыңды сүй,
Болашақтың жолы — осында.

Ағайын, бірлік болсын араңда,
Жалқаулық пен жаттан сақтан.
Ел үшін еңбек еткен жан —
Ұрпаққа үлгі, халыққа арқа.

(1909 жылғы шығарма идеясына сүйенген қысқа оқу мәтіні; демо үшін.)
""",
    },
    {
        "title": "Менің атым Қожа",
        "author": "Бердібек Соқпақбаев",
        "year": 1957,
        "genre": "Балалар әдебиеті",
        "cover_url": "covers/menin-atym-kozha.jpg",
        "content": """МЕНІҢ АТЫМ ҚОЖА
Бердібек Соқпақбаев

— Үзінді (оқу үшін үлгі) —

Менің атым — Қожа. Мен әлі кішкентаймын, бірақ мектепке барамын. Сабақ қызғылықты да, қиын да. Мұғалім күледі, дос-жаран шулайды, мен кейде тым шектен шығып кетемін.

Бір күні мен «жақсы оқушы» болуға бел будым. Бірақ ертеңгісі бәрі басқаша болып шықты: үй тапсырмасын ұмытыппын, сабақта сөйлесіп отырмын. Ұялдым.

Кешке апама айттым. Ол маған: «Қожа, адам қателеседі. Бірақ қатесін мойындап, түзеу — батырлық», — деді. Сол сөз жүрегіме қонды.

Ертеңінде мен тақтаға шығып, жауабымды ақырын, бірақ анық айттым. Сынып тынышталды. Сол сәтте мен өзгеріп келе жатқанымды сездім.

(Бұл үзінді — кітапхана демосы үшін қысқартылған оқу мәтіні.)
""",
    },
]

DEFAULT_COVER = "covers/default-cover.jpg"


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db_path = Path(current_app.config["DATABASE"])
        if not db_path.is_absolute():
            db_path = Path(current_app.root_path).parent / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_: Any = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _column_names(db: sqlite3.Connection) -> set[str]:
    rows = db.execute("PRAGMA table_info(books)").fetchall()
    return {row["name"] for row in rows}


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
            cover_url TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cols = _column_names(db)
    if "cover_url" not in cols:
        db.execute(
            "ALTER TABLE books ADD COLUMN cover_url TEXT NOT NULL DEFAULT ''"
        )
    if "content" not in cols:
        db.execute(
            "ALTER TABLE books ADD COLUMN content TEXT NOT NULL DEFAULT ''"
        )
    db.commit()


def seed_books() -> None:
    db = get_db()
    count = db.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]
    if count == 0:
        db.executemany(
            """
            INSERT INTO books (title, author, year, genre, cover_url, content)
            VALUES (:title, :author, :year, :genre, :cover_url, :content)
            """,
            SAMPLE_BOOKS,
        )
        db.commit()
        return

    # Ескі жазбаларға мұқаба/мәтін толтыру (атауы бойынша).
    for book in SAMPLE_BOOKS:
        row = db.execute(
            "SELECT id, cover_url, content FROM books WHERE title = ?",
            (book["title"],),
        ).fetchone()
        if row is None:
            continue
        cover = (row["cover_url"] or "").strip()
        content = (row["content"] or "").strip()
        if cover and content:
            continue
        db.execute(
            """
            UPDATE books
            SET cover_url = CASE WHEN cover_url IS NULL OR cover_url = '' THEN ?
                                 ELSE cover_url END,
                content = CASE WHEN content IS NULL OR content = '' THEN ?
                               ELSE content END
            WHERE id = ?
            """,
            (book["cover_url"], book["content"], row["id"]),
        )
    db.commit()


def resolve_cover_url(cover_url: str | None) -> str:
    """Статикалық жолды толық URL-ге айналдыру; сыртқы URL қалдыру."""
    value = (cover_url or "").strip() or DEFAULT_COVER
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if value.startswith("/static/"):
        return value
    return url_for("static", filename=value)


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


def create_book(
    title: str,
    author: str,
    year: int,
    genre: str,
    cover_url: str = "",
    content: str = "",
) -> int:
    db = get_db()
    cover = (cover_url or "").strip() or DEFAULT_COVER
    body = (content or "").strip() or (
        f"{title}\n{author}\n\n"
        "Бұл кітапқа әлі толық мәтін қосылмаған. "
        "Кейінірек «Өңдеу» арқылы оқу мәтінін қосуға болады."
    )
    cur = db.execute(
        """
        INSERT INTO books (title, author, year, genre, cover_url, content)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, author, year, genre, cover, body),
    )
    db.commit()
    return int(cur.lastrowid)


def update_book(
    book_id: int,
    title: str,
    author: str,
    year: int,
    genre: str,
    cover_url: str = "",
    content: str = "",
) -> bool:
    db = get_db()
    existing = get_book(book_id)
    if existing is None:
        return False
    cover = (cover_url or "").strip() or existing["cover_url"] or DEFAULT_COVER
    body = (content or "").strip() or existing["content"] or ""
    cur = db.execute(
        """
        UPDATE books
        SET title = ?, author = ?, year = ?, genre = ?,
            cover_url = ?, content = ?
        WHERE id = ?
        """,
        (title, author, year, genre, cover, body, book_id),
    )
    db.commit()
    return cur.rowcount > 0


def delete_book(book_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    return cur.rowcount > 0
