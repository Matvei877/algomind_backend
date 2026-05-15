"""Маршруты для статистики пользователя."""
from fastapi import APIRouter

from services.statistics_service import get_statistics

router = APIRouter(prefix="/stats", tags=["📈 Статистика"])


@router.get(
    "",
    summary="Статистика пользователя",
    description="Возвращает общую статистику: сколько задач решено, прогресс по темам и т.д.",
)
def stats():
    return get_statistics()
