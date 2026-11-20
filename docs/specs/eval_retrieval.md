# `scripts/eval_retrieval.py` 规格卡

> 目标：用 30 条人工标注的问题，给现有 BM25 检索器打出一组可比较、可回归的分数。
> 谁写：你（用户）实现，Claude 只 review 与写测试。卡住 30 分钟再看本文第 9 节的提示分档。

---

## 0. 一句话定义

读评测集 → 对每题调用 `search()` 拿 Top-K → 判定是否命中标注的原文区间 → 汇总成 recall / MRR 报告。

---

## 1. 运行方式

在项目根目录 `/Users/finlaas/my/deepseek-harness` 下：

```bash
.venv/bin/python -m scripts.eval_retrieval
```

可选参数（用 `argparse`）：

| 参数 | 默认值 | 含义 |
|---|---|---|
| `--questions` | `eval/retrieval_questions.jsonl` | 评测集路径 |
| `--docs` | `eval/corpus` | 冻结的评测语料快照 |
| `--top-k` | `5` | 每题取前几条结果 |

> 评测语料冻结在 `eval/corpus/`，是 2026-11-20 的 5 份文档快照。原因：ground truth 用行号标注，而行号只对固定语料版本有效；学习文档每天更新会让块数和行号漂移，基线就不可复现。需要更新语料时，同步重新标注受影响的题目，并在进度里记录版本变更。

退出码：

- `0`：评测正常完成（即使有未命中）。
- `1`：输入错误（评测集不存在、JSON 非法、行号非法、`top_k <= 0`）。

---

## 2. 输入格式

`eval/retrieval_questions.jsonl`，一行一个 JSON 对象：

```json
{"id": 1, "question": "BM25 的 k1 控制什么", "path": "AI-Agent疑问解答.md", "start_line": 1640, "end_line": 1660, "difficulty": "direct", "note": "..."}
```

| 字段 | 类型 | 校验 |
|---|---|---|
| `id` | int | 必填、全文件唯一 |
| `question` | str | 必填、非空 |
| `path` | str | 必填、只写文件名（如 `AI-Agent疑问解答.md`） |

> ⚠️ **路径口径**：`search()` 返回的 `result["path"]` 是相对项目根的路径，形如 `sandbox/docs/AI-Agent疑问解答.md`；评测集里只存文件名。判定时必须先归一化，比较 `Path(result["path"]).name == question["path"]`，直接比较字符串会全部未命中。
| `start_line` / `end_line` | int | 必填、`1 <= start_line <= end_line` |
| `difficulty` | str | 可选，缺省 `"unknown"`；不参与打分，只用于分组展示 |
| `note` | str | 可选，标注理由 |

加载时遇到非法行要抛出带行号的错误，例如 `第 7 行：start_line 必须 >= 1`。

---

## 3. 数据流

```
load_documents(docs_root) -> chunk_all(chunks) -> build_index(index)
load_questions(questions_path) -> questions
for q in questions:
    results = search(index, q["question"], top_k)
    strict_rank = first_hit_rank(results, q, strict=True)
    loose_rank  = first_hit_rank(results, q, strict=False)
summarize(rows, strict=True) / summarize(rows, strict=False)
format_report(...) -> print
```

注意事项：

- **每题只调用一次 `search`**，`recall@1` / `@3` 从同一份 Top-K 结果里截取，不要为每个 K 重新检索。
- 索引只建一次，所有问题共用。
- 不要修改 `app/retrieval.py` / `app/rag.py`；本脚本只做评测编排。

---

## 4. 函数规格（签名与职责，实现留空）

```python
def load_questions(path: Path) -> list[dict]:
    """逐行读 JSONL、校验字段、返回问题列表。非法输入抛 ValueError。"""
```

```python
def is_hit(result: dict, question: dict, strict: bool) -> bool:
    """判定一条检索结果是否命中这道题的 ground truth。

    result 字段：id / path / start_line / end_line / text / score
    注意 result["path"] 形如 sandbox/docs/X.md，与评测集的文件名不同，
    比较前先取 Path(result["path"]).name。
    strict=True ：文件名相同，且两个行号区间有交集
    strict=False：文件名相同
    """
```

```python
def first_hit_rank(results: list[dict], question: dict, strict: bool) -> int | None:
    """results 已按分数降序；返回第一个命中的名次（1-based），无命中返回 None。"""
```

```python
def evaluate(questions: list[dict], index: dict, top_k: int) -> list[dict]:
    """对每题检索一次，返回逐题结果行。"""
```

逐题结果行至少包含：

```python
{
    "id": 1,
    "question": "...",
    "expected_path": "...",
    "expected_start": 1640,
    "expected_end": 1660,
    "difficulty": "direct",
    "strict_rank": 2,
    "loose_rank": 1,
    "top": [{"path": "...", "start_line": 0, "end_line": 0, "score": 0.0}, ...],
}
```

`top` 用于未命中时打印明细，长度等于 `top_k`（或实际返回条数）。

```python
def summarize(rows: list[dict], strict: bool) -> dict:
    """汇总 recall@1/3/5 与 MRR@5。"""
```

返回：

```python
{"total": 30, "recall@1": 0.6, "recall@3": 0.833, "recall@5": 0.9, "mrr@5": 0.712}
```

```python
def format_report(rows: list[dict], strict_summary: dict, loose_summary: dict) -> str:
    """生成最终报告文本：两组指标 + 严格口径下的未命中明细。"""
```

```python
def main() -> None:
    """argparse → 建索引 → 加载问题 → evaluate → summarize → print。捕获 ValueError 后 exit(1)。"""
```

文件末尾：

```python
if __name__ == "__main__":
    main()
```

---

## 5. 指标口径（精确）

对每题，`rank` 表示第一个命中的名次；未命中记 `None`。

| 指标 | 公式 | 说明 |
|---|---|---|
| `recall@K` | `count(rank is not None and rank <= K) / total` | 分母是**总题数** |
| `MRR@5` | `sum(1/rank for rank in ranks if rank is not None and rank <= 5) / total` | 分母仍是**总题数**；未命中贡献 0 |

手算例子：3 道题，第一个命中名次分别为 `1`、`3`、`None`。

- `recall@1 = 1/3 = 0.333`
- `recall@3 = 2/3 = 0.667`
- `recall@5 = 2/3 = 0.667`
- `MRR@5 = (1/1 + 1/3 + 0) / 3 = 0.444`

**严格判定**（两个闭区间相交）：

```text
Path(result["path"]).name == question["path"]
且 result.start_line <= question.end_line
且 question.start_line <= result.end_line
```

画在纸上就是两条线段有重叠；端点相等算相交。

**宽松判定**：只比较 `path`。

两组指标都要输出，不要只报宽松口径。

---

## 6. 边界与错误处理

| 情况 | 期望行为 |
|---|---|
| 评测集文件不存在 | `FileNotFoundError` 或转成带路径的 `ValueError`，退出码 1 |
| 某行 JSON 解析失败 | 报错指明行号，退出码 1 |
| 行号非法（`start < 1` 或 `start > end`） | 报错指明第几条，退出码 1 |
| 评测集为空 | 报错，退出码 1 |
| `--top-k 0` 或负数 | 报错，退出码 1 |
| 某题检索结果为空 | 该题 `rank=None`，正常计入，不崩 |
| 评测集 `path` 不在语料中 | 该题必然未命中；打印一条警告（可选但推荐） |
| 同分结果 | `search` 已按 chunk id 保证稳定顺序，脚本不要重排 |
| 路径格式不一致 | `search` 返回 `sandbox/docs/X.md`，评测集只有 `X.md`；判定前统一取文件名 |

不建议用裸 `except`；只捕获你明确知道怎么处理的异常。

---

## 7. 验收标准

1. `.venv/bin/python -m scripts.eval_retrieval` 一条命令跑完，输出两组指标和未命中明细。
2. 30 条问题在报告中都有对应结果（总题数显示 30）。
3. 逐题明细能回答「这题是没检索到，还是排到了第 6 名」。
4. 用 3 条构造数据手算一遍指标，与脚本输出一致（测试里会验证）。
5. `pytest -q tests/` 全绿。

---

## 8. 明确不做

- 不测 agent 端到端回答与引用准确率（下一块）。
- 不做超参搜索（k1 / b / chunk 大小）。
- 不输出 HTML / CSV 报告。
- 不加缓存、不并发。

---

## 9. 提示分档（卡住 30 分钟后再看，每次只看下一档）

**提示 1**：先只写 `load_questions` + `main` 的串联，用 `print` 看每一步的数据形状；确认 30 条都读进来、索引的 `N` 是多少，再写判定。

**提示 2**：区间相交写成两个不等式，先拿纸画两条线段，把「完全在左、部分重叠、完全包含、完全在右」四种情况都代进去验证。

**提示 3**：`summarize` 里所有指标的分母都是 `total`，不是命中数；MRR 里未命中贡献 0，不是不参与平均。

---

## 10. 用到的 Python 语法点（先看再用）

| 语法 | 作用 | 例子 |
|---|---|---|
| `argparse` | 解析命令行参数；`--top-k` 自动映射为 `args.top_k` | `parser.add_argument("--top-k", type=int, default=5)` |
| `Path` | 路径对象；`/` 运算符拼接路径 | `Path("eval") / "x.jsonl"` |
| `text.splitlines()` | 按行切成字符串列表 | `for line in text.splitlines():` |
| `json.loads(line)` | JSON 字符串转 dict | 每行评测数据 |
| f-string | 格式化字符串 | `f"{value:.3f}"` 保留三位小数 |
| `dict.get(k, default)` | 键不存在时返回默认值 | `row.get("difficulty", "unknown")` |
| `int | None` | 类型注解：整数或 None | 仅用于标注，不影响运行 |
