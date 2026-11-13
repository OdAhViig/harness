import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.llm import stream_chat

result = stream_chat(
    messages=[
        {"role": "user", "content": "用三句话解释什么是上下文工程。"}
    ]
)

for chunk in result:
    print(f"{chunk}", end="", flush=True)