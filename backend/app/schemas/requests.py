"""请求数据模型定义.

使用Pydantic进行数据验证和序列化。
"""

from pydantic import BaseModel, Field, HttpUrl


class PromptGenerationRequest(BaseModel):
    """图片提示词生成请求.
    
    Attributes:
        idea: 用户输入的创意想法
    """
    
    idea: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="用户的创意想法",
        examples=["一只戴墨镜的猫在沙滩上"]
    )


class ImageGenerationRequest(BaseModel):
    """图片生成请求.
    
    Attributes:
        prompt: 图片生成提示词
    """
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="图片生成提示词",
        examples=["A photorealistic image of a cat wearing sunglasses on a beach"]
    )


class VideoPromptOptimiseRequest(BaseModel):
    """视频提示词优化请求.
    
    Attributes:
        prompt: 原始视频描述提示词
    """
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="原始视频动态描述",
        examples=["海浪轻轻拍打，猫的尾巴在摇摆"]
    )


class VideoGenerationRequest(BaseModel):
    """视频生成请求.
    
    Attributes:
        image_url: 首帧图片URL
        prompt: 视频动态描述提示词
    """
    
    image_url: str = Field(
        ...,
        description="首帧图片URL",
        examples=["https://example.com/image.jpg"]
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="视频动态描述提示词",
        examples=["海浪轻轻拍打沙滩，猫的尾巴在微微摇摆"]
    )

