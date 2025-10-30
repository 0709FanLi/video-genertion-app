"""DeepSeek API服务.

提供提示词优化功能，使用DeepSeek-V3.2-Exp模型。
"""

from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.custom_exceptions import ApiError
from app.utils.retry_decorator import retry_decorator

logger = get_logger(__name__)


class DeepSeekService:
    """DeepSeek服务类.
    
    封装DeepSeek API调用逻辑，主要用于提示词优化。
    
    Attributes:
        api_key: DeepSeek API密钥
        base_url: API基础URL
        timeout: 请求超时时间
    """
    
    def __init__(self) -> None:
        """初始化DeepSeek服务."""
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.timeout = settings.request_timeout
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def optimize_prompt(
        self,
        user_prompt: str,
        model: str = "deepseek-chat",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> str:
        """优化提示词.
        
        Args:
            user_prompt: 用户输入的原始提示词
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            优化后的提示词
            
        Raises:
            ApiError: API调用失败
        """
        logger.info(
            f"DeepSeek优化提示词: prompt={user_prompt[:50]}..., model={model}"
        )
        
        # 构建系统提示
        system_prompt = """你是一个专业的AI图像生成提示词优化专家。你的任务是将用户的简单描述扩展为详细、富有艺术感的提示词。

重要规则:
1. **必须使用中文输出** - 优化后的提示词必须是中文
2. 保留用户的核心意图和主要元素
3. 添加艺术风格、光影、构图等细节描述
4. 使用丰富的形容词和专业术语
5. 确保提示词连贯、具体、富有画面感
6. 输出纯提示词，不要任何解释
7. 提示词长度控制在50-100个汉字

示例:
输入: 一只猫
输出: 一只毛茸茸的波斯猫，拥有明亮的蓝色眼睛，优雅地坐在天鹅绒靠垫上，黄金时段的温暖阳光投射出柔和的阴影，浅景深效果，专业宠物摄影风格，温暖色调，舒适的家居室内背景，超高清细节

现在请用中文优化用户的提示词。"""
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"请优化这个提示词: {user_prompt}"
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"DeepSeek API响应: {result}")
                
                # 提取优化后的提示词
                choices = result.get("choices", [])
                if not choices:
                    raise ApiError(
                        message="DeepSeek未返回结果",
                        detail="响应中没有choices字段"
                    )
                
                optimized_prompt = choices[0].get("message", {}).get("content", "").strip()
                
                if not optimized_prompt:
                    raise ApiError(
                        message="DeepSeek返回空提示词",
                        detail="优化后的提示词为空"
                    )
                
                logger.info(f"DeepSeek优化成功: {optimized_prompt[:100]}...")
                return optimized_prompt
                
        except httpx.HTTPError as e:
            logger.error(f"DeepSeek HTTP请求失败: {e}")
            raise ApiError(
                message="DeepSeek请求失败",
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"DeepSeek调用异常: {e}")
            raise ApiError(
                message="DeepSeek调用失败",
                detail=str(e)
            )
    
    async def chat(
        self,
        messages: list[Dict[str, str]],
        model: str = "deepseek-chat",
        **kwargs: Any
    ) -> str:
        """通用聊天接口.
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            模型回复
            
        Raises:
            ApiError: API调用失败
        """
        logger.info(f"DeepSeek聊天: model={model}, messages_count={len(messages)}")
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                result = response.json()
                
                choices = result.get("choices", [])
                if not choices:
                    raise ApiError(
                        message="DeepSeek未返回结果",
                        detail="响应中没有choices字段"
                    )
                
                reply = choices[0].get("message", {}).get("content", "").strip()
                
                logger.info(f"DeepSeek聊天成功: {reply[:100]}...")
                return reply
                
        except httpx.HTTPError as e:
            logger.error(f"DeepSeek HTTP请求失败: {e}")
            raise ApiError(
                message="DeepSeek请求失败",
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"DeepSeek调用异常: {e}")
            raise ApiError(
                message="DeepSeek调用失败",
                detail=str(e)
            )
    
    async def health_check(self) -> bool:
        """健康检查.
        
        Returns:
            服务是否可用
        """
        try:
            await self.chat([{"role": "user", "content": "hello"}])
            return True
        except Exception as e:
            logger.error(f"DeepSeek健康检查失败: {e}")
            return False


# 全局服务实例
deepseek_service = DeepSeekService()

