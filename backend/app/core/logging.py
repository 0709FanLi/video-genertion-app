"""日志配置模块.

提供统一的日志记录功能，支持结构化日志输出。
"""

import logging
import sys
from typing import Any

from app.core.config import settings


def setup_logging() -> None:
    """配置应用日志系统.
    
    配置日志级别、格式和输出方式。
    """
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", encoding="utf-8")
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器.
    
    Args:
        name: 日志记录器名称，通常使用模块名
        
    Returns:
        配置好的日志记录器实例
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("应用启动")
    """
    return logging.getLogger(name)


class LoggerMixin:
    """日志记录器Mixin类.
    
    为类提供日志记录功能。
    
    Example:
        >>> class MyService(LoggerMixin):
        ...     def process(self):
        ...         self.logger.info("处理中...")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器."""
        return get_logger(self.__class__.__name__)

