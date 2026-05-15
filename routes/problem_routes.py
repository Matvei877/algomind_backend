"""Маршруты для работы с задачами ОГЭ."""
from fastapi import APIRouter, HTTPException

from services.problem_service import get_all_problems, get_problem_by_id, check_answer
from models.schemas import CheckAnswerRequest, CheckAnswerResponse

router = APIRouter(tags=["📝 Задачи"])


@router.get(
    "/problems",
    summary="Все задачи",
    description="Возвращает список всех задач ОГЭ по информатике сгруппированных по темам.",
)
def list_problems():
    problems = get_all_problems()
    return {"problems": problems, "count": len(problems)}


@router.get(
    "/problems/{problem_id}",
    summary="Задача по ID",
    description="Возвращает конкретную задачу по её идентификатору (например, t1-p1).",
)
def get_problem(problem_id: str):
    problem = get_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(404, "Задача не найдена")
    return problem


@router.post(
    "/check-answer",
    summary="Проверить ответ",
    description="Проверяет ответ пользователя на задачу. Сравнивает с правильным ответом и возвращает результат с объяснением.",
    response_model=CheckAnswerResponse,
)
def check_answer_endpoint(req: CheckAnswerRequest):
    try:
        result = check_answer(req.problem_id, req.user_answer)
        return CheckAnswerResponse(**result)
    except ValueError as e:
        raise HTTPException(404, str(e))
