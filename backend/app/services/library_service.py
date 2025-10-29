"""内容库服务.

处理用户内容（提示词、图片、视频）的保存和查询。
"""

from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.user import User
from app.models.prompt_history import PromptHistory
from app.models.user_image import UserImage
from app.models.user_video import UserVideo
from app.core.logging import get_logger


logger = get_logger(__name__)


class LibraryService:
    """内容库服务类."""
    
    def __init__(self, db: Session):
        """初始化内容库服务.
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    # ========== 提示词历史 ==========
    
    def save_prompt(
        self,
        user_id: int,
        optimized_prompt: str,
        original_prompt: Optional[str] = None,
        optimization_model: Optional[str] = None,
        scene_type: Optional[str] = None
    ) -> PromptHistory:
        """保存提示词历史.
        
        Args:
            user_id: 用户ID
            optimized_prompt: 优化后的提示词
            original_prompt: 原始提示词（可选）
            optimization_model: 优化模型（可选）
            scene_type: 使用场景（可选）
            
        Returns:
            保存的提示词历史记录
        """
        prompt_history = PromptHistory(
            user_id=user_id,
            original_prompt=original_prompt,
            optimized_prompt=optimized_prompt,
            optimization_model=optimization_model,
            scene_type=scene_type
        )
        
        self.db.add(prompt_history)
        self.db.commit()
        self.db.refresh(prompt_history)
        
        logger.info(
            f"保存提示词历史: user_id={user_id}, "
            f"model={optimization_model}, scene={scene_type}"
        )
        
        return prompt_history
    
    # ========== 图片库 ==========
    
    def save_image(
        self,
        user_id: int,
        image_url: str,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        resolution: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        generation_type: str = "text_to_image",
        file_size: Optional[int] = None,
        thumbnail_url: Optional[str] = None
    ) -> UserImage:
        """保存图片到用户图片库.
        
        Args:
            user_id: 用户ID
            image_url: OSS图片URL
            prompt: 生成提示词
            model: 使用的模型
            resolution: 分辨率
            width: 宽度
            height: 高度
            generation_type: 生成类型
            file_size: 文件大小（字节）
            thumbnail_url: 缩略图URL
            
        Returns:
            保存的图片记录
        """
        user_image = UserImage(
            user_id=user_id,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            prompt=prompt,
            model=model,
            resolution=resolution,
            width=width,
            height=height,
            generation_type=generation_type,
            file_size=file_size
        )
        
        self.db.add(user_image)
        self.db.commit()
        self.db.refresh(user_image)
        
        logger.info(
            f"保存图片: user_id={user_id}, model={model}, "
            f"resolution={resolution}, type={generation_type}"
        )
        
        return user_image
    
    # ========== 视频库 ==========
    
    def save_video(
        self,
        user_id: int,
        video_url: str,
        model: str,
        prompt: Optional[str] = None,
        is_google_veo: bool = False,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        generation_type: str = "text_to_video",
        first_frame_image_id: Optional[int] = None,
        last_frame_image_id: Optional[int] = None,
        source_video_id: Optional[int] = None,
        file_size: Optional[int] = None,
        thumbnail_url: Optional[str] = None
    ) -> UserVideo:
        """保存视频到用户视频库.
        
        Args:
            user_id: 用户ID
            video_url: OSS视频URL
            model: 使用的模型
            prompt: 生成提示词
            is_google_veo: 是否为Google Veo生成
            duration: 时长（秒）
            resolution: 分辨率
            aspect_ratio: 长宽比
            generation_type: 生成类型
            first_frame_image_id: 首帧图片ID
            last_frame_image_id: 尾帧图片ID
            source_video_id: 源视频ID（视频延长）
            file_size: 文件大小（字节）
            thumbnail_url: 缩略图URL
            
        Returns:
            保存的视频记录
        """
        user_video = UserVideo(
            user_id=user_id,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            prompt=prompt,
            model=model,
            is_google_veo=is_google_veo,
            duration=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            generation_type=generation_type,
            first_frame_image_id=first_frame_image_id,
            last_frame_image_id=last_frame_image_id,
            source_video_id=source_video_id,
            file_size=file_size
        )
        
        self.db.add(user_video)
        self.db.commit()
        self.db.refresh(user_video)
        
        logger.info(
            f"保存视频: user_id={user_id}, model={model}, "
            f"duration={duration}s, resolution={resolution}, "
            f"is_google_veo={is_google_veo}, type={generation_type}"
        )
        
        return user_video
    
    # ========== 查询方法（为阶段3准备） ==========
    
    def get_user_prompts(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> tuple[List[PromptHistory], int]:
        """获取用户提示词历史（分页）."""
        query = self.db.query(PromptHistory).filter(
            PromptHistory.user_id == user_id
        )
        
        if search:
            query = query.filter(
                PromptHistory.optimized_prompt.contains(search) |
                PromptHistory.original_prompt.contains(search)
            )
        
        total = query.count()
        prompts = query.order_by(desc(PromptHistory.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return prompts, total
    
    def get_user_images(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        model: Optional[str] = None
    ) -> tuple[List[UserImage], int]:
        """获取用户图片库（分页）."""
        query = self.db.query(UserImage).filter(
            UserImage.user_id == user_id
        )
        
        if search:
            query = query.filter(UserImage.prompt.contains(search))
        
        if model:
            query = query.filter(UserImage.model == model)
        
        total = query.count()
        images = query.order_by(desc(UserImage.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return images, total
    
    def get_user_videos(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        model: Optional[str] = None,
        google_veo_only: bool = False
    ) -> tuple[List[UserVideo], int]:
        """获取用户视频库（分页）."""
        query = self.db.query(UserVideo).filter(
            UserVideo.user_id == user_id
        )
        
        if search:
            query = query.filter(UserVideo.prompt.contains(search))
        
        if model:
            query = query.filter(UserVideo.model == model)
        
        if google_veo_only:
            query = query.filter(UserVideo.is_google_veo == True)
        
        total = query.count()
        videos = query.order_by(desc(UserVideo.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return videos, total

