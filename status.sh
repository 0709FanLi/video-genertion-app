#!/bin/bash
# AI视频创作工作流系统 - 状态查看脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}   AI视频创作工作流系统 - 服务状态${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
}

check_backend() {
    echo -e "${BLUE}后端服务状态:${NC}"
    
    # 检查PID文件
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "  状态: ${GREEN}运行中${NC}"
            echo "  PID: $BACKEND_PID"
            
            # 检查健康状态
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                echo -e "  健康检查: ${GREEN}通过${NC}"
            else
                echo -e "  健康检查: ${YELLOW}失败${NC}"
            fi
            
            echo "  地址: http://localhost:8000"
            echo "  文档: http://localhost:8000/docs"
        else
            echo -e "  状态: ${RED}已停止${NC} (PID文件存在但进程不存在)"
        fi
    else
        echo -e "  状态: ${RED}未启动${NC}"
    fi
    
    echo ""
}

check_frontend() {
    echo -e "${BLUE}前端服务状态:${NC}"
    
    # 检查PID文件
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "  状态: ${GREEN}运行中${NC}"
            echo "  PID: $FRONTEND_PID"
            echo "  地址: http://localhost:5173"
        else
            echo -e "  状态: ${RED}已停止${NC} (PID文件存在但进程不存在)"
        fi
    else
        echo -e "  状态: ${RED}未启动${NC}"
    fi
    
    echo ""
}

check_ports() {
    echo -e "${BLUE}端口占用状态:${NC}"
    
    # 检查8000端口
    PORT_8000=$(lsof -ti:8000 2>/dev/null || echo "")
    if [ ! -z "$PORT_8000" ]; then
        echo -e "  8000 (后端): ${GREEN}占用${NC} (PID: $PORT_8000)"
    else
        echo -e "  8000 (后端): ${RED}空闲${NC}"
    fi
    
    # 检查5173端口
    PORT_5173=$(lsof -ti:5173 2>/dev/null || echo "")
    if [ ! -z "$PORT_5173" ]; then
        echo -e "  5173 (前端): ${GREEN}占用${NC} (PID: $PORT_5173)"
    else
        echo -e "  5173 (前端): ${RED}空闲${NC}"
    fi
    
    echo ""
}

check_logs() {
    echo -e "${BLUE}日志文件:${NC}"
    
    if [ -f "backend.log" ]; then
        SIZE=$(du -h backend.log | cut -f1)
        LINES=$(wc -l < backend.log)
        echo "  backend.log: ${SIZE} (${LINES} 行)"
    else
        echo "  backend.log: 不存在"
    fi
    
    if [ -f "frontend.log" ]; then
        SIZE=$(du -h frontend.log | cut -f1)
        LINES=$(wc -l < frontend.log)
        echo "  frontend.log: ${SIZE} (${LINES} 行)"
    else
        echo "  frontend.log: 不存在"
    fi
    
    if [ -f "backend/app.log" ]; then
        SIZE=$(du -h backend/app.log | cut -f1)
        LINES=$(wc -l < backend/app.log)
        echo "  backend/app.log: ${SIZE} (${LINES} 行)"
    else
        echo "  backend/app.log: 不存在"
    fi
    
    echo ""
}

show_commands() {
    echo -e "${YELLOW}管理命令:${NC}"
    echo "  ./start.sh  - 启动所有服务"
    echo "  ./stop.sh   - 停止所有服务"
    echo "  ./logs.sh   - 查看日志"
    echo "  ./status.sh - 查看状态（本脚本）"
    echo ""
}

# 主函数
main() {
    print_header
    check_backend
    check_frontend
    check_ports
    check_logs
    show_commands
}

# 执行主函数
main

