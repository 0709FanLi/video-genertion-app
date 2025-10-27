@echo off
REM AI视频创作工作流系统 - Windows一键启动脚本
chcp 65001 >nul
title AI视频创作工作流系统

echo.
echo ================================================
echo    AI视频创作工作流系统 - 一键启动
echo ================================================
echo.

REM 检查Python
echo [INFO] 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到Python，请先安装Python 3.9.6或更高版本
    pause
    exit /b 1
)
python --version
echo.

REM 检查Node.js
echo [INFO] 检查Node.js版本...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到Node.js，请先安装Node.js 18或更高版本
    pause
    exit /b 1
)
node --version
echo.

REM 检查.env文件
echo [INFO] 检查环境配置...
if not exist "backend\.env" (
    echo [WARNING] .env文件不存在，正在创建...
    copy "backend\.env.example" "backend\.env" >nul
    echo [WARNING] 请编辑 backend\.env 文件，填入您的DASHSCOPE_API_KEY
    echo [INFO] 按任意键继续（确保已配置API密钥）...
    pause >nul
)
echo.

REM 设置后端
echo [INFO] 设置后端环境...
cd backend

if not exist "venv" (
    echo [INFO] 创建Python虚拟环境...
    python -m venv venv
    echo [SUCCESS] 虚拟环境创建成功
)

echo [INFO] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo [SUCCESS] 后端依赖安装完成
echo.

cd ..

REM 设置前端
echo [INFO] 设置前端环境...
cd frontend

if not exist "node_modules" (
    echo [INFO] 安装前端依赖...
    call npm install
    echo [SUCCESS] 前端依赖安装完成
) else (
    echo [SUCCESS] 前端依赖已存在
)
echo.

cd ..

REM 启动后端
echo [INFO] 启动后端服务...
cd backend
start "后端服务" cmd /k "venv\Scripts\activate.bat && python -m app.main"
cd ..
echo [SUCCESS] 后端服务已启动
echo [INFO] 后端地址: http://localhost:8000
echo [INFO] API文档: http://localhost:8000/docs
echo.

REM 等待后端启动
echo [INFO] 等待后端启动...
timeout /t 3 /nobreak >nul

REM 启动前端
echo [INFO] 启动前端服务...
cd frontend
start "前端服务" cmd /k "npm run dev"
cd ..
echo [SUCCESS] 前端服务已启动
echo [INFO] 前端地址: http://localhost:5173
echo.

echo ================================================
echo    服务已启动！
echo ================================================
echo.
echo 后端服务:
echo   - API地址: http://localhost:8000
echo   - API文档: http://localhost:8000/docs
echo.
echo 前端服务:
echo   - 访问地址: http://localhost:5173
echo.
echo 注意: 请保持所有命令行窗口打开
echo      关闭窗口将停止对应的服务
echo.
echo ================================================
echo.

pause

