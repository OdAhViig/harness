"""手写 Agent loop：模型请求工具 → 本地执行 → 回填 → 继续，直到模型给最终回答或达到步数上限。

和 loop_once.py 的区别：loop_once 只硬编码了两轮；这里用 while 跑到模型自己停下来。
"""

import json
from app.llm import client
from app.permissions import confirm_write, ensure_safe_path
from app.tools import TOOL_SCHEMAS, TOOLS

MODEL = "deepseek-flash"

# 一次用户请求内最多允许的模型调用轮数。简单查询 3–5 足够，20 步任务给 20–25。
MAX_STEPS = 8

# 有副作用的工具：执行前必须过人工确认。
WRITE_TOOLS = {"write_file"}

SYSTEM_PROMPT = "你是项目内的助手。需要信息时调用工具，不要编造。"


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


def run_agent(messages):
    """主循环：反复问模型、执行工具、回填，直到拿到最终回答或用完步数。"""
    steps = 0
    while 1:
        if steps >= MAX_STEPS:
            print(f"超过最大循环次数{MAX_STEPS}")
            return
        steps += 1
        resp = ask(messages)
        msg = resp.choices[0].message
        messages.append(to_message(msg))
        if msg.tool_calls:
            for call in msg.tool_calls:
                res = run_tool(call)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": res})
        else:
            print(f"{msg.content}")
            return

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "读取 README.md，在末尾追加一行 `<!-- write_file 验收 -->`，保持原有内容不变，然后写回 README.md",
        },
    ]
    run_agent(messages)
