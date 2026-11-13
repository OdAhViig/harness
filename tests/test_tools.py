"""工具层的边界测试：正常路径、越界路径、不存在路径。

pytest 的约定：test_ 开头的函数会被自动发现，不需要手写调用。
断言用 pytest.raises 检查「应该抛什么异常」。
"""

import json

import pytest

from app.tools import list_file, read_file


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
