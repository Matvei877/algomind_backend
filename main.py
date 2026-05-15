"""AlgoMind API — чистая архитектура + PostgreSQL + Auth."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import DEEPSEEK_MODEL
from config.database import init_db
from routes.problem_routes import router as problem_router
from routes.chat_routes import router as chat_router
from routes.assessment_routes import router as assessment_router
from routes.statistics_routes import router as statistics_router
from routes.auth_routes import router as auth_router
from routes.progress_routes import router as progress_router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

tags_metadata = [
    {
        "name": "📝 Задачи",
        "description": "Просмотр задач ОГЭ по информатике и проверка ответов.",
    },
    {
        "name": "🤖 AI-чат",
        "description": "Общение с ИИ-ментором на базе DeepSeek для помощи в решении задач.",
    },
    {
        "name": "📊 Оценка",
        "description": "Вступительное тестирование для оценки уровня знаний ученика.",
    },
    {
        "name": "📈 Статистика",
        "description": "Статистика прогресса пользователя по темам.",
    },
    {
        "name": "🔐 Авторизация",
        "description": "Регистрация, вход и проверка токена доступа.",
    },
]

app = FastAPI(
    title="AlgoMind API",
    description="""
    API для подготовки к ОГЭ по информатике с ИИ-ментором.

    ## Возможности

    * **Авторизация** — регистрация, вход, проверка токена
    * **Задачи** — получение списка задач ОГЭ по темам, проверка ответов
    * **AI-чат** — общение с ИИ-ментором на базе DeepSeek
    * **Оценка знаний** — вступительное тестирование по темам
    * **Статистика** — прогресс пользователя по темам

    ## Форматы

    API принимает и возвращает JSON. Аутентификация через Bearer-токен в заголовке `Authorization`.
    """,
    version="0.3.0",
    contact={
        "name": "AlgoMind Team",
        "url": "https://algomind.app",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS — разрешаем всё для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация роутов
app.include_router(problem_router)
app.include_router(chat_router)
app.include_router(assessment_router)
app.include_router(statistics_router)
app.include_router(auth_router)
app.include_router(progress_router)


@app.on_event("startup")
def on_startup():
    try:
        init_db()
        logger.info("Database connected and tables created")
    except Exception as e:
        logger.warning(f"Database not available yet: {e}")


@app.get("/")
def root():
    return {"service": "AlgoMind API", "status": "ok", "model": DEEPSEEK_MODEL}
