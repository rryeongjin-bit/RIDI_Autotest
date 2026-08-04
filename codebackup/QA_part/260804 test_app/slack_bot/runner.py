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
    """플랫폼별로 (suffix, platform_key, modules) 튜플을 만든다. modules는 선택된 전체
    목록을 그대로 넘기고(이전에는 modules[0]만 써서 2개 이상 체크해도 첫번째만 실행되던
    문제가 있었음), 실제로 모듈별 커맨드를 조립하고 순서대로 실행하는 건 run_sequential이
    담당한다."""
    if parallel:
        return [(p, p, modules) for p in ["aos", "ios"]]
    p = platform or "aos"
    return [(p, p, modules)]


def _run_one(
    run_id: str,
    platform_key: str,
    cmd: list[str],
    project_path: str,
    on_log: callable,
    on_device: callable,
):
    """서브프로세스 하나를 실행하고 출력을 파싱한다. (returncode, summary, all_failures,
    was_stopped)를 반환하며, on_finish 호출은 호출측(run_sequential)이 전체 모듈 실행이
    끝난 뒤 한 번만 담당한다."""
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
    all_failures = []
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
                found_kw = next((kw for kw in ["PASSED", "FAILED", "SKIPPED", "ERROR"] if kw in line), None)
                if found_kw:
                    pct_match = re.search(r'\[\s*\d+%\]', line)
                    pct = pct_match.group(0) if pct_match else ""
                    on_log(platform_key, f"{current_test_name} {found_kw} {pct}".strip())
                    current_test_name = None
            continue

        stripped = line.strip()
        if stripped in ("PASSED", "FAILED", "SKIPPED", "ERROR"):
            if current_test_name:
                on_log(platform_key, f"{current_test_name} {stripped}")
                current_test_name = None
            continue

        if "= FAILURES =" in line or "= ERRORS =" in line:
            in_failure = True
            failure_buffer = [line]
        elif in_failure:
            failure_buffer.append(line)
            if line.startswith("=====") and len(failure_buffer) > 2:
                all_failures.append("\n".join(failure_buffer))
                failure_buffer = []
                in_failure = False

    proc.wait()

    with _lock:
        _running_processes.pop(run_id, None)
        was_stopped = run_id in _stopped_runs
        if was_stopped:
            _stopped_runs.discard(run_id)

    summary = "\n".join(summary_lines) if summary_lines else "테스트 강제 종료"
    return proc.returncode, summary, all_failures, was_stopped


def run_sequential(
    run_id: str,
    platform_key: str,
    modules: list[str],
    project_path: str,
    on_log: callable,
    on_device: callable,
    on_finish: callable,
):
    """선택된 모듈이 여러 개면 하나씩 순서대로 실행하고, 결과를 합쳐서 on_finish를 마지막에
    한 번만 호출한다. 모듈 선택이 0~1개면 기존과 동일하게 한 번만 돈다(회귀 없음). 도중에
    강제종료되면 다음 모듈로 넘어가지 않고 그 자리에서 중단한다."""
    module_list = modules if modules else [None]
    base = ["python", "run_all.py", "--reset", "full", "--platform", platform_key]

    combined_summary_parts = []
    combined_failures = []
    final_returncode = 0
    stopped = False

    for idx, module in enumerate(module_list, 1):
        cmd = base + (["--module", module] if module else [])
        module_label = module or "전체"
        if len(module_list) > 1:
            on_log(platform_key, f"▶ [{idx}/{len(module_list)}] {module_label} 실행 시작")

        returncode, summary, failures, was_stopped = _run_one(
            run_id, platform_key, cmd, project_path, on_log, on_device
        )
        if was_stopped:
            stopped = True
            break

        header = f"--- {module_label} ---\n" if len(module_list) > 1 else ""
        combined_summary_parts.append(f"{header}{summary}")
        combined_failures.extend(failures)
        if returncode != 0:
            final_returncode = returncode

    if not stopped:
        on_finish(platform_key, final_returncode, "\n\n".join(combined_summary_parts), combined_failures)


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
            for (suffix, platform_key, modules_for_platform) in commands:
                sub_run_id = f"{run_id}_{suffix}"
                t = threading.Thread(
                    target=run_sequential,
                    args=(sub_run_id, platform_key, modules_for_platform, project_path,
                          on_log, on_device, on_finish),
                    daemon=True,
                )
                threads.append(t)
                t.start()

            for t in threads:
                t.join()
        else:
            for (suffix, platform_key, modules_for_platform) in commands:
                run_sequential(run_id, platform_key, modules_for_platform, project_path,
                               on_log, on_device, on_finish)

    except Exception as e:
        logger.error(f"[runner] 오류: {e}")
        on_finish("error", -1, str(e), [])


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