"""Google Gemini 文生图服务.

封装对 Gemini 图片生成模型的访问逻辑，提供纯文本生成图片能力。
"""

from __future__ import annotations

import base64
import binascii
from datetime import datetime
from io import BytesIO
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import ApiError
from app.services.oss_service import oss_service
from app.utils.retry_decorator import retry_decorator


class GeminiImageService(LoggerMixin):
    """Google Gemini 文生图服务类.

    使用 gemini-2.5-flash-image 模型执行文本生成图片请求，并将结果持久化。

    Attributes:
        base_url: Gemini API 基础 URL
        model: 默认使用的图片生成模型
        timeout: 请求超时时间（秒）
    """

    _SIZE_TO_RATIO_MAP: dict[str, str] = {
        "1024x1024": "1:1",
        "832x1248": "2:3",
        "1248x832": "3:2",
        "864x1184": "3:4",
        "1184x864": "4:3",
        "896x1152": "4:5",
        "1152x896": "5:4",
        "768x1344": "9:16",
        "1344x768": "16:9",
        "1536x672": "21:9",
    }

    def __init__(self) -> None:
        """初始化服务实例."""

        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash-image"
        self.api_key = settings.gemini_api_key
        self.timeout = settings.request_timeout

        if not self.api_key:
            self.logger.warning("Gemini API Key 未配置，文生图服务暂不可用")

    def _resolve_aspect_ratio(self, size: str | None) -> str:
        """根据尺寸字符串推导宽高比."""

        if not size:
            return "1:1"

        normalized = (
            size.strip()
            .lower()
            .replace("×", "x")
            .replace("*", "x")
        )

        if normalized in self._SIZE_TO_RATIO_MAP:
            return self._SIZE_TO_RATIO_MAP[normalized]

        # 尝试通过解析尺寸自动计算比例
        try:
            width_str, height_str = normalized.split("x")
            width = int(width_str)
            height = int(height_str)
            if width <= 0 or height <= 0:
                raise ValueError

            from math import gcd

            divisor = gcd(width, height)
            if divisor == 0:
                raise ValueError

            simplified_width = width // divisor
            simplified_height = height // divisor
            aspect_ratio = f"{simplified_width}:{simplified_height}"
            return aspect_ratio
        except ValueError:
            self.logger.warning("无法识别的尺寸格式: %s，默认使用1:1", size)
            return "1:1"

    def _build_headers(self) -> dict[str, str]:
        """构建请求头."""

        if not self.api_key:
            raise ApiError(
                message="Gemini API Key 未配置",
                detail="请设置 GEMINI_API_KEY 环境变量"
            )

        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

    def _build_payload(self, prompt: str, aspect_ratio: str) -> dict[str, Any]:
        """构建请求体."""

        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio
                }
            }
        }

        return payload

    def _extract_image_bytes(self, data: dict[str, Any]) -> tuple[bytes, str]:
        """从响应中提取图片数据."""

        try:
            candidates = data["candidates"]
            if not candidates:
                raise KeyError("candidates")

            content = candidates[0]["content"]
            parts = content["parts"]
            inline_data = next(
                part["inlineData"]
                for part in parts
                if "inlineData" in part
            )
            image_base64 = inline_data["data"]
            mime_type = inline_data.get("mimeType", "image/png")
        except (KeyError, IndexError, StopIteration) as exc:
            self.logger.error("Gemini 响应格式异常: %s", data)
            raise ApiError(
                message="Gemini 响应格式错误",
                detail="未找到图片数据"
            ) from exc

        try:
            image_bytes = base64.b64decode(image_base64)
        except (ValueError, binascii.Error) as exc:
            self.logger.error("图片Base64解码失败: %s", exc)
            raise ApiError(
                message="图片解码失败",
                detail="Base64数据无效"
            ) from exc

        return image_bytes, mime_type

    def _save_image_to_oss(
        self,
        image_bytes: bytes,
        mime_type: str,
        aspect_ratio: str,
        index: int
    ) -> str:
        """保存图片到OSS，失败时返回Base64数据URL."""

        extension = "png"
        if mime_type.lower() == "image/jpeg":
            extension = "jpg"
        elif mime_type.lower() == "image/webp":
            extension = "webp"

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"gemini_image_{aspect_ratio.replace(':', '-')}_{timestamp}_{index + 1}.{extension}"
        )

        try:
            upload_result = oss_service.upload_file(
                file_data=BytesIO(image_bytes),
                filename=filename,
                category="images",
                content_type=mime_type
            )
            url = upload_result["url"]
            self.logger.info("Gemini 图片已上传到 OSS: %s", url)
            return url
        except ApiError as error:
            self.logger.warning(
                "OSS 未配置或上传失败，使用 Base64 数据URL: %s",
                getattr(error, "detail", str(error))
            )
        except Exception as error:  # pylint: disable=broad-except
            self.logger.error("保存图片到OSS异常: %s", error)

        # 退化到返回Base64数据URL
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def _request_image(
        self,
        prompt: str,
        aspect_ratio: str
    ) -> tuple[bytes, str]:
        """发送请求并返回图片二进制数据."""

        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = self._build_headers()
        payload = self._build_payload(prompt, aspect_ratio)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                detail = exc.response.text
                self.logger.error("Gemini API 请求失败: %s %s", status, detail)
                raise ApiError(
                    message="Gemini API 请求失败",
                    detail=f"HTTP {status}: {detail}"
                ) from exc
            except httpx.RequestError as exc:
                self.logger.error("Gemini API 网络异常: %s", exc)
                raise ApiError(
                    message="Gemini API 网络异常",
                    detail=str(exc)
                ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            self.logger.error("解析Gemini响应JSON失败: %s", exc)
            raise ApiError(
                message="Gemini 响应解析失败",
                detail=str(exc)
            ) from exc

        return self._extract_image_bytes(data)

    async def generate_images(
        self,
        prompt: str,
        size: str = "1024x1024",
        num_images: int = 1
    ) -> list[str]:
        """生成图片并返回URL列表."""

        if num_images <= 0:
            raise ApiError("生成张数必须大于0")

        aspect_ratio = self._resolve_aspect_ratio(size)
        image_urls: list[str] = []

        for index in range(num_images):
            image_bytes, mime_type = await self._request_image(prompt, aspect_ratio)
            image_url = self._save_image_to_oss(image_bytes, mime_type, aspect_ratio, index)
            image_urls.append(image_url)

        self.logger.info(
            "Gemini 图片生成成功: prompt长度=%s, ratio=%s, 数量=%s",
            len(prompt),
            aspect_ratio,
            num_images
        )

        return image_urls


# 全局服务实例
gemini_image_service = GeminiImageService()


