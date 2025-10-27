"""响应数据模型定义.

使用Pydantic进行数据验证和序列化。
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class PromptGenerationResponse(BaseModel):
    """图片提示词生成响应.
    
    Attributes:
        prompts: 生成的提示词列表
    """
    
    prompts: list[str] = Field(
        ...,
        description="生成的图片提示词列表",
        examples=[["prompt1", "prompt2", "prompt3"]]
    )


class ImageResult(BaseModel):
    """单个图片结果.
    
    Attributes:
        url: 图片URL
    """
    
    url: str = Field(..., description="图片URL")


class ImageGenerationResponse(BaseModel):
    """图片生成响应.
    
    Attributes:
        output: 输出结果
    """
    
    output: dict[str, Any] = Field(
        ...,
        description="图片生成结果",
        examples=[{
            "task_id": "task-123",
            "task_status": "SUCCEEDED",
            "results": [{"url": "https://example.com/image1.jpg"}]
        }]
    )


class VideoPromptOptimiseResponse(BaseModel):
    """视频提示词优化响应.
    
    Attributes:
        optimised_prompt: 优化后的提示词
    """
    
    optimised_prompt: str = Field(
        ...,
        description="优化后的视频提示词",
        examples=["海浪轻轻拍打沙滩，泛起白色的泡沫，猫的尾巴在微风中优雅地摇摆"]
    )


class VideoGenerationResponse(BaseModel):
    """视频生成响应.
    
    Attributes:
        output: 输出结果
    """
    
    output: dict[str, Any] = Field(
        ...,
        description="视频生成结果",
        examples=[{
            "task_id": "task-456",
            "task_status": "SUCCEEDED",
            "video_url": "https://example.com/video.mp4"
        }]
    )

