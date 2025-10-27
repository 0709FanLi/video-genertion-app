"""自定义异常类定义.

定义应用中使用的所有自定义异常，便于统一错误处理。
"""

from typing import Any, Optional


class ApiError(Exception):
    """API错误基类.
    
    所有自定义API异常都应继承此类。
    
    Attributes:
        message: 错误消息
        status_code: HTTP状态码
        detail: 详细错误信息
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Any] = None
    ) -> None:
        """初始化API错误.
        
        Args:
            message: 错误消息
            status_code: HTTP状态码，默认500
            detail: 详细错误信息，可选
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class DashScopeApiError(ApiError):
    """阿里云DashScope API调用错误.
    
    当调用DashScope API失败时抛出此异常。
    """
    
    def __init__(
        self,
        message: str = "DashScope API调用失败",
        status_code: int = 502,
        detail: Optional[Any] = None
    ) -> None:
        """初始化DashScope API错误.
        
        Args:
            message: 错误消息
            status_code: HTTP状态码，默认502
            detail: API返回的详细错误信息
        """
        super().__init__(message, status_code, detail)


class TaskFailedError(ApiError):
    """异步任务失败错误.
    
    当轮询的异步任务失败时抛出此异常。
    """
    
    def __init__(
        self,
        message: str = "异步任务执行失败",
        task_id: Optional[str] = None,
        detail: Optional[Any] = None
    ) -> None:
        """初始化任务失败错误.
        
        Args:
            message: 错误消息
            task_id: 任务ID
            detail: 任务失败的详细信息
        """
        self.task_id = task_id
        super().__init__(message, status_code=500, detail=detail)


class TaskTimeoutError(ApiError):
    """任务超时错误.
    
    当异步任务轮询超时时抛出此异常。
    """
    
    def __init__(
        self,
        message: str = "任务执行超时",
        task_id: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> None:
        """初始化任务超时错误.
        
        Args:
            message: 错误消息
            task_id: 任务ID
            timeout: 超时时间（秒）
        """
        self.task_id = task_id
        self.timeout = timeout
        detail = {"task_id": task_id, "timeout": timeout}
        super().__init__(message, status_code=408, detail=detail)

