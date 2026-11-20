# AI Agent 自学路线（A 为主，B 为差异化）· 12 周

> 前提：iOS/Flutter 10 年，强客户端/系统经验，弱生产级 Python 后端。
> 目标岗位：Agent 应用开发（路线 A）为主，AI Coding Agent（路线 B）作为差异化项目。
> 时间预算：按每周 15–20 小时设计；若每周只有 8–10 小时，整体拉长到 18–20 周，不要压缩项目阶段。
> 全职每天 8 小时：用 [6 周冲刺版](AI-Agent全职6周冲刺计划.md)。

---

## 0. 结论：能兼顾，但必须串行

A 和 B 不是两条独立技能树，重叠约 70–75%：

| 能力 | A 应用开发 | B Coding Agent | 是否共用 |
|---|---|---|---|
| Agent loop / 任务分解 | 必须 | 必须 | ✅ |
| Tool Calling / 结构化输出 | 必须 | 必须 | ✅ |
| MCP / Skills / 工具协议 | 必须 | 必须 | ✅ |
| Context Engineering | 必须 | 必须（更极端） | ✅ |
| RAG / 代码检索 | 必须 | 必须（代码检索是变体） | ✅ 70% |
| 失败重试 / 幂等 / 恢复 | 必须 | 必须 | ✅ |
| HITL 审批 / 权限 | 必须 | 必须 | ✅ |
| 评测 / trace / 成本 | 必须 | 必须（SWE-bench 类） | ✅ 70% |
| Docker / CI | 必须 | 必须 | ✅ |
| 仓库操作（git worktree、patch、diff） | 很少 | 核心 | ❌ B 增量 |
| 执行沙箱（容器/microVM、网络与资源限制） | 了解 | 核心 | ❌ B 增量 |
| Coding 评测（SWE-bench-lite、PR 采纳率） | 不需要 | 核心 | ❌ B 增量 |
| 大仓库代码检索（AST、符号索引） | 不需要 | 重要 | ❌ B 增量 |

**所以**：先按 A 学到能独立上线（约 9–10 周），再用 2–3 周在同一个项目上加 B 模块。不要同时学 LangGraph 和 Claude Agent SDK 两套，也不要把 B 的沙箱/仓库工具链提前到前 8 周——那会拖慢主线且暂时用不上。

**如果时间不足**：砍掉 B 模块，把 A 的评测与可观测性做深。B 是加分项，A 是入场券。

---

## 1. 能力差距与补法

| 缺口 | 现状 | 补法 | 验收标准 |
|---|---|---|---|
| 生产级 Python | 语法可用，缺工程化 | FastAPI + asyncio + Pydantic + pytest + ruff/mypy | 能写一个有 10+ 接口、带测试和 Dockerfile 的服务 |
| LLM API 工程 | 会用工具，没写过调用层 | tool calling、结构化输出、流式、重试、token 计费 | 手写一个不依赖框架的 agent loop |
| Agent 编排 | 概念清楚 | 先手写，再 LangGraph | 能解释 checkpoint、interrupt、子图、状态合并 |
| RAG | 知道概念 | 切分/embedding/hybrid/rerank/引用/评估 | 召回率与引用准确率有基线数字 |
| MCP | 未实操 | 写 server + client，工具 schema/权限 | 能被 Claude Code 或其他客户端接入 |
| 评测 | 有契约/质量门经验 | golden set、LLM-as-judge、回归、成本 | CI 里能跑，输出通过率与失败分类 |
| 可观测性 | 客户端排障强 | trace、span、token/延迟/成本面板 | 每次运行可回放，能定位到具体步骤 |
| 分布式落地 | 概念清楚 | 幂等键、重试预算、队列、限流 | 项目里至少一个真实幂等与恢复场景 |
| 沙箱（B） | 无 | Docker 隔离 + 资源/网络限制 | 能安全执行生成的代码并回收 |
| 仓库工具链（B） | 无 | git worktree、patch、PR API、CI 日志 | 能自动完成一次 issue → PR |

---

## 2. 12 周日程

### 阶段一：地基（W1–W2）

| 周 | 主题 | 产出 | 验证 |
|---|---|---|---|
| W1 | Python 生产级 + FastAPI | 一个带 5 个接口、Pydantic 校验、pytest、Dockerfile 的服务 | `docker run` 后可调用；测试覆盖率 >60% |
| W2 | LLM API 与手写 Agent Loop | 不依赖框架的 ReAct loop：工具注册、并行调用、错误回传、步数/预算上限、流式输出 | 能稳定跑 20 步以上；工具失败会重试而非崩溃 |

**关键**：W2 一定先手写。直接上 LangGraph 会导致面试时讲不清状态机与中断恢复。

### 阶段二：Agent 核心（W3–W4）

| 周 | 主题 | 产出 | 验证 |
|---|---|---|---|
| W3 | LangGraph | 把 W2 的 loop 改写成图：节点、边、条件路由、checkpoint、interrupt | 能中断后恢复；能画出一张可解释的状态图 |
| W4 | Context Engineering + 记忆 | token 预算、消息裁剪/摘要、工具结果压缩、长期记忆（向量/结构化） | 长对话不爆窗口；关键信息不丢；有成本对比 |

### 阶段三：知识与工具（W5–W7）

| 周 | 主题 | 产出 | 验证 |
|---|---|---|---|
| W5 | RAG 全链路 | 文档切分、embedding、pgvector/Qdrant、hybrid search、rerank、引用 | 30 条评测问题，召回率/引用准确率有数字 |
| W6 | RAG 评估与优化 | golden set、失败分类（未召回/排序错/生成错）、参数对比 | 能说清每次优化的指标变化 |
| W7 | MCP + Skills | 一个 MCP server（3–5 个工具）+ client；工具 schema、错误码、权限边界 | 能被外部客户端接入；越权调用被拒 |

### 阶段四：生产化（W8–W9）

| 周 | 主题 | 产出 | 验证 |
|---|---|---|---|
| W8 | 可靠性 | 重试/退避、幂等键、超时、断点续跑、HITL 审批、SSE 流式 | 注入 3 类故障（工具超时、模型 5xx、进程重启）后可恢复 |
| W9 | 评测与可观测性 | Langfuse/OTel trace、token/延迟/成本面板、CI 质量门 | 每次 PR 自动跑评测；失败可定位到步骤 |

### 阶段五：毕业项目（W10–W11）

**项目：研发效能 Agent（Repo Copilot）**

阶段 1（A 的能力）：

- 接入一个真实仓库的 issue、README、CI 日志。
- RAG 问答 + 工具调用（查 issue、查 CI、代码搜索、查文档）。
- HITL：修改代码/提 PR 前必须审批。
- 评测集 30–50 条，覆盖问答、工具选择、拒答。
- Docker 部署，有 trace 与成本面板。

阶段 2（B 的增量，W12）：

- issue → 定位文件 → 生成 patch → 沙箱跑测试 → 失败重试 → 提 PR。
- git worktree 隔离；容器沙箱限制网络与资源。
- SWE-bench-lite 子集或自建 10 条任务，报告通过率与人工返工率。

> 这个项目的好处：同一套代码同时命中 A 和 B 的 JD 关键词；对客户端背景的你，"研发效能"比"通用客服 Agent"更容易讲出深度。

### 阶段六：求职材料（W12 并行）

- README：架构图、关键决策、失败案例、指标。
- 3 个可讲的故障故事：循环失控、上下文污染、工具幂等。
- 简历改写：把客户端经验映射到 Agent 语言（事件流、状态恢复、HITL、多端编排）。

---

## 3. 本地教程的复用与替换

`ai-agent-engineer-tutorial/` 基于一份 Agent 平台/Runtime JD，偏路线 C。按下面取舍：

| 章节 | 用法 |
|---|---|
| 01 Python 异步与服务端 | ✅ 直接用，补 FastAPI/Pydantic 实操 |
| 02 分布式与可靠性 | ✅ 选读幂等、重试、队列；不必深入一致性理论 |
| 03 LLM 推理工程 | ⚠️ 只取 token/上下文/结构化输出；vLLM 部分跳过 |
| 04 Agent 原理与设计模式 | ✅ 精读 ReAct、Plan-and-Execute、Reflection、Multi-Agent |
| 05 AgentRuntime | ⚠️ 理解 checkpoint/事件溯源即可，不必照着实现 Runtime |
| 06 MCP/沙箱/安全 | ✅ MCP 与权限必做；沙箱做到 Docker 级即可 |
| 07 可观测性与评测 | ✅ 重点，市场正在把评测独立成岗 |
| 08 实战项目 | ⚠️ 若偏 Runtime，替换成本路线第 2 节的 Repo Copilot |
| 09 简历与面试 | ✅ 参考，但要按 A 的 JD 重写 |

---

## 4. 取舍规则

1. **框架只学一个**：LangGraph 为主；Claude Agent SDK / OpenAI Agents SDK 在 W12 用半天看概念即可。
2. **RAG 不追求前沿**：GraphRAG、多路召回是加分项，不是入场券。先把 hybrid + rerank + 评估做扎实。
3. **Infra 不深入**：K8s 会部署即可，不学 Operator、microVM。
4. **每两周一个可演示产物**：没有产出的周视为无效学习。
5. **评测贯穿始终**：W5 开始每加一个能力就补一条评测，不要最后补。
6. **B 模块是可选加时赛**：W12 做不完就砍，不影响 A 的完整性。

---

## 5. 面试可讲的三条主线

1. **可靠性**：非确定性系统怎么保证可恢复——checkpoint、幂等、重试预算、HITL。
2. **上下文工程**：token 预算、压缩、隔离、污染治理，有前后对比数字。
3. **评测闭环**：golden set、失败分类、CI 质量门、成本/延迟权衡。

这三条正好是 2026 JD 里从「会调 API」分化出来的核心差异点。
