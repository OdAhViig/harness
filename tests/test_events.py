"""事件日志的边界测试：写入回环、半行容错、消息还原、pending 检测。"""

from app.events import EventLog, messages_from, pending_tool_calls


def test_append_load_roundtrip(tmp_path):
    """写两条事件再读回来，数量和内容一致，且每条都有时间戳。"""
    log = EventLog(tmp_path / "events.jsonl")
    log.append({"type": "user", "content": "hi"})
    log.append({"type": "done"})

    events = EventLog.load(log.path)

    assert len(events) == 2
    assert events[0]["content"] == "hi"
    assert all("ts" in event for event in events)


def test_load_skips_torn_line(tmp_path):
    """模拟 kill -9 留下的半行 JSON：前面的完整事件仍能读出。"""
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"type": "user", "content": "hi"}\n'
        '{"type": "assistant", "content": "yo"}\n'
        '{"type": "assistant", "content": \n',
        encoding="utf-8",
    )

    events = EventLog.load(path)

    assert len(events) == 2


def test_messages_from_roundtrip():
    """事件流还原成 messages：role 顺序正确，done 等控制事件被忽略。"""
    events = [
        {"type": "user", "content": "q"},
        {
            "type": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "c1",
                    "type": "function",
                    "function": {"name": "read_file", "arguments": "{}"},
                }
            ],
        },
        {"type": "tool", "tool_call_id": "c1", "name": "read_file", "content": "ok"},
        {"type": "done", "steps": 1},
    ]

    messages = messages_from(events)

    assert len(messages) == 3
    assert [m["role"] for m in messages] == ["user", "assistant", "tool"]
    assert messages[2]["tool_call_id"] == "c1"


def test_messages_from_text_only_assistant():
    """纯文本回答没有 tool_calls 键：不能抛 KeyError，也不能写出 None 字段。"""
    events = [
        {"type": "user", "content": "q"},
        {"type": "assistant", "content": "答完了"},
        {"type": "done", "steps": 1},
    ]

    messages = messages_from(events)

    assert len(messages) == 2
    assert messages[1]["content"] == "答完了"
    assert "tool_calls" not in messages[1]


def test_pending_tool_calls():
    """assistant 请求了两个工具，只回填了一个：应只返回缺的那个。"""
    messages = [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "c1",
                    "type": "function",
                    "function": {"name": "read_file", "arguments": "{}"},
                },
                {
                    "id": "c2",
                    "type": "function",
                    "function": {"name": "write_file", "arguments": "{}"},
                },
            ],
        },
        {"role": "tool", "tool_call_id": "c1", "content": "ok"},
    ]

    pending = pending_tool_calls(messages)

    assert [call["id"] for call in pending] == ["c2"]
