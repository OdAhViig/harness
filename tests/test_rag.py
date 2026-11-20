"""RAG 切分规格测试：加载范围、行号映射、窗口长度、重叠、id 唯一性。"""

import copy

from app import rag
from app.rag import chunk_all, chunk_document, load_documents


def make_doc(text, path="sandbox/docs/demo.md"):
    return {"path": path, "text": text}


def test_load_documents_scopes_to_root_and_sorts(monkeypatch, tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    (root / "b.txt").write_text("B", encoding="utf-8")
    (root / "a.md").write_text("A", encoding="utf-8")
    (root / "sub").mkdir()
    (root / "sub" / "c.md").write_text("C", encoding="utf-8")
    (tmp_path / "outside.md").write_text("OUT", encoding="utf-8")
    monkeypatch.setattr(rag, "PROJECT_ROOT", tmp_path)

    docs = load_documents(root)

    # 只读 root 下的 .md/.txt；path 相对项目根；按 path 排序
    assert [d["path"] for d in docs] == ["docs/a.md", "docs/b.txt", "docs/sub/c.md"]
    assert [d["text"] for d in docs] == ["A", "B", "C"]


def test_empty_document_has_no_chunks():
    assert chunk_document(make_doc("")) == []
    assert chunk_document({"path": "p"}) == []
    assert chunk_document({"path": "p", "text": None}) == []


def test_whitespace_only_document_has_no_chunks():
    # 只有空白的文档不应产出块
    assert chunk_document(make_doc("\n\n   \n")) == []


def test_short_document_single_chunk_line_range():
    chunks = chunk_document(make_doc("第一行\n第二行\n第三行"))

    assert len(chunks) == 1
    # 行号 1-based，整篇是第 1 到第 3 行
    assert (chunks[0]["start_line"], chunks[0]["end_line"]) == (1, 3)
    assert chunks[0]["text"] == "第一行\n第二行\n第三行"


def test_blank_lines_keep_one_based_line_numbers():
    chunks = chunk_document(make_doc("A\n\n\nB"))

    # 空行占行号但不占内容，首行仍是第 1 行，末行是第 4 行
    assert (chunks[0]["start_line"], chunks[0]["end_line"]) == (1, 4)


def test_chunk_ending_at_newline_does_not_claim_next_line():
    chunks = chunk_document(make_doc("AAAA\nBBBB\nCCCC"), max_chars=5, overlap=0)

    # 末尾换行属于上一行，不能把下一行算进引用范围
    assert (chunks[0]["start_line"], chunks[0]["end_line"]) == (1, 1)
    assert chunks[0]["text"] == "AAAA\n"
    assert (chunks[1]["start_line"], chunks[1]["end_line"]) == (2, 2)


def test_chunk_text_within_max_chars():
    chunks = chunk_document(make_doc("长" * 1500), max_chars=600, overlap=100)

    assert len(chunks) == 3
    # 单块总量（含重叠部分）不得超过 max_chars
    assert all(len(c["text"]) <= 600 for c in chunks)


def test_adjacent_chunks_share_overlap():
    text = "0123456789" * 200
    chunks = chunk_document(make_doc(text), max_chars=600, overlap=100)

    assert chunks[0]["text"][-100:] == chunks[1]["text"][:100]


def test_concatenated_chunks_reconstruct_text():
    text = "".join(chr(ord("a") + i % 26) for i in range(2000))
    chunks = chunk_document(make_doc(text), max_chars=300, overlap=50)

    merged = chunks[0]["text"]
    for c in chunks[1:]:
        merged += c["text"][50:]
    assert merged == text


def test_ids_unique_for_long_single_line():
    chunks = chunk_document(make_doc("x" * 3000), max_chars=600, overlap=100)

    # 单行被切多块时行号区间相同，id 仍必须唯一
    assert len(chunks) == 6
    ids = [c["id"] for c in chunks]
    assert len(ids) == len(set(ids))


def test_id_contains_path_and_sequence():
    chunks = chunk_document(make_doc("短文"), max_chars=100, overlap=10)

    assert chunks[0]["id"].startswith(chunks[0]["path"] + ":")
    assert chunks[0]["id"].endswith("#0")


def test_input_document_not_mutated():
    doc = make_doc("A\n\nB\nC")
    snapshot = copy.deepcopy(doc)

    chunk_document(doc)

    assert doc == snapshot


def test_chunk_all_keeps_document_order():
    docs = [
        make_doc("A" * 700, "sandbox/docs/a.md"),
        make_doc("B" * 700, "sandbox/docs/b.md"),
    ]

    chunks = chunk_all(docs, max_chars=600, overlap=100)

    paths = [c["path"] for c in chunks]
    assert paths == sorted(paths)
    assert paths[0] == "sandbox/docs/a.md"
    assert paths[-1] == "sandbox/docs/b.md"


def test_zero_overlap_does_not_duplicate():
    text = "x" * 1300

    chunks = chunk_document(make_doc(text), max_chars=600, overlap=0)

    assert "".join(c["text"] for c in chunks) == text
