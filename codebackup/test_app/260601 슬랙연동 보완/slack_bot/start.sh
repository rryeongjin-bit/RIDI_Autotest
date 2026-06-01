
cd "$(dirname "$0")"


source ../.venv/bin/activate


pip install -r requirements.txt -q
playwright install chromium --with-deps 2>/dev/null || playwright install chromium


echo "🌐 ngrok 시작..."
ngrok http 5000 &
NGROK_PID=$!
sleep 2


NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)
echo "✅ ngrok URL: $NGROK_URL"
echo ""
echo "📋 Slack App 설정에 아래 URL을 등록하세요:"
echo "  슬래시 커맨드 /QA-App-TestStart : $NGROK_URL/slack/command/start"
echo "  슬래시 커맨드 /QA-App-TestStop  : $NGROK_URL/slack/command/stop"
echo "  인터랙티브    Interactivity URL  : $NGROK_URL/slack/interactions"
echo ""

echo "🚀 Flask 서버 시작..."
python app.py


kill $NGROK_PID 2>/dev/null