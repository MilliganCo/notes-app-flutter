from database import get_all_notes, get_series_notes, get_user_notes
from geocoding import calculate_distance

def search_notes_nearby(user_coords, user_id=None, radius=200):
    """
    Найти записки в радиусе от пользователя, включая логику работы с сериями и проверку найденных записок.
    """
    notes = get_all_notes()
    user_found_notes = get_user_notes(user_id) if user_id else []
    user_found_note_ids = {note[0] for note in user_found_notes}

    nearby_notes = []

    for note in notes:
        note_coords = (note[3], note[4])  # latitude, longitude
        distance = calculate_distance(user_coords, note_coords)

        if distance <= radius:
            if note[8]:  # Если записка принадлежит серии (series_id не NULL)
                series = get_series_notes(note[8])

                if series:
                    series_info = f"Серия {note[8]}, записка {note[9]}/{len(series)}"

                    if note[9] == 1:
                        next_note = next(
                            (n for n in series if n[0] not in user_found_note_ids),
                            None,
                        )
                        if next_note:
                            link_address = f"Записка {next_note[9]}/{len(series)}, {next_note[5]}"
                        else:
                            link_address = "Все записки найдены."
                    else:
                        first_note = series[0]
                        if first_note[0] not in user_found_note_ids:
                            link_address = f"Записка 1/{len(series)}, {first_note[5]}"
                        else:
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
