from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def read_file(path: str) -> str:
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT):
        return f"错误：路径越界 {path}"
    if not target.is_file():
        return f"错误：文件不存在 {path}"
    return target.read_text(encoding="utf-8")

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
    }
]

TOOLS = {"read_file": read_file}