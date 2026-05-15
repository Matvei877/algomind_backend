"""Запуск сервера с правильной конфигурацией для Windows."""

import uvicorn

if __name__ == "__main__":
    PORT = 8000
    print(f"\n🚀 Starting AlgoMind API on http://0.0.0.0:{PORT} (доступно с iPhone)\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info",
    )
