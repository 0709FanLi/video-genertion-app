# AI视频创作工作流系统 - 后端 (重构版)

## 项目概述

这是一个基于FastAPI的企业级AI视频创作工作流系统后端，采用现代化的Python开发最佳实践重构而成。

### 主要特性

✅ **模块化架构**: 严格的分层设计（API → Service → Model）  
✅ **类型安全**: 完整的类型提示和Pydantic数据验证  
✅ **异步优化**: 使用httpx实现异步HTTP请求  
✅ **依赖注入**: FastAPI依赖注入实现松耦合  
✅ **错误处理**: 统一的异常处理和日志记录  
✅ **重试机制**: 使用tenacity实现智能重试  
✅ **配置管理**: 环境变量和Pydantic Settings  
✅ **测试完备**: 单元测试和集成测试  
✅ **代码质量**: Black/MyPy/Ruff工具链  
✅ **文档完善**: Google风格docstring和OpenAPI文档  

## 技术栈

- **Python**: 3.9.6+
- **Web框架**: FastAPI 0.115.6
- **ASGI服务器**: Uvicorn 0.34.0
- **HTTP客户端**: httpx 0.28.1 (异步)
- **数据验证**: Pydantic 2.10.6
- **重试机制**: tenacity 9.0.0
- **测试框架**: pytest 8.3.5
- **代码格式化**: Black 24.10.0
- **类型检查**: MyPy 1.14.1
- **代码检查**: Ruff 0.9.2

## 项目结构

```
backend/
├── app/                        # 应用核心代码
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── api/                    # API层
│   │   ├── __init__.py
│   │   ├── dependencies.py     # 依赖注入
│   │   └── routes/             # 路由模块
│   │       ├── __init__.py
│   │       └── generation.py   # 内容生成路由
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   └── logging.py          # 日志配置
│   ├── services/               # 服务层
│   │   ├── __init__.py
│   │   ├── llm_service.py      # 大语言模型服务
│   │   └── wanx_service.py     # 通义万相服务
│   ├── schemas/                # 数据模型
│   │   ├── __init__.py
│   │   ├── requests.py         # 请求模型
│   │   └── responses.py        # 响应模型
│   └── exceptions/             # 自定义异常
│       ├── __init__.py
│       └── custom_exceptions.py
├── tests/                      # 测试代码
│   ├── __init__.py
│   ├── conftest.py             # pytest配置
│   ├── test_api.py             # API测试
│   └── test_services.py        # 服务层测试
├── requirements.txt            # 依赖列表
├── pyproject.toml              # 项目配置
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略文件
└── README.md                   # 本文档
```

## 快速开始

### 1. 环境准备

确保已安装Python 3.9.6或更高版本：

```bash
python --version
```

### 2. 创建虚拟环境

```bash
cd backend
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑`.env`文件，填入您的阿里云API密钥：

```env
DASHSCOPE_API_KEY=your-api-key-here
```

### 5. 启动服务

```bash
# 开发模式（支持热重载）
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## API接口

### 1. 生成图片提示词

**接口**: `POST /api/generate-image-prompts`

**请求体**:
```json
{
  "idea": "一只戴墨镜的猫在沙滩上"
}
```

**响应**:
```json
{
  "prompts": [
    "A photorealistic cat wearing sunglasses on a beach...",
    "Digital art of a cool cat on a tropical beach...",
    "Cinematic scene of a stylish cat on sandy beach..."
  ]
}
```

### 2. 生成图片

**接口**: `POST /api/generate-images`

**请求体**:
```json
{
  "prompt": "A photorealistic cat wearing sunglasses on a beach"
}
```

**响应**:
```json
{
  "output": {
    "task_id": "task-123",
    "task_status": "SUCCEEDED",
    "results": [
      {"url": "https://example.com/image1.jpg"},
      {"url": "https://example.com/image2.jpg"}
    ]
  }
}
```

### 3. 优化视频提示词

**接口**: `POST /api/optimise-video-prompt`

**请求体**:
```json
{
  "prompt": "海浪轻轻拍打，猫的尾巴在摇摆"
}
```

**响应**:
```json
{
  "optimised_prompt": "海浪轻轻拍打沙滩，泛起白色的泡沫，猫的尾巴在微风中优雅地摇摆"
}
```

### 4. 生成视频

**接口**: `POST /api/generate-video`

**请求体**:
```json
{
  "image_url": "https://example.com/image.jpg",
  "prompt": "海浪轻轻拍打沙滩，猫的尾巴在摇摆"
}
```

**响应**:
```json
{
  "output": {
    "task_id": "video-task-456",
    "task_status": "SUCCEEDED",
    "video_url": "https://example.com/video.mp4"
  }
}
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 查看测试覆盖率
pytest --cov=app --cov-report=html
```

### 代码格式化

```bash
# 使用Black格式化代码
black app/ tests/

# 检查但不修改
black --check app/ tests/
```

### 类型检查

```bash
# 使用MyPy进行类型检查
mypy app/
```

### 代码检查

```bash
# 使用Ruff进行代码质量检查
ruff check app/ tests/

# 自动修复部分问题
ruff check --fix app/ tests/
```

## 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│         API Layer (routes)          │  ← HTTP请求/响应
├─────────────────────────────────────┤
│       Service Layer (services)      │  ← 业务逻辑
├─────────────────────────────────────┤
│    External APIs (DashScope)        │  ← 外部服务调用
└─────────────────────────────────────┘
```

### 依赖注入流程

```python
# 1. 定义依赖
def get_llm_service() -> LLMService:
    return LLMService()

# 2. 注入到路由
@router.post("/api/generate-image-prompts")
async def generate_prompts(
    request: Request,
    service: LLMService = Depends(get_llm_service)
):
    return service.generate_image_prompts(request.idea)
```

### 异常处理流程

```
Service Layer Exception
    ↓
Custom Exception (ApiError)
    ↓
FastAPI Exception Handler
    ↓
JSON Error Response
```

## 配置说明

所有配置项都可以通过环境变量覆盖，配置优先级：

1. 环境变量
2. `.env`文件
3. 默认值（`app/core/config.py`）

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云API密钥 | 必填 |
| `DEBUG` | 调试模式 | false |
| `LOG_LEVEL` | 日志级别 | INFO |
| `REQUEST_TIMEOUT` | 请求超时时间（秒） | 300 |
| `TASK_POLL_INTERVAL` | 任务轮询间隔（秒） | 5 |
| `MAX_RETRY_ATTEMPTS` | 最大重试次数 | 3 |

## 部署

### 生产环境部署

1. **使用Gunicorn**:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **使用Docker**:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. **使用Systemd**:

创建`/etc/systemd/system/video-gen.service`:

```ini
[Unit]
Description=Video Generation API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

## 性能优化

### 已实现的优化

1. **异步IO**: 使用httpx实现异步HTTP请求
2. **智能重试**: tenacity实现指数退避重试
3. **连接池**: httpx自动管理连接池
4. **日志优化**: 结构化日志减少性能开销

### 建议的优化

1. **添加缓存**: 使用Redis缓存API结果
2. **任务队列**: 使用Celery处理长时间任务
3. **负载均衡**: 部署多个实例
4. **监控告警**: 集成Prometheus/Grafana

## 常见问题

### Q: 如何切换到测试环境？

A: 修改`.env`文件中的`DASHSCOPE_API_KEY`为测试环境密钥。

### Q: 如何调整日志级别？

A: 在`.env`文件中设置`LOG_LEVEL=DEBUG`。

### Q: 如何处理API调用失败？

A: 系统已内置重试机制（最多3次），会自动重试失败的请求。

### Q: 如何扩展新的API接口？

A: 
1. 在`app/schemas/`中定义请求/响应模型
2. 在`app/services/`中实现业务逻辑
3. 在`app/api/routes/`中添加路由
4. 在`tests/`中添加测试

## 重构对比

### 重构前（原main.py）

❌ 单文件158行，所有逻辑混在一起  
❌ 无类型提示  
❌ 硬编码API密钥  
❌ 简单的try-except  
❌ 同步轮询阻塞  
❌ 无测试代码  

### 重构后

✅ 模块化设计，职责清晰  
✅ 完整类型提示  
✅ 环境变量管理  
✅ 统一异常处理  
✅ 异步优化 + 智能重试  
✅ 单元测试覆盖  

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题，请提交Issue或联系开发团队。

---

**重构完成时间**: 2025-10-24  
**遵循规范**: 企业级Python开发规则

