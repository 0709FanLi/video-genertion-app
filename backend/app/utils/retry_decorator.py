"""重试装饰器工具.

提供可配置的重试装饰器，支持全局开关控制。
"""

from functools import wraps
from typing import Callable, Any

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential
)

from app.core.config import settings


def retry_decorator(
    max_attempts: int = None,
    wait_multiplier: float = 1,
    wait_min: float = 2,
    wait_max: float = 10
) -> Callable:
    """可配置的重试装饰器.
    
    根据全局配置决定是否启用重试功能。
    如果 `settings.enable_retry` 为 False，则返回空装饰器（不重试）。
    如果为 True，则返回带重试逻辑的装饰器。
    
    注意：配额错误的检测和跳过重试逻辑已在各个服务的异常处理中实现。
    
    Args:
        max_attempts: 最大重试次数，默认使用配置中的值
        wait_multiplier: 等待时间倍数
        wait_min: 最小等待时间（秒）
        wait_max: 最大等待时间（秒）
        
    Returns:
        装饰器函数
    """
    max_attempts = max_attempts or settings.max_retry_attempts
    
    def decorator(func: Callable) -> Callable:
        if not settings.enable_retry:
            # 如果禁用重试，返回原函数（不包装）
            return func
        
        # 如果启用重试，使用基础的 tenacity 装饰器
        # 配额错误的检测在函数内部异常处理中完成
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=wait_multiplier, min=wait_min, max=wait_max),
            reraise=True
        )(func)
    
    return decorator


# 便捷函数：直接使用默认配置
def api_retry(func: Callable) -> Callable:
    """使用默认配置的 API 重试装饰器.
    
    用法：
        @api_retry
        async def my_api_call():
            ...
    """
    return retry_decorator()(func)

