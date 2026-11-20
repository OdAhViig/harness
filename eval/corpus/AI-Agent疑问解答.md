# AI Agent 学习 · 疑问解答

> 用途：收集学习过程中所有概念性疑问与解答，避免答案散落在对话里。
> 建立日期：2026-11-13 · 最近更新：2026-11-13

## 归档规则

1. 用户每提出一个概念性疑问，回答完**立即**追加到本文档，不停留在对话中。
2. 一个问题一个 `###` 小节，格式：**问** → **答**（一句话结论）→ 展开。
3. 按**主题**分组，不按时间排序；同主题的新问题并入已有小节，不重复开节。
4. `AI-Agent学习进度.md` 只记「做了什么」，本文档只记「问过什么」，两边不重复。
5. 已回答过的问题不再重复解释，直接指回本文档对应小节。
6. 文档超过约 800 行时按主题拆成多个文件，本文件保留索引。

## 索引

| 主题 | 小节 |
|---|---|
| HTTP 与流式 | [1.1](#11-content-type-与-content-length) · [1.2](#12-encodeuricomponent-与-stream-true) · [1.3](#13-流式-http-与-sse) · [1.4](#14-流式-http-与-keep-alive) · [1.5](#15-streamingresponse-改的是响应) · [1.6](#16-invalid-http-request-received) |
| Python 语言机制 | [2.1](#21-yield-from-与-for-循环) · [2.2](#22-iterator-类型为什么宽松) · [2.3](#23-print-的颜色空-print-与-flush) · [2.4](#24-切片-200) · [2.5](#25-字典解包) · [2.6](#26-model_dump) · [2.7](#27-直接运行脚本找不到-app) · [2.8](#28-root--path-是什么意思) · [2.9](#29-with-pytestraises-的-with) · [2.10](#210-relative_to-与-is_relative_to) · [2.11](#211-模块级常量与-monkeypatch) · [2.12](#212-lambda-是什么) · [2.13](#213-from-import-是复制对象吗) · [2.14](#214-class-继承__init__-与-self) · [2.15](#215-类型注解与-pathpath) · [2.16](#216-staticmethod-与-classmethod) · [2.17](#217-from-import-与-import-module) · [2.18](#218-裸-except-会捕获什么) · [2.19](#219-实例方法类方法的首个参数能省略吗) · [2.20](#220-argparse-是什么) · [2.21](#221-真值判断与-get-返回-none) · [2.22](#222-keyerror-是什么) · [2.23](#223-默认参数为什么还会传进-list) |
| FastAPI 与 pytest | [3.1](#31-pytest-的参数从哪来为什么没有类型) · [3.2](#32-toolpytestini_options-的层级) · [3.3](#33-pytestfixture-的作用范围与命名) · [3.4](#34-pytest-找不到-app-包) · [3.5](#35-不包-write_input-怎么替换内置-input) |
| 工程化 | [4.1](#41-venv-是什么) · [4.2](#42-依赖包各自的作用) · [4.3](#43-toml-是什么) · [4.4](#44-git-仓库边界) · [4.5](#45-pip-的-ssl-证书错误) · [4.6](#46-隐式契约与显式设计) · [4.7](#47-zsh-粘贴多行文本的问题) · [4.8](#48-边扫边拼的问题怎么提前发现和拆解) |
| Agent 与 Tool Calling | [5.1](#51-tool_schemas-与-tools) · [5.2](#52-为什么一条用户消息要多次-ask) · [5.3](#53-messages-每一条的含义) · [5.4](#54-模型是请求调用不是调用) · [5.5](#55-步数上限是什么) · [5.6](#56-ask-是自定义函数名吗) · [5.7](#57-事件日志为什么用-type-而不是-role) · [5.8](#58-to_message-为什么只转-assistant) · [5.9](#59-assistant-消息与-tool_call-的配对) · [5.10](#510-日志对象为什么用参数传而不是全局变量) |
| 上下文工程 | [6.1](#61-tool_result_limit-为什么存在截断不会影响结果吗) · [6.2](#62-为什么不无条件调用-trim) · [6.3](#63-预算没超时要不要截断工具结果) · [6.4](#64-新的-trim_messages-是什么逻辑) |
| 检索与 RAG | [7.1](#71-bigram-与-embedding-是什么) · [7.2](#72-rag-是什么在-agent-调用里处于哪里) · [7.3](#73-rag-要做到什么层次对-agent-开发重要吗) · [7.4](#74-chunk_overlap-是干什么的) · [7.5](#75-bm25-检索基础从分词到打分) · [7.6](#76-token-的三层含义检索-term模型-token字符估算) · [7.7](#77-检索评测集是什么recall-与-mrr-怎么理解) |

---

## 一、HTTP 与流式

### 1.1 content-type 与 content-length

**问**：浏览器 Network 里 `/chat/stream` 的响应头是 `content-type: text/plain`，没有 `content-length`，这两点代表什么？

**答**：前者说明响应体是纯文本；后者说明长度未知，HTTP/1.1 必须改用 `transfer-encoding: chunked` 分块返回，每块到达就能交给前端，这是逐字显示的前提。

展开：

- `content-type` 决定浏览器怎么解释响应体。`text/html` 会渲染标签，`text/plain` 显示原文，`application/json` 会被工具解析。
- HTTP/1.1 判断响应体结束只有两种方式：

  | 方式 | 前提 | 结束标志 |
  |---|---|---|
  | `content-length: 1234` | 发送前知道总字节数 | 收满 1234 字节 |
  | `transfer-encoding: chunked` | 不知道总长度 | 收到长度为 0 的块 |

- `StreamingResponse` 的生成器在模型说完之前不知道总字节数，所以只能 chunked。
- 如果错误地给了 `content-length`，浏览器会等满才把数据交给 JS，逐字显示就消失了。这也是 nginx 反向代理缓冲会把流式接口变成一次性返回的原因。

### 1.2 encodeURIComponent 与 { stream: true }

**问**：这两个各解决什么问题？

**答**：前者解决中文在 URL 里必须百分号编码；后者解决一个汉字的 UTF-8 字节被切在两个 chunk 之间。

展开：

- URL 里的中文不编码，服务器解析请求行失败，报 `Invalid HTTP request received`。`encodeURIComponent("用")` → `%E7%94%A8`。
- 一个汉字在 UTF-8 里占 3 字节，可能第 1 个字节在第 1 块、后 2 个字节在第 2 块。直接解码第一块会得到替换字符 `�`。
- `TextDecoder` 加 `{ stream: true }` 后，会把不完整的尾巴留在内部缓冲，等下一块拼完整再输出。

三层各管各的：URL 层百分号编码 → HTTP body 层 UTF-8 字节 → JS 层增量解码。

### 1.3 流式 HTTP 与 SSE

**问**：流式 HTTP 和 SSE 有什么区别？

**答**：SSE 是流式 HTTP 之上的一种内容格式，流式 HTTP 是传输层行为。

| | 流式 HTTP | SSE |
|---|---|---|
| 层次 | 传输 | 内容格式 |
| 标志 | `transfer-encoding: chunked` | `content-type: text/event-stream` |
| 数据单位 | 任意字节块 | `data: ...\n\n` 事件 |
| 客户端 API | `fetch` + `body.getReader()` | `EventSource` |

SSE 必须跑在流式 HTTP 上，但流式 HTTP 不一定是 SSE。

### 1.4 流式 HTTP 与 keep-alive

**问**：流式 HTTP 和 keep-alive 的 HTTP 有什么区别？

**答**：两个层次。keep-alive 管连接复用，流式管单个响应如何分块返回。

- HTTP/1.0 默认每个请求新建一条 TCP 连接。
- keep-alive 让一条 TCP 连接上连续跑多个请求，省掉握手开销。
- 流式是**一个响应内部**边计算边发送多个块。
- 两者正交，可以同时存在：一条 keep-alive 连接上，先跑一个普通请求，再跑一个流式请求。

### 1.5 StreamingResponse 改的是响应

**问**：`StreamingResponse` 是把请求结果变成流式了吗？

**答**：是把**响应**变成流式。请求仍是普通的 GET，没有任何变化。

### 1.6 Invalid HTTP request received

**问**：curl 请求时报这个错怎么解决？

**答**：URL 里的中文没有百分号编码。

```bash
curl -N -G "http://127.0.0.1:8000/chat/stream" --data-urlencode "q=用三句话解释什么是Agent"
```

- `-G`：把 `--data-urlencode` 的内容拼到 query string，而不是放进请求体。
- `--data-urlencode`：自动做百分号编码，相当于前端的 `encodeURIComponent`。
- `-N`：关掉 curl 的缓冲，边收边打印。

---

## 二、Python 语言机制

### 2.1 yield from 与 for 循环

**问**：yield 的结果可以用 `yield from` 读取，iterator 的结果不可以吗，只能 `for chunk in` 吗？

**答**：都可以。`yield from it` 就是 `for x in it: yield x` 的简写。

```python
def a():
    for x in it:
        yield x

def b():
    yield from it      # 与 a 等价
```

`yield from` 还额外支持 `send()` / `throw()` 的传递，但在普通流式场景里用不上。

### 2.2 Iterator 类型为什么宽松

**问**：`Iterator` 这个返回类型，既可以返回这个对象，也可以把值一个个 yield 出去吗？为什么这块的类型很宽松，编译器做了什么？

**答**：Python 没有编译期类型检查，注解只是元数据；生成器函数调用后返回一个 generator 对象，它实现了 Iterator 协议。

- 函数体里有 `yield`，这个函数就是**生成器函数**。调用它不执行函数体，只返回一个 generator 对象。
- generator 对象满足迭代协议（有 `__iter__` 和 `__next__`），所以它就是 `Iterator`。
- `-> Iterator[str]` 只是告诉人和 IDE「这个函数返回的东西能迭代出字符串」，CPython 执行时不检查。
- 注解真正被消费的场景：FastAPI 的路由参数、pydantic 模型、mypy/pyright 静态检查。

### 2.3 print 的颜色、空 print 与 flush

**问**：`print` 怎么加颜色？`print()` 这个空打印什么作用？`flush` 删掉看不出作用？

**答**：

- 颜色靠 ANSI 转义序列，不是 `print` 的功能：`print(f"\033[36m{text}\033[0m")`。`\033[36m` 是青色，`\033[0m` 复位。
- `print()` 输出一个换行符，用于分段或让光标落到下一行。
- `flush=True` 让内容立即写出缓冲区。终端是行缓冲，换行时就刷了，所以看不出差别；重定向到文件时是块缓冲，不 flush 会攒满一块才写。

### 2.4 切片 :200

**问**：`result[:200]` 中，后面的 `:200` 是什么？

**答**：切片，取前 200 个字符。

```python
s[:3]     # 前 3 个
s[2:]     # 从第 2 个到末尾
s[-3:]    # 最后 3 个
```

越界不报错，自动截到末尾。对列表同样适用。Swift 对应 `String.prefix(200)`。

### 2.5 字典解包

**问**：`TOOLS[name](**args)` 是什么用法，`**` 是什么？

**答**：字典解包，把 `{"path": "x"}` 拆成关键字参数 `path="x"`。

```python
TOOLS["read_file"](**{"path": "README.md"})
# 等价于
read_file(path="README.md")
```

机制：

- 函数定义 `def read_file(path)` 时，形参名存在 code object 的 `co_varnames` 里，是运行时可查的字符串。
- `**` 把字典的 key 当作参数名、value 当作实参。
- key 必须是字符串（否则 `TypeError: keywords must be strings`），且必须和形参名匹配（否则 `unexpected keyword argument`）。
- 源码里的 `path="x"` 和 `**{"path": "x"}` 在解释器里走同一条参数绑定逻辑。

`*` 是解包列表成位置参数：`f(*[1, 2])` 等价 `f(1, 2)`。

**字典字面量里的 `**`：合并与浅复制**

```python
event = {**event, "ts": "..."}
```

- dict 字面量里的 `**` 表示「把右边映射的键值展开进来」，多个映射合并，后面的同名键覆盖前面的。
- 这个表达式创建一个**新 dict**，原 `event` 不变，所以能达到「复制一份再修改」的效果。
- 新 dict 的 value 还是原对象的引用，属于浅拷贝：嵌套的 list / dict 仍被共享。事件会立刻被 JSON 序列化，这个场景不需要深拷贝。
- 等价写法：`dict(event, ts="...")`、`event | {"ts": "..."}`（3.9+）、`{**event}`。

**Python 有没有值类型 / copy-on-write**

- Python 的变量全是引用，赋值只复制指针；对象是否「像值」取决于它可不可变。
- `int`、`str`、`tuple` 不可变，看起来像值语义：`a = b` 后「改 b」其实是重新绑定，不影响 `a`。
- `list`、`dict` 和自定义对象可变：`a = b` 后两边指向同一对象，`a.append()` 对两边都可见。
- 没有通用的 copy-on-write；要独立副本必须显式 `copy.copy`（浅）或 `copy.deepcopy`（深）。
- Swift 对照：Swift 的 struct / Array 有值语义和 COW；Python 默认是引用语义。

### 2.6 model_dump

**问**：`model_dump()` 是干嘛的？

**答**：把 pydantic 模型对象转成普通 Python 字典。

- SDK 返回的 `msg` 是 `ChatCompletionMessage` 对象，不是字典。
- `messages` 参数最终要序列化成 JSON 发出去，字典是最直接的形状。
- `exclude_none=True` 去掉值为 `None` 的字段，但**不会**去掉空字符串和空列表。

### 2.7 直接运行脚本找不到 app

**问**：直接运行 `scripts/xxx.py` 报 `No module named 'app'`，能不能不改运行路径，改代码解决？

**答**：有三种解法。

| 方案 | 做法 | 代价 |
|---|---|---|
| 改代码 | 脚本顶部 `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` | 每个脚本抄一遍 |
| 改运行方式 | 从项目根用 `python -m scripts.xxx` | 必须在项目根执行 |
| 装成包 | `pip install -e .` | 需要配 `[build-system]` 和 `[project]` |

原因：`python scripts/x.py` 时 `sys.path[0]` 是 `scripts/` 目录；`python -m scripts.x` 时 `sys.path[0]` 是当前工作目录。

当前约定：M6 之前统一下用 `python -m scripts.xxx`，M6 收尾再做 `pip install -e .`。

### 2.8 (ROOT / path) 是什么意思

**问**：`(ROOT / path)` 里的 `/` 是什么意思？

**答**：`/` 不是除法，是 `pathlib.Path` 重载的「拼接路径」运算符，等价于 Swift 的 `URL.appendingPathComponent`。

展开：

- `ROOT` 是 `Path` 对象（`Path(__file__).resolve().parent.parent`），`Path` 实现了 `__truediv__`，所以 `a / b` 会返回新路径。
- `ROOT / "app"` → `/Users/finlaas/my/deepseek-harness/app`。
- 和字符串 `ROOT + "/" + path` 的区别：`Path` 自动处理分隔符，不会拼出 `//`；右侧是绝对路径时直接丢弃左侧（`Path("/a") / "/b"` → `/b`）。
- `.resolve()` 把结果变成绝对路径，并消解 `..` 和符号链接。越界校验必须基于 resolve 后的路径：

  ```text
  ROOT / "../secret"         → .../deepseek-harness/../secret
  (ROOT / "../secret").resolve() → /Users/finlaas/my/secret
  is_relative_to(ROOT)       → False → 判为越界
  ```

- 如果只拼接不 resolve，`..` 还留在字符串里，`is_relative_to` 无法识别出跑到了父目录。
- 分工记法：`/` 负责拼，`.resolve()` 负责规整，`is_relative_to` 负责判断。

### 2.9 with pytest.raises 的 with

**问**：`with pytest.raises(...)` 里的 `with` 是什么用法？

**答**：`with` 是上下文管理器语法，套在 `pytest.raises` 上用来「声明这段代码应该抛出指定异常」，并自动捕获、校验、吞掉它。

展开：

- `with` 要求对象实现 `__enter__` / `__exit__`。`pytest.raises(ValueError)` 返回的对象实现了这两个方法。
- 进入块时调用 `__enter__`，返回 `ExceptionInfo`；块内代码抛异常时调用 `__exit__`，此时它检查异常类型是否匹配：
  - 匹配 → 返回 True，异常被吞掉，程序继续往下走
  - 不匹配 → 返回 False，异常继续向外抛
  - 块内没抛异常 → `__exit__` 抛 `Failed: DID NOT RAISE`，测试失败
- `match="越界"` 是用正则去匹配 `str(异常)`，类型对但文案不对也会失败。
- 等价的朴素写法：

  ```python
  try:
      list_file("..")
  except ValueError as e:
      assert "越界" in str(e)
  else:
      assert False, "应该抛 ValueError"
  ```

- `with` 与 `open` 的相同点：都保证退出时执行清理/校验；不同点在于 `open` 的 `__exit__` 只负责关文件，`pytest.raises` 还负责断言异常类型。
- 需要拿异常对象时写 `with pytest.raises(ValueError) as exc_info:`，之后用 `exc_info.value` 访问。

### 2.10 relative_to 与 is_relative_to

**问**：`if not target.relative_to(ROOT)` 为什么不能用来判断越界？

**答**：`relative_to` 返回 `Path` 对象，越界时抛 `ValueError`；判断路径归属要用返回 bool 的 `is_relative_to`。

展开：

- `Path` 对象恒为真值，包括 `Path(".")`，所以 `not Path(...)` 永远是 `False`，这个判断永远不成立。
- 路径在 `ROOT` 外面时，`relative_to` 不会返回「假值」，而是直接抛 `ValueError: ... is not in the subpath of ...`。
- 正确写法：

  ```python
  if not target.is_relative_to(ROOT):
      raise PermissionError(f"路径越界：{path}")
  rel = target.relative_to(ROOT)   # 只有确认在内部之后才调用
  ```

- `is_relative_to` 返回 bool，Python 3.9+ 可用。
- 记法：`is_relative_to` 用来问「在不在里面」；`relative_to` 用来取「相对路径是什么」，前提是已经在里面。

### 2.11 模块级常量与 monkeypatch

**问**：测试里已经 `monkeypatch.setattr(permissions, "ROOT", tmp_path)`，为什么 `write_file` 还是判越界？

**答**：项目里有两个 `ROOT`，测试只替换了 `app.permissions` 的那份，`app.tools` 里的那份没变。

展开：

- `from app.permissions import ensure_safe_path` 导入的是函数对象，函数执行时读的是自己模块的全局变量，所以 patch `permissions.ROOT` 有效。
- `app.tools` 自己又写了 `ROOT = Path(__file__).resolve().parent.parent`，这是另一个模块全局，patch 不到。
- 结果：`ensure_safe_path` 认为 `tmp_path/note.txt` 合法，`write_file` 里第二个守卫却用旧 `ROOT` 判断，前后不一致。
- 修法：删掉重复守卫，让 `ensure_safe_path` 成为唯一判据；长期解法是 `ROOT` 只定义一次。
- 测试侧更稳的做法：写完后直接读 `tmp_path / "note.txt"`，不要经过 `read_file`（它用的是 `tools.ROOT`）。

### 2.12 lambda 是什么

**问**：`lambda _: "y"` 是什么用法？为什么参数里看不到函数定义？

**答**：`lambda 参数: 返回值` 是匿名函数表达式，整个表达式的值就是一个函数对象，可以直接作为参数传走。

展开：

- 它等价于：

  ```python
  def fake_input(_):
      return "y"
  ```

- 参数列表照常写；`_` 是「这个参数我不使用」的惯用名。`input(prompt)` 会带一个参数调用，所以替身也必须接受一个参数，否则 `TypeError`。
- 只能写一个表达式，不能有语句、多行结构或 `return` 关键字；冒号后面的表达式结果就是返回值。
- 常见用途：`sorted(..., key=lambda x: x.age)`、monkeypatch 替身、一次性回调。
- Swift 类比：`{ _ in "y" }`。
- 需要断言或多行逻辑时用 `def`，lambda 里写不了 `assert`。

### 2.13 from import 是复制对象吗

> **状态：暂未完全理解，先记录结论，不纠结。** 后续遇到内存模型、GC、闭包相关场景时再回头深入。当前只需记住操作层结论：`from x import y` 是导入时快照引用；函数体读模块全局是运行时动态查。

**问**：`from x import y` 之后，`y` 是新副本吗？为什么导入的函数内部读 `ROOT` 会被 patch 影响，而模块里 `from ... import ROOT` 的名字不会？

**答**：`from x import y` 只新建一个名字绑定，不复制对象；函数和常量都还是同一个对象，区别在于之后改的是「哪个名字」。

展开：

- 模块是对象。首次 import 执行模块代码，结果存进 `sys.modules`；再次 import 直接返回同一个模块对象，不会重新执行。
- `from app.permissions import ensure_safe_path` 做两件事：
  1. 导入 `app.permissions` 模块对象（走缓存）
  2. 在当前命名空间绑定 `ensure_safe_path = 模块.__dict__["ensure_safe_path"]`
- 赋值只复制**引用**，不复制对象。验证：

  ```python
  f is p.ensure_safe_path      # True，同一个函数对象
  f.__globals__ is vars(p)     # True，函数体里的全局名在定义模块里查
  ```

- 因此有两层容易混淆的行为：

  | 操作 | 结果 |
  |---|---|
  | `p.ensure_safe_path = 新函数` | 已 `from ... import` 的 `f` 仍指向旧函数，不受影响 |
  | `p.ROOT = 新路径` | 已被导入的 `ensure_safe_path` 内部读 `ROOT` **会**看到新值，因为它的 `__globals__` 就是 `p` 的命名空间 |
  | `p.ROOT = 新路径` | 另一个模块里 `from app.permissions import ROOT` 得到的 `ROOT` 仍指向旧对象 |

- 对象可变与不可变的差别：若源模块里是 `LIST`，`p.LIST.append(x)` 对所有引用可见；`p.LIST = 新列表` 只改源模块的名字。`Path` 不可变，所以只能靠重新绑定。
- `builtins` 同理。`from builtins import input` 把原始函数对象绑进模块命名空间，之后替换 `builtins.input` 不再影响它；裸调 `input()` 每次运行时才回落到 builtins，所以能拿到替换后的版本。
- 判断标准：**看名字在哪个命名空间、什么时候查**。
  - `x.y`：每次运行时查 `x` 的命名空间 → patch `x.y` 生效
  - `from x import y` 得到的 `y`：导入时已绑定 → patch `x.y` 不生效
- 内存角度：没有产生副本，只有一个对象和多份引用，赋值让引用计数 +1；模块代码只执行一次。Swift 类比：引用类型赋值，`from x import y` 相当于 `let y = x.y`。
- 实用结论：测试里要替换「函数体内读的模块常量」，patch **定义模块**；要替换「调用方手里的函数引用」，patch **调用方命名空间**，或改成 `module.func()` 的调用方式。

#### 整体模型：对象、名字、命名空间

**对象**：Python 里所有值都是堆上的对象，对象头至少含引用计数和类型指针。字符串、整数、函数、模块、类都是对象。

**名字**：变量不是装对象的盒子，只是命名空间字典里的一个键，值是指向对象的引用。

```text
模块.__dict__ = { "ROOT": → Path对象A, "ensure_safe_path": → 函数对象F }
```

**赋值**：`x = obj` 只做「把 x 这个键指向 obj」，引用计数 +1，不复制对象。

**查找**：函数执行时按 LEGB 查名字——局部 → 闭包 → 模块全局 → builtins。函数对象自带 `__globals__`，指向**定义它**的模块的字典，所以函数体内读 `ROOT` 时永远去定义模块找。

**内存管理**：

- 引用计数归零立即释放（CPython 的主机制）。
- 循环引用靠分代 GC 兜底回收。
- 模块对象被 `sys.modules` 长期持有，模块字典里的对象因此不会被释放；即使别处重新绑定名字，旧对象仍被其余引用保活。
- Python 3.12 对字面量字符串、小整数引入 immortal 对象，引用计数显示为极大值，不会被回收；分析引用时不要被这个数字迷惑。

**import 全流程**：

1. 查 `sys.modules`，命中就直接复用，不重新执行。
2. 未命中则由 finder 沿 `sys.path` 找模块，生成 spec。
3. 创建模块对象和它的 `__dict__`，**先注册进 `sys.modules`**，再执行模块代码（循环 import 时对方可能看到半成品）。
4. 模块顶层语句在模块字典里执行，函数、常量被定义并绑定进去。
5. 回到导入方执行绑定：
   - `import x` → 导入方命名空间里 `x` 指向模块对象
   - `from x import y` → 执行一次 `getattr(x, "y")`，把得到的对象引用绑定到导入方命名空间
   - `importlib.reload` 会重新执行模块代码，但**不会**更新其他模块里已 `from ... import` 的名字

**所以「y 在导入时就绑定了旧对象」的准确含义**：`from x import y` 在导入那一刻求值一次 `x.y`，把当时指向的对象引用存进导入方字典。之后 `x.y = 新对象` 改的是源模块字典里的键，导入方字典里的 `y` 不受影响。没有复制对象，只是复制了引用。

```python
m.ROOT = "new"           # 源模块改名
from demo import ROOT    # 导入时拿到旧对象 "old"
get_root()               # 函数体内动态查 m.__dict__ → "new"
m.LIST.append(2)         # 同一个列表对象被原地修改 → 两边都看到
m.LIST = [9]             # 源模块换新列表 → 导入方仍指旧列表
```

实测输出：

```text
from import 的 ROOT: old
函数读全局 ROOT: new
from import 的 LIST: [1, 2]
重绑后 LIST: [1, 2]
同一个函数对象: True
函数全局就是定义模块: True
```

**和 iOS block / Swift closure 的对照**：

| 机制 | 捕获方式 | 源变量重绑后 |
|---|---|---|
| ObjC block 捕获局部对象变量 | 复制指针并 retain | 块内仍是旧指针 |
| ObjC `__block` 变量 | 引用同一份存储 | 能看到变化 |
| Swift 闭包捕获局部 var | 捕获变量存储（引用） | 能看到变化 |
| Swift 捕获列表 `[y]` | 创建时快照 | 看不到变化 |
| Python `from x import y` | 导入时快照引用 | 看不到变化 |
| Python 函数读模块全局 | 每次调用时动态查 `__globals__` | 能看到变化 |

- `from x import y` 更接近「ObjC block 捕获对象指针」或「Swift 捕获列表 `[y]`」：拿到的是当时那个对象的引用。
- 函数读模块全局不属于闭包捕获，是运行时的全局查找，类似直接访问一个全局变量。
- Python 的闭包（嵌套函数引用外层局部变量）通过 `__closure__` 的 cell 实现，也是晚绑定；想要定义时快照，用默认参数：`def f(root=ROOT)`，默认值在 def 执行时求值。

**判断口诀**：先问「这个名字存在哪个字典里」，再问「什么时候查这个字典」。导入时绑定 = 快照；运行时查属性 = 实时。

### 2.14 class、继承、__init__ 与 self

**问**：class 不用继承基类吗？`__init__` 怎么定义，参数是否必须？为什么类里引用 `path` 要写 `self.path`？

**答**：Python 3 的类默认继承 `object`，不需要显式写基类；`__init__(self, ...)` 在实例化时自动调用，除 `self` 外的参数默认必传；方法内访问实例属性必须显式写 `self.`。

展开：

- `class EventLog:` 等价于 `class EventLog(object):`。只有需要复用行为或接口时才显式继承。
- `EventLog(path)` 的执行顺序：`__new__` 创建实例 → `__init__(实例, path)`。`self` 由 Python 自动传入。
- 参数规则和普通函数一致：没有默认值就必传；可以写默认值、`*args`、`**kwargs`。
- `def append(self, event)` 被调用时，`log.append(e)` 等价于 `EventLog.append(log, e)`。
- 类体不是「实例作用域」，不能裸写 `path` 访问实例属性；必须 `self.path`。
- `self` 不是关键字，只是约定名，换成 `this` 也能运行，但不要这么做。
- Swift 对照：Swift 的 `self` 隐式可用；Python 必须显式写进方法参数和属性访问。

### 2.15 类型注解与 Path(path)

**问**：`path` 已经标注为 `Path`，为什么赋值给 `self.path` 还要 `Path(path)`？

**答**：注解只服务于静态检查和阅读，运行时完全不校验；调用方传 `str` 也能进来，所以再包一层做归一化。

展开：

- `def f(path: Path)` 不会阻止 `f("logs/x.jsonl")`。
- `Path(Path(...))` 幂等，开销很小，能保证 `self.path` 一定是 Path。
- 调用点完全可信时可以省略；库边界和公共 API 建议保留防御。
- 需要真正的运行时校验，得显式写 `isinstance` 或 `try: Path(path) except TypeError`。
- 注解的消费者是 mypy / pyright / IDE，不是解释器。

### 2.16 staticmethod 与 classmethod

**问**：`@staticmethod` 是类方法吗？没有实例也能调用吗？

**答**：`@staticmethod` 是静态方法，挂在类命名空间上，不需要实例，也不自动接收 `self` 或 `cls`；`@classmethod` 才是类方法，第一个参数是 `cls`。

展开：

| 类型 | 第一个参数 | 调用方式 | 典型用途 |
|---|---|---|---|
| 实例方法 | `self` | `obj.m()` | 读写实例状态 |
| classmethod | `cls` | `Cls.m()` / `obj.m()` | 替代构造函数、访问类属性 |
| staticmethod | 无 | `Cls.m()` / `obj.m()` | 纯工具函数，逻辑上属于该类 |

- `EventLog.load(path)` 不需要实例，也不碰类属性，用 `staticmethod` 合适。
- `staticmethod` 本质就是普通函数，放在类里只是为了归属清晰。
- `classmethod` 的例子：`@classmethod def from_file(cls, path): return cls(path)`，子类调用时 `cls` 是子类。

### 2.17 from import 与 import module

**问**：loop 里为什么 `from app.events import ...`，直接 `import app.events` 然后 `app.events.xxx` 不行吗？

**答**：两种都行，纯风格选择；区别是名字绑定的方式不同，测试 patch 时要注意（见 2.13）。

展开：

- `from app.events import EventLog`：导入方命名空间多一个 `EventLog`，指向同一个类对象。
- `import app.events`：导入方多一个 `events` 模块引用，调用时每次查 `events.EventLog`。
- 取舍：短名简洁；模块前缀能避免重名、明确来源。
- 与 patch 的关系：`from ... import` 拿到的是快照，patch 源模块属性不会影响导入方已绑定的名字。
- 本项目选 `from ... import` 只是可读性偏好，不是语法要求。

### 2.18 裸 except 会捕获什么

**问**：`except:` 会把 `KeyboardInterrupt`、`SystemExit` 也捕获吗？try 里明明只有 JSON 解析可能报错。

**答**：裸 `except:` 捕获 `BaseException`，包括 `KeyboardInterrupt` 和 `SystemExit`；异常不只来自你预期的表达式，Ctrl-C 可能在 try 内任意两条字节码之间触发。

展开：

- 继承结构：`BaseException` → `Exception`；`KeyboardInterrupt`、`SystemExit`、`GeneratorExit` 直接继承 `BaseException`，不属于 `Exception`。
- `except Exception` 只捕获业务异常；裸 `except:` 连用户按 Ctrl-C、`sys.exit()` 都吞掉。
- 即使 try 里只有 `json.loads`，解释器可以在任意字节码边界检查信号并抛 `KeyboardInterrupt`，所以「这里不会抛别的异常」不成立。
- 吞掉 `KeyboardInterrupt` 的后果：Ctrl-C 没反应，循环继续读完文件，用户只能更强硬地杀进程。
- 正确写法是 `except json.JSONDecodeError`；需要兜底时用 `except Exception`，不要裸 `except:`。
- 兜底范围过大会掩盖编程错误（`NameError`、`TypeError`），bug 被静默吞掉，比崩溃更难查。

### 2.19 实例方法/类方法的首个参数能省略吗

**问**：`def append(event)` 不写 `self` 行不行？`@classmethod` 不写 `cls` 呢？

**答**：语法上能定义，但调用时的隐式传参会对不上，正常使用会 `TypeError`。

展开：

- 实例方法 `def m(self, x)`：`obj.m(1)` 调用时 Python 自动把 `obj` 作为第一个位置参数传入，实际执行 `m(obj, 1)`。
- 写成 `def m(x)` 少一个参数：`obj.m(1)` 等价 `m(obj, 1)`，多传一个 → `TypeError: takes 1 positional argument but 2 were given`。
- 但 `Cls.m(1)` 在 Python 3 里不做实例绑定，等价于 `m(1)`，反而能跑——此时它只是挂在类下的普通函数，不是实例方法。这个现象容易误导。
- `@classmethod` 无论通过类还是实例调用，装饰器都会把类作为第一个参数传入；`def m()` 少参数 → 一定 `TypeError`。
- `@staticmethod` 没有隐式参数，零参数完全合法。
- `self` / `cls` 只是约定名，改成 `this` / `klass` 语法上可行，但工具和阅读都会混乱。
- 判断标准：方法签名必须和「调用时隐式传入什么」匹配。

### 2.20 argparse 是什么

**问**：`argparse` 是做什么的？

**答**：标准库的命令行参数解析器，把 `--resume path` 这类参数解析成 Python 变量，顺带生成 `-h` 帮助和类型错误提示。

展开：

- 手写 `sys.argv` 要自己切分、判断长度、处理 `--x=y` 和 `--x y` 两种写法、处理 `-h`，还要自己做字符串到 `Path`/`int` 的转换。
- `argparse` 的 `add_argument("--resume", type=Path)` 声明「这个参数叫 resume，出现时把值转成 Path」；解析后通过 `args.resume` 访问，没传就是 `None`。
- 参数名里的 `--` 表示长选项，用户写 `--resume logs/a.jsonl`；`type=` 是转换函数，不是类型注解。
- 它只管解析，不做业务校验（比如文件是否存在要自己判断）。

**`--resume` 里的 `--` 是什么**

- `--name` 是 GNU 风格的长选项；`-r` 是短选项；不带前缀的是位置参数（如 `cp 源 目标`）。
- 分隔符是约定的语法，argparse 靠它区分选项和位置参数；写成 `"resume"`（没有 `--`）就成了位置参数，`args.resume` 不再存在。
- 调用形式两种等价：`--resume logs/a.jsonl` 和 `--resume=logs/a.jsonl`。
- 单独一个 `--` 表示「后面的都是位置参数」，不是选项。

**`ArgumentParser` 怎么用**

三步：

```python
parser = argparse.ArgumentParser(description="...")   # 1. 建解析器
parser.add_argument("--resume", type=Path)            # 2. 声明参数规则
args = parser.parse_args()                            # 3. 读 sys.argv[1:] 并按规则转换
```

`parse_args()` 返回 `Namespace` 对象，用 `args.参数名` 取值；没传且没设 `default` 就是 `None`。`-h/--help` 自动生成。真正的 main 逻辑写在 `if __name__ == "__main__": main()` 之后，这样被 import 时不会解析别人的命令行参数。

**命令行参数和「用户与 Agent 对话」是两层东西**

- 命令行参数：在终端启动程序时传给**程序本身**的开关（如 `--resume`），进程启动前由 shell 解析，Python 里从 `sys.argv` 读。
- 对话消息：程序跑起来之后，用户通过 HTTP / stdin / 聊天框传给**模型**的文本，存在 `messages` 里。
- 二者互不相干：`--resume` 不会发给模型，模型说的话也不会变成命令行参数。argparse 只管前者。
- 场景：所有 CLI 工具都用它（`git commit -m`、`pip install -r`、`pytest -v`）。我们的 `agent_loop.py` 用它决定「新开会话还是从日志恢复」。

**这段代码逐行拆**

```python
parser = argparse.ArgumentParser()
parser.add_argument("--resume", type=Path, help="从已有 JSONL 日志恢复")
parser.add_argument("--log", type=Path, help="新会话日志路径")
args = parser.parse_args()
```

- `argparse`：文件顶部 `import argparse` 导入的标准库模块；`argparse.ArgumentParser` 是模块里的一个**类**。
- `ArgumentParser()`：调用类 = 创建实例（和 `EventLog(path)` 一样），得到解析器对象，赋给变量 `parser`。规则必须挂在某个具体对象上。
- `parser.add_argument(...)`：调用对象的方法，给它**注册一条参数规则**。第一个字符串 `"--resume"` 是命令行里要敲的字面选项名。
- `type=Path`、`help="..."` 是**关键字参数**：`type` 告诉 argparse 拿到字符串后用 `Path(...)` 转一下（值是一个函数，不是类型注解）；`help` 只用于 `-h` 显示。
- `parser.parse_args()`：读取启动时的 `sys.argv[1:]`，按注册的规则解析，返回一个 `argparse.Namespace` 对象。

**为什么 `args` 可以 `.resume`**

- argparse 的约定：选项名去掉前导 `--` 就是属性名；名字里的 `-` 换成 `_`。所以 `--resume` → `args.resume`，`--dry-run` → `args.dry_run`。
- 属性和命令行里写没写无关：没传时属性仍然存在，值是 `None`（没设 `default` 的话）。
- 实测：

```
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument("--resume", type=Path)
>>> parser.parse_args(["--resume", "logs/a.jsonl"])
Namespace(resume=PosixPath('logs/a.jsonl'))
>>> parser.parse_args([])
Namespace(resume=None)
```

- 所以 `if args.resume:` 就是在问「用户启动时带没带 `--resume` 和路径」。True 走恢复分支，False 走新会话分支。

### 2.21 真值判断与 `.get()` 返回 None

**问**：「`None` 是假值，`if` 里直接跳过」是什么意思？为 `None` 时跳过不是符合逻辑吗？

**答**：是的，这正是想要的行为——`if` 体跳过的是「添加 `tool_calls` 这个键」这一步，消息本身照常追加。

展开：

- Python 在 `if` 里看的是「真值」：`None`、`False`、`0`、`0.0`、`""`、`[]`、`{}`、`()` 都算假，其余算真。
- `event.get("tool_calls")` 在键不存在时返回 `None`（而 `event["tool_calls"]` 会抛 `KeyError`）。所以：

```python
msg = {"role": "assistant", "content": ...}
if event.get("tool_calls"):          # 有且非空才进
    msg["tool_calls"] = event["tool_calls"]
res.append(msg)                      # 无论有没有 tool_calls 都追加
```

- 关键词是「添加键」被跳过，不是「这条消息」被跳过。区别在于 `res.append(msg)` 在 `if` 外面。
- 不写成 `msg["tool_calls"] = event.get("tool_calls")` 的原因：会得到 `"tool_calls": None`，序列化后是 `null`，API 可能直接拒绝；缺键和不带这个参数的语义才一致。

### 2.22 KeyError 是什么

**问**：`KeyError` 是什么意思？

**答**：用 `d[key]` 读一个不存在的键时抛的异常，属于「访问方式太强硬」。

展开：

- `d["x"]`：键不存在 → `KeyError: 'x'`
- `d.get("x")`：键不存在 → 返回 `None`，不抛
- `d.get("x", 默认值)`：键不存在 → 返回默认值
- 判断该用哪个：字段是协议必填、缺失就是 bug → 用 `[]` 让它炸；字段可选、允许缺席 → 用 `.get()`
- 本项目里 `event["tool_calls"]` 属于可选字段（纯文本回答就没有），所以必须 `.get()`；`event["content"]` 在写日志时一定会写，用 `[]` 合理。

为什么不能写成 `event["tool_calls"]`：`run_agent` 写 assistant 事件时是「有 tool_calls 才加这个键」，纯文本回答的事件字典里根本没有这个键，硬取就 `KeyError`。`.get()` 把「键不存在」变成 `None`，再由 `if` 判断是否要往 message 里加键。

### 2.23 默认参数为什么还会传进 list

**问**：`run_agent(..., steps=0)` 不是你写的吗？为什么说 `steps` 是 list？

**答**：`steps=0` 只是**默认值**，调用时不传才生效；`main()` 里显式传了 `steps`，实参覆盖默认值，传什么类型它就成了什么类型。

展开：

- 两个 `steps` 是不同作用域的变量：`main()` 里的局部变量，和 `run_agent` 的形参，只是同名。
- `steps = [msg for msg in messages if ...]` 得到 list；`run_agent(messages, log, steps)` 把它绑给形参；`if steps >= MAX_STEPS` 变成 `list >= int` → `TypeError`。
- Python 是动态类型，形参没有类型约束；默认值不参与类型检查，也不限制实参类型。
- 想在写的时候就发现：给形参加注解 `steps: int = 0`，再用 mypy/pyright 检查（pytest 不会替你检查类型）。

---

## 三、FastAPI 与 pytest

### 3.1 pytest 的参数从哪来，为什么没有类型

**问**：`test_health(client)` 里的 `client` 参数从哪来？为什么没有类型？

**答**：pytest 按参数名去 fixture 注册表查同名对象并注入；注解对注入没有作用，所以省略。

- pytest 读取测试函数签名，看到参数名 `client`，查找 `@pytest.fixture def client()`。
- 找到就调用它，把返回值传进测试函数；找不到报 `fixture 'client' not found`。
- **按名字匹配，不按位置**，参数名必须和 fixture 名完全一致。
- `monkeypatch`、`tmp_path`、`capsys`、`caplog` 是 pytest 内置 fixture，不用自己定义。
- 默认作用域是 `function`，每个测试各构造一次。

注解不生效的原因：CPython 运行时忽略注解，pytest 的注入靠运行时字符串查找，注解在这里没有消费者。

### 3.2 tool.pytest.ini_options 的层级

**问**：`[tool.pytest.ini_options]` 是每个模块都有自己的 `ini_options` 吗？`app` 也可以有吗？为什么是 `tool.pytest`？

**答**：一个项目只有一份 `pyproject.toml`；`tool` 是第三方工具的公共命名空间；只有 pytest 会读 `[tool.pytest]` 这一支。

| 层级 | 谁定的 | 含义 |
|---|---|---|
| `tool` | PEP 518 | 第三方工具配置都放这里 |
| `pytest` | pytest 项目 | 工具自己的名字 |
| `ini_options` | pytest 项目 | 兼容旧 `pytest.ini` 的配置项名 |

- 语法上可以写 `[tool.app]`，但没有任何程序读它，等于死配置。
- pytest 启动时从当前目录向上找配置文件，`pyproject.toml` 里的其他节会被忽略。

### 3.3 @pytest.fixture 的作用范围与命名

**问**：`@pytest.fixture` 是说下面所有 def 都可以用作参数吗？为什么叫 fixture？

**答**：只作用于紧挨着的那一个函数；fixture 指测试前固定好的环境。

- `@dec` 加在 `def f` 上是 `f = dec(f)` 的语法糖，一次只包一个函数。
- fixture 之间可以互相请求：`def logged_client(client)` 会先构造 `client` 再传入。
- 词源：fixture = 固定装置（房屋固定设施、体育固定赛程），借指测试的固定前提。
- 和 `unittest.setUp` 的区别：按需构造、可跨作用域共享、可依赖其他 fixture、`yield` 之后做清理。

### 3.4 pytest 找不到 app 包

**问**：pytest 报 `ModuleNotFoundError: No module named 'app'` 怎么解决？

**答**：在 `pyproject.toml` 里配 `pythonpath`。

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

pytest 启动时读取这个列表，替你把路径插进 `sys.path`。原因是 pytest 默认把测试文件所在目录（`tests/`）而不是项目根加进 `sys.path`。

### 3.5 不包 write_input 怎么替换内置 input

**问**：如果 `confirm_write` 里直接调用 `input()`，测试怎么替换？加 `write_input` 有什么作用？

**答**：直接 `monkeypatch.setattr("builtins.input", lambda _: "y")`；`write_input` 只是项目里额外加的一个更精确的可替换接缝。

展开：

- Python 查名字的顺序：局部作用域 → 模块全局 → `builtins`。`confirm_write` 里没有定义 `input`，所以落到 `builtins.input`。
- 替换写法：

  ```python
  def test_confirm_write(monkeypatch):
      monkeypatch.setattr("builtins.input", lambda _: "y")
      assert confirm_write("a.txt", "x") is True

      monkeypatch.setattr("builtins.input", lambda _: "n")
      assert confirm_write("a.txt", "x") is False
  ```

- `monkeypatch` fixture 会在测试结束后自动恢复，不用手动改回去。
- 两种接缝的取舍：

  | 接缝 | 优点 | 代价 |
  |---|---|---|
  | `builtins.input` | 生产代码零改动 | 影响整个测试进程内的所有 `input` 调用 |
  | 自定义 `write_input` | 替换目标精确、可读 | 生产代码多一层函数 |

- 即使 `confirm_write` 通过 `write_input` 间接调用，patch `builtins.input` 依然生效：`write_input` 函数体里的 `input` 也是运行时按「模块全局 → builtins」查找，最终拿到被替换的实现。两种接缝都能用。
- 真正会让 patch 失效的是静态绑定：写成 `from builtins import input` 后，模块全局里存着原始函数对象的引用，`builtins.input` 再被替换也影响不到它。同理，如果别的模块写 `from app.permissions import write_input`，patch `app.permissions.write_input` 也影响不到那边的引用。
- 判断标准：调用点用的是「运行时查模块全局」，patch 源模块有效；用的是「导入时复制到本模块」，patch 源模块无效。

---

## 四、工程化

### 4.1 venv 是什么

**问**：venv 是什么，真正开发时需要手写吗？

**答**：项目级依赖隔离环境；创建一次即可，不需要每次手写。

- `python3.12 -m venv .venv` 生成一个目录，里面有独立的解释器、`pip`、`site-packages`。
- 激活（`source .venv/bin/activate`）只是把 `.venv/bin` 放到 `PATH` 最前面。
- 不激活也可以直接用 `.venv/bin/python`、`.venv/bin/pip`。
- 作用：不同项目的依赖版本互不污染；`.venv` 不进版本库。

### 4.2 依赖包各自的作用

**问**：`pip install` 的这些包是什么，为什么要这些？

| 包 | 作用 |
|---|---|
| `fastapi` | Web 框架，定义路由、参数校验、自动文档 |
| `uvicorn` | ASGI 服务器，真正监听端口、跑 FastAPI |
| `openai` | 官方 SDK，DeepSeek 兼容其协议所以直接复用 |
| `python-dotenv` | 从 `.env` 读环境变量 |
| `pytest` | 测试框架 |
| `httpx` | `fastapi.testclient.TestClient` 的底层 HTTP 客户端 |

### 4.3 TOML 是什么

**问**：TOML 是什么？

**答**：一种配置文件格式，用 `[表头]` 表达层级，支持注释和原生日期类型。

- 全称 Tom's Obvious Minimal Language，2013 年提出，2021 年发布 1.0。
- 目标只做配置，不做数据交换，所以允许注释、不要求引号、没有 null。
- Python 生态里 `pyproject.toml` 是统一配置入口，各工具占 `[tool.工具名]`。
- 与 YAML 的关键差异：TOML 没有隐式类型转换，`version = 1.0` 不会变成浮点。
- 值类型：字符串、整数、浮点、布尔、数组、表、日期。

### 4.4 git 仓库边界

**问**：`deepseek-harness` 用哪种方式做版本管理？

**答**：独立仓库，父仓库忽略它。

- `/Users/finlaas/my/.git` 是父仓库，`deepseek-harness` 原本只是它下面的未跟踪目录。
- 在 `deepseek-harness` 内 `git init -b main`，成为独立仓库，可单独推 GitHub。
- 父仓库新建 `.gitignore` 写 `deepseek-harness/`，避免误提交。
- 远端：`git@github.com:OdAhViig/harness.git`，走 SSH。

### 4.5 pip 的 SSL 证书错误

**问**：`pip install` 报 `CERTIFICATE_VERIFY_FAILED` 怎么解决？

**答**：Python 找不到根证书。装 `certifi`，再把它的 `cacert.pem` 软链到默认验证路径。

```bash
# 1. 为目标 Python 安装 certifi
python3.12 -m pip install certifi

# 2. 把 certifi 的证书链链到 OpenSSL 默认路径
sudo ln -sf <site-packages>/certifi/cacert.pem \
  /Library/Frameworks/Python.framework/Versions/3.12/etc/openssl/cert.pem
```

验证：`.venv/bin/python -c "import ssl; print(ssl.get_default_verify_paths().openssl_cafile)"` 指向的文件应存在。

临时绕过：`pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <包>`，但会关闭 TLS 校验，只作应急。

### 4.6 隐式契约与显式设计

**问**：隐式契约是不好的吗？有没有相关设计原则？这些原则权威吗？

**答**：隐式契约本身没有好坏，坏的是「被违反时没有报错」。判断看四点：失败是否响亮、契约活多久、有多少消费方、能不能被工具检查。

#### 什么是隐式契约

代码里没有写下来、但调用方或数据消费方必须遵守的约定。我们这个项目里就有很多：

- `messages_from` 假设日志里 assistant 事件一定先于对应的 tool 事件
- 恢复逻辑假设 `function.arguments` 是 JSON 字符串
- 外部 `jq` 命令假设字段名叫 `type`
- 每个日志文件只装一个 session

这些都没写在任何 schema 里，靠读代码和口头约定维持。

#### 四条判断维度

| 维度 | 隐式便宜的情况 | 隐式危险的情况 |
|---|---|---|
| 失败方式 | 违反后立刻抛异常 | 违反后静默算错，像正常结果 |
| 寿命 | 进程内临时对象 | 持久化到磁盘、跨版本读取 |
| 消费方 | 一个函数自己用 | 恢复逻辑、jq、以后的分析脚本都要读 |
| 可检查性 | 有类型/schema/测试覆盖 | 只靠「大家都记得」 |

判据可以压成一句：**隐性约定的风险 ≈ 违反的概率 × 发现它的难度 × 修它的成本**。

#### 相关设计原则与权威等级

「权威吗」这个问题必须诚实回答：工程上没有单一权威，下面这些约束力差别很大。

| 来源 | 说的是什么 | 类型与约束力 |
|---|---|---|
| PEP 20《The Zen of Python》（Tim Peters，2004） | 「Explicit is better than implicit.」「Errors should never pass silently. Unless explicitly silenced.」「In the face of ambiguity, refuse the temptation to guess.」 | Status: Active，Type: **Informational**。是 Python 社区的设计取向，不是可执行规范，违反不违规 |
| Design by Contract（Bertrand Meyer，Eiffel，1986 前后） | 把前置条件、后置条件、不变式写成可检查的断言，调用方和被调方各自有明确义务 | 方法论，不是标准。落地靠 assert / 类型 / 测试 |
| Hyrum's Law（《Software Engineering at Google》第 1 章，O'Reilly 2020） | 「有足够多使用者时，所有可观察行为都会被依赖，包括你没承诺的」 | 对现实的**观察**，不是规范。Hyrum Wright 本人更愿意叫 The Law of Implicit Dependencies |
| RFC 9413《Maintaining Robust Protocols》（IAB，2023-06） | 反驳 Postel「发送保守、接收宽容」：宽容接收会让协议退化，主张主动维护和有原则地拒绝（virtuous intolerance） | Type: **Informational**，不是 standards track。但它是 IETF 架构委员会的立场文件，分量高于博客 |
| Make illegal states unrepresentable（Yaron Minsky，Jane Street，2011） | 用类型系统把非法状态排除在表示之外 | 实务经验，非标准 |
| Convention over configuration（Rails 等） | 大量隐式约定换少写配置 | 反向力量：说明隐式不是原罪 |

注意 PEP 20 和 RFC 9413 都是 Informational——它们表达的是「有充分理由的立场」，不是「你必须这样」。真正有强制力的是：语言规范、协议 standards track、团队 lint 规则。

#### 结论怎么用

- **一次性脚本、内部 demo**：隐式约定便宜，写满 schema 是过度设计
- **持久化数据 + 多消费方 + 要演进**：显式字段值钱。我们的日志要把 `role` 换成 `type`，正是因为这三个条件全占
- **显式化不是消灭隐式**：它只能把最重要的那部分从「沉默」变成「可检测」。事件日志仍然隐式依赖字段名、事件顺序、`tool_call_id` 配对、`arguments` 是 JSON 字符串——这些靠代码和测试守，不可能穷尽

#### 回到「role 换成 type」这个具体争论

用「有没有 `role` 字段」来判断控制事件，本身就是一个隐式契约：以后新增一种带 `role` 的控制事件（比如上下文压缩 `compaction`）就会混进 messages。`type` 是显式判别字段，外部 jq 脚本不用读 Python 源码就知道这行是什么。代价是多一个字段、写入时多一行映射；收益是新增事件类型不会破坏还原逻辑。

### 4.7 zsh 粘贴多行文本的问题

**问**：在 zsh 里复制文本，总是把换行和空格一起带进来，有什么解决办法？

**答**：交互式 shell 会把粘贴内容当成连续输入逐行执行；用 bracketed paste、heredoc 或 `pbpaste` 落盘，都能绕开。

展开：

- **bracketed paste**：zsh 5.1+ 默认开启（`setopt bracketed-paste`）。开启后粘贴内容先进编辑缓冲区、不逐行执行，缩进也保留；确认无误再按一次回车。检查：`bindkey -l | grep bracketed-paste`。
- **多行代码不要直接粘到提示符**：用 heredoc 写文件再执行：

```bash
cat > /tmp/check.py <<'EOF'
多行内容原样保留
EOF
.venv/bin/python /tmp/check.py
```

  引号包裹的 `'EOF'` 表示不做变量展开，内容原样写入。

- **剪贴板直接落盘**（macOS）：`pbpaste > /tmp/check.py`，完全不经过 shell 解析。
- **带 CR 的文本**（从网页或 Windows 复制）：`tr -d '\r' < /tmp/check.py > /tmp/check2.py`。
- 前导空格在 zsh 里属于命令的一部分，粘贴后报 `no such file or directory`，通常是缩进被当成了命令名。

**想让终端输出显示成代码块、方便复制**

- 没有 zsh 插件能把普通输出变成 Markdown 代码块——终端只处理字符流，框线要靠工具自己画。
- `bat`（`brew install bat`）：`cat` 的替代，语法高亮、行号、可用 `--style=full` 加框线；复制仍由终端选区完成。
- `glow`：直接渲染 Markdown，适合看文档，不适合当通用分页器。
- 最直接的办法：`命令 | pbcopy` 直接把输出放进剪贴板；`pbpaste` 反过来从剪贴板读。
- 如果目的是把代码放进项目，最省事的是让 Agent 直接写文件（本项目的编辑工具），不走剪贴板。

### 4.8 「边扫边拼」的问题怎么提前发现和拆解

**问**：原来的问题在于边扫边拼，有没有设计原则能参考，以后遇到类似问题能及时发现并拆解？

**答**：有——当一个循环同时维护「游标、累计量、输出容器」三种状态时，就说明遍历、决策、拼装三个职责缠在一起；拆成「先建结构 → 再决策 → 最后拼装」三阶段，每阶段只碰一种状态。

展开：

**识别信号（出现两条以上就该拆）**

1. 循环体里同时有：位置指针（`msg_index`）、累计值（`total_tokens`）、正在构建的输出（`res`）。
2. 下标算术里出现 `+1`、`+tool_count` 这类派生量。
3. 同一个循环里既有「判断留不留」，又有「把消息塞进结果」。
4. 多个分支都必须记得推进游标——漏一个就死循环。
5. 需要写注释解释「这个下标现在指向哪」。
6. 循环体超过约 15 行，或嵌套两层 `while`。

**对应的设计原则**

| 原则 | 在这次代码里的落地 |
|---|---|
| 单一职责 / 关注点分离 | 遍历、决策、拼装各一个阶段 |
| 数据结构先于算法 | `split_units` 把「tool_call 配对」这个协议约束编码成单元结构，而不是每次现算 |
| 决策与执行分离（plan-then-act） | 先产出 `dropped` / `replaced` 决策集合，再统一拼装 |
| 纯函数、不可变输出 | 返回新列表，输入不修改 |
| 不变量显式化 | 配对完整、顺序保持、system 与首条 user 存在；用测试钉住 |
| 先固化行为再重构 | 10 条测试先绿，再改结构，改完仍然绿 |

**拆解套路（按顺序做）**

1. 写下输出必须满足的不变量（这次：配对不拆、顺序不变、保护消息必在）。
2. 定义单元/记录结构，把隐含约束变成字段（`start`、`end`、`tokens`）。
3. 第一遍：建结构并测量，不做修改。
4. 第二遍：只做决策，产出「保留 / 丢弃 / 替换」三张表。
5. 第三遍：按决策拼装，不再做任何判断。
6. 补测试：正常、边界、极端、副作用四类。

**什么时候不必拆**

数据量小、只执行一次、没有分支时，拆开只是多写代码。拆的收益首先是**可验证**（每个阶段能单独断言），其次才是性能。判断阈值就用上面的识别信号，不用凭感觉。

**同类例子**：编译器「词法 → 语法 → 语义」、数据库「解析 → 生成执行计划 → 执行」、SwiftUI 的 `body` 只描述结果不手工改视图，都是同一件事：先把状态和决策算清楚，再一次性产出结果。

---

## 五、Agent 与 Tool Calling

### 5.1 TOOL_SCHEMAS 与 TOOLS

**问**：`TOOL_SCHEMAS` 和 `TOOLS` 的格式，是 openai 库的要求吗？

**答**：`TOOL_SCHEMAS` 的格式是 OpenAI Chat Completions 的 HTTP 协议，不是 Python 库发明的；`TOOLS` 是本地的名字到函数映射，与 openai 无关。

| 变量 | 谁读 | 格式来源 |
|---|---|---|
| `TOOL_SCHEMAS` | 远程模型服务 | OpenAI 协议（JSON Schema 子集） |
| `TOOLS` | 本地代码 | 自己定义 |

- schema 随请求体发给服务端，字段名不能错：`type: "function"`、函数定义在 `function` 键下、参数用 JSON Schema 描述。
- 模型只能看到描述，拿不到函数体，执行权在本地。
- DeepSeek 兼容这套协议，所以同一份定义可以直接用。

### 5.2 为什么一条用户消息要多次 ask

**问**：调用完 `read_file` 后再次调用 `ask` 合法吗？为什么一条用户消息会调用多次 `ask`？

**答**：合法。Chat Completions 是无状态的，每次 `ask` 是独立的 HTTP 请求，靠重发完整 `messages` 维持连续性。

```
第 1 次 ask
  请求: [user]
  响应: assistant(tool_calls)

本地执行 read_file

第 2 次 ask
  请求: [user, assistant(tool_calls), tool(结果)]
  响应: assistant(content)
```

- 模型生成是单向不可中断的，不能在生成中途说"等我拿到工具结果再继续"。
- 所以只能：模型输出决策 → 请求结束 → 本地执行 → 带结果开新请求。
- 20 步任务就是 20 次 HTTP 请求。
- 连接层可能复用同一条 TCP（keep-alive），但语义上是多次独立请求。

### 5.3 messages 每一条的含义

**问**：打印出来的后续消息是什么意思，OpenAI 怎么规定的，最后一条自己写入的也符合规定吗？

**答**：依次是 `user`、`assistant(tool_calls)`、`tool`；最后一条符合规定。

| # | role | 来源 | 必填字段 |
|---|---|---|---|
| 1 | `user` | 自己写 | `content` |
| 2 | `assistant` | `msg.model_dump()` | `content`（可为空）、`tool_calls` |
| 3 | `tool` | 自己写 | `tool_call_id`、`content` |

协议规定：

- 角色只有 `system`、`user`、`assistant`、`tool`。
- 带 `tool_calls` 的 assistant 消息后面，必须紧跟为每个 `tool_call.id` 提供一条 `tool` 消息，不能缺、不能多、不能隔开。
- `tool_call_id` 必须与 `tool_calls[].id` 一致，一次多个调用靠它配对。

两个坑：

- `reasoning_content` 是 DeepSeek 私有字段，OpenAI 不认；换供应商时可能 400。稳妥做法是手动只保留 `role`、`content`、`tool_calls`。
- 最终回答没有 append 进 `messages`。单轮无碍，多轮对话必须补上。

### 5.4 模型是请求调用，不是调用

**问**：是模型在收到消息后查看 tool schemas，决定调用 `read_file`，然后在我们自己的代码中真正调用 `read_file` 函数？

**答**：基本对，但模型是「请求调用」，不是「调用」。

- 模型返回的只是一段 JSON：`{"name": "read_file", "arguments": "{\"path\": \"README.md\"}"}`。
- 它运行在远端，碰不到本地文件系统。
- 真正执行的是 `TOOLS[name](**args)` 这一行，在本地进程里。
- 这条边界是 Agent 的唯一安全防线：模型说什么只是建议，代码决定执不执行、执行前要不要问人。权限层就建在这里。

### 5.5 步数上限是什么

**问**：步数上限是什么？

**答**：一次用户请求内，Agent loop 最多允许的「模型调用轮数」。到顶就强制收尾，防止模型无限调用工具、无限计费。

展开：

- 一轮 = 一次 `ask` + 执行它请求的工具 + 把结果回填。模型不再请求工具、只回文本时，就是最后一轮。
- 为什么必须有：模型可能反复调同一个工具（结果不符合预期就重试）、路径写错后不断换路径、任务本身无解。每一轮都是一次真实的 HTTP 请求和计费，没有上限就是死循环。
- 它与「工具失败重试」不是一回事：重试是单次工具失败后的策略；步数上限是整条链路的兜底。
- 典型实现：`while` 里维护 `steps`，每轮 +1，`if steps >= MAX_STEPS` 时往 `messages` 追加一条系统提示（让模型基于已有信息收尾）然后 `break`，或直接返回「已达步数上限」。
- 上限值按任务定：单步查询 3–5 足够；20 步复杂任务给 20–25，留一点重试余量。
- 反面教材：`scripts/agent_loop.py` 用递归 `processTool` 调用自己，既没有计数也没有终止条件。模型只要一直请求工具，递归就会一直下去，最终 `RecursionError` 或持续计费。递归还额外吃 Python 栈（默认约 1000 层），换成 `while` 没有这个问题。

**恢复时为什么要数出已经用了多少步**

- `steps` 不只是打印信息，它会被传进 `run_agent`，参与 `if steps >= MAX_STEPS`。
- 如果恢复后从 0 开始数，每次 `--resume` 都重置预算，用户可以靠反复中断无限续命，上限形同虚设。
- 恢复后的剩余预算 = `MAX_STEPS - steps`；计数来源是日志里 `type == "assistant"` 的事件数（每次 `ask` 恰好写一条）。
- 注意：数出来的必须是**整数**。写成列表推导得到 list，`list >= int` 在 Python 3 会直接 `TypeError`。
- 上限的预算范围是「一条用户提问对应的 `run_agent` 调用 / 它的恢复链」，**不跨用户提问**：用户发下一条消息时重新从 0 开始。它计的是 `ask` 次数，一次响应里带 5 个 `tool_calls` 也只算 1 步；如果只想限制单轮工具数量，那是另一个参数，不是 `MAX_STEPS`。

**`run_agent`、while 与 steps 的对应关系**

- `run_agent` 不是「每次对话调用一次」，而是「一条用户消息调用一次」。内部 `while` 反复 `ask`，直到模型不再请求工具、给出最终文本。
- 两个循环职责不同：外层 `while` = 每轮问一次模型；内层 `for call in msg.tool_calls` = 处理这一轮响应里的多个工具调用。后者数量不影响 `steps`。
- `steps` 等于 assistant 消息数，也等于 `ask` 次数；不等于工具调用次数，也不等于用户消息数。
- user 和 assistant 不是 1:1：一条用户消息可以产生 N 条 assistant（每轮一条），只有最后一条是最终回答。
- 因此 `MAX_STEPS` 限制的是「一条请求内部允许的模型调用次数」，不是「一个会话的最大对话轮数」。恢复时接着累计。

**主流 Agent 的同类限制**

| 框架 | 机制 | 默认与超出行为 |
|---|---|---|
| OpenAI Agents SDK | `max_turns`，限制内部的模型调用/工具循环 | 默认 10，超出抛 `MaxTurnsExceededError`；可显式设 `None` 关闭 |
| LangGraph | `recursion_limit`，限制图节点访问次数 | 默认 25，超出抛 `GraphRecursionError`；一次工具往返约 2 步 |
| Claude Agent SDK | `max_turns`（agentic turns / API round-trips） | 不设则无上限；另有 `max_budget_usd` 金额上限 |

结论：主流框架普遍有步数或预算兜底，只是默认值、是否默认开启不同；「完全不限制」通常只出现在个人脚本或显式关闭的配置里。

**为什么上下文压缩不能替代步数上限**

- 两者解决不同问题：压缩解决「上下文窗口满」，步数上限解决「循环不收敛 / 成本失控」。
- 死循环如果每步消息很短（反复调同一个空参数工具），上下文增长很慢，压缩很久才触发，但调用次数和费用已经在涨。
- 压缩有信息损失，压缩后模型可能重复犯错，仍需要次数兜底。
- 成本与延迟随调用次数线性增长，最便宜的保险就是调用次数上限。
- 反过来的风险也存在：上限设太小会截断长任务（LangGraph 默认 25 常被诟病），所以值要按任务定，20 步任务给 20–25。

**为什么不能「给单次 ask 设上限」**

- 单次 `ask` 天然就是一次模型调用，没有可增长的计数；「单次 ask 最多调用 1 次」是恒真的，起不到任何限制作用。
- 会失控的是 `ask` 的**序列**：`ask → 工具 → ask → 工具 → …`。每一环都是新的一次 `ask`，不是同一次调用的重试。
- 所以计数器必须跨 `ask` 累计，也就是 `steps += 1` 放在循环里，而不是放在单次请求内部。
- 类比：信用卡「单笔限额」防不住分成很多笔的小额盗刷，需要「单日/单任务累计限额」；电梯限重防不住一趟一趟地搬，需要「总搬运次数」。

**为什么按「一条用户消息」计数，而不是按整个会话**

- `run_agent` 的调用单位是「一条用户消息」：每条新消息进来就重新调用一次，`steps` 从 0 开始。
- 多轮聊天时，用户发 100 条消息就是 100 次 `run_agent`，互不影响；上限只约束「这一条消息内部模型最多自己转几圈」。
- 所以它不会限制用户能聊多少轮，只限制单条任务内部的自动化步数。
- 当前 CLI 一次进程只有一条写死的用户消息，看起来才像「会话总上限」。

**为什么主流产品看起来没有这个限制**

- 多数聊天产品把上限设得很高或隐藏起来，正常使用撞不到；`MAX_STEPS` 是安全网，不是常规路径。
- 聊天产品每一轮用户输入只触发少量工具调用，且人在回路，可以随时点停止；无人值守的 Agent 没有这个刹车。
- Agent 类产品（Claude Code、ChatGPT Agent、各种自动化框架）普遍有显式的步数/时间/预算限制，只是不一定展示给用户。
- 另一种兜底方式是预算而非步数（如 Claude Agent SDK 的 `max_budget_usd`）；步数是最便宜、最容易实现的代理指标。

### 5.6 ask 是自定义函数名吗

**问**：`ask` 是我们自己起的名字吗？面试时应该说「请求次数」吗？

**答**：`ask` 是项目里对 `client.chat.completions.create` 的本地包装函数名；面试时说「一次模型调用」或「一次 Chat Completions 请求」。

展开：

- 协议层没有 `ask` 这个概念。官方 SDK 的调用是 `client.chat.completions.create(...)`，一次网络请求。
- 我们把它包成 `def ask(messages)`，只是为了让 loop 里少写参数；名字可以叫 `call_model`、`complete` 等。
- 准确表述：「循环每向模型发起一次请求记一步；一次请求可能返回多个 `tool_calls`，所以工具调用次数可以大于步数」。
- 不建议说 turn：assistant turn 可能含多个工具调用，也可能没有工具调用，容易和「步」混淆。
- 代码对应关系：`scripts/agent_loop.py` 里 `steps += 1` 紧挨着 `resp = ask(messages)`，一个 `steps` 对应一次 HTTP 请求。

### 5.7 事件日志为什么用 type 而不是 role

**问**：`record` 已经是 message dict，为什么不直接写日志，还要把 `role` 换成 `type`？`messages_from` 为什么忽略控制事件？

**答**：日志记录的是「事件流」，比对话消息多出 `done` / `interrupted` / `limit` 等控制事件；统一用 `type` 区分事件种类，只在还原 messages 时映射成协议要求的 `role`。

展开：

- 事件种类有两类：
  - 消息事件：`user`、`assistant`、`tool`
  - 控制事件：`done`、`interrupted`、`limit`
- 控制事件没有合法的 message role；如果日志混用 `role` 字段，筛选就必须同时判断两套字段。
- `messages` 协议只接受 `system` / `user` / `assistant` / `tool` 四种 role，把 `done` 塞进去会 400 或让模型困惑。
- 两种可接受的 schema：
  - 扁平：`{"type": "assistant", "content": ..., "tool_calls": [...]}`
  - 嵌套：`{"type": "assistant", "message": {...}}`，边界更清晰
- 关键是转换只在一个地方做（`messages_from`），日志 schema 保持一致。

**为什么不在写入时过滤控制事件**

- 日志是事实记录，控制事件承载恢复所需的信息：`done` 表示任务已完成，恢复时不应继续；`interrupted` 表示进程被打断，提示需要 resume；`limit` 记录触顶。删掉它们，日志只剩对话，无法判断会话为何结束。
- 写入时过滤等于永久丢失信息；读取时过滤让同一份日志服务不同用途（恢复、调试、统计）。
- 日志保持 append-only，投影逻辑放在读侧。

**为什么用显式 type，而不是「没有 role 就当控制事件」**

- 依赖字段缺失是隐式契约：消息事件如果因 bug 漏写 `role`，会被静默当成控制事件丢掉；新增事件类型也无法表达「有类似 role 的字段但不是消息」。
- 显式 `type` 是判别联合（discriminated union）：每个事件自描述类型，校验和过滤只依赖一个字段。
- 两套字段同时存在会造成双重真相，判断时还得决定以谁为准；显式 `type` 只有一套判据。
- 以后新增 `tool_start` 之类事件时，规则不用改。

**为什么转成事件时要把 `role` 去掉，保留不行吗**

- 保留不会立刻出错，但它让同一个事实有了两份副本（`type` 和 `role`）。两份一旦不一致，`messages_from` 必须临时决定信谁——这个「信谁」的规则没人写下来，那才是隐式契约。
- 控制事件没有 `role`；如果 role 只在消息事件出现，「有没有 role」就又成了一个判别信号，和 `type` 重叠且可能矛盾。
- 冗余只有在**有校验**时才安全（类似 checksum）：可以两边都写，但读的时候必须断言两者一致，不一致就报错。我们没有这个校验，所以冗余只有成本没有收益。
- 不是「字段越少越好」：如果 `role` 有独立用途（比如日志要直接喂给只认 role 的系统），保留并加一致性校验是合理的。判断标准是两个字段是否永远同步、有没有代码保证这一点。

### 5.8 to_message 为什么只转 assistant

**问**：`to_message` 看上去只转换 assistant 消息，难道不应该转换所有可能的返回消息类型吗？

**答**：Chat Completions 的响应里，`choices[].message` 按协议永远是 assistant；user / system / tool 消息都是我们本地构造的，不从响应里来。

展开：

- 角色数量与来源是两件事。协议允许四种 role，但一次请求的返回值只携带模型这一轮的话，角色恒定是 `assistant`。
- user 消息在 `main()` 里手工构造；tool 消息在 `run_agent` 里用 `call.id` 和工具结果构造；system 消息是常量。
- 所以「转换所有返回消息类型」这个需求不存在——返回类型只有一种。
- `to_message` 真正的职责不是「转换角色」，而是**裁剪字段**：SDK 的 message 对象带 `reasoning_content` 等私有字段，只保留 `role` / `content` / `tool_calls` 才不会被换供应商时的校验拒绝。

### 5.9 assistant 消息与 tool_call 的配对

**问**：assistant 类型是做什么的，为什么要和工具调用一一对应？

**答**：assistant 表示「模型这一轮说的话」，可能是文本，也可能带着调用工具的请求；**每个 tool_call 必须有一条 tool 消息回报**，用 `id` 配对。

展开：

- 一轮完整交互是四段式：
  1. `user` 提问
  2. `assistant` 回答或请求工具（`tool_calls: [c1, c2]`）
  3. 每个 `cN` 对应一条 `{"role": "tool", "tool_call_id": "cN", "content": ...}`
  4. 下一次 `ask` 带着以上全部历史，模型看到「我请求了 c1，工具返回 X」再决定下一步
- 配对单位是 **tool_call ↔ tool 消息**，不是 assistant ↔ tool_call。一条 assistant 可以带多个调用，就要回多条 tool 消息；`run_agent` 里的 `for call in msg.tool_calls` 就是这个意思。
- 为什么不配对不行：模型下一轮看不到执行结果就无法推进；协议层面服务器也会校验，缺少对应 tool 消息直接 400。
- 日志同理：assistant 事件先落盘，再执行工具、再落 tool 事件。进程在工具执行中被杀，就会出现「有 assistant 调用、没有 tool 结果」，`pending_tool_calls` 正是用来识别这种状态，恢复时不能盲目重放。

### 5.10 日志对象为什么用参数传，而不是全局变量

**问**：`main` 的思路不理解，为什么没有把 event 作为各个函数都可以访问的变量，这样在 `run_agent` 里不就可以直接添加 log 了吗？

**答**：`log` 已经是参数传进去的——`main` 里创建 `EventLog`，再 `run_agent(messages, log, steps)`，函数体内直接用 `log.append(...)`，写的就是当前会话那个文件。

展开：

- 调用链：`main()` 创建 `log = EventLog(args.resume 或 args.log)` → `run_agent(messages, log, steps)` → `log.append(event)`。
- 不设全局变量的三个理由：
  1. **显式依赖**：函数签名直接说明「我要写日志」，读代码不用翻模块全局
  2. **可测试**：测试传一个 `tmp_path` 的 EventLog 即可，全局变量要污染再重置
  3. **多会话/恢复**：全局只能指向一个文件，resume 和新会话同时存在时会串
- Python 模块级变量确实能被所有函数读到，但那正是 4.6 说的隐式契约：谁在什么时候改了它，从函数签名上看不出来。
- TODO 4 的接法：在 `run_agent` 里 `log.append({...})`，字段取 `to_message` 的 `record`，把 `role` 改成 `type`，`tool_calls` 有才带；工具执行完再 `log.append` 一条 `type="tool"`，带 `tool_call_id`、`name`、`content`。写入顺序必须是 assistant 先、tool 后。

---

## 六、上下文工程

### 6.1 TOOL_RESULT_LIMIT 为什么存在，截断不会影响结果吗

**问**：总量有限裁剪旧 messages 能理解，但把单条 tool 结果也截断，不会影响后续结果吗？

**答**：会影响，这是有意的有损取舍；不截的话，单条工具结果就能吃掉整个预算，逼着裁剪删掉更多完整单元（包括刚产生的关键消息），损失反而更大。

展开：

- 这是 agent loop 特有的压力：**每一轮 `ask` 都重发全部历史**，一条 3000 行的 `read_file` 结果是几万 token，之后每一步都要重付一遍，token 总量随步数近似平方增长。
- 工具结果是上下文里「体积最大、信息密度最低」的部分。裁剪旧单元是按轮次整体丢弃，粒度粗；单条工具结果截断粒度细，先切掉冗余的大头，通常就不需要再丢整轮了。
- 截断为什么可接受：
  1. 保留开头——多数工具输出（文件头、列表前几项、报错栈顶部）关键信息在前；
  2. 显式标记 `…[已截断，原长 N 字符]`，模型知道信息不全，可以换更窄的调用重读，而不是误以为看到了全文；
  3. 只截发给模型的那份，`messages` 内存与 `EventLog` 里的完整结果不丢，可回溯、可 resume。
- 截断是**兜底保险丝**，不是最优解。真正的解法在工具层：`read_file` 支持 `offset` / `limit` 分页，让模型自己按需读窄范围。M3 后续可以做工具结果摘要压缩，截断仍然保留作最后一道闸。
- 判断标准：截断不要求精确，只要求**有界**——任何单条工具结果都不能单独撑爆预算。

### 6.2 为什么不无条件调用 trim

**问**：`run_agent` 里是不是不该每次无条件 `trim_messages`，以减少处理时间？

**答**：对，先估算、超预算才裁剪；估算是一次 O(n) 的字符串长度累加，和一次网络请求比可以忽略，而裁剪本身要遍历、复制列表，没必要每轮都做。

展开：

- 成本对比：一次 `chat.completions.create` 是几百毫秒到几十秒；`estimate_messages_tokens` 只是把已有字符串取 `len()` 累加，微秒级；`deepcopy` 才是相对贵的部分，只在超预算时付。
- 正确接法：每轮先算 `before = estimate_messages_tokens(messages)`；`before > budget` 才 `trim_messages`，并把 `before/after` 记一条 `context` 事件；否则原样发送。
- 可选的进一步优化：历史只增不减，可以缓存上一轮的估算值，本轮只累加新增消息，避免每轮全量重算。属于优化，不影响正确性，M3 主线上先不做。
- 注意：估算便宜不等于可以省——不估算直接发，等于把「爆窗口」交给服务端报错，属于把可预防的错误变成线上故障。

### 6.3 预算没超时要不要截断工具结果

**问**：`TOOL_RESULT_LIMIT` 的判断，是指「总预算不超时也截断」还是「超了才截断」？

**答**：只做超预算时的保险丝，不超不截——预算够的时候截断只会白丢信息，没有任何收益。

展开：

- 两种策略的区别：
  - **常态策略**：不管预算，每条工具结果一律封顶（比如 2000 字符）。行为稳定、请求体积可预测，但会把本来装得下的内容也砍掉。
  - **保险丝策略**（当前实现）：只有总量超预算，才把超长工具结果截到上限；截完还不够才丢整轮。
- 选保险丝的理由：截断是有损的，损失只在「必须损失」时才付；预算没超时，完整信息对模型更有用。测试 `test_tool_result_untouched_when_within_budget` 把这条规则钉死。
- 代价：`TOOL_RESULT_LIMIT` 不再是「每条结果的策略」，而是「溢出的第一道处理」。如果以后想要「任何单条结果都不超 4000」，那属于工具层的输出策略，应该放在 `run_tool` 返回处，而不是上下文裁剪里。
- 顺带：裁剪顺序是「先截断最旧的超长工具结果，够用就停；不够再整轮丢弃」。这个贪心方向是对的——旧数据大概率已经被模型消费过，新数据正在用。

### 6.4 新的 trim_messages 是什么逻辑

**问**：原来的做法是「总 tokens 减去剪裁部分，剩下的保留」，新版的 `trim_messages` 是怎么做的？

**答**：贪心策略没变，变的是结构——先把消息切成不可拆的单元并算好每格大小，再按单元从旧到新做「截断 / 丢弃」决策，最后按决策拼出结果；`total_tokens` 只当停止条件，不再参与拼装。

展开（`app/context.py:41-100`）：

1. **切单元**（`split_units`，第 19 行）：一次扫描得到 `[(start, end, tokens), ...]`。`assistant(tool_calls)` 和它后面紧跟的所有 `tool` 消息算一个单元，其余消息各自一个单元。配对关系在切分时就固定下来了。
2. **标记保护单元**（第 50-58 行）：`system` 和**第一条** `user` 永不删除。后续 user 消息是普通单元，可丢。
3. **算总量**（第 60 行）：`total_tokens = sum(每个单元 tokens)`。不超预算直接返回新列表（浅拷贝）。
4. **逐单元决策**（第 67-89 行），从最旧开始：
   - 总量已经达标 → `break`，后面的单元全部保留；
   - 保护单元 → 跳过；
   - 先尝试截断这个单元里的超长 tool 结果：`cut = Σ(长度 - TOOL_RESULT_LIMIT)`。如果 `total_tokens - cut <= budget`，记下替换内容、`total_tokens -= cut`，这个单元保住；
   - 否则整单元丢弃：`total_tokens -= 该单元 tokens`。
5. **拼结果**（第 91-100 行）：按原顺序遍历单元，丢掉的跳过，被截断的 tool 消息换成新 dict，其余直接引用原消息。

和旧版的区别：

| | 旧版 | 新版 |
|---|---|---|
| 总量怎么维护 | 标量 `total_tokens` 边扫边减 | 同样有标量，但单元大小预先算好 |
| 结果怎么来 | `res` 收集保护消息 + `extend` 剩余下标 | 按单元决策表拼装，顺序天然正确 |
| 下标算术 | `msg_index + tool_count + 1` | 无，单元自带 `start/end` |
| 每轮重算 | `estimate_messages_tokens(res)` | 不重算 |

不变的部分：仍然是「超预算才动」；仍然优先截断工具结果、不够再丢整轮；仍然从最旧开始；输入列表不被修改。新增那条 `<=` 边界和后续 user 可丢，都是把旧逻辑里的隐含规则显式化了。

---

## 七、检索与 RAG

### 7.1 bigram 与 embedding 是什么

**问**：bigram 和 embedding 分别是什么？它们是什么关系？

**答**：bigram 是「把中文切成两字片段」的分词办法，服务于 BM25 这类字面匹配检索；embedding 是「把文本变成向量、用向量距离表示语义相近」的另一条检索路线。前者是词表怎么建，后者是检索依据换了维度，两者不在同一层。

展开：

**bigram（二元组）**

- 定义：把连续文本按「相邻两个字符」滑窗切开。中文没有空格，检索需要先把文本变成可计数的「词项」，bigram 是最省事的近似。
- 例子：`上下文工程` → `上下 / 下文 / 文工 / 工程`；一段 n 字的文本产生 n-1 个 bigram（允许重复）。
- 在 BM25 里的角色：文档和查询用同一套切法，每个 bigram 当一个 term，统计词频和文档频率，再算相关性分数。
- 为什么是两个字：
  - 单字歧义太大（「工」在工程、工作、工具里都出现），区分度低；
  - 三字以上的组合数量爆炸，且必须连续命中才有效，召回反而低；
  - 两字刚好覆盖中文最常见的词形，且不依赖词典。
- 英文怎么处理：ASCII 单词按空格和标点切，整个单词当 term；只有中文连续片段才做 bigram。
- 优点：零依赖、对未登录词和错别字有一定容忍度（`上下文窗囗` 仍能命中 `窗口` 的其他 bigram）。
- 缺点：词表大（每个文档的 bigram 数约等于字数）；同义不同词零重叠——查询「汽车」永远匹配不到只写了「轿车」的文档。

**embedding（嵌入向量）**

- 定义：用一个模型把文本映射成固定长度的数字向量（常见几百到几千维），语义相近的文本，向量方向也相近。
- 怎么来：embedding 模型在海量文本对上训练，训练目标是让意思相近的句子距离近、无关的远。模型把「语义」压进了向量，但单个维度没有可读含义。
- RAG 里怎么用：
  1. 建索引时，把每个 chunk 过一遍 embedding 模型，保存向量；
  2. 查询时，把问题也转成向量；
  3. 用余弦相似度（只看方向不看长度，越接近 1 越相似）排序，取 top-k。
- 优点：能处理同义改写、跨语言、口语化表达；查询「车太贵」可以召回写「价格偏高」的段落。
- 缺点：
  - 需要模型和算力：本地跑通常要 PyTorch 和较大内存，本机不合适；走 API 则要额外 key、按量计费；
  - 建索引和每次查询都要调用模型，延迟和成本都比 BM25 高；
  - 对精确编号、代码标识符、专有名词不一定比字面匹配强；
  - 相似度是连续值，阈值要校准，可解释性差。

**两者的关系与选型**

| | BM25 + bigram | embedding 检索 |
|---|---|---|
| 匹配依据 | 字面重叠 | 语义相近 |
| 额外依赖 | 无 | 模型 / API |
| 同义词、改写 | 差 | 好 |
| 精确术语、编号 | 好 | 一般 |
| 成本 | 极低 | 建索引 + 每次查询都要算 |
| 可解释性 | 能列出命中的 bigram | 只能看相似度分数 |

- 关键点：bigram 不是 embedding 的替代品，它是 BM25 内部的分词细节。真正的路线选择是「字面匹配 vs 语义匹配」。
- 生产上常见做法是 hybrid：BM25 和向量各取 top-k，用 RRF 之类的规则融合，再上 rerank 精排。M3 先用 BM25 拿到基线，后面加向量才有可比较的提升数字。
- 用本项目的场景验证差异：问「上下文超预算怎么裁」，BM25 能命中包含「上下文」「预算」「裁剪」的段落；但如果文档只写「对话太长模型记不住」，BM25 得 0 分，embedding 能召回。反过来问错误码 `MAX_STEPS`，BM25 精确命中，embedding 可能因为语义泛化反而排后。

### 7.2 RAG 是什么，在 agent 调用里处于哪里

**问**：看不懂。RAG 到底是什么？这个步骤在 agent 调用中处于哪里？要前端实现吗？是 RAG 处理完再调用模型吗？

**答**：RAG 就是「先查资料，再让模型回答」，没有新模型；它在 agent loop 里就是一次工具调用，全部在后端完成；顺序上，经典 RAG 是先检索再调一次模型，本项目的 agentic RAG 是模型先要求检索、再带着结果调第二次。

展开：

**1. RAG 三个字母拆开**

- **R**etrieval 检索：从资料里找出相关段落。
- **A**ugmented 增强：把这些段落附加到这次请求里。
- **G**eneration 生成：模型基于问题和附加段落写答案。

类比开卷考试：模型是考生，训练数据是它背下来的内容；RAG 允许它翻书，检索是查目录找页码，答案里的引用就是页码。

RAG 不是模型，也不是微调。它是一条代码流程：**搜索 + 拼消息 + 调模型**，没有任何魔法。

**2. 在 agent 调用里的位置**

它就是 loop 里的一个工具，和 `read_file` / `write_file` 平级：

```text
用户提问
  → ask 第 1 次 ──→ 模型返回 tool_call: search_docs("...")
  → 本地执行检索（BM25）
  → 结果作为 role=tool 追加进 messages
  → ask 第 2 次 ──→ 模型基于证据回答
```

模型觉得不需要查资料时，直接回答，loop 只跑一轮。所以不存在「先做完 RAG，再进入 agent」——**RAG 是 agent 可能调用的一次工具**。

**3. 前端还是后端**

全部在后端。前端只做两件事：把用户问题发到 FastAPI 接口；把返回的答案显示出来。切分、建索引、检索、调模型都在 Python 后端，因为 API key 不能放到浏览器里，索引也不该下发到前端。

```text
浏览器 ──HTTP──> FastAPI ──> agent loop ──> DeepSeek
                      └──> BM25 索引（后端内存/磁盘）
```

以后做聊天界面，改动只在「怎么发问题、怎么显示流式回答」，检索逻辑一行不动。

**4. 先检索再调用，还是先调用再检索**

| | 经典 RAG | Agentic RAG（本项目） |
|---|---|---|
| 谁决定查什么 | 代码固定：拿用户原话去搜 | 模型：生成查询词，可改写、可多查 |
| 模型调用次数 | 1 次 | 2 次起 |
| 检索时机 | 调模型之前 | 两次调用之间 |
| 适合 | 简单问答、单跳 | 多跳、需要换词或追问 |

- 经典 RAG：`问题 → 检索 → 拼进 prompt → 调模型（1 次）`。
- 本项目：`问题 → 调模型（第 1 次，模型说要查）→ 检索 → 调模型（第 2 次，带证据回答）`。
- 两者都是 RAG，区别只是「谁触发检索」。选 agentic 是因为 tool loop 已经有了，复用零成本，模型还能自己换查询词。

**仍然要记住的三点**

- 模型只看 top-k，看不到整个语料。top-k 没召回正确段落，模型要么说不知道，要么编——这就是要测召回率的原因。
- 检索结果是普通 `tool` 消息，照样计入上下文预算，所以 chunk 大小 × k 要和 `TOOL_RESULT_LIMIT` / `CONTEXT_BUDGET` 对得上。
- 引用（`path:start_line-end_line`）让答案可核对，「引用准确率」测的是引用是否真的包含所引内容。

**什么时候不需要检索**

- 问题不需要外部知识（纯推理、改写、总结当前对话）；
- 文档很短，整份塞进上下文更简单可靠；
- 需要精确计算或结构化查询时，用专门工具比检索更合适。

### 7.3 RAG 要做到什么层次，对 agent 开发重要吗

**问**：RAG 似乎是一个很复杂、很有深度的领域，数据预处理、切片粒度、用户提问处理都有很多东西；我们目前要做到哪一层次？这个技术对 agent 开发重要吗？后续是否要深入？

**答**：本冲刺只做到「跑得通、量得出、讲得清」的应用层，不碰研究级内容；RAG 在 JD 里占 45%，是 agent 的知识入口，但 agent 的核心仍是 loop、工具和可靠性，后续是否深入按岗位和数字需求决定。

展开：

**分四层看目标**

| 层次 | 内容 | 本冲刺是否覆盖 |
|---|---|---|
| L0 概念 | RAG 是什么、什么时候用、和微调的区别 | 已覆盖（7.1 / 7.2） |
| L1 跑通 | 切分、检索、引用、接进 agent loop | M3 第二块 |
| L2 可评估 | golden set、召回率、引用准确率、失败分类 | M3 第三、四块 |
| L3 可优化 | 参数对比（chunk 大小、k）、hybrid、rerank，有前后数字 | M3 收尾选做 / M4 复用 |
| L4 研究级 | query rewriting、多路召回、GraphRAG、embedding 微调 | 不做 |

本冲刺的目标是 **L1–L3**：能拿出一套 30 条问题的评测集，能说清召回率与引用准确率，能把失败分成「没召回 / 排序错 / 生成错」，并能用数字说明一次优化前后的差异。这已经覆盖面试和日常开发能问到的绝大部分。

**为什么停在 L3**

- 冲刺计划给 M3 的预算是 5 天，超预算 30% 就要砍范围；研究级内容没有边界，投进去会挤占 M4–M6。
- 岗位数据里 RAG 提及率 45.0%，低于 Python（71.3%）和 Tool Calling（49.0%）；它是核心能力之一，但不是唯一门槛。
- 面试真正区分人的是「为什么这么设计、怎么评测、失败怎么归类」，不是会不会装向量库。

**对 agent 开发重要吗**

- 重要，但角色是「知识入口」。Agent 的常见形态是「模型 + 工具 + 知识」：工具让它能做事，RAG 让它知道该做什么、依据是什么。
- Agent 的核心竞争力在 loop、工具设计、权限、状态恢复、可靠性——这些是 M2、M5 的内容，RAG 只是可调用的工具之一。
- 不要把 agent 开发等同于 RAG 开发：只会 RAG 不会 loop，做不出能落地的 agent；只会 loop 不会 RAG，agent 只能靠模型记忆和用户输入。

**什么时候再深入**

满足任一条件再投入额外时间：

1. 目标岗位 JD 把 RAG 写进职责而不是加分项，且面试反馈问到；
2. 项目里确实需要 hybrid / rerank 才能达标，且已有评测集能证明收益；
3. M4–M6 完成后仍有时间预算。

深入时的顺序：先补评测集与失败分类（已有）→ 加 embedding 做 hybrid → 加 rerank → 最后才考虑 query rewriting 和 GraphRAG。

**常见误区**

- 没有评测集就反复调 chunk size，属于凭感觉优化；
- 一上来就上向量库和 GraphRAG，没有 BM25 基线，说不清提升来自哪里；
- 把 RAG 当银弹，忽略上下文工程、工具设计和错误处理。

### 7.4 CHUNK_OVERLAP 是干什么的

**问**：`CHUNK_OVERLAP` 是干嘛用的？

**答**：让相邻两块共享一小段原文，防止一句完整的话正好被切在边界上，导致哪一块都拿不到完整信息。

展开：

- 问题长这样：按 600 字符封块，第 600 个字符正好落在句子中间。

```text
原文：……上下文超预算时，先截断工具结果，再丢整轮……

块 1：……上下文超预算时，先            ← 后半句没了
块 2：截断工具结果，再丢整轮……          ← 前半句没了
```

- 不带重叠时，查询「上下文超预算怎么处理」可能只命中块 1，而块 1 没有完整的处理办法；模型拿到的证据是残句，答案就会缺一半。
- 带 `overlap=100` 后，块 2 从块 1 结束前约 100 字符处开始，两句在块 2 里是完整的：

```text
块 1：|-------- 600 --------|
块 2：              |--100--|-------- 600 --------|
                    共享
```

- 参数怎么定：经验值是块大小的 10%–20%。这里是 `100 / 600 ≈ 17%`。
- 代价：
  - 索引体积变大（重叠部分被重复存储）；
  - 检索时可能同时返回共享同一段的两块，浪费 top-k 名额；
  - 下游拼上下文时出现重复文本。
- 反过来，重叠太大（比如 300）会让相邻块高度相似，top-k 变成「同一段话换了个开头」；太小（比如 10）又救不了跨边界的句子。
- 本项目首版按字符窗口切分，重叠严格按字符数；如果按行切分，重叠只能按整行携带，实际重叠会大于设定值。
- 它不是唯一解法：按句子/段落边界切分（sentence-aware chunking）可以从根上避免切断句子，但要先做句子分割；字符窗口 + 重叠是成本最低的第一版。

### 7.5 BM25 检索基础：从分词到打分

**问**：CJK、bigram、term、df、dl、avgdl 这些词都看不懂；BM25 到底怎么从一堆 chunk 里算出排名？为什么有了 rag 的 chunks 还要 `build_index`？

**答**：BM25 是一套「把查询词与文档的字面重叠折算成分数」的公式。分词先把文本变成 term，倒排索引把「term → 哪些块含它」预先存好，BM25 再用 tf、df、dl、avgdl 四个统计量给候选块打分排序。`build_index` 不是另一份语料，它只是把 rag 的 chunks 换一种查得更快的存法。

#### 1. 检索系统的最小模型

输入是查询 `q` 和语料 `corpus`，输出是按相关度排序的文档列表。检索只负责挑段落，不负责生成答案。

IR（信息检索）里把每个被索引的单元叫 **document**。本项目的 document 就是一个 chunk，所以后文说「文档」时，指的都是块，不是整份 md 文件。

两条技术路线：

- 字面匹配：查询词和文档词有重叠就加分，BM25 属于这条；
- 语义匹配：把查询和文档映射成向量算距离，embedding 属于这条（见 7.1）。

#### 2. 分词：把文本变成 term

**term（词项）** 是检索系统实际计数的单位，也叫 token。文本先被切成 term 列表，后面的 tf/df 都是对 term 统计的。

英文有空格，按空格和标点切即可；中文没有空格，必须另想办法：

- 用词典分词（jieba 等）：更准，但要装依赖、处理未登录词；
- 用字符 bigram：不依赖词典，把连续中文按相邻两字滑窗切开。首版选这个。

**CJK** 是 Chinese、Japanese、Korean 的缩写，指中日韩文字。我们只需要判断「这个字符是不是汉字」，用 Unicode 的汉字区 `\u4e00-\u9fff` 即可。Python 里用正则一次取出连续的汉字段和英文/数字段：

```python
import re
runs = re.findall(r"[\u4e00-\u9fff]+|[a-z0-9]+", text.lower())
```

逐个符号解释：

- `text.lower()`：英文统一小写，保证 `Python` 和 `python` 是同一个 term；
- `re.findall(pattern, text)`：返回所有不重叠的匹配子串，组成列表；
- `[...]`：字符类，匹配其中任意一个字符；
- `\u4e00-\u9fff`：汉字 Unicode 范围；
- `+`：前一项出现一次或多次，所以会取到一整段连续汉字/英文；
- `|`：或，左边匹配汉字段，右边匹配英文数字段。

得到的是「段」的列表，例如 `"Python 的 list 推导式"` → `["python", "的", "list", "推导式"]`。标点和空格因为不在任何字符类里，自动被跳过。

然后对每个中文段做 bigram。注意是**滑窗**，不是两两不重叠地切：

```text
推导式     → 推导 / 导式              （长度 3，产出 2 个）
上下文工程 → 上下 / 下文 / 文工 / 工程  （长度 5，产出 4 个）
单字「的」 → 的                        （长度 1，只能保留单字）
```

一段长度 L 的中文，产出 L-1 个 bigram（L=1 时产出 1 个单字）。bigram 不跨标点和空格，因为正则已经先按连续段切开了。英文/数字段直接整段作为 term，不再切。

首版不做停用词表：「的」这种高频词会被 idf 自动压低，不需要手工删。

#### 3. 倒排索引：为什么 build_index

先看两种存法：

- 正排：`chunk → [term, term, ...]`，即每块有哪些词；
- 倒排：`term → {chunk_id: tf}`，即每个词出现在哪些块、各出现几次。

查询时，我们只关心「哪些块包含查询词」，所以倒排更合适：拿到查询的 term，直接查出候选块，不用把 137 个块全部重新分词。类比书末索引：查「BM25」直接翻到对应页码，而不是从第一页读到最后一页。

`build_index(chunks)` 的输入就是 rag 的 chunks，它没有取代 chunks，而是生成一份派生结构；`search` 同时拿着索引和 chunks 原文。如果不在 build 阶段做，而是每次 search 都现算，那么每次查询都要把全部块重新分词、重新计数，白白重复 137 次。

索引至少存这些：

```text
postings: {term: {chunk_id: tf}}   # 倒排表
doc_len:  {chunk_id: dl}           # 每块 token 数
chunks:   {chunk_id: chunk}        # 原文，命中后按 id 取回
N:        int                      # 块总数
avgdl:    float                    # 平均块长
```

`df(term)` 不用单独存，`len(postings[term])` 就是包含该 term 的块数。构建顺序：

1. 逐块分词，得到 tokens；
2. `dl = len(tokens)`，记进 `doc_len`；
3. 用 `Counter` 统计每个 term 在本块的 tf，写入 `postings[term][chunk_id]`；
4. 全部块处理完后，`avgdl = sum(doc_len) / N`。

#### 4. 四个统计量

| 符号 | 名字 | 定义 | 例子 |
|---|---|---|---|
| N | 文档总数 | 索引里有多少块 | 137 |
| tf(t,d) | 词频 | term t 在文档 d 里出现几次 | 「apple」在 D1 出现 2 次 → tf=2 |
| df(t) | 文档频率 | 含 t 的文档数，**不是出现总次数** | 「apple」在 D1、D2 出现 → df=2 |
| dl(d) | 文档长度 | 文档 d 的 token 数 | D1 有 3 个 token → dl=3 |
| avgdl | 平均文档长度 | 所有文档 dl 的平均 | 三块 dl 为 3、2、3 → avgdl=8/3 |

最容易混的是 tf 和 df：tf 数「同一个词在一块里出现几次」，df 数「这个词出现在几块里」。一个词可以在少数块里高频出现，df 很小而 tf 很大。

#### 5. BM25：先讲直觉，再给公式

先把它拆成「每个查询词投一票」：

```text
score(q, d) = Σ idf(t) × B(t, d)
             t∈q
```

- `idf(t)` 是这位投票人的话语权；
- `B(t,d)` 是这个文档对这位投票人的匹配强度，范围有限；
- 查询里没有出现的 term 不参与；查询里重复的 term 只投一次。

**5.1 匹配强度 B 要有上限**

最直觉的做法是「出现一次算一次」，但这样有两个问题：tf 从 10 涨到 20 分数翻倍，一个词重复刷屏就能霸榜；长文档天然有更多重复机会。

所以 BM25 把 tf 压成一条饱和曲线：

```text
B(t, d) = tf × (k1 + 1) / (tf + k1)
```

`k1=1.5` 时：

| tf | B |
|---|---|
| 1 | 1.00 |
| 2 | 1.43 |
| 5 | 1.92 |
| 10 | 2.17 |
| ∞ | 2.50 |

tf 越大涨得越慢，上限是 `k1+1=2.5`。`k1` 越小，饱和得越快；它控制「重复出现还能加多少分」。

**5.2 长度归一化**

同样 tf 下，长文档得分应该低一些，因为它天然有更多机会命中。把 5.1 分母里的 `k1` 换成一个随文档长度变化的值：

```text
L(d) = 1 - b + b × dl(d) / avgdl

B(t, d) = tf × (k1 + 1) / (tf + k1 × L(d))
```

- `dl = avgdl` 时，`L=1`，不做惩罚；
- 文档比平均长，`L>1`，分母变大，分数降低；
- 文档比平均短，`L<1`，分数升高；
- `b=0` 关闭长度惩罚，`b=1` 完全按长度比例惩罚，首版用 `b=0.75`。

**5.3 idf 衡量稀有度**

```text
idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
```

N=3 时：

| df | idf | 含义 |
|---|---|---|
| 1 | 0.981 | 只在一篇出现，很有区分度 |
| 2 | 0.470 | 两篇出现，权重减半 |
| 3 | 0.134 | 每篇都有，几乎不提供信息 |

- `+0.5` 是平滑：避免 df=0 时除零，也避免极端值；可以理解成「每个计数都先加上半篇文档的不确定性」。
- 对数里的 `+1` 让 idf 恒为正。经典 BM25 公式在 `df > N/2` 时会算出负数，Lucene/Elasticsearch 用的就是这种非负变体。

**5.4 合起来**

```text
idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))

L(d) = 1 - b + b × dl(d) / avgdl

score(q, d) = Σ  idf(t) × tf(t,d) × (k1 + 1)
             t∈q   -------------------------------------
                    tf(t,d) + k1 × L(d)
```

三段各管一件事：idf 管「这个词有多值钱」，tf 管「这个文档匹配得多强」，L 管「这个文档是不是靠长度占便宜」。

**5.5 多个 query term 的分数怎么叠加**

**问**：不同查询词的分数是直接相加吗？

**答**：是。BM25 的分数就是对 query 中每个不同 term 各算一项，再把这些项直接相加；项与项之间没有乘法、平均或归一化。

```text
score(q, d) = 项(t1, d) + 项(t2, d) + ...
```

三个注意点：

- 每个 term 独立套完整公式（idf × tf 因子），不能先把多个 term 的 tf 加在一起再套公式。
- query 先去重：query 里「模型」出现两次，只贡献一项；不去重会重复加分。
- 只对同时出现在 query 和文档里的 term 求和；query 里有、文档里没有的 term，tf=0，项为 0，直接跳过。
- 最终分数没有归一化到 [0,1]，不是概率，只用于同一批候选之间的排序。

#### 6. 手算例子

三块语料（用英文词，便于手算；中文只是 term 长得不一样）：

| 块 | 内容 | tokens | dl | tf(apple) |
|---|---|---|---|---|
| D1 | apple banana apple | apple, banana, apple | 3 | 2 |
| D2 | apple cherry | apple, cherry | 2 | 1 |
| D3 | banana cherry cherry | banana, cherry, cherry | 3 | 0 |

N=3，avgdl=(3+2+3)/3≈2.667。查询「apple」，df(apple)=2。

idf = ln(1 + (3-2+0.5)/(2+0.5)) = ln(1.6) ≈ 0.470。

D1：

- L = 1 − 0.75 + 0.75 × 3/2.667 ≈ 1.094
- 分母 = 2 + 1.5 × 1.094 ≈ 3.641
- 分子 = 2 × (1.5+1) = 5
- score ≈ 0.470 × 5 / 3.641 ≈ 0.645

D2：

- L = 1 − 0.75 + 0.75 × 2/2.667 ≈ 0.813
- 分母 = 1 + 1.5 × 0.813 ≈ 2.219
- 分子 = 1 × 2.5 = 2.5
- score ≈ 0.470 × 2.5 / 2.219 ≈ 0.530

D3：tf=0，score=0。排序 D1 > D2 > D3。D1 的 tf 是 D2 的两倍，但分数只高约 22%，这就是 tf 饱和；D2 更短，长度因子帮了它，但不足以反超。

分数是相对值，不是 0–1 的百分比，只有排序意义。

#### 7. 排序与边界

- 候选集：查询 term 在 postings 里命中的块的并集；没命中的块不用算。
- 算完分后按 `score` 降序；同分按 `id` 升序，保证测试可复现。
- 只返回 `score > 0` 的块，取前 `top_k`。
- 空查询、查询分词后为空（纯标点）、无候选、`top_k <= 0` → `[]`。
- 不要修改传入的 chunks；返回时用 `{**chunk, "score": score}` 复制。

**为什么同分还要按 id 排**

**问**：BM25 分数相同就相同，为什么还要规定一个 id 顺序？

**答**：不是相关性要求，是工程上的可复现要求（deterministic ranking）。同分时 BM25 不提供先后，如果不指定 tie-breaker，顺序会由 `scores` 的插入顺序决定，而插入顺序受 `set` 的迭代顺序影响，跨进程可能不同。

展开：

- `sorted` 是稳定排序：key 相同就保留输入顺序。
- 输入是 `scores.items()`，顺序是 chunk 第一次被命中的插入顺序。
- 插入顺序取决于 `query_terms = set(tokenize(query))` 的遍历顺序。
- Python 对字符串的哈希默认随机化（`PYTHONHASHSEED`），同一个 query 在不同进程里 set 的迭代顺序可能不同。
- 结果：同样的 query、同样的索引，两次运行中同分块的先后可能不同。

影响：

- 测试断言固定 id 顺序会间歇性失败（flaky）；
- 评测集比较 top-k 时，同分块换位会被算成不一致；
- 日志里的结果无法逐字复现，排查问题困难；
- 用户重复问同一个问题，看到的引用顺序在变。

为什么选 id 当 tie-breaker：

- id 在索引内唯一，且由 `path`、行号、文档内序号组成，跨运行稳定；
- 不需要额外字段，`scores.items()` 里现成就有；
- 字典序比较是确定的，不依赖哈希。

**排序 key 怎么读**

```python
sorted(scores.items(), key=lambda item: (-item[1], item[0]))
```

- `item` 是 `(chunk_id, score)`；
- `-item[1]` 把「分数降序」转换成「负分升序」；
- `item[0]` 是第二键，只在负分相同时才参与比较；
- 元组按字典序比较：先比第一项，相等再比第二项；
- 不用 `reverse=True`，因为它会把整个元组反序，连带 id 变成降序。

#### 8. 和伪代码对照

- tokenize：整体小写对；不用手工列分隔符，正则一次取出连续段更稳；「检查有没有中文」用 `\u4e00-\u9fff`；「按 2 个字分割」要做滑窗，`推导式` 要产出 `推导` 和 `导式` 两个。
- build_index：它不是「另一份 rag 结果」，输入就是 rag 的 chunks；作用是把「每次查询都要重算的分词和计数」提前做一次。
- search：流程是「查询分词去重 → 从 postings 拿候选 → 对每个 term 累加 BM25 分 → 排序取 top_k」。

#### 9. 缩写全称表

| 缩写 | 全称 | 中文 | 记法 |
|---|---|---|---|
| IR | Information Retrieval | 信息检索 | 检索系统的学科名 |
| BM25 | Best Matching 25 | 最佳匹配（第 25 号） | 25 是 Okapi 检索系统的版本编号，不是参数、也不是文档数 |
| CJK | Chinese, Japanese, Korean | 中日韩文字 | 判断汉字范围时用 |
| tf | term frequency | 词频 | 这个 term 在这篇 document 里出现了几次 |
| df | document frequency | 文档频率 | 有多少篇 document 含这个 term |
| idf | inverse document frequency | 逆文档频率 | 越稀有值越大 |
| dl | document length | 文档长度 | 这篇 document 有多少个 term |
| avgdl | average document length | 平均文档长度 | 所有 document 的 dl 平均 |
| N | number of documents | 文档总数 | 索引里有多少块 |
| q | query | 查询 | |
| d | document | 文档 | 本项目里是一个 chunk |
| k1 | — | 词频饱和参数 | 参数符号，没有通用全称；控制 tf 多快达到上限 |
| b | — | 长度归一化参数 | 参数符号，没有通用全称；控制长度惩罚强度 |
| top-k | top k | 前 k 个 | |
| corpus | — | 语料库 | 全部文档的集合 |
| bigram | bi- + -gram | 二元组 | 相邻两个字符组成的 term |
| postings | posting list | 倒排列表 | term → 含它的文档及 tf |
| RAG | Retrieval-Augmented Generation | 检索增强生成 | |

以后遇到新缩写，第一次出现就按「全称 + 中文 + 一句话定义」展开，不能只写缩写。

#### 10. tf 是局部的，不是全库总和

**问**：`build_index` 的 tf，岂不是所有 chunk 分割以后的 term 的总和？这应该是个很大的数目吧？

**答**：不是。tf 永远是「某个 term 在某一篇 document 里的出现次数」，按 `(term, chunk)` 分开存；把所有 tf 加起来确实等于全库 token 总数，但没有任何一个变量保存这个总和，BM25 也不用它打分。

展开：

**三个容易混的「总数」**

| 量 | 含义 | 三块例子 | 本项目实测 |
|---|---|---|---|
| tf(t,d) | term t 在 document d 内出现几次 | D1 的 apple=2，D2 的 apple=1 | 单块最大值 16 |
| df(t) | 含 term t 的 document 数 | apple 在 D1、D2 → df=2 | 最大 84（N=137） |
| Σ_d tf(t,d) | term t 在全库出现总次数（collection frequency, cf，集合频率） | apple 总出现 3 次 | 例如高频词可达上百次 |

BM25 用的是前两个：tf 负责「这一块匹配多强」，df 负责「这个词多稀有」。第三个只是全库统计，不参与打分。

`postings` 存的是第一种：

```text
postings["apple"] = {"D1": 2, "D2": 1}
```

每个 value 都是单独一块里的计数，不是总和。把所有 value 加起来才是全库出现总次数。

**为什么不能把 tf 存成一个总数**

如果只存「apple 在全库出现 3 次」，查询时就不知道哪一块出现了 2 次、哪一块 1 次，没法给单块打分。BM25 的每一项都是针对某个候选块算的，所以 tf 必须按块拆分。

**实测规模**

项目语料 5 份文档、137 块：

| 指标 | 数值 |
|---|---|
| 全库 token 总数（所有 tf 之和） | 29,327 |
| postings 条目数（不同的 term-chunk 对） | 23,580 |
| 不同 term 数（词表大小） | 8,986 |
| 单块最大 tf | 16 |
| 平均块长 avgdl | 214.1 |

29,327 是「建索引时处理过的 token 总次数」，不是某个 tf 变量的值；索引里每个 tf 都是小块内的计数。条目数 23,580 小于 29,327，因为同一块内重复的 term 被合并成一条、只把 tf 加高。2 万多条对内存来说很小。

#### 11. 「票」是什么意思

**问**：票权能理解是一个权重值，但票是什么意思？

**答**：「票」只是为了帮助理解临时用的比喻，不是 IR 术语，面试不要用。BM25 的写法是「对查询里的每个 term 求和」，原文没有给求和项起专门名字；每一项由 `idf(t)` 和该 term 的词频因子相乘得到。

展开：

| 比喻（仅帮助理解） | 公式里对应的东西 | 标准术语 |
|---|---|---|
| 一张票 | `idf(t) × tf 因子` | 求和式中的一项 |
| 票权 | `idf(t)` | inverse document frequency（逆文档频率） |
| 投票力度 | tf 的饱和函数 | term frequency factor |
| 谁有资格投 | `postings[t]` | 包含该 term 的文档集合 |
| 总票数 | `score(q,d)` | BM25 分数 |

代码里也没有「票」这个对象，只有一个累加器：

```text
scores = {}
for term in query_terms:
    for chunk_id, tf in postings[term]:
        scores[chunk_id] += idf(term) * B(tf, dl, avgdl)
```

一个块被两个查询词命中，就累加两次；没被命中的块不会进入 `scores`。

**面试怎么说**：不要说「票权」这类自造词。直接说：「BM25 对每个查询词算一项，项里包含 idf 和词频饱和因子，再把所有项相加。」对方追问时，再展开 idf 和 tf 因子。

**不要靠别名记公式**：BM25 原文没有给求和项单独命名；以公式为准，遇到「term contribution」之类的说法，先确认它指的是不是求和中的一项。

#### 12. 空 term 块与 postings[term]

**问**：没有 term 的块有什么用，不应该直接过滤掉吗？再拿过滤完的 chunks 算 avgdl？`postings[term]` 又是什么？

**答**：对检索索引来说，空 term 块确实没用，可以直接过滤，并用过滤后的集合算 N 和 avgdl；`postings[term]` 是倒排表里的一行，表示「这个 term 出现在哪些块、各出现几次」。

展开：

**空 term 块**

- 空 term 块（只有标点/符号，或切不出任何 term）不会出现在任何 `postings` 行里，查询永远命中不了它；
- 留在 N 里会拉低 avgdl，让其他块看起来更长，所以过滤更一致；
- 处理顺序：先 tokenize → 丢掉 tokens 为空的块 → 用剩下的块算 N、avgdl、postings；
- 边界：如果全被过滤，N=0，avgdl 不能做除法，search 直接返回 `[]`；
- 本项目实测 137 块里空 term 块为 0，所以今天数字不变，但代码要能处理。

**postings[term]**

- 倒排表 `postings` 的 key 是 term，value 是「包含这个 term 的块 → tf」；
- 例子：`postings["apple"] = {"D1": 2, "D2": 1}`；
- 含义：apple 在 D1 出现 2 次、D2 出现 1 次；`df = len(postings["apple"]) = 2`；
- term 不在表里时，查询用 `.get(term, {})` 拿到空表，贡献 0；
- 它只存 `chunk_id` 和 `tf`；原文和 dl 放在另外两张表里，避免同一个块在每个 term 下重复。

### 7.6 token 的三层含义：检索 term、模型 token、字符估算

**问**：term、bigram、token 是不是一回事？`dl` 里的 token 是 `tokenize()` 之后的 term，还是 `estimate_tokens` 统计的那个？`build_index` 只收到 chunks、没收到 tokens，怎么计算 tf？

**答**：token 只是「切分后的单位」的通称，不同系统切法不同。本项目里 BM25 用的 token 是 `tokenize()` 的输出（term：中文 bigram 或英文单词）；`context.py` 的 `estimate_tokens` 只是字符数近似，服务上下文预算；两者不是一回事。`build_index` 内部会对每个 chunk 调用 `tokenize`，所以不需要外部传 tokens。

展开：

#### 三层不要混

| 名称 | 怎么产生 | 例子 | 用在哪 |
|---|---|---|---|
| 字符 | `len(text)`；`estimate_tokens` 返回的就是它 | `"上下文工程"` → 5 | `context.py` 的上下文预算 |
| 检索 term / token | `tokenize(text)` | `"上下文工程"` → 上下 / 下文 / 文工 / 工程 → 4 个 | BM25 的 tf、df、dl |
| 模型 token | 模型自带的 tokenizer（BPE 等） | 未接入 | 上下文窗口、计费 |

`context.py` 里的 `estimate_tokens` 实现是 `0 if text is None else len(text)`，它按**字符数**估算模型 token，不是真正的分词器。中文大约一字一 token、英文大约四字符一 token，所以用字符数做保守近似。它的数字只影响「要不要裁剪上下文」，和检索打分没有关系。

`dl` 用的是第二层：

```text
dl(chunk) = len(tokenize(chunk["text"]))
```

不是 `len(chunk["text"])`，也不是 `estimate_tokens(chunk["text"])`。

#### term、token、bigram 的关系

- **token / term**：在 IR 语境里基本可以互换，指分词后参与计数的单位。本项目的 `tokenize()` 返回的就是 term 列表。
- **bigram**：一种具体的 term，由相邻两个汉字组成。`推导`、`导式` 是 bigram；英文的 `python` 是 term 但不是 bigram；中文单字 `的` 是 term 但不是 bigram。
- 所以关系是：`bigram ⊂ term/token`，不是所有 term 都是 bigram。
- 「分割后的单词」只适用于英文；中文在 bigram 方案下没有「词」的概念，term 是字符对。

例子：

```text
"Python 的 list 推导式"
  → tokenize()
  → ["python", "的", "list", "推导", "导式"]   # 5 个 term
  → dl = 5
  → len(text) / estimate_tokens = 17           # 字符数，不是 5
```

同一个 chunk 里，`dl=5` 而 `estimate_tokens=17`，两个数字服务不同目的。

#### build_index 为什么不需要 tokens 入参

chunk 里有 `text`，tokens 是 `text` 的派生数据：

```text
for chunk in chunks:
    tokens = tokenize(chunk["text"])   # 函数内部现算
    dl = len(tokens)
    tf = Counter(tokens)
    ...
```

这和 `chunk_document(doc)` 一样：调用方只给原始文档，行、窗口、bigram 都在函数内部派生。如果要求调用方先算好 tokens 再传进来，每个调用方都得保证用的是同一个 tokenizer、同样的参数；一旦不一致，索引和查询的 term 对不上，分数会悄悄错掉。

#### tf 和 df 分别怎么来

- `tf`：`Counter(tokens)` 得到「本块每个 term 出现几次」；
- `df`：所有块处理完后，`len(postings[term])` 就是「含这个 term 的块数」；
- `N`：`len(chunks)`；
- `avgdl`：`sum(doc_len.values()) / N`。

查询时只对查询 term 去查 postings，拿到 `(chunk_id, tf)` 列表，再套 BM25 公式。没有出现在 postings 里的 term 贡献 0。

#### 数据粒度：哪些跟 term 走，哪些跟 chunk 走，哪些是全局

**问**：df、tf 这些数据，哪些和 term 一一对应，哪些和 chunk 一一对应，哪些是全局的？

**答**：判断标准是「换掉哪个对象，值会变」。df、idf、cf 换 term 才变；dl、L(d) 换 chunk 才变；N、avgdl 要换整个语料才变；tf 必须同时指定 term 和 chunk 才有值。

| 数据 | 全称 | 对应粒度 | 含义 | 存在哪 / 怎么来 |
|---|---|---|---|---|
| N | number of documents | 全局标量 | 文档总数 | `len(chunks)` |
| avgdl | average document length | 全局标量 | 平均文档长度 | `sum(doc_len.values()) / N` |
| 词表 | vocabulary | 全局集合 | 所有不同的 term | `postings.keys()` |
| df(t) | document frequency | term 级 | 包含 term t 的文档数 | `len(postings[t])` |
| idf(t) | inverse document frequency | term 级派生 | t 的稀有度权重 | 由 N、df(t) 算 |
| cf(t) | collection frequency | term 级 | t 在整个语料中的总出现次数 | `sum(postings[t].values())`，当前实现未用 |
| postings[t] | posting list | term 级结构 | t 对应的倒排列表 | 存储 |
| tf(t,d) | term frequency | (term, chunk) 对级 | t 在文档 d 中出现的次数 | `postings[t][d]` |
| dl(d) | document length | chunk 级 | d 的 term 总数（含重复） | `doc_len[d]` |
| L(d) | — | chunk 级派生 | 长度归一化项 | `1 - b + b * dl(d) / avgdl` |
| path / 行号 / text | — | chunk 级 | 引用所需的元数据 | `chunks[d]` |
| score(q,d) | — | (query, chunk) 对级派生 | 查询 q 对文档 d 的分数 | 打分时累加，不入索引 |

最容易分错的是 tf：

- 它**存放在** `postings[term]` 下面，看起来像 term 级；
- 但数值本身属于 `(term, chunk)` 对：同一个 term 在不同 chunk 里 tf 可以不同，同一个 chunk 对不同 term 的 tf 也不同；
- 存储时只存非零项，没出现就是 tf=0，不占位置。

按存储结构看：

```text
index
├── N            全局标量
├── avgdl        全局标量
├── postings     term → {chunk_id: tf}
│   ├── key      term 级
│   └── value    (term, chunk) 对级
├── doc_len      chunk → dl        chunk 级
└── chunks       chunk → 元数据    chunk 级
```

哪些是派生值、不必单独存：

```text
df(t)  = len(postings[t])
idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
cf(t)  = sum(postings[t].values())
avgdl  = sum(doc_len.values()) / N
L(d)   = 1 - b + b * dl(d) / avgdl
```

判断口诀：**换 term 值就变 → term 级；换 chunk 值就变 → chunk 级；两个都换才变 → 对级；换整个语料才变 → 全局。**

#### 嵌套遍历能不能平铺成一层

**问**：`build_index` 里「遍历 chunks 再遍历 terms」的嵌套循环，能不能平铺？平铺后时间复杂度会变吗？

**答**：能平铺，复杂度不变；嵌套和平铺都要处理同样多的 `(chunk, term)` 对，量级都是 O(总 term 数)。平铺只改变代码形式和常数，除非平铺时额外引入排序或分组，才会改变量级。

计数方式：

- 设 C 个 chunk，第 i 个 chunk 有 L_i 个 term，总 term 数 `T = Σ L_i`。
- 嵌套写法：外层执行 C 次，内层合计执行 T 次，总迭代 O(C + T)。
- 平铺写法：一层循环执行 T 次，总迭代 O(T)。
- 两者只差一个 C；当每个块至少有一个 term 时 C ≤ T，所以同为 O(T)。
- 如果先把所有对物化成列表再遍历，构造列表 O(T) + 遍历 O(T)，还是 O(T)，只是常数翻倍、多一份内存。

平铺的两种形态：

```python
# 物化：多一份 O(T) 的列表
pairs = [(chunk["id"], term) for chunk in chunks for term in tokenize(chunk["text"])]
for chunk_id, term in pairs:
    ...

# 生成器：惰性展开，额外内存 O(1)
pairs = ((chunk["id"], term) for chunk in chunks for term in tokenize(chunk["text"]))
for chunk_id, term in pairs:
    ...
```

但 `build_index` 不建议平铺，原因是**语义需要 chunk 作用域**：

- tf 要先对单个 chunk 做 `Counter(terms)`，块内去重后才能写 `postings[term][chunk_id]`；
- df 要按「块是否包含 term」计数，不能按 term 出现次数计数；
- 平铺成 `(chunk_id, term)` 流后，仍要在流里判断「chunk_id 是否变了」来结算上一个块的 tf，反而把简单逻辑写复杂；
- 真要平铺，元素得带 `(chunk_id, term, tf)`，而这份数据本身就得先按 chunk 聚合，等于把嵌套搬到了构造阶段。

什么时候平铺有实际收益：内层有可以提到外层的重复计算、先过滤掉空块减少外层次数、或者本来就需要跨块批量处理。什么时候会改变量级：平铺后接排序（O(T log T)）或全局分组。

**为什么不是 O(T²)**

双层循环相乘的前提是：外层每执行一次，内层都跑**同样规模**的一整轮。这里不是：

```text
for chunk in chunks:          # C 次
    for term in terms_of(chunk):   # 第 i 次跑 L_i 次
```

内层第 i 次只跑当前块的长度 L_i，不是全局 T 次。总内层执行次数是求和，不是相乘：

```text
Σ_{i=1}^{C} L_i = T
```

所以总迭代是 C + T，不是 C × T，更不是 T × T。T 的定义本来就是「所有块的 term 数之和」，已经把 C 个块的长度加总过了。

会变成 O(T²) 的写法是内层遍历全局集合：

```python
for chunk in chunks:            # C 次
    for term in all_terms:      # 每次都跑 T 次 → O(C × T)
        ...
```

如果再把「每个 term 对所有 term」做一遍，就是 O(T²)。判断方法：把每层循环次数写成输入规模的函数，内层依赖外层时用求和，不依赖时才是相乘。

**面试怎么说**：嵌套层数不影响复杂度，复杂度看最内层语句执行了多少次；C 个块、总 T 个 term，嵌套和平铺都是 O(T)，平铺只是形式变化。

#### build 与 query 的完整流程

**问**：`build_index` 里是对 chunk 本身做 tokenize 吗？我一直以为只对用户提问做 tokenize，然后遍历所有 chunk 去找提问的 term，原来不是这样吗？

**答**：文档和查询都要 tokenize，只是时机不同：chunk 在 build 阶段 tokenize 一次并记下 tf，查询在 search 阶段 tokenize。你说的「只 tokenize 查询，再遍历所有 chunk」是不建索引的暴力做法，它仍然要处理每个 chunk，只是把文档侧的分词放到了每次查询时。

完整流程：

```text
建索引（一次，build_index）
  chunks
    → 逐块 tokenize(chunk["text"]) → tokens
    → Counter(tokens) 得到本块 tf
    → postings[term][chunk_id] = tf
    → doc_len[chunk_id] = len(tokens)
  → N = len(chunks)，avgdl = sum(doc_len) / N

查询（每次，search）
  query
    → tokenize(query) → q_terms
    → 去重
    → 对每个 term 查 postings[term] → [(chunk_id, tf), ...]
    → 用 BM25 给这些候选块累加分数
    → 按 score 降序、id 升序排序
    → 取 top_k，用 chunk_id 从 chunks 取回原文
```

关键差别：

| | 不建索引（暴力） | 建倒排索引 |
|---|---|---|
| 文档 tokenize | 每次查询都做 | build 时做一次 |
| 查询 tokenize | 每次查询 | 每次查询 |
| 找候选 | 遍历全部 chunk | 只查 postings |
| 每次查询成本 | O(全部块) | O(命中的块) |

例子：三块 `D1: apple banana apple`、`D2: apple cherry`、`D3: banana cherry cherry`。

build 之后：

```text
postings["apple"]  = {D1: 2, D2: 1}
postings["banana"] = {D1: 1, D3: 1}
postings["cherry"] = {D2: 1, D3: 2}
```

查询 `apple`：

1. `tokenize("apple")` → `["apple"]`；
2. 查 `postings["apple"]` → 只有 D1、D2；
3. 只给 D1、D2 算分，D3 完全没被访问；
4. D3 的原文甚至不需要读出来。

如果每次都遍历所有 chunk，就要对 D1、D2、D3 各 tokenize 一遍、再数 `apple` 出现几次；倒排索引把这些工作提前做完了。

两边必须用同一个 `tokenize`：建索引时 chunk 怎么切，查询时 query 就怎么切；否则 `postings` 的 key 和查询 term 不是同一套，分数会错。

#### doc_len 和 chunks 为什么不合并

**问**：`doc_len` 和 `chunks` 都用 `chunk_id` 做 key，为什么不合并成一个？

**答**：可以合并，没有对错，只是结构职责不同。分开是 IR 中常见的三分法：倒排表、文档存储、文档长度；合并则少一层、查一次拿两样。本项目规模小，两者性能没差别，选一种并保证 dl 只有一个来源即可。

展开：

- 标准 IR 结构通常分三块：
  - inverted index（倒排索引）：term → 包含它的文档及 tf；
  - document store（文档存储，也叫正排索引）：doc_id → 文档原文和元数据；
  - document lengths（文档长度表）：doc_id → dl，打分时用。
- 三者访问时机不同：打分循环只读 dl；排序完成后才需要原文。分开可以让打分只碰紧凑的数值表，也避免把派生字段写进原文。
- 合并写法：

  ```text
  docs[chunk_id] = {"chunk": chunk, "dl": dl}
  ```

  优点：少一个顶层 key，查一次拿两样。缺点：dl 是索引派生数据，混进了文档数据；返回结果时要记得只取 chunk，不能把整个包装结构丢给调用方。
- 不要两处都存：`doc_len[id]` 和 `docs[id]["dl"]` 同时存在就有两个真值，更新漏一处就会错。
- 本项目建议分开：
  - `doc_len` 只服务打分，`chunks` 只服务返回；
  - 不改动 rag 产出的原 chunk dict；
  - 两个 dict 各建一次，成本可以忽略。
- 如果合并，推荐 `docs[chunk_id] = {"chunk": chunk, "dl": dl}`，search 里 `docs[cid]["dl"]` 取长度、`docs[cid]["chunk"]` 取原文。

**面试怎么说**：倒排索引、文档存储、文档长度表通常分开；小项目合并也可以，关键是不能有重复真值。

#### N 和 avgdl 要不要单独存

**问**：N 是不是可以直接用文档数据的 key 数量得到，不需要单独列？avgdl 也可以直接算吧？

**答**：都可以推导出来，单独存不是必须，是缓存。N 用 `len(chunks)` 是 O(1)；avgdl 要遍历 `doc_len` 求和，建议 build 结束时算一次存起来，避免每次查询重算。

展开：

- `N`（number of documents，文档总数）：
  - 如果 `chunks` 里只放被索引的、非空的块，`N = len(chunks)`；
  - 如果 `chunks` 还包含被过滤掉的空 term 块，`len(chunks)` 就不等于 N，必须另记过滤后的数量；
  - `len(dict)` 是 O(1)，所以 N 存不存都不影响性能，存一份只是让索引自描述。
- `avgdl`（average document length，平均文档长度）：
  - `avgdl = sum(doc_len.values()) / N`；
  - 每次查询都重算是 O(N)，137 块无所谓，但没必要；
  - build 结束时算一次存进索引，属于缓存派生值，不是第二个真值。
- 关键约束：N、avgdl、postings、doc_len 必须基于**同一个过滤后的集合**；不能一个用全集、一个用子集。
- 空索引：N=0 时不能做除法，avgdl 置 0，search 直接返回 `[]`。
- 「存储开销」和「重算开销」是两回事：`doc_len` 每个块只存一个整数，内存很小；avgdl 现算的成本是每次查询遍历 N 个条目求和，不是数组本身占内存大。缓存 avgdl 是把「每次查询 O(N)」换成「build 时 O(N) 一次 + 查询 O(1) 读取」。
- 推荐写法：build 结束时统一算 `N = len(chunks)`、`avgdl = sum(doc_len.values()) / N if N else 0.0`，之后索引不再变，缓存不会失效。

**面试怎么说**：N 可以由文档存储的条目数得到，avgdl 是文档长度的平均值；存不存是缓存选择，关键是只用一份过滤后的数据、在 build 结束时算一次。

#### 打分阶段到底读哪些数据

**问**：「打分循环只读 dl，不需要原文」是什么意思？打分只需要倒排索引和 dl，不用读文档数据吗？

**答**：是的，但更准确地说：打分只读 build 阶段算好的数值统计——tf、df、dl、N、avgdl；原文不在打分输入里。原文只在选出 top-k 之后，用来返回 text、path 和行号。

展开：

| 打分需要的数据 | 来源 | 用途 |
|---|---|---|
| tf(t,d) | `postings[term][chunk_id]` | 词频因子 |
| df(t) | `len(postings[term])` | idf |
| N | 索引元数据 | idf |
| dl(d) | `doc_len[chunk_id]` | 长度因子 |
| avgdl | 索引元数据 | 长度因子 |
| 原文 text | 不读 | 返回 top-k 时才取 |
| path / start_line | 不读 | 返回 top-k 时才取 |

搜索分两段：

1. 打分：query tokenize → 查 postings 拿候选和 tf → 结合 df、N、dl、avgdl 算分 → 排序；
2. 组装结果：只对 top_k 个 chunk_id 查 `chunks[chunk_id]`，取 path、行号、text。

为什么不需要原文：

- 原文在 build 阶段已经被 tokenize 成 terms，并折算成 tf、dl；打分要的就是这些数字；
- 打分时再读原文，就得重新 tokenize、重新计数，等于把索引的工作又做一遍；
- 文本内容不参与排序，只参与展示和引用。

注意：如果以后要做命中高亮，也是排序完成后读 top-k 的原文再找片段，不影响打分阶段。

### 7.7 检索评测集是什么，recall 与 MRR 怎么理解

**问**：检索评测集是做什么的？是用它来测之前的 rag / retrieval 逻辑，然后我抽检几条看数据对不对吗？

**答**：是。评测集 = 一批问题 + 每题「正确答案在哪块文档」的标注；它把检索器从「感觉能用」变成有分数的回归测试，抽检则是核对标注本身没标错。

展开：

**测的是哪一层**：只测 `search()` 返回的排序结果，不测模型回答。检索层的问题（分词切错、chunk 没切到、排序把正确块压到第 6 名）和模型层的问题（检索对了但引用错、编造行号）必须分开定位，混在一起看不出是哪一层的锅。

**为什么需要它**：

- 现在 BM25 能跑、能引用，但「还行」是主观判断。以后改 k1 / b、换分词方式、调 chunk 大小、加向量混合检索，没有数字就分不清是变好还是变坏。
- 它同时是回归测试：改代码后重跑一遍，分数掉了就是改坏了。
- 面试要的是基线数字与改进对比（如 recall@5 82% → 91%），不是「我做过 RAG」。

**一条评测样本长什么样**：

```json
{"id": 1, "question": "BM25 的 k1 控制什么", "path": "AI-Agent疑问解答.md", "start_line": 1640, "end_line": 1660, "difficulty": "direct"}
```

`question` 是查询；`path` + 行号区间是 ground truth（标准答案所在的那块原文）；`difficulty` 只用于分组统计，不参与打分。

**指标定义**：

| 指标 | 含义 | 算法 |
|---|---|---|
| recall@K（召回率） | 前 K 条里至少命中一条的问题占比 | 命中问题数 / 总问题数 |
| MRR@5（Mean Reciprocal Rank，平均倒数排名） | 命中的块排得有多靠前 | 每题取第一个命中的排名 r，记 1/r；前 5 没命中记 0；全部求平均 |

例：3 道题，第一个命中分别排第 1、第 3、没命中 → MRR@5 = (1 + 1/3 + 0) / 3 = 0.444；recall@1 = 1/3，recall@3 = 2/3，recall@5 = 2/3。

**命中怎么算**：

- 严格命中：结果的 `path` 与标注相同，且行号区间有交集。
- 宽松命中：只要 `path` 相同就算命中（容忍 chunk 边界切偏）。

两个都报：严格分低而宽松分高，说明排序基本对但 chunk 边界需要调；两者都低，说明分词或索引有问题。只看宽松分会把 chunk 问题掩盖掉。

**为什么要你抽检 5 条**：ground truth 是 Claude 起草的，标错了（问题其实该命中另一块、或行号区间偏移）会让分数虚高或虚低，后面的改进对比全部失真。抽检核对三件事：那段原文确实回答了问题；区间没有把关键句切在外面；同一问题没有更该命中的块被漏标。

**和端到端评测的分工**：今天这块只回答「检索器有没有把正确资料找出来」；下一块再让 agent 真跑这 30 个问题，统计「最终回答里的引用是否命中 ground truth」，那一步会同时暴露检索错误和模型引用错误，失败案例要能回溯到是哪一层。

**追问：`eval_retrieval.py` 是做什么的，就是算 recall 和 MRR 吗？**

是，但算分只是最后一步。脚本是一条完整流水线：加载并切块文档 → 建索引 → 对每条问题调用 `search(top_k=5)` → 判定每条结果是否命中 ground truth → 汇总指标 → 输出总表与未命中明细。recall / MRR 属于「汇总」这一步，脚本的大部分工作量在加载、调用和命中判定上。

各步骤职责：

| 步骤 | 做什么 | 复用 / 新写 |
|---|---|---|
| 1. 准备语料 | 读 5 份文档并切块 | 复用 `app/rag.chunk_all` |
| 2. 建索引 | 倒排、文档长度、avgdl | 复用 `app/retrieval.build_index` |
| 3. 逐条检索 | 每条问题调 `search(index, q, top_k=5)` | 复用 `app/retrieval.search` |
| 4. 命中判定 | 把每个结果的 path / 行号与标注比对，记下第一个命中的排名（严格、宽松各一份） | 新写 |
| 5. 汇总 | 由排名列表算 recall@1/3/5、MRR@5，可按 difficulty / 文档分组 | 新写 |
| 6. 输出 | 总表 + 未命中明细（问题、期望位置、Top-5 实际结果） | 新写 |

几个容易写错的口径：

- **一次检索、三个 K**：只请求一次 `top_k=5`，recall@1 / @3 从同一份结果的前 1 / 前 3 条里截取，不要为每个 K 重跑检索。
- **MRR 每题只看第一个命中**：一条问题命中多块也只取排名最靠前的那次；没命中记 0。
- **严格与宽松并行算**：同一份 Top-5 结果分别判定两次，输出两组指标。
- **未命中也必须能看见**：只打一个总分无法定位问题；明细要能一眼看出是「没检索到」还是「排在第 6 名」。

示例输出形态：

```
recall@1 0.600  recall@3 0.833  recall@5 0.900  MRR@5 0.712   (strict)
recall@1 0.667  recall@3 0.900  recall@5 0.967  MRR@5 0.768   (loose)

未命中 (strict):
#12  "chunk 重叠为什么能救回被切断的句子"
     期望 AI-Agent疑问解答.md:1440-1475
     Top-5: AI-Agent疑问解答.md:1392-1435 (rank 2, 区间不相交)
            AI-Agent自学路线-12周.md:88-120 (rank 3)
```
