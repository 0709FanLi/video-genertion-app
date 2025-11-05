"""通义千问文生图服务.

封装与通义千问Qwen-Image模型的交互逻辑，用于纯文本生成图片。
"""

from typing import Any, Optional

import httpx

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import ApiError
from app.services.oss_service import oss_service
from app.utils.retry_decorator import retry_decorator


class QwenImageService(LoggerMixin):
    """通义千问文生图服务类.
    
    使用qwen-image-plus模型进行纯文本生成图片。
    支持5种分辨率（16:9、4:3、1:1、3:4、9:16）。
    
    注意：此模型不支持参考图，仅支持纯文本生成。
    
    Attributes:
        base_url: API基础URL
        api_key: API密钥
        timeout: 请求超时时间
    """
    
    def __init__(self) -> None:
        """初始化通义千问文生图服务."""
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.api_key = settings.dashscope_api_key
        self.timeout = settings.request_timeout
        self.logger.info("QwenImageService初始化完成")
    
    def _get_headers(self) -> dict[str, str]:
        """获取请求头.
        
        Returns:
            包含认证信息的请求头字典
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def generate_image(
        self,
        prompt: str,
        size: str = "1328*1328",
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None
    ) -> dict[str, Any]:
        """生成图片（纯文本，同步接口）.
        
        Args:
            prompt: 正向提示词，描述期望的图像内容（最长800字符）
            size: 输出图像分辨率，格式为宽*高，可选：
                - 1664*928 (16:9)
                - 1472*1140 (4:3)
                - 1328*1328 (1:1，默认)
                - 1140*1472 (3:4)
                - 928*1664 (9:16)
            prompt_extend: 是否开启提示词智能改写（默认True）
            watermark: 是否添加水印（默认False）
            seed: 随机种子（可选，范围0-2147483647）
            
        Returns:
            包含图片URL和元数据的字典:
            {
                "image_url": str,  # OSS永久URL
                "orig_prompt": str,
                "actual_prompt": str,  # 智能改写后的提示词（如果开启）
                "task_id": str,
                "width": int,
                "height": int
            }
            
        Raises:
            ApiError: API调用失败
        """
        url = f"{self.base_url}/services/aigc/multimodal-generation/generation"
        headers = self._get_headers()
        
        # 构建请求体
        payload = {
            "model": "qwen-image-plus",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "size": size,
                "n": 1,
                "prompt_extend": prompt_extend,
                "watermark": watermark
            }
        }
        
        # 添加可选参数
        if seed is not None:
            payload["parameters"]["seed"] = seed
        
        self.logger.info(
            f"通义千问文生图: prompt长度={len(prompt)}, "
            f"size={size}, prompt_extend={prompt_extend}"
        )
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # 解析响应
                if "output" not in data or "choices" not in data["output"]:
                    error_message = data.get("message", "未知错误")
                    self.logger.error(f"生成图片失败: {error_message}, 详情: {data}")
                    raise ApiError(
                        f"生成图片失败: {error_message}",
                        detail=str(data)
                    )
                
                # 提取图片URL
                choices = data["output"]["choices"]
                if not choices or "message" not in choices[0]:
                    raise ApiError(
                        "响应格式错误：缺少choices或message",
                        detail=str(data)
                    )
                
                message = choices[0]["message"]
                content = message.get("content", [])
                if not content or "image" not in content[0]:
                    raise ApiError(
                        "响应格式错误：缺少image字段",
                        detail=str(data)
                    )
                
                temp_image_url = content[0]["image"]
                
                # 提取usage信息
                usage = data.get("usage", {})
                width = usage.get("width", 0)
                height = usage.get("height", 0)
                
                self.logger.info(
                    f"通义千问文生图成功: {width}x{height}, "
                    f"temp_url={temp_image_url[:80]}..."
                )
                
                # 转存图片到OSS（24小时临时URL → 永久URL）
                permanent_url = await self._save_image_to_oss(
                    temp_image_url,
                    size
                )
                
                # 构建返回结果
                result = {
                    "image_url": permanent_url,
                    "orig_prompt": prompt,
                    "temp_image_url": temp_image_url,  # 保留临时URL供调试
                    "width": width,
                    "height": height
                }
                
                # 如果开启了prompt_extend，添加actual_prompt
                # 注意：同步接口不返回actual_prompt，只有异步接口才有
                # 这里我们可以记录原始prompt
                self.logger.info(f"图片已转存OSS，永久URL: {permanent_url[:80]}...")
                
                return result
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                self.logger.error(f"通义千问请求失败: {error_detail}")
                raise ApiError("通义千问请求失败", detail=error_detail)
            except Exception as e:
                self.logger.error(f"生成图片异常: {str(e)}")
                raise
    
    async def _save_image_to_oss(
        self,
        temp_image_url: str,
        size: str
    ) -> str:
        """将临时图片URL转存到OSS并返回永久URL.
        
        Args:
            temp_image_url: 通义千问返回的临时图片URL（24小时有效期）
            size: 图片尺寸（用于文件命名）
            
        Returns:
            OSS永久图片URL
            
        Raises:
            ApiError: 转存失败
        """
        try:
            self.logger.info(f"开始转存图片到OSS: size={size}")
            
            # 生成文件名（带时间戳和尺寸标识）
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            size_tag = size.replace("*", "x")  # 1328*1328 -> 1328x1328
            filename = f"qwen_image_{size_tag}_{timestamp}.png"
            
            # 从临时URL下载并上传到OSS
            oss_result = await oss_service.upload_from_url(
                url=temp_image_url,
                filename=filename,
                category="images"
            )
            
            permanent_url = oss_result["url"]
            self.logger.info(
                f"图片转存成功: {filename}, "
                f"大小: {oss_result['size'] / 1024:.2f}KB, "
                f"OSS URL: {permanent_url[:100]}..."
            )
            
            return permanent_url
            
        except Exception as e:
            self.logger.error(f"图片转存OSS失败: {str(e)}")
            # 转存失败时，返回原临时URL作为降级方案
            self.logger.warning("使用临时URL作为降级方案（24小时有效期）")
            return temp_image_url


# 全局服务实例
qwen_image_service = QwenImageService()

