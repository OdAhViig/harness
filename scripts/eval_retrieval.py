import argparse
import json
from pathlib import Path

from app.rag import PROJECT_ROOT, load_documents, chunk_all
from app.retrieval import build_index, search

# 用绝对路径做默认值，避免必须从某个目录启动才能找到文件
DEFAULT_QUESTIONS = PROJECT_ROOT / "eval" / "retrieval_questions.jsonl"
# 评测语料冻结在 eval/corpus：ground truth 的行号只对这一个版本有效。
DEFAULT_CORPUS = PROJECT_ROOT / "eval" / "corpus"


def load_questions(path: Path) -> list[dict]:
    """读取并校验评测集。任何一条不合法都报错，不静默跳过。"""
    if not path.exists():
        raise ValueError(f"评测集不存在：{path}")

    questions = []
    seen_ids = set()
    text = path.read_text(encoding="utf-8")

    # enumerate(..., 1) 让行号从 1 开始，和编辑器里看到的一致。
    for line_no, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue

        try:
            question = json.loads(line)
        except json.JSONDecodeError as exc:
            # from exc 保留原始异常链，调试时能看到 JSON 报错的位置。
            raise ValueError(f"第 {line_no} 行 JSON解析失败：{exc}") from exc

        for key in ("id", "question", "path", "start_line", "end_line"):
            if key not in question:
                raise ValueError(f"第 {line_no} 行缺少字段 {key}")
        if not str(question["question"]).strip():
            raise ValueError(f"第 {line_no} 行 question为空")
        if not str(question["path"]).strip():
            raise ValueError(f"第 {line_no} 行 path 为空")
        if question["id"] in seen_ids:
            raise ValueError(f"第 {line_no} 行 id 重复：{question['id']}")
        seen_ids.add(question["id"])

        start = question["start_line"]
        end = question["end_line"]
        if not (1 <= start <= end):
            raise ValueError(f"第 {line_no} 行行号非法：{start}-{end}")

        # setdefault：键不存在时才写入默认值，已存在则不动。
        question.setdefault("difficulty", "unknown")
        question.setdefault("note", "")
        questions.append(question)

    if not questions:
        raise ValueError(f"评测集为空：{path}")
    return questions


def is_hit(result: dict, question: dict, strict: bool) -> bool:
    """判断一条检索结果是否命中 ground truth。
    search() 返回的 path 形如 sandbox/docs/X.md，评测集里只有 X.md，所以先取文件名再比较。"""
    if Path(result["path"]).name != question["path"]:
        return False
    if not strict:
        return True

    # 两个闭区间相交：左端不大于对方右端，且右端不小于对方左端。
    return (
        result["start_line"] <= question["end_line"]
        and question["start_line"] <= result["end_line"]
    )


def first_hit_rank(results: list[dict], question: dict, strict: bool) -> int | None:
    """results 已按分数降序，第一个命中的位置就是名次（从 1 开始）。"""
    for rank, result in enumerate(results, 1):
        if is_hit(result, question, strict):
            return rank
    return None

    
def evaluate(questions: list[dict], index: dict, top_k: int) -> list[dict]:
    """每题只检索一次，严格和宽松两种名次都从同一份结果里取。"""
    rows = []
    for question in questions:
        results = search(index, question["question"], top_k)

        # 保留 Top-K 的实际位置，未命中时报告要用。
        top = []
        for result in results:
            top.append({
                "path": Path(result["path"]).name,
                "start_line": result["start_line"],
                "end_line": result["end_line"],
                "score": result["score"],
            })

        rows.append({
            "id": question["id"],
            "question": question["question"],
            "expected_path": question["path"],
            "expected_start": question["start_line"],
            "expected_end": question["end_line"],
            "difficulty": question.get("difficulty", "unknown"),
            "strict_rank": first_hit_rank(results, question, True),
            "loose_rank": first_hit_rank(results, question, False),
            "top": top,
        })
    return rows


def summarize(rows: list[dict], strict: bool) -> dict:
    """所有指标的分母都是总题数；未命中对 MRR 贡献 0。"""
    total = len(rows)
    if total == 0:
        raise ValueError("没有可汇总的题目")

    key = "strict_rank" if strict else "loose_rank"
    ranks = []
    for row in rows:
        ranks.append(row[key])

    recall = {}
    for k in (1, 3, 5):
        hits = 0
        for rank in ranks:
            # rank 可能是 None，必须先判断再比较，否则 None <= 3 会抛 TypeError。
            if rank is not None and rank <= k:
                hits += 1
        recall[k] = hits / total

    reciprocal_sum = 0.0
    for rank in ranks:
        if rank is not None and rank <= 5:
            reciprocal_sum += 1 / rank

    return {
        "total": total,
        "recall@1": recall[1],
        "recall@3": recall[3],
        "recall@5": recall[5],
        "mrr@5": reciprocal_sum / total,
    }


def format_report(rows: list[dict], strict_summary: dict, loose_summary: dict) -> str:
    """两组指标 + 严格口径未命中明细。"""
    lines = []
    for label, summary in (("strict", strict_summary), ("loose", loose_summary)):
        # {label:6} 表示左对齐、占 6 个字符宽，让两行指标对齐。
        lines.append(
            f"{label:6} recall@1 {summary['recall@1']:.3f}  "
            f"recall@3 {summary['recall@3']:.3f}  "
            f"recall@5 {summary['recall@5']:.3f}  "
            f"MRR@5 {summary['mrr@5']:.3f} (n={summary['total']})"
        )

    missed = []
    for row in rows:
        if row["strict_rank"] is None:
            missed.append(row)

    if not missed:
        lines.append("")
        lines.append("严格口径：所有题目都在 Top-5 内命中。")
        return "\n".join(lines)

    lines.append("")
    lines.append(f"严格口径未命中 {len(missed)} 条：")
    for row in missed:
        lines.append(
            f'#{row["id"]}  {row["question"]}\n'
            f'     期望 {row["expected_path"]}:{row["expected_start"]}-{row["expected_end"]}'
        )
        for rank, top in enumerate(row["top"], 1):
            lines.append(
                f'     Top-{rank}: {top["path"]}:{top["start_line"]}-{top["end_line"]}'
                f'  score={top["score"]:.4f}'
            )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="跑检索评测集，输出 recall 与 MRR。")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--docs", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    try:
        if args.top_k <= 0:
            raise ValueError(f"top_k 必须大于 0，收到 {args.top_k}")
        if not args.docs.exists():
            raise ValueError(f"文档目录不存在：{args.docs}")

        questions = load_questions(args.questions)
        chunks = chunk_all(load_documents(args.docs))
        index = build_index(chunks)
        rows = evaluate(questions, index, args.top_k)

        strict_summary = summarize(rows, strict=True)
        loose_summary = summarize(rows, strict=False)

        print(f"语料：{index['N']} 块；题目：{len(questions)} 条")
        print(format_report(rows, strict_summary, loose_summary))
    except (ValueError, OSError) as exc:
        # 预期内的输入错误：只打印一行提示，退出码 1。
        # 其他未预料的异常不在这里捕获，让完整堆栈暴露出来方便调试。
        print(f"错误：{exc}")
        raise SystemExit(1)
    

if __name__ == "__main__":
    main()
