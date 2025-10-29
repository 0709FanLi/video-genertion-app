"""认证相关的依赖注入.

提供获取当前用户等依赖函数，用于路由保护。
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.auth import AuthUtils


# HTTP Bearer认证方案
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户.
    
    从请求头的Authorization中提取JWT Token，验证后返回当前用户。
    用于需要登录的路由保护。
    
    Args:
        credentials: HTTP Bearer凭证
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: Token无效或用户不存在
        
    Example:
        ```python
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"username": current_user.username}
        ```
    """
    # 解码Token
    token_data = AuthUtils.decode_access_token(credentials.credentials)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该账号已被禁用",
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前登录用户（可选）.
    
    类似get_current_user，但Token不存在或无效时返回None而不抛出异常。
    用于既支持登录用户也支持匿名用户的路由。
    
    Args:
        credentials: HTTP Bearer凭证（可选）
        db: 数据库会话
        
    Returns:
        当前用户对象，未登录返回None
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

