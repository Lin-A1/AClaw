# AClaw

Personal AI assistant powered by MiniMax, built with Electron + FastAPI + LangChain.

## 架构

```
Electron 主进程
  ├── BrowserWindow (UI 窗口)
  ├── backend.ts (启动 FastAPI 子进程)
  └── preload/index.ts (IPC 桥接)

Electron 渲染进程 (React)
  └── App.tsx → components/Chat + ChatInput

FastAPI 后端 (Python)
  ├── api/claw.py (聊天 API - 支持流式)
  ├── api/memory.py (记忆管理 API)
  ├── api/skills.py (Skill 查询 API)
  ├── core/agent/ (Agent 核心 - LangChain)
  ├── core/memory/ (四层记忆系统)
  ├── core/skills/ (Skill 系统)
  ├── core/mcp/ (MCP 客户端)
  ├── core/hooks/ (Hook/Harness 系统)
  ├── core/prompt/ (提示词管理)
  └── core/cot/ (Chain of Thought 记录器)
```

## 目录结构

```
AClaw/
├── frontend/                     # Electron + React
│   ├── src/
│   │   ├── main/                 # 主进程
│   │   │   ├── index.ts
│   │   │   └── backend.ts        # FastAPI 子进程管理
│   │   ├── preload/              # IPC 桥接
│   │   └── renderer/             # 渲染进程 (React)
│   │       ├── App.tsx
│   │       ├── main.tsx
│   │       ├── api/claw.ts
│   │       ├── components/
│   │       └── styles/
│   ├── electron.vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                      # FastAPI + LangChain
│   ├── app/
│   │   ├── main.py              # 入口
│   │   ├── config.py            # 配置读取
│   │   ├── schema.py            # 配置模型
│   │   ├── api/                 # API 路由层
│   │   │   ├── claw.py          # 聊天 API
│   │   │   ├── memory.py        # 记忆管理 API
│   │   │   └── skills.py        # Skill 查询 API
│   │   └── core/                # 核心业务层
│   │       ├── agent/           # Agent 核心
│   │       │   ├── claw_agent.py
│   │       │   ├── subagent.py
│   │       │   ├── context.py
│   │       │   └── output.py
│   │       ├── memory/          # 四层记忆系统
│   │       │   ├── store.py
│   │       │   ├── user.py
│   │       │   ├── preferences.py
│   │       │   ├── session.py
│   │       │   └── longterm.py
│   │       ├── skills/          # Skill 系统
│   │       │   ├── schema.py
│   │       │   ├── loader.py
│   │       │   ├── registry.py
│   │       │   └── tool_adapter.py
│   │       ├── mcp/             # MCP 集成
│   │       │   ├── schema.py
│   │       │   ├── loader.py
│   │       │   ├── client.py
│   │       │   └── tool_adapter.py
│   │       ├── hooks/           # Hook/Harness 系统
│   │       │   ├── types.py
│   │       │   ├── registry.py
│   │       │   ├── callback.py
│   │       │   └── builtin/
│   │       │       ├── safety.py
│   │       │       ├── logger.py
│   │       │       └── memory_flush.py
│   │       ├── prompt/          # 提示词管理
│   │       │   ├── manager.py
│   │       │   └── builder.py
│   │       └── cot/             # Chain of Thought
│   │           └── recorder.py
│   └── requirements.txt
│
├── scripts/
│   └── dev.sh                    # 启动脚本
│
└── .claw/                        # 项目配置
    ├── config.json              # 主配置
    ├── memory/                   # 记忆存储
    │   ├── user.md              # 用户身份档案
    │   ├── preferences.md       # 用户偏好
    │   ├── session/             # 短期会话记忆
    │   └── longterm/            # 长期记忆提炼
    ├── skills/                  # Skill 定义
    │   ├── commit.md
    │   ├── review.md
    │   └── summarize.md
    ├── prompts/                # 提示词模板
    │   ├── system.zh.md
    │   ├── system.en.md
    │   └── fragments/
    │       ├── memory_block.md
    │       ├── skills_block.md
    │       └── tool_result.md
    └── mcp/
        └── mcp.json             # MCP 服务器配置
```

## 四层记忆系统

| 层级 | 来源 | 内容 | 加载方式 |
|------|------|------|----------|
| **用户偏好** | preferences.md | 通信方式、工作习惯 | 每会话加载 |
| **用户信息** | user.md | 身份背景、长期事实 | 每会话加载 |
| **短期记忆** | session/*.json | 当前会话消息 | 实时读写 |
| **长期记忆** | longterm/*.md | 提炼的事实和项目 | 按需加载 |

## Skill 系统

Skill 是可复用的提示词包，在特定上下文下自动加载。

### 内置 Skill

- `commit`: Git commit 生成
- `review`: 代码审查
- `summarize`: 内容总结

### 自定义 Skill

在 `.claw/skills/` 目录创建 `.md` 文件：

```markdown
---
name: my-skill
description: 技能描述
language: zh
tags: [category]
---

# Skill 标题

技能说明和使用方法...
```

## Hook/Harness 系统

Hook 系统在关键事件点执行自定义逻辑。

### 支持的事件

| 事件 | 触发时机 |
|------|----------|
| `PRE_AGENT_RUN` | Agent 运行前 |
| `POST_AGENT_RUN` | Agent 运行后 |
| `PRE_TOOL_USE` | 工具调用前（可阻断） |
| `POST_TOOL_USE` | 工具调用后 |
| `ON_AGENT_ERROR` | Agent 错误时 |

### 内置 Hook

- `safety_check_hook`: 安全检查，阻止危险操作
- `logger_hook`: 日志记录

## Chain of Thought (COT)

支持思维链记录，用于：
- 推理过程追踪
- Debug 和优化
- 用户可见的思考过程

## 开发

```bash
# 安装依赖并启动
bash scripts/dev.sh
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/claw/chat` | POST | 非流式聊天 |
| `/api/claw/chat/stream` | POST | 流式聊天 (SSE) |
| `/api/claw/memory/user` | GET/PUT | 用户记忆 |
| `/api/claw/memory/preferences` | GET/PUT | 用户偏好 |
| `/api/claw/memory/sessions` | GET | 会话列表 |
| `/api/claw/memory/longterm/facts` | GET/POST | 长期记忆 |
| `/api/claw/skills/` | GET | Skill 列表 |
| `/api/claw/skills/{name}` | GET | Skill 详情 |

## 配置

所有配置通过 `.claw/config.json` 管理：

```json
{
  "name": "MultClaw",
  "role": "personal-ai-assistant",
  "server": {
    "llm": {
      "name": "MiniMax-M2.7",
      "url": "https://api.minimaxi.com/v1",
      "apikey": "your-api-key",
      "params": {
        "temperature": 0.7,
        "enable_thinking": true,
        "max_iterations": 20
      }
    },
    "agent": {
      "language": "zh",
      "enable_cot": true,
      "session_max_messages": 50
    }
  }
}
```

## 依赖

- Node.js 18+
- Python 3.10+
- pip
- LangChain
- MCP SDK
