# harness

DeepSeek 客户端与 Agent 实验工程。

## 环境

- Python 3.12
- 依赖见 `requirements.txt`

## 快速开始

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # 填入 DEEPSEEK_API_KEY
uvicorn app.main:app --reload --port 8000
```

浏览器打开 <http://127.0.0.1:8000/static/index.html>，输入问题点发送，回答逐字出现。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查 |
| GET | `/chat?q=` | 回显，非流式 |
| GET | `/echo?msg=` | 原样返回参数 |
| GET | `/chat/stream?q=` | DeepSeek 流式回答，`text/plain` + chunked |

## 目录

```
app/       FastAPI 应用与 LLM 客户端封装
scripts/   一次性验证脚本
static/    前端页面
```

## 说明

- API key 只从环境变量读取，不硬编码、不进仓库
- 流式接口不设 `content-length`，走 `transfer-encoding: chunked`
