import random
from geocoding import find_nearest_place



def enrich_notes_with_geodata(notes):
    """
    Обогащает записки ближайшими адресами и станциями метро.
    """
    enriched_notes = []
    for note in notes:
        lat, lon = note[2], note[3]
        address, _ = find_nearest_place((lat, lon))
        place_name, distance = find_nearest_place(coords, kind="metro")
        enriched_notes.append((*note, address, place_name, distance))
    return enriched_notes


def generate_series(series_id, size):
    """
    Генерация серии записок с указанным идентификатором серии и размером.
    """
    series = []
    for i in range(1, size + 1):  # Порядковый номер начинается с 1
        lat, lon = generate_random_coordinates()
        username = generate_random_name()
        text = f"Серия {series_id}, записка {i}/{size}"

        # Найти ближайший адрес
        address, _ = find_nearest_place((lat, lon), kind="house")

        # Найти ближайшее метро
        metro_name, _ = find_nearest_place((lat, lon), kind="metro")

        # Добавить данные в список серии
        series.append((username, text, lat, lon, address, metro_name, series_id, i))
    return series

def generate_random_notes(count):
    """
    Генерация случайных записок вне серии.
    """
    notes = []
    for _ in range(count):
        lat, lon = generate_random_coordinates()
        username = generate_random_name()
        text = generate_random_text()
        notes.append((username, text, lat, lon, None, None))  # None для series_id и order
    return notes

def generate_random_coordinates():
    """
    Сгенерировать случайные координаты в пределах Москвы.
    """
    min_lat, max_lat = 55.55, 55.95
    min_lon, max_lon = 37.35, 37.85
    return round(random.uniform(min_lat, max_lat), 6), round(random.uniform(min_lon, max_lon), 6)

def generate_random_name():
    """
    Генерация случайного имени.
    """
    names = ["Алексей", "Ирина", "Ольга", "Сергей", "Анна", "Дмитрий", "Елена"]
    return random.choice(names)

def generate_random_text():
    """
    Генерация случайного текста заметки.
    """
    texts = [
        "Записка для всех.",
        "Не забудь об этом месте.",
        "Просто записка.",
        "Замечательное место.",
        "Я был здесь.",
        "Советую посетить.",
    ]
    return random.choice(texts)
