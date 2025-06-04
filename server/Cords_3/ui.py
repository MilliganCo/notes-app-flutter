import tkinter as tk
from tkinter import messagebox, simpledialog
from database import login_user, save_found_note_to_user, get_user_notes, clear_database, insert_notes, insert_series
from search import search_notes_nearby
from utils import generate_random_notes, generate_series, enrich_notes_with_geodata

# Глобальные переменные для текущего пользователя
current_user = None
user_id = None


def create_ui():
    """
    Создание основного интерфейса.
    """
    global current_user, user_id

    root = tk.Tk()
    root.title("Notes App")

    def handle_login():
        global current_user, user_id
        username = simpledialog.askstring("Логин", "Введите имя пользователя:")
        if username:
            current_user = username
            user_id = login_user(username)
            messagebox.showinfo("Логин", f"Вы вошли как {current_user}")

    def handle_logout():
        global current_user, user_id
        current_user = None
        user_id = None
        messagebox.showinfo("Выход", "Вы вышли из учётной записи")

    def show_user_notes():
        if user_id:
            notes = get_user_notes(user_id)
            if notes:
                result_str = "\n\n".join(
                    f"Записка #{note[0]}:\n"
                    f"Пользователь: {note[1]}\n"
                    f"Текст: {note[2]}\n"
                    f"Адрес: {note[5]}\n"
                    f"Ближайшее метро: {note[6]}"
                    for note in notes
                )
                messagebox.showinfo("Ваши записи", result_str)
            else:
                messagebox.showinfo("Ваши записи", "Нет сохранённых записок.")
        else:
            messagebox.showerror("Ошибка", "Войдите в систему, чтобы увидеть ваши записки.")

    def search_ui():
        global user_id
        lat = simpledialog.askfloat("Координаты", "Введите широту (latitude):")
        lon = simpledialog.askfloat("Координаты", "Введите долготу (longitude):")
        if lat is not None and lon is not None:
            user_coords = (lat, lon)
            results = search_notes_nearby(user_coords, user_id)
            if results:
                for note in results:
                    result_str = (
                        f"Записка #{note['id']}:\n"
                        f"Пользователь: {note['username']}\n"
                        f"Текст: {note['text']}\n"
                        f"Адрес: {note['address']}\n"
                        f"Ближайшее метро: {note['nearest_metro']}\n"
                        f"Расстояние: {note['distance']}\n"
                        f"Связь с серией: {note.get('series_info', 'Нет')}\n"
                        f"Ссылка на следующую: {note.get('link_address', 'Нет')}"
                    )
                    messagebox.showinfo("Результаты поиска", result_str)
                    if current_user:
                        save = messagebox.askyesno("Сохранить?", "Сохранить эту записку?")
                        if save:
                            save_found_note_to_user(user_id, note['id'])
                            messagebox.showinfo("Сохранение", "Записка сохранена.")
            else:
                messagebox.showinfo("Результаты поиска", "Записок рядом не найдено.")

    def generate_notes_ui():
        """
        Генерация случайных записок.
        """
        count = simpledialog.askinteger("Генерация записок", "Сколько записок создать?", minvalue=1, maxvalue=100)
        if count:
            notes = generate_random_notes(count)
            insert_notes(notes)
            messagebox.showinfo("Генерация", f"{count} записок успешно создано.")

    def generate_series_ui():
        """
        Генерация серии записок.
        """
        series_id = simpledialog.askinteger("Серия ID", "Введите ID для серии:")
        size = simpledialog.askinteger("Размер серии", "Введите количество записок в серии:", minvalue=2, maxvalue=10)
        if series_id and size:
            series = generate_series(series_id, size)
            insert_series(series)
            messagebox.showinfo("Серии", f"Серия {series_id} из {size} записок успешно создана.")

    def clear_database_ui():
        """
        Очистка базы данных.
        """
        confirm = messagebox.askyesno("Очистка базы", "Вы уверены, что хотите удалить все данные?")
        if confirm:
            clear_database()
            messagebox.showinfo("Очистка базы", "База данных успешно очищена.")

    # Кнопки интерфейса
    login_button = tk.Button(root, text="Login", command=handle_login)
    login_button.pack(pady=5)

    logout_button = tk.Button(root, text="Logout", command=handle_logout)
    logout_button.pack(pady=5)

    notes_button = tk.Button(root, text="Найденные записки", command=show_user_notes)
    notes_button.pack(pady=5)

    search_button = tk.Button(root, text="Поиск записок", command=search_ui)
    search_button.pack(pady=10)

    generate_button = tk.Button(root, text="Создать записки", command=generate_notes_ui)
    generate_button.pack(pady=5)

    series_button = tk.Button(root, text="Создать серию записок", command=generate_series_ui)
    series_button.pack(pady=5)

    clear_button = tk.Button(root, text="Очистить базу", command=clear_database_ui)
    clear_button.pack(pady=5)

    return root
