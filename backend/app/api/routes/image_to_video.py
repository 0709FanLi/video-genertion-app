"""图生视频API路由.

提供图生视频和图片智能分析的API接口。
"""

import base64
import io
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.core.logging import LoggerMixin
from app.schemas.image_to_video import (
    AnalyzeImageRequest,
    AnalyzeImageResponse,
    ImageToVideoRequest,
    ImageToVideoResponse,
    VideoModel
)
from app.services.qwen_vl_service import qwen_vl_service
from app.services.volc_video_service import volc_video_service
from app.services.wanx_kf2v_service import wanx_kf2v_service
from app.services.oss_service import oss_service

router = APIRouter()
logger = LoggerMixin().logger


def base64_to_oss_url(base64_data: Optional[str]) -> Optional[str]:
    """将Base64图片上传到OSS并返回URL.
    
    Args:
        base64_data: Base64编码的图片数据 (格式: data:image/{type};base64,{data})
        
    Returns:
        OSS图片URL，如果输入为None则返回None
    """
    if not base64_data:
        return None
    
    try:
        # 解析Base64数据
        if not base64_data.startswith("data:image/"):
            raise ValueError("Invalid Base64 format")
        
        # 提取MIME类型和Base64数据
        header, encoded = base64_data.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0]  # e.g., "image/jpeg"
        image_ext = mime_type.split("/")[1]  # e.g., "jpeg"
        
        # 解码Base64
        image_data = base64.b64decode(encoded)
        image_file = io.BytesIO(image_data)
        
        # 生成文件名
        import uuid
        from datetime import datetime
        filename = f"video_frames/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4().hex}.{image_ext}"
        
        # 上传到OSS
        oss_result = oss_service.upload_file(image_file, filename, mime_type)
        logger.info(f"Base64图片已上传到OSS: {oss_result}")
        
        # 提取URL字符串
        if isinstance(oss_result, dict):
            oss_url = oss_result.get('url')
        else:
            oss_url = str(oss_result)
        
        return oss_url
        
    except Exception as e:
        logger.error(f"Base64转OSS URL失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"图片处理失败: {str(e)}"
        )


@router.post("/analyze-image", response_model=AnalyzeImageResponse)
async def analyze_image(
    request: AnalyzeImageRequest
) -> AnalyzeImageResponse:
    """分析图片并生成视频描述.
    
    使用视觉理解模型分析图片内容，生成适合视频生成的描述提示词。
    
    Args:
        request: 图片分析请求
        
    Returns:
        图片分析结果
        
    Raises:
        HTTPException: 分析失败
    """
    try:
        logger.info(f"用户请求分析图片")
        
        # 调用视觉理解服务
        description = await qwen_vl_service.analyze_image_for_video(
            image_url=request.image_base64,
            enable_thinking=request.enable_thinking
        )
        
        logger.info(f"图片分析完成，描述长度: {len(description)}")
        
        return AnalyzeImageResponse(description=description)
        
    except Exception as e:
        logger.error(f"图片分析失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"图片分析失败: {str(e)}"
        )


@router.post("/generate", response_model=ImageToVideoResponse)
async def generate_video(
    request: ImageToVideoRequest
) -> ImageToVideoResponse:
    """生成视频.
    
    根据图片和提示词生成视频，支持单图首帧和首尾帧两种模式。
    
    Args:
        request: 视频生成请求
        
    Returns:
        视频生成结果
        
    Raises:
        HTTPException: 生成失败
    """
    try:
        mode = "首尾帧" if request.last_frame_base64 else ("单图首帧" if request.first_frame_base64 else "文生视频")
        logger.info(
            f"用户请求生成视频（{mode}模式）: "
            f"model={request.model}, duration={request.duration}s"
        )
        
        # 将Base64图片转换为OSS URL（如果需要）
        first_frame_url = base64_to_oss_url(request.first_frame_base64) if request.first_frame_base64 else None
        last_frame_url = base64_to_oss_url(request.last_frame_base64) if request.last_frame_base64 else None
        
        logger.info(f"图片已转换为OSS URL: first={bool(first_frame_url)}, last={bool(last_frame_url)}")
        if first_frame_url:
            logger.info(f"first_frame_url type: {type(first_frame_url)}, value: {first_frame_url[:100]}")
        
        # 根据模型选择不同的服务（直接传递URL字符串）
        if request.model in [VideoModel.VOLC_T2V, VideoModel.VOLC_I2V_FIRST, VideoModel.VOLC_I2V_FIRST_TAIL]:
            # 火山引擎即梦
            result = await _generate_volc_video(request, first_frame_url, last_frame_url)
        
        elif request.model in [VideoModel.WANX_KF2V_FLASH, VideoModel.WANX_KF2V_PLUS]:
            # 通义万相
            result = await _generate_wanx_video(request, first_frame_url, last_frame_url)
        
        else:
            raise ValueError(f"不支持的模型: {request.model}")
        
        logger.info(f"视频生成完成: video_url={result.video_url}")
        
        return result
        
    except Exception as e:
        logger.error(f"视频生成失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"视频生成失败: {str(e)}"
        )


async def _generate_volc_video(
    request: ImageToVideoRequest,
    first_frame_url: Optional[str],
    last_frame_url: Optional[str]
) -> ImageToVideoResponse:
    """使用火山引擎即梦生成视频.
    
    Args:
        request: 视频生成请求
        first_frame_url: 首帧OSS URL
        last_frame_url: 尾帧OSS URL
        
    Returns:
        视频生成结果
    """
    # 根据模式选择服务
    if request.model == VideoModel.VOLC_T2V:
        # 文生视频模式（纯文本，无需图片）
        result = await volc_video_service.generate_text_to_video(
            prompt=request.prompt,
            duration=request.duration.value,
            aspect_ratio=request.aspect_ratio or "16:9"
        )
    
    elif request.model == VideoModel.VOLC_I2V_FIRST:
        # 单图首帧模式
        if not first_frame_url:
            raise ValueError("单图首帧模式需要提供first_frame_url")
        
        result = await volc_video_service.generate_image_to_video_first(
            image_url=first_frame_url,
            prompt=request.prompt,
            duration=request.duration.value
        )
    
    elif request.model == VideoModel.VOLC_I2V_FIRST_TAIL:
        # 首尾帧模式
        if not first_frame_url or not last_frame_url:
            raise ValueError("首尾帧模式需要提供first_frame_url和last_frame_url")
        
        result = await volc_video_service.generate_image_to_video_first_tail(
            first_image_url=first_frame_url,
            last_image_url=last_frame_url,
            prompt=request.prompt,
            duration=request.duration.value
        )
    
    else:
        raise ValueError(f"不支持的火山引擎模型: {request.model}")
    
    # 构建响应
    return ImageToVideoResponse(
        video_url=result.get("video_url", ""),
        task_id="",  # 火山引擎不返回task_id
        model=request.model.value,
        duration=request.duration.value,
        orig_prompt=request.prompt,
        actual_prompt=None
    )


async def _generate_wanx_video(
    request: ImageToVideoRequest,
    first_frame_url: Optional[str],
    last_frame_url: Optional[str]
) -> ImageToVideoResponse:
    """使用通义万相生成视频.
    
    Args:
        request: 视频生成请求
        first_frame_url: 首帧OSS URL
        last_frame_url: 尾帧OSS URL
        
    Returns:
        视频生成结果
    """
    # 通义万相仅支持首尾帧模式
    # 但可以只提供首帧（单图模式）
    
    if not first_frame_url:
        raise ValueError("通义万相模型需要提供first_frame_url")
    
    # 映射模型名称
    model_mapping = {
        VideoModel.WANX_KF2V_FLASH: "wan2.2-kf2v-flash",
        VideoModel.WANX_KF2V_PLUS: "wanx2.1-kf2v-plus"
    }
    
    model_name = model_mapping.get(request.model)
    if not model_name:
        raise ValueError(f"不支持的通义万相模型: {request.model}")
    
    # 调用通义万相服务
    result = await wanx_kf2v_service.generate_video(
        first_frame_url=first_frame_url,
        prompt=request.prompt,
        last_frame_url=last_frame_url,
        model=model_name,
        resolution=request.resolution.value
    )
    
    # 构建响应
    return ImageToVideoResponse(
        video_url=result.get("video_url", ""),
        task_id=result.get("task_id", ""),
        model=request.model.value,
        duration=5,  # 通义万相固定5秒
        orig_prompt=result.get("orig_prompt", request.prompt),
        actual_prompt=result.get("actual_prompt")
    )
