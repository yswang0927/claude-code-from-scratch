#!/bin/bash

# AI Agent 启动脚本

echo "🚀 Starting AI Agent System..."

# 检查是否在正确的目录
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# 启动后端
echo ""
echo "📡 Starting backend server..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/.installed" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and add your ANTHROPIC_API_KEY"
    exit 1
fi

# 在后台启动Python服务
python main.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

cd ..

# 启动前端
echo ""
echo "🎨 Starting frontend..."
cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# 启动前端（前台运行）
echo ""
echo "✨ Starting development servers..."
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

npm run dev

# 清理：当前端停止时，也停止后端
echo ""
echo "🛑 Stopping servers..."
kill $BACKEND_PID 2>/dev/null
echo "✅ All servers stopped"
