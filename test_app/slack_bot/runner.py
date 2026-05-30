import subprocess
import threading
import os
import re
import signal
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_running_processes: dict[str, subprocess.Popen] = {}
_lock = threading.Lock()


def build_command(platform: Optional[str], modules: list[str], environment: str, parallel: bool) -> list[list[str]]:
    base = ["python", "run_all.py", "--reset", "full"]
    commands = []

    if parallel and not platform:
        cmd = base + ["--parallel"]
        if modules:
            cmd += ["--module", modules[0]]
        commands.append(("parallel", cmd))
    else:
        platforms = []
        if platform == "aos":
            platforms = ["aos"]
        elif platform == "ios":
            platforms = ["ios"]
        elif platform == "both":
            platforms = ["aos", "ios"]

        for p in platforms:
            cmd = base + ["--platform", p]
            if modules:
                cmd += ["--module", modules[0]]
            commands.append((p, cmd))

    return commands


def run_tests(
    run_id: str,
    platform: Optional[str],
    modules: list[str],
    environment: str,
    parallel: bool,
    on_log: callable,
    on_finish: callable,
):

    project_path = os.getenv("TEST_PROJECT_PATH", ".")
    commands = build_command(platform, modules, environment, parallel)

    try:
        for platform_key, cmd in commands:
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
                logger.info(f"[runner] 프로세스 등록: {run_id} | 현재 목록: {list(_running_processes.keys())}")

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

                if "테스트 결과 요약" in line or "테스트 기기" in line:
                    in_summary = True
                if in_summary:
                    summary_lines.append(line)
                    if "로그파일명" in line and report_filename:
                        summary_lines.append(f"📄 Test Report : {report_filename}")

                if "::" in line and "tests/" in line:
                    match = re.match(r'(tests/\S+::\S+::\S+)', line)
                    if match:
                        current_test_name = match.group(1)

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

            summary = "\n".join(summary_lines) if summary_lines else "테스트 요약 없음"
            on_finish(platform_key, proc.returncode, summary)

    except Exception as e:
        logger.error(f"[runner] 오류: {e}")
        on_finish("error", -1, str(e))
    finally:
        with _lock:
            _running_processes.pop(run_id, None)


def stop_test(run_id: str) -> bool:
    with _lock:
        proc = _running_processes.get(run_id)
        if proc:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                logger.info(f"[stop_test] 프로세스 그룹 종료: {run_id}")
            except Exception as e:
                logger.warning(f"[stop_test] killpg 실패, terminate 시도: {e}")
                proc.terminate()
            _running_processes.pop(run_id, None)
            return True
        logger.warning(f"[stop_test] run_id 없음: {run_id} | 현재 목록: {list(_running_processes.keys())}")
    return False


def get_running_ids() -> list[str]:
    with _lock:
        return list(_running_processes.keys())