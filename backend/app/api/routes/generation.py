"""内容生成API路由.

提供图片和视频生成相关的API接口。
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.dependencies import LLMServiceDep, WanxServiceDep
from app.core.logging import get_logger
from app.exceptions import ApiError
from app.schemas import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    PromptGenerationRequest,
    PromptGenerationResponse,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoPromptOptimiseRequest,
    VideoPromptOptimiseResponse,
)

router = APIRouter(prefix="/api", tags=["generation"])
logger = get_logger(__name__)


@router.post(
    "/generate-image-prompts",
    response_model=PromptGenerationResponse,
    summary="生成图片提示词",
    description="根据用户的创意想法，生成3个专业的图片生成提示词"
)
async def generate_image_prompts(
    request: PromptGenerationRequest,
    llm_service: LLMServiceDep
) -> PromptGenerationResponse:
    """生成图片提示词API.
    
    Args:
        request: 包含用户想法的请求体
        llm_service: LLM服务依赖注入
        
    Returns:
        包含3个提示词的响应
        
    Raises:
        HTTPException: 当生成失败时抛出
    """
    try:
        logger.info(f"收到图片提示词生成请求，想法: {request.idea}")
        prompts = llm_service.generate_image_prompts(request.idea)
        return PromptGenerationResponse(prompts=prompts)
        
    except ApiError as e:
        logger.error(f"生成图片提示词失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )


@router.post(
    "/generate-images",
    response_model=ImageGenerationResponse,
    summary="生成图片",
    description="根据提示词生成图片，通常需要1-2分钟"
)
async def generate_images(
    request: ImageGenerationRequest,
    wanx_service: WanxServiceDep
) -> ImageGenerationResponse:
    """生成图片API.
    
    Args:
        request: 包含图片提示词的请求体
        wanx_service: Wanx服务依赖注入
        
    Returns:
        包含图片URL列表的响应
        
    Raises:
        HTTPException: 当生成失败时抛出
    """
    try:
        logger.info(f"收到图片生成请求，提示词长度: {len(request.prompt)}")
        result = await wanx_service.generate_images(request.prompt)
        return ImageGenerationResponse(output=result.get("output", {}))
        
    except ApiError as e:
        logger.error(f"生成图片失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )


@router.post(
    "/optimise-video-prompt",
    response_model=VideoPromptOptimiseResponse,
    summary="优化视频提示词",
    description="将用户输入的视频描述优化成更专业的提示词"
)
async def optimise_video_prompt(
    request: VideoPromptOptimiseRequest,
    llm_service: LLMServiceDep
) -> VideoPromptOptimiseResponse:
    """优化视频提示词API.
    
    Args:
        request: 包含原始视频描述的请求体
        llm_service: LLM服务依赖注入
        
    Returns:
        包含优化后提示词的响应
        
    Raises:
        HTTPException: 当优化失败时抛出
    """
    try:
        logger.info(f"收到视频提示词优化请求，原始描述: {request.prompt}")
        optimised = llm_service.optimise_video_prompt(request.prompt)
        return VideoPromptOptimiseResponse(optimised_prompt=optimised)
        
    except ApiError as e:
        logger.error(f"优化视频提示词失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )


@router.post(
    "/generate-video",
    response_model=VideoGenerationResponse,
    summary="生成视频",
    description="根据图片和提示词生成视频，通常需要3-5分钟"
)
async def generate_video(
    request: VideoGenerationRequest,
    wanx_service: WanxServiceDep
) -> VideoGenerationResponse:
    """生成视频API.
    
    Args:
        request: 包含图片URL和视频提示词的请求体
        wanx_service: Wanx服务依赖注入
        
    Returns:
        包含视频URL的响应
        
    Raises:
        HTTPException: 当生成失败时抛出
    """
    try:
        logger.info(
            f"收到视频生成请求，图片: {request.image_url}, "
            f"提示词长度: {len(request.prompt)}"
        )
        result = await wanx_service.generate_video(
            request.image_url,
            request.prompt
        )
        return VideoGenerationResponse(output=result.get("output", {}))
        
    except ApiError as e:
        logger.error(f"生成视频失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )

