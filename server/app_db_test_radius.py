from flask import Flask, request, send_file, jsonify
from flask_cors import CORS, cross_origin
import mysql.connector
import pandas as pd
import random
import tempfile
import os
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

CORS(app)

# Функция для расчета расстояния между двумя точками (в метрах)
def calculate_distance(lat1, lon1, lat2, lon2):
    # Преобразуем значения координат в тип float
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    print(f"Calculating distance from ({lat1}, {lon1}) to ({lat2}, {lon2})")

    R = 6371  # Радиус Земли в километрах
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c * 1000  # Возвращаем расстояние в метрах

    print(f"Calculated distance: {distance} meters")

    return distance

@app.route("/", methods=['GET', 'OPTIONS', 'POST'])
@cross_origin()
def test():
    if request.method == 'POST':
        print(request.data)
        print(request.values)
        return "Hello"

    if request.method == 'GET':
        print(request.args)
        name = request.args.get('user')
        lat = float(request.args.get('lat'))  # Получаем широту клиента
        lon = float(request.args.get('lon'))  # Получаем долготу клиента

        if name == 'andr':
            # Подключение к базе данных
            mydb = mysql.connector.connect(
                host="localhost",
                user="notes_db",
                password="admin456123",
                database="notes_db_mysql"
            )
            mycursor = mydb.cursor()

            # Извлекаем только нужные столбцы из базы данных (без cluster_id)
            mycursor.execute("""
                SELECT id, username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order
                FROM notes
            """)
            myresult = mycursor.fetchall()
            mycursor.close()

            # Преобразование данных в DataFrame
            df = pd.DataFrame(myresult)

            # Переименование столбцов
            df.columns = ['id', 'username', 'text', 'latitude', 'longitude', 'address', 'nearest_metro', 'metro_distance', 'series_id', 'series_order']

            # Фильтрация данных, оставляем только те записи, которые находятся в радиусе 1000 метров от клиента
            filtered_records = []
            for _, row in df.iterrows():
                distance = calculate_distance(lat, lon, row['latitude'], row['longitude'])
                print(f"Distance to record: {distance}")  # Выводим расстояние для каждой записи
                if distance <= 1000:  # Фильтруем только записи в радиусе 1000 метров
                    filtered_records.append(row.to_dict())

            # Создание структуры для JSON: добавляем 'count' в начало
            data = {
                'count': len(filtered_records),
                'records': filtered_records
            }

            # Создание временного файла для передачи
            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.json') as tmpfile:
                tmpfile.write(pd.Series(data).to_json(force_ascii=False))
                temp_file_name = tmpfile.name  # Сохраняем имя временного файла для отправки

            # Отправка файла клиенту
            response = send_file(temp_file_name)

            # Удаление временного файла после отправки
            os.remove(temp_file_name)
            print(f"Temporary file {temp_file_name} has been deleted.")

            return response

        return "Hello, get user"



if __name__ == '__main__':
    # Запуск сервера
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('certs/cert.pem', 'certs/key.pem'))
