#!/usr/bin/env python3
"""
Appium MCP Server
Claude Desktop에서 iOS/Android 실기기를 직접 제어하기 위한 MCP 서버
"""

import asyncio
import json
import sys
import logging
from typing import Any

from src.appium_controller import AppiumController
from src.tools import get_tool_definitions, handle_tool_call

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


async def read_message(reader: asyncio.StreamReader) -> dict | None:
    """stdin에서 JSON-RPC 메시지 읽기"""
    try:
        line = await reader.readline()
        if not line:
            return None
        return json.loads(line.decode().strip())
    except Exception as e:
        logger.error(f"Failed to read message: {e}")
        return None


def write_message(message: dict):
    """stdout으로 JSON-RPC 메시지 전송"""
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def make_response(req_id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


async def main():
    controller = AppiumController()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    logger.info("Appium MCP Server started")

    while True:
        message = await read_message(reader)
        if message is None:
            break

        method = message.get("method")
        req_id = message.get("id")
        params = message.get("params", {})

        try:
            if method == "initialize":
                write_message(make_response(req_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "appium-mcp", "version": "1.0.0"}
                }))

            elif method == "tools/list":
                write_message(make_response(req_id, {
                    "tools": get_tool_definitions()
                }))

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = await handle_tool_call(tool_name, tool_args, controller)

                try:
                    parsed = json.loads(result)
                    if isinstance(parsed, dict) and parsed.get("type") == "image":
                        content = [{
                            "type": "image",
                            "data": parsed["data"],
                            "mimeType": parsed["mediaType"]
                        }]
                    else:
                        content = [{"type": "text", "text": result}]
                except (json.JSONDecodeError, TypeError):
                    content = [{"type": "text", "text": result}]

                write_message(make_response(req_id, {"content": content}))

            elif method == "notifications/initialized":
                pass  # 응답 불필요

            else:
                if req_id is not None:
                    write_message(make_error(req_id, -32601, f"Method not found: {method}"))

        except Exception as e:
            logger.error(f"Error handling {method}: {e}")
            if req_id is not None:
                write_message(make_error(req_id, -32603, str(e)))


if __name__ == "__main__":
    asyncio.run(main())
