"""Маршруты для ИИ-чата с DeepSeek."""
from fastapi import APIRouter, HTTPException

from services.chat_service import get_chat_response
from models.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["🤖 AI-чат"])


@router.post(
    "",
    summary="Отправить сообщение в чат",
    description="Отправляет сообщение ИИ-помощнику на базе DeepSeek. Может объяснить решение задачи или ответить на вопросы.",
)
def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(400, "Сообщение не может быть пустым")

    messages_dicts = [m.dict() for m in req.messages]
    response = get_chat_response(messages_dicts, req.problem_id)
    return response
