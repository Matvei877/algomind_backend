"""Регистрация и авторизация пользователей."""
from fastapi import APIRouter, HTTPException

from models.schemas import RegisterRequest, LoginRequest, AuthResponse, VerifyTokenRequest
from services.auth_service import register_user, login_user, verify_token

router = APIRouter(prefix="/auth", tags=["🔐 Авторизация"])


@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя с указанным именем и паролем. Возвращает токен для авторизации.",
    response_model=AuthResponse,
)
def register(req: RegisterRequest):
    try:
        result = register_user(req.username, req.password)
        return AuthResponse(**result)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post(
    "/login",
    summary="Вход пользователя",
    description="Авторизует пользователя по имени и паролю. Возвращает токен для дальнейших запросов.",
    response_model=AuthResponse,
)
def login(req: LoginRequest):
    try:
        result = login_user(req.username, req.password)
        return AuthResponse(**result)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post(
    "/verify",
    summary="Проверка токена",
    description="Проверяет, действителен ли переданный токен. Возвращает информацию о пользователе.",
)
def verify(req: VerifyTokenRequest):
    try:
        return verify_token(req.token)
    except ValueError as e:
        raise HTTPException(401, str(e))
