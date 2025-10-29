"""用户模型.

定义用户表结构和相关方法。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database.session import Base


class User(Base):
    """用户表模型.
    
    存储用户基本信息和认证凭证。
    
    Attributes:
        id: 用户ID（主键）
        username: 用户名（唯一）
        password: 密码哈希值
        created_at: 注册时间
        last_login_at: 最后登录时间
        is_active: 是否启用
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # 哈希后的密码
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关联关系
    prompts = relationship("PromptHistory", back_populates="user", cascade="all, delete-orphan")
    images = relationship("UserImage", back_populates="user", cascade="all, delete-orphan")
    videos = relationship("UserVideo", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<User(id={self.id}, username='{self.username}', active={self.is_active})>"
    
    def update_last_login(self) -> None:
        """更新最后登录时间."""
        self.last_login_at = datetime.utcnow()

