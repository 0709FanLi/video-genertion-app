"""图生视频API路由.

提供图生视频和图片智能分析的API接口。
"""

import base64
import io
from typing import Optional, Dict, Any, Tuple

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.logging import LoggerMixin
from app.api.deps_auth import get_current_user
from app.models.user import User
from app.database.session import get_db
from app.exceptions.custom_exceptions import ApiError
from app.services.library_service import LibraryService
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
from app.services.google_veo_service import google_veo_service
from app.services.sora_service import sora_service
from app.services.oss_service import oss_service

router = APIRouter()
logger = LoggerMixin().logger


def base64_to_oss_url(base64_data: Optional[str]) -> Optional[str]:
    """将Base64图片上传到OSS并返回URL.
    
    Args:
        base64_data: Base64编码的图片数据 (格式: data:image/{type};base64,{data})
        
    Returns:
        OSS图片URL，如果输入为None则返回None
        
    Raises:
        ApiError: OSS服务未配置或其他OSS相关错误
        HTTPException: 其他错误
    """
    if not base64_data:
        return None
    
    try:
        # 解析Base64数据
        # 支持格式：data:image/{type};base64,{data} 或 data:application/octet-stream;base64,{data}
        if not (base64_data.startswith("data:image/") or base64_data.startswith("data:application/octet-stream")):
            raise ValueError("Invalid Base64 format")
        
        # 提取MIME类型和Base64数据
        header, encoded = base64_data.split(",", 1)
        mime_type_str = header.split(":")[1].split(";")[0]  # e.g., "image/jpeg" 或 "application/octet-stream"
        
        # 如果MIME类型是 application/octet-stream，尝试从Base64数据推断类型
        if mime_type_str == "application/octet-stream":
            # 尝试从Base64数据推断图片类型（JPEG通常以 /9j/ 开头，PNG以 iVBORw0KGgo 开头）
            if encoded.startswith("/9j/"):
                mime_type = "image/jpeg"
                image_ext = "jpeg"
            elif encoded.startswith("iVBORw0KGgo"):
                mime_type = "image/png"
                image_ext = "png"
            else:
                # 默认使用jpeg
                mime_type = "image/jpeg"
                image_ext = "jpeg"
        else:
            mime_type = mime_type_str
            image_ext = mime_type.split("/")[1]  # e.g., "jpeg"
        
        # 解码Base64
        image_data = base64.b64decode(encoded)
        image_file = io.BytesIO(image_data)
        
        # 生成文件名
        import uuid
        from datetime import datetime
        filename = f"video_frames/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4().hex}.{image_ext}"
        
        # 上传到OSS
        # 注意：这里会抛出 ApiError 如果OSS未配置
        oss_result = oss_service.upload_file(image_file, filename, "images", mime_type)
        logger.info(f"Base64图片已上传到OSS: {oss_result}")
        
        # 提取URL字符串
        if isinstance(oss_result, dict):
            oss_url = oss_result.get('url')
        else:
            oss_url = str(oss_result)
        
        return oss_url
        
    except ApiError as e:
        # OSS服务错误（包括未配置），直接重新抛出以便上层识别
        logger.error(f"Base64转OSS URL失败: {e.message}, 详情: {e.detail}")
        raise
    except Exception as e:
        # 其他错误转换为HTTPException
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
    request: ImageToVideoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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
        
        # 将Base64图片或URL转换为OSS URL（如果需要）
        # 如果是URL格式，直接使用；如果是Base64格式，尝试上传到OSS
        # 注意：Google Veo模型可以直接使用Base64格式，不需要OSS转换
        is_google_veo = request.model in [
            VideoModel.GOOGLE_VEO_T2V, 
            VideoModel.GOOGLE_VEO_I2V_FIRST, 
            VideoModel.GOOGLE_VEO_I2V_FIRST_TAIL
        ]
        
        if request.first_frame_base64:
            if request.first_frame_base64.startswith("http://") or request.first_frame_base64.startswith("https://"):
                first_frame_url = request.first_frame_base64  # 直接使用URL
            elif is_google_veo:
                # Google Veo模型可以直接使用Base64，不需要OSS转换
                first_frame_url = request.first_frame_base64
            else:
                # 其他模型需要Base64格式上传到OSS，如果OSS未配置则抛出错误
                try:
                    first_frame_url = base64_to_oss_url(request.first_frame_base64)  # Base64转OSS
                except ApiError as e:
                    # 检查是否是OSS未配置的错误
                    if "OSS服务未配置" in e.message or "OSS" in e.message:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "message": "OSS服务未配置",
                                "detail": "Base64格式的图片需要OSS服务支持。请配置OSS或使用图片URL格式。"
                            }
                        )
                    # 其他ApiError也需要转换为HTTPException
                    raise HTTPException(
                        status_code=e.status_code,
                        detail={
                            "message": e.message,
                            "detail": str(e.detail) if e.detail else None
                        }
                    )
                except HTTPException:
                    # HTTPException直接重新抛出
                    raise
        else:
            first_frame_url = None
            
        if request.last_frame_base64:
            if request.last_frame_base64.startswith("http://") or request.last_frame_base64.startswith("https://"):
                last_frame_url = request.last_frame_base64  # 直接使用URL
            elif is_google_veo:
                # Google Veo模型可以直接使用Base64，不需要OSS转换
                last_frame_url = request.last_frame_base64
            else:
                # 其他模型需要Base64格式上传到OSS，如果OSS未配置则抛出错误
                try:
                    last_frame_url = base64_to_oss_url(request.last_frame_base64)  # Base64转OSS
                except ApiError as e:
                    # 检查是否是OSS未配置的错误
                    if "OSS服务未配置" in e.message or "OSS" in e.message:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "message": "OSS服务未配置",
                                "detail": "Base64格式的图片需要OSS服务支持。请配置OSS或使用图片URL格式。"
                            }
                        )
                    # 其他ApiError也需要转换为HTTPException
                    raise HTTPException(
                        status_code=e.status_code,
                        detail={
                            "message": e.message,
                            "detail": str(e.detail) if e.detail else None
                        }
                    )
                except HTTPException:
                    # HTTPException直接重新抛出
                    raise
        else:
            last_frame_url = None
        
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
        
        elif request.model in [VideoModel.GOOGLE_VEO_T2V, VideoModel.GOOGLE_VEO_I2V_FIRST, VideoModel.GOOGLE_VEO_I2V_FIRST_TAIL]:
            # Google Veo 3.1
            result, google_file_id = await _generate_google_veo_video(request)
        
        elif request.model in [VideoModel.SORA_V2_PORTRAIT, VideoModel.SORA_V2_LANDSCAPE, 
                                VideoModel.SORA_V2_PORTRAIT_15S, VideoModel.SORA_V2_LANDSCAPE_15S]:
            # Sora 2 API
            result = await _generate_sora_video(request, first_frame_url)
            google_file_id = None
        
        else:
            raise ValueError(f"不支持的模型: {request.model}")
        
        logger.info(f"视频生成完成: video_url={result.video_url}")
        
        # 保存生成的视频到用户视频库
        library_service = LibraryService(db)
        
        # 判断是否为Google Veo模型
        is_google_veo = 'google-veo' in request.model.value.lower()
        
        # 确定generation_type
        if request.last_frame_base64:
            generation_type = "image_to_video_first_tail"
        elif request.first_frame_base64:
            generation_type = "image_to_video_first"
        else:
            generation_type = "text_to_video"
        
        # 对于非 Google Veo 模型，google_file_id 为 None
        if not is_google_veo:
            google_file_id = None
        
        library_service.save_video(
            user_id=current_user.id,
            video_url=result.video_url,
            model=request.model.value,
            prompt=request.prompt,
            is_google_veo=is_google_veo,
            duration=result.duration,
            resolution=request.resolution.value if request.resolution else None,
            aspect_ratio=request.aspect_ratio,
            generation_type=generation_type,
            google_file_id=google_file_id
        )
        
        return result
        
    except ApiError as e:
        logger.error(f"视频生成失败: {e.message}, 详情: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "message": e.message,
                "detail": str(e.detail) if e.detail else None
            }
        )
    except Exception as e:
        logger.error(f"视频生成失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "视频生成失败",
                "detail": str(e)
            }
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
            duration=request.duration,
            aspect_ratio=request.aspect_ratio or "16:9"
        )
    
    elif request.model == VideoModel.VOLC_I2V_FIRST:
        # 单图首帧模式
        if not first_frame_url:
            raise ValueError("单图首帧模式需要提供first_frame_url")
        
        result = await volc_video_service.generate_image_to_video_first(
            image_url=first_frame_url,
            prompt=request.prompt,
            duration=request.duration
        )
    
    elif request.model == VideoModel.VOLC_I2V_FIRST_TAIL:
        # 首尾帧模式
        if not first_frame_url or not last_frame_url:
            raise ValueError("首尾帧模式需要提供first_frame_url和last_frame_url")
        
        result = await volc_video_service.generate_image_to_video_first_tail(
            first_image_url=first_frame_url,
            last_image_url=last_frame_url,
            prompt=request.prompt,
            duration=request.duration
        )
    
    else:
        raise ValueError(f"不支持的火山引擎模型: {request.model}")
    
    # 构建响应
    return ImageToVideoResponse(
        video_url=result.get("video_url", ""),
        task_id="",  # 火山引擎不返回task_id
        model=request.model.value,
        duration=request.duration,
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


async def _generate_google_veo_video(
    request: ImageToVideoRequest
) -> Tuple[ImageToVideoResponse, Optional[str]]:
    """使用Google Veo 3.1生成视频.
    
    Args:
        request: 视频生成请求
        
    Returns:
        元组：(视频生成结果, google_file_id)
        
    Raises:
        ValueError: 参数验证失败
    """
    # 根据模型类型调用不同的方法
    raw_result: Dict[str, Any] = {}
    
    if request.model == VideoModel.GOOGLE_VEO_T2V:
        # 文生视频模式（纯文本，无图片）
        raw_result = await google_veo_service.generate_text_to_video(
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution.value.lower(),  # "720P" -> "720p"
            aspect_ratio=request.aspect_ratio or "16:9",
            negative_prompt=None
        )
    
    elif request.model == VideoModel.GOOGLE_VEO_I2V_FIRST:
        # 单图首帧模式
        if not request.first_frame_base64:
            raise ValueError("Google Veo单图首帧模式需要提供first_frame_base64")
        
        # Google Veo需要Base64格式，如果是URL需要先下载并转换为Base64
        image_base64 = request.first_frame_base64
        if image_base64.startswith("http://") or image_base64.startswith("https://"):
            # 如果是URL，需要下载并转换为Base64
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(image_base64)
                response.raise_for_status()
                import base64
                image_base64 = f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
        
        raw_result = await google_veo_service.generate_image_to_video_first(
            image_base64=image_base64,
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution.value.lower(),  # "720P" -> "720p"
            aspect_ratio=request.aspect_ratio or "16:9",
            negative_prompt=None
        )
    
    elif request.model == VideoModel.GOOGLE_VEO_I2V_FIRST_TAIL:
        # 首尾帧插值模式
        if not request.first_frame_base64 or not request.last_frame_base64:
            raise ValueError("Google Veo首尾帧模式需要提供first_frame_base64和last_frame_base64")
        
        # Google Veo需要Base64格式，如果是URL需要先下载并转换为Base64
        first_image_base64 = request.first_frame_base64
        last_image_base64 = request.last_frame_base64
        
        if first_image_base64.startswith("http://") or first_image_base64.startswith("https://"):
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(first_image_base64)
                response.raise_for_status()
                import base64
                first_image_base64 = f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
        
        if last_image_base64.startswith("http://") or last_image_base64.startswith("https://"):
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(last_image_base64)
                response.raise_for_status()
                import base64
                last_image_base64 = f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
        
        raw_result = await google_veo_service.generate_image_to_video_first_tail(
            first_image_base64=first_image_base64,
            last_image_base64=last_image_base64,
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution.value.lower(),  # "720P" -> "720p"
            aspect_ratio=request.aspect_ratio or "16:9",
            negative_prompt=None
        )
    
    else:
        raise ValueError(f"不支持的Google Veo模型: {request.model}")
    
    # 提取 google_file_id
    google_file_id = raw_result.get("google_file_id") if isinstance(raw_result, dict) else None
    
    # 构建响应
    response = ImageToVideoResponse(
        video_url=raw_result.get("video_url", ""),
        task_id="",  # Google Veo不返回task_id
        model=request.model.value,
        duration=raw_result.get("duration", request.duration),
        orig_prompt=request.prompt,
        actual_prompt=None
    )
    
    return response, google_file_id


async def _generate_sora_video(
    request: ImageToVideoRequest,
    first_frame_url: Optional[str]
) -> ImageToVideoResponse:
    """使用 Sora 2 API 生成视频.
    
    Args:
        request: 视频生成请求
        first_frame_url: 首帧图片URL（文生视频时为None）
        
    Returns:
        视频生成结果
        
    Raises:
        ValueError: 参数验证失败
    """
    # 映射模型名（前端枚举值 -> Sora API模型名）
    model_mapping = {
        VideoModel.SORA_V2_PORTRAIT: "sora_video2",
        VideoModel.SORA_V2_LANDSCAPE: "sora_video2-landscape",
        VideoModel.SORA_V2_PORTRAIT_15S: "sora_video2-15s",
        VideoModel.SORA_V2_LANDSCAPE_15S: "sora_video2-landscape-15s",
    }
    
    sora_model = model_mapping.get(request.model)
    if not sora_model:
        raise ValueError(f"不支持的 Sora 模型: {request.model}")
    
    # 确定时长（从模型名推断）
    duration = 15 if "15s" in sora_model else 10
    
    # 调用服务
    if first_frame_url:
        # 图生视频
        result = await sora_service.generate_image_to_video(
            image_url=first_frame_url,
            prompt=request.prompt,
            model=sora_model,
            duration=duration
        )
    else:
        # 文生视频
        result = await sora_service.generate_text_to_video(
            prompt=request.prompt,
            model=sora_model,
            duration=duration
        )
    
    return ImageToVideoResponse(
        video_url=result["video_url"],
        task_id="",  # Sora API不返回task_id
        model=request.model.value,
        duration=duration,
        orig_prompt=request.prompt,
        actual_prompt=request.prompt  # Sora 不修改提示词
    )
