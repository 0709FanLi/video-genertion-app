"""通义千问视觉理解服务.

封装与通义千问视觉理解模型的交互逻辑，用于图片分析和描述生成。
"""

from typing import Any

import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import ApiError
from app.utils.retry_decorator import retry_decorator


class QwenVLService(LoggerMixin):
    """通义千问视觉理解服务类.
    
    使用qwen3-vl-plus模型进行图片分析，生成视频化的描述提示词。
    
    Attributes:
        client: OpenAI兼容的异步客户端
        model: 模型名称
    """
    
    def __init__(self) -> None:
        """初始化通义千问VL服务."""
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen3-vl-plus"
        self.logger.info("QwenVLService初始化完成")
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def analyze_image_for_video(
        self,
        image_url: str,
        enable_thinking: bool = True
    ) -> str:
        """分析图片并生成适合视频生成的描述.
        
        使用视觉理解模型分析图片内容，生成详细的、适合视频动态化的描述文本。
        
        Args:
            image_url: 图片URL（支持公网URL或Base64）
            enable_thinking: 是否开启思考模式（默认开启）
            
        Returns:
            生成的视频描述提示词（中文）
            
        Raises:
            ApiError: API调用失败
        """
        self.logger.info(f"开始分析图片: enable_thinking={enable_thinking}")
        
        # 构建提示词，引导模型生成适合视频的描述
        prompt = """请详细分析这张图片，并生成一段适合用于视频生成的描述文本。
        
要求：
1. 详细描述图片中的主体、场景、氛围
2. 描述可能的动态变化（如运动轨迹、镜头移动、光影变化）
3. 使用生动的语言，突出视觉细节
4. 长度控制在200字以内
5. 必须使用中文回复

示例格式：
"一只胖乎乎的橘猫正安静地躺在金色的沙滩上熟睡，阳光柔和地洒在它身上，白色的肚皮随着呼吸微微起伏，周围是细腻的沙粒和零星的贝壳，背景是波光粼粼的蔚蓝大海，海浪轻轻拍岸，画面采用写实风格，光线温暖自然，构图以猫咪为中心，低角度拍摄突出其可爱的姿态与环境的和谐。"

现在请分析这张图片："""
        
        try:
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # 根据是否使用思考模式选择调用方式
            if enable_thinking:
                # 使用流式输出（思考模式）
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    extra_body={
                        "enable_thinking": True,
                        "thinking_budget": 500
                    }
                )
                
                # 收集回复内容
                answer_content = ""
                is_answering = False
                
                async for chunk in completion:
                    if not chunk.choices:
                        continue
                    
                    delta = chunk.choices[0].delta
                    
                    # 跳过思考过程，只收集最终回复
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        continue
                    
                    # 开始收集回复内容
                    if delta.content:
                        if not is_answering:
                            is_answering = True
                        answer_content += delta.content
                
                result = answer_content.strip()
            
            else:
                # 不使用思考模式（直接回复）
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False
                )
                
                result = completion.choices[0].message.content.strip()
            
            if not result:
                raise ApiError("视觉模型返回空内容")
            
            self.logger.info(f"图片分析完成，生成描述长度: {len(result)}")
            return result
            
        except Exception as e:
            self.logger.error(f"图片分析失败: {str(e)}")
            raise ApiError(f"图片分析失败: {str(e)}")


# 全局服务实例
qwen_vl_service = QwenVLService()

