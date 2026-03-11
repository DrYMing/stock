#!/bin/bash
# 一键启动开发环境

echo "🚀 启动股票收益率可视化系统..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  Python虚拟环境不存在，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors pandas
    echo "✅ 虚拟环境创建完成"
else
    source venv/bin/activate
fi

# 检查数据文件
if [ ! -f "src/backend/data/stock_returns.json" ]; then
    echo ""
    echo "📊 处理数据..."
    python scripts/process_data.py
    echo "✅ 数据处理完成"
else
    echo "✅ 数据文件已存在"
fi

# 启动后端
echo ""
echo "🔧 启动后端服务..."
python src/backend/app.py &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo "   API地址: http://localhost:5000"

# 等待后端启动
sleep 2

# 启动前端
echo ""
echo "🎨 启动前端服务..."
cd src/frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo "   访问地址: http://localhost:5173"

# 返回根目录
cd ../..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 系统启动成功！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 前端地址: http://localhost:5173"
echo "🔌 后端API:  http://localhost:5000"
echo "📚 API文档:  docs/api.md"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 服务已停止'; exit 0" INT TERM

# 保持运行
wait
