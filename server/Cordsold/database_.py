import sqlite3

DB_NAME = "notes.db"


def initialize_database():
    """
    Инициализация базы данных SQLite. Создание таблицы, если она не существует.
    Если таблица уже существует, проверяем наличие столбцов series_id и series_order.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создание таблицы, если она отсутствует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            text TEXT,
            latitude REAL,
            longitude REAL,
            address TEXT,
            nearest_metro TEXT,
            metro_distance REAL
        )
    """)

    # Проверка и добавление недостающих столбцов
    cursor.execute("PRAGMA table_info(notes)")
    columns = [col[1] for col in cursor.fetchall()]

    if "series_id" not in columns:
        cursor.execute("ALTER TABLE notes ADD COLUMN series_id INTEGER")
    if "series_order" not in columns:
        cursor.execute("ALTER TABLE notes ADD COLUMN series_order INTEGER")

    conn.commit()
    conn.close()

    def insert_notes(notes):
        """
        Добавить список записок в базу данных.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Форматируем данные для таблицы (9 полей)
        formatted_notes = [
            (
                note[0],  # username
                note[1],  # text
                note[2],  # latitude
                note[3],  # longitude
                "Unknown address",  # address (по умолчанию)
                "Unknown metro",  # nearest_metro (по умолчанию)
                None,  # metro_distance (по умолчанию)
                None,  # series_id (нет серии)
                None,  # series_order (нет порядка)
            )
            for note in notes
        ]

        # Вставляем данные
        cursor.executemany("""
            INSERT INTO notes (
                username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, formatted_notes)

        conn.commit()
        conn.close()


def insert_series(series):
    """
    Добавить серию записок в базу данных.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Приведение данных к полному формату (9 полей для каждой записки)
    formatted_series = [
        (
            note[0],  # username
            note[1],  # text
            note[2],  # latitude
            note[3],  # longitude
            "Unknown address",  # address (по умолчанию)
            "Unknown metro",  # nearest_metro (по умолчанию)
            None,  # metro_distance (по умолчанию)
            note[4],  # series_id
            note[5],  # series_order
        )
        for note in series
    ]

    # Вставка данных в таблицу
    cursor.executemany("""
        INSERT INTO notes (
            username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, formatted_series)

    conn.commit()
    conn.close()


def get_all_notes():
    """
    Получить все записи из таблицы.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    conn.close()
    return notes


def get_notes_in_radius(lat, lon, radius):
    """
    Получить записки в радиусе от заданной точки.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order
        FROM notes
        WHERE ((latitude - ?) * (latitude - ?) + (longitude - ?) * (longitude - ?)) <= (? * ?)
    """, (lat, lat, lon, lon, radius / 111.12, radius / 111.12))  # Пример расчета квадратного радиуса в градусах
    notes = cursor.fetchall()
    conn.close()
    return notes


def get_notes_by_series(series_id):
    """
    Получить записки из указанной серии.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order
        FROM notes
        WHERE series_id = ?
        ORDER BY series_order
    """, (series_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes
