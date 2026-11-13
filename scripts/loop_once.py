import json
from app.llm import client
from app.tools import TOOL_SCHEMAS, TOOLS

MODEL = "deepseek-flash"

def ask(messages):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMAS,
    )

messages = [{"role": "user", "content": "读一下README.md，用一句话概括这个项目"}]

resp = ask(messages)
msg = resp.choices[0].message
messages.append(msg.model_dump(exclude_none=True))

if msg.tool_calls:
    for call in msg.tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments)
        print(f"[工具调用] {name}({args})")

        result = TOOLS[name](**args)
        print(f"[工具结果] {result[:200]}")

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": result,
        })
    resp = ask(messages)
    print("\n[最终回答]")
    print(resp.choices[0].message.content)
    print(f"{messages}")
else:
    print(msg.content)