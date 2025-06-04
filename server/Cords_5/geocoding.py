import requests
from geopy.distance import geodesic
import time

NOMINATIM_URL = "https://nominatim.openstreetmap.org"
USER_AGENT = "AudioLED XXL NotesApp/1.0 (support@audioledyxxl.ru)"

def calculate_distance(point1, point2):
    """
    Рассчитать расстояние между двумя точками в метрах.
    """
    return geodesic(point1, point2).meters

def find_nearest_place(coords, kind):
    """
    Найти ближайшее место через Nominatim API (адрес или метро).
    """
    lat, lon = coords
    headers = {"User-Agent": USER_AGENT}

    if kind == "house":
        # Поиск ближайшего адреса
        url = f"{NOMINATIM_URL}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "jsonv2",
        }
    elif kind == "metro":
        # Поиск метро в радиусе от точки
        url = f"{NOMINATIM_URL}/search"
        params = {
            "q": "станция метро",  # Специфичный поиск станций метро
            "format": "json",
            "extratags": 1,
            "bounded": 1,
            "viewbox": "37.35,55.95,37.85,55.55",
            "lat": lat,  # Ограничиваем поиск радиусом
            "lon": lon
        }
    else:
        return f"Error: Unsupported kind '{kind}'", None

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if kind == "house":
            # Обработка данных для адреса
            address = data.get("display_name", "Unknown address")
            return address, None
        elif kind == "metro":
            # Обработка данных для метро
            if data:
                nearest_metro = data[0].get("display_name", "Unknown metro")
                metro_coords = (float(data[0]["lat"]), float(data[0]["lon"]))
                distance = calculate_distance(coords, metro_coords)
                return nearest_metro, distance
            return "No metro found", None
    except requests.exceptions.RequestException as e:
        return f"Error: {e}", None


def rate_limited_request(func, *args, **kwargs):
    """
    Ограничение запросов: 1 запрос в секунду.
    """
    time.sleep(1)  # Задержка 1 секунда между запросами
    return func(*args, **kwargs)
