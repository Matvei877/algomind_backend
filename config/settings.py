"""Конфигурация и константы приложения."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- DeepSeek ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_MAX_TOKENS = 1024
DEEPSEEK_TEMPERATURE = 0.7

# --- Server ---
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# --- AI Mentor System Prompt (loaded from file) ---
_SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "data" / "system_prompt.txt"
SYSTEM_PROMPT = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
