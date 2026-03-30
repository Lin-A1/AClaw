#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

# 从 .claw/config.json 读取端口
PORT=$(python -c "import json; print(json.load(open('$ROOT_DIR/.claw/config.json'))['server']['port'])")

echo "==> 安装后端依赖"
cd "$BACKEND_DIR"
uv pip install -r requirements.txt

echo "==> 安装前端依赖"
cd "$ROOT_DIR/frontend"
npm install

echo "==> 启动后端 (端口 $PORT)"
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port "$PORT" &
BACKEND_PID=$!

echo "==> 启动前端"
cd "$ROOT_DIR/frontend"
npm run dev

kill $BACKEND_PID 2>/dev/null || true
