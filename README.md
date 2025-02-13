# todo_plash
# ToDo Flask & Telegram Bot Project

## 📜 Описание проекта

Это проект, который состоит из **Flask API** и **Telegram-бота**, взаимодействующих друг с другом. Он использует Flask для обработки запросов и управления задачами, а Telegram-бот позволяет пользователям взаимодействовать с API через команды в Telegram. Этот проект позволяет создавать, получать, обновлять и удалять задачи, а также управлять пользователями с помощью бота.

**Технологии:**
- **Flask** — для создания RESTful API.
- **SQLAlchemy** — для взаимодействия с базой данных SQLite.
- **Aiogram** — для создания Telegram-бота.
- **Docker** — для упаковки и изоляции приложения.
- **Docker Compose** — для запуска нескольких сервисов (Flask API и Telegram-бот).

---

## ⚙️ Как работает проект?

### 🛠️ End-points

- **`/create-todo`** — для создания новой задачи.
- **`/get-todo`** — для получения задачи по ID.
- **`/get-all-todo`** — для получения всех задач.
- **`/update-todo`** — для обновления задачи по ID.
- **`/delete-todo`** — для удаления задачи.
- **`/delete-all-todo`** — для удаления всех задач.
- **`/get-users`** — для получения всех пользователей.
- **`/add-user`** — для добавления нового пользователя.
- **`/delete-user`** — для удаления пользователя.
- **`/edit-user`** — для редактирования информации пользователя.
- **`/search-domains`** — для проверки доменов (SSL, статус, доступность).

API использует **SQLite** для хранения данных о задачах и пользователях.

---

## 🛠️ Как запустить проект

### 🖥️ Установка и настройка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/mikhailyemets/todoplash.git
   cd todo_plash
2. Создайте env файл в корне проекта:
   ```bash
   BOT_TOKEN=YOUR_TG_TOKEN
   API_URL=FLASK_API_URL
   ADMIN_IDS=ADMIN_1,ADMIN_ID_2,ADMIN_ID_3
3. Создайте виртуальное окружение и установите зависимости:
   ```bash
    python -m venv .venv
    source .venv/bin/activate  # Для Linux/Mac
    .\.venv\Scripts\activate   # Для Windows
    pip install -r requirements.txt
4. Запуск через Docker Compose:
   ```bash
   docker-compose up --build
