import requests
from geopy.distance import geodesic

YANDEX_API_KEY = "fc164944-953f-414a-8f60-1b7207f2273f"

def calculate_distance(point1, point2):
    """
    Рассчитать расстояние между двумя точками в метрах.
    """
    return geodesic(point1, point2).meters

def find_nearest_place(coords, kind):
    """
    Найти ближайшее место через Яндекс API (дом, метро, или другое).
    """
    try:
        lat, lon = coords
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "kind": kind,  # Тип места: дом, метро, и т.д.
            "results": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "response" in data:
            feature = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            place_name = feature["metaDataProperty"]["GeocoderMetaData"]["text"]
            point = feature["Point"]["pos"].split()
            place_coords = (float(point[1]), float(point[0]))
            distance = calculate_distance(coords, place_coords)
            return place_name, distance
        return "Unknown place", None
    except Exception as e:
        return f"Error: {e}", None
