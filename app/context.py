import json

CONTEXT_BUDGET: int = 24000
TOOL_RESULT_LIMIT: int = 2000

def estimate_tokens(text: str) -> int:
    return 0 if text is None else len(text)


def estimate_messages_tokens(messages: list[dict]) -> int:
    res: int = 0
    for msg in messages:
        res += estimate_tokens(msg.get("content"))
        if msg.get("tool_calls"):
            res += estimate_tokens(json.dumps(msg.get("tool_calls")))
    return res


def split_units(messages: list[dict]) -> list[tuple[int, int, int]]:
    """把消息按「不可拆分的单元」切开，返回 [(start, end, tokens), ...]。

    单元的定义：
    - assistant(tool_calls) + 紧随其后的全部 tool 消息，算一个单元；
    - 其余消息各自算一个单元。

    这样做而不是在循环里现算下标，是因为 `assistant 后面跟几个 tool` 的配对关系
    是协议硬约束，拆散会让请求直接被拒。先切好单元，后面只做「留 / 丢」决策。
    """
    units = []
    i = 0
    while i < len(messages):
        end = i + 1
        if messages[i].get("role") == "assistant" and messages[i].get("tool_calls"):
            while end < len(messages) and messages[end].get("role") == "tool":
                end += 1
        units.append((i, end, estimate_messages_tokens(messages[i:end])))
        i = end
    return units


def trim_messages(messages: list[dict], budget: int = CONTEXT_BUDGET) -> list[dict]:
    """在预算内返回一份新的消息列表；原列表不修改。

    优先级：system 和首条 user（任务本身）永不删除 > 从最旧的单元开始处理 >
    先截断超长 tool 结果，截断够用就停，不够再丢整个单元。
    """
    units = split_units(messages)

    # 永不删除的单元：system，以及第一条 user（它就是任务，删了模型不知道要干什么）
    protected = set()
    seen_user = False
    for start, _, _ in units:
        role = messages[start].get("role")
        if role == "system":
            protected.add(start)
        elif role == "user" and not seen_user:
            seen_user = True
            protected.add(start)

    total_tokens = sum(tokens for _, _, tokens in units)
    if total_tokens <= budget:
        return list(messages)

    dropped = set()    # 被整单元丢弃的单元起点
    replaced = {}      # 被截断的消息下标 -> 新的 content

    for start, end, tokens in units:
        if total_tokens <= budget:
            break
        if start in protected:
            continue

        # 先尝试只截断这个单元里的超长 tool 结果，尽量保住整轮对话
        cut = 0
        new_contents = {}
        for i in range(start, end):
            if messages[i].get("role") != "tool":
                continue
            content = messages[i].get("content") or ""
            if len(content) > TOOL_RESULT_LIMIT:
                cut += len(content) - TOOL_RESULT_LIMIT
                new_contents[i] = content[:TOOL_RESULT_LIMIT] + f"…[已截断，原长 {len(content)} 字符]"

        if cut and total_tokens - cut <= budget:
            total_tokens -= cut
            replaced.update(new_contents)
        else:
            total_tokens -= tokens
            dropped.add(start)

    result = []
    for start, end, _ in units:
        if start in dropped:
            continue
        for i in range(start, end):
            if i in replaced:
                result.append({**messages[i], "content": replaced[i]})
            else:
                result.append(messages[i])
    return result
