"""
MCP Tool 정의 및 라우팅
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_tool_definitions() -> list[dict]:
    return [
        # ── 세션 ──────────────────────────────────────────────
        {
            "name": "appium_connect",
            "description": "Appium 세션을 생성하여 iOS 또는 Android 기기에 연결합니다. 기기 UDID/Serial은 자동 감지됩니다. iOS/Android 동시 연결 가능하며, 연결 후 해당 플랫폼이 활성으로 설정됩니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["ios", "android"],
                        "description": "연결할 플랫폼"
                    },
                    "bundle_id": {
                        "type": "string",
                        "description": (
                            "앱 키 또는 번들 ID. "
                            "Android 키: ridi, ridi_stage, ridi_dev, ridi_one, ridi_one_stage, ridi_one_dev / "
                            "iOS 키: ridi, ridi_stage, ridi_dev / "
                            "또는 직접 bundle ID 입력 가능"
                        )
                    }
                },
                "required": ["platform"]
            }
        },
        {
            "name": "appium_switch_platform",
            "description": "이미 연결된 세션 간 활성 플랫폼을 전환합니다. iOS와 Android 모두 연결된 상태에서 명령 대상을 바꿀 때 사용합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["ios", "android"],
                        "description": "전환할 플랫폼"
                    }
                },
                "required": ["platform"]
            }
        },
        {
            "name": "appium_disconnect",
            "description": "Appium 세션을 종료합니다. platform 미지정 시 현재 활성 플랫폼 종료.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["ios", "android"],
                        "description": "종료할 플랫폼 (미지정 시 활성 플랫폼)"
                    }
                }
            }
        },
        {
            "name": "appium_status",
            "description": "현재 연결된 모든 Appium 세션 상태를 확인합니다.",
            "inputSchema": {"type": "object", "properties": {}}
        },

        # ── 스크린샷 ──────────────────────────────────────────
        {
            "name": "appium_screenshot",
            "description": "현재 활성 플랫폼의 화면 스크린샷을 촬영합니다.",
            "inputSchema": {"type": "object", "properties": {}}
        },

        # ── 탭 ───────────────────────────────────────────────
        {
            "name": "appium_tap",
            "description": "화면의 특정 좌표를 탭합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X 좌표 (픽셀)"},
                    "y": {"type": "integer", "description": "Y 좌표 (픽셀)"}
                },
                "required": ["x", "y"]
            }
        },
        {
            "name": "appium_tap_by_accessibility_id",
            "description": "accessibility_id로 요소를 찾아 탭합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "accessibility_id": {"type": "string"},
                    "timeout": {"type": "integer", "default": 10}
                },
                "required": ["accessibility_id"]
            }
        },
        {
            "name": "appium_tap_by_text",
            "description": "화면에 표시된 텍스트로 요소를 찾아 탭합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "버튼/레이블 텍스트"},
                    "timeout": {"type": "integer", "default": 10}
                },
                "required": ["text"]
            }
        },
        {
            "name": "appium_tap_by_xpath",
            "description": "XPath로 요소를 찾아 탭합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "xpath": {"type": "string"},
                    "timeout": {"type": "integer", "default": 10}
                },
                "required": ["xpath"]
            }
        },

        # ── 텍스트 입력 ───────────────────────────────────────
        {
            "name": "appium_type_text",
            "description": "accessibility_id로 입력 필드를 찾아 텍스트를 입력합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "accessibility_id": {"type": "string"},
                    "text": {"type": "string", "description": "입력할 텍스트"}
                },
                "required": ["accessibility_id", "text"]
            }
        },

        # ── 스와이프 / 스크롤 ─────────────────────────────────
        {
            "name": "appium_swipe",
            "description": "시작 좌표에서 끝 좌표로 스와이프합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_x": {"type": "integer"},
                    "start_y": {"type": "integer"},
                    "end_x": {"type": "integer"},
                    "end_y": {"type": "integer"},
                    "duration_ms": {"type": "integer", "default": 500}
                },
                "required": ["start_x", "start_y", "end_x", "end_y"]
            }
        },
        {
            "name": "appium_scroll_down",
            "description": "화면을 아래로 스크롤합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "times": {"type": "integer", "default": 3, "description": "스크롤 횟수"}
                }
            }
        },
        {
            "name": "appium_scroll_up",
            "description": "화면을 위로 스크롤합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "times": {"type": "integer", "default": 3}
                }
            }
        },

        # ── UI 탐색 ───────────────────────────────────────────
        {
            "name": "appium_get_page_source",
            "description": "현재 화면의 UI 계층 구조(XML)를 가져옵니다. 요소 탐색에 사용합니다.",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "appium_find_elements",
            "description": "strategy와 값으로 화면 요소를 검색합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "strategy": {
                        "type": "string",
                        "enum": ["accessibility_id", "xpath", "class_name", "id"],
                        "description": "탐색 전략"
                    },
                    "value": {"type": "string", "description": "탐색 값"}
                },
                "required": ["strategy", "value"]
            }
        },
        {
            "name": "appium_element_exists",
            "description": "accessibility_id로 요소 존재 여부를 확인합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "accessibility_id": {"type": "string"}
                },
                "required": ["accessibility_id"]
            }
        },

        # ── 앱 제어 ───────────────────────────────────────────
        {
            "name": "appium_launch_app",
            "description": "앱을 포그라운드로 실행/전환합니다.",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "appium_terminate_app",
            "description": "앱을 완전히 종료합니다.",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "appium_background_app",
            "description": "앱을 잠시 백그라운드로 보냅니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "default": 3}
                }
            }
        },
        {
            "name": "appium_get_window_size",
            "description": "현재 기기의 화면 크기를 반환합니다.",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "appium_type_text_by_xpath",
            "description": "XPath로 입력 필드를 찾아 텍스트를 입력합니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "xpath": {"type": "string"},
                    "text": {"type": "string"}
                },
                "required": ["xpath", "text"]
            }
        },
    ]


async def handle_tool_call(tool_name: str, args: dict, controller) -> str:
    """툴 이름에 따라 AppiumController 메서드 라우팅"""

    # ── 세션 ──────────────────────────────────────────────────
    if tool_name == "appium_connect":
        return controller.connect(
            args["platform"],
            args.get("bundle_id", None)
        )

    elif tool_name == "appium_switch_platform":
        return controller.switch_platform(args["platform"])

    elif tool_name == "appium_disconnect":
        return controller.disconnect(args.get("platform", None))

    elif tool_name == "appium_status":
        return controller.get_status()

    elif tool_name == "appium_type_text_by_xpath":
        return controller.type_text_by_xpath(
            args["xpath"],
            args["text"],
            args.get("timeout", 10)
        )

    # ── 스크린샷 ──────────────────────────────────────────────
    elif tool_name == "appium_screenshot":
        result = controller.screenshot()
        return json.dumps(result)

    # ── 탭 ───────────────────────────────────────────────────
    elif tool_name == "appium_tap":
        return controller.tap(args["x"], args["y"])

    elif tool_name == "appium_tap_by_accessibility_id":
        return controller.tap_by_accessibility_id(
            args["accessibility_id"],
            args.get("timeout", 10)
        )

    elif tool_name == "appium_tap_by_text":
        return controller.tap_by_text(
            args["text"],
            args.get("timeout", 10)
        )

    elif tool_name == "appium_tap_by_xpath":
        return controller.tap_by_xpath(
            args["xpath"],
            args.get("timeout", 10)
        )

    # ── 텍스트 입력 ───────────────────────────────────────────
    elif tool_name == "appium_type_text":
        return controller.type_text(
            args["accessibility_id"],
            args["text"],
            args.get("timeout", 10)
        )

    # ── 스와이프 / 스크롤 ─────────────────────────────────────
    elif tool_name == "appium_swipe":
        return controller.swipe(
            args["start_x"], args["start_y"],
            args["end_x"], args["end_y"],
            args.get("duration_ms", 500)
        )

    elif tool_name == "appium_scroll_down":
        return controller.scroll_down(args.get("times", 3))

    elif tool_name == "appium_scroll_up":
        return controller.scroll_up(args.get("times", 3))

    # ── UI 탐색 ───────────────────────────────────────────────
    elif tool_name == "appium_get_page_source":
        return controller.get_page_source()

    elif tool_name == "appium_find_elements":
        return controller.find_elements(args["strategy"], args["value"])

    elif tool_name == "appium_element_exists":
        return controller.element_exists(args["accessibility_id"])

    # ── 앱 제어 ───────────────────────────────────────────────
    elif tool_name == "appium_launch_app":
        return controller.launch_app()

    elif tool_name == "appium_terminate_app":
        return controller.terminate_app()

    elif tool_name == "appium_background_app":
        return controller.background_app(args.get("seconds", 3))

    elif tool_name == "appium_get_window_size":
        return controller.get_window_size()

    else:
        raise ValueError(f"Unknown tool: {tool_name}")