"""数据模型模块."""

from app.schemas.requests import (
    ImageGenerationRequest,
    PromptGenerationRequest,
    VideoGenerationRequest,
    VideoPromptOptimiseRequest,
)
from app.schemas.responses import (
    ImageGenerationResponse,
    PromptGenerationResponse,
    VideoGenerationResponse,
    VideoPromptOptimiseResponse,
)

__all__ = [
    # Requests
    "PromptGenerationRequest",
    "ImageGenerationRequest",
    "VideoPromptOptimiseRequest",
    "VideoGenerationRequest",
    # Responses
    "PromptGenerationResponse",
    "ImageGenerationResponse",
    "VideoPromptOptimiseResponse",
    "VideoGenerationResponse",
]

