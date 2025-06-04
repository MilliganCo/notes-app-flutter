import requests
from geopy.distance import geodesic

USER_AGENT = "AudioLED XXL NotesApp/1.0 (support@audioledyxxl.ru)"

def calculate_distance(point1, point2):
    """
    Рассчитать расстояние между двумя точками в метрах.
    """
    return geodesic(point1, point2).meters

def find_nearest_address(coords):
    """
    Найти ближайший адрес через Nominatim API (обратное геокодирование).
    """
    try:
        lat, lon = coords
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "jsonv2",
        }
        headers = {"User-Agent": USER_AGENT}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()

        if "display_name" in data:
            return data["display_name"], None
        return "Unknown address", None
    except Exception as e:
        return f"Error: {e}", None

def find_nearest_place(coords, kind):
    """
    Найти ближайшее место через Nominatim API (например, станцию метро).
    """
    try:
        lat, lon = coords

        if kind == "metro":
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": "метро",  # Текстовый поиск метро
                "format": "json",
                "extratags": 1,
                "bounded": 1,
                "viewbox": "37.35,55.95,37.85,55.55",  # Ограничение на область Москвы
            }
        else:
            raise ValueError("Unsupported kind for place search")

        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()

        if data:
            # Находим ближайший объект (метро)
            result = min(
                data,
                key=lambda place: calculate_distance(coords, (float(place["lat"]), float(place["lon"]))),
            )
            place_name = result["display_name"]
            place_coords = (float(result["lat"]), float(result["lon"]))
            distance = calculate_distance(coords, place_coords)
            return place_name, distance
        return "Unknown place", None
    except Exception as e:
        return f"Error: {e}", None

# Ограничение запросов: 1 запрос в секунду
def rate_limited_request(func, *args, **kwargs):
    time.sleep(1)  # Задержка 1 секунда
    return func(*args, **kwargs)
