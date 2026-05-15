"""Сохранение и чтение решённых задач пользователя."""
from config.database import get_connection


def get_solved_ids(user_id: int) -> list[str]:
    """Все problem_id, которые пользователь решил."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT problem_id FROM user_progress WHERE user_id = %s AND solved = TRUE",
            (user_id,),
        )
        return [row[0] for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


from typing import Optional


def mark_solved(user_id: int, problem_id: str, answer_text: Optional[str] = None) -> None:
    """Отметить задачу решённой. Если запись уже есть — обновить."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO user_progress (user_id, problem_id, solved, answer_text)
            VALUES (%s, %s, TRUE, %s)
            ON CONFLICT (user_id, problem_id)
            DO UPDATE SET solved = TRUE,
                          answer_text = COALESCE(EXCLUDED.answer_text, user_progress.answer_text),
                          solved_at = NOW()
            """,
            (user_id, problem_id, answer_text),
        )
    finally:
        cur.close()
        conn.close()
