# AClaw - Agent Framework

基于 LangChain v1.0 的模块化 AI Agent 开发框架，支持 Tool Use、对话记忆、多入口部署。

---

## 项目结构

```
AClaw/
├── src/claw/                   # 核心代码
│   ├── core/                    # 核心 Agent 逻辑
│   │   ├── agent.py            # Agent 主类，驱动对话循环
│   │   ├── client.py            # SDK 封装
│   │   └── memory.py            # 对话历史 / 上下文管理
│   ├── tools/                   # 内置工具（LangChain @tool）
│   │   ├── bash.py             # 执行 Shell 命令
│   │   ├── file_read.py        # 读文件（支持分页）
│   │   ├── file_write.py       # 写文件（覆盖）
│   │   ├── file_edit.py        # 精确替换（old → new）
│   │   ├── glob.py             # 文件模式匹配
│   │   ├── grep.py             # 正则内容搜索
│   │   ├── todo_write.py       # Todo 列表管理
│   │   └── config.py            # 配置读写（.env / config.json）
│   ├── prompts/                 # Prompt 管理
│   │   ├── system.py            # System Prompt 模板
│   │   └── templates/agent.txt
│   ├── config/                  # 配置管理
│   │   └── settings.py          # 读取 .env，统一配置入口
│   └── utils/                   # 工具函数
│       ├── logger.py            # 日志配置
│       └── helpers.py
├── interfaces/                   # 不同交互入口
│   ├── cli.py                  # 命令行对话界面
│   ├── api_server.py           # FastAPI Web 服务
│   └── gradio_app.py           # Gradio UI（可选）
├── tests/                       # 单元 & 集成测试
├── examples/                    # 使用示例
│
├── .env                         # 环境变量（不提交 git）
├── .env.example                 # 环境变量模板
├── .claw/config.json            # 项目元信息（可提交）
├── .claw/logs/                 # 日志文件（自动生成）
├── pyproject.toml               # 依赖配置（uv / poetry）
├── requirements.txt            # pip 依赖列表
└── NOTES.md                    # 代码注意事项
```

---

## 环境变量

**`.env`**（不提交 git）：
```bash
MODEL_NAME=MiniMax-M2.7
MODEL_URL=https://api.minimaxi.com/v1
MODEL_APIKEY=your-api-key-here

MAX_TOKENS=4096
TEMPERATURE=1.0

LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=18000
```

**`.claw/config.json`**（可提交）：
```json
{
  "name": "AClaw",
  "role": "claw-agent",
  "description": "Agent Framework",
  "version": "0.1.0",
  "port": 18000
}
```

---

## 快速开始

### 1. 安装依赖

```bash
uv sync          # 推荐
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入真实的 API Key
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
