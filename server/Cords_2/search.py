from Cordsold.database_ import get_all_notes
from geocoding import calculate_distance

def get_series_notes(series_id):
    """
    Получить все записки в серии по series_id.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM notes WHERE series_id = ? ORDER BY series_order
    """, (series_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_next_unfound_note(series, found_notes):
    """
    Найти следующую не найденную записку в серии.
    """
    for note in series:
        if note[0] not in found_notes:  # note[0] — это id записки
            return note
    return None

def find_note_and_series(lat, lon, radius=200):
    """
    Найти записку по координатам и установить связь с серией.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Найти ближайшую записку в радиусе
    cursor.execute("""
        SELECT * FROM notes
        WHERE ((latitude - ?) * (latitude - ?) + (longitude - ?) * (longitude - ?)) <= (? / 111111.0) * (? / 111111.0)
    """, (lat, lat, lon, lon, radius, radius))
    note = cursor.fetchone()

    if note:
        note_id, username, text, lat, lon, address, metro, metro_distance, series_id, series_order = note

        # Если записка принадлежит серии
        if series_id:
            series_notes = get_series_notes(series_id)

            # Найти следующую записку
            next_note = next((n for n in series_notes if n[8] > series_order), None)

            return {
                "note": note,
                "series": series_notes,
                "next_note": next_note
            }
    conn.close()
    return None


def search_notes_nearby(user_coords, radius=200, found_notes=set()):
    """
    Найти записки в радиусе от пользователя, включая логику работы с сериями.
    """
    notes = get_all_notes()
    nearby_notes = []
    for note in notes:
        note_coords = (note[3], note[4])  # latitude, longitude
        distance = calculate_distance(user_coords, note_coords)
        if distance <= radius:
            if note[7]:  # Если записка принадлежит серии (series_id не NULL)
                series = get_series_notes(note[7])
                if note[8] == 1:  # Если это первая записка в серии
                    next_note = get_next_unfound_note(series, found_notes)
                    link_address = next_note[5] if next_note else "Все записки найдены."
                else:
                    link_address = series[0][5]  # Первая записка серии
                note_data = {
                    "id": note[0],
                    "username": note[1],
                    "text": note[2],
                    "address": note[5],
                    "nearest_metro": note[6],
                    "distance": f"{distance:.2f} m",
                    "link_address": link_address,
                    "series_info": f"{note[8]}/{len(series)}"
                }
            else:  # Обычная записка
                note_data = {
                    "id": note[0],
                    "username": note[1],
                    "text": note[2],
                    "address": note[5],
                    "nearest_metro": note[6],
                    "distance": f"{distance:.2f} m"
                }
            nearby_notes.append(note_data)
    return nearby_notes
