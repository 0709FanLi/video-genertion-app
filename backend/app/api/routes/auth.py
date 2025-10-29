"""认证相关的API路由.

提供用户注册、登录、获取当前用户信息等接口。
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token, UserInfo
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=UserInfo,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="使用用户名和密码注册新用户"
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> UserInfo:
    """用户注册接口.
    
    Args:
        user_data: 用户注册数据（用户名+密码）
        db: 数据库会话
        
    Returns:
        新创建的用户信息
        
    Raises:
        ApiError: 用户名已存在
    """
    auth_service = AuthService(db)
    user = auth_service.register(user_data)
    
    return UserInfo.from_orm(user)


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名和密码登录，返回JWT Token"
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """用户登录接口.
    
    Args:
        login_data: 登录数据（用户名+密码）
        db: 数据库会话
        
    Returns:
        JWT访问令牌
        
    Raises:
        ApiError: 用户名或密码错误
    """
    auth_service = AuthService(db)
    token = auth_service.login(login_data)
    
    return token


@router.get(
    "/me",
    response_model=UserInfo,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserInfo:
    """获取当前用户信息接口.
    
    需要在请求头中携带有效的JWT Token。
    
    Args:
        current_user: 当前登录用户（通过依赖注入）
        
    Returns:
        当前用户信息
    """
    return UserInfo.from_orm(current_user)


@router.post(
    "/logout",
    summary="用户登出",
    description="用户登出（客户端需要清除Token）"
)
def logout(
    current_user: User = Depends(get_current_user)
) -> dict:
    """用户登出接口.
    
    由于JWT是无状态的，服务端不存储Token，
    所以登出只需要客户端删除本地存储的Token即可。
    此接口主要用于验证Token有效性和记录登出行为。
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        登出成功消息
    """
    return {
        "message": "登出成功",
        "username": current_user.username
    }

