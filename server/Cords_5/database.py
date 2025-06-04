import sqlite3

DB_NAME = "notes.db"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE
        )
    """)

    # Таблица записок
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

    # Таблица сохранённых записок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_notes (
            user_id INTEGER,
            note_id INTEGER,
            PRIMARY KEY (user_id, note_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (note_id) REFERENCES notes (id)
        )
    """)

    conn.commit()
    conn.close()


def clear_database():
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

    # Приведение данных к формату для таблицы
    formatted_notes = [
        (
            note[0],  # username
            note[1],  # text
            note[2],  # latitude
            note[3],  # longitude
            note[4] if len(note) > 4 else "Unknown address",  # address
            note[5] if len(note) > 5 else "Unknown metro",  # nearest_metro
            note[6] if len(note) > 6 else None,  # metro_distance
            note[7] if len(note) > 7 else None,  # series_id
            note[8] if len(note) > 8 else None,  # series_order
        )
        for note in notes
    ]

    cursor.executemany("""
        INSERT INTO notes (
            username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, formatted_notes)
    conn.commit()
    conn.close()



def login_user(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id


def save_found_note_to_user(user_id, note_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO user_notes (user_id, note_id)
        VALUES (?, ?)
    """, (user_id, note_id))
    conn.commit()
    conn.close()


def get_user_notes(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT notes.*
        FROM notes
        INNER JOIN user_notes ON notes.id = user_notes.note_id
        WHERE user_notes.user_id = ?
    """, (user_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes


def insert_series(series):
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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    conn.close()
    return notes


def get_series_notes(series_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE series_id = ? ORDER BY series_order", (series_id,))
    series_notes = cursor.fetchall()
    conn.close()
    return series_notes


def update_note_address_and_metro(note_id, address, metro, metro_distance):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notes
        SET address = ?, nearest_metro = ?, metro_distance = ?
        WHERE id = ?
    """, (address, metro, metro_distance, note_id))
    conn.commit()
    conn.close()
