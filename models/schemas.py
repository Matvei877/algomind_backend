"""Pydantic схемы запросов и ответов API."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# === Авторизация ===

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, description="Имя пользователя (минимум 3 символа)")
    password: str = Field(..., min_length=4, description="Пароль (минимум 4 символа)")


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    username: str
    user_id: int


class VerifyTokenRequest(BaseModel):
    token: str = Field(..., description="Токен для проверки")


# === Чат ===

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' или 'assistant'")
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    problem_id: Optional[str] = Field(
        None, description="ID задачи, если чат идёт в контексте задачи"
    )


class ChatResponse(BaseModel):
    reply: str
    usage: dict


# === Задачи ===

class CheckAnswerRequest(BaseModel):
    problem_id: str
    user_answer: str


class CheckAnswerResponse(BaseModel):
    is_correct: bool
    explanation: str
    correct_answer: str


class RecordAttemptRequest(BaseModel):
    problem_id: str
    user_answer: str
    is_correct: bool


# === Оценка ===

class AssessmentSubmit(BaseModel):
    answers: dict = Field(..., description="Ответы на вступительный тест")
    test_results: Optional[dict] = Field(
        None, description="Результаты тестовых задач: {problem_id: {correct: bool}}"
    )
