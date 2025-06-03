import mysql.connector
import random
import requests
import math

# Списки случайных текстов и пользователей
random_texts = [
    "Советуем посетить", "Не забудь об этом месте", "Записка для всех", "Просто запись", "Я был здесь",
    "Записка от Андрея", "Здесь весело", "Рекомендую посетить", "Записка для хороших людей", "Секретное место",
    "Важная заметка", "Нужно помнить", "Очень интересное место", "Записка для вас", "Друзья, не забывайте",
    "Место для прогулок", "Далеко от суеты", "Место для отдыха", "Скоро буду", "Приходите сюда"
]

random_usernames = [
    "Андрей", "Елена", "Дмитрий", "Ольга", "Сергей", "Алексей", "Ирина", "Анна", "Екатерина", "Мария",
    "Юлия", "Иван", "Роман", "Максим", "Анатолий", "Виктория", "Татьяна", "Светлана", "Николай", "Владимир"
]

# Устанавливаем USER_AGENT
USER_AGENT = "AudioLED XXL NotesApp/1.0 (support@audioledyxxl.ru)"


# Функция для генерации случайных координат в радиусе 500 метров
def generate_random_coords(lat, lon, radius_meters):
    # Радиус Земли в метрах
    earth_radius = 6371000
    # Случайное смещение
    delta_lat = random.uniform(-radius_meters, radius_meters) / earth_radius * (180 / math.pi)
    delta_lon = random.uniform(-radius_meters, radius_meters) / earth_radius * (180 / math.pi) / math.cos(
        lat * math.pi / 180)

    return lat + delta_lat, lon + delta_lon


# Получаем ближайший адрес с помощью Overpass API
def get_address_from_coords(lat, lon):
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
    response = requests.get(OVERPASS_API_URL, params={'data': overpass_query})
    data = response.json()

    for element in data['elements']:
        if 'tags' in element and 'addr:full' in element['tags']:
            return element['tags']['addr:full']
        elif 'tags' in element and 'addr:street' in element['tags']:
            return f"{element['tags'].get('addr:street', 'Unknown street')}, {element['tags'].get('addr:housenumber', 'Unknown number')}"

    return 'Unknown address'


# Получаем ближайшую станцию метро с помощью Overpass API
def get_nearest_metro(lat, lon):
    OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
        node(around:2000, {lat}, {lon})["railway"="station"]["station"="subway"];
    );
    out body;
    """
    response = requests.get(OVERPASS_API_URL, params={'data': overpass_query})
    data = response.json()

    if data['elements']:
        metro_name = data['elements'][0]['tags'].get('name', 'Unknown metro')
        return metro_name
    else:
        return None


# Поиск ближайшего метро через Nominatim API
def get_nearest_metro_nominatim(lat, lon):
    NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': 'subway station',
        'format': 'json',
        'lat': lat,
        'lon': lon,
        'radius': 2000
    }
    headers = {
        'User-Agent': USER_AGENT
    }

    response = requests.get(NOMINATIM_API_URL, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            metro_name = data[0].get('display_name', 'Unknown metro')
            return metro_name
    return 'Unknown metro'


def get_address_from_nominatim(lat, lon):
    NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {
        'User-Agent': USER_AGENT
    }
    response = requests.get(NOMINATIM_API_URL, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'address' in data:
            address = data['address']
            return f"{address.get('road', 'Unknown street')}, {address.get('house_number', 'Unknown number')}"
    return 'Unknown address'


# Подключение к базе данных
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="notes_db",
        password="admin456123",
        database="notes_db_mysql"
    )



# Функция для получения cluster_id
def get_cluster_id(mycursor, lat, lon):
    sql = """
    SELECT cluster_id FROM clusters
    WHERE min_lat <= %s AND max_lat >= %s AND min_lon <= %s AND max_lon >= %s
    """
    val = (lat, lat, lon, lon)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    return result[0] if result else None


# Основная функция для добавления записок
def generate_notes():
    lat_origin = float(input("Введите широту: "))
    lon_origin = float(input("Введите долготу: "))
    num_notes = int(input("Введите количество записок: "))

    mydb = connect_to_db()
    mycursor = mydb.cursor()

    for i in range(num_notes):
        lat, lon = generate_random_coords(lat_origin, lon_origin, 500)
        username = random.choice(random_usernames)
        text = random.choice(random_texts)

        address = get_address_from_coords(lat, lon)
        if address == 'Unknown address':
            address = get_address_from_nominatim(lat, lon)

        nearest_metro = get_nearest_metro(lat, lon)
        if not nearest_metro:
            nearest_metro = get_nearest_metro_nominatim(lat, lon)

        cluster_id = get_cluster_id(mycursor, lat, lon)
        if not cluster_id:
            print(f"Не удалось определить кластер для координат: {lat}, {lon}")
            continue

        metro_distance = random.uniform(500, 1000)
        series_id = 220
        series_order = 1

        sql = """
        INSERT INTO notes (username, text, latitude, longitude, address, nearest_metro, metro_distance, series_id, series_order, cluster_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (username, text, lat, lon, address, nearest_metro, metro_distance, series_id, series_order, cluster_id)

        mycursor.execute(sql, val)

    mydb.commit()
    mycursor.close()
    mydb.close()

    print(f"Добавлено {num_notes} записок.")


if __name__ == "__main__":
    generate_notes()
