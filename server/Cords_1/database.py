import sqlite3

DB_NAME = "notes.db"

def initialize_database():
    """
    Инициализация базы данных SQLite. Создание таблицы, если она не существует.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            text TEXT,
            latitude REAL,
            longitude REAL,
            address TEXT,
            nearest_metro TEXT,
            metro_distance REAL,
            series_id INTEGER,
            series_order INTEGER
        )
    """)
    conn.commit()
    conn.close()

def clear_database():
    """
    Очистить таблицу записок.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes")
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
    cursor.executemany("""
        INSERT INTO notes (
            username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, series)
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
