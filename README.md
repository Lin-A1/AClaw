# AClaw - Anthropic Claude Agent 框架

基于 Anthropic SDK 的模块化 AI Agent 开发框架，支持 Tool Use、对话记忆、多入口部署。

---

## 项目结构

```
AClaw/
├── .env                        # ⚠️ 运行时密钥（API Key 等），不提交 git
├── .env.example                # 环境变量模板，复制后填入真实值
├── .claw/config.json           # 项目元信息，可提交（不含密钥）
│
├── pyproject.toml              # uv / pip 依赖配置
├── requirements.txt            # pip 依赖列表
│
├── src/claude_agent/
│   ├── core/                   # 核心逻辑
│   │   ├── agent.py            # Agent 主循环，驱动对话流程
│   │   ├── client.py           # Anthropic SDK 封装，发送请求/处理响应
│   │   └── memory.py           # 对话历史管理，上下文窗口控制
│   │
│   ├── tools/                  # 工具定义（Tool Use）
│   │   ├── base.py             # Tool 基类 + 注册机制
│   │   ├── web_search.py       # 示例工具：网络搜索
│   │   ├── file_reader.py      # 示例工具：读写文件
│   │   └── calculator.py       # 示例工具：计算器
│   │
│   ├── prompts/                # Prompt 管理
│   │   ├── system.py           # System Prompt 模板，定义 Agent 角色行为
│   │   └── templates/          # Prompt 模板文件
│   │       └── agent.txt
│   │
│   ├── config/                 # 配置加载
│   │   └── settings.py         # 读取 .env + config.json，统一配置入口
│   │
│   └── utils/                  # 工具函数
│       ├── logger.py           # 日志配置
│       └── helpers.py          # 通用辅助函数
│
├── interfaces/                 # 交互入口
│   ├── cli.py                  # 命令行对话界面
│   ├── api_server.py           # FastAPI Web 服务
│   └── gradio_app.py           # Gradio 可视化界面
│
├── tests/                      # 单元 & 集成测试
│   ├── test_agent.py
│   ├── test_tools.py
│   └── fixtures/
│       └── sample_responses.json
│
└── examples/                   # 使用示例
    ├── simple_chat.py          # 基础对话示例
    ├── tool_use_demo.py        # 工具调用示例
    └── multi_turn_demo.py      # 多轮对话示例
```

---

## 文件职责说明

### 运行时密钥（不提交 git）

**`.env`** — API Key、Token 等敏感凭证
```
ANTHROPIC_NAME=MiniMax-M2.7
ANTHROPIC_URL=https://api.minimaxi.com/v1
ANTHROPIC_APIKEY=your-api-key-here
```

### 项目元信息（可提交）

**`.claw/config.json`** — 不含密钥的结构化配置，团队共享
```json
{
  "name": "MultClaw",
  "role": "personal-ai-assistant",
  "description": "Personal AI assistant powered by MiniMax",
  "version": "1.0.0",
  "port": 18000
}
```

### 核心逻辑

**`src/claude_agent/core/agent.py`**
- Agent 主循环：接收用户输入 → 构建消息列表 → 调用 LLM → 解析响应 → 执行工具或返回文本
- 管理对话轮次、最大迭代次数、停止条件

**`src/claude_agent/core/client.py`**
- 封装 Anthropic SDK（`anthropic` 包）
- 处理 `messages`、`tools`、`system_prompt` 的组装
- 流式输出（streaming）支持

**`src/claude_agent/core/memory.py`**
- 管理对话历史（`messages` 列表）
- 控制上下文窗口长度（token 预算）
- 支持历史摘要（summarization）策略

### 工具系统

**`src/claude_agent/tools/base.py`**
- Tool 基类定义（`name`、`description`、`parameters`、`execute()`）
- 工具注册表（Decorator 或显式注册）

**`src/claude_agent/tools/*.py`**
- 每个文件一个工具，继承基类
- `web_search.py`：搜索工具
- `file_reader.py`：文件读写工具
- `calculator.py`：计算工具

### Prompt 管理

**`src/claude_agent/prompts/system.py`**
- 定义 System Prompt 模板
- 包含 Agent 角色设定、行为约束、工具说明

**`src/claude_agent/prompts/templates/agent.txt`**
- Agent 对话模板，可按场景切换

### 配置加载

**`src/claude_agent/config/settings.py`**
- 统一加载 `.env`（密钥）+ `.claw/config.json`（元信息）
- 提供类型化配置访问接口（`settings.llm.name`、`settings.server.port` 等）

### 交互入口

**`interfaces/cli.py`** — 命令行界面，适合调试
**`interfaces/api_server.py`** — FastAPI 服务，适合生产接入
**`interfaces/gradio_app.py`** — Gradio 界面，适合快速演示

---

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入真实的 API Key
```

### 3. 运行示例

```bash
# 命令行对话
python -m interfaces.cli

# 或直接运行示例
python examples/simple_chat.py
```

---

## 开发指南

### 添加新工具

1. 在 `src/claude_agent/tools/` 新建文件，如 `my_tool.py`
2. 继承 `BaseTool`，实现 `name`、`description`、`parameters`、`execute()`
3. 在 `tools/base.py` 的注册表中添加（或使用装饰器）
4. 重启 Agent 即可使用

### 添加新交互入口

1. 在 `interfaces/` 新建文件
2. 实例化 `ClaudeAgent` 并调用其 `run()` 方法
3. 处理输入输出格式（CLI 文本 / API JSON / UI 组件）

### 配置加载流程

```
.env ──────────────► settings.py ◄─────── config.json
(ANTHROPIC_APIKEY)      │            (name, port, ...)
                        │
                        ▼
                   Agent / Client
```
