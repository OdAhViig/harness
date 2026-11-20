"""BM25 检索规格测试：分词、索引统计量、打分排序与边界。"""

import copy
import math

import pytest

from app.retrieval import build_index, search, tokenize


def make_chunk(chunk_id, text, path="sandbox/docs/demo.md", start_line=1, end_line=None):
    return {
        "id": chunk_id,
        "path": path,
        "start_line": start_line,
        "end_line": start_line if end_line is None else end_line,
        "text": text,
    }


# ---------- tokenize ----------


def test_tokenize_lowercases_and_keeps_english_words():
    assert tokenize("Hello, WORLD 123!") == ["hello", "world", "123"]


def test_tokenize_chinese_as_bigrams():
    assert tokenize("上下文") == ["上下", "下文"]


def test_tokenize_mixes_chinese_and_english():
    assert tokenize("BM25 上下文") == ["bm25", "上下", "下文"]


def test_tokenize_drops_punctuation_and_whitespace():
    assert tokenize("a, b!\n c?") == ["a", "b", "c"]


def test_tokenize_single_chinese_char_has_no_bigram():
    assert tokenize("中") == []


def test_tokenize_empty_or_symbol_only_text():
    assert tokenize("") == []
    assert tokenize("!!! ???") == []


def test_tokenize_keeps_repeated_terms():
    # 分词不去重；去重是 tf 统计和 query 侧的事
    assert tokenize("apple apple") == ["apple", "apple"]


# ---------- build_index ----------


def test_build_index_records_postings_and_doc_lengths():
    index = build_index([
        make_chunk("c1", "apple banana"),
        make_chunk("c2", "apple cherry"),
    ])

    assert index["N"] == 2
    assert index["avgdl"] == 2.0
    assert index["doc_len"] == {"c1": 2, "c2": 2}
    assert index["postings"]["apple"] == {"c1": 1, "c2": 1}
    assert index["postings"]["banana"] == {"c1": 1}
    assert index["chunks"]["c1"]["text"] == "apple banana"


def test_build_index_counts_df_once_per_chunk():
    index = build_index([
        make_chunk("c1", "apple apple apple"),
        make_chunk("c2", "apple"),
    ])

    # tf 是块内出现次数，df 是包含该 term 的块数
    assert index["postings"]["apple"] == {"c1": 3, "c2": 1}
    assert len(index["postings"]["apple"]) == 2


def test_build_index_filters_chunks_without_terms():
    index = build_index([
        make_chunk("c1", "apple"),
        make_chunk("c2", "!!! ???"),
    ])

    assert index["N"] == 1
    assert index["avgdl"] == 1.0
    assert "c2" not in index["doc_len"]
    assert "c2" not in index["chunks"]


def test_build_index_computes_average_length():
    index = build_index([
        make_chunk("c1", "apple banana"),
        make_chunk("c2", "apple banana cherry date"),
    ])

    assert index["doc_len"]["c1"] == 2
    assert index["doc_len"]["c2"] == 4
    assert index["N"] == 2
    assert index["avgdl"] == 3.0


def test_build_index_skips_missing_text():
    index = build_index([make_chunk("c1", None)])

    assert index["N"] == 0
    assert index["postings"] == {}


def test_build_index_keeps_citation_fields():
    index = build_index([
        make_chunk("c1", "apple", path="sandbox/docs/a.md", start_line=3, end_line=5),
    ])

    assert index["chunks"]["c1"] == {
        "path": "sandbox/docs/a.md",
        "start_line": 3,
        "end_line": 5,
        "text": "apple",
    }


def test_build_index_does_not_mutate_input():
    chunks = [
        make_chunk("c1", "apple banana"),
        make_chunk("c2", "apple cherry"),
    ]
    snapshot = copy.deepcopy(chunks)

    build_index(chunks)

    assert chunks == snapshot


def test_build_index_empty_input():
    index = build_index([])

    assert index["N"] == 0
    assert index["avgdl"] == 0.0
    assert index["chunks"] == {}
    assert index["doc_len"] == {}
    assert index["postings"] == {}


# ---------- search ----------


def test_search_returns_matching_chunk_with_citation_fields():
    index = build_index([
        make_chunk("c1", "apple", path="sandbox/docs/a.md", start_line=2, end_line=4),
    ])

    results = search(index, "apple")

    assert len(results) == 1
    assert results[0]["id"] == "c1"
    assert results[0]["path"] == "sandbox/docs/a.md"
    assert results[0]["start_line"] == 2
    assert results[0]["end_line"] == 4
    assert results[0]["text"] == "apple"
    assert results[0]["score"] > 0


def test_search_scores_single_document_term_exactly():
    index = build_index([make_chunk("c1", "apple")])

    # N=1, df=1, tf=1, dl=avgdl=1 → idf 项与长度项都简化，score 等于 idf
    score = search(index, "apple")[0]["score"]

    assert score == pytest.approx(math.log(4 / 3))


def test_search_adds_scores_of_multiple_query_terms():
    index = build_index([make_chunk("c1", "apple banana")])

    score = search(index, "apple banana")[0]["score"]

    # 两个 term 各贡献一个 idf，直接相加
    assert score == pytest.approx(2 * math.log(4 / 3))


def test_search_deduplicates_query_terms():
    index = build_index([make_chunk("c1", "apple")])

    once = search(index, "apple")[0]["score"]
    twice = search(index, "apple apple")[0]["score"]

    assert twice == pytest.approx(once)


def test_search_prefers_shorter_chunk_when_tf_equal():
    index = build_index([
        make_chunk("c_short", "apple"),
        make_chunk("c_long", "apple b c d"),
    ])

    results = search(index, "apple")

    # 两块的 tf 都是 1，短块的长度归一化更小，分数更高
    assert [r["id"] for r in results] == ["c_short", "c_long"]
    assert results[0]["score"] > results[1]["score"]


def test_search_rare_term_scores_higher():
    index = build_index([
        make_chunk("c1", "apple banana"),
        make_chunk("c2", "apple cherry"),
        make_chunk("c3", "cherry date"),
    ])

    # 两块 dl 相同、tf 相同，只有 df 不同：apple 出现在 2 块，banana 只出现在 1 块
    apple_score = search(index, "apple")[0]["score"]
    banana_score = search(index, "banana")[0]["score"]

    assert banana_score > apple_score


def test_search_returns_empty_for_unknown_query():
    index = build_index([make_chunk("c1", "apple")])

    assert search(index, "zzz") == []


def test_search_returns_empty_for_empty_or_single_char_chinese_query():
    index = build_index([make_chunk("c1", "apple")])

    assert search(index, "") == []
    # 单个汉字切不出 bigram，没有查询 term
    assert search(index, "中") == []


def test_search_limits_to_top_k():
    index = build_index([
        make_chunk("c1", "apple a"),
        make_chunk("c2", "apple b"),
        make_chunk("c3", "apple c"),
    ])

    results = search(index, "apple", top_k=2)

    assert len(results) == 2


def test_search_top_k_non_positive_returns_empty():
    index = build_index([make_chunk("c1", "apple")])

    assert search(index, "apple", top_k=0) == []
    assert search(index, "apple", top_k=-1) == []


def test_search_tie_breaks_by_chunk_id():
    index = build_index([
        make_chunk("c3", "apple a"),
        make_chunk("c1", "apple a"),
        make_chunk("c2", "apple a"),
    ])

    # 三块内容相同，分数相同，按 id 升序保证结果稳定
    assert [r["id"] for r in search(index, "apple")] == ["c1", "c2", "c3"]
