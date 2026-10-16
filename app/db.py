"""SQLite дерекқор қабаты."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import current_app, g, url_for


# Мұқабалар: Wikimedia Commons (PD / CC) — app/static/covers/
# Мәтін: көптілді оқу үзінділері (демо).
SAMPLE_BOOKS = [
    {
        "title": "Абай жолы",
        "title_en": "The Path of Abai",
        "title_ru": "Путь Абая",
        "author": "Мұхтар Әуезов",
        "year": 1942,
        "genre": "Роман",
        "genre_en": "Novel",
        "genre_ru": "Роман",
        "cover_url": "covers/abai-zholy.jpg",
        "wiki_kk": "Абай жолы",
        "wiki_en": "Abai Qunanbaiuly",
        "wiki_ru": "Путь Абая",
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
        "content_en": """THE PATH OF ABAI
Mukhtar Auezov

— Reading excerpt (demo) —

On a cool autumn day the village at the foot of Shyngystau lay quiet. Morning dew silvered the grass, and distant ridges were wrapped in blue mist. Young Abai stepped into the yard and looked far away.

His father Kunanbai's house stood in the middle of the aul. Horses waited at the entrance; people spoke softly outside. In Abai's heart curiosity and doubt mixed: "Who will I become? Where is my path?"

Later that boy's path turned toward knowledge, justice, and service to the people. Abai learned the power of the word: a weapon, a remedy, and a light.

In youth he measured friendships, sorrow, and joy with his heart. Every event pushed him to think deeper. Humanity, learning, and labor became his compass.

When evening fell, stars brightened above the village. Abai listened to the steppe and repeated lines of verse within himself. In that moment he felt his path clearly: to reach the heart of his people.

(This excerpt is a shortened demo text for the library app.)
""",
        "content_ru": """ПУТЬ АБАЯ
Мухтар Ауэзов

— Отрывок для чтения (демо) —

В прохладный осенний день аул у подножия Чингистау лежал тихо. Утренняя роса серебрила траву, а дальние хребты окутывал голубой туман. Юный Абай вышел во двор и посмотрел вдаль.

Дом отца Кунанбая стоял в центре аула. У входа стояли кони, снаружи люди говорили тихо. В сердце Абая смешались сомнение и жажда: «Кем я стану? Где мой путь?»

Позже путь того мальчика повернул к знанию, справедливости и служению народу. Абай понял силу слова: это и оружие, и лекарство, и свет.

В юности он мерил дружбу, печаль и радость сердцем. Каждое событие вело его к более глубокой мысли. Человечность, учение и труд стали его компасом.

Когда сгущался вечер, над аулом зажигались звёзды. Абай слушал голос степи и повторял строки стихов про себя. В тот миг он ясно почувствовал свой путь: найти дорогу к сердцу народа.

(Это сокращённый демо-текст для библиотеки.)
""",
    },
    {
        "title": "Қан мен тер",
        "title_en": "Blood and Sweat",
        "title_ru": "Кровь и пот",
        "author": "Әбдіжәміл Нұрпейісов",
        "year": 1970,
        "genre": "Роман",
        "genre_en": "Novel",
        "genre_ru": "Роман",
        "cover_url": "covers/kan-men-ter.jpg",
        "wiki_kk": "Қан мен тер",
        "wiki_en": "Abdizhamil Nurpeisov",
        "wiki_ru": "Нурпеисов, Абдижамил Каримович",
        "content": """ҚАН МЕН ТЕР
Әбдіжәміл Нұрпейісов

— Үзінді (оқу үшін үлгі) —

Аралдың жағасында жел қатты еді. Толқындар құмды жалап, қайықшылардың дауысы алыстан естілетін. Ел тіршілігі теңізбен байланысты: балық, тұз, тер, күрес.

Еламан күн шыға бере жағаға шықты. Қолындағы тор ауыр, иығы қажыған. Бірақ ол тоқтауды білмейтін. «Адамның күші — еңбегінде», — деп ішінен қайталайтын.

Ауылда әңгіме көп: біреулердің үміті, біреулердің қайғысы. Соғыс пен бейбіт күннің арасындағы адам тағдыры осында айқын көрінеді. Қан төгілген күндер, тер төгілген күндер — бәрі тарихтың бір парағы.

Кешке от басында отырып, адамдар өткенді еске алады. Балалар тыңдайды. Қарттар үнсіз. Теңіз шуылы сол сәтте де үзілмейді.

(Бұл үзінді — кітапхана демосы үшін қысқартылған оқу мәтіні.)
""",
        "content_en": """BLOOD AND SWEAT
Abdizhamil Nurpeisov

— Reading excerpt (demo) —

The wind was strong on the Aral shore. Waves licked the sand, and boatmen's voices carried from afar. Life was tied to the sea: fish, salt, sweat, struggle.

Elaman came to the shore at sunrise. His net was heavy, his shoulders tired. Still he would not stop. "A person's strength is in labor," he repeated to himself.

In the village talk was endless: someone's hope, someone's grief. Between war and peace, human fate shows clearly here. Days of blood and days of sweat are pages of one history.

In the evening by the fire people remember the past. Children listen. Elders stay silent. The sea's murmur does not pause.

(This excerpt is a shortened demo text for the library app.)
""",
        "content_ru": """КРОВЬ И ПОТ
Абдижамил Нурпеисов

— Отрывок для чтения (демо) —

На берегу Арала дул сильный ветер. Волны лизали песок, голоса рыбаков доносились издалека. Жизнь была связана с морем: рыба, соль, пот, борьба.

Еламан вышел к берегу на рассвете. Сеть была тяжёлой, плечи устали. Но он не умел останавливаться. «Сила человека — в труде», — повторял он про себя.

В ауле много разговоров: чья-то надежда, чья-то печаль. Между войной и миром здесь ясно видна судьба человека. Дни крови и дни пота — страницы одной истории.

Вечером у огня люди вспоминают прошлое. Дети слушают. Старики молчат. Шум моря не умолкает.

(Это сокращённый демо-текст для библиотеки.)
""",
    },
    {
        "title": "Көшпенділер",
        "title_en": "The Nomads",
        "title_ru": "Кочевники",
        "author": "Ілияс Есенберлин",
        "year": 1969,
        "genre": "Тарихи",
        "genre_en": "Historical",
        "genre_ru": "Исторический",
        "cover_url": "covers/koshpendiler.jpg",
        "wiki_kk": "Көшпенділер",
        "wiki_en": "Ilyas Yesenberlin",
        "wiki_ru": "Кочевники (трилогия)",
        "content": """КӨШПЕНДІЛЕР
Ілияс Есенберлин

— Үзінді (оқу үшін үлгі) —

Ұлы дала — шексіз көкжиек. Киіз үйлердің түтіні аспанға ырғып, жылқынын кісінеуі алысқа тарайды. Бұл — көшпенділердің мекені, еркіндіктің мекені.

Хан ордасында кеңес жүріп жатыр. Біреулер соғысты айтады, біреулер бейбітшілікті. Жас батырдың жүрегі дауылдай соғады: елдің бірлігінен артық қазына жоқ.

Көш жолдары — тарихтың тамыры. Әрбір қоныс, әрбір шайқас, әрбір жыр — халықтың жадын сақтайды. Дала заңы қатал, бірақ әділ болуға тырысады.

Түнде от жанында жыршы жырлайды. Тыңдаушылардың көзінде от жарқырайды. Сол жыр арқылы өткен батырлар қайта тірілгендей.

(Бұл үзінді — кітапхана демосы үшін қысқартылған оқу мәтіні.)
""",
        "content_en": """THE NOMADS
Ilyas Yesenberlin

— Reading excerpt (demo) —

The great steppe is an endless horizon. Smoke from yurts rises, and the neighing of horses carries far. This is the home of nomads, the home of freedom.

In the khan's camp a council is underway. Some speak of war, others of peace. A young batyr's heart pounds like a storm: no treasure is greater than the unity of the people.

Migration routes are the roots of history. Every camp, every battle, every song keeps the people's memory. The law of the steppe is stern, yet it strives to be just.

At night by the fire a singer performs. Fire shines in the listeners' eyes. Through that song past heroes seem to live again.

(This excerpt is a shortened demo text for the library app.)
""",
        "content_ru": """КОЧЕВНИКИ
Ильяс Есенберлин

— Отрывок для чтения (демо) —

Великая степь — бесконечный горизонт. Дым юрт поднимается к небу, ржание коней разносится далеко. Это край кочевников, край свободы.

В ханской орде идёт совет. Одни говорят о войне, другие о мире. Сердце юного батыра бьётся бурей: нет сокровища дороже единства народа.

Пути кочевий — корни истории. Каждый стан, каждая битва, каждая песнь хранят память народа. Закон степи суров, но стремится быть справедливым.

Ночью у огня жырши поёт. В глазах слушателей горит огонь. Через ту песнь оживают батыры прошлого.

(Это сокращённый демо-текст для библиотеки.)
""",
    },
    {
        "title": "Оян, қазақ!",
        "title_en": "Wake Up, Kazakh!",
        "title_ru": "Проснись, казах!",
        "author": "Міржақып Дулатұлы",
        "year": 1909,
        "genre": "Публицистика",
        "genre_en": "Publicism",
        "genre_ru": "Публицистика",
        "cover_url": "covers/oyan-kazak.jpg",
        "wiki_kk": "Міржақып Дулатұлы",
        "wiki_en": "Mirjaqip Dulatuli",
        "wiki_ru": "Дулатов, Миржакип",
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
        "content_en": """WAKE UP, KAZAKH!
Mirjaqip Dulatuly

— Reading excerpt (demo) —

Wake up, Kazakh, open your eyes —
How long will darkness remain?
Land, faith, and herds were lost —
Why sit and wait now?

Knowledge is light; ignorance is night.
Read books, work, seek.
Love your language and your history —
The road to the future is here.

Kinfolk, let unity stand among you;
Beware of laziness and alien ways.
Those who labor for the people
Become a model for the next generation.

(A short demo text inspired by the 1909 work.)
""",
        "content_ru": """ПРОСНИСЬ, КАЗАХ!
Миржакып Дулатов

— Отрывок для чтения (демо) —

Проснись, казах, открой глаза —
Доколе тьма господствует?
Земля ушла, вера ушла, скот ушёл —
Чего же ты ждёшь теперь?

Знание — свет, невежество — ночь.
Читай книги, трудись, ищи.
Люби свой язык и свою историю —
Путь в будущее здесь.

Братья, пусть будет единство между вами;
Берегитесь лени и чуждого.
Кто трудится для народа —
Тот пример для потомков.

(Краткий демо-текст по мотивам произведения 1909 года.)
""",
    },
    {
        "title": "Менің атым Қожа",
        "title_en": "My Name Is Kozha",
        "title_ru": "Меня зовут Кожа",
        "author": "Бердібек Соқпақбаев",
        "year": 1957,
        "genre": "Балалар әдебиеті",
        "genre_en": "Children's literature",
        "genre_ru": "Детская литература",
        "cover_url": "covers/menin-atym-kozha.jpg",
        "wiki_kk": "Менің атым Қожа",
        "wiki_en": "Berdibek Soqpaqbaev",
        "wiki_ru": "Меня зовут Кожа",
        "content": """МЕНІҢ АТЫМ ҚОЖА
Бердібек Соқпақбаев

— Үзінді (оқу үшін үлгі) —

Менің атым — Қожа. Мен әлі кішкентаймын, бірақ мектепке барамын. Сабақ қызғылықты да, қиын да. Мұғалім күледі, дос-жаран шулайды, мен кейде тым шектен шығып кетемін.

Бір күні мен «жақсы оқушы» болуға бел будым. Бірақ ертеңгісі бәрі басқаша болып шықты: үй тапсырмасын ұмытыппын, сабақта сөйлесіп отырмын. Ұялдым.

Кешке апама айттым. Ол маған: «Қожа, адам қателеседі. Бірақ қатесін мойындап, түзеу — батырлық», — деді. Сол сөз жүрегіме қонды.

Ертеңінде мен тақтаға шығып, жауабымды ақырын, бірақ анық айттым. Сынып тынышталды. Сол сәтте мен өзгеріп келе жатқанымды сездім.

(Бұл үзінді — кітапхана демосы үшін қысқартылған оқу мәтіні.)
""",
        "content_en": """MY NAME IS KOZHA
Berdibek Sokpakbaev

— Reading excerpt (demo) —

My name is Kozha. I am still little, but I go to school. Lessons are interesting and hard. The teacher smiles, friends chatter, and sometimes I go too far.

One day I decided to become a "good student." But the next morning everything went wrong: I forgot homework and talked in class. I felt ashamed.

In the evening I told my mother. She said: "Kozha, people make mistakes. Admitting them and fixing them is bravery." Those words stayed in my heart.

The next day I went to the board and answered slowly but clearly. The class grew quiet. In that moment I felt myself changing.

(This excerpt is a shortened demo text for the library app.)
""",
        "content_ru": """МЕНЯ ЗОВУТ КОЖА
Бердибек Сокпакбаев

— Отрывок для чтения (демо) —

Меня зовут Кожа. Я ещё маленький, но уже хожу в школу. Уроки интересные и трудные. Учитель улыбается, друзья шумят, а я иногда захожу слишком далеко.

Однажды я решил стать «хорошим учеником». Но на другой день всё пошло иначе: я забыл домашнее задание и болтал на уроке. Мне стало стыдно.

Вечером я рассказал маме. Она сказала: «Кожа, люди ошибаются. Но признать ошибку и исправить её — это мужество». Эти слова запали мне в сердце.

На другой день я вышел к доске и ответил тихо, но ясно. Класс затих. В тот миг я почувствовал, что меняюсь.

(Это сокращённый демо-текст для библиотеки.)
""",
    },
]

DEFAULT_COVER = "covers/default-cover.jpg"

I18N_COLUMNS = (
    "title_en",
    "title_ru",
    "genre_en",
    "genre_ru",
    "content_en",
    "content_ru",
)

WIKI_COLUMNS = (
    "wiki_kk",
    "wiki_en",
    "wiki_ru",
)


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
            title_en TEXT NOT NULL DEFAULT '',
            title_ru TEXT NOT NULL DEFAULT '',
            author TEXT NOT NULL,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            genre_en TEXT NOT NULL DEFAULT '',
            genre_ru TEXT NOT NULL DEFAULT '',
            cover_url TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            content_en TEXT NOT NULL DEFAULT '',
            content_ru TEXT NOT NULL DEFAULT '',
            wiki_kk TEXT NOT NULL DEFAULT '',
            wiki_en TEXT NOT NULL DEFAULT '',
            wiki_ru TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cols = _column_names(db)
    for col in ("cover_url", "content", *I18N_COLUMNS, *WIKI_COLUMNS):
        if col not in cols:
            db.execute(
                f"ALTER TABLE books ADD COLUMN {col} TEXT NOT NULL DEFAULT ''"
            )
    db.commit()


def seed_books() -> None:
    db = get_db()
    count = db.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]
    if count == 0:
        db.executemany(
            """
            INSERT INTO books (
                title, title_en, title_ru, author, year,
                genre, genre_en, genre_ru, cover_url,
                content, content_en, content_ru,
                wiki_kk, wiki_en, wiki_ru
            ) VALUES (
                :title, :title_en, :title_ru, :author, :year,
                :genre, :genre_en, :genre_ru, :cover_url,
                :content, :content_en, :content_ru,
                :wiki_kk, :wiki_en, :wiki_ru
            )
            """,
            SAMPLE_BOOKS,
        )
        db.commit()
        return

    for book in SAMPLE_BOOKS:
        row = db.execute(
            "SELECT * FROM books WHERE title = ?",
            (book["title"],),
        ).fetchone()
        if row is None:
            continue
        updates = []
        values = []
        for key in (
            "cover_url",
            "content",
            "title_en",
            "title_ru",
            "genre_en",
            "genre_ru",
            "content_en",
            "content_ru",
            "wiki_kk",
            "wiki_en",
            "wiki_ru",
        ):
            current = (row[key] if key in row.keys() else "") or ""
            if not str(current).strip():
                updates.append(f"{key} = ?")
                values.append(book[key])
        if updates:
            values.append(row["id"])
            db.execute(
                f"UPDATE books SET {', '.join(updates)} WHERE id = ?",
                values,
            )
    db.commit()


def resolve_cover_url(cover_url: str | None) -> str:
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
            WHERE title LIKE ? OR title_en LIKE ? OR title_ru LIKE ?
               OR author LIKE ?
               OR genre LIKE ? OR genre_en LIKE ? OR genre_ru LIKE ?
            ORDER BY title COLLATE NOCASE
            """,
            (like, like, like, like, like, like, like),
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
    title_en: str = "",
    title_ru: str = "",
    genre_en: str = "",
    genre_ru: str = "",
    content_en: str = "",
    content_ru: str = "",
    wiki_kk: str = "",
    wiki_en: str = "",
    wiki_ru: str = "",
) -> int:
    db = get_db()
    cover = (cover_url or "").strip() or DEFAULT_COVER
    body = (content or "").strip() or f"{title}\n{author}\n\n"
    cur = db.execute(
        """
        INSERT INTO books (
            title, title_en, title_ru, author, year,
            genre, genre_en, genre_ru, cover_url,
            content, content_en, content_ru,
            wiki_kk, wiki_en, wiki_ru
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            (title_en or "").strip(),
            (title_ru or "").strip(),
            author,
            year,
            genre,
            (genre_en or "").strip(),
            (genre_ru or "").strip(),
            cover,
            body,
            (content_en or "").strip(),
            (content_ru or "").strip(),
            (wiki_kk or "").strip(),
            (wiki_en or "").strip(),
            (wiki_ru or "").strip(),
        ),
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
    title_en: str = "",
    title_ru: str = "",
    genre_en: str = "",
    genre_ru: str = "",
    content_en: str = "",
    content_ru: str = "",
    wiki_kk: str = "",
    wiki_en: str = "",
    wiki_ru: str = "",
) -> bool:
    db = get_db()
    existing = get_book(book_id)
    if existing is None:
        return False
    cover = (cover_url or "").strip() or existing["cover_url"] or DEFAULT_COVER
    body = (content or "").strip() or existing["content"] or ""
    cur = db.execute(
        """
        UPDATE books SET
            title = ?, title_en = ?, title_ru = ?,
            author = ?, year = ?,
            genre = ?, genre_en = ?, genre_ru = ?,
            cover_url = ?,
            content = ?, content_en = ?, content_ru = ?,
            wiki_kk = ?, wiki_en = ?, wiki_ru = ?
        WHERE id = ?
        """,
        (
            title,
            (title_en or "").strip(),
            (title_ru or "").strip(),
            author,
            year,
            genre,
            (genre_en or "").strip(),
            (genre_ru or "").strip(),
            cover,
            body,
            (content_en or "").strip(),
            (content_ru or "").strip(),
            (wiki_kk or "").strip(),
            (wiki_en or "").strip(),
            (wiki_ru or "").strip(),
            book_id,
        ),
    )
    db.commit()
    return cur.rowcount > 0


def delete_book(book_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    return cur.rowcount > 0


def resolve_wiki_title(book, lang: str) -> str:
    """Тілге сай Wikipedia мақала атауы."""
    lang = (lang or "kk").lower()
    col = f"wiki_{lang}"
    if col in book.keys() and (book[col] or "").strip():
        return book[col].strip()
    # fallback: localized book title
    if lang == "en" and (book["title_en"] or "").strip():
        return book["title_en"].strip()
    if lang == "ru" and (book["title_ru"] or "").strip():
        return book["title_ru"].strip()
    return (book["title"] or "").strip()
