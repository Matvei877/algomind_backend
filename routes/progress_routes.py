"""Маршруты для сохранения и чтения прогресса пользователя."""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from services.auth_service import get_user_from_token
from services.progress_service import get_solved_ids, mark_solved
from services.assessment_storage import save_assessment, get_latest_assessment

router = APIRouter(prefix="/progress", tags=["📈 Статистика"])


class SolvedRequest(BaseModel):
    problem_id: str
    answer_text: Optional[str] = None


class AssessmentSaveRequest(BaseModel):
    readiness: str
    target_score: str


def _user_id_from_header(authorization: Optional[str]) -> int:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Требуется Bearer-токен в заголовке Authorization")
    token = authorization.split(" ", 1)[1].strip()
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Недействительный или просроченный токен")
    return user["user_id"]


@router.get(
    "",
    summary="Решённые задачи",
    description="Возвращает массив id всех задач, решённых текущим пользователем.",
)
def list_progress(authorization: Optional[str] = Header(default=None)):
    user_id = _user_id_from_header(authorization)
    return {"solved_ids": get_solved_ids(user_id)}


@router.post(
    "",
    summary="Отметить задачу решённой",
    description="Сохраняет факт правильного решения задачи в БД для текущего пользователя.",
)
def save_progress(req: SolvedRequest, authorization: Optional[str] = Header(default=None)):
    user_id = _user_id_from_header(authorization)
    mark_solved(user_id, req.problem_id, req.answer_text)
    return {"ok": True}


@router.get(
    "/assessment",
    summary="Последний результат вступительного теста",
    description="Возвращает {readiness, target_score} последнего пройденного теста или null.",
)
def get_assessment(authorization: Optional[str] = Header(default=None)):
    user_id = _user_id_from_header(authorization)
    return {"assessment": get_latest_assessment(user_id)}


@router.post(
    "/assessment",
    summary="Сохранить результат вступительного теста",
    description="Сохраняет ответы пользователя на вступительный тест (готовность и цель).",
)
def post_assessment(req: AssessmentSaveRequest, authorization: Optional[str] = Header(default=None)):
    user_id = _user_id_from_header(authorization)
    save_assessment(user_id, req.readiness, req.target_score)
    return {"ok": True}
