# AlgoMind API

API для подготовки к ОГЭ по информатике с ИИ-ментором на базе DeepSeek.

## Содержание

- [О проекте](#о-проекте)
- [Стек технологий](#стек-технологий)
- [Архитектура](#архитектура)
- [Установка и запуск](#установка-и-запуск)
- [OpenAPI / Swagger документация](#openapi--swagger-документация)
- [Эндпоинты API](#эндпоинты-api)
- [Схемы данных](#схемы-данных)
- [Структура проекта](#структура-проекта)
- [Генерация openapi.json](#генерация-openapijson)

---

## О проекте

AlgoMind API — бэкенд-сервис для платформы подготовки школьников к ОГЭ по информатике. Сервис предоставляет:

- 📝 Базу задач — 35 задач по всем 15 темам ОГЭ
- 🤖 ИИ-ментора — чат с DeepSeek AI, который помогает разбирать задачи
- 📊 Оценку знаний — вступительное тестирование и построение персонального роадмапа
- 📈 Статистику — отслеживание прогресса, слабые и сильные темы
- 🔐 Авторизацию — регистрация и вход с токен-аутентификацией

---

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Фреймворк | FastAPI 0.99 (Python 3.10+) |
| Сервер | Uvicorn |
| База данных | PostgreSQL 17 + psycopg2 |
| ИИ | DeepSeek Chat API (OpenAI-совместимый клиент) |
| Документация | OpenAPI 3.1 (Swagger UI, ReDoc) |
| Авторизация | Токен-сессии (SHA-256 хеши паролей) |

---

## Архитектура

Проект следует чистой архитектуре с строгим разделением на слои и однонаправленными зависимостями:

```
+----------------------------------------------+
|               FastAPI App                    |
|         main.py + middleware (CORS)           |
+----------------------------------------------+
|           Routes (HTTP слой)                 |
|   Только маршрутизация + Pydantic-валидация   |
|   auth / problem / chat / assessment / stats  |
+----------------------------------------------+
|          Services (бизнес-логика)             |
|   auth_service / problem_service              |
|   chat_service / assessment_service           |
|   statistics_service                          |
+----------------------------------------------+
|             Data (данные)                    |
|   Только статические данные и хранилища       |
|   problems / assessment (TOPICS) / user_stats |
+----------------------------------------------+
|      Config & Models (конфигурация)          |
|   settings / database / schemas (Pydantic)    |
+----------------------------------------------+
```

Слои и правила:

| Слой | Назначение | Импортирует |
|------|-----------|-------------|
| Routes | HTTP-обработка, валидация через Pydantic, вызов сервисов | services/, models/ |
| Services | Бизнес-логика, работа с данными | data/, config/ |
| Data | Статические данные (задачи, темы) + JSON-хранилище | нет внешних зависимостей |
| Config | Настройки, подключение к БД | внешние библиотеки |
| Models | Pydantic схемы запросов/ответов | pydantic |

Ключевые принципы:
- Routes НЕ импортируют Data напрямую — только через Services
- Services НЕ знают о HTTP (нет HTTPException)
- Data содержит только данные и простые функции поиска
- Все общение с клиентом идёт через Pydantic-модели (не dict)

---

## Установка и запуск

### Локальный запуск (без Docker)

1. Клонировать репозиторий

```bash
git clone <url>
cd backend
```

2. Создать виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Установить зависимости

```bash
pip install -r requirements.txt
```

4. Настроить .env

Создайте файл .env в корне backend/:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DATABASE_URL=postgresql://postgres@localhost:5432/algomind
```

5. Запустить сервер

```bash
python run.py
# или
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: http://localhost:8000

### Запуск через Docker Compose (рекомендуется)

Весь проект (БД + бекенд + фронтенд) запускается одной командой из корня проекта:

```bash
docker compose up --build
```

Или только бекенд с БД:

```bash
docker compose up --build db backend
```

Сервисы:

| Сервис | Порт | URL |
|--------|------|-----|
| PostgreSQL | 5432 | `postgresql://postgres:postgres@localhost:5432/algomind` |
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 3000 | http://localhost:3000 |

Переменные окружения задаются через `.env` в корне проекта:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### Структура Docker-файлов

```
docker-compose.yml          # Оркестрация: db + backend + frontend
backend/Dockerfile           # Python-образ для API
backend/.dockerignore        # Исключения для backend
frontend/Dockerfile          # Многостадийная сборка Expo + Nginx
frontend/.dockerignore       # Исключения для frontend
```

---

## OpenAPI / Swagger документация

FastAPI автоматически генерирует OpenAPI 3.1 спецификацию. Доступны три формата:

| Формат | URL | Описание |
|--------|-----|----------|
| Swagger UI | http://localhost:8000/docs | Интерактивная документация с возможностью тестировать эндпоинты |
| ReDoc | http://localhost:8000/redoc | Альтернативный читаемый интерфейс документации |
| OpenAPI JSON | http://localhost:8000/openapi.json | Сырая OpenAPI 3.1 схема в JSON |

Метаданные API

- Title: AlgoMind API
- Version: 0.3.0
- Contact: AlgoMind Team
- License: MIT
- Описание: Полное описание всех возможностей API с Markdown-форматированием

Теги (группы эндпоинтов)

| Тег | Описание |
|-----|----------|
| 📝 Задачи | Просмотр задач ОГЭ по информатике и проверка ответов |
| 🤖 AI-чат | Общение с ИИ-ментором на базе DeepSeek |
| 📊 Оценка | Вступительное тестирование для оценки уровня знаний |
| 📈 Статистика | Статистика прогресса пользователя по темам |
| 🔐 Авторизация | Регистрация, вход и проверка токена доступа |

---

## Эндпоинты API

Всего 13 эндпоинтов (плюс корневой /).

Корневой

| Метод | Путь | Описание |
|-------|------|----------|
| GET | / | Информация о сервисе |

📝 Задачи

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /problems | Список всех задач (35 задач по 15 темам) |
| GET | /problems/{problem_id} | Конкретная задача по ID (например, t1-p1) |
| POST | /check-answer | Проверить ответ пользователя на задачу |

Пример запроса /check-answer:
```json
{
  "problem_id": "t1-p1",
  "user_answer": "400"
}
```

Пример ответа:
```json
{
  "is_correct": true,
  "correct_answer": "400",
  "explanation": "1) 16 бит = 2 байта на символ...\nОтвет: 400."
}
```

🤖 AI-чат

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /chat | Отправить сообщение ИИ-ментору |

Пример запроса:
```json
{
  "messages": [
    {"role": "user", "content": "Объясни, как решать задачу про информационный объём текста"}
  ],
  "problem_id": "t1-p1"
}
```

Пример ответа:
```json
{
  "reply": "Давай разберём эту задачу по шагам...",
  "usage": {
    "prompt_tokens": 250,
    "completion_tokens": 120,
    "total_tokens": 370
  }
}
```

📊 Оценка знаний

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /assessment/topics | Все темы ОГЭ с эмодзи и описаниями |
| GET | /assessment/entry-questions | Вопросы вступительного теста |
| GET | /assessment/test-problems?count=3 | Случайные задачи для теста |
| POST | /assessment/calculate-level | Рассчитать уровень и построить роадмап |

📈 Статистика

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /stats | Статистика пользователя |

🔐 Авторизация

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /auth/register | Регистрация нового пользователя |
| POST | /auth/login | Вход пользователя |
| POST | /auth/verify | Проверка токена |

Пример запроса регистрации:
```json
{
  "username": "ivan2024",
  "password": "mysecret123"
}
```

Пример ответа:
```json
{
  "token": "a1b2c3d4e5f6...",
  "username": "ivan2024",
  "user_id": 1
}
```

---

## Схемы данных

Pydantic схемы (11 схем, отображаются в OpenAPI)

| Схема | Назначение | Поля |
|-------|-----------|------|
| AuthResponse | Ответ при авторизации | token: str, username: str, user_id: int |
| LoginRequest | Запрос входа | username: str, password: str |
| RegisterRequest | Запрос регистрации | username: str (min 3), password: str (min 4) |
| VerifyTokenRequest | Запрос проверки токена | token: str |
| ChatMessage | Сообщение в чате | role: str, content: str |
| ChatRequest | Запрос к AI-чату | messages: List[ChatMessage], problem_id: Optional[str] |
| ChatResponse | Ответ AI-чата | reply: str, usage: dict |
| CheckAnswerRequest | Запрос проверки ответа | problem_id: str, user_answer: str |
| CheckAnswerResponse | Результат проверки | is_correct: bool, explanation: str, correct_answer: str |
| RecordAttemptRequest | Запись попытки | problem_id: str, user_answer: str, is_correct: bool |
| AssessmentSubmit | Отправка результатов теста | answers: dict, test_results: Optional[dict] |

---

## Структура проекта

```
backend/
  main.py                      # Точка входа FastAPI, конфигурация, CORS
  run.py                       # Скрипт запуска сервера
  requirements.txt             # Зависимости
  generate_openapi.py          # Генератор openapi.json
  openapi.json                 # Сгенерированная OpenAPI 3.1 спецификация
  .env                         # Переменные окружения (не в git)
  Dockerfile                   # Docker-образ
  .dockerignore                # Исключения для Docker

  config/
    __init__.py
    settings.py              # Константы: DeepSeek, SYSTEM_PROMPT
    database.py              # Подключение к PostgreSQL, init_db()

  models/
    __init__.py
    schemas.py               # Pydantic модели запросов/ответов

  routes/                      # HTTP слой — только маршрутизация
    __init__.py
    auth_routes.py           # /auth/* — регистрация, логин, verify
    problem_routes.py        # /problems, /check-answer
    chat_routes.py           # /chat — ИИ-ментор
    assessment_routes.py     # /assessment/* — тестирование
    statistics_routes.py     # /stats — статистика
    progress_routes.py       # /progress — прогресс пользователя

  services/                    # Бизнес-логика
    __init__.py
    auth_service.py          # Регистрация, логин, верификация
    problem_service.py       # Все операции с задачами: список, поиск, проверка
    chat_service.py          # DeepSeek чат, build_messages
    assessment_service.py    # Расчёт уровня, роадмап, тест
    statistics_service.py    # Статистика, JSON-хранилище
    assessment_storage.py    # Хранение результатов оценки
    progress_service.py      # Сервис прогресса пользователя

  data/                        # Только данные
    __init__.py
    problems.py              # 35 задач ОГЭ + функции поиска
    assessment.py            # TOPICS + ENTRY_QUESTIONS (статич.)
    user_stats.json          # Файл с данными статистики
```

---

## Генерация openapi.json

Статический файл OpenAPI спецификации можно сгенерировать без запуска сервера:

```bash
cd backend
python generate_openapi.py
```

Это создаст файл openapi.json в корне проекта. Файл содержит полную спецификацию OpenAPI 3.1, включая:

- Все 13 эндпоинтов с параметрами и ответами
- 11 Pydantic схем (компоненты OpenAPI)
- Метаданные API (название, описание, версия, контакт)
- Теги для группировки эндпоинтов
- Описания и summary для каждого метода

Использование openapi.json

Сгенерированный файл можно использовать для:

- Генерации клиентского кода — через OpenAPI Generator, NSwag, Autorest и др.
- Импорта в Postman — создание коллекции через Import → OpenAPI
- Документирования — подключение к Swagger Editor, Stoplight и др.
- CI/CD проверок — валидация спецификации, проверка изменений

---

## Разработка

### Добавление нового эндпоинта

1. Добавьте Pydantic схемы в models/schemas.py при необходимости
2. Реализуйте бизнес-логику в services/ (без HTTP-зависимостей)
3. Создайте обработчик в routes/ — только валидация и вызов сервиса
4. Зарегистрируйте роутер в main.py
5. Перегенерируйте openapi.json: python generate_openapi.py

### Правила чистой архитектуры

- Routes не импортируют data/ напрямую, только через services/
- Services не имеют HTTP-зависимостей (нет HTTPException, Request)
- Data содержит только статические данные и простые функции-геттеры
- Models — Pydantic BaseModel с Field-описаниями для OpenAPI

### Формат задачи

Каждая задача в data/problems.py имеет структуру:

```python
{
    "id": "t1-p1",         # Уникальный ID
    "topic": 1,            # Номер темы ОГЭ (1-15)
    "oge_number": 1,       # Номер задания в ОГЭ
    "statement": "...",    # Условие задачи
    "answer": "400",       # Правильный ответ (строка)
    "explanation": "...",  # Разбор решения
}
```

---

## Лицензия

MIT
