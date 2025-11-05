"""FastAPI应用主入口.

企业级AI视频创作工作流系统后端应用。
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.routes import (
    generation,
    text_to_image,
    file_upload,
    image_to_video,
    video_extension,
    auth,
    library
)
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.database.session import init_db
from app.exceptions import ApiError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理.
    
    在应用启动和关闭时执行必要的初始化和清理操作。
    
    Args:
        app: FastAPI应用实例
        
    Yields:
        None
    """
    # 启动时初始化
    logger = get_logger(__name__)
    logger.info(f"{settings.app_name} v{settings.app_version} 启动中...")
    logger.info(f"调试模式: {settings.debug}")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info(f"{settings.app_name} 关闭中...")


def create_app() -> FastAPI:
    """创建并配置FastAPI应用.
    
    Returns:
        配置好的FastAPI应用实例
    """
    # 初始化日志
    setup_logging()
    
    # 创建应用实例
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置CORS
    # 支持通过环境变量CORS_ORIGINS设置（逗号分隔）
    # 检查环境变量，如果设置了CORS_ORIGINS则使用它
    import os
    cors_origins_env = os.getenv("CORS_ORIGINS")
    if cors_origins_env:
        if cors_origins_env.strip() == "*":
            cors_origins = ["*"]
        else:
            cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    else:
        cors_origins = settings.cors_origins
    
    # 开发环境：如果debug模式且origins列表包含"*"，允许所有源
    if settings.debug and "*" in cors_origins:
        logger = get_logger(__name__)
        logger.warning("⚠️ CORS配置为允许所有源（开发模式）")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],  # 暴露所有响应头
    )
    
    # 注册异常处理器
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """请求验证错误处理.
        
        记录详细的验证错误信息，便于调试。
        
        Args:
            request: 请求对象
            exc: 验证异常实例
            
        Returns:
            JSON格式的错误响应
        """
        logger = get_logger(__name__)
        errors = exc.errors()
        
        # 将错误信息转换为可序列化的格式
        serializable_errors = []
        for error in errors:
            serializable_error = {
                "loc": list(error.get("loc", [])),
                "msg": str(error.get("msg", "")),
                "type": str(error.get("type", ""))
            }
            # 处理 ctx 中的异常对象
            if "ctx" in error and isinstance(error["ctx"], dict):
                ctx = {}
                for key, value in error["ctx"].items():
                    if isinstance(value, Exception):
                        ctx[key] = str(value)
                    else:
                        ctx[key] = value
                serializable_error["ctx"] = ctx
            serializable_errors.append(serializable_error)
        
        # 格式化错误信息以便于调试
        error_summary = []
        for err in serializable_errors:
            loc = " -> ".join(str(x) for x in err.get("loc", []))
            msg = err.get("msg", "")
            error_summary.append(f"{loc}: {msg}")
        
        logger.error(
            f"请求验证失败: {request.url.path}\n详细错误: {'; '.join(error_summary)}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "请求参数验证失败",
                "detail": serializable_errors
            }
        )
    
    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        """统一API错误处理.
        
        Args:
            request: 请求对象
            exc: API异常实例
            
        Returns:
            JSON格式的错误响应
        """
        logger = get_logger(__name__)
        logger.error(
            f"API错误: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "detail": exc.detail
            }
        )
    
    # 注册路由
    app.include_router(auth.router, prefix="/api")  # 认证路由
    app.include_router(library.router)  # 资源库路由
    app.include_router(generation.router)
    app.include_router(text_to_image.router)
    app.include_router(file_upload.router)
    app.include_router(image_to_video.router, prefix="/api/image-to-video", tags=["image-to-video"])
    app.include_router(video_extension.router)
    
    # 健康检查端点
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """健康检查接口.
        
        Returns:
            包含状态信息的字典
        """
        return {
            "status": "healthy",
            "version": settings.app_version
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

