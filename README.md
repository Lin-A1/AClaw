# AClaw

Personal AI assistant powered by MiniMax, built with Electron + FastAPI + LangChain/LangGraph.

## 快速开始

```bash
# 启动后端 + 前端（需要先配置 .claw/config.json 中的 LLM API Key）
bash scripts/dev.sh
```

- **后端**: http://localhost:18000（端口由 `.claw/config.json` 配置）
- **前端**: http://localhost:5173（Electron 应用）
- **API 文档**: http://localhost:18000/docs

> **注意**: 修改端口或 LLM 配置后需重启后端。

## 架构

```
Electron 主进程
  ├── BrowserWindow (UI 窗口)
  └── preload/index.ts (IPC 桥接，访问 .claw/config.json)

Electron 渲染进程 (React)
  └── App.tsx → components/Chat + ChatInput + Settings + Sidebar

FastAPI 后端 (Python)
  ├── api/claw.py      # 聊天 API - 支持流式 SSE
  ├── api/memory.py    # 记忆管理 API
  ├── api/skills.py    # Skill 查询 API
  ├── core/agent/      # Agent 核心 - LangGraph ReAct
  ├── core/memory/     # 四层记忆系统
  ├── core/skills/     # Skill 系统（自动加载提示词包）
  ├── core/mcp/        # MCP 客户端（Model Context Protocol）
  ├── core/hooks/      # Hook/Harness 事件系统
  ├── core/prompt/     # 提示词模板管理（Jinja2）
  └── core/cot/        # Chain of Thought 记录器
```

## 目录结构

```
AClaw/
├── frontend/                     # Electron + React (electron-vite)
│   ├── src/
│   │   ├── main/                 # 主进程 (Electron)
│   │   │   ├── index.ts          # 窗口管理、IPC 注册
│   │   │   └── backend.ts        # 从 .claw/config.json 读取后端地址
│   │   ├── preload/              # 上下文隔离桥接
│   │   └── renderer/             # 渲染进程 (React)
│   │       ├── App.tsx           # 根组件
│   │       ├── api/claw.ts       # 后端配置 API 封装
│   │       └── components/
│   │           ├── Chat.tsx      # 消息列表
│   │           ├── ChatInput.tsx # 输入框
│   │           ├── Sidebar.tsx   # 侧边栏
│   │           └── Settings.tsx  # 配置编辑器
│   ├── electron.vite.config.ts
│   └── package.json
│
├── backend/                      # FastAPI + LangChain
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 唯一读取 .claw/config.json 的地方
│   │   ├── schema.py            # Pydantic 配置模型
│   │   ├── api/
│   │   │   ├── claw.py          # POST /chat, /chat/stream
│   │   │   ├── memory.py         # 记忆 CRUD
│   │   │   └── skills.py         # Skill 查询
│   │   └── core/
│   │       ├── agent/
│   │       │   ├── claw_agent.py # LangGraph ReAct Agent
│   │       │   ├── context.py    # AgentContext
│   │       │   └── output.py     # AgentOutput / AgentChunk
│   │       ├── memory/
│   │       │   ├── store.py      # 四层记忆统一门面
│   │       │   ├── user.py       # 用户身份 (user.md)
│   │       │   ├── preferences.py# 用户偏好 (preferences.md)
│   │       │   ├── session.py    # 短期会话 (session/*.json)
│   │       │   └── longterm.py  # 长期记忆提炼 (longterm/)
│   │       ├── skills/
│   │       │   ├── schema.py    # SkillDef 数据模型
│   │       │   ├── loader.py    # frontmatter 解析
│   │       │   └── registry.py  # Skill 注册表
│   │       ├── mcp/
│   │       │   ├── loader.py    # MCP 服务器配置加载
│   │       │   ├── client.py    # MCP HTTP 客户端
│   │       │   └── tool_adapter.py # MCP → LangChain Tool
│   │       ├── hooks/
│   │       │   ├── types.py     # HookEvent / HookContext
│   │       │   ├── registry.py  # 同步/异步 Hook 注册表
│   │       │   ├── callback.py  # LangChain CallbackHandler
│   │       │   └── builtin/
│   │       │       ├── safety.py   # PRE_TOOL_USE 安全检查
│   │       │       ├── logger.py   # POST_TOOL_USE 日志
│   │       │       └── memory_flush.py # 内存自动 flush
│   │       ├── prompt/
│   │       │   ├── manager.py   # Jinja2 模板 + 语言切换
│   │       │   └── builder.py    # 系统提示词组合
│   │       └── cot/
│   │           └── recorder.py  # CoT 推理过程记录
│   └── requirements.txt
│
├── scripts/
│   └── dev.sh                   # 安装依赖 + 启动后端/前端
│
└── .claw/                       # 项目配置（gitignore 忽略）
    ├── config.json             # 主配置（LLM、路径等）
    ├── memory/                  # 记忆存储
    │   ├── user.md             # 用户身份档案
    │   ├── preferences.md      # 用户偏好
    │   ├── session/            # 短期会话 JSON
    │   └── longterm/          # 长期记忆 MD
    ├── skills/                  # Skill 定义
    │   ├── commit.md
    │   ├── review.md
    │   └── summarize.md
    ├── prompts/                 # 提示词模板
    │   ├── system.zh.md
    │   ├── system.en.md
    │   └── fragments/
    └── mcp/                    # MCP 服务器配置
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/claw/chat` | POST | 非流式聊天，返回 `response` + `session_id` |
| `/api/claw/chat/stream` | POST | SSE 流式聊天，逐块返回 `thinking` / `text` / `tool_call` / `tool_result` |
| `/api/claw/memory/user` | GET/PUT | 用户身份档案 |
| `/api/claw/memory/preferences` | GET/PUT | 用户偏好 |
| `/api/claw/memory/sessions` | GET | 会话列表 |
| `/api/claw/memory/sessions/{id}` | DELETE | 删除会话 |
| `/api/claw/memory/sessions/{id}/history` | GET | 获取会话历史 |
| `/api/claw/memory/longterm/facts` | GET/POST | 长期记忆事实 |
| `/api/claw/skills/` | GET | Skill 列表 |
| `/api/claw/skills/{name}` | GET | Skill 详情 |

### 流式 SSE 格式

`POST /api/claw/chat/stream` 返回 Server-Sent Events 流，每条消息格式：

```
data: {"type": "thinking", "content": "...", "session_id": "..."}\n\n
data: {"type": "text", "content": "...", "session_id": "..."}\n\n
data: {"type": "tool_call", "content": "...", "tool_name": "...", "session_id": "..."}\n\n
data: {"type": "tool_result", "content": "...", "tool_name": "...", "session_id": "..."}\n\n
data: [DONE]\n\n
```

## 四层记忆系统

| 层级 | 存储位置 | 内容 | 加载时机 |
|------|----------|------|----------|
| **用户偏好** | `memory/preferences.md` | 通信风格、工作习惯 | 每次会话 |
| **用户信息** | `memory/user.md` | 身份背景、长期事实 | 每次会话 |
| **短期记忆** | `memory/session/*.json` | 当前会话消息 | 实时读写 |
| **长期记忆** | `memory/longterm/facts.md` | 提炼的事实 | 按需自动加载 |

记忆内容通过 Jinja2 模板注入到系统提示词的 `{{ memory_context }}` 占位符中。

## Skill 系统

Skill 是可复用的**提示词模板**，通过**上下文匹配**按需注入到 Agent 的系统提示词中。不作为 Tool 调用，无往返开销。

### 工作原理

1. **加载**: 启动时从 `.claw/skills/*.md` 加载所有 Skill 定义
2. **匹配**: 每次对话时，根据用户消息的关键词匹配相关 Skill（匹配 name、description、tags、prompt_template）
3. **注入**: 将匹配到的 Skill 的 `prompt_template` 渲染后，注入到 `{{ skills_context }}` 占位符
4. **同轮完成**: Agent 在同一轮 LLM 调用中使用所有上下文，无需额外 tool_call 往返

### 定义格式

在 `.claw/skills/` 创建 `.md` 文件（使用 frontmatter）：

```markdown
---
name: my-skill
description: 技能描述
language: zh
tags: [category, keyword]
---

# Skill 标题

你正在帮助用户完成某项任务...

## 步骤
1. ...
2. ...
```

### 内置 Skill

- `commit`: 分析 staged 变更，生成规范的 git commit message
- `review`: 审查代码质量、安全性和可维护性
- `summarize`: 总结长文本或对话内容为简洁摘要

## Hook / Harness 系统

Hook 在 Agent 运行的关键事件点插入自定义逻辑。

### 支持的事件

| 事件 | 触发时机 | 阻塞 |
|------|----------|------|
| `PRE_AGENT_RUN` | Agent 运行前 | - |
| `POST_AGENT_RUN` | Agent 运行后 | - |
| `ON_AGENT_ERROR` | Agent 出错时 | - |
| `PRE_TOOL_USE` | 工具调用前 | 可阻断 |
| `POST_TOOL_USE` | 工具调用后 | - |
| `PRE_MEMORY_FLUSH` | 记忆 flush 前 | - |
| `POST_MEMORY_FLUSH` | 记忆 flush 后 | - |

### 内置 Hook

- `safety_check_hook` (`PRE_TOOL_USE`): 阻止危险操作
- `logger_hook` (`POST_TOOL_USE`): 记录工具调用日志
- `memory_flush_hook` (`PRE_AGENT_RUN`): 自动 flush 接近 token 限制的会话

## Chain of Thought (COT)

`enable_cot: true` 时，推理过程会写入 `memory/` 目录，并在下一轮对话时通过 `{{ memory_context }}` 注入上下文。

## MCP 集成

MCP (Model Context Protocol) 服务器定义在 `.claw/mcp/mcp.json`：

```json
[
  {
    "name": "filesystem",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
  }
]
```

## 配置

所有配置通过 `.claw/config.json` 管理（**唯一配置源**）：

```json
{
  "name": "MultClaw",
  "role": "personal-ai-assistant",
  "description": "Personal AI assistant powered by MiniMax",
  "port": 18000,
  "server": {
    "llm": {
      "name": "MiniMax-M2.7",
      "url": "https://api.minimaxi.com/v1",
      "apikey": "sk-cp-...",
      "params": {
        "temperature": 0.7,
        "enable_thinking": true,
        "reasoning_split": true,
        "max_tokens": 8192,
        "max_iterations": 20
      }
    },
    "agent": {
      "language": "zh",
      "enable_cot": true,
      "memory_flush_threshold": 0.8,
      "session_max_messages": 50
    }
  },
  "paths": {
    "memory": "memory",
    "skills": "skills",
    "mcp": "mcp",
    "prompts": "prompts"
  }
}
```

> 修改配置后需重启后端服务（`uvicorn` 不会热重载 config）。

### 前端配置编辑器

应用内置 Settings 页面（侧边栏 → 设置），可直接编辑 `config.json`，保存后需手动重启后端。

## 开发

### 环境要求

- **Python**: 3.10+
- **Node.js**: 18+（推荐 Node 24，dev.sh 会自动通过 nvm 加载）
- **包管理**: `uv` (Python), `npm` (Node.js)

### 常用命令

```bash
# 安装依赖 + 启动（推荐）
bash scripts/dev.sh

# 仅启动后端
cd backend && uv venv && uv pip install -r requirements.txt && uvicorn app.main:app --port 18000

# 仅构建前端
cd frontend && npm install && npm run build
```

### 代码风格

Python: 参考 `lin-deeplearning` skill 的代码规范。

## 依赖

- **Python**: fastapi, uvicorn, langchain, langgraph, mcp, jinja2, frontmatter, pyyaml
- **Node.js**: electron, electron-vite, react
