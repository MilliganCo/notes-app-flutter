import tkinter as tk
from tkinter import messagebox, simpledialog
from Cordsold.database_ import insert_series
from utils import generate_random_notes, generate_series
from search import search_notes_nearby

# Создаём интерфейс
def create_ui():
    """
    Создание основного интерфейса.
    """
    root = tk.Tk()
    root.title("Notes App")

    def generate_notes_ui():
        """
        Генерация обычных записок через интерфейс.
        """
        count = simpledialog.askinteger("Генерация записок", "Сколько записок создать?", minvalue=1, maxvalue=100)
        if count:
            notes = generate_random_notes(count)
            for note in notes:
                insert_note(note)
            messagebox.showinfo("Генерация", f"{count} записок успешно создано.")

    def generate_series_ui():
        """
        Генерация серии записок через интерфейс.
        """
        series_id = simpledialog.askinteger("Серия ID", "Введите ID для серии:")
        size = simpledialog.askinteger("Размер серии", "Введите количество записок в серии:", minvalue=2, maxvalue=10)
        if series_id and size:
            series = generate_series(series_id, size)
            insert_series(series)
            messagebox.showinfo("Серии", f"Серия {series_id} из {size} записок успешно создана.")

    def handle_submit():
        series_id = int(series_id_entry.get())
        size = int(size_entry.get())

        # Генерация координат, имен и текста записок
        raw_series = generate_series(series_id, size)

        # Обогащение записок адресами и метро
        enriched_series = enrich_notes_with_geodata(raw_series)

        # Запись в базу данных
        insert_series(enriched_series)

        messagebox.showinfo("Успех", f"Серия записок #{series_id} успешно добавлена!")
        series_window.destroy()

    series_window = tk.Toplevel()
    series_window.title("Создать серию записок")

    tk.Label(series_window, text="ID серии:").pack()
    series_id_entry = tk.Entry(series_window)
    series_id_entry.pack()

    tk.Label(series_window, text="Количество записок:").pack()
    size_entry = tk.Entry(series_window)
    size_entry.pack()

    submit_button = tk.Button(series_window, text="Создать", command=handle_submit)
    submit_button.pack()

    def search_ui():
        """
        Ввод координат пользователя и поиск записок.
        """
        lat = simpledialog.askfloat("Координаты", "Введите широту (latitude):")
        lon = simpledialog.askfloat("Координаты", "Введите долготу (longitude):")
        if lat is not None and lon is not None:
            user_coords = (lat, lon)
            results = search_notes_nearby(user_coords)
            if results:
                result_str = "\n\n".join(
                    f"Записка #{note['id']}:\n"
                    f"Пользователь: {note['username']}\n"
                    f"Текст: {note['text']}\n"
                    f"Адрес: {note['address']}\n"
                    f"Ближайшее метро: {note['nearest_metro']}\n"
                    f"Расстояние: {note['distance']}\n"
                    f"Связь с серией: {note.get('series_info', 'Нет')}\n"
                    f"Ссылка на следующую: {note.get('link_address', 'Нет')}"
                    for note in results
                )
                messagebox.showinfo("Результаты поиска", result_str)
            else:
                messagebox.showinfo("Результаты поиска", "Записок рядом не найдено.")

    # Кнопки интерфейса
    generate_button = tk.Button(root, text="Создать записки", command=generate_notes_ui)
    generate_button.pack(pady=10)

    series_button = tk.Button(root, text="Создать серию записок", command=generate_series_ui)
    series_button.pack(pady=10)

    search_button = tk.Button(root, text="Поиск записок", command=search_ui)
    search_button.pack(pady=10)

    return root
