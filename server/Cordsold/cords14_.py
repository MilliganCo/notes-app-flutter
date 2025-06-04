import json
import random
import requests
import sqlite3
from tkinter import Tk, messagebox
from geopy.distance import geodesic

# Яндекс API ключ
YANDEX_API_KEY = "fc164944-953f-414a-8f60-1b7207f2273f"

# Имя базы данных
DB_NAME = "notes.db"

# Генерация записок
def generate_random_notes(count=50):
    names = ["Алексей", "Ольга", "Мария", "Иван", "Дмитрий", "Елена", "Владимир", "Татьяна", "Николай", "Анна"]
    texts = [
        "Это пример записки.",
        "Очень важное сообщение.",
        "Заметка для всех.",
        "Погода отличная сегодня.",
        "Записка с важной информацией.",
        "Здесь было лучшее кафе!",
        "Не забудьте посмотреть на закат.",
        "Я нашел что-то интересное.",
        "Удивительное место.",
        "Здесь классно отдыхать."
    ]
    notes = []
    for _ in range(count):
        username = random.choice(names)
        text = random.choice(texts)
        lat = random.uniform(55.55, 55.95)  # Координаты Москвы
        lon = random.uniform(37.35, 37.85)
        notes.append((username, text, lat, lon))
    return notes

# Функция поиска адреса через Яндекс
def find_nearest_address(coords):
    try:
        lat, lon = coords
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "results": 1,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "response" in data and "GeoObjectCollection" in data["response"]["GeoObjectCollection"]:
            geo_objects = data["response"]["GeoObjectCollection"]["featureMember"]
            if geo_objects:
                address = geo_objects[0]["GeoObject"]["name"]
                return address
        return "Unknown address"
    except Exception as e:
        return f"Error: {e}"

# Функция поиска метро через Яндекс
def find_nearest_metro(coords):
    try:
        lat, lon = coords
        url = "https://search-maps.yandex.ru/v1/"
        params = {
            "apikey": YANDEX_API_KEY,
            "text": "станция метро",
            "ll": f"{lon},{lat}",
            "type": "biz",
            "results": 1,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "features" in data and data["features"]:
            feature = data["features"][0]
            metro_name = feature["properties"]["name"]
            metro_coords = feature["geometry"]["coordinates"]
            distance = geodesic(coords, (metro_coords[1], metro_coords[0])).meters
            return metro_name, distance
        return "Unknown metro", None
    except Exception as e:
        return f"Error: {e}", None

# Работа с базой данных
def initialize_database():
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
            metro_distance REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_notes_into_db(notes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for username, text, lat, lon in notes:
        address = find_nearest_address((lat, lon))
        nearest_metro, metro_distance = find_nearest_metro((lat, lon))
        cursor.execute("""
            INSERT INTO notes (username, text, latitude, longitude, address, nearest_metro, metro_distance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, text, lat, lon, address, nearest_metro, metro_distance))
    conn.commit()
    conn.close()

def clear_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes")
    conn.commit()
    conn.close()

def fetch_all_notes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    conn.close()
    return notes

# GUI для выбора действия
def handle_user_choice():
    root = Tk()
    root.withdraw()  # Скрываем главное окно
    choice = messagebox.askquestion(
        "Действие",
        "Выберите действие:\n1. Сгенерировать дополнительные 50 записок\n2. Стереть все предыдущие и сгенерировать 50 записок\n3. Продолжить с нынешней базой данных"
    )
    if choice == "yes":
        action = messagebox.askquestion(
            "Выбор",
            "Стереть всё или добавить новые?\n1. Стереть всё\n2. Добавить новые"
        )
        if action == "yes":
            clear_database()
            notes = generate_random_notes()
            insert_notes_into_db(notes)
            messagebox.showinfo("Успех", "База данных очищена и записки добавлены.")
        else:
            notes = generate_random_notes()
            insert_notes_into_db(notes)
            messagebox.showinfo("Успех", "Новые записки добавлены.")
    else:
        messagebox.showinfo("Продолжение", "Запускаем скрипт с существующими данными.")

# Логика поиска записок
def search_notes_near_user(lat, lon, radius=200):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, text, latitude, longitude, address, nearest_metro, metro_distance FROM notes")
    notes = cursor.fetchall()
    conn.close()

    nearby_notes = []
    for note in notes:
        note_coords = (note[2], note[3])
        distance = geodesic((lat, lon), note_coords).meters
        if distance <= radius:
            nearby_notes.append({
                "username": note[0],
                "text": note[1],
                "coordinates": {"latitude": note[2], "longitude": note[3]},
                "address": note[4],
                "nearest_metro": note[5],
                "metro_distance_m": f"{note[6]:.2f} m" if note[6] else "Unknown distance",
                "distance_from_user_m": f"{distance:.2f} m"
            })
    return nearby_notes

# Основная логика
def main():
    initialize_database()
    handle_user_choice()

    # Пример поиска записок
    user_lat = 55.7558  # Пример: Москва, Красная площадь
    user_lon = 37.6173
    radius = 500

    notes_nearby = search_notes_near_user(user_lat, user_lon, radius)
    for note in notes_nearby:
        print(json.dumps(note, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
