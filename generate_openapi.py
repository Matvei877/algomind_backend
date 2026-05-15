"""Генератор OpenAPI схемы для AlgoMind API.

Скрипт запускает FastAPI приложение в синхронном режиме,
извлекает OpenAPI схему (OpenAPI 3.1) и сохраняет её в файл openapi.json.

Использование:
    python generate_openapi.py
"""

import json
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, если ещё не добавлен
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from main import app


def generate_openapi_json(output_path: str = "openapi.json") -> None:
    """Генерирует openapi.json схему из FastAPI приложения."""
    openapi_schema = app.openapi()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

    print(f"✅ OpenAPI схема сохранена в {output_path}")
    print(f"   Версия: {openapi_schema.get('info', {}).get('version', '?')}")
    print(f"   Эндпоинтов: {len(openapi_schema.get('paths', {}))}")
    print(f"   Компонент (схем): {len(openapi_schema.get('components', {}).get('schemas', {}))}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"
    generate_openapi_json(output)
