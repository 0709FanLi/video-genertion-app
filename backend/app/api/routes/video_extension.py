"""视频扩展API路由.

提供视频扩展功能，基于原始视频生成扩展内容。
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.video_extension import (
    VideoExtensionRequest,
    VideoExtensionResponse,
    ModelsListResponse
)
from app.services.google_veo_service import google_veo_service
from app.exceptions.custom_exceptions import ApiError

router = APIRouter(prefix="/api/video-extension", tags=["video-extension"])
logger = get_logger(__name__)


@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="获取视频扩展模型列表",
    description="返回所有可用的视频扩展模型及其规格信息"
)
async def get_models() -> ModelsListResponse:
    """获取视频扩展模型列表API.
    
    Returns:
        包含所有可用模型信息的响应
    """
    logger.info("获取视频扩展模型列表")
    
    return ModelsListResponse(
        video_extension_models=settings.video_extension_models
    )


@router.post(
    "/extend",
    response_model=VideoExtensionResponse,
    summary="扩展视频",
    description="基于原始视频和提示词生成扩展内容"
)
async def extend_video(
    request: VideoExtensionRequest
) -> VideoExtensionResponse:
    """扩展视频API.
    
    核心流程：
    1. 验证请求参数
    2. 从OSS下载原始视频
    3. 调用Google Veo API进行视频扩展
    4. 上传扩展后的视频到OSS
    5. 返回结果
    
    Args:
        request: 视频扩展请求参数
        
    Returns:
        包含扩展后视频URL和元数据的响应
        
    Raises:
        HTTPException: 参数验证失败或扩展失败
    """
    logger.info(
        f"收到视频扩展请求: model={request.model}, "
        f"aspect_ratio={request.aspect_ratio}, "
        f"video_url={request.video_url[:100]}"
    )
    
    try:
        # 验证模型
        if request.model not in settings.video_extension_models:
            raise ApiError(
                message="不支持的模型",
                detail=f"{request.model} 不在可用模型列表中"
            )
        
        # 目前仅支持Google Veo 3.1
        if request.model == "google-veo-3.1":
            result = await google_veo_service.extend_video(
                video_url=request.video_url,
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio,
                negative_prompt=request.negative_prompt
            )
        else:
            raise ApiError(
                message="模型尚未实现",
                detail=f"{request.model} 功能尚未实现"
            )
        
        logger.info(f"视频扩展成功: {result['extended_video_url'][:100]}")
        
        return VideoExtensionResponse(**result)
        
    except ApiError as e:
        logger.error(f"视频扩展失败: {e.message} - {e.details}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": e.message,
                "detail": e.details
            }
        )
    except Exception as e:
        logger.error(f"视频扩展异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "视频扩展失败",
                "detail": str(e)
            }
        )

