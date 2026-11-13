import os

from collections.abc import Iterator
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

def stream_chat(messages: list[dict]) -> Iterator[str]:
    stream = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
