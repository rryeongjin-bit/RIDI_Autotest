import sys
import os
import re
import signal
import socket
import subprocess
import threading
import time
import urllib.request
from datetime import datetime
from config.capabilities import *
from utils.helpers import *

DEFAULT_STALL_SECONDS = 300
DEFAULT_MAX_RETRIES   = 5

def check_appium_server(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def get_active_devices(platform: str = None) -> list:
    active  = []
    targets = DEVICE_CONFIG if platform is None else {platform: DEVICE_CONFIG.get(platform, [])}

    for plat, devices in targets.items():
        for device in devices:
            if check_appium_server(device["port"]):
                active.append({**device, "platform": plat})
                print(f"[ACTIVE] {device['device_name']} | 플랫폼: {plat} | 환경: {device['type']} | 포트: {device['port']}")
            else:
                print(f"[SKIP]   {device['device_name']} | 서버 연결 안됨")

    if not active:
        print("[ERROR] 활성화된 서버/기기 없음. 테스트 중단")
        sys.exit(1)

    return active

def build_pytest_command(
    device:  dict,
    module:  str  = None,
    keyword: str  = None,
    login:   str  = "auto",  
    reset:   str  = "full",  
) -> list:
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    platform = device["platform"]
    env      = device["type"]
    report   = get_report_path(platform, ts)

    cmd = [
        "pytest",
        module if module else "tests/",
        f"--platform={platform}",
        f"--env={env}",
        f"--login={login}",
        f"--reset={reset}",
        f"--html={report}",
        "--self-contained-html",
        "-v",
        "--tb=short",  
    ]

    if keyword:
        cmd += ["-k", keyword]

    return cmd

def _kill_port(port: int):
    """포트를 점유 중인 프로세스를 찾아 강제 종료(Appium 서버 재시작 전 정리용)."""
    try:
        pids = subprocess.check_output(["lsof", "-ti", f"tcp:{port}"], text=True).split()
    except subprocess.CalledProcessError:
        pids = []
    for pid in pids:
        try:
            os.kill(int(pid), signal.SIGKILL)
        except ProcessLookupError:
            pass

def _wait_appium_ready(port: int, timeout: int = 30) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/status", timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

def _dismiss_ios_restart_popups(device: dict, settle_seconds: int = 15):
    """watchdog로 Appium 서버를 재시작한 직후, 새 WDA 세션이 앱을 다시 활성화시키면서
    알림 권한/트래킹 팝업이 재실기기로 확인된 바 있다(2026-07-23). 본 재실행 pytest를
    띄우기 전에 짧은 드라이버 세션 하나로 기존 Alertnotification.click_noti_alert()
    (알림+트래킹 팝업 최대 2개 허용, 팝업이 없으면 조용히 무시하도록 이미 구현되어 있음)를
    재사용해 미리 정리해둔다. 팝업 자체가 없거나 이 단계에서 실패해도 본 재실행은
    그대로 진행한다(수동 개입 없이 넘어가는 게 목적이라 이 단계는 실패해도 무시)."""
    try:
        from appium import webdriver
        from pages.home_page import Alertnotification

        options = get_capabilities(device["platform"], device)
        drv = webdriver.Remote(get_server_url(device["port"]), options=options)
        time.sleep(settle_seconds)
        Alertnotification(drv, device["platform"]).click_noti_alert()
        drv.quit()
        print("[watchdog] 재시작 후 알림/트래킹 팝업 정리 완료")
    except Exception as e:
        print(f"[watchdog] 팝업 정리 시도 실패(무시하고 재실행 계속): {e}")

def restart_appium_server(port: int) -> bool:
    """멈춤 감지 시 pytest 프로세스만 죽이면 그 밑에 물려있던 WDA 세션이 찌꺼기로 남아
    다음 재시도가 같은 고장난 세션을 재사용하려다 또 멈추는 문제가 실기기로 확인되어
    (2026-07-23), Appium 서버 자체도 같이 재시작한다. 앱 자체의 데이터 초기화/재로그인과는
    무관 - 그건 --reset/--login 옵션이 별도로 담당하며 재시도 시 skip으로 유지한다."""
    print(f"[watchdog] Appium 서버(포트 {port}) 재시작")
    _kill_port(port)
    time.sleep(2)
    subprocess.Popen(
        ["appium", "-p", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    ready = _wait_appium_ready(port)
    if ready:
        print(f"[watchdog] Appium 서버(포트 {port}) 재기동 완료")
    else:
        print(f"[watchdog] Appium 서버(포트 {port}) 재기동 확인 실패 - 계속 진행은 시도함")
    return ready

def _collect_test_classes(module: str, platform: str, env: str) -> list:
    """대상 모듈의 테스트 클래스를 파일에 등장하는 순서대로 수집(--collect-only는 픽스처를
    실행하지 않아 기기 연결 없이도 가볍게 조회 가능). 멈춤 발생 시 "어느 클래스부터 재시작할지"
    판단하는 기준이 된다.

    pytest.ini의 addopts에 -v가 항상 포함돼 있어, 이 호출에서 -q를 줘도 순단위(-v)가 상쇄되지
    않고 --collect-only가 트리 형태(<Class .../<Function ...>)로 출력되는 문제가 실기기 회귀
    테스트로 확인되었다(2026-07-28) - 아래 정규식이 기대하는 "module::Class::test" 평면 형식이
    전혀 안 나와 classes가 항상 빈 리스트로 반환되고, 그 결과 watchdog 재시도 때마다 멈춘
    클래스가 아니라 모듈 맨 처음부터 다시 실행되는 버그로 이어졌다. -o addopts=""로 ini의
    addopts를 이 호출 한정으로 리셋해 평면 형식이 나오도록 강제한다."""
    cmd = ["pytest", module, f"--platform={platform}", f"--env={env}",
           "--collect-only", "-q", "-o", "addopts="]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return []
    classes = []
    seen = set()
    pattern = re.compile(re.escape(module) + r"::(\w+)::")
    for line in result.stdout.splitlines():
        m = pattern.match(line)
        if m:
            cls = m.group(1)
            if cls not in seen:
                seen.add(cls)
                classes.append(cls)
    return classes

_NODE_ID_RE = re.compile(r"::(\w+)::test_")

def _last_class_from_output(text: str) -> str | None:
    last = None
    for m in _NODE_ID_RE.finditer(text):
        last = m.group(1)
    return last

def _remaining_classes(all_classes: list, stalled_class: str) -> list:
    if stalled_class in all_classes:
        return all_classes[all_classes.index(stalled_class):]
    return all_classes

def run_with_watchdog(
    device:        dict,
    module:        str,
    keyword:       str  = None,
    login:         str  = "auto",
    reset:         str  = "full",
    stall_seconds: int  = DEFAULT_STALL_SECONDS,
    max_retries:   int  = DEFAULT_MAX_RETRIES,
) -> int:
    """pytest 서브프로세스 출력을 실시간 추적하다가 stall_seconds 동안 새 출력이 없으면
    (WDA 세션이 살아있는 것처럼 보이지만 실제로는 응답 없이 멈추는 현상, 2026-07-23 실기기로
    반복 확인됨) 프로세스와 Appium 서버를 함께 재시작하고, 멈춘 지점의 테스트 클래스부터
    (--login=skip --reset=skip로) 이어서 실행한다. 같은 실행에서 max_retries회 넘게
    멈추면 포기하고 마지막 실행 결과를 그대로 반환한다."""
    platform = device["platform"]
    env      = device["type"]
    port     = device["port"]

    all_classes  = _collect_test_classes(module, platform, env)
    targets      = [f"{module}::{c}" for c in all_classes] if all_classes else [module]
    cur_login    = login
    cur_reset    = reset
    retries      = 0

    while True:
        ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = get_report_path(platform, ts)
        cmd = [
            "pytest", *targets,
            f"--platform={platform}", f"--env={env}",
            f"--login={cur_login}", f"--reset={cur_reset}",
            f"--html={report}", "--self-contained-html", "-v", "--tb=short",
        ]
        if keyword:
            cmd += ["-k", keyword]
        print(f"\n[RUN] {' '.join(cmd)}\n")

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, start_new_session=True,
        )
        last_activity = time.time()
        captured_lines = []

        def _reader():
            nonlocal last_activity
            for line in proc.stdout:
                print(line, end="")
                captured_lines.append(line)
                last_activity = time.time()

        reader_thread = threading.Thread(target=_reader, daemon=True)
        reader_thread.start()

        stalled = False
        while proc.poll() is None:
            time.sleep(5)
            if time.time() - last_activity > stall_seconds:
                stalled = True
                break

        if not stalled:
            reader_thread.join(timeout=5)
            return proc.returncode

        print(f"\n[watchdog] {stall_seconds}초 무응답 감지 - 프로세스 종료 후 재시작 시도")
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        reader_thread.join(timeout=5)

        restart_appium_server(port)
        if platform == "ios":
            _dismiss_ios_restart_popups(device)

        stalled_class = _last_class_from_output("".join(captured_lines))
        if stalled_class and all_classes:
            remaining = _remaining_classes(all_classes, stalled_class)
            # iOS 3분 무응답 재시작 시 로그인 세션이 풀려있어 이후 개인화 섹션을 못 찾는 연쇄
            # 실패가 실기기로 확인되어(2026-07-23), 재시작 대상 맨 앞에 로그인 관련 클래스를
            # 포함시켜 매번 재로그인 후 멈췄던 클래스(장르홈 섹션)로 돌아와 이어서 진행한다.
            prelude = [c for c in ("TestLogoutIfNeeded", "TestLogin") if c in all_classes and c not in remaining]
            all_classes = prelude + remaining
            targets = [f"{module}::{c}" for c in all_classes]
            print(f"[watchdog] 재시작 지점: {stalled_class} 클래스부터 (재로그인 포함)")
        # TestLogin은 --reset==skip and --login==skip일 때만 자기 자신을 스킵하므로(conftest.py),
        # login=auto로 바꿔 재로그인이 실제로 수행되게 한다. reset은 계속 skip 유지(앱 전체
        # 재설치는 불필요).
        cur_login, cur_reset = "auto", "skip"

        retries += 1
        if retries > max_retries:
            print(f"[watchdog] 재시도 {max_retries}회 초과 - 포기하고 종료")
            return 1

def run(
    platform:      str  = None,
    module:        str  = None,
    keyword:       str  = None,
    login:         str  = "auto",
    reset:         str  = "full",
    parallel:      bool = False,
    watchdog:      bool = False,
    stall_seconds: int  = DEFAULT_STALL_SECONDS,
    max_retries:   int  = DEFAULT_MAX_RETRIES,
):
    active_devices = get_active_devices(platform)

    for device in active_devices:
        init_output_dirs(device["platform"])

    # watchdog(무응답 감지 + 세션 종료 후 자동 재시작)은 기본 비활성화한다(2026-07-29).
    #
    # 원래 iOS 무응답 대응으로 넣었지만, 실제로는 "멈춘 것"이 아니라 "느린 것"을 죽이고 있었다.
    # iOS는 섹션 콘텐츠를 읽을 때 XCUIElementTypeOther 블롭을 조회하는데 이 화면에서 WDA 응답이
    # 수 분씩 걸린다. 좌우스와이프 5회를 도는 동안 그 조회가 반복되지만 그 사이에는 로그가
    # 전혀 출력되지 않아, 정상 진행 중인데도 무응답으로 오판된다(2026-07-29 실기기 확인 -
    # "방금 본 작품과 비슷한" 첫번째 작품 로그 이후 300초간 로그가 없어 재시작됐는데, 실기기
    # 화면에서는 스와이프가 끝나고 마지막 작품까지 정상 노출된 상태였음).
    #
    # 게다가 재시작은 --reset=skip으로 들어가 앱의 로그인 세션이 남은 상태라 로그인 단계가
    # 어긋나고(로그인 누락/실패로 기록), 재시작 지점부터 다시 도느라 같은 느린 구간을 또
    # 만나 무한 재시도로 이어졌다. 즉 문제를 해결하지 못하고 오히려 실행을 망가뜨렸다.
    #
    # 섹션 플로우 자체는 "5회 좌스와이프 → 그 위치 기준 마지막 작품 확인 → 역방향 스와이프로
    # 원복 → 더보기 있으면 진입, 없으면 다음 섹션"으로 이미 유한하게 끝나는 구조이므로,
    # 중간에 강제로 끊지 않고 끝까지 기다리는 게 맞다. 필요하면 --watchdog으로 명시적으로만
    # 켠다. module이 없으면(tests/ 전체 실행) 클래스 단위 재시작 지점을 계산할 수 없어
    # 이때도 기존 방식으로 동작한다.
    procs   = []
    threads = []
    for device in active_devices:
        use_watchdog = watchdog and module and device["platform"] == "ios"

        if use_watchdog:
            args = (device, module, keyword, login, reset, stall_seconds, max_retries)
            if parallel:
                th = threading.Thread(target=run_with_watchdog, args=args)
                th.start()
                threads.append(th)
            else:
                run_with_watchdog(*args)
            continue

        cmd = build_pytest_command(
            device=device,
            module=module,
            keyword=keyword,
            login=login,
            reset=reset,
        )
        print(f"\n[RUN] {' '.join(cmd)}\n")

        if parallel:
            procs.append(subprocess.Popen(cmd))
        else:
            subprocess.run(cmd)

    for proc in procs:
        proc.wait()
    for th in threads:
        th.join()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mobile App 자동화 테스트 실행")
    parser.add_argument("--platform", default=None,   help="실행 플랫폼: aos | ios")
    parser.add_argument("--module",   default=None,   help="특정 모듈: tests/test_basic.py")
    parser.add_argument("--keyword",  default=None,   help="키워드: test_login_success")
    parser.add_argument("--login",    default="auto", help="로그인 방식: auto | skip")  
    parser.add_argument("--reset",    default="full", help="앱 초기화: full | skip")   
    parser.add_argument("--parallel", action="store_true", help="병렬 실행 여부")
    # watchdog는 기본 비활성화(2026-07-29). iOS의 느린 구간을 무응답으로 오판해 정상 진행 중인
    # 실행을 죽이고, 재시작이 로그인 상태와 어긋나 오히려 실패를 만들었다(run() 주석 참고).
    # 진단 목적으로 필요할 때만 --watchdog으로 명시적으로 켠다. --no-watchdog은 기존 호출부
    # 호환을 위해 남겨두지만 이제 기본값과 같아 아무 효과가 없다.
    parser.add_argument("--watchdog", action="store_true",
                         help="무응답 감지+자동재시작(watchdog) 활성화 (기본 비활성화)")
    parser.add_argument("--no-watchdog", action="store_true",
                         help="(사용 안 함 - watchdog은 기본 비활성화) 호환용 플래그")
    parser.add_argument("--stall-seconds", type=int, default=DEFAULT_STALL_SECONDS,
                         help=f"watchdog 무응답 판단 기준(초), 기본 {DEFAULT_STALL_SECONDS}")
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
                         help="watchdog 최대 재시도 횟수, 기본 5")
    args = parser.parse_args()

    run(
        platform=args.platform,
        module=args.module,
        keyword=args.keyword,
        login=args.login,
        reset=args.reset,
        parallel=args.parallel,
        watchdog=args.watchdog and not args.no_watchdog,
        stall_seconds=args.stall_seconds,
        max_retries=args.max_retries,
    )