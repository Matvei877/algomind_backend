"""Сохранение и чтение результатов вступительного теста."""
from typing import Optional
from config.database import get_connection


def save_assessment(user_id: int, readiness: str, target_score: str) -> None:
    """Сохранить ответы пользователя на вступительный тест.

    Каждый раз пишем новую запись — последняя считается актуальной.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO assessment_results (user_id, readiness, target_score) VALUES (%s, %s, %s)",
            (user_id, readiness, target_score),
        )
    finally:
        cur.close()
        conn.close()


def get_latest_assessment(user_id: int) -> Optional[dict]:
    """Последний результат теста пользователя или None."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT readiness, target_score
            FROM assessment_results
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"readiness": row[0], "target_score": row[1]}
    finally:
        cur.close()
        conn.close()
