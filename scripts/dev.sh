#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# 加载 nvm（支持 Node 24）
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    source "$NVM_DIR/nvm.sh"
    nvm use 24.13.0 > /dev/null 2>&1 || true
fi

# 从 .claw/config.json 读取端口
PORT=$(python3 -c "import json; print(json.load(open('$ROOT_DIR/.claw/config.json'))['port'])")

echo "==> 检查/安装后端依赖"
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
    uv venv
fi
uv pip install -r requirements.txt

echo "==> 检查/安装前端依赖"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "==> 启动后端 (端口 $PORT)"
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port "$PORT" &
BACKEND_PID=$!

# 等待后端就绪
for i in $(seq 1 10); do
    if curl -sf "http://localhost:$PORT/docs" > /dev/null 2>&1; then
        echo "    后端已就绪 (PID $BACKEND_PID)"
        break
    fi
    sleep 1
done

echo "==> 启动前端"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "服务已启动:"
echo "  后端: http://localhost:$PORT (PID $BACKEND_PID)"
echo "  前端: http://localhost:5173 (PID $FRONTEND_PID)"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待任意进程退出
wait $BACKEND_PID $FRONTEND_PID
