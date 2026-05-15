#!/bin/bash

echo "⏳ Ждём полной очистки rate-limit (5 минут)..."
sleep 300

echo "🔄 Перезапускаю сервер..."
pkill -f "python run.py" 2>/dev/null
sleep 2

echo "🚀 Стартую новый сервер..."
python run.py &
PIDNUM=$!

sleep 5

echo ""
echo "🧪 Запускаю тесты ИИ..."
python test_ai_responses.py

echo ""
echo "Завершено!"
