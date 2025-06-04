from Cordsold.database_ import initialize_database
from ui import create_ui

def main():
    """
    Точка входа в приложение. Инициализирует базу данных и запускает пользовательский интерфейс.
    """
    # Инициализация базы данных
    initialize_database()

    # Создание пользовательского интерфейса
    root = create_ui()
    root.mainloop()

if __name__ == "__main__":
    main()
