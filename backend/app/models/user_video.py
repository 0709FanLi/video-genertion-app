"""用户视频库模型.

存储用户生成的视频记录。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base


class UserVideo(Base):
    """用户视频库表模型.
    
    存储用户通过视频生成功能创建的视频。
    
    Attributes:
        id: 视频ID（主键）
        user_id: 用户ID（外键）
        video_url: OSS视频URL
        thumbnail_url: 缩略图URL
        prompt: 生成提示词
        model: 使用的模型
        is_google_veo: 是否为Google Veo生成（重要：视频延长时筛选）
        duration: 时长（秒）
        resolution: 分辨率
        aspect_ratio: 长宽比
        generation_type: 生成类型
        first_frame_image_id: 首帧图片ID（外键）
        last_frame_image_id: 尾帧图片ID（外键）
        source_video_id: 源视频ID（视频延长时使用）
        file_size: 文件大小（字节）
        created_at: 创建时间
    """
    
    __tablename__ = "user_videos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    prompt = Column(Text, nullable=True)
    model = Column(String(50), nullable=False)
    
    # 🆕 Google Veo 标记（用于视频延长筛选）
    is_google_veo = Column(Boolean, default=False, nullable=False, index=True)
    
    duration = Column(Integer, nullable=True)  # 秒
    resolution = Column(String(20), nullable=True)  # 如：1080P
    aspect_ratio = Column(String(10), nullable=True)  # 如：16:9
    generation_type = Column(String(50), nullable=True)  # text_to_video/image_to_video_first/video_extension
    
    # 关联字段
    first_frame_image_id = Column(Integer, ForeignKey("user_images.id"), nullable=True)
    last_frame_image_id = Column(Integer, ForeignKey("user_images.id"), nullable=True)
    source_video_id = Column(Integer, ForeignKey("user_videos.id"), nullable=True)
    
    file_size = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关联关系
    user = relationship("User", back_populates="videos")
    first_frame_image = relationship("UserImage", foreign_keys=[first_frame_image_id])
    last_frame_image = relationship("UserImage", foreign_keys=[last_frame_image_id])
    source_video = relationship("UserVideo", remote_side=[id], foreign_keys=[source_video_id])
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<UserVideo(id={self.id}, user_id={self.user_id}, model='{self.model}', is_google_veo={self.is_google_veo})>"

