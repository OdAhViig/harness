"""JSONL 事件日志：一行一个事件，用于回放、排查和 kill 后恢复。

为什么用 JSONL 而不是一个大 JSON 数组：
- 追加写不需要读回整个文件
- 进程被杀时最多损坏最后一行，前面的事件仍然可读
- 每一行独立可解析，方便 grep / jq
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"


def new_log_path() -> Path:
    """每次新会话一个文件，避免不同会话的事件混在一起。"""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return LOG_DIR / f"agent-{stamp}.jsonl"


class EventLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict) -> None:
        """追加一条事件，自动补时间戳。"""
        event = {**event, "ts": datetime.now(timezone.utc).isoformat()}
        with open(self.path, "a", encoding="utf-8") as f:
            event_str = json.dumps(event, ensure_ascii=False)
            f.write(f"{event_str}\n")

    @staticmethod
    def load(path: Path) -> list[dict]:
        """读回全部事件。跳过空行和 JSON 解析失败的行（硬杀留下的半行）。"""
        res = []
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    dic = json.loads(line.strip())
                    res.append(dic)
                except json.JSONDecodeError:
                    continue
        return res


def messages_from(events: list[dict]) -> list[dict]:
    """把事件流还原成 Chat Completions 的 messages。

    只认识 type 为 user / assistant / tool 的事件；done、interrupted 等控制事件忽略。
    """
    res = []
    for event in events:
        if event["type"] == "user":
            msg = {"role": event["type"], "content": event["content"]}
            res.append(msg)
        elif event["type"] == "assistant":
            msg = {"role": event["type"], "content": event["content"]}
            if event.get("tool_calls"):
                msg["tool_calls"] = event["tool_calls"]
            res.append(msg)
        elif event["type"] == "tool":
            msg = {"role": event["type"], "tool_call_id": event["tool_call_id"], "content": event["content"]}
            res.append(msg)
    return res


def pending_tool_calls(messages: list[dict]) -> list[dict]:
    """返回「模型请求了、但没有对应 tool 结果」的调用。

    进程在工具执行中途被杀时会出现这种状态。恢复时不自动重放：
    写操作可能已经落盘，重放会造成重复副作用。调用方应把「结果未知」回填给模型。
    """
    answered = {m["tool_call_id"] for m in messages if m.get("role") == "tool"}
    pending = []
    for m in messages:
        if m.get("role") == "assistant":
            for call in m.get("tool_calls") or []:
                if call["id"] not in answered:
                    pending.append(call)
    return pending
