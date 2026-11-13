import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

start = time.time()
first = None
reply = None
thinking = False
responding = False

stream = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "user", "content": "用三句话解释什么是上下文工程。"},
    ],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    reasoning = getattr(delta, "reasoning_content", None)
    if reasoning:
        if first is None:
            first = time.time() - start
        if not thinking:
            thinking = True
            print("思考：")
        print(f"\033[36m{reasoning}\033[0m", end="", flush = True)
    if delta.content:
        if reply is None:
            reply = time.time() - start
        if not responding:
            responding = True
            print()
            print("回答：")
        print(f"{delta.content}", end="", flush=True)

print()
if first is None:
    print("未收到内容")
else:
    reply_time = reply if reply is not None else time.time() - start
    print(f"首 token 延迟：{first: 0.2f}s，思考耗时：{(reply_time - first): 0.2f}s，总耗时：{(time.time() - start): 0.2f}s")