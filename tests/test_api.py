import pytest
from fastapi.testclient import TestClient

from app import main

@pytest.fixture
def client():
    return TestClient(main.app)

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

def test_chat_echo(client):
    resp = client.get("/chat", params={"q": "你好"})
    assert resp.json() == {"message": "你说了：你好"}

def test_chat_stream(client, monkeypatch):
    def fake_stream(messages):
        assert messages == [{"role": "user", "content": "测试"}]
        yield "你"
        yield "好"

    monkeypatch.setattr(main, "stream_chat", fake_stream)

    resp = client.get("/chat/stream", params={"q": "测试"})
    assert resp.status_code == 200
    assert resp.text == "你好"