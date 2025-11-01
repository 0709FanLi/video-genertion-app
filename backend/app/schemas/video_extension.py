"""视频扩展相关的Pydantic模型定义."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class VideoExtensionRequest(BaseModel):
    """视频扩展请求模型."""
    
    video_url: str = Field(
        ...,
        description="原始视频OSS URL",
        min_length=1
    )
    
    prompt: str = Field(
        ...,
        description="视频扩展描述提示词",
        min_length=1,
        max_length=1000
    )
    
    model: str = Field(
        default="google-veo-3.1",
        description="视频扩展模型"
    )
    
    aspect_ratio: str = Field(
        default="16:9",
        description="视频长宽比",
        pattern="^(16:9|9:16)$"
    )
    
    duration: Optional[int] = Field(
        default=8,
        description="视频时长（秒），可选值：4、6、8",
        ge=4,
        le=8
    )
    
    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """验证时长只能是4、6、8秒."""
        if v is not None and v not in [4, 6, 8]:
            raise ValueError("duration必须是4、6或8秒")
        return v
    
    resolution: Optional[str] = Field(
        default="720p",
        description="视频分辨率",
        pattern="^(720p|1080p)$"
    )
    
    negative_prompt: Optional[str] = Field(
        default=None,
        description="反向提示词（可选）",
        max_length=500
    )
    
    @field_validator("video_url")
    @classmethod
    def validate_video_url(cls, v: str) -> str:
        """验证视频URL格式."""
        if not v.startswith("http"):
            raise ValueError("video_url必须是有效的HTTP(S) URL")
        return v
    
    class Config:
        """Pydantic配置."""
        
        json_schema_extra = {
            "example": {
                "video_url": "https://tool251027.oss-cn-shanghai.aliyuncs.com/videos/example.mp4",
                "prompt": "Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower.",
                "model": "google-veo-3.1",
                "aspect_ratio": "16:9",
                "negative_prompt": "cartoon, drawing, low quality"
            }
        }


class VideoExtensionResponse(BaseModel):
    """视频扩展响应模型."""
    
    extended_video_url: str = Field(
        ...,
        description="扩展后的视频OSS URL"
    )
    
    original_video_url: str = Field(
        ...,
        description="原始视频URL"
    )
    
    prompt: str = Field(
        ...,
        description="扩展提示词"
    )
    
    duration: int = Field(
        ...,
        description="视频时长（秒）"
    )
    
    resolution: str = Field(
        ...,
        description="视频分辨率"
    )
    
    aspect_ratio: str = Field(
        ...,
        description="视频长宽比"
    )
    
    model: str = Field(
        ...,
        description="使用的模型"
    )
    
    class Config:
        """Pydantic配置."""
        
        json_schema_extra = {
            "example": {
                "extended_video_url": "https://tool251027.oss-cn-shanghai.aliyuncs.com/videos/veo_extended_16x9_20250128_143022.mp4",
                "original_video_url": "https://tool251027.oss-cn-shanghai.aliyuncs.com/videos/example.mp4",
                "prompt": "Track the butterfly into the garden as it lands on an orange origami flower.",
                "duration": 8,
                "resolution": "720p",
                "aspect_ratio": "16:9",
                "model": "veo-3.1-generate-preview"
            }
        }


class ModelsListResponse(BaseModel):
    """模型列表响应模型."""
    
    video_extension_models: dict = Field(
        ...,
        description="可用的视频扩展模型列表"
    )
    
    class Config:
        """Pydantic配置."""
        
        json_schema_extra = {
            "example": {
                "video_extension_models": {
                    "google-veo-3.1": {
                        "name": "Google Veo 3.1",
                        "model_id": "veo-3.1-generate-preview",
                        "default": True,
                        "specs": {
                            "resolution": "720p",
                            "duration": 8,
                            "aspect_ratios": ["16:9", "9:16"],
                            "supports_negative_prompt": True
                        }
                    }
                }
            }
        }

