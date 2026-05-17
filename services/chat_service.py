"""Сервис для работы с DeepSeek AI чатом."""

import json
import logging
from pathlib import Path

from openai import OpenAI

from config.settings import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    DEEPSEEK_MAX_TOKENS,
    DEEPSEEK_TEMPERATURE,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

_PROBLEMS_PATH = Path(__file__).resolve().parent.parent / "data" / "problems.json"
_PROBLEMS = json.loads(_PROBLEMS_PATH.read_text(encoding="utf-8"))


def _get_problem_by_id(problem_id: str) -> dict | None:
    for p in _PROBLEMS:
        if p["id"] == problem_id:
            return p
    return None


def _build_client() -> OpenAI | None:
    """Создать клиент DeepSeek, если есть ключ."""
    if not DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY не задан")
        return None
    return OpenAI(
        base_url=DEEPSEEK_BASE_URL,
        api_key=DEEPSEEK_API_KEY,
        max_retries=0,
    )


def build_messages(problem_id: str | None, messages: list[dict]) -> list[dict]:
    """Собрать список сообщений для DeepSeek с системным промптом."""
    system_text = SYSTEM_PROMPT

    if problem_id:
        problem = _get_problem_by_id(problem_id)
        if problem:
            system_text += (
                f"\n\nКонтекст задачи (задание ОГЭ №{problem['topic']}):\n"
                f"Условие: {problem['statement']}\n"
                f"Правильный ответ: {problem['answer']}\n"
                f"Эталонный разбор:\n{problem['explanation']}\n\n"
                "Используй этот контекст, чтобы помочь ученику разобраться. "
                "Не выдавай готовый ответ сразу — наводи на решение."
            )

    api_messages = [{"role": "system", "content": system_text}]
    api_messages.extend(messages)
    return api_messages


def send_chat(messages: list[dict]) -> tuple[str, dict]:
    """Отправить запрос в DeepSeek и получить ответ."""
    client = _build_client()
    if not client:
        raise RuntimeError("DEEPSEEK_API_KEY не настроен")

    if not messages:
        raise ValueError("messages пуст")

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            max_tokens=DEEPSEEK_MAX_TOKENS,
            temperature=DEEPSEEK_TEMPERATURE,
        )
    except Exception as e:
        error_msg = str(e)
        status_code = 502
        if "429" in error_msg:
            status_code = 429
            error_msg = "DeepSeek API rate-limited. Повтори позже."
        logger.error(f"DeepSeek error: {type(e).__name__}: {e}", exc_info=True)
        raise RuntimeError(error_msg, status_code)

    reply_text = response.choices[0].message.content or ""

    usage = {}
    if response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    return reply_text, usage


def get_chat_response(messages: list[dict], problem_id: str | None = None) -> dict:
    """Получить ответ от ИИ с учётом контекста задачи.

    Args:
        messages: История сообщений.
        problem_id: ID задачи (если чат в контексте задачи).

    Returns:
        dict с ключами reply и usage.
    """
    api_messages = build_messages(problem_id, messages)
    reply_text, usage = send_chat(api_messages)
    return {"reply": reply_text, "usage": usage}
