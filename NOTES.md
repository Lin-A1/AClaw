# 代码注意事项

## 项目架构

```
AClaw/
├── .env                         # 环境变量（API Key 等，不提交到 git）
├── .env.example                 # 环境变量模板
├── .gitignore                   # git 忽略规则
├── .claw/                       # 项目数据（可提交结构，不含敏感数据）
│   ├── config.json             # 项目元信息
│   ├── logs/                   # 日志文件（自动生成，不提交 git）
│   └── memory/                 # 记忆存储
│       ├── user.md             # 用户画像（user_info + path）
│       ├── preferences.md       # 用户偏好（preferences + path）
│       └── longterm/           # 长期历史（不读内容）
├── .env                         # 环境变量（API Key 等，不提交到 git）
├── pyproject.toml               # 项目依赖配置（推荐用 uv 或 poetry）
├── requirements.txt             # 依赖列表
├── README.md                    # 项目说明文档
├── NOTES.md                     # 本文件
│
├── src/claw/                   # 核心代码
│   ├── __init__.py
│   │
│   ├── core/                    # 核心 Agent 逻辑
│   │   ├── __init__.py
│   │   ├── agent.py             # Agent 主类，驱动对话循环
│   │   ├── client.py            # SDK 封装
│   │   └── memory.py            # 记忆模块（userprofile/longterm/shortterm）
│   │
│   ├── tools/                   # 内置工具（LangChain @tool）
│   │   ├── __init__.py         # ALL_TOOLS 工具列表导出
│   │   ├── bash.py             # 执行 Shell 命令
│   │   ├── file_read.py        # 读文件（支持分页）
│   │   ├── file_write.py       # 写文件（覆盖）
│   │   ├── file_edit.py        # 精确替换（old → new）
│   │   ├── glob.py             # 文件模式匹配
│   │   ├── grep.py             # 正则内容搜索
│   │   ├── todo_write.py       # Todo 列表管理
│   │   └── config.py            # 配置读写（.env / config.json）
│   │
│   ├── prompts/                 # Prompt 管理
│   │   ├── __init__.py
│   │   ├── system.py            # System Prompt 模板
│   │   └── templates/
│   │       └── agent.txt
│   │
│   ├── config/                  # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py          # 读取 .env，统一配置入口
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── logger.py            # 日志配置
│       └── helpers.py
│
├── interfaces/                   # 不同交互入口
│   ├── cli.py                   # 命令行对话界面
│   ├── api_server.py            # FastAPI / Flask Web 服务
│   └── gradio_app.py            # Gradio UI（可选）
│
├── tests/                       # 单元 & 集成测试
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   └── fixtures/
│       └── sample_responses.json
│
└── examples/                    # 使用示例
    ├── simple_chat.py
    ├── tool_use_demo.py
    └── multi_turn_demo.py
```

### 核心原则

- **配置层先行**：所有新增代码优先从 `settings` 读配置，禁止硬编码
- **LangChain v1.0 原生**：工具用 `@tool`，Agent 用 LangChain 原生类型，不造中间层
- **无骨架文件**：新增模块必须有实质实现，禁止只建空壳占位

---

## 配置说明

统一入口：`from claw.config.settings import settings`

### `.env` — 运行时密钥（不提交 git）

从 `.env.example` 复制后填入真实值。

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MODEL_NAME` | 模型名称 | `MiniMax-M2.7` |
| `MODEL_URL` | API 地址 | `https://api.minimaxi.com/v1` |
| `MODEL_APIKEY` | API 密钥 | —（必填）|
| `MAX_TOKENS` | 最大输出 token 数 | `4096` |
| `TEMPERATURE` | 采样温度 | `1.0` |
| `SYSTEM_PROMPT` | 系统提示词 | `You are a helpful AI assistant.` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `API_HOST` | API 服务监听地址 | `0.0.0.0` |
| `API_PORT` | API 服务端口 | `18000` |

### `.claw/config.json` — 项目元信息（可提交）

| 字段 | 说明 |
|------|------|
| `name` | 项目名称 |
| `role` | Agent 角色标识 |
| `description` | 项目描述 |
| `version` | 版本号 |
| `port` | 默认端口 |

### Settings 对象

```python
settings.llm.name           # MODEL_NAME
settings.llm.url           # MODEL_URL
settings.llm.api_key       # MODEL_APIKEY
settings.llm.max_tokens    # MAX_TOKENS
settings.llm.temperature   # TEMPERATURE
settings.llm.system_prompt # SYSTEM_PROMPT
settings.llm.api_base      # 等于 url + "/messages"（自动拼接）
settings.server.host        # API_HOST
settings.server.port       # API_PORT
settings.log.level         # LOG_LEVEL
settings.project.name      # .claw/config.json → name
settings.project.role      # .claw/config.json → role
settings.project.version   # .claw/config.json → version
```

传给 ChatModel 的典型用法：

```python
from langchain_openai import ChatOpenAI
from claw.config.settings import settings

llm = ChatOpenAI(
    model=settings.llm.name,
    api_key=settings.llm.api_key,
    base_url=settings.llm.url,
    max_tokens=settings.llm.max_tokens,
)
```

---

## 日志

统一入口：`from claw.utils.logger import logger`

日志文件写入 `.claw/logs/aclaw_YYYY-MM-DD.log`，按 10MB 切割，保留 7 天，gzip 压缩旧文件。

**禁止使用 `print()`，统一用 `logger`**：

```python
from claw.utils.logger import logger

logger.debug("debug info")
logger.info("hello")
logger.warning("something wrong")
logger.error("failed")
```

- Console 输出带颜色，级别 INFO+
- 文件记录全量 DEBUG+
- 线程安全，支持多进程（`enqueue=True`）

---

## 记忆模块

统一入口：`from claw.core.memory import memory`

结构：

```
Memory
├── userprofile
│   ├── user_info: str          # .claw/memory/user.md 内容
│   ├── preferences: str        # .claw/memory/preferences.md 内容
│   ├── user_info_path: str     # .claw/memory/user.md 路径
│   └── preferences_path: str   # .claw/memory/preferences.md 路径
├── longterm
│   └── longterm_dir: str       # .claw/memory/longterm/ 路径（只写不读）
├── shortterm: str               # 占位
└── session: str                 # 占位
```

使用方式：

```python
from claw.core.memory import memory

memory.userprofile.user_info       # str
memory.userprofile.preferences     # str
memory.userprofile.user_info_path  # str
memory.userprofile.preferences_path # str
memory.longterm.longterm_dir       # str
```

---

## 内置工具

所有工具使用 LangChain `@tool`，统一从 `agent.tools` 导入：

```python
from claw.tools import ALL_TOOLS   # list，直接注入 Agent
from claw.tools import bash, grep, file_read, ...  # 单个工具
```

| 工具 | 功能 | 输入字段 |
|------|------|---------|
| `bash` | 执行 Shell 命令 | `command`, `timeout?`, `cwd?` |
| `file_read` | 读文件（支持分页） | `path`, `offset?`, `limit?` |
| `file_write` | 写文件（覆盖） | `path`, `content` |
| `file_edit` | 精确字符串替换 | `path`, `old_string`, `new_string` |
| `glob` | 文件模式匹配 | `pattern`, `root?` |
| `grep` | 正则内容搜索 | `pattern`, `path?`, `file_pattern?`, `case_sensitive?` |
| `todo_write` | Todo 列表管理 | `action`, `content?`, `index?` |
| `config` | 配置读写 | `action`, `key?`, `value?`, `scope?` |

状态存储：
- `todo_write` → `.claw/todo.json`
- `config(scope=env)` → `.env`
- `config(scope=config)` → `.claw/config.json`

---

## 主要依赖

| 库 | 用途 |
|---|---|
| `langchain` / `langchain-core` | Agent、Chain、Runnable 核心抽象 |
| `langchain-community` | 第三方集成（工具、memory 等） |
| `langchain-openai` | ChatModel，MiniMax 等 OpenAI 兼容 API |
| `tiktoken` | token 计数，控制上下文长度 |
| `python-dotenv` | 加载 .env 环境变量 |
| `pydantic` | 配置模型（LLM / Server / Log / Project） |
| `loguru` | 日志 |

可选依赖（`uv sync aclaw[api,ui,dev]` 装全量）：

| 库 | 用途 |
|---|---|
| `fastapi` / `uvicorn` | API 服务入口 |
| `sse-starlette` | SSE 流式响应 |
| `gradio` | Gradio 可视化界面 |
| `pytest` / `ruff` / `mypy` | 测试、格式化、类型检查 |

---

## Vibe Coding 后必做清单

每次写完新功能或做完修改后，按顺序执行：

### 1. 代码
- [ ] 新增模块有实质实现，无空壳文件
- [ ] 工具使用 LangChain `@tool`，不再自建 base.py / register_tool
- [ ] 配置从 `settings` 读取，不硬编码
- [ ] `ruff . --fix` 检查并修复格式问题

### 2. README.md
- [ ] 新增了文件/目录 → 更新项目结构
- [ ] 新增了环境变量 → 更新 .env.example + README 环境变量章节
- [ ] 新增了核心概念 → 更新主要依赖表格
- [ ] 新增了使用方式 → 更新快速开始

### 3. pyproject.toml / requirements.txt / NOTES.md
- [ ] 新增了依赖 → pyproject.toml + requirements.txt 两处同步添加
- [ ] 不需要的依赖 → 两处同步删除
- [ ] 新增/修改了配置字段、架构规则、使用方式 → NOTES.md 同步更新

### 4. Git
- [ ] `git status` 查看变更范围
- [ ] 确认 .env / __pycache__ / *.pyc 不在提交列表中
- [ ] commit message 描述改动原因，不只是"add files"
- [ ] 更新并推送仓库

---

## 禁止事项

- 禁止创建无实质内容的占位 .py 文件
- 禁止硬编码配置值（API URL、token 限额等）
- 禁止在 README 中引用不存在的文件/模块路径
- 禁止提交 .env 文件
- 禁止使用 `print()`，统一用 `logger`
