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

DEFAULT_STALL_SECONDS = 180
DEFAULT_MAX_RETRIES   = 2

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
    판단하는 기준이 된다."""
    cmd = ["pytest", module, f"--platform={platform}", f"--env={env}", "--collect-only", "-q"]
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
    watchdog:      bool = True,
    stall_seconds: int  = DEFAULT_STALL_SECONDS,
    max_retries:   int  = DEFAULT_MAX_RETRIES,
):
    active_devices = get_active_devices(platform)

    for device in active_devices:
        init_output_dirs(device["platform"])

    # watchdog(3분 무응답 감지+자동 재시작)은 현재 iOS에서만 반복 확인된 문제라 iOS에만
    # 적용한다(AOS는 기존 방식 그대로 - 검증 안 된 새 로직을 이미 안정적인 파이프라인에
    # 굳이 넣지 않기 위함). module이 없으면(tests/ 전체 실행) 클래스 단위 재시작 지점을
    # 계산할 수 없어 이때도 기존 방식으로 동작한다.
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
    parser.add_argument("--no-watchdog", action="store_true",
                         help="iOS 3분 무응답 감지+자동재시작(watchdog) 비활성화")
    parser.add_argument("--stall-seconds", type=int, default=DEFAULT_STALL_SECONDS,
                         help="watchdog 무응답 판단 기준(초), 기본 180")
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
                         help="watchdog 최대 재시도 횟수, 기본 2")
    args = parser.parse_args()

    run(
        platform=args.platform,
        module=args.module,
        keyword=args.keyword,
        login=args.login,
        reset=args.reset,
        parallel=args.parallel,
        watchdog=not args.no_watchdog,
        stall_seconds=args.stall_seconds,
        max_retries=args.max_retries,
    )