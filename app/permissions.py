"""权限层：工具执行前的最后一道闸。

三层各管一件事：
1. 路径守卫：resolve 后必须留在项目根目录内，防逃逸
2. 敏感名单：.env / .git / .venv 一律拒绝，防密钥泄漏与仓库损坏
3. 人工确认：上面两层通过后，写操作再问一次，防「合法但非本意」的修改
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 路径里任意一段命中就拒绝。注意 ".env.example" 不在名单里，允许编辑。
DENY_PARTS = {".env", ".git", ".venv"}


def ensure_safe_path(path: str) -> Path:
    """把相对路径转成绝对路径，并校验没有逃出项目根目录、不是敏感路径。

    通过时返回 Path；不通过抛 PermissionError，调用方决定怎么提示。
    """
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT):
        raise PermissionError(f"路径越界：{path}")
    for part in target.relative_to(ROOT).parts:
        if part in DENY_PARTS:
            raise PermissionError(f"敏感路径：{path}")
    return target

def confirm_write(path: str, content: str) -> bool:
    """写操作的人工确认，返回 True 才允许执行。

    非交互环境（pytest）里 input() 会抛 EOFError，测试要用 monkeypatch 替换。
    """
    print(f"{content[:100]}")
    res = write_input(path)
    if res == "y" or res == "Y":
        return True
    return False


def write_input(path) -> str:
    return input(f"允许写入 {path}？[y/N] ")