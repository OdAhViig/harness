"""工具层的边界测试：正常路径、越界路径、不存在路径。

pytest 的约定：test_ 开头的函数会被自动发现，不需要手写调用。
断言用 pytest.raises 检查「应该抛什么异常」。
"""

import json

import pytest

from app import permissions
from app import tools
from app.permissions import confirm_write
from app.retrieval import build_index
from app.tools import list_file, read_file, write_file


def test_list_file_ok():
    """正常目录：列项目根目录，返回的 JSON 里应同时包含目录和文件。"""
    result = json.loads(list_file("."))
    assert "app" in result
    assert "README.md" in result


def test_list_file_out_of_root():
    """越界路径：父目录应该被拒绝，而不是把 .venv 之外的内容列出来。"""
    with pytest.raises(ValueError, match="越界"):
        list_file("..")


def test_read_file_missing():
    """不存在的文件：返回明确错误，而不是抛 FileNotFoundError 让调用方猜。"""
    with pytest.raises(ValueError, match="不存在"):
        read_file("no_such_file.txt")


def test_write_file_ok(tmp_path, monkeypatch):
    """正常写入：把 permissions.ROOT 指到临时目录，写完再读回来。

    参数 tmp_path 和 monkeypatch 都是 pytest 自动注入的 fixture，不用手写。
    """
    monkeypatch.setattr(permissions, "ROOT", tmp_path)
    monkeypatch.setattr(tools, "ROOT", tmp_path)
    write_file("note.txt", "hello")
    assert read_file("note.txt") == "hello"


def test_write_out_of_root():
    """越界写入：不能写到项目根目录之外。"""
    with pytest.raises(PermissionError, match="越界"):
        write_file("../hack.txt", "x")


def test_write_sensitive(tmp_path, monkeypatch):
    """敏感路径：.env 里是 API key，模型不能碰。"""
    monkeypatch.setattr(permissions, "ROOT", tmp_path)
    with pytest.raises(PermissionError, match="敏感"):
        write_file(".env", "SECRET=1")


def test_confirm_write(monkeypatch):
    """人工确认：y 放行，n 拒绝。"""
    def fake_input(path) -> str:
        return "y"
    monkeypatch.setattr(permissions, "write_input", fake_input)
    assert confirm_write("", "")
    monkeypatch.setattr(permissions, "write_input", lambda _: "n")
    assert confirm_write("", "") is False
    # TODO 8：monkeypatch 替换 builtins.input，
    # 先返回 "y" 断言 confirm_write(...) is True，再返回 "n" 断言 is False。


def test_search_docs_returns_citation_json(monkeypatch):
    """检索结果转成 JSON，保留 path / 行号 / 原文 / 分数。"""
    index = build_index([
        {
            "id": "c1",
            "path": "sandbox/docs/a.md",
            "start_line": 3,
            "end_line": 5,
            "text": "apple",
        },
    ])
    monkeypatch.setattr(tools, "_INDEX", index)

    payload = json.loads(tools.search_docs("apple"))

    assert payload[0]["path"] == "sandbox/docs/a.md"
    assert payload[0]["start_line"] == 3
    assert payload[0]["end_line"] == 5
    assert payload[0]["text"] == "apple"
    assert payload[0]["score"] > 0


def test_search_docs_rejects_empty_query(monkeypatch):
    monkeypatch.setattr(tools, "_INDEX", build_index([]))

    with pytest.raises(ValueError, match="不能为空"):
        tools.search_docs("   ")


def test_search_docs_clamps_top_k(monkeypatch):
    chunks = [
        {
            "id": f"c{i}",
            "path": "sandbox/docs/a.md",
            "start_line": 1,
            "end_line": 1,
            "text": "apple",
        }
        for i in range(3)
    ]
    monkeypatch.setattr(tools, "_INDEX", build_index(chunks))

    # top_k 上限是 10，这里只有 3 条命中
    assert len(json.loads(tools.search_docs("apple", top_k=100))) == 3


def test_search_docs_is_not_a_path_tool():
    """search_docs 没有 path 参数，不能无条件走路径守卫。"""
    assert "search_docs" not in tools.PATH_TOOLS
