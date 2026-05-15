#!/bin/bash

PORT=8003

echo "=== AlgoMind API Test Suite (DeepSeek) ==="
echo ""
echo "Testing on http://127.0.0.1:$PORT"
echo ""

echo "✓ GET /"
curl -s http://127.0.0.1:$PORT/ | head -c 150
echo ""
echo ""

echo "✓ GET /problems?topic=1"
curl -s "http://127.0.0.1:$PORT/problems?topic=1" | python -m json.tool | head -20
echo ""

echo "✓ GET /problems/t3-p2"
curl -s "http://127.0.0.1:$PORT/problems/t3-p2" | python -m json.tool
echo ""

echo "✓ POST /chat (простой вопрос)"
echo "Request payload:"
cat <<EOF | tee /tmp/chat_request.json
{
  "messages": [
    {"role": "user", "content": "Привет! Скажи мне, что такое кодирование информации. Ответь одним предложением."}
  ]
}
EOF
echo ""
echo "Response:"
curl -s -X POST http://127.0.0.1:$PORT/chat \
  -H "Content-Type: application/json" \
  -d @/tmp/chat_request.json | python -m json.tool
echo ""
