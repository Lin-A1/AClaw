# AClaw - Agent Framework

基于 LangChain v1.0 的模块化 AI Agent 开发框架，支持 Tool Use、对话记忆、多入口部署。

---

## 项目结构

```
AClaw/
├── .env                         # 环境变量（仅 API Key，不提交到 git）
├── .env.example                 # 环境变量模板（仅占位符）
├── .gitignore                   # git 忽略规则
├── .claw/                       # 项目数据（可提交，含非敏感配置）
│   ├── config.json            # 项目元信息 + 运行时配置
│   ├── logs/                  # 日志文件（自动生成，不提交 git）
│   └── memory/                # 记忆存储
│       ├── users/              # 多用户隔离
│       │   └── {user_id}/       # 用户目录
│       │       ├── user.md      # 用户画像
│       │       ├── preferences.md  # 用户偏好
│       │       └── longterm/   # 长期记忆文件
│       └── session.db          # 会话历史（SqliteSaver checkpoint）
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

---

## 配置

统一入口：`from claw.config.settings import settings`

**`.env`**（不提交 git）：仅含 API Key
```bash
MODEL_APIKEY=your-api-key-here
```

**`.claw/config.json`**（可提交）：所有非敏感配置

```json
{
  "name": "AClaw",
  "llm": { "name": "MiniMax-M2.7", "url": "https://api.minimaxi.com/v1" },
  "server": { "host": "0.0.0.0", "port": 18000 },
  "log": { "level": "INFO" },
  "memory": { "root": ".claw/memory" },
  "project": { "role": "claw-agent", "version": "0.1.0" }
}
```

---

## 快速开始

### 1. 安装依赖

```bash
uv sync          # 推荐
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
# 编辑 .env，填入 MODEL_APIKEY
# 编辑 .claw/config.json，配置 LLM / Server / Memory 等
```

### 3. 使用配置

```python
from claw.config.settings import settings
```

### 4. 日志

```python
from claw.utils.logger import logger
logger.info("hello")
```

日志文件位于 `.claw/logs/aclaw_YYYY-MM-DD.log`。

### 5. 内置工具

```python
from claw.tools import ALL_TOOLS   # 全部工具列表，注入 Agent 用
from claw.tools import bash, grep, file_read, file_write, ...
```

8 个内置工具：bash / file_read / file_write / file_edit / glob / grep / todo_write / config。
