import subprocess
import threading
import os
import re
import signal
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_running_processes: dict[str, subprocess.Popen] = {}
_lock = threading.Lock()

_stopped_runs: set = set()


def build_commands(platform: Optional[str], modules: list[str], parallel: bool) -> list[tuple]:
    base = ["python", "run_all.py", "--reset", "full"]
    commands = []

    if parallel:
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

        if "[driver] 연결 기기:" in line and on_device:
            match = re.search(r'연결 기기: (.+)', line)
            if match:
                on_device(match.group(1))

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

    project_path = os.getenv("TEST_PROJECT_PATH", ".")
    commands = build_commands(platform, modules, parallel)

    try:
        if parallel:
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
    with _lock:
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
    with _lock:
        base_ids = set()
        for key in _running_processes:
            base_id = key.split("_aos")[0].split("_ios")[0]
            base_ids.add(base_id)
        return list(base_ids)