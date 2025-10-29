"""文生图API路由.

提供完整的文本生成图片功能，包括:
- 提示词优化（通义千问/DeepSeek可选）
- 文生图（火山即梦/通义万相可选）
- 多图生图（通义万相参考图模式）
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger
from app.services.llm_service import llm_service
from app.services.deepseek_service import deepseek_service
from app.services.volc_jimeng_service import volc_jimeng_service
from app.services.wanx_i2i_service import wanx_i2i_service
from app.services.qwen_image_service import qwen_image_service
from app.exceptions.custom_exceptions import ApiError

router = APIRouter(prefix="/api/text-to-image", tags=["text-to-image"])
logger = get_logger(__name__)


# ==================== Schemas ====================

class PromptOptimizeRequest(BaseModel):
    """提示词优化请求."""
    
    prompt: str = Field(..., description="用户输入的原始提示词", min_length=1, max_length=500)
    model: str = Field(
        default="qwen-plus",
        description="优化模型: qwen-plus 或 deepseek-v3"
    )
    language: str = Field(default="en", description="输出语言: en/zh")


class PromptOptimizeResponse(BaseModel):
    """提示词优化响应."""
    
    original_prompt: str = Field(..., description="原始提示词")
    optimized_prompt: str = Field(..., description="优化后的提示词")
    model: str = Field(..., description="使用的模型")


class TextToImageRequest(BaseModel):
    """文生图请求."""
    
    prompt: str = Field(..., description="图片生成提示词", min_length=1)
    model: str = Field(
        default="volc-jimeng",
        description="生成模型: volc-jimeng / aliyun-wanx / aliyun-wanx-i2i"
    )
    size: str = Field(default="1024x1024", description="图片尺寸")
    num_images: int = Field(default=1, ge=1, le=4, description="生成图片数量")
    reference_image_urls: Optional[List[str]] = Field(
        default=None,
        description="参考图片URL列表（仅aliyun-wanx-i2i支持）"
    )
    style: Optional[str] = Field(default=None, description="风格参数（可选）")


class TextToImageResponse(BaseModel):
    """文生图响应."""
    
    image_urls: List[str] = Field(..., description="生成的图片URL列表")
    model: str = Field(..., description="使用的模型")
    num_images: int = Field(..., description="生成的图片数量")


class ModelsListResponse(BaseModel):
    """模型列表响应."""
    
    text_to_image_models: Dict[str, Any] = Field(..., description="文生图模型列表")
    prompt_optimization_models: Dict[str, Any] = Field(..., description="提示词优化模型列表")


# ==================== API Endpoints ====================

@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="获取模型列表",
    description="获取可用的文生图模型和提示词优化模型列表"
)
async def get_models() -> ModelsListResponse:
    """获取模型列表API.
    
    Returns:
        包含所有可用模型信息的响应
    """
    logger.info("获取模型列表")
    
    return ModelsListResponse(
        text_to_image_models=settings.text_to_image_models,
        prompt_optimization_models=settings.prompt_optimization_models
    )


@router.post(
    "/optimize-prompt",
    response_model=PromptOptimizeResponse,
    summary="优化提示词",
    description="使用AI模型优化用户输入的提示词，支持通义千问和DeepSeek"
)
async def optimize_prompt(request: PromptOptimizeRequest) -> PromptOptimizeResponse:
    """优化提示词API.
    
    Args:
        request: 提示词优化请求
    
    Returns:
        包含优化后提示词的响应
    
    Raises:
        HTTPException: 当优化失败时抛出
    """
    try:
        logger.info(
            f"收到提示词优化请求: model={request.model}, "
            f"prompt={request.prompt[:50]}..."
        )
        
        # 验证模型
        if request.model not in ["qwen-plus", "deepseek-v3"]:
            raise ApiError(
                message="不支持的模型",
                detail=f"model必须是 qwen-plus 或 deepseek-v3"
            )
        
        # 调用对应的服务
        if request.model == "qwen-plus":
            # 使用通义千问
            if request.language == "zh":
                optimized = llm_service.generate_image_prompts(request.prompt)
                optimized_prompt = optimized[0] if optimized else request.prompt
            else:
                # 英文提示词
                optimized_prompt = llm_service.optimise_video_prompt(request.prompt)
        
        else:  # deepseek-v3
            # 使用DeepSeek
            optimized_prompt = await deepseek_service.optimize_prompt(request.prompt)
        
        logger.info(f"提示词优化成功: {optimized_prompt[:100]}...")
        
        return PromptOptimizeResponse(
            original_prompt=request.prompt,
            optimized_prompt=optimized_prompt,
            model=request.model
        )
    
    except ApiError as e:
        logger.error(f"优化提示词失败: {e.message}")
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
    "/generate",
    response_model=TextToImageResponse,
    summary="文本生成图片",
    description="根据提示词生成图片，支持多种模型和参考图功能"
)
async def generate_image(request: TextToImageRequest) -> TextToImageResponse:
    """文本生成图片API.
    
    Args:
        request: 文生图请求
    
    Returns:
        包含生成图片URL的响应
    
    Raises:
        HTTPException: 当生成失败时抛出
    """
    try:
        logger.info(
            f"收到文生图请求: model={request.model}, "
            f"prompt={request.prompt[:50]}..., num={request.num_images}"
        )
        
        # 验证模型
        if request.model not in settings.text_to_image_models:
            raise ApiError(
                message="不支持的模型",
                detail=f"model必须是: {', '.join(settings.text_to_image_models.keys())}"
            )
        
        # 验证参考图功能
        if request.reference_image_urls:
            model_info = settings.text_to_image_models[request.model]
            if not model_info.get("supports_reference"):
                raise ApiError(
                    message="该模型不支持参考图功能",
                    detail=f"{request.model} 不支持reference_image_urls参数"
                )
            
            max_refs = model_info.get("max_reference_images", 1)
            if len(request.reference_image_urls) > max_refs:
                raise ApiError(
                    message="参考图数量超过限制",
                    detail=f"{request.model} 最多支持 {max_refs} 张参考图"
                )
        
        # 根据模型调用对应的服务
        image_urls: List[str] = []
        
        if request.model == "volc-jimeng":
            # 火山引擎即梦4.0（支持最多6张参考图）
            image_urls = await volc_jimeng_service.generate_image(
                prompt=request.prompt,
                size=request.size,
                num_images=request.num_images,
                reference_image_urls=request.reference_image_urls  # 直接传递URL列表
            )
        
        elif request.model == "aliyun-wanx-i2i":
            # 通义万相多图生图（支持最多2张参考图）
            image_urls = await wanx_i2i_service.generate_image(
                prompt=request.prompt,
                reference_image_urls=request.reference_image_urls,
                size=request.size,
                num_images=request.num_images
            )
        
        elif request.model == "aliyun-qwen-image":
            # 通义千问文生图（纯文本，不支持参考图）
            result = await qwen_image_service.generate_image(
                prompt=request.prompt,
                size=request.size or "1328*1328",
                prompt_extend=True,
                watermark=False
            )
            # 返回格式统一为列表
            image_urls = [result["image_url"]]
        
        else:
            raise ApiError(
                message="未实现的模型",
                detail=f"{request.model} 尚未实现"
            )
        
        if not image_urls:
            raise ApiError(
                message="生成图片失败",
                detail="未返回图片URL"
            )
        
        logger.info(f"文生图成功: 生成 {len(image_urls)} 张图片")
        
        return TextToImageResponse(
            image_urls=image_urls,
            model=request.model,
            num_images=len(image_urls)
        )
    
    except ApiError as e:
        logger.error(f"文生图失败: {e.message}")
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
    "/upload-reference",
    summary="上传参考图",
    description="上传参考图片，返回图片URL（用于多图生图）"
)
async def upload_reference_image(file: UploadFile = File(...)) -> Dict[str, str]:
    """上传参考图API.
    
    Args:
        file: 上传的图片文件
    
    Returns:
        包含图片URL的字典
    
    Raises:
        HTTPException: 当上传失败时抛出
    """
    try:
        logger.info(f"收到图片上传请求: {file.filename}")
        
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ApiError(
                message="无效的文件类型",
                detail="仅支持图片文件"
            )
        
        # TODO: 实现图片上传到OSS/CDN的逻辑
        # 这里暂时返回示例URL
        # 实际应该上传到阿里云OSS或其他存储服务
        
        raise HTTPException(
            status_code=501,
            detail={
                "message": "功能未实现",
                "detail": "图片上传功能需要配置OSS服务"
            }
        )
    
    except ApiError as e:
        logger.error(f"上传图片失败: {e.message}")
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


@router.get(
    "/health",
    summary="健康检查",
    description="检查文生图服务是否正常运行"
)
async def health_check() -> Dict[str, Any]:
    """健康检查API.
    
    Returns:
        服务健康状态
    """
    logger.info("执行健康检查")
    
    health_status = {
        "status": "healthy",
        "services": {
            "volc_jimeng": "unknown",
            "deepseek": "unknown",
            "wanx": "unknown",
            "wanx_i2i": "unknown"
        }
    }
    
    # 检查各个服务（快速检查，不实际调用API）
    try:
        # 简单检查配置是否存在
        health_status["services"]["volc_jimeng"] = (
            "healthy" if volc_jimeng_service.access_key_id else "unhealthy"
        )
        health_status["services"]["deepseek"] = (
            "healthy" if deepseek_service.api_key else "unhealthy"
        )
        health_status["services"]["wanx"] = (
            "healthy" if wanx_service.api_key else "unhealthy"
        )
        health_status["services"]["wanx_i2i"] = (
            "healthy" if wanx_i2i_service.api_key else "unhealthy"
        )
    except Exception as e:
        logger.error(f"健康检查异常: {e}")
        health_status["status"] = "unhealthy"
    
    return health_status

