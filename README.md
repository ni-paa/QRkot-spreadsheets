# QRKot — Благотворительный фонд поддержки котиков

## Описание

QRKot — это backend-приложение для благотворительного фонда, которое позволяет:

- Создавать целевые проекты (например, «Котику Мурзику на лечение»).
- Принимать пожертвования от пользователей.
- Автоматически распределять поступившие средства между открытыми проектами (инвестирование «по старшинству»).
- Формировать отчёты в Google Sheets о закрытых проектах, отсортированных по скорости сбора средств.

Проект решает задачу прозрачного сбора и распределения средств, помогает администраторам отслеживать статус проектов, а пользователям — делать пожертвования и видеть их историю.

### Основные возможности

- Регистрация и аутентификация пользователей (JWT, FastAPI Users).
- CRUD для целевых проектов (только суперпользователь).
- Создание пожертвований любым авторизованным пользователем.
- Автоматическое инвестирование: новые пожертвования идут в самый старый открытый проект, пока он не закроется.
- Формирование отчёта в Google Sheets: список закрытых проектов с временем сбора средств.
- Асинхронная работа (SQLAlchemy 2.0, aiosqlite).

## Технологии

- **FastAPI** — веб-фреймворк.
- **SQLAlchemy 2.0** (asyncio) — ORM.
- **Alembic** — миграции базы данных.
- **FastAPI Users** — управление пользователями и JWT-аутентификация.
- **Aiogoogle** — асинхронный клиент Google API.
- **Pydantic** — валидация данных.
- **SQLite + aiosqlite** (для локальной разработки; легко заменяется на PostgreSQL).
- **Pytest** — тестирование.

## Установка и запуск на локальной машине

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-repo/QRKot-spreadsheets.git
cd QRKot-spreadsheets
```
### 2. Создать виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```
### 3. Установить зависимости

```bash
pip install -r requirements.txt
```
### 4. Настроить переменные окружения
Создайте в корне проекта файл .env со следующим содержимым:

```ini
# Общие настройки
PROJECT_NAME=QRKot
DATABASE_URL=sqlite+aiosqlite:///./fastapi.db
SECRET=ваш_секретный_ключ

# Google API (сервисный аккаунт)
TYPE=service_account
PROJECT_ID=ваш_project_id
PRIVATE_KEY_ID=...
PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
CLIENT_EMAIL=...@...gserviceaccount.com
CLIENT_ID=...
AUTH_URI=https://accounts.google.com/o/oauth2/auth
TOKEN_URI=https://oauth2.googleapis.com/token
AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
CLIENT_X509_CERT_URL=...
# Ваш личный email (для прав на таблицу)
EMAIL=ваша_почта@gmail.com
```
### 5. Применить миграции
```bash
alembic upgrade head
```
### 6. Запустить сервер
```bash
uvicorn app.main:app --reload
Сервер будет доступен по адресу http://localhost:8000.
Документация API (Swagger) — http://localhost:8000/docs.
```
## Примеры запросов к API
Регистрация пользователя
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "strongpassword"
}
```
Ответ (201 Created):

```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```
## Получение JWT-токена
```http
POST /auth/jwt/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=strongpassword
```
#### Ответ:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
### Далее во всех запросах для авторизованных пользователей добавляйте заголовок:
```text
Authorization: Bearer <access_token>
```
### Создание целевого проекта (только суперпользователь)
```http
POST /charity_project/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Лечение кота Мурзика",
  "description": "Сбор на операцию",
  "full_amount": 50000
}
```
#### Ответ (200 OK):
```json
{
  "id": 1,
  "name": "Лечение кота Мурзика",
  "description": "Сбор на операцию",
  "full_amount": 50000,
  "invested_amount": 0,
  "fully_invested": false,
  "create_date": "2025-04-23T10:00:00"
}
```
### Создание пожертвования
```http
POST /donation/
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_amount": 1000,
  "comment": "На здоровье котику"
}
```
#### Ответ (200 OK, поле comment отсутствует, если не указано):
```json
{
  "id": 1,
  "full_amount": 1000,
  "create_date": "2025-04-23T10:05:00"
}
```
### Получение списка своих пожертвований
```http
GET /donation/my
Authorization: Bearer <token>
```
#### Ответ:
```json
[
  {
    "id": 1,
    "full_amount": 1000,
    "comment": "На здоровье котику",
    "create_date": "2025-04-23T10:05:00"
  }
]
```
### Формирование отчёта в Google Sheets (только суперпользователь)
```http
GET /google/
Authorization: Bearer <token>
```
#### Ответ:
```json
{
  "message": "Отчёт создан",
  "url": "https://docs.google.com/spreadsheets/d/1AbC..."
}
```
После этого по ссылке будет доступна таблица с закрытыми проектами, отсортированными по времени сбора (от самого быстрого к самому долгому).

### Получение всех проектов (доступно без авторизации)
```http
GET /charity_project/
```
Ответ — список всех проектов.

### Структура проекта
```text
QRKot-spreadsheets/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── charity_project.py
│   │   │   ├── donation.py
│   │   │   └── google.py
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── google_client.py
│   │   ├── user.py
│   │   └── user_manager.py
│   ├── crud/
│   │   └── base.py
│   ├── models/
│   │   ├── base.py
│   │   ├── charity_project.py
│   │   ├── donation.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── charity_project.py
│   │   ├── donation.py
│   │   └── user.py
│   ├── services/
│   │   ├── charity_project.py
│   │   └── google.py
│   └── main.py
├── alembic/
│   └── versions/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```
### Тестирование
Для запуска тестов (требуется установленный pytest и все зависимости):
```bash
pytest -v
```
