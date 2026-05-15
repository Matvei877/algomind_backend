"""Сервис вступительного тестирования и построения роадмапа.

Определяет уровень ученика на основе:
1. Целевого балла ОГЭ
2. Самооценки по темам
3. Результатов решения случайных задач
"""

import random
from data.assessment import TOPICS, ENTRY_QUESTIONS
from data.problems import get_all_problems


def get_topics() -> dict:
    """Вернуть все темы ОГЭ."""
    return {"topics": TOPICS}


def get_entry_questions() -> dict:
    """Вернуть вопросы вступительного теста."""
    return {"questions": ENTRY_QUESTIONS, "topics": TOPICS}


def select_test_problems(count: int = 3) -> list:
    """Выбрать ровно `count` случайных задач из разных тем (по одной из темы)."""
    all_problems = get_all_problems()
    if len(all_problems) <= count:
        return all_problems

    # Группируем задачи по темам
    by_topic = {}
    for p in all_problems:
        by_topic.setdefault(p["topic"], []).append(p)

    # Перемешиваем темы и выбираем по одной задаче из каждой
    topics = list(by_topic.keys())
    random.shuffle(topics)

    selected = []
    for topic in topics:
        if len(selected) >= count:
            break
        chosen = random.choice(by_topic[topic])
        selected.append(chosen)

    random.shuffle(selected)
    return selected


def calculate_level(answers: dict) -> dict:
    """Рассчитать уровень ученика на основе ответов вступительного теста.

    Параметры:
        answers: словарь с ответами пользователя
            {
                "target_score": "4",
                "difficult_topics": ["1", "5", "9"],
                "test_results": {
                    "t1-p1": {"correct": True},
                    "t2-p2": {"correct": False},
                    ...
                }
            }

    Возвращает:
        словарь с уровнем и рекомендациями
    """
    target_score = int(answers.get("target_score", "3"))

    # Трудные темы (отмеченные пользователем)
    difficult_topics = answers.get("difficult_topics", [])

    # Оценка самооценки по темам
    topic_ratings = {}
    for topic_id in TOPICS:
        # Если тема отмечена как трудная — ставим "hard", иначе "easy"
        if str(topic_id) in difficult_topics:
            topic_ratings[topic_id] = "hard"
        else:
            topic_ratings[topic_id] = "easy"

    # Оценка результатов тестовых задач
    test_results = answers.get("test_results", {})
    correct_count = sum(1 for v in test_results.values() if v.get("correct"))
    total_tests = len(test_results) if test_results else 1
    test_score_pct = correct_count / total_tests

    # Определяем общий уровень
    hard_topics = sum(1 for r in topic_ratings.values() if r == "hard")

    if test_score_pct >= 0.8 and hard_topics == 0 and target_score >= 4:
        overall_level = "advanced"
    elif test_score_pct >= 0.5 and hard_topics <= 1:
        overall_level = "intermediate"
    else:
        overall_level = "beginner"

    # Строим роадмап
    roadmap = _build_roadmap(overall_level, target_score, topic_ratings)

    return {
        "level": overall_level,
        "target_score": target_score,
        "difficult_topics": difficult_topics,
        "topic_ratings": topic_ratings,
        "test_score": {
            "correct": correct_count,
            "total": total_tests,
            "percentage": round(test_score_pct * 100),
        },
        "roadmap": roadmap,
    }


def _build_roadmap(
    level: str,
    target_score: int,
    topic_ratings: dict,
) -> list:
    """Построить персональный роадмап обучения."""
    roadmap = []

    # Определяем приоритеты тем (сначала сложные)
    topic_priority = sorted(
        TOPICS.keys(),
        key=lambda t: {"hard": 0, "medium": 1, "easy": 2}.get(topic_ratings.get(t, "medium")),
    )

    # Базовая рекомендация в зависимости от уровня
    if level == "beginner":
        roadmap.append({
            "step": 1,
            "type": "foundation",
            "title": "🔤 Изучи основы",
            "description": "Начни с базовых понятий: бит, байт, кодирование, логические операции.",
            "topics": list(topic_priority[:2]),
            "estimated_lessons": 3,
        })
    elif level == "intermediate":
        roadmap.append({
            "step": 1,
            "type": "practice",
            "title": "📚 Закрепи знания",
            "description": "Прорешай задачи по темам, в которых чувствуешь неуверенность.",
            "topics": [t for t in topic_priority if topic_ratings.get(t) in ("hard", "medium")],
            "estimated_lessons": 2,
        })
    else:  # advanced
        roadmap.append({
            "step": 1,
            "type": "mastery",
            "title": "🏆 Доведи до совершенства",
            "description": "Решай задачи повышенной сложности, разбирай олимпиадные приёмы.",
            "topics": list(TOPICS.keys()),
            "estimated_lessons": 1,
        })

    # Пошаговый план по темам
    for i, topic_id in enumerate(topic_priority, start=2):
        topic = TOPICS[topic_id]
        rating = topic_ratings.get(topic_id, "medium")

        if rating == "hard":
            description = f"Подробно разбери тему «{topic['name']}» с нуля. Реши минимум 5 задач."
        elif rating == "medium":
            description = f"Повтори тему «{topic['name']}» и прорешай 3-4 задачи для закрепления."
        else:
            description = f"Проверь себя по теме «{topic['name']}» — реши 1-2 задачи для уверенности."

        roadmap.append({
            "step": i,
            "type": "topic",
            "topic_id": topic_id,
            "title": f"{topic['emoji']} {topic['name']}",
            "description": description,
            "difficulty": rating,
        })

    # Финальный этап — подготовка к экзамену
    roadmap.append({
        "step": len(topic_priority) + 2,
        "type": "final",
        "title": "🎯 Финальная подготовка",
        "description": (
            f"Реши полный пробный вариант ОГЭ. "
            f"При target-балле {target_score} удели внимание заданиям с развёрнутым ответом."
        ),
        "estimated_lessons": 2,
    })

    return roadmap
