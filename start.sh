#!/bin/bash
# AI视频创作工作流系统 - 一键启动脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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
print_header() {
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}   AI视频创作工作流系统 - 一键启动脚本${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "未找到Python3，请先安装Python 3.9.6或更高版本"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python版本: $PYTHON_VERSION"
}

# 检查Node.js版本
check_node() {
    print_info "检查Node.js版本..."
    
    if ! command -v node &> /dev/null; then
        print_error "未找到Node.js，请先安装Node.js 18或更高版本"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js版本: $NODE_VERSION"
}

# 检查.env文件
check_env() {
    print_info "检查环境配置..."
    
    if [ ! -f "backend/.env" ]; then
        print_warning ".env文件不存在，正在创建..."
        cp backend/.env.example backend/.env
        print_warning "请编辑 backend/.env 文件，填入您的DASHSCOPE_API_KEY"
        print_info "按Enter继续（确保已配置API密钥）..."
        read
    else
        print_success ".env文件已存在"
    fi
}

# 设置后端
setup_backend() {
    print_info "设置后端环境..."
    
    cd backend
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建Python虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    fi
    
    # 激活虚拟环境
    print_info "激活虚拟环境..."
    source venv/bin/activate
    
    # 安装依赖
    print_info "安装Python依赖..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_success "后端依赖安装完成"
    
    cd ..
}

# 设置前端
setup_frontend() {
    print_info "设置前端环境..."
    
    cd frontend
    
    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        print_info "安装前端依赖..."
        npm install
        print_success "前端依赖安装完成"
    else
        print_success "前端依赖已存在"
    fi
    
    cd ..
}

# 启动后端
start_backend() {
    print_info "启动后端服务..."
    
    cd backend
    source venv/bin/activate
    
    # 后台启动
    nohup python -m app.main > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    print_success "后端服务已启动 (PID: $BACKEND_PID)"
    print_info "后端日志: backend.log"
    print_info "后端地址: http://localhost:8000"
    print_info "API文档: http://localhost:8000/docs"
    
    cd ..
}

# 启动前端
start_frontend() {
    print_info "启动前端服务..."
    
    cd frontend
    
    # 后台启动
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    print_success "前端服务已启动 (PID: $FRONTEND_PID)"
    print_info "前端日志: frontend.log"
    print_info "前端地址: http://localhost:5173"
    
    cd ..
}

# 等待服务启动
wait_for_services() {
    print_info "等待服务启动..."
    sleep 3
    
    # 检查后端
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "后端服务健康检查通过"
    else
        print_warning "后端服务可能未完全启动，请查看 backend.log"
    fi
    
    print_success "所有服务启动完成！"
}

# 显示访问信息
show_info() {
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}   服务已启动！${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${BLUE}后端服务:${NC}"
    echo "  - API地址: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - 日志文件: backend.log"
    echo ""
    echo -e "${BLUE}前端服务:${NC}"
    echo "  - 访问地址: http://localhost:5173"
    echo "  - 日志文件: frontend.log"
    echo ""
    echo -e "${YELLOW}管理命令:${NC}"
    echo "  - 查看日志: ./logs.sh"
    echo "  - 停止服务: ./stop.sh"
    echo "  - 重启服务: ./stop.sh && ./start.sh"
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo ""
}

# 主函数
main() {
    print_header
    
    # 检查环境
    check_python
    check_node
    check_env
    
    # 设置环境
    setup_backend
    setup_frontend
    
    # 启动服务
    start_backend
    start_frontend
    
    # 等待并检查
    wait_for_services
    
    # 显示信息
    show_info
}

# 执行主函数
main

