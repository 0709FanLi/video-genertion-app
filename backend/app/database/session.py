"""数据库会话管理.

配置SQLAlchemy引擎、会话和Base类。
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 连接池预ping，检测连接是否有效
    pool_recycle=3600,   # 连接回收时间（秒）
    echo=False,          # 不打印SQL语句（生产环境）
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建Base类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话.
    
    使用FastAPI的依赖注入系统，确保每个请求都有独立的数据库会话，
    并在请求结束后自动关闭会话。
    
    Yields:
        Session: 数据库会话对象
        
    Example:
        ```python
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库.
    
    创建所有表结构。应在应用启动时调用一次。
    注意：这会自动导入所有模型并创建表。
    """
    # 导入所有模型，确保Base.metadata知道所有表
    from app.models import User, PromptHistory, UserImage, UserVideo
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")

