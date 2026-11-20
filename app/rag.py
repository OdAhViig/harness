from pathlib import Path
import bisect

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = PROJECT_ROOT / "sandbox" / "docs"

CHUNK_MAX_CHARS = 600
CHUNK_OVERLAP = 100

def load_documents(root: Path = DOCS_ROOT) -> list[dict]:
    """递归读取 .md/.txt，返回 [{"path", "text"}]，按 path 排序。"""
    res = []
    for file in root.rglob("*.md"):
        res.append({"path": f"{file.relative_to(PROJECT_ROOT)}", "text": file.read_text(encoding="utf-8")})
    for file in root.rglob("*.txt"):
        res.append({"path": f"{file.relative_to(PROJECT_ROOT)}", "text": file.read_text(encoding="utf-8")})
    res.sort(key=lambda item: item["path"])
    return res


def chunk_document(
    doc: dict,
    max_chars: int = CHUNK_MAX_CHARS,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """按字符窗口切分文档（相邻窗口重叠 overlap 字符），返回带 id / path / start_line / end_line / text 的列表。"""
    res = []
    path = doc.get("path")
    text = doc.get("text")
    if not isinstance(text, str):
        return res
    lines = [ln.rstrip() for ln in text.splitlines()]
    if not lines:
        return res
    flat = ""
    line_starts = []
    for index, line in enumerate(lines):
        if index > 0:
            flat += "\n"
        # 记录本行第一个字符在 flat 中的下标，而不是它前面那个换行符
        line_starts.append(len(flat))
        flat += line
    if max_chars <= 0:
        raise ValueError("max_chars 必须大于 0")
    if overlap < 0 or overlap >= max_chars:
        raise ValueError("overlap 必须在 [0, max_chars) 内")
    step = max_chars - overlap
    char_start = 0
    while char_start < len(flat):
        char_end = min(char_start + max_chars, len(flat))
        chunk = flat[char_start: char_end]
        start_line = bisect.bisect_right(line_starts, char_start)
        end_line = bisect.bisect_right(line_starts, char_end - 1)
        if chunk.strip():
            res.append({
                # 行号区间在同一行被切多块时会重复，追加文档内序号保证唯一。
                "id": f"{path}:{start_line}-{end_line}#{len(res)}",
                "path": doc.get("path"),
                "start_line": start_line,
                "end_line": end_line,
                "text": chunk
            })
        if char_end == len(flat):
            break
        char_start += step




    


    # start: int = 0
    # end: int = 0
    # chunk = ""
    # prefix = ""
    # for index, line in enumerate(lines):
    #     while len(line) > 0:
    #         if chunk == "":
    #             start = index + 1
    #             chunk = prefix

    #         end = index + 1
        
    #         if len(chunk + line) <= max_chars:
    #             chunk += line
    #             line = ""
    #             if (index + 1) == len(lines):
    #                 res.append({
    #                     "id": "", 
    #                     "path": doc.get("path"), 
    #                     "start_line": start, 
    #                     "end_line": end, 
    #                     "text": chunk
    #                 })
    #         else:
    #             rest_len = max_chars - len(chunk)
    #             chunk += line[:rest_len]
    #             res.append({
    #                 "id": "", 
    #                 "path": doc.get("path"), 
    #                 "start_line": start, 
    #                 "end_line": end, 
    #                 "text": chunk
    #             })
    #             prefix = chunk[-overlap:]
    #             line = line[rest_len:]
    #             chunk = ""
    return res


def chunk_all(
    docs: list[dict],
    max_chars: int = CHUNK_MAX_CHARS,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """对每份文档切分并拼接，保持文档顺序。"""
    res = []
    for doc in docs:
        res.extend(
            chunk_document(
                doc,
                max_chars,
                overlap
            )
        )
    return res