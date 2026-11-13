from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.llm import stream_chat

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health() -> dict:
    return {"ok": True}

@app.get("/chat")
async def chat(q: str = "你好") -> dict:
    return {"message": f"你说了：{q}"}

@app.get("/echo")
async def echo(msg: str) -> dict:
    return {"echo": msg}

@app.get("/chat/stream")
async def chat_stream(q: str):
    def generate():
        yield from stream_chat(
            messages=[
                {"role": "user", "content": q}
            ]
        )
    return StreamingResponse(content=generate(), media_type="text/plain")