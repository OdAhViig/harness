"""BM25 检索：分词、建倒排索引、按查询打分。"""

from collections import Counter
from math import log
import re

# 连续的小写英文/数字，或连续的汉字；标点、空白自动当分隔符。
TERM_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+")

# BM25 的两个自由参数：k1 控制词频饱和速度，b 控制长度归一化强度。
K1 = 1.5
B = 0.75


def tokenize(text: str) -> list[str]:
    """把文本切成检索用的 term：英文/数字整段保留，中文按相邻两字切 bigram。"""
    terms = []
    for run in TERM_PATTERN.findall(text.lower()):
        if "\u4e00" <= run[0] <= "\u9fff":
            # 中文连续段：相邻两字切 bigram
            terms.extend(run[i:i + 2] for i in range(len(run) - 1))
        else:
            # 英文/数字：整段当一个 term
            terms.append(run)
    return terms


def build_index(chunks: list[dict]) -> dict:
    """对 chunk 列表建 BM25 索引。

    返回结构：
    {
        "N": 文档数,
        "avgdl": 平均文档长度,
        "chunks": {chunk_id: {"path", "start_line", "end_line", "text"}},
        "doc_len": {chunk_id: dl},
        "postings": {term: {chunk_id: tf}},
    }

    tokenize 后没有 term 的块不进入索引，也不计入 N / avgdl。
    """
    docs = {}
    doc_len = {}
    postings = {}

    for chunk in chunks:
        text = chunk.get("text")
        if not isinstance(text, str):
            continue
        terms = tokenize(text)
        if not terms:
            continue

        chunk_id = chunk["id"]
        docs[chunk_id] = {
            "path": chunk.get("path"),
            "start_line": chunk.get("start_line"),
            "end_line": chunk.get("end_line"),
            "text": text,
        }
        doc_len[chunk_id] = len(terms)

        for term, tf in Counter(terms).items():
            postings.setdefault(term, {})[chunk_id] = tf

    n = len(docs)
    avgdl = sum(doc_len.values()) / n if n else 0.0
    return {
        "N": n,
        "avgdl": avgdl,
        "chunks": docs,
        "doc_len": doc_len,
        "postings": postings,
    }


def search(index: dict, query: str, top_k: int = 5) -> list[dict]:
    """按 BM25 给包含查询 term 的 chunk 打分，返回分数最高的 top_k 条。"""
    query_terms = set(tokenize(query))
    if not query_terms or top_k <= 0:
        return []

    n = index["N"]
    avgdl = index["avgdl"]
    if n == 0 or avgdl <= 0:
        return []

    postings = index["postings"]
    doc_len = index["doc_len"]
    scores = {}

    for term in query_terms:
        term_postings = postings.get(term)
        if not term_postings:
            continue
        df = len(term_postings)
        idf = log(1 + (n - df + 0.5) / (df + 0.5))
        for chunk_id, tf in term_postings.items():
            length_norm = 1 - B + B * doc_len[chunk_id] / avgdl
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (
                idf * tf * (K1 + 1) / (tf + K1 * length_norm)
            )

    # 分数降序；同分按 chunk_id 升序，保证结果稳定。
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:top_k]

    results = []
    for chunk_id, score in ranked:
        doc = index["chunks"][chunk_id]
        results.append({
            "id": chunk_id,
            "path": doc["path"],
            "start_line": doc["start_line"],
            "end_line": doc["end_line"],
            "text": doc["text"],
            "score": score,
        })
    return results
