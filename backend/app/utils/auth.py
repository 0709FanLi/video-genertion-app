"""认证工具类.

提供密码哈希、JWT Token生成和验证等功能。
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.auth import TokenData


class AuthUtils:
    """认证工具类."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希加密.
        
        使用PBKDF2-SHA256算法，避免bcrypt兼容性问题。
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码（格式：salt$hash）
        """
        # 生成随机salt
        salt = secrets.token_hex(16)
        
        # 使用PBKDF2进行哈希
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        )
        
        # 返回 salt$hash 格式
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码.
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码（格式：salt$hash）
            
        Returns:
            密码是否匹配
        """
        try:
            # 分离salt和hash
            salt, stored_hash = hashed_password.split('$')
            
            # 使用相同的salt对输入密码进行哈希
            pwd_hash = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            # 比较哈希值
            return pwd_hash.hex() == stored_hash
        except Exception:
            return False
    
    @staticmethod
    def create_access_token(
        username: str,
        user_id: int,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建JWT访问令牌.
        
        Args:
            username: 用户名
            user_id: 用户ID
            expires_delta: 过期时间增量
            
        Returns:
            JWT Token字符串
        """
        # 准备数据
        to_encode = {
            "sub": username,
            "user_id": user_id
        }
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
        
        to_encode.update({"exp": expire})
        
        # 生成JWT
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[TokenData]:
        """解码JWT访问令牌.
        
        Args:
            token: JWT Token字符串
            
        Returns:
            解码后的Token数据，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if username is None or user_id is None:
                return None
            
            return TokenData(username=username, user_id=user_id)
        
        except JWTError:
            return None

