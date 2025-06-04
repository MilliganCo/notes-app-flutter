import json
import random
import requests
import sqlite3
from tkinter import Tk, Button, Label, simpledialog, messagebox, Entry
from geopy.distance import geodesic

# Яндекс API ключ
YANDEX_API_KEY = "fc164944-953f-414a-8f60-1b7207f2273f"

# Имя базы данных
DB_NAME = "notes.db"

# Генерация случайных записок
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

def clear_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes")
    conn.commit()
    conn.close()

def insert_notes_into_db(notes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for username, text, lat, lon in notes:
        address, _ = find_nearest_address((lat, lon))
        metro_name, metro_distance = find_nearest_metro((lat, lon))
        cursor.execute("""
            INSERT INTO notes (username, text, latitude, longitude, address, nearest_metro, metro_distance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, text, lat, lon, address, metro_name, metro_distance))
    conn.commit()
    conn.close()

# Функция для поиска адреса
def find_nearest_address(coords):
    try:
        lat, lon = coords
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "kind": "house",
            "results": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        geo_objects = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
        if geo_objects:
            geo_object = geo_objects[0]["GeoObject"]
            address = geo_object["metaDataProperty"]["GeocoderMetaData"]["text"]
            return address, None
        return "Unknown address", None
    except Exception as e:
        return f"Error: {e}", None

# Функция для поиска ближайшего метро
def find_nearest_metro(coords):
    try:
        lat, lon = coords
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "kind": "metro",
            "results": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        geo_objects = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
        if geo_objects:
            geo_object = geo_objects[0]["GeoObject"]
            metro_name = geo_object["metaDataProperty"]["GeocoderMetaData"]["text"]
            return metro_name, None
        return "Unknown metro", None
    except Exception as e:
        return f"Error: {e}", None

# Логика выбора действия
def handle_user_choice(action):
    if action == "add":
        notes = generate_random_notes()
        insert_notes_into_db(notes)
        messagebox.showinfo("Успех", "Новые записки добавлены.")
    elif action == "overwrite":
        clear_database()
        notes = generate_random_notes()
        insert_notes_into_db(notes)
        messagebox.showinfo("Успех", "База данных очищена и записки добавлены.")
    elif action == "continue":
        messagebox.showinfo("Продолжение", "Запускаем скрипт с существующими данными.")
    search_window()

# Создание интерфейса для выбора действия
def user_choice_window():
    root = Tk()
    root.title("Выбор действия")

    Label(root, text="Выберите действие:").pack(pady=10)

    Button(root, text="Добавить записки", command=lambda: [handle_user_choice("add"), root.destroy()]).pack(pady=5)
    Button(root, text="Стереть и добавить", command=lambda: [handle_user_choice("overwrite"), root.destroy()]).pack(pady=5)
    Button(root, text="Продолжить", command=lambda: [handle_user_choice("continue"), root.destroy()]).pack(pady=5)

    root.mainloop()

# Окно поиска записок
def search_window():
    def search_notes():
        try:
            lat = float(latitude_entry.get())
            lon = float(longitude_entry.get())
            radius = 200
            coords = (lat, lon)

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes")
            notes = cursor.fetchall()
            conn.close()

            results = []
            for note in notes:
                note_coords = (note[3], note[4])
                distance = calculate_distance(coords, note_coords)
                if distance <= radius:
                    results.append({
                        "id": note[0],
                        "username": note[1],
                        "text": note[2],
                        "coordinates": {"latitude": note[3], "longitude": note[4]},
                        "address": note[5],
                        "nearest_metro": note[6],
                        "distance_from_user": f"{distance:.2f} m"
                    })

            if results:
                result_text = json.dumps(results, indent=4, ensure_ascii=False)
            else:
                result_text = "Нет записок в радиусе 200 метров."
            messagebox.showinfo("Результаты поиска", result_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {e}")

    search_root = Tk()
    search_root.title("Поиск записок")

    Label(search_root, text="Введите широту:").pack(pady=5)
    latitude_entry = Entry(search_root)
    latitude_entry.pack(pady=5)

    Label(search_root, text="Введите долготу:").pack(pady=5)
    longitude_entry = Entry(search_root)
    longitude_entry.pack(pady=5)

    Button(search_root, text="Найти записки", command=search_notes).pack(pady=10)

    search_root.mainloop()

# Основная логика
def main():
    initialize_database()
    user_choice_window()

if __name__ == "__main__":
    main()
