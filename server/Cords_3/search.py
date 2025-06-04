from database import get_all_notes, get_series_notes, get_user_notes
from geocoding import calculate_distance


def search_notes_nearby(user_coords, user_id=None, radius=200):
    """
    Найти записки в радиусе от пользователя, включая логику работы с сериями и проверку найденных записок.
    """
    # Получаем все записки и найденные записки текущего пользователя
    notes = get_all_notes()  # Все записки в базе
    user_found_notes = get_user_notes(user_id) if user_id else []  # Записки, уже найденные пользователем
    user_found_note_ids = {note[0] for note in user_found_notes}  # Собираем ID найденных записок

    nearby_notes = []  # Список записок, найденных в радиусе

    for note in notes:
        note_coords = (note[3], note[4])  # latitude, longitude
        distance = calculate_distance(user_coords, note_coords)

        if distance <= radius:
            # Проверяем, принадлежит ли записка серии
            if note[8]:  # Если series_id не NULL
                series = get_series_notes(note[8])  # Получить все записки этой серии

                if series:
                    # Формируем информацию о серии
                    series_info = f"Серия {note[8]}, записка {note[9]}/{len(series)}"

                    # Если это первая записка в серии
                    if note[9] == 1:
                        # Находим следующую не найденную записку
                        next_note = next(
                            (n for n in series if n[9] > note[9] and n[0] not in user_found_note_ids),
                            None,
                        )
                        if next_note:
                            link_address = f"Записка {next_note[9]}/{len(series)}, {next_note[5]}"
                        else:
                            link_address = "Все записки найдены."
                    else:
                        # Если это не первая записка, ищем первую или следующую ненайденную
                        first_note = series[0]
                        if first_note[0] not in user_found_note_ids:
                            link_address = f"Записка 1/{len(series)}, {first_note[5]}"
                        else:
                            # Найти следующую не найденную записку
                            next_note = next(
                                (n for n in series if n[0] not in user_found_note_ids),
                                None,
                            )
                            if next_note:
                                link_address = f"Записка {next_note[9]}/{len(series)}, {next_note[5]}"
                            else:
                                link_address = "Все записки найдены."
                else:
                    series_info = "Нет данных"
                    link_address = "Серия не найдена."

                note_data = {
                    "id": note[0],
                    "username": note[1],
                    "text": note[2],
                    "address": note[5],
                    "nearest_metro": note[6],
                    "distance": f"{distance:.2f} m",
                    "series_info": series_info,
                    "link_address": link_address,
                }

            else:  # Обычная записка
                note_data = {
                    "id": note[0],
                    "username": note[1],
                    "text": note[2],
                    "address": note[5],
                    "nearest_metro": note[6],
                    "distance": f"{distance:.2f} m",
                    "series_info": "Нет",
                    "link_address": "Нет",
                }

            nearby_notes.append(note_data)

    return nearby_notes
