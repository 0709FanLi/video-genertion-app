"""用户图片库模型.

存储用户生成的图片记录。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base


class UserImage(Base):
    """用户图片库表模型.
    
    存储用户通过文生图等功能生成的图片。
    
    Attributes:
        id: 图片ID（主键）
        user_id: 用户ID（外键）
        image_url: OSS图片URL
        thumbnail_url: 缩略图URL（可选）
        prompt: 生成提示词
        model: 使用的模型
        resolution: 分辨率
        width: 宽度
        height: 高度
        generation_type: 生成类型
        file_size: 文件大小（字节）
        created_at: 创建时间
    """
    
    __tablename__ = "user_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    prompt = Column(Text, nullable=True)
    model = Column(String(50), nullable=True)
    resolution = Column(String(20), nullable=True)  # 如：1024x1024
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    generation_type = Column(String(50), nullable=True)  # text_to_image/reference_image
    file_size = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关联关系
    user = relationship("User", back_populates="images")
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<UserImage(id={self.id}, user_id={self.user_id}, model='{self.model}')>"

