"""大语言模型服务.

封装与通义千问大语言模型的交互逻辑。
"""

import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import DashScopeApiError
from app.utils.retry_decorator import retry_decorator


class LLMService(LoggerMixin):
    """大语言模型服务类.
    
    负责调用通义千问API进行文本生成、提示词优化等任务。
    
    Attributes:
        client: OpenAI客户端实例
    """
    
    def __init__(self) -> None:
        """初始化LLM服务."""
        self.client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.qwen_base_url,
        )
        self.logger.info("LLMService初始化完成")
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    def _call_api(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "qwen-plus",
        response_format: dict[str, str] = {"type": "json_object"}
    ) -> str:
        """调用通义千问API.
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            model: 模型名称，默认qwen-plus
            response_format: 响应格式，默认JSON
            
        Returns:
            API返回的内容
            
        Raises:
            DashScopeApiError: API调用失败时抛出
        """
        try:
            self.logger.info(
                "调用通义千问API",
                extra={"model": model, "user_prompt_length": len(user_prompt)}
            )
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=response_format
            )
            
            content = completion.choices[0].message.content
            self.logger.info("通义千问API调用成功")
            
            return content
            
        except Exception as e:
            self.logger.error(
                f"通义千问API调用失败: {str(e)}",
                exc_info=True
            )
            raise DashScopeApiError(
                message="调用通义千问API失败",
                detail=str(e)
            )
    
    def generate_image_prompts(self, idea: str) -> list[str]:
        """生成图片提示词.
        
        根据用户的创意想法，生成3个专业的图片生成提示词。
        
        Args:
            idea: 用户的创意想法
            
        Returns:
            包含3个提示词的列表
            
        Raises:
            DashScopeApiError: API调用失败或响应解析失败
        """
        self.logger.info(f"生成图片提示词，用户想法: {idea}")
        
        system_prompt = (
            "你是一个专业的提示词工程师。"
            "请将用户的想法扩展成3个详细的、用于AI绘画的中文提示词，"
            "包含场景描述、光线、画风、构图等细节，并以JSON格式返回。"
            "重要：提示词必须使用中文，要详细且富有画面感。"
            "返回格式: {\"prompts\": [\"prompt1\", \"prompt2\", \"prompt3\"]}"
        )
        
        try:
            content = self._call_api(system_prompt, idea)
            data = json.loads(content)
            prompts = data.get("prompts", [])
            
            if not prompts or len(prompts) != 3:
                raise ValueError(f"返回的提示词数量不正确: {len(prompts)}")
            
            self.logger.info(f"成功生成{len(prompts)}个图片提示词")
            return prompts
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.error(f"解析图片提示词失败: {str(e)}")
            raise DashScopeApiError(
                message="解析图片提示词失败",
                detail=str(e)
            )
    
    def optimise_video_prompt(self, prompt: str) -> str:
        """优化视频提示词.
        
        将用户输入的视频描述优化成更专业的提示词。
        
        Args:
            prompt: 用户输入的视频描述
            
        Returns:
            优化后的提示词
            
        Raises:
            DashScopeApiError: API调用失败或响应解析失败
        """
        self.logger.info(f"优化视频提示词，原始描述: {prompt}")
        
        system_prompt = (
            "你是一个专业的视频提示词工程师。"
            "请将用户的想法优化成一个更专业的、细节丰富的中文视频动态描述提示词，"
            "并以JSON格式返回。"
            "重要：提示词必须使用中文，要详细描述动态效果。"
            "返回格式: {\"optimised_prompt\": \"优化后的提示词\"}"
        )
        
        try:
            content = self._call_api(system_prompt, prompt)
            data = json.loads(content)
            optimised_prompt = data.get("optimised_prompt", "")
            
            if not optimised_prompt:
                raise ValueError("返回的优化提示词为空")
            
            self.logger.info("视频提示词优化成功")
            return optimised_prompt
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.error(f"解析优化提示词失败: {str(e)}")
            raise DashScopeApiError(
                message="解析优化提示词失败",
                detail=str(e)
            )


# 全局服务实例
llm_service = LLMService()

