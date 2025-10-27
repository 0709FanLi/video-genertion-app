"""依赖注入模块.

定义FastAPI依赖项，实现服务的依赖注入。
"""

from typing import Annotated

from fastapi import Depends

from app.services import LLMService, WanxService


def get_llm_service() -> LLMService:
    """获取LLM服务实例.
    
    Returns:
        LLMService实例
    """
    return LLMService()


def get_wanx_service() -> WanxService:
    """获取Wanx服务实例.
    
    Returns:
        WanxService实例
    """
    return WanxService()


# 类型别名，简化注解
LLMServiceDep = Annotated[LLMService, Depends(get_llm_service)]
WanxServiceDep = Annotated[WanxService, Depends(get_wanx_service)]

