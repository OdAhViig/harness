"""手写 Agent loop：模型请求工具 → 本地执行 → 回填 → 继续，直到模型给最终回答或达到步数上限。

和 loop_once.py 的区别：loop_once 只硬编码了两轮；这里用 while 跑到模型自己停下来。
"""

import argparse
import json
from pathlib import Path

from app.events import EventLog, messages_from, new_log_path, pending_tool_calls
from app.llm import client
from app.permissions import confirm_write, ensure_safe_path
from app.tools import PATH_TOOLS, TOOL_SCHEMAS, TOOLS
from app.context import trim_messages, estimate_messages_tokens, CONTEXT_BUDGET

MODEL = "deepseek-flash"

# 每条用户提问独立计数：一次 run_agent 内最多 ask 多少次（= 最多产生几条 assistant 消息）。
# 一次 ask 只算一步，即使它带回多个 tool_calls；工具调用数不受这个值直接限制。
# 同一条提问 --resume 时接着累计，不重置。简单查询 3–5 足够，20 步任务给 20–25。
MAX_STEPS = 20

# 有副作用的工具：执行前必须过人工确认。
WRITE_TOOLS = {"write_file"}

SYSTEM_PROMPT = (
    "你是项目内的助手。需要信息时调用工具，不要编造。"
    "回答文档内容时先调用 search_docs，并在答案中标注来源（path:start_line）。"
)


def ask(messages):
    """发一次 Chat Completions 请求。注意这里是同步调用，不是 async。"""
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMAS,
    )


def to_message(msg):
    """把 SDK 返回的 message 对象转成可以写回 messages 的 dict。

    不用 msg.model_dump() 全量转：它会带上 reasoning_content 等 DeepSeek 私有字段，
    换供应商时可能 400。只保留协议规定的三个字段。
    """
    data = {"role": "assistant", "content": msg.content}
    if msg.tool_calls:
        data["tool_calls"] = [call.model_dump() for call in msg.tool_calls]
    return data


def run_tool(call):
    """执行一次工具调用，任何失败都转成文本返回，绝不把异常抛给 loop。

    返回的字符串会作为 role=tool 的 content 回给模型，模型据此决定下一步。
    """
    name = call.function.name
    print(f"[工具调用] {name}({call.function.arguments})")

    args = None
    error = None
    try:
        args = json.loads(call.function.arguments)
    except Exception as e:
        error = str(e)
    if error is not None:
        print(f"[工具结果] {str(error)[:200]}")
        return error

    try:
        if name in PATH_TOOLS:
            ensure_safe_path(args["path"])
        if name == "write_file":
            if confirm_write(**args):
                result = TOOLS[name](**args)
            else:
                result = "用户拒绝写入（人工确认未通过），未做任何修改"
        else:
            result = TOOLS[name](**args)
    except PermissionError as e:
        result = f"错误：{e}"
    except ValueError as e:
        result = f"错误：{e}"
    except KeyError as e:
        result = f"错误：{e}"
    except TypeError as e:
        result = f"错误：{e}"

    print(f"[工具结果] {str(result)[:200]}")
    return str(result)


def run_agent(messages, log, steps=0):
    """主循环。steps 是这条用户提问已用的 ask 次数；> 0 表示从日志恢复，预算接着累计。"""
    while 1:
        if steps >= MAX_STEPS:
            print(f"超过模型调用上限（MAX_STEPS={MAX_STEPS}），停止")
            log.append({"type": "limit", "steps": steps})
            return
        steps += 1
        msg_tokens = estimate_messages_tokens(messages)
        trimed_msgs = None
        if msg_tokens > CONTEXT_BUDGET:
            trimed_msgs = trim_messages(messages)
            trimed_msg_tokens = estimate_messages_tokens(trimed_msgs)
            log.append({"type": "context", "before": msg_tokens, "after": trimed_msg_tokens})
        resp = ask(trimed_msgs if trimed_msgs is not None else messages)
        msg = resp.choices[0].message
        record = to_message(msg)
        messages.append(record)
        event = {"type": "assistant", "content": record["content"]}
        if record.get("tool_calls"):
            event["tool_calls"] = record["tool_calls"]
        log.append(event)
        if msg.tool_calls:
            for call in msg.tool_calls:
                res = run_tool(call)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": res})
                log.append({"type": "tool", "name": call.function.name, "tool_call_id": call.id, "content": res})
        else:
            print(f"{msg.content}")
            log.append({"type": "done", "steps": steps})
            return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=Path, help="从已有 JSONL 日志恢复")
    parser.add_argument("--log", type=Path, help="新会话日志路径")
    parser.add_argument("--task", help="新会话的用户消息；不传则用内置验收任务")
    args = parser.parse_args()

    if args.resume:
        log = EventLog(args.resume)
        events = EventLog.load(args.resume)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_from(events)
        waitingCalls = pending_tool_calls(messages)
        for call in waitingCalls:
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": "上次执行被中断，结果未知。不要重复执行有副作用的操作。"})
            log.append({"type": "tool", "name": call["function"]["name"], "tool_call_id": call["id"], "content": "上次执行被中断，结果未知。不要重复执行有副作用的操作。"})
        steps = len([msg for msg in messages if msg["role"] == "assistant"])
        print(f"[恢复] {args.resume}：{len(events)} 条事件，已完成 {steps} 步")
    else:
        path = args.log or new_log_path()
        log = EventLog(path)
        user = args.task or "读取 README.md，在末尾追加一行 `<!-- write_file 验收 -->`，保持原有内容不变，然后写回 README.md"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ]
        log.append({"type": "user", "content": user})
        steps = 0
        print(f"[日志] {path}")

    try:
        run_agent(messages, log, steps)
    except KeyboardInterrupt:
        log.append({"type": "interrupted"})
        print(f"\n已中断。恢复：.venv/bin/python -m scripts.agent_loop --resume {log.path}")


if __name__ == "__main__":
    main()
