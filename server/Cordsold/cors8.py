
import json

import re

import requests



from tkinter import Tk, Text, Button, Label, END


# API ключ 2ГИС

DGIS_API_KEY = "66ee0d69-3732-41f7-a049-b039b100a1d2"  # Вставьте ваш ключ API 2ГИС



def clean_json(raw_data):

   """

   Очистить входные данные JSON: удалить лишние символы, исправить формат.

   """

   start = raw_data.find("{")

   end = raw_data.rfind("}") + 1

   json_data = raw_data[start:end]

   cleaned_data = re.sub(r"\n", "", json_data)

   cleaned_data = re.sub(r"\s+", " ", cleaned_data)

   return cleaned_data



from geopy.distance import geodesic

def calculate_distance(point1, point2):
    """
    Рассчитать расстояние между двумя точками в метрах.
    """
    return geodesic(point1, point2).meters


def find_nearest_address_with_distance(coords):
    """
    Найти ближайший адрес через Catalog API 2ГИС с ручной проверкой расстояния.
    """
    try:
        lat, lon = coords
        url = "https://catalog.api.2gis.ru/3.0/items"
        params = {
            "key": DGIS_API_KEY,
            "q": "адрес",  # Или убрать для общего поиска
            "point": f"{lon},{lat}",
            "fields": "items.point,items.full_name,items.address_name",
            "radius": 3000,  # Радиус поиска
            "sort": "distance",  # Сортировка по расстоянию
            "page_size": 5,  # Получить до 5 объектов
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Лог ответа для отладки
        print("Response from Catalog API (address):", json.dumps(data, indent=4, ensure_ascii=False))

        if "result" in data and "items" in data["result"] and data["result"]["items"]:
            closest_item = None
            closest_distance = float("inf")
            for item in data["result"]["items"]:
                item_coords = (item["point"]["lat"], item["point"]["lon"])
                distance = calculate_distance(coords, item_coords)
                if distance < closest_distance:
                    closest_item = item
                    closest_distance = distance

            if closest_item:
                address = closest_item.get("address_name", "Unknown address")
                return f"{address} (Distance: {closest_distance:.2f} m)"
        return "No results found"
    except Exception as e:
        return f"Error: {e}"





def find_nearest_metro(coords):

   """

   Найти ближайшее метро через API 2ГИС.

   :param coords: tuple (latitude, longitude) - координаты

   :return: Название станции метро

   """

   try:

       lat, lon = coords

       url = "https://catalog.api.2gis.ru/3.0/items"

       params = {

           "key": DGIS_API_KEY,

           "q": "станция метро",

           "point": f"{lon},{lat}",

           "fields": "items.point,items.full_name,items.address_name",

           "radius": 3000,  # Радиус поиска в метрах

           "sort": "distance",

           "page_size": 1,  # Вернуть только один ближайший объект

       }

       response = requests.get(url, params=params)

       response.raise_for_status()

       data = response.json()


       if "result" in data and "items" in data["result"] and data["result"]["items"]:

           item = data["result"]["items"][0]

           name = item.get("full_name", "Unknown metro")

           address = item.get("address_name")

           return f"{name}"

       else:

           return "Unknown metro"

   except Exception as e:

       return f"Error: {e}"



def process_input():
    """
    Обработать входные данные, найти ближайший адрес и метро, и отобразить результат.
    """
    try:
        raw_data = input_text.get("1.0", END).strip()
        cleaned_data = clean_json(raw_data)
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

            nearest_address = find_nearest_address_with_distance(coords)
            nearest_metro = find_nearest_metro(coords)

            results.append({
                "username": usernames[i][0],
                "note_text": texts[i][0],
                "date": dates[i][0],
                "nearest_address": nearest_address,
                "nearest_metro": nearest_metro
            })

        output_text.delete("1.0", END)
        output_text.insert(END, json.dumps(results, indent=4, ensure_ascii=False))
    except Exception as e:
        output_text.insert(END, f"Ошибка: {e}\n")




# Создание GUI

root = Tk()

root.title("Nearest Address and Metro Finder - 2ГИС Geocoder API")


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

