#!/bin/bash
# AI视频创作工作流系统 - 日志查看脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}   $1${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
}

# 主菜单
show_menu() {
    print_header "AI视频创作工作流系统 - 日志查看"
    
    echo "请选择要查看的日志:"
    echo ""
    echo "  1) 后端日志 (backend.log)"
    echo "  2) 前端日志 (frontend.log)"
    echo "  3) 后端实时日志 (tail -f)"
    echo "  4) 前端实时日志 (tail -f)"
    echo "  5) 清空所有日志"
    echo "  0) 退出"
    echo ""
    echo -n "请输入选项 [0-5]: "
}

# 查看后端日志
view_backend_log() {
    if [ -f "backend.log" ]; then
        print_header "后端日志 (最后50行)"
        tail -n 50 backend.log
    else
        echo "后端日志文件不存在"
    fi
    echo ""
    echo "按Enter返回菜单..."
    read
}

# 查看前端日志
view_frontend_log() {
    if [ -f "frontend.log" ]; then
        print_header "前端日志 (最后50行)"
        tail -n 50 frontend.log
    else
        echo "前端日志文件不存在"
    fi
    echo ""
    echo "按Enter返回菜单..."
    read
}

# 实时查看后端日志
tail_backend_log() {
    if [ -f "backend.log" ]; then
        print_header "后端实时日志 (Ctrl+C退出)"
        tail -f backend.log
    else
        echo "后端日志文件不存在"
        echo ""
        echo "按Enter返回菜单..."
        read
    fi
}

# 实时查看前端日志
tail_frontend_log() {
    if [ -f "frontend.log" ]; then
        print_header "前端实时日志 (Ctrl+C退出)"
        tail -f frontend.log
    else
        echo "前端日志文件不存在"
        echo ""
        echo "按Enter返回菜单..."
        read
    fi
}

# 清空日志
clear_logs() {
    echo ""
    echo -n "确认要清空所有日志吗? (y/N): "
    read confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        > backend.log 2>/dev/null || true
        > frontend.log 2>/dev/null || true
        > backend/app.log 2>/dev/null || true
        echo ""
        echo -e "${GREEN}[SUCCESS]${NC} 所有日志已清空"
    else
        echo "操作已取消"
    fi
    
    echo ""
    echo "按Enter返回菜单..."
    read
}

# 主循环
while true; do
    clear
    show_menu
    read choice
    
    case $choice in
        1)
            clear
            view_backend_log
            ;;
        2)
            clear
            view_frontend_log
            ;;
        3)
            clear
            tail_backend_log
            ;;
        4)
            clear
            tail_frontend_log
            ;;
        5)
            clear_logs
            ;;
        0)
            echo ""
            echo "退出日志查看"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo "无效选项，请重新输入"
            sleep 1
            ;;
    esac
done

