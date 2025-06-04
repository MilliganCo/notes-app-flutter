import json
import re
import requests
import os
import tkinter
from geopy.distance import geodesic
from tkinter import Tk, Text, Button, Label, END

# API ключ Яндекс.Карт
YANDEX_API_KEY = "fc164944-953f-414a-8f60-1b7207f2273f"

def clean_json(raw_data):
    """
    Очистить входные данные JSON: удалить лишние символы, исправить формат.
    """
    start = raw_data.find("{")
    end = raw_data.rfind("}") + 1
    json_data = raw_data[start:end]
    cleaned_data = re.sub(r"[\n\r\t]", "", json_data)  # Убираем \n, \r, \t
    cleaned_data = re.sub(r"\s+", " ", cleaned_data)  # Убираем лишние пробелы
    return cleaned_data.strip()

def calculate_distance(point1, point2):
    """
    Рассчитать расстояние между двумя точками в метрах.
    """
    return geodesic(point1, point2).meters

def find_nearest_address(coords):
    """
    Найти ближайший адрес через HTTP Геокодер API Яндекс.Карт.
    """
    try:
        lat, lon = coords
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "kind": "house",  # Искать только здания
            "results": 1  # Вернуть только один ближайший объект
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Лог для отладки
        print("Response from Yandex Geocoder API (address):", json.dumps(data, indent=4, ensure_ascii=False))

        if "response" in data:
            feature = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            address = feature["metaDataProperty"]["GeocoderMetaData"]["text"]
            point = feature["Point"]["pos"].split()
            address_coords = (float(point[1]), float(point[0]))
            distance = calculate_distance(coords, address_coords)
            return address, distance
        return "No results found", None
    except Exception as e:
        return f"Error: {e}", None

def find_nearest_metro(coords):
    """
    Найти ближайшее метро через HTTP Геокодер API Яндекс.Карт.
    """
    try:
        lat, lon = coords
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "kind": "metro",  # Искать только станции метро
            "results": 1  # Вернуть только один ближайший объект
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Лог для отладки
        print("Response from Yandex Geocoder API (metro):", json.dumps(data, indent=4, ensure_ascii=False))

        if "response" in data:
            feature = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            name = feature["metaDataProperty"]["GeocoderMetaData"]["text"]
            point = feature["Point"]["pos"].split()
            metro_coords = (float(point[1]), float(point[0]))
            distance = calculate_distance(coords, metro_coords)
            return name, distance
        return "No metro found", None
    except Exception as e:
        return f"Error: {e}", None

def process_input():
    """
    Обработать входные данные, найти ближайший адрес и метро, и отобразить результат.
    """
    try:
        raw_data = input_text.get("1.0", END).strip()
        cleaned_data = clean_json(raw_data)
        print("Очищенные данные:", cleaned_data)
        parsed_data = json.loads(cleaned_data)

        if not parsed_data.get("c2array") or not parsed_data.get("data"):
            output_text.insert(END, "Ошибка: Неверная структура данных\n")
            return

        data = parsed_data["data"]
        results = []

        usernames = data[0]
        latitudes = data[1]
        longitudes = data[2]
        texts = data[3]
        dates = data[4]

        for i in range(len(usernames)):
            latitude = float(latitudes[i][0])
            longitude = float(longitudes[i][0])
            coords = (latitude, longitude)

            nearest_address, address_distance = find_nearest_address(coords)
            nearest_metro, metro_distance = find_nearest_metro(coords)

            results.append({
                "username": usernames[i][0],
                "note_text": texts[i][0],
                "date": dates[i][0],
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "nearest_address": nearest_address,
                "address_distance_m": f"{address_distance:.2f} m" if address_distance else "Unknown distance",
                "nearest_metro": nearest_metro,
                "metro_distance_m": f"{metro_distance:.2f} m" if metro_distance else "Unknown distance"
            })

        output_text.delete("1.0", END)
        output_text.insert(END, json.dumps(results, indent=4, ensure_ascii=False))
    except Exception as e:
        output_text.insert(END, f"Ошибка: {e}\n")

# Создание GUI
root = Tk()
root.title("Nearest Address and Metro Finder - Яндекс.Карты API")

input_label = Label(root, text="Введите данные клиента:")
input_label.pack()

input_text = Text(root, height=15, width=80)
input_text.pack()

process_button = Button(root, text="Обработать", command=process_input)
process_button.pack()

output_label = Label(root, text="Результат:")
output_label.pack()

output_text = Text(root, height=15, width=80)
output_text.pack()

root.mainloop()
