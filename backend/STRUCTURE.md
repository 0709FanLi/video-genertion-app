# 项目结构说明

## 目录树

```
backend/
├── app/                                # 应用主目录
│   ├── __init__.py                     # 包初始化
│   ├── main.py                         # FastAPI应用入口，启动配置
│   │
│   ├── core/                           # 核心配置模块
│   │   ├── __init__.py
│   │   ├── config.py                   # Pydantic Settings配置管理
│   │   └── logging.py                  # 日志配置（结构化日志）
│   │
│   ├── api/                            # API层（处理HTTP请求）
│   │   ├── __init__.py
│   │   ├── dependencies.py             # FastAPI依赖注入定义
│   │   └── routes/                     # 路由模块
│   │       ├── __init__.py
│   │       └── generation.py           # 内容生成相关路由
│   │
│   ├── services/                       # 服务层（业务逻辑）
│   │   ├── __init__.py
│   │   ├── llm_service.py              # 大语言模型服务（通义千问）
│   │   └── wanx_service.py             # 通义万相服务（图片/视频生成）
│   │
│   ├── schemas/                        # 数据模型（Pydantic）
│   │   ├── __init__.py
│   │   ├── requests.py                 # API请求模型
│   │   └── responses.py                # API响应模型
│   │
│   └── exceptions/                     # 异常处理
│       ├── __init__.py
│       └── custom_exceptions.py        # 自定义异常类
│
├── tests/                              # 测试代码
│   ├── __init__.py
│   ├── conftest.py                     # pytest配置和fixtures
│   ├── test_api.py                     # API接口测试
│   └── test_services.py                # 服务层单元测试
│
├── requirements.txt                    # Python依赖列表
├── pyproject.toml                      # 项目配置（Black/MyPy/Ruff）
├── .env.example                        # 环境变量示例
├── .gitignore                          # Git忽略文件
├── README.md                           # 项目文档
├── MIGRATION_GUIDE.md                  # 从旧版本迁移指南
└── STRUCTURE.md                        # 本文档
```

## 模块职责

### 1. `app/core/` - 核心模块

#### `config.py`
- **职责**: 应用配置管理
- **功能**:
  - 使用Pydantic Settings管理所有配置
  - 从环境变量加载配置
  - 提供类型验证和默认值
- **主要类**: `Settings`

#### `logging.py`
- **职责**: 日志系统配置
- **功能**:
  - 配置日志格式和输出
  - 提供统一的日志获取接口
  - 支持文件和控制台双输出
- **主要函数**: `setup_logging()`, `get_logger()`

### 2. `app/api/` - API层

#### `dependencies.py`
- **职责**: 依赖注入定义
- **功能**:
  - 定义服务实例的创建函数
  - 提供FastAPI Depends注解
- **主要函数**: `get_llm_service()`, `get_wanx_service()`

#### `routes/generation.py`
- **职责**: 内容生成相关的API路由
- **功能**:
  - 定义4个API端点
  - 处理HTTP请求和响应
  - 调用服务层实现业务逻辑
- **端点**:
  - `POST /api/generate-image-prompts` - 生成图片提示词
  - `POST /api/generate-images` - 生成图片
  - `POST /api/optimise-video-prompt` - 优化视频提示词
  - `POST /api/generate-video` - 生成视频

### 3. `app/services/` - 服务层

#### `llm_service.py`
- **职责**: 大语言模型服务
- **功能**:
  - 封装通义千问API调用
  - 实现提示词生成和优化
  - 集成重试机制
- **主要类**: `LLMService`
- **主要方法**:
  - `generate_image_prompts()` - 生成图片提示词
  - `optimise_video_prompt()` - 优化视频提示词

#### `wanx_service.py`
- **职责**: 通义万相服务
- **功能**:
  - 封装通义万相API调用
  - 实现异步任务创建和轮询
  - 处理图片和视频生成
- **主要类**: `WanxService`
- **主要方法**:
  - `generate_images()` - 生成图片
  - `generate_video()` - 生成视频
  - `_create_task()` - 创建异步任务
  - `_poll_task()` - 轮询任务结果

### 4. `app/schemas/` - 数据模型

#### `requests.py`
- **职责**: API请求数据模型
- **功能**:
  - 定义所有API的请求体结构
  - 提供数据验证（Field约束）
- **模型**:
  - `PromptGenerationRequest`
  - `ImageGenerationRequest`
  - `VideoPromptOptimiseRequest`
  - `VideoGenerationRequest`

#### `responses.py`
- **职责**: API响应数据模型
- **功能**:
  - 定义所有API的响应体结构
  - 确保响应格式统一
- **模型**:
  - `PromptGenerationResponse`
  - `ImageGenerationResponse`
  - `VideoPromptOptimiseResponse`
  - `VideoGenerationResponse`

### 5. `app/exceptions/` - 异常处理

#### `custom_exceptions.py`
- **职责**: 自定义异常类
- **功能**:
  - 定义应用特定的异常类型
  - 提供统一的错误信息结构
- **异常类**:
  - `ApiError` - 基础API错误
  - `DashScopeApiError` - DashScope API错误
  - `TaskFailedError` - 异步任务失败
  - `TaskTimeoutError` - 任务超时

### 6. `app/main.py` - 应用入口

- **职责**: FastAPI应用初始化和配置
- **功能**:
  - 创建FastAPI应用实例
  - 配置CORS中间件
  - 注册路由
  - 注册异常处理器
  - 定义应用生命周期
- **主要函数**: `create_app()`, `lifespan()`

### 7. `tests/` - 测试代码

#### `conftest.py`
- **职责**: pytest配置
- **功能**:
  - 定义测试fixtures
  - 创建测试客户端

#### `test_api.py`
- **职责**: API接口测试
- **功能**:
  - 测试所有API端点
  - 验证请求/响应格式
  - 测试错误场景

#### `test_services.py`
- **职责**: 服务层单元测试
- **功能**:
  - 测试LLMService
  - 测试WanxService
  - Mock外部API调用

## 数据流

### 1. 生成图片提示词流程

```
用户请求
  ↓
API层 (generation.py)
  ├─ 接收 PromptGenerationRequest
  ├─ 验证数据（Pydantic自动）
  └─ 调用 llm_service.generate_image_prompts()
       ↓
Service层 (llm_service.py)
  ├─ 构造系统提示词
  ├─ 调用 _call_api()
  ├─ 调用通义千问API（重试机制）
  ├─ 解析JSON响应
  └─ 返回 list[str]
       ↓
API层
  ├─ 包装为 PromptGenerationResponse
  └─ 返回JSON响应给用户
```

### 2. 生成图片流程

```
用户请求
  ↓
API层 (generation.py)
  ├─ 接收 ImageGenerationRequest
  └─ 调用 wanx_service.generate_images()
       ↓
Service层 (wanx_service.py)
  ├─ 构造请求payload
  ├─ 调用 _create_task() 创建异步任务
  │    └─ httpx异步POST请求
  │         └─ 返回 task_id
  ├─ 调用 _poll_task() 轮询任务
  │    ├─ 每5秒查询一次任务状态
  │    ├─ PENDING/RUNNING → 继续等待
  │    ├─ SUCCEEDED → 返回结果
  │    └─ FAILED → 抛出 TaskFailedError
  └─ 返回包含图片URL的结果
       ↓
API层
  ├─ 包装为 ImageGenerationResponse
  └─ 返回JSON响应给用户
```

### 3. 生成视频流程

```
用户请求
  ↓
API层 (generation.py)
  ├─ 接收 VideoGenerationRequest
  └─ 调用 wanx_service.generate_video()
       ↓
Service层 (wanx_service.py)
  ├─ 构造请求payload（包含图片URL和提示词）
  ├─ 调用 _create_task() 创建异步任务
  ├─ 调用 _poll_task() 轮询任务（最多180次）
  └─ 返回包含视频URL的结果
       ↓
API层
  ├─ 包装为 VideoGenerationResponse
  └─ 返回JSON响应给用户
```

## 依赖关系

```
main.py
  ├─ 依赖 core/config.py (配置)
  ├─ 依赖 core/logging.py (日志)
  ├─ 依赖 api/routes/generation.py (路由)
  └─ 依赖 exceptions/ (异常处理)

api/routes/generation.py
  ├─ 依赖 api/dependencies.py (依赖注入)
  ├─ 依赖 schemas/ (数据模型)
  ├─ 依赖 services/ (业务逻辑)
  └─ 依赖 exceptions/ (异常)

api/dependencies.py
  └─ 依赖 services/ (创建服务实例)

services/llm_service.py
  ├─ 依赖 core/config.py (配置)
  ├─ 依赖 core/logging.py (日志)
  ├─ 依赖 exceptions/ (异常)
  └─ 依赖 openai (外部库)

services/wanx_service.py
  ├─ 依赖 core/config.py (配置)
  ├─ 依赖 core/logging.py (日志)
  ├─ 依赖 exceptions/ (异常)
  └─ 依赖 httpx (外部库)

schemas/*
  └─ 依赖 pydantic (外部库)

exceptions/custom_exceptions.py
  └─ 无内部依赖
```

## 配置流程

```
启动应用
  ↓
加载环境变量
  ├─ .env文件（如果存在）
  └─ 系统环境变量
  ↓
创建Settings实例
  ├─ 读取DASHSCOPE_API_KEY
  ├─ 读取QWEN_BASE_URL
  ├─ 读取WANX_BASE_URL
  └─ 其他配置项
  ↓
初始化日志系统
  ├─ 设置日志级别
  ├─ 配置日志格式
  └─ 添加处理器（文件+控制台）
  ↓
创建FastAPI应用
  ├─ 配置CORS
  ├─ 注册路由
  └─ 注册异常处理器
  ↓
启动服务器
```

## 扩展指南

### 添加新的API端点

1. 在 `app/schemas/requests.py` 定义请求模型
2. 在 `app/schemas/responses.py` 定义响应模型
3. 在相应的Service中实现业务逻辑
4. 在 `app/api/routes/` 中添加路由
5. 在 `tests/` 中添加测试

### 添加新的服务

1. 在 `app/services/` 创建新的服务类
2. 在 `app/api/dependencies.py` 添加依赖注入函数
3. 在路由中使用新服务
4. 添加对应的测试

### 添加新的配置项

1. 在 `app/core/config.py` 的 `Settings` 类中添加字段
2. 在 `.env.example` 中添加说明
3. 更新 `README.md` 的配置说明

## 最佳实践

### 1. 代码风格
- 使用Black格式化所有代码
- 遵循PEP 8命名规范
- 保持函数简短（< 50行）

### 2. 类型提示
- 所有函数添加类型注解
- 使用MyPy进行静态检查
- 避免使用 `Any` 类型

### 3. 文档
- 所有模块、类、函数添加docstring
- 使用Google风格
- 说明参数、返回值、异常

### 4. 错误处理
- 使用自定义异常
- 记录详细日志
- 提供友好的错误信息

### 5. 测试
- 每个功能编写测试
- Mock外部依赖
- 保持测试独立性

---

**文档版本**: 1.0  
**最后更新**: 2025-10-24

