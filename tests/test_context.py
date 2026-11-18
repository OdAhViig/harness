"""上下文裁剪的规格测试：估算、预算内不动、超预算按单元丢弃、tool 配对、工具结果截断。

约定：测试里用很小的 budget（几十到几千字符），让用例一眼能算出预期结果，
不依赖 CONTEXT_BUDGET 的具体取值。
"""

import copy

from app.context import (
    TOOL_RESULT_LIMIT,
    estimate_messages_tokens,
    estimate_tokens,
    trim_messages,
)


def tool_call(call_id="c1"):
    """构造一个最小 tool_call；id 是配对断言的关键。"""
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": "read_file", "arguments": "{}"},
    }


def tool_msg(call_id="c1", content="ok"):
    return {"role": "tool", "tool_call_id": call_id, "content": content}


def assistant_call(call_id="c1", content=None):
    return {"role": "assistant", "content": content, "tool_calls": [tool_call(call_id)]}


def test_estimate_tokens_treats_none_as_zero():
    """content=None 是带 tool_calls 的 assistant 的常态：不能崩，也不能按字面量 'None' 计数。"""
    with_none = {"role": "assistant", "content": None, "tool_calls": [tool_call()]}
    with_empty = {"role": "assistant", "content": "", "tool_calls": [tool_call()]}

    assert estimate_tokens(None) == 0
    assert estimate_messages_tokens([with_none]) == estimate_messages_tokens([with_empty])
    assert estimate_messages_tokens([with_none]) > 0


def test_under_budget_keeps_every_message():
    """预算足够时原样返回：不截断、不删减、顺序不变。"""
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
    ]

    result = trim_messages(messages, budget=1000)

    assert result == messages


def test_exactly_at_budget_keeps_every_message():
    """边界：总量等于预算不算超，不能触发裁剪。"""
    messages = [
        {"role": "system", "content": "S" * 50},
        {"role": "user", "content": "U" * 50},
    ]

    result = trim_messages(messages, budget=100)

    assert len(result) == 2


def test_over_budget_drops_oldest_assistant_unit():
    """超预算时从最旧开始丢整轮，system 与首条 user（任务）必须留下。"""
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        {"role": "assistant", "content": "OLD" * 50},
        {"role": "assistant", "content": "NEW"},
    ]

    result = trim_messages(messages, budget=30)

    assert [m["role"] for m in result] == ["system", "user", "assistant"]
    assert result[1]["content"] == "TASK"
    assert result[2]["content"] == "NEW"


def test_tool_unit_is_kept_or_dropped_as_a_whole():
    """assistant(tool_calls) 与 tool 结果同进退：不能只剩一半，否则请求违反协议。"""
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        assistant_call("c1"),
        tool_msg("c1", "x" * 1000),
        assistant_call("c2"),
        tool_msg("c2", "ok"),
    ]

    result = trim_messages(messages, budget=250)

    tool_ids = [m["tool_call_id"] for m in result if m["role"] == "tool"]
    call_ids = [call["id"] for m in result if m["role"] == "assistant" for call in m["tool_calls"]]
    assert tool_ids == call_ids
    assert "c1" not in tool_ids


def test_huge_tool_result_is_truncated_to_limit():
    """单条工具结果吃满预算时，先截断它，而不是丢掉整轮。"""
    big = "x" * 30000
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        assistant_call("c1"),
        tool_msg("c1", big),
    ]

    result = trim_messages(messages, budget=5000)

    tool_out = [m for m in result if m["role"] == "tool"][0]
    assert "已截断" in tool_out["content"]
    assert len(tool_out["content"]) <= TOOL_RESULT_LIMIT + 100
    assert estimate_messages_tokens(result) <= 5000


def test_tool_result_untouched_when_within_budget():
    """预算没超时不做任何截断：2000 字符上限是保险丝，不是常态处理。"""
    content = "x" * 3000
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        assistant_call("c1"),
        tool_msg("c1", content),
    ]

    result = trim_messages(messages, budget=10000)

    assert [m for m in result if m["role"] == "tool"][0]["content"] == content


def test_system_and_task_alone_over_budget_returns_only_them():
    """极端情况：光 system + 首条 user 就超预算，只返回这两条，不抛异常。"""
    messages = [
        {"role": "system", "content": "S" * 60},
        {"role": "user", "content": "U" * 60},
    ]

    result = trim_messages(messages, budget=100)

    assert [m["role"] for m in result] == ["system", "user"]


def test_multiple_tool_calls_in_one_unit_stay_together():
    """一次 ask 带多个 tool_call 时，整个单元一起保留，所有 id 都要有回填。"""
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [tool_call("c1"), tool_call("c2")],
        },
        tool_msg("c1", "x" * 30000),
        tool_msg("c2", "ok"),
    ]

    result = trim_messages(messages, budget=5000)

    tool_ids = {m["tool_call_id"] for m in result if m["role"] == "tool"}
    assert tool_ids == {"c1", "c2"}


def test_truncation_landing_exactly_on_budget_keeps_the_unit():
    """边界：截断后恰好等于预算也算达标，不能再白丢一整轮。"""
    big = "x" * 3000
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        assistant_call("c1"),
        tool_msg("c1", big),
    ]
    exact_budget = estimate_messages_tokens(messages) - (len(big) - TOOL_RESULT_LIMIT)

    result = trim_messages(messages, budget=exact_budget)

    assert [m["role"] for m in result] == ["system", "user", "assistant", "tool"]
    assert "已截断" in result[-1]["content"]


def test_later_user_messages_are_droppable_units():
    """多轮对话里，首条 user 保留，后续 user 与普通轮次一样可被丢弃，且不能死循环。"""
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        {"role": "user", "content": "OLD" * 50},
        {"role": "assistant", "content": "NEW"},
    ]

    result = trim_messages(messages, budget=30)

    assert [m["role"] for m in result] == ["system", "user", "assistant"]
    assert result[1]["content"] == "TASK"
    assert all(m.get("content") != "OLD" * 50 for m in result)


def test_input_messages_are_not_mutated():
    """trim_messages 是纯函数：loop 里的 messages 还要继续 append 全量历史，不能被改写。"""
    messages = [
        {"role": "system", "content": "S" * 10},
        {"role": "user", "content": "TASK"},
        assistant_call("c1"),
        tool_msg("c1", "x" * 30000),
    ]
    snapshot = copy.deepcopy(messages)

    trim_messages(messages, budget=5000)

    assert messages == snapshot
