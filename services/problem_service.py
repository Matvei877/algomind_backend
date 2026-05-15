"""Сервис для работы с задачами."""

import logging

from data.problems import PROBLEMS, get_problem_by_id as _get_problem_by_id

logger = logging.getLogger(__name__)


def get_all_problems() -> list:
    """Вернуть список всех задач."""
    return PROBLEMS


def get_problem_by_id(problem_id: str) -> dict | None:
    """Найти задачу по ID."""
    return _get_problem_by_id(problem_id)


def check_answer(problem_id: str, user_answer: str) -> dict:
    """Проверить ответ пользователя на задачу.

    Returns:
        dict с ключами: is_correct, correct_answer, explanation
    """
    problem = _get_problem_by_id(problem_id)
    if not problem:
        raise ValueError("Problem not found")

    is_correct = user_answer.strip().lower() == problem["answer"].strip().lower()

    return {
        "is_correct": is_correct,
        "correct_answer": problem["answer"],
        "explanation": problem["explanation"],
    }
