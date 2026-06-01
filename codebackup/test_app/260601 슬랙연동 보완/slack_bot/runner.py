import subprocess
import threading
import os
import re
import signal
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 실행 중인 프로세스 관리
_running_processes: dict[str, subprocess.Popen] = {}
_lock = threading.Lock()

# 강제 종료된 run_id 관리
_stopped_runs: set = set()


def build_commands(platform: Optional[str], modules: list[str], parallel: bool) -> list[tuple]:
    """실행할 커맨드 리스트 생성 - (run_id_suffix, platform_key, cmd) 튜플 반환"""
    base = ["python", "run_all.py", "--reset", "full"]
    commands = []

    if parallel:
        # aos, ios 각각 별도 커맨드로 생성
        for p in ["aos", "ios"]:
            cmd = base + ["--platform", p]
            if modules:
                cmd += ["--module", modules[0]]
            commands.append((p, p, cmd))
    else:
        p = platform or "aos"
        cmd = base + ["--platform", p]
        if modules:
            cmd += ["--module", modules[0]]
        commands.append((p, p, cmd))

    return commands


def run_single(
    run_id: str,
    platform_key: str,
    cmd: list[str],
    project_path: str,
    on_log: callable,
    on_device: callable,
    on_finish: callable,
):
    """단일 플랫폼 테스트 실행"""
    logger.info(f"[runner] 실행: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,
    )

    with _lock:
        _running_processes[run_id] = proc
        logger.info(f"[runner] 프로세스 등록: {run_id} | 목록: {list(_running_processes.keys())}")

    summary_lines = []
    in_summary = False
    failure_buffer = []
    in_failure = False
    report_filename = None
    current_test_name = None

    for line in proc.stdout:
        line = line.rstrip()

        if line.startswith("[ACTIVE]") or line.startswith("[RUN]"):
            continue

        if "Generated html report" in line:
            match = re.search(r'(\d{8}_\d{6}_\w+_report\.html)', line)
            if match:
                report_filename = match.group(1)
            continue

        # 기기 정보 감지
        if "[driver] 연결 기기:" in line and on_device:
            match = re.search(r'연결 기기: (.+)', line)
            if match:
                on_device(match.group(1))

        # 테스트 요약 캡처
        if "테스트 결과 요약" in line or "테스트 기기" in line:
            in_summary = True
        if in_summary:
            summary_lines.append(line)
            if "로그파일명" in line and report_filename:
                summary_lines.append(f"📄 Test Report : {report_filename}")

        # 테스트 함수명 감지
        if "::" in line and "tests/" in line:
            match = re.match(r'(tests/\S+::\S+::\S+)', line)
            if match:
                current_test_name = match.group(1)

        # PASSED/FAILED/SKIPPED/ERROR 즉시 전송
        if any(kw in line for kw in ["PASSED", "FAILED", "SKIPPED", "ERROR"]):
            for kw in ["PASSED", "FAILED", "SKIPPED", "ERROR"]:
                if kw in line:
                    pct_match = re.search(r'\[\s*\d+%\]', line)
                    pct = pct_match.group(0) if pct_match else ""
                    if current_test_name:
                        on_log(f"{current_test_name} {kw} {pct}".strip())
                        current_test_name = None
                    break

        elif "= FAILURES =" in line or "= ERRORS =" in line:
            in_failure = True
            failure_buffer = [line]

        elif in_failure:
            failure_buffer.append(line)
            if line.startswith("=====") and len(failure_buffer) > 2:
                chunk = "\n".join(failure_buffer)
                on_log(f"```{chunk[:2900]}```")
                failure_buffer = []
                in_failure = False

    proc.wait()

    with _lock:
        _running_processes.pop(run_id, None)
        was_stopped = run_id in _stopped_runs
        if was_stopped:
            _stopped_runs.discard(run_id)

    if not was_stopped:
        summary = "\n".join(summary_lines) if summary_lines else "테스트 강제 종료"
        on_finish(platform_key, proc.returncode, summary)


def run_tests(
    run_id: str,
    platform: Optional[str],
    modules: list[str],
    environment: str,
    parallel: bool,
    on_log: callable,
    on_finish: callable,
    on_device: callable = None,
):
    """테스트 실행 - parallel이면 aos/ios 별도 스레드로 실행"""
    project_path = os.getenv("TEST_PROJECT_PATH", ".")
    commands = build_commands(platform, modules, parallel)

    try:
        if parallel:
            # aos, ios 별도 스레드로 동시 실행
            threads = []
            for (suffix, platform_key, cmd) in commands:
                sub_run_id = f"{run_id}_{suffix}"
                t = threading.Thread(
                    target=run_single,
                    args=(sub_run_id, platform_key, cmd, project_path,
                          on_log, on_device, on_finish),
                    daemon=True,
                )
                threads.append(t)
                t.start()

            for t in threads:
                t.join()
        else:
            for (suffix, platform_key, cmd) in commands:
                run_single(run_id, platform_key, cmd, project_path,
                           on_log, on_device, on_finish)

    except Exception as e:
        logger.error(f"[runner] 오류: {e}")
        on_finish("error", -1, str(e))


def stop_test(run_id: str) -> bool:
    """실행 중인 테스트 강제 종료 (자식 프로세스 포함)"""
    with _lock:
        # run_id 또는 run_id_aos, run_id_ios 모두 종료
        keys_to_stop = [k for k in _running_processes if k == run_id or k.startswith(f"{run_id}_")]
        if not keys_to_stop:
            logger.warning(f"[stop_test] run_id 없음: {run_id} | 목록: {list(_running_processes.keys())}")
            return False

        for key in keys_to_stop:
            proc = _running_processes.get(key)
            if proc:
                _stopped_runs.add(key)
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    logger.info(f"[stop_test] 종료: {key}")
                except Exception as e:
                    logger.warning(f"[stop_test] killpg 실패: {e}")
                    proc.terminate()
                _running_processes.pop(key, None)

        return True


def get_running_ids() -> list[str]:
    """현재 실행 중인 run_id 목록 (suffix 제외한 base run_id)"""
    with _lock:
        base_ids = set()
        for key in _running_processes:
            base_id = key.split("_aos")[0].split("_ios")[0]
            base_ids.add(base_id)
        return list(base_ids)