#!/bin/bash
# slack_bot 실행 스크립트

cd "$(dirname "$0")"

# 가상환경 활성화 (프로젝트 .venv 사용)
source ../.venv/bin/activate

# 의존성 설치
pip install -r requirements.txt -q
playwright install chromium --with-deps 2>/dev/null || playwright install chromium

# ngrok 실행 (백그라운드)
echo "🌐 ngrok 시작..."
ngrok http 5000 &
NGROK_PID=$!
sleep 2

# ngrok URL 출력
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)
echo "✅ ngrok URL: $NGROK_URL"
echo ""
echo "📋 Slack App 설정에 아래 URL을 등록하세요:"
echo "  슬래시 커맨드 /QA-App-TestStart : $NGROK_URL/slack/command/start"
echo "  슬래시 커맨드 /QA-App-TestStop  : $NGROK_URL/slack/command/stop"
echo "  인터랙티브    Interactivity URL  : $NGROK_URL/slack/interactions"
echo ""

# Flask 실행
echo "🚀 Flask 서버 시작..."
python app.py

# 종료 시 ngrok도 종료
kill $NGROK_PID 2>/dev/null