"""Сервис авторизации пользователей."""
import hashlib
import secrets
from datetime import datetime, timedelta

from config.database import get_connection

# Простая JWT-подобная система (без внешних зависимостей)
# В production использовать python-jose / PyJWT
TOKENS: dict[str, dict] = {}  # token -> {user_id, username, expires}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_hex(32)


def get_user_from_token(token: str) -> dict | None:
    """Получить данные пользователя по токену."""
    data = TOKENS.get(token)
    if not data:
        return None
    if data["expires"] < datetime.now():
        del TOKENS[token]
        return None
    return data


def register_user(username: str, password: str) -> dict:
    """Зарегистрировать нового пользователя.

    Returns:
        dict с ключами token, username, user_id

    Raises:
        ValueError: если пользователь уже существует или некорректные данные.
    """
    if len(username) < 3:
        raise ValueError("Имя пользователя должно быть минимум 3 символа")
    if len(password) < 4:
        raise ValueError("Пароль должен быть минимум 4 символа")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            raise ValueError("Пользователь уже существует")

        pwd_hash = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
            (username, pwd_hash),
        )
        user_id = cur.fetchone()[0]

        token = generate_token()
        TOKENS[token] = {
            "user_id": user_id,
            "username": username,
            "expires": datetime.now() + timedelta(days=30),
        }

        return {"token": token, "username": username, "user_id": user_id}
    finally:
        cur.close()
        conn.close()


def login_user(username: str, password: str) -> dict:
    """Авторизовать пользователя.

    Returns:
        dict с ключами token, username, user_id

    Raises:
        ValueError: если неверное имя или пароль.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("Неверное имя пользователя или пароль")

        user_id, db_username, pwd_hash = row
        if hash_password(password) != pwd_hash:
            raise ValueError("Неверное имя пользователя или пароль")

        token = generate_token()
        TOKENS[token] = {
            "user_id": user_id,
            "username": db_username,
            "expires": datetime.now() + timedelta(days=30),
        }

        return {"token": token, "username": db_username, "user_id": user_id}
    finally:
        cur.close()
        conn.close()


def verify_token(token: str) -> dict:
    """Проверить действительность токена.

    Returns:
        dict с ключами valid, user_id, username

    Raises:
        ValueError: если токен недействителен.
    """
    user = get_user_from_token(token)
    if not user:
        raise ValueError("Недействительный токен")
    return {"valid": True, "user_id": user["user_id"], "username": user["username"]}
