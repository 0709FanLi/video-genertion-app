"""FastAPI应用主入口.

企业级AI视频创作工作流系统后端应用。
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    generation,
    text_to_image,
    file_upload,
    image_to_video,
    video_extension
)
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(generation.router)
    
    # 注册异常处理器
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

