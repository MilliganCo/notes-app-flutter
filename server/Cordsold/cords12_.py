import sqlite3
import random
import requests
import json
from geopy.distance import geodesic

# API ключ Яндекс
YANDEX_API_KEY = "fc164944-953f-414a-8f60-1b7207f2273f"

# Координаты Москвы
MOSCOW_LAT_MIN = 55.55
MOSCOW_LAT_MAX = 55.95
MOSCOW_LON_MIN = 37.35
MOSCOW_LON_MAX = 37.85

# Список реальных имен и текстов
USERNAMES = ["Анна", "Иван", "Мария", "Петр", "Сергей", "Екатерина", "Алексей", "Ольга", "Дмитрий", "Юлия"]
TEXTS = [
    "Увидимся завтра на встрече.",
    "Забыл ключи дома, подскажите адрес.",
    "Пожалуйста, принесите кофе.",
    "Нужен совет по поводу задачи.",
    "Отправил документы по почте.",
    "Скоро буду, ожидайте.",
    "Забыл важный файл дома.",
    "Встретимся через 15 минут.",
    "Сегодня отличная погода!",
    "Нужна помощь с проектом."
]

# Функция для генерации случайных координат
def generate_random_coordinates():
    lat = random.uniform(MOSCOW_LAT_MIN, MOSCOW_LAT_MAX)
    lon = random.uniform(MOSCOW_LON_MIN, MOSCOW_LON_MAX)
    return lat, lon

# Функция для обращения к Яндекс API
def get_nearest_address_and_metro(lat, lon):
    address_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": f"{lon},{lat}",
        "format": "json"
    }
    response = requests.get(address_url, params=params)
    response.raise_for_status()
    data = response.json()

    # Парсим ближайший адрес
    address = "Unknown address"
    if "GeoObjectCollection" in data["response"] and "featureMember" in data["response"]["GeoObjectCollection"]:
        feature_member = data["response"]["GeoObjectCollection"]["featureMember"]
        if feature_member:
            address = feature_member[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]

    # TODO: Добавить логику поиска метро, если потребуется (аналогичная работа с API Яндекс)

    return address, "Unknown metro"  # Пока метро не ищем

# Подключение к SQLite базе
conn = sqlite3.connect("../notes.db")
cursor = conn.cursor()

# Создание таблицы
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    latitude REAL,
    longitude REAL,
    content TEXT,
    nearest_address TEXT,
    nearest_metro TEXT
)
""")

# Генерация записок и сохранение
def generate_notes(num_notes=50):
    for _ in range(num_notes):
        lat, lon = generate_random_coordinates()
        username = random.choice(USERNAMES)
        content = random.choice(TEXTS)

        # Обращение к Яндекс API
        nearest_address, nearest_metro = get_nearest_address_and_metro(lat, lon)

        # Запись в базу данных
        cursor.execute("""
        INSERT INTO notes (username, latitude, longitude, content, nearest_address, nearest_metro)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (username, lat, lon, content, nearest_address, nearest_metro))
    conn.commit()

generate_notes()
print("Сгенерированные записки сохранены в базу данных.")

def find_notes_near_user(lat, lon, radius=200):
    """
    Найти записки в радиусе от пользователя.
    """
    cursor.execute("SELECT * FROM notes")
    all_notes = cursor.fetchall()

    nearby_notes = []
    for note in all_notes:
        note_coords = (note[2], note[3])  # latitude, longitude
        distance = geodesic((lat, lon), note_coords).meters
        if distance <= radius:
            nearby_notes.append({
                "id": note[0],
                "username": note[1],
                "latitude": note[2],
                "longitude": note[3],
                "content": note[4],
                "nearest_address": note[5],
                "nearest_metro": note[6],
                "distance": f"{distance:.2f} m"
            })
    return nearby_notes

from tkinter import Tk, Label, Entry, Button, Text, END

def search_notes():
    try:
        user_lat = float(entry_lat.get())
        user_lon = float(entry_lon.get())
        notes = find_notes_near_user(user_lat, user_lon, radius=200)

        result_box.delete("1.0", END)
        if notes:
            for note in notes:
                result_box.insert(END, f"ID: {note['id']}, User: {note['username']}\n")
                result_box.insert(END, f"Text: {note['content']}\n")
                result_box.insert(END, f"Address: {note['nearest_address']}\n")
                result_box.insert(END, f"Metro: {note['nearest_metro']}\n")
                result_box.insert(END, f"Distance: {note['distance']}\n")
                result_box.insert(END, "------\n")
        else:
            result_box.insert(END, "Нет записок поблизости.")
    except Exception as e:
        result_box.insert(END, f"Ошибка: {e}\n")

# Интерфейс
root = Tk()
root.title("Поиск записок")

Label(root, text="Широта:").pack()
entry_lat = Entry(root)
entry_lat.pack()

Label(root, text="Долгота:").pack()
entry_lon = Entry(root)
entry_lon.pack()

Button(root, text="Искать записки", command=search_notes).pack()

result_box = Text(root, height=20, width=50)
result_box.pack()

root.mainloop()
