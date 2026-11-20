# AI Agent 学习进度

> 配套计划：[`AI-Agent全职6周冲刺计划.md`](AI-Agent全职6周冲刺计划.md)
> 疑问归档：[`AI-Agent疑问解答.md`](AI-Agent疑问解答.md)（概念问题的答案都收在这里）
> 用法：每天开始学习时说「继续 Agent 学习」或「今天做什么」，我读这份文件和冲刺计划，按实际进度生成当天任务并追加到下面。
> 原则：只排当天；未完成不自动顺延；周五验收。

---

## 当前状态

| 项 | 值 |
|---|---|
| 当前进度 | **8/37** |
| 当前里程碑 | M3 上下文工程 + RAG（第三块完成，3/5 天） |
| 累计学习 | 8 个工作日 |
| 已完成里程碑 | M1、M2 |
| 上次卡点 | 评测脚本缩进层级：入口判断写进 `main` 内部、字段校验写进 `for key` 循环 |
| 下次入口 | M3 第四块：agent 端到端 30 条引用准确率（复用现有评测集） |

---

## 里程碑进度

| # | 里程碑 | 预算 | 已用 | 状态 | 验收证据 |
|---|---|---|---|---|---|
| M1 | Python 工程化 + DeepSeek 接入 | 7 天 | 2 | 完成 | Python 3.12.10；FastAPI `/health` `/chat` `/echo` `/chat/stream`；流式 curl + 浏览器逐字显示；依赖固化 + README；pytest 3 passed；github.com/OdAhViig/harness |
| M2 | 手写 loop + 工具 + 权限 + 事件日志 | 6 天 | 3 | 完成 | 工具注册表 + 越界/敏感路径拒绝（7 passed）；`MAX_STEPS` 截断；`write_file` 三层权限；JSONL 事件日志 + kill/resume（15 passed）；20 步多跳任务 19 次读取 + 最终回答，`done steps=20` |
| M3 | 上下文工程 + RAG | 5 天 | 3 | 进行中 | 第一块：`app/context.py` 单元化裁剪 + 12 条测试（27 passed）；31499 字符工具结果触发一次裁剪，`before=31752` → `after=2271`。第二块：`app/retrieval.py` BM25 + 26 条测试（71 passed）；真实语料 185 块，agent 检索问答带 `path:line` 引用。第三块：30 条评测集 + `scripts/eval_retrieval.py` + 26 条测试（全量 97 passed）；strict recall@1/3/5 0.900/0.967/1.000、MRR@5 0.934，loose 0.933/1.000/1.000/0.961 |
| M4 | LangGraph + 评测 | 5 天 | 0 | 未开始 | — |
| M5 | MCP + 可靠性 | 4 天 | 0 | 未开始 | — |
| M6 | 毕业项目 + 面试材料 | 5 天 | 0 | 未开始 | — |

---

## 2026-11-12（周四）· M1 · 1/37

**今天可用**：5h
**昨日遗留**：无
**已确认环境**：python3.12 未装、项目目录不存在、`DEEPSEEK_API_KEY` 未设置

**今日任务**（按优先级，每项 1–1.5h）

1. [x] **装 Python 3.12 + 建项目骨架**（1h）
   - 下载 `python-3.12.10-macos11.pkg` 并安装（需管理员密码）
   - `python3.12 -m venv /Users/finlaas/my/deepseek-harness/.venv`
   - 激活后装 `openai fastapi uvicorn pydantic`
   - 验收：`python3.12 --version` 输出 3.12.x；`pip list` 能看到四个包

2. [x] **FastAPI 两个接口（示范-模仿）**（1.5h）
   - 我给带逐行注释的示例：`/health` 和 `/chat`
   - 你跑通后改 3 处：加 `/echo` 路由、改返回字段、把固定文本改成回显请求参数
   - 验收：能不看代码复述请求进来后的处理流程

3. [x] **DeepSeek 非流式（读 + 改）**（1h）
   - 配置 `DEEPSEEK_API_KEY`，我给示例；你改模型名、system prompt、temperature 各一次
   - 验收：能解释 `messages`、`usage`、`choices[0].message.content` 分别是什么

4. [x] **DeepSeek 流式（读 + 改）**（1.5h）
   - 我给示例；你改打印格式，把 `reasoning_content` 和 `content` 分标签输出
   - 验收：能说清一个 chunk 里有哪些字段；有首 token 延迟数字

**今日验收**：`python3.12 --version` 是 3.12.x；`/health`、`/chat`、`/echo` 可访问；DeepSeek 非流式与流式各成功一次；能解释今天用到的 Python 语法（函数、字典、`async def`、`await`）。

**风险**：API key 需要你提供；旧机装 pkg 需要管理员权限；流式 thinking 内容与正式内容混在一起，先分开打印。

**时间不够时的砍单顺序**：先保 1–3，任务 4 顺延到明天；但 1 当天必须完成，否则后面全部阻塞。

---

## 每日记录

### 2026-11-20 · M3 第三块（检索评测完成）· 8/37

**模式**：用户写实现（照抄骨架 + 自己排查缩进 bug），Claude 起草评测集与测试

**今日任务**
1. [x] 30 条评测集 `eval/retrieval_questions.jsonl`（5 文档各 6 条；direct 10 / paraphrase 10 / multi_term 5 / distractor 5）
2. [x] 用户抽检 5 条（id 2、11、16、23、30）通过
3. [x] `scripts/eval_retrieval.py`：加载校验 → 建索引 → 逐题 `search` → 严格/宽松命中 → recall@1/3/5 + MRR@5 → 报告
4. [x] `tests/test_eval_retrieval.py` 26 条（Claude 写）

**验收证据**
- `pytest -q tests/` → 97 passed（新增 26）
- `python -m scripts.eval_retrieval` → 204 块 / 30 条
- strict recall@1 0.900 / @3 0.967 / @5 1.000，MRR@5 0.934
- loose recall@1 0.933 / @3 1.000 / @5 1.000，MRR@5 0.961
- 严格口径 Top-5 全部命中

**发现的问题**
- `if __name__ == "__main__"` 被缩进进 `main()` 内部 → 运行零输出、退出码 0
- 字段校验与 id 去重被缩进进 `for key` 循环 → 第二轮 key 检查时报「第 1 行 id 重复」
- `search()` 返回 `sandbox/docs/X.md`，评测集只存 `X.md` → 判定前必须取 basename，否则全不命中
- `difficulty` 是可选字段，`evaluate` 直接下标访问会 KeyError，改用 `.get`
- `sandbox/docs` 的疑问解答副本落后源文档 170 行，已同步；id 23 行号 1839–1869 → 1878–1908

**下一块**
- M3 第四块：agent 端到端 30 条引用准确率
- 复用同一评测集，让 agent 真跑问题，统计回答引用是否命中 ground truth
- 待定：是否补更难的 paraphrase 题提升区分度

### 2026-11-20 · M3 第二块（检索完成）

**模式**：用户写思路与初版，Claude 完成实现与测试（用户指令「剩下的你来写吧」）

**今日任务**
1. [x] `app/retrieval.py`：tokenize（英文整词 + 中文 bigram）+ build_index（倒排、doc_len、N/avgdl）+ search（BM25、query 去重、同分按 id）
2. [x] `tests/test_retrieval.py` 26 条（Claude 写）
3. [x] `search_docs` 工具注册 + agent 一次带 `path:line` 引用的问答实测

**验收证据**
- `pytest -q tests/test_retrieval.py` → 26 passed；全量 `pytest -q tests/` → 71 passed
- 真实语料：185 块 / N=185 / avgdl=212.81 / 词表 11195；查询「BM25 k1 b 词频饱和」top-1 命中 `AI-Agent疑问解答.md:1724-1738`
- agent 任务：问 BM25 的 k1 / b 作用；日志 `logs/m3_search2.jsonl`；回答引用 `AI-Agent疑问解答.md:1583-1603`、`1604-1612`、`1637-1652`
- 修复：`sandbox/docs` 是 11-18 的旧副本（不含 BM25 章节），已同步最新 5 份文档；重建后 137 → 185 块

**收尾**
- 面试素材已补第 8–10 条（BM25 选型、统计量粒度、引用与排序确定性）及口述版
- 已提交推送：harness `ee9ba39`、文档 `afd2c5b34`
- 索引是进程内缓存，文档更新后需重启进程

**下一块**
- M3 第三块：30 条检索评测集（覆盖 5 份文档）+ `scripts/eval_retrieval.py`
- 指标：`recall@1/3/5`、`MRR@5`；严格命中 = 同 path 且行号区间相交，宽松命中 = 同 path
- 待确认：30 条由 Claude 起草、用户抽检 5 条；ground truth 按行号区间标注
- 再下一块：agent 端到端 30 条引用准确率

### 2026-11-19 · M3 第二块（第一版检索：BM25 + 引用）

**模式**：独立（用户写实现，Claude review + 写测试）
**方案假设**：首版用 BM25（中文按字符 bigram、英文按单词）做关键词检索，不引入向量库和本地模型。理由：旧机无 Docker、不装本地模型；先拿到可量化的关键词基线，后续加向量/hybrid 才有对比数字。

**今日任务**
1. [x] 主任务：`app/rag.py` —— 文档加载 + 按行切分（目标 600 字符、重叠约 100），每块带 `path` / `start_line` / `end_line`
2. [x] 辅助：`app/retrieval.py` —— 分词 + BM25 + `tests/test_retrieval.py`（Claude 写，11-20 完成）
3. [x] 辅助：`search_docs` 工具注册，agent 一次带 `path:line` 引用的问答实测（11-20 完成）

**进展**
- `app/rag.py`：滑动窗口切分（`max_chars=600`、`overlap=100`）+ 1-based 行号 + 文档内 `#n` id；空白块跳过
- `tests/test_rag.py` 14 条通过；全量 `pytest -q tests/` → 41 passed
- 真实语料：5 文档 / 67656 字符 → 137 块；id 全唯一，最大块 600 字符，空白块 0

**今日验收**：切块行号能回溯原文；已知问题的 top-1 命中正确文档；agent 回答带引用

### 2026-11-18 · M3 第一块（上下文预算 + 截断）

**模式**：独立（用户写实现，Claude review + 写测试）
**今日任务**
1. [x] 主任务：`app/context.py` —— token 估算 + `CONTEXT_BUDGET` + 裁剪（system 保留、旧轮删除、超长 tool 结果截断、tool_call 配对不拆）
2. [x] 辅助：`tests/test_context.py` 12 条（Claude 写）
3. [x] 辅助（精简）：接入 `agent_loop.ask` 前调用，日志记录裁剪前后估算 token

**今日验收**：50+ 轮伪造对话不报 context length；裁剪后 tool 配对完整；有裁剪前后数字

**进展**
- 两轮 review 后修掉：`content=None` 崩溃、`budget` 参数被常量覆盖、截断结果取错列表、极端分支多返回剩余消息
- 测试：`pytest -q tests/` → 27 passed（其中新增 12 条）
- 口径确定：`TOOL_RESULT_LIMIT` 只在超预算时生效（疑问解答 6.3）
- 优化（Claude 改）：`split_units` 预切单元取代索引算术；单元 token 只算一次；去掉整表 `deepcopy`
- 用户修掉：多条 user 消息死循环；`<` 改 `<=` 边界

**验收证据**
- 任务：读取 `sandbox/big_context.txt`（31499 字符）
- 日志 `logs/context.jsonl` 事件统计：`user 1 / assistant 2 / tool 1 / context 1 / done 1`
- 裁剪事件仅 1 条：`before=31752` → `after=2271`（`MAX_STEPS` 内一次工具调用完成，无重读）
- `pytest -q tests/` → 27 passed（`test_context.py` 12 条）

**遗留**
- 无

### 2026-11-18 · M2 第五块（验收，完成）· 5/37

**今日任务**
1. [x] 20 步验收任务（`MAX_STEPS` 调到 20）
2. [x] 辅助：`--task` 参数，方便换成验收任务文本
3. [x] 进度与文档同步

**验收证据**
- 任务：多跳文件追踪。19 个线索文件，每个文件一行，内容指向下一个文件，最后一个为 `STOP`
- 命令：`.venv/bin/python -m scripts.agent_loop --log logs/acceptance.jsonl --task "…"`
- 事件统计：`user 1 / assistant 20 / tool 19 / done 1`；`done.steps = 20`；无 `limit` 事件
- 每次 `ask` 只带 1 个 `tool_call`，证明是串行追踪，不是并行批处理
- 模型最终列出 19 条路径并报告「一共读了 19 个文件」

**卡点**：无

**未完成**：代码与文档改动尚未提交（等收尾指令）

### 2026-11-14 · M2 第四块（完成）· 4/37

**今日任务**
1. [x] 主任务：`app/events.py` —— JSONL `append` / `load` / `messages_from`
2. [x] 接入 `agent_loop.py`：每轮写 assistant / tool 事件
3. [x] 恢复：统计已完成步数 + 处理中断时未回填的 tool call
4. [x] 测试 5 条 + kill 演练

**验收**：进程在工具执行后被杀，`--resume` 能接着跑；不重复执行已有副作用的工具；日志能用 `jq` 逐行读出

**已交付**
- `app/events.py`：`EventLog.append` / `load` / `messages_from` / `pending_tool_calls`
- `scripts/agent_loop.py`：assistant / tool 事件写入顺序；`--resume` 恢复步数与 pending 工具回填
- `tests/test_events.py`：5 条用例（写入回环、半行容错、消息还原、纯文本 assistant、pending 检测）
- `.gitignore` 增加 `logs/`

**验收证据**
- `.venv/bin/python -m pytest -q tests/` → 15 passed
- kill 演练（`logs/drill.jsonl`）：`user → assistant(read_file) → tool → assistant(write_file) → interrupted`，write_file 无结果
- `--resume` 后先回填「结果未知」的 tool 事件，模型改用 `read_file` 核对，再被人工拒绝，最终 `done steps=5`；README 全程未变（`git status` 干净）
- 事件序列：`interrupted` 之后是合成的 tool 事件（id 与 pending call 一致），没有重复执行写操作

**发现的问题**
- 新会话分支漏 `steps = 0` → `UnboundLocalError`（骨架遗留，已补）
- `.count` 写成属性拿到的是方法对象，应为 `len(...)`
- `event.get("tool_calls")` 缺失时返回 None，避免纯文本 assistant 事件触发 KeyError

### 2026-11-13 · M2 第三块（完成）· 3/37

**今日任务**
1. [x] 主任务：`write_file(path, content)` + schema + 路径守卫
2. [x] 权限层 `app/permissions.py`：`ensure_safe_path` + `confirm_write`
3. [x] 测试：正常写 / 越界拒 / 敏感路径拒 / 确认拒绝
4. [x] 收尾：面试素材补「权限为什么在工具执行前」+ commit

**验收证据**
- `pytest -q tests/test_tools.py -v` → 7 passed
- 输入 `n`：工具结果 `禁止写入`，README 未变
- 输入 `y`：工具结果 `已写入 README.md（748 字符）`，随后 `read_file` 校验内容正确
- `../hack.txt` 与 `.env` 由 `PermissionError` 拒绝，不弹确认框

**发现的问题**
- 拒绝文案 `禁止写入` 太笼统，模型理解成「环境限制」并想找替代路径；应改成「用户拒绝写入（人工确认未通过），未做任何修改」
- `write_file` 已返回写入结果，不再是 `None`

**卡点**
- `relative_to` 返回 Path，不能当布尔；越界时抛 `ValueError`，应改用 `is_relative_to`
- `permissions.ROOT` 与 `tools.ROOT` 各定义一份，测试只 patch 前者导致不一致
- import / 内存模型整体暂未吃透：已把疑问解答 2.13 标记为「暂不纠结」，只记操作层结论，后续遇到再深入

**收尾**：面试素材第 4 条已补；README 的验收痕迹已清理；代码与文档提交推送

**未完成**：无

### 2026-11-13（周五）· M2 第二块（完成）

**今日任务**
1. [x] 主任务：`scripts/agent_loop.py` 递归改 `while` + `MAX_STEPS` 步数上限
2. [x] `tests/test_tools.py`：正常目录 / 越界 / 不存在 三条用例
3. [x] 工具异常兜底：补 `KeyError`、`TypeError`、非法 JSON

**实际完成**：3/3 + 面试素材（commit 未做）
**卡点**：
- `steps` 初始化后忘记 `+1`，上限条件成了死代码；靠临时把 `MAX_STEPS` 改成 2 并观察截断才暴露
- 三条测试函数体先写成 `pass`，pytest 照样记通过，属于假绿
- `list_file` 用了 `os.listdir(path)` 而不是校验后的 `target`

**验收证据**
- 多步任务：3 次工具调用 + 最终回答（列目录 → 读 pyproject → 读 requirements）
- 截断：`MAX_STEPS=2` 时输出「超过最大循环次数2」后停止；上限计的是 `ask` 次数，不是工具调用次数（那次 2 轮 ask 共触发 4 次工具调用）
- 测试：`pytest -q tests/test_tools.py` → 3 passed
- 概念归档：疑问解答 5.5 步数上限、2.8 路径拼接、2.9 with 语句
- 面试素材：`/Users/finlaas/my/AI-Agent面试素材.md`（三条：步数上限、工具回填、异常兜底）

**未完成**：无（代码与文档均已提交推送）

### 2026-11-13（周五）· M1 · 2/37

**实际完成**：3/3
**实际用时**：未记录

**做了什么**：
- 任务 2：`/chat/stream` 接流式，`curl -N -G --data-urlencode` 验证通过
- 任务 3：`static/index.html` + `StaticFiles` 挂载，浏览器逐字显示通过
- 任务 4：独立仓库 `git init -b main`，首次提交 `bdbf651`，推送到 github.com/OdAhViig/harness
- 任务 5：`requirements.txt`、`.env.example`、`README.md`、`app/__init__.py`
- 任务 6：`tests/test_api.py` 三个冒烟测试，`pyproject.toml` 配 `pythonpath`，3 passed
- M2 第一块：`app/tools.py` + `scripts/loop_once.py`，tool call 链路跑通（tool_calls → 本地 `read_file` → 回填 → 最终回答）

**卡点**：
- 理解了「无 `content-length`」与「`transfer-encoding: chunked`」是同一件事的两面
- 修正认知：`{ stream: true }` 处理的是 UTF-8 字节被 chunk 切断，不是 URL 转义

**明日候选**：
- 依赖固化 `requirements.txt` + `README.md` + `.env.example`
- pytest 冒烟测试 `/health`
- `app/`、`scripts/` 补 `__init__.py`

### 2026-11-12（周四）· M1 · 1/37

**实际完成**：4/4
**实际用时**：未记录
**卡点**：
- 流式输出的第一个 chunk 被 `if/else` 吞掉：状态切换和打印内容写成了互斥分支，修复方式是把打印移出分支、前缀只打一次。
- `flush` 在终端里差异不明显，重定向到文件时才看得出块缓冲。

**明日候选**：
- 把 `stream_deepseek.py` 的调用封装成函数。
- FastAPI `/chat` 改成流式响应，浏览器能逐字显示。
- 补 `.gitignore` 和第一次 git commit。

<!-- 每天在这里追加一段，最新的放最上面 -->

<!-- 模板：

## YYYY-MM-DD（周X）· M?

**今天可用**：8h
**昨日遗留**：……

**今日任务**
1. [ ] 主任务：……
2. [ ] 辅助：……
3. [ ] 辅助：……

**今日验收**：……

**实际完成**：x/3
**实际用时**：xh
**卡点**：……
**明日候选**：……

-->
