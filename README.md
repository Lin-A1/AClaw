# AClaw

Personal AI assistant powered by Claude, built with Electron + FastAPI.

## 架构

```
Electron 主进程
  ├── BrowserWindow (UI 窗口)
  ├── backend.ts (启动 FastAPI 子进程)
  └── preload/index.ts (IPC 桥接)

Electron 渲染进程 (React)
  └── App.tsx → components/Chat + ChatInput

FastAPI 后端 (Python)
  ├── api/claw.py (路由层)
  ├── services （可调用模块）
  └── config.py (配置读取)
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
├── backend/                      # FastAPI
│   ├── app/
│   │   ├── main.py              # 入口
│   │   ├── config.py            # 配置读取
│   │   ├── services/            # 业务逻辑层
│   │   └── api/                  # 路由层
│   │       └── claw.py
│   └──requirements.txt
│
├── scripts/
│   └── dev.sh                    # 启动脚本
│
└── .claw/                        # 项目配置
    ├── config.json
    ├── memory/
    ├── skills/
    └── mcp/
```

## 后端三层架构（可拓展）

```
请求 → API Route → Service Layer → AI Provider
                   (可插拔)          (配置驱动)
```

- `services/` 每个文件对应一个能力域（LLM/STT/TTS）
- 新增 Provider 只需在对应 service 文件中添加 class
- `config.py` 是唯一读取 `.claw/config.json` 的地方

## 开发

```bash
# 安装依赖并启动
bash scripts/dev.sh
```

依赖：
- Node.js 18+
- Python 3.10+
- pip
