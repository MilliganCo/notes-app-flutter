from dotenv import load_dotenv
load_dotenv()

import json
import math
import re
import sys
import uuid
from math import radians, sin, cos, sqrt, atan2

import mysql.connector
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
import firebase_admin
from firebase_admin import credentials, messaging
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from functools import wraps
from datetime import datetime, timedelta


def generate_unique_id():
    return str(uuid.uuid4())


app = Flask(__name__)
CORS(app)

# Инициализация ограничителя скорости
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100/minute"]
)

cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
firebase_admin.initialize_app(cred, {
    "projectId": os.environ["FCM_PROJECT_ID"],
})

# Для запуска генерации записок через сервер:
# 1. Откройте новый терминал, когда сервер уже работает.
# 2. Введите команду: python3 GPGtest.py generateradius - для генерации в конкретном месте, python3 GPGtest.py generaterandom - для генерации в случайных местах Москвы.
# Эти команды запустят генерацию записок в фоновом режиме.


# Границы России
MIN_LAT, MAX_LAT = 41.1851, 81.8587
MIN_LON, MAX_LON = 19.6389, 169.05

# Списки случайных текстов, пользователей и заголовков
random_texts = [
    "Советуем посетить", "Не забудь об этом месте", "Записка для всех", "Просто запись", "Я был здесь"
]
random_usernames = [
    "Андрей", "Елена", "Дмитрий", "Ольга", "Сергей"
]
random_titles = [
    "Первый визит", "Заметка путешественника", "Незабываемый момент", "Уникальная находка"
]

USER_AGENT = "AudioLED XXL NotesApp/1.0 (support@audioledyxxl.ru)"


def generate_notes_in_background(mode):
    thread = threading.Thread(target=generate_notes, args=(mode,))
    thread.start()
    print(f"Запуск генерации записок в режиме: {mode}")


def calculate_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    R = 6371  # Радиус Земли в километрах
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c * 1000  # Возвращаем расстояние в метрах


import random
import hashlib


def generate_users(num_users=1000):
    mydb = mysql.connector.connect(
        host="localhost",
        user="db_admin",
        password="admin456123",
        database="notes"
    )
    mycursor = mydb.cursor()

    usernames = set()
    while len(usernames) < num_users:
        username = f"user{random.randint(10000, 99999)}"
        usernames.add(username)

    for username in usernames:
        password = f"pass{random.randint(10000, 99999)}"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        email = f"{username}@example.com"
        phone_number = random.randint(7000000000, 7999999999)

        sql = """
            INSERT INTO user_auth (username, password_hash, phone_number, email, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (username, password_hash, phone_number, email, 'user', 1)
        mycursor.execute(sql, values)

    mydb.commit()
    mycursor.close()
    mydb.close()


import threading


def simulate_user(user_id):
    """
    Симулирует действия одного пользователя с индивидуальными интервалами.
    """
    while True:
        # Поиск записок
        search_interval = random.randint(30, 60)
        try:
            search_and_save_notes(user_id)
        except Exception as e:
            print(f"Ошибка при поиске записок для пользователя {user_id}: {e}")
        time.sleep(search_interval)

        # Создание записок
        create_note_interval = random.randint(300, 1800)  # 5-30 минут
        if random.random() < 0.5:  # 50% вероятность создания
            try:
                create_note_for_user(user_id)
            except Exception as e:
                print(f"Ошибка при создании записки для пользователя {user_id}: {e}")
        time.sleep(create_note_interval)


from concurrent.futures import ThreadPoolExecutor
import time


def simulate_user_activity_optimized():
    """
    Оптимизированная симуляция с ограничением на количество потоков.
    """
    # Количество одновременных потоков
    max_threads = 50  # Настройте в зависимости от возможностей вашей системы

    mydb = mysql.connector.connect(
        host="localhost",
        user="db_admin",
        password="admin456123",
        database="notes"
    )
    mycursor = mydb.cursor()

    # Получаем всех пользователей
    mycursor.execute("SELECT id FROM user_auth WHERE is_active = 1")
    users = [user[0] for user in mycursor.fetchall()]
    mycursor.close()
    mydb.close()

    with ThreadPoolExecutor(max_threads) as executor:
        for user_id in users:
            executor.submit(simulate_user, user_id)


def create_note_for_user(user_id):
    lat, lon = generate_random_coords_russia()
    text = random.choice(random_texts)
    title = random.choice(random_titles)

    mydb = mysql.connector.connect(
        host="localhost",
        user="db_admin",
        password="admin456123",
        database="notes"
    )
    mycursor = mydb.cursor()

    sql = """
        INSERT INTO notes (username, title, text, latitude, longitude, address, nearest_metro)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (f"user{user_id}", title, text, lat, lon, get_address_from_coords(lat, lon), get_nearest_metro(lat, lon))
    mycursor.execute(sql, values)
    mydb.commit()
    mycursor.close()
    mydb.close()


def search_and_save_notes(user_id):
    lat, lon = generate_random_coords_russia()

    # Отправляем GET-запрос на поиск записок
    response = requests.get(f"http://localhost:5000/?user=user{user_id}&lat={lat}&lon={lon}")
    data = response.json()

    if data.get("c2array"):
        notes = data["data"]
        for note in notes:
            if random.random() < 0.7:  # 70% вероятность сохранить
                save_note_for_user(user_id, note[0][0])


def save_note_for_user(user_id, note_id):
    payload = {"username": f"user{user_id}", "note_id": note_id}
    requests.post("http://localhost:5000/save", json=payload)


# Функция очистки JSON
def clean_json(raw_data):
    start = raw_data.find("{")
    end = raw_data.rfind("}") + 1
    json_data = raw_data[start:end]
    cleaned_data = re.sub(r"[\n\r\t]", "", json_data)
    cleaned_data = re.sub(r"\s+", " ", cleaned_data)
    return cleaned_data.strip()


# Проверка диапазонов координат
def validate_coordinates(lat, lon, use_clusters=False):
    if not use_clusters:
        # Проверка фиксированных границ (быстрый метод)
        return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON
    else:
        # Проверка координат в базе данных (кластерный метод)
        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        sql = """
        SELECT cluster_id FROM clusters
        WHERE min_lat <= %s AND max_lat >= %s AND min_lon <= %s AND max_lon >= %s
        """
        mycursor.execute(sql, (lat, lat, lon, lon))
        cluster = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        return cluster is not None


# Защита от SQL-инъекций
def is_sqli_attempt(data):
    sqli_patterns = [
        r"(?:--|;|/\*|\*/|'|\"|=|#)",
        r"(?:\b(OR|AND|UNION|SELECT|INSERT|DELETE|DROP|UPDATE)\b)",
    ]
    for pattern in sqli_patterns:
        if re.search(pattern, data, re.IGNORECASE):
            return True
    return False


# Сохранение записки с поддержкой текстового запроса
@app.route("/save", methods=['POST'])
@cross_origin()
@token_required
def save_note():
    global mycursor
    try:
        # Извлекаем данные из запроса
        raw_data = request.data.decode('utf-8')
        print(f"Request Data: {raw_data}")
        data = json.loads(raw_data)

        username = data.get('username')
        note_id = data.get('note_id')

        if not username or not note_id:
            return jsonify({"error": "username and note_id are required"}), 400

        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        # Проверка существования записки
        mycursor.execute("SELECT username FROM notes WHERE id = %s", (note_id,))
        result = mycursor.fetchone()

        if not result:
            return jsonify({"error": "Note not found"}), 404

        note_creator = result[0]
        if note_creator == username:
            return jsonify({"error": "You cannot save your own note"}), 400

        # Добавление сохраненной записки
        sql = """
            INSERT INTO saved_notes (username, note_id)
            VALUES (%s, %s)
        """
        try:
            mycursor.execute(sql, (username, note_id))
            mydb.commit()
            return jsonify({"message": "Note saved successfully"}), 200
        except mysql.connector.errors.IntegrityError as e:
            # Обработка ошибки при повторяющейся записи
            if "Duplicate entry" in str(e):
                return jsonify({"error": "Note already saved"}), 400
            raise

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals():
            mydb.close()


# Отправка сообщений к записке
@app.route("/message", methods=['POST'])
@cross_origin()
@token_required
def send_message():
    try:
        data = request.json
        note_id = data.get('note_id')
        sender = data.get('sender')
        receiver = data.get('receiver')
        content = data.get('content')

        if not note_id or not sender or not receiver or not content:
            return jsonify({"error": "note_id, sender, receiver, and content are required"}), 400

        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        # Проверка существования записки
        mycursor.execute("SELECT id FROM notes WHERE id = %s", (note_id,))
        if not mycursor.fetchone():
            return jsonify({"error": "Note not found"}), 404

        # Проверка пользователей
        mycursor.execute("SELECT username FROM user_auth WHERE username = %s", (sender,))
        if not mycursor.fetchone():
            return jsonify({"error": "Sender not found"}), 404

        mycursor.execute("SELECT username FROM user_auth WHERE username = %s", (receiver,))
        if not mycursor.fetchone():
            return jsonify({"error": "Receiver not found"}), 404

        # Добавление сообщения в таблицу
        sql = """
            INSERT INTO messages (note_id, sender, receiver, content)
            VALUES (%s, %s, %s, %s)
        """
        mycursor.execute(sql, (note_id, sender, receiver, content))
        mydb.commit()

        # Отправка уведомления получателю
        # Проверяем, что отправитель и получатель разные перед отправкой уведомления
        if sender != receiver:
            # TODO: Get receiver user_id from username
            # Placeholder: Assuming receiver is user_id for now based on playbook structure
            receiver_user_id = receiver # Replace with actual user_id retrieval
            send_notification(receiver_user_id, "Новое сообщение", f"У вас новое сообщение по записке {note_id}", data={"note_id": note_id})

        return jsonify({"message": "Message sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals():
            mydb.close()


def send_notification(user_id: int, title: str, body: str, data: dict | None = None):
    try:
        mydb = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME')
        )
        mycursor = mydb.cursor(dictionary=True)

        mycursor.execute("SELECT device_token FROM user_devices WHERE user_id=%s", (user_id,))
        rows = mycursor.fetchall()
        tokens = [r["device_token"] for r in rows]

        if not tokens:
            print(f"No device tokens found for user {user_id}. Skipping notification.")
            return False  # silently skip

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            tokens=tokens,
        )
        response = messaging.send_multicast(message)
        print(f"FCM sent to {user_id} ➜ success={response.success_count} failure={response.failure_count}")
        return response.success_count > 0

    except Exception as e:
        print(f"Error sending notification to user {user_id}: {e}")
        return False
    finally:
        if 'mycursor' in locals() and mycursor:
            mycursor.close()
        if 'mydb' in locals() and mydb:
            mydb.close()


# Получение сообщений к записке
@app.route("/messages", methods=['GET'])
@cross_origin()
def get_messages():
    try:
        note_id = request.args.get('note_id')
        username = request.args.get('username')

        if not note_id or not username:
            return jsonify({"error": "note_id and username are required"}), 400

        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        # Проверка существования записки
        mycursor.execute("SELECT id FROM notes WHERE id = %s", (note_id,))
        if not mycursor.fetchone():
            return jsonify({"error": "Note not found"}), 404

        # Пометка сообщений как прочитанных
        sql_update_read = """
            UPDATE messages
            SET is_read = 1
            WHERE note_id = %s AND receiver = %s AND is_read = 0
        """
        mycursor.execute(sql_update_read, (note_id, username))
        mydb.commit()

        # Получение всех сообщений
        sql_get_messages = """
            SELECT id, sender, receiver, content, sent_at, is_read
            FROM messages
            WHERE note_id = %s AND (sender = %s OR receiver = %s)
            ORDER BY sent_at ASC
        """
        mycursor.execute(sql_get_messages, (note_id, username, username))
        result = mycursor.fetchall()

        messages = [
            {
                "id": row[0],
                "sender": row[1],
                "receiver": row[2],
                "content": row[3],
                "sent_at": row[4],
                "is_read": bool(row[5])
            }
            for row in result
        ]

        return jsonify({"messages": messages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals():
            mydb.close()


# Маршрут для обновления флага прочтения сообщений
# Появится сценарии, где обновление флага "прочитано" потребуется без запроса всех сообщений (например, через push-уведомления или другую систему).
# Мы захотим изолировать логику пометки сообщений как прочитанных в отдельной функции для повторного использования (в других маршрутах или фоновых задачах))

@app.route("/message/read", methods=['POST'])
@cross_origin()
@token_required
def mark_message_as_read():
    try:
        data = request.json
        message_id = data.get('message_id')
        # TODO: Validate ownership of the message before marking as read

        if not message_id:
            return jsonify({"error": "message_id is required"}), 400

        mydb = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME')
        )
        mycursor = mydb.cursor()

        # Обновление статуса сообщения и добавление read_at
        sql = "UPDATE messages SET is_read = 1, read_at = NOW() WHERE id = %s"
        mycursor.execute(sql, (message_id,))
        updated_count = mycursor.rowcount
        mydb.commit()

        # TODO: Consider adding logic to send a read receipt notification back to the sender

        return jsonify({"updated": updated_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'mycursor' in locals() and mycursor:
            mycursor.close()
        if 'mydb' in locals() and mydb:
            mydb.close()


@app.route("/active_saved_notes", methods=['GET'])
@cross_origin()
def get_active_saved_notes():
    username = request.args.get('username')

    if not username:
        return jsonify({"error": "username is required"}), 400

    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        # Получаем только активные сохраненные записки
        sql = """
            SELECT notes.id, notes.username, notes.title, notes.text, notes.latitude, 
                   notes.longitude, notes.address, notes.nearest_metro, saved_notes.saved_at
            FROM saved_notes
            JOIN notes ON saved_notes.note_id = notes.id
            WHERE saved_notes.username = %s AND saved_notes.is_deleted = 0
        """
        mycursor.execute(sql, (username,))
        result = mycursor.fetchall()

        # Формируем ответ
        data = {
            "c2array": True,
            "size": [len(result), 9, 1],
            "data": [
                [[record[0]], [record[1]], [record[2]], [record[3]], [record[4]],
                 [record[5]], [record[6]], [record[7]], [record[8]]]
                for record in result
            ]
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        mycursor.close()
        mydb.close()


@app.route("/active_notes", methods=['GET'])
@cross_origin()
def get_active_notes():
    global mydb
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        # Получаем только активные записки
        sql = "SELECT * FROM notes WHERE is_deleted = 0"
        mycursor.execute(sql)
        result = mycursor.fetchall()

        # Формируем ответ
        data = {
            "c2array": True,
            "size": [len(result), 8, 1],
            "data": [
                [[record[0]], [record[1]], [record[2]], [record[3]], [record[4]],
                 [record[5]], [record[6]], [record[7]]]
                for record in result
            ]
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        mycursor.close()
        mydb.close()


@app.route("/delete_note", methods=['POST'])
@cross_origin()
@token_required
def delete_note():
    try:
        # Получаем данные из запроса
        data = json.loads(request.data.decode('utf-8'))
        note_id = data.get('note_id')

        if not note_id:
            return jsonify({"error": "note_id is required"}), 400

        # Подключение к базе данных
        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        # Обновляем флаг is_deleted для указанной записки
        sql = "UPDATE notes SET is_deleted = 1 WHERE id = %s AND is_deleted = 0"
        mycursor.execute(sql, (note_id,))
        if mycursor.rowcount == 0:
            return jsonify({"error": "Note not found or already deleted"}), 404

        mydb.commit()
        return jsonify({"message": "Note marked as deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        mycursor.close()
        mydb.close()


# Удаление сохраненной записки
@app.route("/delete_saved_note", methods=['POST'])
@cross_origin()
@token_required
def delete_saved_note():
    try:
        # Получаем данные из запроса
        data = json.loads(request.data.decode('utf-8'))
        username = data.get('username')
        note_id = data.get('note_id')

        if not username or not note_id:
            return jsonify({"error": "username and note_id are required"}), 400

        # Подключение к базе данных
        mydb = mysql.connector.connect(
            host="localhost",
            user="db_admin",
            password="admin456123",
            database="notes"
        )
        mycursor = mydb.cursor()

        # Удаляем запись, обновляя is_deleted
        sql = """
            UPDATE saved_notes
            SET is_deleted = 1
            WHERE username = %s AND note_id = %s AND is_deleted = 0
        """
        mycursor.execute(sql, (username, note_id))
        if mycursor.rowcount == 0:
            return jsonify({"error": "Saved note not found or already deleted"}), 404

        mydb.commit()
        return jsonify({"message": "Saved note marked as deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        mycursor.close()
        mydb.close()


# Вставка данных в таблицу notes
def insert_into_db(data):
    mydb = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
    )
    mycursor = mydb.cursor()

    try:
        # Начинаем транзакцию
        mydb.start_transaction()
        
        sql = """
            INSERT INTO notes (id, username, title, text, latitude, longitude, address, nearest_metro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Подготавливаем все значения для вставки
        values = []
        for record in data:
            note_id, username, title, text, lat, lon, address, metro = record
            if is_sqli_attempt(username) or is_sqli_attempt(title) or is_sqli_attempt(text):
                raise ValueError(f"SQL injection attempt detected in record: {record}")
            if not validate_coordinates(lat, lon):
                raise ValueError(f"Invalid coordinates: lat={lat}, lon={lon}")
            values.append((note_id, username, title, text, lat, lon, address, metro))
        
        # Выполняем массовую вставку
        mycursor.executemany(sql, values)
        
        # Фиксируем транзакцию
        mydb.commit()
        return {"message": f"Successfully inserted {len(values)} records"}
        
    except Exception as e:
        # В случае ошибки откатываем транзакцию
        mydb.rollback()
        return {"error": str(e)}
    finally:
        mycursor.close()
        mydb.close()


# Функция для получения адреса
def get_address_from_coords(lat, lon):
    # Сначала пытаемся получить адрес через Overpass API
    time.sleep(random.uniform(1.1, 2))  # Задержка от 1.1 до 2 секунд
    OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
        node(around:100, {lat}, {lon});
        way(around:100, {lat}, {lon});
        relation(around:100, {lat}, {lon});
    );
    out body;
    """
    try:
        response = requests.get(OVERPASS_API_URL, params={'data': overpass_query})
        response.raise_for_status()
        data = response.json()
        for element in data.get('elements', []):
            if 'tags' in element and 'addr:full' in element['tags']:
                return element['tags']['addr:full']
            elif 'tags' in element and 'addr:street' in element['tags']:
                street = element['tags'].get('addr:street', 'Unknown street')
                house_number = element['tags'].get('addr:housenumber', 'Unknown number')
                return f"{street}, {house_number}"
    except Exception as e:
        print(f"Overpass API failed: {e}")

    # Если Overpass не возвращает результат, используем Nominatim
    NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/reverse"
    params = {'lat': lat, 'lon': lon, 'format': 'json', 'addressdetails': 1}
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(NOMINATIM_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'address' in data:
            address = data['address']
            road = address.get('road', 'Unknown street')
            house_number = address.get('house_number', '')
            city = address.get('city', 'Unknown city')
            return f"{road} {house_number}, {city}".strip().replace(' ,', ',')
    except Exception as e:
        print(f"Nominatim API failed: {e}")

    return 'Unknown address'

    # Функция для поиска ближайшего метро


def get_nearest_metro(lat, lon):
    time.sleep(random.uniform(1.1, 2))  # Задержка от 1.1 до 2 секунд
    OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
    NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "AudioLED XXL NotesApp/1.0 (support@audioledyxxl.ru)"

    # Сначала пытаемся получить данные через Overpass API
    overpass_query = f"""
    [out:json];
    (
        node(around:4000, {lat}, {lon})["railway"="station"]["station"="subway"];
    );
    out body;
    """
    try:
        response = requests.get(OVERPASS_API_URL, params={'data': overpass_query})
        response.raise_for_status()
        data = response.json()
        elements = data.get('elements', [])

        if elements:
            # Вычисляем ближайшую станцию метро
            nearest_station = None
            min_distance = float('inf')

            for element in elements:
                station_lat = element['lat']
                station_lon = element['lon']
                station_name = element['tags'].get('name', 'Unknown metro')

                # Вычисляем расстояние до станции метро
                distance = calculate_distance(lat, lon, station_lat, station_lon)

                if distance < min_distance:
                    min_distance = distance
                    nearest_station = station_name

            if nearest_station:
                return nearest_station
    except Exception as e:
        print(f"Overpass API failed: {e}")

    # Если Overpass не возвращает данные, используем Nominatim
    try:
        params = {'q': 'subway station', 'format': 'json', 'lat': lat, 'lon': lon, 'radius': 4000}
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(NOMINATIM_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            nearest_station = None
            min_distance = float('inf')

            for item in data:
                station_lat = float(item['lat'])
                station_lon = float(item['lon'])
                station_name = item.get('display_name', 'Unknown metro')

                # Вычисляем расстояние до станции метро
                distance = calculate_distance(lat, lon, station_lat, station_lon)

                if distance < min_distance:
                    min_distance = distance
                    nearest_station = station_name

            if nearest_station:
                return nearest_station
    except Exception as e:
        print(f"Nominatim API failed: {e}")

    return 'Unknown metro'


# Поиск записок пользователем

# noinspection PyUnreachableCode
@app.route("/", methods=['GET'])
@cross_origin()
def get_notes():
    name = request.args.get('user')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not name or not lat or not lon:
        return jsonify({"error": "Missing parameters: 'user', 'lat', or 'lon'"}), 400

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({"error": "Invalid latitude or longitude format"}), 400

    # Подключение к базе данных
    mydb = mysql.connector.connect(
        host="localhost",
        user="db_admin",
        password="admin456123",
        database="notes"
    )
    mycursor = mydb.cursor()

    # Проверяем, существует ли пользователь в таблице user_auth
    mycursor.execute("SELECT COUNT(*) FROM user_auth WHERE username = %s AND is_active = 1", (name,))
    user_exists = mycursor.fetchone()[0]

    if not user_exists:
        mycursor.close()
        mydb.close()
        return jsonify({"error": "User not registered or inactive"}), 404

    # Если пользователь существует, выполняем запрос на получение записок
    mycursor.execute("""
        SELECT id, username, title, text, latitude, longitude, address, nearest_metro, created_at
        FROM notes
        ORDER BY created_at DESC
    """)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    # Фильтруем записи по радиусу 1000 метров
    filtered_records = []
    for record in myresult:
        distance = calculate_distance(lat, lon, record[4], record[5])
        if distance <= 1000:  # Радиус в метрах
            filtered_records.append(record)

    # Формируем ответ
    data = {
        "c2array": True,
        "size": [len(filtered_records), 9, 1],
        "data": [
            [[record[0]], [record[1]], [record[2]], [record[3]], [record[4]], [record[5]], [record[6]], [record[7]],
             [record[8].strftime('%Y-%m-%d %H:%M:%S')]]
            for record in filtered_records
        ]
    }

    return jsonify(data), 200

    # Запрос с сортировкой по created_at в порядке убывания
    mycursor.execute("""
            SELECT id, username, title, text, latitude, longitude, address, nearest_metro, created_at
            FROM notes
            ORDER BY created_at DESC
        """)
    myresult = mycursor.fetchall()
    mycursor.close()

    filtered_records = []
    for record in myresult:
        distance = calculate_distance(lat, lon, record[4], record[5])
        if distance <= 1000:
            filtered_records.append(record)

    data = {
        "c2array": True,
        "size": [len(filtered_records), 9, 1],
        "data": [
            [[record[0]], [record[1]], [record[2]], [record[3]], [record[4]], [record[5]], [record[6]], [record[7]],
             [record[8].strftime('%Y-%m-%d %H:%M:%S')]]
            for record in filtered_records
        ]
    }
    return jsonify(data)


    return "Hello, get user"


# Обработчик POST запросов
# noinspection PyUnreachableCode
@app.route("/upload", methods=['POST'])
@cross_origin()
@token_required
def upload_notes():
    try:
        print(f"Request form: {request.form}")  # Вывод всего содержимого формы
        raw_data = request.form.get('data')
        if not raw_data:
            if len(request.form) == 1:
                raw_data = list(request.form.keys())[0]  # Извлекаем первый ключ, если форма содержит только одно поле
                print(f"Raw data extracted from first key: {raw_data}")
            else:
                print("No 'data' field provided in POST request.")
                return jsonify({"error": "No data provided"}), 400

        print(f"Raw data: {raw_data}")
        cleaned_data = clean_json(raw_data)
        parsed_data = json.loads(cleaned_data)
        print(f"Parsed JSON: {parsed_data}")

        if not parsed_data.get("c2array") or not parsed_data.get("data"):
            print("Invalid JSON structure.")
            return jsonify({"error": "Invalid JSON structure"}), 400

        data = parsed_data["data"]
        formatted_data = []
        for record in data:
            note_id = generate_unique_id()
            username = record[0][0]
            title = record[1][0]
            text = record[2][0].strip()  # Убираем лишние пробелы
            lat = float(record[4][0])
            lon = float(record[3][0])

            # Проверяем, что текст не пустой
            if not text:
                print(f"Skipped record with empty text for user {username}.")
                continue

            address = get_address_from_coords(lat, lon)
            metro = get_nearest_metro(lat, lon)
            formatted_data.append((note_id, username, title, text, lat, lon, address, metro))

        if not formatted_data:
            return jsonify({"error": "No valid data to insert"}), 400

        print(f"Formatted data for DB: {formatted_data}")
        result = insert_into_db(formatted_data)
        if "error" in result:
            print(f"Database insertion error: {result}")
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


def generate_random_coords(lat, lon, radius_meters):
    """
    Генерация случайных координат в пределах заданного радиуса (в метрах) от центральной точки.
    """
    earth_radius = 6371000  # Радиус Земли в метрах
    delta_lat = random.uniform(-radius_meters, radius_meters) / earth_radius * (180 / math.pi)
    delta_lon = random.uniform(-radius_meters, radius_meters) / earth_radius * (180 / math.pi) / math.cos(
        lat * math.pi / 180)
    return lat + delta_lat, lon + delta_lon


def generate_random_coords_russia():
    """
    Генерация случайных координат в пределах границ России.
    """
    lat = random.uniform(MIN_LAT, MAX_LAT)
    lon = random.uniform(MIN_LON, MAX_LON)
    return lat, lon


# Генерация записок через консоль
def generate_notes(mode):
    if mode == 'generaterandom':
        num_notes = int(input("Введите количество записок: "))

        def generate_coords():
            return generate_random_coords_russia()
    else:
        print("Неизвестный режим.")
        return

    # Подключение к базе данных
    mydb = mysql.connector.connect(
        host="localhost",
        user="db_admin",
        password="admin456123",
        database="notes"
    )
    mycursor = mydb.cursor()

    # Генерация записок
    for _ in range(num_notes):
        lat, lon = generate_coords()
        username = random.choice(random_usernames)
        title = random.choice(random_titles)
        text = random.choice(random_texts)
        address = get_address_from_coords(lat, lon)
        metro = get_nearest_metro(lat, lon)

        sql = """
            INSERT INTO notes (username, title, text, latitude, longitude, address, nearest_metro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        val = (username, title, text, lat, lon, address, metro)
        mycursor.execute(sql, val)

    mydb.commit()
    mycursor.close()
    mydb.close()
    print(f"{num_notes} записок успешно добавлено!")


# Запуск
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run the NotesApp server or perform CLI tasks.')
    subparsers = parser.add_subparsers(dest='command')

    # simulate_users command
    simulate_users_parser = subparsers.add_parser('simulate_users', help='Run user activity simulation')

    # generate_users command
    generate_users_parser = subparsers.add_parser('generate_users', help='Generate random users')
    generate_users_parser.add_argument('--count', type=int, default=1000, help='Number of users to generate')

    # generaterandom command
    generaterandom_parser = subparsers.add_parser('generaterandom', help='Generate random notes in random locations in Russia')
    generaterandom_parser.add_argument('--count', type=int, default=100, help='Number of notes to generate') # Added default count

    # generateradius command
    generateradius_parser = subparsers.add_parser('generateradius', help='Generate random notes within a specified radius')
    generateradius_parser.add_argument("--center", nargs=2, type=float, required=True, help="Center coordinates (latitude longitude)")
    generateradius_parser.add_argument("--radius", type=float, default=5.0, help="Radius in kilometers")
    generateradius_parser.add_argument("--count",  type=int,   default=100, help="Number of notes to generate")

    args = parser.parse_args()

    if args.command == "simulate_users":
        print("Запуск симуляции жизни пользователей...")
        threading.Thread(target=simulate_user_activity_optimized).start()
    elif args.command in ["generateradius", "generaterandom"]:
        if args.command == "generateradius":
            if not args.center or len(args.center) != 2:
                print("Error: --center requires exactly two coordinates (latitude longitude)")
                sys.exit(1)
            center_lat, center_lon = args.center
            generate_radius(center_lat, center_lon, args.radius, args.count)
        else:  # generaterandom
            num_notes = args.count
            for _ in range(num_notes):
                lat, lon = generate_random_coords_russia()
                insert_note(lat, lon)
            print(f"{num_notes} random notes successfully added!")
    elif args.command == "generate_users":
        print("Генерация пользователей...")
        generate_users(args.count)
    else:
        print("Неизвестная команда.")
    app.run(
    host='0.0.0.0',
    debug=True,
    ssl_context=('/var/www/audioledyxxl.ru/geo/certs/cert.pem', '/var/www/audioledyxxl.ru/geo/certs/key.pem')
    )

@app.route("/register_device", methods=['POST'])
def register_device():
    # TODO: Implement JWT authentication to get user_id
    # user_id = g.user.id  # once JWT is in place
    # Placeholder for now:
    user_id = request.json.get('user_id') # For testing without JWT

    token  = request.json.get("token")
    platform = request.json.get("platform", "android")

    if not user_id or not token or not platform:
        return jsonify({"error": "user_id, token, and platform are required"}), 400

    try:
        mydb = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME')
        )
        mycursor = mydb.cursor()

        sql = "REPLACE INTO user_devices (user_id, device_token, platform) VALUES (%s,%s,%s)"
        mycursor.execute(sql, (user_id, token, platform))
        mydb.commit()
        return jsonify({"ok": True}), 200

    except Exception as e:
        print(f"Error registering device: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'mycursor' in locals() and mycursor:
            mycursor.close()
        if 'mydb' in locals() and mydb:
            mydb.close()

# Константа для системного пользователя
SYSTEM_UID = 1  # Предполагаем, что ID 1 зарезервирован для системных операций

def random_coord_within_radius(center_lat: float, center_lon: float, radius_km: float) -> tuple[float, float]:
    """
    Генерирует случайные координаты в пределах заданного радиуса от центральной точки.
    
    Args:
        center_lat: Широта центральной точки
        center_lon: Долгота центральной точки
        radius_km: Радиус в километрах
        
    Returns:
        tuple[float, float]: Случайные координаты (широта, долгота)
    """
    # Конвертируем радиус из километров в градусы (примерно)
    radius_deg = radius_km / 111.32  # 111.32 км в одном градусе на экваторе
    
    # Генерируем случайное расстояние и угол
    distance = random.uniform(0, radius_deg)
    angle = random.uniform(0, 2 * math.pi)
    
    # Вычисляем смещение
    lat_offset = distance * math.cos(angle)
    lon_offset = distance * math.sin(angle)
    
    # Применяем смещение к центральным координатам
    new_lat = center_lat + lat_offset
    new_lon = center_lon + lon_offset
    
    return new_lat, new_lon

def insert_note(lat: float, lon: float, user_id: int = SYSTEM_UID) -> None:
    """
    Вставляет новую записку в базу данных.
    
    Args:
        lat: Широта
        lon: Долгота
        user_id: ID пользователя (по умолчанию SYSTEM_UID)
    """
    try:
        mydb = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME')
        )
        mycursor = mydb.cursor()
        
        # Получаем случайные данные для записки
        username = random.choice(random_usernames)
        title = random.choice(random_titles)
        text = random.choice(random_texts)
        address = get_address_from_coords(lat, lon)
        metro = get_nearest_metro(lat, lon)
        
        # Вставляем записку
        sql = """
            INSERT INTO notes (username, title, text, latitude, longitude, address, nearest_metro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        val = (username, title, text, lat, lon, address, metro)
        mycursor.execute(sql, val)
        mydb.commit()
        
    except Exception as e:
        print(f"Error inserting note: {e}")
        raise
    finally:
        if 'mycursor' in locals() and mycursor:
            mycursor.close()
        if 'mydb' in locals() and mydb:
            mydb.close()

def generate_radius(center_lat: float, center_lon: float, radius_km: float, count: int) -> None:
    """
    Генерирует указанное количество записок в пределах заданного радиуса.
    
    Args:
        center_lat: Широта центральной точки
        center_lon: Долгота центральной точки
        radius_km: Радиус в километрах
        count: Количество записок для генерации
    """
    print(f"Generating {count} notes within {radius_km}km radius of ({center_lat}, {center_lon})")
    
    for i in range(count):
        try:
            lat, lon = random_coord_within_radius(center_lat, center_lon, radius_km)
            insert_note(lat, lon)
            if (i + 1) % 10 == 0:  # Прогресс каждые 10 записок
                print(f"Generated {i + 1} notes...")
        except Exception as e:
            print(f"Error generating note {i + 1}: {e}")
            continue
    
    print(f"Successfully generated {count} notes!")

# JWT конфигурация
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = timedelta(days=1)

def generate_token(user_id: int) -> str:
    """
    Генерирует JWT токен для пользователя.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        str: JWT токен
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def token_required(f):
    """
    Декоратор для защиты маршрутов, требующих аутентификации.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Получаем токен из заголовка Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Декодируем токен
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            g.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# Эндпоинт для аутентификации
@app.route("/login", methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing username or password'}), 400
        
        mydb = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME')
        )
        mycursor = mydb.cursor(dictionary=True)
        
        # Проверяем учетные данные
        mycursor.execute(
            "SELECT id, password_hash FROM user_auth WHERE username = %s AND is_active = 1",
            (username,)
        )
        user = mycursor.fetchone()
        
        if not user or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Генерируем токен
        token = generate_token(user['id'])
        
        return jsonify({
            'token': token,
            'user_id': user['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'mycursor' in locals() and mycursor:
            mycursor.close()
        if 'mydb' in locals() and mydb:
            mydb.close()

def verify_password(password: str, password_hash: str) -> bool:
    """
    Проверяет соответствие пароля его хешу.
    
    Args:
        password: Пароль в открытом виде
        password_hash: Хеш пароля
        
    Returns:
        bool: True если пароль верный, False в противном случае
    """
    return hashlib.sha256(password.encode()).hexdigest() == password_hash
