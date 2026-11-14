import os
import json
from pathlib import Path

from app.permissions import ensure_safe_path

ROOT = Path(__file__).resolve().parent.parent

def read_file(path: str) -> str:
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f"错误：路径越界 {path}")
    if not target.is_file():
        raise ValueError(f"错误：文件不存在 {path}")
    return target.read_text(encoding="utf-8")

def list_file(path: str) -> str:
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f"错误：路径越界 {path}")
    if target.is_file():
        raise ValueError(f"错误：路径不是目录 {path}")
    return json.dumps(os.listdir(target))

def write_file(path: str, content: str) -> str:
    """写入项目内的文本文件，会覆盖原内容。

    路径守卫交给 permissions.ensure_safe_path，写之前的人工确认在 run_tool 里做。
    """
    target = ensure_safe_path(path)
    if target.exists() and target.is_dir():
        raise ValueError(f"错误：路径是目录 {path}")
    if not target.parent.is_dir():
        raise ValueError(f"错误：父目录不存在 {path}")
    target.write_text(content, encoding="utf-8")
    return f"已写入 {path}（{len(content)} 字符）"

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取项目内的文本文件，返回文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "相对于项目根目录的文件路径",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_file",
            "description": "读取目录内的文件，返回文件列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "相对于项目根目录的目录路径",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入项目内的文本文件，会覆盖原内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "相对于项目根目录的文件路径",
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的完整文本",
                    },
                },
                "required": ["path", "content"],
            },
        },
    }
]

TOOLS = {
    "read_file": read_file,
    "list_file": list_file,
    "write_file": write_file,
}