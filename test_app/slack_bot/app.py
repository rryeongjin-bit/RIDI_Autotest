import os
import json
import hmac
import hashlib
import time
import threading
import uuid
import logging
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import runner
import reporter

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SLACK_BOT_TOKEN      = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_CHANNEL_ID     = os.getenv("SLACK_CHANNEL_ID")
slack_client         = WebClient(token=SLACK_BOT_TOKEN)


_active_runs: dict = {}
_runs_lock = threading.Lock()


TEST_MODULES = [
    {"value": "tests/test_basic.py", "label": "test_basic.py"},
]

def verify_slack_signature(req) -> bool:
    timestamp = req.headers.get("X-Slack-Request-Timestamp", "")
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False
    sig_basestring = f"v0:{timestamp}:{req.get_data(as_text=True)}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256,
    ).hexdigest()
    slack_signature = req.headers.get("X-Slack-Signature", "")
    return hmac.compare_digest(my_signature, slack_signature)


@app.route("/slack/command/start", methods=["POST"])
def slash_start():
    if not verify_slack_signature(request):
        return jsonify({"error": "invalid signature"}), 403

    trigger_id = request.form.get("trigger_id")
    _open_start_modal(trigger_id)
    return "", 200


def _open_start_modal(trigger_id: str):
    module_options = [
        {
            "text": {"type": "plain_text", "text": m["label"]},
            "value": m["value"],
        }
        for m in TEST_MODULES
    ]

    modal = {
        "type": "modal",
        "callback_id": "qa_test_start_modal",
        "title": {"type": "plain_text", "text": "🤖 QA 자동화 테스트 실행"},
        "submit": {"type": "plain_text", "text": "실행"},
        "close":  {"type": "plain_text", "text": "취소"},
        "blocks": [
            {
                "type": "input",
                "block_id": "platform_block",
                "label": {"type": "plain_text", "text": "📱 플랫폼"},
                "element": {
                    "type": "checkboxes",
                    "action_id": "platform_select",
                    "options": [
                        {"text": {"type": "plain_text", "text": "AOS"}, "value": "aos"},
                        {"text": {"type": "plain_text", "text": "iOS"}, "value": "ios"},
                    ],
                },
            },
            {
                "type": "input",
                "block_id": "module_block",
                "label": {"type": "plain_text", "text": "🗂 테스트 모듈"},
                "element": {
                    "type": "checkboxes",
                    "action_id": "module_select",
                    "options": module_options,
                },
                "optional": False,
            },
            {
                "type": "input",
                "block_id": "env_block",
                "label": {"type": "plain_text", "text": "🌐 테스트 환경"},
                "element": {
                    "type": "radio_buttons",
                    "action_id": "env_select",
                    "options": [
                        {"text": {"type": "plain_text", "text": "🔴 Stage"},      "value": "stage"},
                        {"text": {"type": "plain_text", "text": "🟡 Canary"},     "value": "canary"},
                        {"text": {"type": "plain_text", "text": "🔵 Production"}, "value": "production"},
                    ],
                },
            },
        ],
    }

    try:
        slack_client.views_open(trigger_id=trigger_id, view=modal)
    except SlackApiError as e:
        logger.error(f"[modal] 열기 실패: {e}")


@app.route("/slack/command/stop", methods=["POST"])
def slash_stop():
    if not verify_slack_signature(request):
        return jsonify({"error": "invalid signature"}), 403

    trigger_id = request.form.get("trigger_id")
    _open_stop_modal(trigger_id)  
    return "", 200

def _open_stop_modal(trigger_id: str):
    modal = {
        "type": "modal",
        "callback_id": "qa_test_stop_modal",
        "title": {"type": "plain_text", "text": "🛑 테스트 강제 종료"},
        "submit": {"type": "plain_text", "text": "종료"},
        "close":  {"type": "plain_text", "text": "취소"},
        "blocks": [
            {
                "type": "input",
                "block_id": "run_id_block",
                "label": {"type": "plain_text", "text": "🆔 종료할 Run ID 입력"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "run_id_input",
                    "placeholder": {"type": "plain_text", "text": "예: 20260530_204512"},
                },
                "hint": {"type": "plain_text", "text": "슬랙 메시지에서 Run ID를 확인하세요."},
            },
        ],
    }

    try:
        slack_client.views_open(trigger_id=trigger_id, view=modal)
    except SlackApiError as e:
        logger.error(f"[modal] 종료 모달 열기 실패: {e}")


@app.route("/slack/interactions", methods=["POST"])
def interactions():
    if not verify_slack_signature(request):
        return jsonify({"error": "invalid signature"}), 403

    payload = json.loads(request.form.get("payload", "{}"))
    interaction_type = payload.get("type")

    if interaction_type == "view_submission":
        callback_id = payload["view"]["callback_id"]
        if callback_id == "qa_test_start_modal":

            t = threading.Thread(target=_handle_modal_submit, args=(payload,), daemon=True)
            t.start()
            return "", 200
        elif callback_id == "qa_test_stop_modal":
  
            t = threading.Thread(target=_handle_stop_modal_submit, args=(payload,), daemon=True)
            t.start()
            return "", 200

    return "", 200


def _handle_stop_modal_submit(payload: dict):
    values = payload["view"]["state"]["values"]
    run_id = values.get("run_id_block", {}).get("run_id_input", {}).get("value", "").strip()

    if not run_id:
        return

    if runner.stop_test(run_id):
        with _runs_lock:
            run_info = _active_runs.get(run_id, {})

        if run_info:
            _update_main_message(
                channel=run_info["channel"],
                ts=run_info["ts"],
                env_label=run_info["environment"], 
                status="🛑 테스트 강제 종료",
                run_id=run_id,
            )
            _post_thread(
                channel=run_info["channel"],
                thread_ts=run_info["thread_ts"],
                text=f"🛑 테스트가 강제 종료되었습니다. (Run ID: `{run_id}`)",
            )
            with _runs_lock:
                _active_runs.pop(run_id, None)
    else:
        slack_client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=f"⚠️ Run ID `{run_id}` 에 해당하는 실행 중인 테스트가 없습니다.",
        )


def _handle_modal_submit(payload: dict):
    values  = payload["view"]["state"]["values"]
    user_id = payload["user"]["id"]
    channel = SLACK_CHANNEL_ID


    platform_selected = [
        o["value"]
        for o in values.get("platform_block", {}).get("platform_select", {}).get("selected_options", [])
    ]


    modules_selected = [
        o["value"]
        for o in values.get("module_block", {}).get("module_select", {}).get("selected_options", [])
    ]


    env_selected = values.get("env_block", {}).get("env_select", {}).get("selected_option", {}).get("value", "stage")

    if len(platform_selected) == 2:
        platform = "both"
        parallel = True
    elif len(platform_selected) == 1:
        platform = platform_selected[0]
        parallel = False
    else:
        platform = None
        parallel = False


    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    env_label_map = {
        "stage":      "🔴 Stage",
        "canary":     "🟡 Canary",
        "production": "🔵 Production",
    }
    env_label = env_label_map.get(env_selected, "🔴 Stage")

    msg = _post_main_message(channel, env_label, "테스트 시작 🚀", run_id)
    ts  = msg["ts"]

    _update_main_message(channel, ts, env_label, "테스트 진행중 ⏳", run_id=run_id)

    thread_resp = _post_thread(channel, ts, f"<@{user_id}> 님이 테스트를 시작했어요.")
    thread_ts   = thread_resp["ts"]

    with _runs_lock:
        _active_runs[run_id] = {
            "channel":     channel,
            "ts":          ts,
            "thread_ts":   thread_ts,
            "environment": env_label,
            "platform":    platform,
        }

    t = threading.Thread(
        target=_execute_tests,
        args=(run_id, platform, modules_selected, env_selected, env_label, parallel, channel, ts, thread_ts),
        daemon=True,
    )
    t.start()


def _execute_tests(run_id, platform, modules, env_selected, env_label, parallel, channel, ts, thread_ts):
    
    progress_ts = [None]
    progress_lines = []

    def on_log(log_chunk: str):
        if not log_chunk.strip():
            return
        
        is_progress = any(kw in log_chunk for kw in ["PASSED", "FAILED", "SKIPPED", "ERROR"]) and "::" in log_chunk
        
        if is_progress:
            progress_lines.append(log_chunk)
            content = "```\n" + "\n".join(progress_lines[-50:]) + "\n```"  
            
            if progress_ts[0] is None:
                resp = _post_thread(channel, thread_ts, content)
                progress_ts[0] = resp.get("ts")
            else:
                try:
                    slack_client.chat_update(
                        channel=channel,
                        ts=progress_ts[0],
                        text=content,
                    )
                except SlackApiError as e:
                    logger.error(f"[slack] 진행률 업데이트 실패: {e}")
        else:
            _post_thread(channel, thread_ts, log_chunk)

    def on_finish(platform_key: str, returncode: int, summary: str):
        report_path = reporter.get_latest_report(platform_key if platform_key != "parallel" else "aos")
        if report_path:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                screenshot_path = f.name
            if reporter.capture_report_screenshot(report_path, screenshot_path):
                try:
                    slack_client.files_upload_v2(
                        channel=channel,
                        thread_ts=thread_ts,
                        file=screenshot_path,
                        title=f"📊 {platform_key} 테스트 리포트",
                    )
                except SlackApiError as e:
                    logger.error(f"[reporter] 업로드 실패: {e}")

        _update_main_message(channel, ts, env_label, "테스트 종료 🔚", run_id=run_id, summary=summary)

        with _runs_lock:
            _active_runs.pop(run_id, None)

    runner.run_tests(
        run_id=run_id,
        platform=platform,
        modules=modules,
        environment=env_selected,
        parallel=parallel,
        on_log=on_log,
        on_finish=on_finish,
    )


def _post_main_message(channel: str, env_label: str, status: str, run_id: str = "") -> dict:
    text = f"*Test Environment :* {env_label}\n*{status}*"
    if run_id:
        text += f"\n🆔 Run ID : `{run_id}`"

    resp = slack_client.chat_postMessage(
        channel=channel,
        text=text,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
            }
        ],
    )
    return resp


def _update_main_message(channel: str, ts: str, env_label: str, status: str, run_id: str = "", summary: str = ""):
    text = f"*Test Environment :* {env_label}\n*{status}*"
    if run_id:
        text += f"\n🆔 Run ID : `{run_id}`"

    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        }
    ]
    if summary:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"```{summary}```"},
        })

    try:
        slack_client.chat_update(
            channel=channel,
            ts=ts,
            text=text,
            blocks=blocks,
        )
    except SlackApiError as e:
        logger.error(f"[slack] 메시지 업데이트 실패: {e}")


def _post_thread(channel: str, thread_ts: str, text: str) -> dict:
    try:
        resp = slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=text,
        )
        return resp
    except SlackApiError as e:
        logger.error(f"[slack] 스레드 전송 실패: {e}")
        return {}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(port=port, debug=False)