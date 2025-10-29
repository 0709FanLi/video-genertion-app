"""资源库API路由.

提供用户内容库查询功能，包括提示词历史、图片库、视频库。
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.models.user import User
from app.database.session import get_db
from app.services.library_service import LibraryService
from app.core.logging import get_logger

router = APIRouter(prefix="/api/library", tags=["library"])
logger = get_logger(__name__)


# ==================== Schemas ====================

class PromptHistoryItem(BaseModel):
    """提示词历史项."""
    
    id: int = Field(..., description="记录ID")
    original_prompt: Optional[str] = Field(None, description="原始提示词")
    optimized_prompt: str = Field(..., description="优化后的提示词")
    optimization_model: Optional[str] = Field(None, description="优化模型")
    scene_type: Optional[str] = Field(None, description="使用场景")
    created_at: str = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class UserImageItem(BaseModel):
    """用户图片项."""
    
    id: int = Field(..., description="记录ID")
    image_url: str = Field(..., description="图片URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    prompt: Optional[str] = Field(None, description="生成提示词")
    model: Optional[str] = Field(None, description="使用的模型")
    resolution: Optional[str] = Field(None, description="分辨率")
    width: Optional[int] = Field(None, description="宽度")
    height: Optional[int] = Field(None, description="高度")
    generation_type: str = Field(..., description="生成类型")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    created_at: str = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class UserVideoItem(BaseModel):
    """用户视频项."""
    
    id: int = Field(..., description="记录ID")
    video_url: str = Field(..., description="视频URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    prompt: Optional[str] = Field(None, description="生成提示词")
    model: str = Field(..., description="使用的模型")
    is_google_veo: bool = Field(False, description="是否为Google Veo生成")
    duration: Optional[int] = Field(None, description="时长(秒)")
    resolution: Optional[str] = Field(None, description="分辨率")
    aspect_ratio: Optional[str] = Field(None, description="长宽比")
    generation_type: str = Field(..., description="生成类型")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    created_at: str = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class PromptsListResponse(BaseModel):
    """提示词列表响应."""
    
    prompts: List[PromptHistoryItem] = Field(..., description="提示词列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")


class ImagesListResponse(BaseModel):
    """图片列表响应."""
    
    images: List[UserImageItem] = Field(..., description="图片列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")


class VideosListResponse(BaseModel):
    """视频列表响应."""
    
    videos: List[UserVideoItem] = Field(..., description="视频列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")


# ==================== API Endpoints ====================

@router.get(
    "/prompts",
    response_model=PromptsListResponse,
    summary="获取提示词历史",
    description="获取当前用户的提示词历史记录（分页）"
)
async def get_prompts(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PromptsListResponse:
    """获取提示词历史API.
    
    Args:
        page: 页码
        limit: 每页数量
        search: 搜索关键词（可选）
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        提示词历史列表
    """
    logger.info(
        f"用户 {current_user.username} 查询提示词历史: "
        f"page={page}, limit={limit}, search={search}"
    )
    
    library_service = LibraryService(db)
    prompts, total = library_service.get_user_prompts(
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search
    )
    
    # 转换为字符串格式的created_at
    prompts_data = [
        PromptHistoryItem(
            id=p.id,
            original_prompt=p.original_prompt,
            optimized_prompt=p.optimized_prompt,
            optimization_model=p.optimization_model,
            scene_type=p.scene_type,
            created_at=p.created_at.isoformat() if p.created_at else ""
        )
        for p in prompts
    ]
    
    return PromptsListResponse(
        prompts=prompts_data,
        total=total,
        page=page,
        limit=limit
    )


@router.get(
    "/images",
    response_model=ImagesListResponse,
    summary="获取图片库",
    description="获取当前用户的图片库（分页+筛选）"
)
async def get_images(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    model: Optional[str] = Query(None, description="筛选模型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ImagesListResponse:
    """获取图片库API.
    
    Args:
        page: 页码
        limit: 每页数量
        search: 搜索关键词（可选）
        model: 筛选模型（可选）
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        图片列表
    """
    logger.info(
        f"用户 {current_user.username} 查询图片库: "
        f"page={page}, limit={limit}, search={search}, model={model}"
    )
    
    library_service = LibraryService(db)
    images, total = library_service.get_user_images(
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        model=model
    )
    
    # 转换为字符串格式的created_at
    images_data = [
        UserImageItem(
            id=img.id,
            image_url=img.image_url,
            thumbnail_url=img.thumbnail_url,
            prompt=img.prompt,
            model=img.model,
            resolution=img.resolution,
            width=img.width,
            height=img.height,
            generation_type=img.generation_type,
            file_size=img.file_size,
            created_at=img.created_at.isoformat() if img.created_at else ""
        )
        for img in images
    ]
    
    return ImagesListResponse(
        images=images_data,
        total=total,
        page=page,
        limit=limit
    )


@router.get(
    "/videos",
    response_model=VideosListResponse,
    summary="获取视频库",
    description="获取当前用户的视频库（分页+筛选+Google Veo筛选）"
)
async def get_videos(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    model: Optional[str] = Query(None, description="筛选模型"),
    google_veo_only: bool = Query(False, description="仅显示Google Veo视频"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> VideosListResponse:
    """获取视频库API.
    
    Args:
        page: 页码
        limit: 每页数量
        search: 搜索关键词（可选）
        model: 筛选模型（可选）
        google_veo_only: 仅显示Google Veo视频
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        视频列表
    """
    logger.info(
        f"用户 {current_user.username} 查询视频库: "
        f"page={page}, limit={limit}, search={search}, "
        f"model={model}, google_veo_only={google_veo_only}"
    )
    
    library_service = LibraryService(db)
    videos, total = library_service.get_user_videos(
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        model=model,
        google_veo_only=google_veo_only
    )
    
    # 转换为字符串格式的created_at
    videos_data = [
        UserVideoItem(
            id=vid.id,
            video_url=vid.video_url,
            thumbnail_url=vid.thumbnail_url,
            prompt=vid.prompt,
            model=vid.model,
            is_google_veo=vid.is_google_veo,
            duration=vid.duration,
            resolution=vid.resolution,
            aspect_ratio=vid.aspect_ratio,
            generation_type=vid.generation_type,
            file_size=vid.file_size,
            created_at=vid.created_at.isoformat() if vid.created_at else ""
        )
        for vid in videos
    ]
    
    return VideosListResponse(
        videos=videos_data,
        total=total,
        page=page,
        limit=limit
    )


@router.get(
    "/health",
    summary="健康检查",
    description="检查资源库服务是否正常"
)
async def health_check() -> dict:
    """健康检查API.
    
    Returns:
        服务健康状态
    """
    return {"status": "healthy", "service": "library"}

