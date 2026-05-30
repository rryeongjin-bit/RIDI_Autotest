import sys
import socket
import subprocess
from datetime import datetime
from config.capabilities import *
from utils.helpers import *

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
        "-s",     
        "--tb=short", 
    ]

    if keyword:
        cmd += ["-k", keyword]

    return cmd

def run(
    platform: str  = None,
    module:   str  = None,
    keyword:  str  = None,
    login:    str  = "auto",
    reset:    str  = "full",
    parallel: bool = False,
):
    active_devices = get_active_devices(platform)

    for device in active_devices:
        init_output_dirs(device["platform"])

    procs = []
    for device in active_devices:
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mobile App 자동화 테스트 실행")
    parser.add_argument("--platform", default=None,   help="실행 플랫폼: aos | ios")
    parser.add_argument("--module",   default=None,   help="특정 모듈: tests/test_basic.py")
    parser.add_argument("--keyword",  default=None,   help="키워드: test_login_success")
    parser.add_argument("--login",    default="auto", help="로그인 방식: auto | skip")  
    parser.add_argument("--reset",    default="full", help="앱 초기화: full | skip")   
    parser.add_argument("--parallel", action="store_true", help="병렬 실행 여부")
    args = parser.parse_args()

    run(
        platform=args.platform,
        module=args.module,
        keyword=args.keyword,
        login=args.login,    
        reset=args.reset,  
        parallel=args.parallel,
    )