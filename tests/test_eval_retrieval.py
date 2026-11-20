"""检索评测脚本规格测试：加载校验、命中判定、指标汇总与报告。"""

import json

import pytest

from scripts.eval_retrieval import (
    evaluate,
    first_hit_rank,
    format_report,
    is_hit,
    load_questions,
    summarize,
)


def make_question(**overrides):
    question = {
        "id": 1,
        "question": "BM25 的 k1 控制什么",
        "path": "a.md",
        "start_line": 10,
        "end_line": 20,
    }
    question.update(overrides)
    return question


def make_result(**overrides):
    result = {
        "id": "c1",
        "path": "sandbox/docs/a.md",
        "start_line": 12,
        "end_line": 18,
        "text": "",
        "score": 1.0,
    }
    result.update(overrides)
    return result


def write_jsonl(tmp_path, rows):
    path = tmp_path / "questions.jsonl"
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows),
        encoding="utf-8",
    )
    return path


def make_summary(total=1, recall1=1.0, recall3=1.0, recall5=1.0, mrr=1.0):
    return {
        "total": total,
        "recall@1": recall1,
        "recall@3": recall3,
        "recall@5": recall5,
        "mrr@5": mrr,
    }


# ---------- load_questions ----------


def test_load_questions_reads_all_rows(tmp_path):
    path = write_jsonl(tmp_path, [make_question(), make_question(id=2, path="b.md")])

    questions = load_questions(path)

    assert len(questions) == 2
    assert [q["id"] for q in questions] == [1, 2]


def test_load_questions_fills_optional_defaults(tmp_path):
    path = write_jsonl(tmp_path, [make_question()])

    question = load_questions(path)[0]

    assert question["difficulty"] == "unknown"
    assert question["note"] == ""


def test_load_questions_rejects_missing_field(tmp_path):
    row = make_question()
    del row["path"]
    path = write_jsonl(tmp_path, [row])

    with pytest.raises(ValueError, match=r"第 1 行缺少字段\s*path"):
        load_questions(path)


def test_load_questions_rejects_reversed_range(tmp_path):
    path = write_jsonl(tmp_path, [make_question(start_line=30, end_line=10)])

    with pytest.raises(ValueError, match="行号非法"):
        load_questions(path)


def test_load_questions_rejects_zero_start(tmp_path):
    path = write_jsonl(tmp_path, [make_question(start_line=0, end_line=10)])

    with pytest.raises(ValueError, match="行号非法"):
        load_questions(path)


def test_load_questions_rejects_duplicate_id(tmp_path):
    path = write_jsonl(tmp_path, [make_question(), make_question()])

    with pytest.raises(ValueError, match="id 重复"):
        load_questions(path)


def test_load_questions_rejects_empty_file(tmp_path):
    path = write_jsonl(tmp_path, [])

    with pytest.raises(ValueError, match="评测集为空"):
        load_questions(path)


def test_load_questions_rejects_broken_json(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="第 1 行 JSON"):
        load_questions(path)


def test_load_questions_rejects_missing_file(tmp_path):
    with pytest.raises(ValueError, match="不存在"):
        load_questions(tmp_path / "nope.jsonl")


# ---------- is_hit ----------


def test_is_hit_loose_compares_file_name_only():
    result = make_result(path="sandbox/docs/a.md")
    question = make_question(path="a.md")

    assert is_hit(result, question, strict=False)


def test_is_hit_loose_rejects_other_file():
    result = make_result(path="sandbox/docs/b.md")
    question = make_question(path="a.md")

    assert not is_hit(result, question, strict=False)


def test_is_hit_strict_accepts_partial_overlap():
    result = make_result(start_line=15, end_line=25)
    question = make_question(start_line=10, end_line=20)

    assert is_hit(result, question, strict=True)


def test_is_hit_strict_accepts_containment():
    # result 完全包住 question，两个端点都不在 question 区间内，但两段相交
    result = make_result(start_line=5, end_line=30)
    question = make_question(start_line=10, end_line=20)

    assert is_hit(result, question, strict=True)


def test_is_hit_strict_accepts_touching_endpoint():
    result = make_result(start_line=20, end_line=25)
    question = make_question(start_line=10, end_line=20)

    assert is_hit(result, question, strict=True)


def test_is_hit_strict_rejects_disjoint_ranges():
    result = make_result(start_line=30, end_line=40)
    question = make_question(start_line=10, end_line=20)

    assert not is_hit(result, question, strict=True)


# ---------- first_hit_rank ----------


def test_first_hit_rank_returns_first_position():
    results = [
        make_result(path="sandbox/docs/b.md"),
        make_result(),
        make_result(),
    ]

    assert first_hit_rank(results, make_question(), strict=True) == 2


def test_first_hit_rank_returns_none_when_missing():
    results = [make_result(path="sandbox/docs/b.md")]

    assert first_hit_rank(results, make_question(), strict=True) is None


def test_first_hit_rank_handles_empty_results():
    assert first_hit_rank([], make_question(), strict=True) is None


# ---------- evaluate ----------


def test_evaluate_calls_search_once_per_question(monkeypatch):
    calls = []

    def fake_search(index, query, top_k):
        calls.append((query, top_k))
        return [make_result()]

    monkeypatch.setattr("scripts.eval_retrieval.search", fake_search)

    rows = evaluate([make_question(), make_question(id=2)], index={}, top_k=5)

    assert calls == [("BM25 的 k1 控制什么", 5), ("BM25 的 k1 控制什么", 5)]
    assert rows[0]["strict_rank"] == 1
    assert rows[0]["loose_rank"] == 1
    assert rows[0]["top"][0]["path"] == "a.md"


def test_evaluate_records_miss(monkeypatch):
    monkeypatch.setattr(
        "scripts.eval_retrieval.search",
        lambda index, query, top_k: [make_result(path="sandbox/docs/b.md")],
    )

    rows = evaluate([make_question()], index={}, top_k=5)

    assert rows[0]["strict_rank"] is None
    assert rows[0]["loose_rank"] is None


# ---------- summarize ----------


def test_summarize_matches_hand_calculation():
    # 命中名次 1 / 3 / 未命中
    rows = [
        {"strict_rank": 1, "loose_rank": 1},
        {"strict_rank": 3, "loose_rank": 3},
        {"strict_rank": None, "loose_rank": 2},
    ]

    summary = summarize(rows, strict=True)

    assert summary["total"] == 3
    assert summary["recall@1"] == pytest.approx(1 / 3)
    assert summary["recall@3"] == pytest.approx(2 / 3)
    assert summary["recall@5"] == pytest.approx(2 / 3)
    assert summary["mrr@5"] == pytest.approx((1 + 1 / 3) / 3)


def test_summarize_uses_loose_rank():
    rows = [
        {"strict_rank": None, "loose_rank": 1},
        {"strict_rank": None, "loose_rank": 1},
    ]

    summary = summarize(rows, strict=False)

    assert summary["recall@1"] == 1.0
    assert summary["mrr@5"] == 1.0


def test_summarize_counts_rank_five_in_mrr():
    rows = [{"strict_rank": 5, "loose_rank": 5}]

    summary = summarize(rows, strict=True)

    assert summary["mrr@5"] == pytest.approx(1 / 5)


def test_summarize_rejects_empty_rows():
    with pytest.raises(ValueError, match="没有可汇总"):
        summarize([], strict=True)


# ---------- format_report ----------


def test_format_report_all_hit():
    rows = [{
        "id": 1,
        "question": "q",
        "expected_path": "a.md",
        "expected_start": 1,
        "expected_end": 5,
        "strict_rank": 1,
        "loose_rank": 1,
        "top": [],
    }]
    summary = make_summary()

    report = format_report(rows, summary, summary)

    assert "strict recall@1 1.000" in report
    assert "所有题目都在 Top-5 内命中" in report


def test_format_report_lists_missed_question():
    rows = [{
        "id": 7,
        "question": "未命中的问题",
        "expected_path": "a.md",
        "expected_start": 10,
        "expected_end": 20,
        "strict_rank": None,
        "loose_rank": 2,
        "top": [{"path": "b.md", "start_line": 1, "end_line": 5, "score": 2.5}],
    }]
    summary = make_summary(recall1=0.0, recall3=0.0, recall5=0.0, mrr=0.0)

    report = format_report(rows, summary, summary)

    assert "未命中 1 条" in report
    assert "#7" in report
    assert "期望 a.md:10-20" in report
    assert "Top-1: b.md:1-5" in report
