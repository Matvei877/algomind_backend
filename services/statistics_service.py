"""Сервис статистики по задачам.

Хранит и анализирует результаты решений пользователя:
- Какие задачи решены правильно/неправильно
- Статистика по темам
- Прогресс во времени
"""

import json
import os
import time
from collections import defaultdict

from data.problems import get_problem_by_id
from data.assessment import TOPICS

STATS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_stats.json")


def _load_stats() -> dict:
    """Загрузить статистику из файла."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"attempts": [], "sessions": []}
    return {"attempts": [], "sessions": []}


def _save_stats(stats: dict):
    """Сохранить статистику в файл."""
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_attempt(problem_id: str, user_answer: str, is_correct: bool):
    """Записать попытку решения задачи."""
    stats = _load_stats()

    attempt = {
        "problem_id": problem_id,
        "user_answer": user_answer,
        "is_correct": is_correct,
        "timestamp": time.time(),
    }
    stats["attempts"].append(attempt)
    _save_stats(stats)


def start_session() -> str:
    """Начать новую сессию обучения. Возвращает ID сессии."""
    stats = _load_stats()
    session_id = f"session_{int(time.time())}"
    stats["sessions"].append({
        "id": session_id,
        "start_time": time.time(),
        "end_time": None,
        "problems_attempted": 0,
        "correct": 0,
    })
    _save_stats(stats)
    return session_id


def end_session(session_id: str):
    """Завершить сессию обучения."""
    stats = _load_stats()
    for session in stats["sessions"]:
        if session["id"] == session_id:
            session["end_time"] = time.time()
            session_start = session["start_time"]
            session_attempts = [
                a for a in stats["attempts"]
                if a["timestamp"] >= session_start
            ]
            session["problems_attempted"] = len(session_attempts)
            session["correct"] = sum(1 for a in session_attempts if a["is_correct"])
            break
    _save_stats(stats)


def get_statistics() -> dict:
    """Получить полную статистику по задачам."""
    stats = _load_stats()
    attempts = stats.get("attempts", [])

    if not attempts:
        return {
            "total_attempts": 0,
            "total_correct": 0,
            "total_wrong": 0,
            "accuracy": 0,
            "by_topic": {},
            "by_problem": {},
            "recent_attempts": [],
            "weak_topics": [],
            "strong_topics": [],
        }

    total = len(attempts)
    correct = sum(1 for a in attempts if a["is_correct"])
    wrong = total - correct
    accuracy = round(correct / total * 100, 1) if total > 0 else 0

    # Статистика по темам
    by_topic = defaultdict(lambda: {"attempts": 0, "correct": 0, "wrong": 0})
    by_problem = defaultdict(lambda: {"attempts": 0, "correct": 0, "wrong": 0})

    for a in attempts:
        problem = get_problem_by_id(a["problem_id"])
        topic_id = problem["topic"] if problem else 0

        by_topic[topic_id]["attempts"] += 1
        by_topic[topic_id]["correct"] += 1 if a["is_correct"] else 0
        by_topic[topic_id]["wrong"] += 0 if a["is_correct"] else 1

        by_problem[a["problem_id"]]["attempts"] += 1
        by_problem[a["problem_id"]]["correct"] += 1 if a["is_correct"] else 0
        by_problem[a["problem_id"]]["wrong"] += 0 if a["is_correct"] else 1

    # Форматируем по темам
    by_topic_formatted = {}
    for topic_id, data in by_topic.items():
        topic_info = TOPICS.get(topic_id, {"name": f"Тема {topic_id}", "emoji": "📚"})
        topic_accuracy = round(data["correct"] / data["attempts"] * 100, 1) if data["attempts"] > 0 else 0
        by_topic_formatted[str(topic_id)] = {
            "name": topic_info["name"],
            "emoji": topic_info["emoji"],
            "attempts": data["attempts"],
            "correct": data["correct"],
            "wrong": data["wrong"],
            "accuracy": topic_accuracy,
        }

    # Форматируем по задачам
    by_problem_formatted = {}
    for prob_id, data in by_problem.items():
        problem = get_problem_by_id(prob_id)
        prob_accuracy = round(data["correct"] / data["attempts"] * 100, 1) if data["attempts"] > 0 else 0
        by_problem_formatted[prob_id] = {
            "topic": problem["topic"] if problem else 0,
            "attempts": data["attempts"],
            "correct": data["correct"],
            "wrong": data["wrong"],
            "accuracy": prob_accuracy,
        }

    # Определяем слабые и сильные темы
    weak_topics = []
    strong_topics = []
    for topic_id, data in by_topic_formatted.items():
        if data["accuracy"] < 50 and data["attempts"] >= 2:
            weak_topics.append({"topic_id": int(topic_id), **data})
        elif data["accuracy"] >= 80 and data["attempts"] >= 2:
            strong_topics.append({"topic_id": int(topic_id), **data})

    weak_topics.sort(key=lambda x: x["accuracy"])
    strong_topics.sort(key=lambda x: -x["accuracy"])

    # Последние 10 попыток
    recent = sorted(attempts, key=lambda x: x["timestamp"], reverse=True)[:10]
    recent_attempts = []
    for a in recent:
        problem = get_problem_by_id(a["problem_id"])
        recent_attempts.append({
            "problem_id": a["problem_id"],
            "topic": problem["topic"] if problem else 0,
            "is_correct": a["is_correct"],
            "time": time.strftime("%d.%m %H:%M", time.localtime(a["timestamp"])),
        })

    return {
        "total_attempts": total,
        "total_correct": correct,
        "total_wrong": wrong,
        "accuracy": accuracy,
        "by_topic": by_topic_formatted,
        "by_problem": by_problem_formatted,
        "recent_attempts": recent_attempts,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
    }


def clear_statistics():
    """Очистить всю статистику."""
    _save_stats({"attempts": [], "sessions": []})
