# 一键启动脚本使用指南

## 概述

本项目提供了完整的一键启动脚本，支持macOS/Linux和Windows系统。

## 文件说明

### macOS/Linux脚本

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start.sh` | 一键启动 | 启动前后端所有服务 |
| `stop.sh` | 停止服务 | 停止所有运行中的服务 |
| `status.sh` | 查看状态 | 查看服务运行状态 |
| `logs.sh` | 查看日志 | 交互式日志查看工具 |

### Windows脚本

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start.bat` | 一键启动 | 启动前后端所有服务 |

## 使用方法

### macOS/Linux

#### 1. 首次使用（一键启动）

```bash
# 1. 进入项目目录
cd video_generation_app

# 2. 配置API密钥（重要！）
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，填入您的 DASHSCOPE_API_KEY

# 3. 执行启动脚本
./start.sh
```

启动脚本会自动完成：
- ✅ 检查Python和Node.js版本
- ✅ 创建Python虚拟环境
- ✅ 安装后端依赖
- ✅ 安装前端依赖
- ✅ 启动后端服务（后台运行）
- ✅ 启动前端服务（后台运行）
- ✅ 执行健康检查

#### 2. 查看服务状态

```bash
./status.sh
```

输出示例：
```
================================================
   AI视频创作工作流系统 - 服务状态
================================================

后端服务状态:
  状态: 运行中
  PID: 12345
  健康检查: 通过
  地址: http://localhost:8000
  文档: http://localhost:8000/docs

前端服务状态:
  状态: 运行中
  PID: 12346
  地址: http://localhost:5173

端口占用状态:
  8000 (后端): 占用 (PID: 12345)
  5173 (前端): 占用 (PID: 12346)
```

#### 3. 查看日志

```bash
./logs.sh
```

交互式菜单：
```
1) 后端日志 (backend.log)
2) 前端日志 (frontend.log)
3) 后端实时日志 (tail -f)
4) 前端实时日志 (tail -f)
5) 清空所有日志
0) 退出
```

#### 4. 停止服务

```bash
./stop.sh
```

自动停止所有服务并清理进程。

#### 5. 重启服务

```bash
./stop.sh && ./start.sh
```

### Windows

#### 1. 首次使用（一键启动）

```cmd
REM 1. 进入项目目录
cd video_generation_app

REM 2. 配置API密钥（重要！）
copy backend\.env.example backend\.env
REM 编辑 backend\.env 文件，填入您的 DASHSCOPE_API_KEY

REM 3. 执行启动脚本（双击或命令行）
start.bat
```

启动脚本会自动完成：
- ✅ 检查Python和Node.js版本
- ✅ 创建Python虚拟环境
- ✅ 安装后端依赖
- ✅ 安装前端依赖
- ✅ 打开两个新窗口启动前后端服务

**注意**: Windows版本会打开两个新的命令行窗口：
- 一个窗口运行后端服务
- 一个窗口运行前端服务
- **关闭窗口将停止对应的服务**

#### 2. 停止服务

直接关闭后端和前端的命令行窗口即可。

## 详细功能说明

### start.sh / start.bat

**功能**:
1. 环境检查
   - 检查Python 3.9.6+
   - 检查Node.js 18+
   - 检查.env配置文件

2. 环境设置
   - 创建Python虚拟环境（如果不存在）
   - 安装/更新Python依赖
   - 安装/更新Node.js依赖

3. 启动服务
   - 后台启动后端（8000端口）
   - 后台启动前端（5173端口）
   - 记录进程PID

4. 健康检查
   - 验证后端健康状态
   - 显示访问地址

**输出文件**:
- `backend.pid` - 后端进程ID
- `frontend.pid` - 前端进程ID
- `backend.log` - 后端日志
- `frontend.log` - 前端日志

### stop.sh

**功能**:
1. 读取PID文件
2. 停止后端进程
3. 停止前端进程
4. 清理端口占用
5. 删除PID文件

**清理策略**:
- 优先使用PID文件停止进程
- 如果失败，强制清理端口占用
- 确保8000和5173端口释放

### status.sh

**功能**:
1. 检查后端服务状态
   - 进程是否运行
   - 健康检查API
   - 显示访问地址

2. 检查前端服务状态
   - 进程是否运行
   - 显示访问地址

3. 检查端口占用
   - 8000端口（后端）
   - 5173端口（前端）

4. 查看日志文件
   - 显示日志文件大小
   - 显示日志行数

### logs.sh

**功能**:
1. 查看后端日志（最后50行）
2. 查看前端日志（最后50行）
3. 实时跟踪后端日志（tail -f）
4. 实时跟踪前端日志（tail -f）
5. 清空所有日志文件

**支持的日志文件**:
- `backend.log` - 后端标准输出/错误
- `frontend.log` - 前端标准输出/错误
- `backend/app.log` - 后端应用日志

## 常见问题

### Q1: 启动失败，提示端口被占用

**解决方法**:
```bash
# 1. 停止所有服务
./stop.sh

# 2. 检查状态
./status.sh

# 3. 如果仍有端口占用，手动清理
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Q2: 脚本没有执行权限

**解决方法** (macOS/Linux):
```bash
chmod +x start.sh stop.sh logs.sh status.sh
```

### Q3: 后端启动失败

**排查步骤**:
```bash
# 1. 查看日志
./logs.sh  # 选择 1) 后端日志

# 2. 检查.env配置
cat backend/.env

# 3. 手动测试
cd backend
source venv/bin/activate
python -m app.main
```

常见原因：
- ❌ 未配置DASHSCOPE_API_KEY
- ❌ Python版本过低（需要3.9.6+）
- ❌ 依赖安装失败

### Q4: 前端启动失败

**排查步骤**:
```bash
# 1. 查看日志
./logs.sh  # 选择 2) 前端日志

# 2. 手动测试
cd frontend
npm run dev
```

常见原因：
- ❌ Node.js版本过低（需要18+）
- ❌ node_modules未安装或损坏
- ❌ 端口5173被占用

### Q5: 如何修改端口？

**后端端口**（默认8000）:
修改 `backend/app/main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,  # 修改这里
        ...
    )
```

**前端端口**（默认5173）:
修改 `frontend/vite.config.js`:
```javascript
export default defineConfig({
  server: {
    port: 5173,  // 修改这里
    ...
  }
})
```

### Q6: Windows下看不到彩色输出？

这是正常的，Windows命令行不支持ANSI颜色代码。功能完全正常，只是没有颜色显示。

## 高级用法

### 开发模式（手动启动）

如果需要更灵活的控制，可以手动启动：

**后端**:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate.bat
python -m app.main
```

**前端**:
```bash
cd frontend
npm run dev
```

### 生产模式启动

使用Gunicorn启动后端（推荐生产环境）:
```bash
cd backend
source venv/bin/activate
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 自定义启动参数

修改 `start.sh` 中的启动命令：
```bash
# 后端启动部分
nohup python -m app.main \
  --host 0.0.0.0 \
  --port 8080 \
  --reload \
  > ../backend.log 2>&1 &
```

## 访问地址

启动成功后，可以访问：

### 后端
- **API地址**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 前端
- **应用地址**: http://localhost:5173

## 脚本特性

### ✅ 优点
1. **一键启动**: 无需手动执行多个命令
2. **自动化**: 自动检查环境、安装依赖
3. **后台运行**: 服务在后台运行，不阻塞终端
4. **日志管理**: 统一管理所有日志
5. **健康检查**: 自动验证服务状态
6. **进程管理**: 自动记录和清理进程
7. **跨平台**: 支持macOS/Linux/Windows

### ⚠️ 注意事项
1. **首次启动较慢**: 需要下载和安装依赖
2. **API密钥必填**: 必须配置DASHSCOPE_API_KEY
3. **端口冲突**: 确保8000和5173端口未被占用
4. **虚拟环境**: 自动创建，无需手动管理
5. **日志文件**: 会持续增长，建议定期清理

## 故障排除

如果遇到问题，按以下顺序排查：

1. **查看状态**: `./status.sh`
2. **查看日志**: `./logs.sh`
3. **停止服务**: `./stop.sh`
4. **清理进程**: 手动kill端口进程
5. **重新启动**: `./start.sh`

如果问题仍未解决，请查看详细日志或提交Issue。

---

**文档版本**: 1.0  
**最后更新**: 2025-10-24

