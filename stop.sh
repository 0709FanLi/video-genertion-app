#!/bin/bash
# AI视频创作工作流系统 - 停止脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印标题
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   停止AI视频创作工作流系统${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# 停止后端
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    print_info "停止后端服务 (PID: $BACKEND_PID)..."
    
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        print_success "后端服务已停止"
    else
        print_warning "后端进程不存在"
    fi
    
    rm backend.pid
else
    print_warning "未找到后端PID文件"
fi

# 停止前端
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    print_info "停止前端服务 (PID: $FRONTEND_PID)..."
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        print_success "前端服务已停止"
    else
        print_warning "前端进程不存在"
    fi
    
    rm frontend.pid
else
    print_warning "未找到前端PID文件"
fi

# 清理遗留的进程
print_info "清理遗留进程..."

# 查找并停止端口8000的进程（后端）
BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null || echo "")
if [ ! -z "$BACKEND_PORT_PID" ]; then
    print_info "发现8000端口进程: $BACKEND_PORT_PID，正在停止..."
    kill -9 $BACKEND_PORT_PID 2>/dev/null || true
    print_success "8000端口进程已停止"
fi

# 查找并停止端口5173的进程（前端）
FRONTEND_PORT_PID=$(lsof -ti:5173 2>/dev/null || echo "")
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    print_info "发现5173端口进程: $FRONTEND_PORT_PID，正在停止..."
    kill -9 $FRONTEND_PORT_PID 2>/dev/null || true
    print_success "5173端口进程已停止"
fi

echo ""
print_success "所有服务已停止！"
echo ""

