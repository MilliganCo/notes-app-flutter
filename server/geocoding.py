import requests
from geopy.distance import geodesic
import time

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "AudioLED XXL NotesApp/1.0 (support@audioledyxxl.ru)"


def calculate_distance(point1, point2):
    """
    Рассчитать расстояние между двумя точками в метрах.
    """
    return geodesic(point1, point2).meters


def find_nearest_place(coords, kind):
    """
    Найти ближайшее место через Overpass API (адрес или метро).
    """
    lat, lon = coords
    headers = {"User-Agent": USER_AGENT}

    if kind == "house":
        # Поиск ближайшего адреса (любого объекта)
        query = f"""
        [out:json];
        (
          node["name"](around:200,{lat},{lon});
          way["name"](around:200,{lat},{lon});
          relation["name"](around:200,{lat},{lon});
        );
        out center 1;
        """
    elif kind == "metro":
        # Поиск ближайшей станции метро
        query = f"""
        [out:json];
        (
          node["railway"="subway"]["name"](around:1000,{lat},{lon});
          way["railway"="subway"]["name"](around:1000,{lat},{lon});
        );
        out body;
        """
    else:
        return f"Error: Unsupported kind '{kind}'", None

    try:
        response = requests.post(OVERPASS_API_URL, data=query, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "elements" not in data or not data["elements"]:
            # Если данных нет, возвращаем сообщение
            return f"No {kind} found", None

        # Обработка данных для адреса
        if kind == "house":
            nearest = data["elements"][0]
            if "tags" in nearest and "name" in nearest["tags"]:
                address = nearest["tags"]["name"]
                return address, None
            return "Unknown address", None

        # Обработка данных для метро
        elif kind == "metro":
            nearest = data["elements"][0]
            if "tags" in nearest and "name" in nearest["tags"]:
                metro_name = nearest["tags"]["name"]
                metro_coords = (float(nearest["lat"]), float(nearest["lon"]))
                distance = calculate_distance(coords, metro_coords)
                return metro_name, distance
            return "Unknown metro", None

    except requests.exceptions.RequestException as e:
        return f"Error: {e}", None


def rate_limited_request(func, *args, **kwargs):
    """
    Ограничение запросов: 1 запрос в секунду.
    """
    time.sleep(1)  # Задержка 1 секунда между запросами
    return func(*args, **kwargs)
