"""Маршруты для вступительного тестирования."""
from fastapi import APIRouter

from services.assessment_service import get_topics, select_test_problems, get_entry_questions, calculate_level
from models.schemas import AssessmentSubmit

router = APIRouter(prefix="/assessment", tags=["📊 Оценка"])


@router.get(
    "/topics",
    summary="Темы ОГЭ",
    description="Возвращает список всех тем ОГЭ по информатике с эмодзи для отображения.",
)
def get_topics_endpoint():
    return get_topics()


@router.get(
    "/test-problems",
    summary="Задачи для теста",
    description="Возвращает случайные задачи для вступительного теста. Количество задаётся параметром count.",
)
def get_test_problems(count: int = 3):
    problems = select_test_problems(count)
    return {"problems": problems}


@router.get(
    "/entry-questions",
    summary="Вопросы вступительного теста",
    description="Возвращает вопросы вступительного тестирования с вариантами ответов.",
)
def get_entry_questions_endpoint():
    return get_entry_questions()


@router.post(
    "/calculate-level",
    summary="Рассчитать уровень",
    description="Принимает ответы на вступительный тест и возвращает уровень ученика с персональным роадмапом.",
)
def calculate_level_endpoint(data: AssessmentSubmit):
    answers = data.dict()
    if data.test_results:
        answers["test_results"] = data.test_results
    result = calculate_level(answers)
    return result
