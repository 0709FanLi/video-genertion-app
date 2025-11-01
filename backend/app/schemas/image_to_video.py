"""图生视频相关的数据模型.

定义图生视频功能的请求和响应数据结构。
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class VideoModel(str, Enum):
    """支持的视频生成模型."""
    
    # 火山引擎即梦模型
    VOLC_T2V = "volc-t2v"  # 文生视频（纯文本）
    VOLC_I2V_FIRST = "volc-i2v-first"  # 图生视频（首帧）
    VOLC_I2V_FIRST_TAIL = "volc-i2v-first-tail"  # 图生视频（首尾帧）
    
    # 通义万相模型
    WANX_KF2V_FLASH = "wanx-kf2v-flash"  # 万相2.2极速版
    WANX_KF2V_PLUS = "wanx-kf2v-plus"  # 万相2.1专业版
    
    # Google Veo 3.1模型
    GOOGLE_VEO_T2V = "google-veo-t2v"  # 文生视频
    GOOGLE_VEO_I2V_FIRST = "google-veo-i2v-first"  # 单图首帧
    GOOGLE_VEO_I2V_FIRST_TAIL = "google-veo-i2v-first-tail"  # 首尾帧插值
    
    # Sora 2 模型
    SORA_V2_PORTRAIT = "sora-v2-portrait"  # 竖屏 10s
    SORA_V2_LANDSCAPE = "sora-v2-landscape"  # 横屏 10s
    SORA_V2_PORTRAIT_15S = "sora-v2-portrait-15s"  # 竖屏 15s
    SORA_V2_LANDSCAPE_15S = "sora-v2-landscape-15s"  # 横屏 15s


class VideoResolution(str, Enum):
    """视频分辨率档位."""
    
    P480 = "480P"
    P720 = "720P"
    P1080 = "1080P"


class VideoDuration(int, Enum):
    """视频时长（秒）."""
    
    FOUR_SECONDS = 4  # Google Veo支持
    FIVE_SECONDS = 5
    SIX_SECONDS = 6   # Google Veo支持
    EIGHT_SECONDS = 8 # Google Veo支持
    TEN_SECONDS = 10
    FIFTEEN_SECONDS = 15  # Sora 2 支持


class ImageToVideoRequest(BaseModel):
    """图生视频请求模型."""
    
    model: VideoModel = Field(
        default=VideoModel.VOLC_I2V_FIRST,
        description="视频生成模型"
    )
    
    first_frame_base64: Optional[str] = Field(
        default=None,
        description="首帧图片Base64编码（文生视频模式可选）"
    )
    
    last_frame_base64: Optional[str] = Field(
        default=None,
        description="尾帧图片Base64编码（仅首尾帧模式需要）"
    )
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=800,
        description="视频描述提示词"
    )
    
    duration: int = Field(
        default=5,
        description="视频时长（秒），支持4/5/6/8/10/15秒"
    )
    
    resolution: VideoResolution = Field(
        default=VideoResolution.P720,
        description="视频分辨率档位（通义万相模型使用）"
    )
    
    aspect_ratio: Optional[str] = Field(
        default="16:9",
        description="视频长宽比（仅文生视频模式使用）",
        pattern="^(16:9|4:3|1:1|3:4|9:16|21:9)$"
    )
    
    @field_validator("first_frame_base64", "last_frame_base64")
    @classmethod
    def validate_base64(cls, v: Optional[str]) -> Optional[str]:
        """验证Base64编码格式."""
        if v is None:
            return v
        
        # 检查是否包含data URI前缀
        if not v.startswith("data:image/"):
            raise ValueError(
                "图片必须为Base64格式，格式: data:image/{type};base64,{data}"
            )
        
        return v
    
    @field_validator("model")
    @classmethod
    def validate_model_with_frames(cls, v: VideoModel) -> VideoModel:
        """验证模型与帧模式的匹配."""
        return v
    
    class Config:
        """Pydantic配置."""
        
        json_schema_extra = {
            "example": {
                "model": "volc-i2v-first",
                "first_frame_base64": "data:image/png;base64,iVBORw0KGgoAAAA...",
                "last_frame_base64": None,
                "prompt": "一只橘猫在沙滩上熟睡，海浪轻轻拍岸，镜头缓缓拉远",
                "duration": 5,
                "resolution": "720P",
                "aspect_ratio": "16:9"
            }
        }


class AnalyzeImageRequest(BaseModel):
    """图片分析请求模型."""
    
    image_base64: str = Field(
        ...,
        description="图片Base64编码"
    )
    
    enable_thinking: bool = Field(
        default=True,
        description="是否开启思考模式"
    )
    
    @field_validator("image_base64")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        """验证Base64编码格式."""
        if not v.startswith("data:image/"):
            raise ValueError(
                "图片必须为Base64格式，格式: data:image/{type};base64,{data}"
            )
        
        return v
    
    class Config:
        """Pydantic配置."""
        
        json_schema_extra = {
            "example": {
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAA...",
                "enable_thinking": True
            }
        }


class AnalyzeImageResponse(BaseModel):
    """图片分析响应模型."""
    
    description: str = Field(
        ...,
        description="生成的图片描述（适合视频生成）"
    )
    
    class Config:
        """Pydantic配置."""
        
        json_schema_extra = {
            "example": {
                "description": "一只胖乎乎的橘猫正安静地躺在金色的沙滩上熟睡..."
            }
        }


class ImageToVideoResponse(BaseModel):
    """图生视频响应模型."""
    
    video_url: str = Field(
        ...,
        description="生成的视频URL"
    )
    
    task_id: str = Field(
        ...,
        description="任务ID"
    )
    
    model: str = Field(
        ...,
        description="使用的模型"
    )
    
    duration: int = Field(
        ...,
        description="视频时长（秒）"
    )
    
    orig_prompt: Optional[str] = Field(
        default=None,
        description="原始提示词"
    )
    
    actual_prompt: Optional[str] = Field(
        default=None,
        description="实际使用的提示词（如果模型进行了改写）"
    )
    
    class Config:
        """Pydantic配置."""
        
        json_schema_extra = {
            "example": {
                "video_url": "https://example.com/video.mp4",
                "task_id": "12345678",
                "model": "volc-i2v-first",
                "duration": 5,
                "orig_prompt": "一只橘猫在沙滩上",
                "actual_prompt": "一只胖乎乎的橘猫正安静地躺在金色的沙滩上熟睡..."
            }
        }

