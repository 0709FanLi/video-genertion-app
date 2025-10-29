"""认证服务.

处理用户注册、登录等业务逻辑。
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token
from app.utils.auth import AuthUtils
from app.exceptions.custom_exceptions import ApiError


class AuthService:
    """认证服务类."""
    
    def __init__(self, db: Session):
        """初始化认证服务.
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def register(self, user_data: UserRegister) -> User:
        """用户注册.
        
        Args:
            user_data: 用户注册数据
            
        Returns:
            创建的用户对象
            
        Raises:
            ApiError: 用户名已存在
        """
        # 检查用户名是否存在
        existing_user = self.db.query(User).filter(
            User.username == user_data.username
        ).first()
        
        if existing_user:
            raise ApiError("用户名已存在", detail=f"用户名 '{user_data.username}' 已被注册")
        
        # 哈希密码
        hashed_password = AuthUtils.hash_password(user_data.password)
        
        # 创建用户
        new_user = User(
            username=user_data.username,
            password=hashed_password
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return new_user
    
    def login(self, login_data: UserLogin) -> Token:
        """用户登录.
        
        Args:
            login_data: 登录数据
            
        Returns:
            JWT Token
            
        Raises:
            ApiError: 用户名或密码错误
        """
        # 查找用户
        user = self.db.query(User).filter(
            User.username == login_data.username
        ).first()
        
        if not user:
            raise ApiError("登录失败", detail="用户名或密码错误")
        
        # 验证密码
        if not AuthUtils.verify_password(login_data.password, user.password):
            raise ApiError("登录失败", detail="用户名或密码错误")
        
        # 检查用户是否被禁用
        if not user.is_active:
            raise ApiError("登录失败", detail="该账号已被禁用")
        
        # 更新最后登录时间
        user.update_last_login()
        self.db.commit()
        
        # 生成JWT Token
        access_token = AuthUtils.create_access_token(
            username=user.username,
            user_id=user.id
        )
        
        return Token(access_token=access_token)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户.
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象，不存在返回None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户.
        
        Args:
            username: 用户名
            
        Returns:
            用户对象，不存在返回None
        """
        return self.db.query(User).filter(User.username == username).first()

