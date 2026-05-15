"""Подключение к локальному PostgreSQL через psycopg2."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env из корня backend/
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost:5432/algomind")


def get_connection():
    """Создать и вернуть новое подключение к БД."""
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def init_db():
    """Создать таблицы, если их нет. Ждём появления БД до 30 секунд."""
    import time
    import psycopg2
    last_err = None
    for _ in range(30):
        try:
            conn = get_connection()
            break
        except psycopg2.OperationalError as e:
            last_err = e
            time.sleep(1)
    else:
        raise last_err  # type: ignore[misc]
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            problem_id VARCHAR(50) NOT NULL,
            solved BOOLEAN DEFAULT FALSE,
            answer_text TEXT,
            solved_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, problem_id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessment_results (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            readiness VARCHAR(20),
            target_score VARCHAR(10),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.close()
    conn.close()
    logger.info("Database tables initialized successfully")
