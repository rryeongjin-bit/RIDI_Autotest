

HOST="127.0.0.1"

# 포트 정의 
AOS_REAL_PORT=4725
IOS_SIMULATOR_PORT=4727
IOS_REAL_PORT=4729

# 서버 종료
stop_servers() {
    echo "\n🛑 Appium 서버 전체 종료 중..."
    for PORT in $AOS_EMULATOR_PORT $AOS_REAL_PORT $IOS_SIMULATOR_PORT $IOS_REAL_PORT; do
        PID=$(lsof -ti :$PORT)
        if [ -n "$PID" ]; then
            kill -9 $PID
            echo "  ✅ 포트 $PORT 종료 완료 (PID: $PID)"
        else
            echo "  ⚪ 포트 $PORT 실행 중이지 않음"
        fi
    done
    echo "🛑 Appium 서버 종료 완료"
    exit 0
}

# 단일 포트 서버 실행
start_single() {
    PORT=$1
    LOG_FILE="logs/appium_${PORT}.log"
    mkdir -p logs

    # 이미 실행 중이면 종료 후 재시작
    PID=$(lsof -ti :$PORT)
    if [ -n "$PID" ]; then
        echo "  ⚠️  포트 $PORT 이미 실행 중 → 재시작"
        kill -9 $PID
        sleep 1
    fi

    appium -p $PORT --address $HOST > $LOG_FILE 2>&1 &
    echo "  ✅ 포트 $PORT 시작 | 주소: $HOST:$PORT | 로그: $LOG_FILE"
}

# 메인 실행
if [ "$1" = "stop" ]; then
    stop_servers
elif [ -n "$1" ]; then
    # 특정 포트만 실행
    echo "\n🚀 Appium 서버 시작 (포트: $1)"
    start_single $1
else
    # 전체 포트 실행
    echo "\n🚀 Appium 서버 전체 시작 | HOST: $HOST"
    start_single $AOS_EMULATOR_PORT
    start_single $AOS_REAL_PORT
    start_single $IOS_SIMULATOR_PORT
    start_single $IOS_REAL_PORT
fi

echo "\n✅ 완료"