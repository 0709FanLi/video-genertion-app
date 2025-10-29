"""认证相关的数据模型.

定义注册、登录等请求和响应的数据结构。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class UserRegister(BaseModel):
    """用户注册请求.
    
    Attributes:
        username: 用户名（3-20个字符）
        password: 密码（6-20个字符）
    """
    
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    
    @validator('username')
    def username_alphanumeric(cls, v: str) -> str:
        """验证用户名只包含字母、数字和下划线."""
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserLogin(BaseModel):
    """用户登录请求.
    
    Attributes:
        username: 用户名
        password: 密码
    """
    
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """JWT Token响应.
    
    Attributes:
        access_token: JWT访问令牌
        token_type: Token类型（默认bearer）
    """
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token解析后的数据.
    
    Attributes:
        username: 用户名
        user_id: 用户ID
    """
    
    username: Optional[str] = None
    user_id: Optional[int] = None


class UserInfo(BaseModel):
    """用户信息响应.
    
    Attributes:
        id: 用户ID
        username: 用户名
        created_at: 注册时间
        last_login_at: 最后登录时间
        is_active: 是否启用
    """
    
    id: int
    username: str
    created_at: datetime
    last_login_at: Optional[datetime]
    is_active: bool
    
    class Config:
        """Pydantic配置."""
        from_attributes = True  # SQLAlchemy模型转换

