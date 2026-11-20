import os
import json
from pathlib import Path

from app.permissions import ensure_safe_path
from app.rag import chunk_all, load_documents
from app.retrieval import build_index, search

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

# 进程内缓存：文档不变就复用索引，避免每次工具调用重新切分、分词。
_INDEX = None


def _get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = build_index(chunk_all(load_documents()))
    return _INDEX


def search_docs(query: str, top_k: int = 5) -> str:
    """在 sandbox/docs 中做 BM25 检索，返回 JSON 字符串；每条带 path / 行号 / 原文 / 分数。"""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query 不能为空")
    top_k = max(1, min(int(top_k), 10))
    results = search(_get_index(), query, top_k=top_k)
    return json.dumps(results, ensure_ascii=False)

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
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "在项目文档中按关键词检索，返回最相关的片段及 path:line 引用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "检索关键词或问题",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回片段数，默认 5，最多 10",
                    },
                },
                "required": ["query"],
            },
        },
    }
]

# 这些工具的第一个参数是项目内路径，执行前要过路径守卫。
PATH_TOOLS = {"read_file", "list_file", "write_file"}

TOOLS = {
    "read_file": read_file,
    "list_file": list_file,
    "write_file": write_file,
    "search_docs": search_docs,
}