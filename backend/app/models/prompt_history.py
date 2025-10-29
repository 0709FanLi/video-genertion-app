"""提示词历史模型.

存储用户的提示词优化历史记录。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base


class PromptHistory(Base):
    """提示词历史表模型.
    
    存储用户使用提示词优化功能的历史记录。
    
    Attributes:
        id: 记录ID（主键）
        user_id: 用户ID（外键）
        original_prompt: 原始提示词
        optimized_prompt: 优化后的提示词
        optimization_model: 使用的优化模型
        scene_type: 使用场景
        created_at: 创建时间
    """
    
    __tablename__ = "prompt_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_prompt = Column(Text, nullable=True)  # 可能只有优化后的
    optimized_prompt = Column(Text, nullable=False)
    optimization_model = Column(String(50), nullable=True)  # 如：deepseek-v3.2
    scene_type = Column(String(50), nullable=True)  # text_to_image/image_to_video/video_extension
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关联关系
    user = relationship("User", back_populates="prompts")
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<PromptHistory(id={self.id}, user_id={self.user_id}, model='{self.optimization_model}')>"

