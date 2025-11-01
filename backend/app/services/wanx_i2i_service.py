"""通义万相多图生图服务.

支持使用参考图片生成新图片，基于wan2.5-i2i-preview模型。
参考文档: https://bailian.console.aliyun.com/
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.custom_exceptions import ApiError
from app.services.oss_service import oss_service
from app.utils.retry_decorator import retry_decorator

logger = get_logger(__name__)


class WanxI2IService:
    """通义万相多图生图服务类.
    
    封装通义万相多图生图API调用逻辑，支持参考图功能。
    
    Attributes:
        base_url: API基础URL
        api_key: API密钥
        timeout: 请求超时时间
        poll_interval: 轮询间隔（秒）
        max_poll_attempts: 最大轮询次数
    """
    
    MODEL_ID = "wan2.5-i2i-preview"
    MAX_REFERENCE_IMAGES = 2  # 根据文档，数组长度不超过2
    
    def __init__(self) -> None:
        """初始化通义万相多图生图服务."""
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"  # 固定URL
        self.api_key = settings.dashscope_api_key
        self.timeout = settings.request_timeout
        self.poll_interval = 10  # 根据文档建议，设置10秒轮询间隔
        self.max_poll_attempts = 36  # 最多轮询6分钟（36次 * 10秒）
        
        logger.info("WanxI2IService初始化完成")
    
    def _get_headers(self, async_enabled: bool = True) -> Dict[str, str]:
        """获取请求头.
        
        Args:
            async_enabled: 是否启用异步任务模式
        
        Returns:
            包含认证信息的请求头字典
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if async_enabled:
            headers["X-DashScope-Async"] = "enable"
        
        return headers
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def _create_task(
        self,
        prompt: str,
        reference_image_urls: Optional[List[str]] = None,
        size: str = "1024*1024",
        num_images: int = 1,
        style: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """创建多图生图任务.
        
        Args:
            prompt: 文本提示词
            reference_image_urls: 参考图片URL列表（最多4张）
            size: 图片尺寸
            num_images: 生成图片数量
            style: 风格参数
            **kwargs: 其他参数
        
        Returns:
            任务ID
        
        Raises:
            ApiError: 创建任务失败
        """
        logger.info(
            f"创建万相多图生图任务: prompt={prompt[:50]}..., "
            f"ref_imgs={len(reference_image_urls) if reference_image_urls else 0}"
        )
        
        # 验证参考图数量
        if reference_image_urls and len(reference_image_urls) > self.MAX_REFERENCE_IMAGES:
            raise ApiError(
                message=f"参考图数量超过限制",
                detail=f"最多支持{self.MAX_REFERENCE_IMAGES}张参考图"
            )
        
        # 构建请求负载（根据文档格式）
        input_data: Dict[str, Any] = {
            "prompt": prompt,
            "images": reference_image_urls if reference_image_urls else []  # 参数名为images
        }
        
        payload = {
            "model": self.MODEL_ID,
            "input": input_data,
            "parameters": {
                "n": num_images  # 不传size参数，文档中无size参数
            }
        }
        
        # 添加其他可选参数
        if kwargs:
            payload["parameters"].update(kwargs)
        
        # 根据文档，正确的URL路径
        url = f"{self.base_url}/services/aigc/image2image/image-synthesis"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(async_enabled=True),
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"创建任务失败: {response.status_code} - {response.text}")
                    raise ApiError(
                        message="创建任务失败",
                        detail=response.text
                    )
                
                data = response.json()
                
                # 检查响应状态
                if "output" not in data or "task_id" not in data.get("output", {}):
                    logger.error(f"无效的响应格式: {data}")
                    raise ApiError(
                        message="创建任务失败",
                        detail=f"响应格式错误: {data}"
                    )
                
                task_id = data["output"]["task_id"]
                logger.info(f"任务创建成功，任务ID: {task_id}")
                
                return task_id
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP请求失败: {e}")
            raise ApiError(
                message="HTTP请求失败",
                detail=str(e)
            )
    
    async def _poll_task(self, task_id: str) -> Dict[str, Any]:
        """轮询任务结果.
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务结果数据
        
        Raises:
            ApiError: 任务失败或超时
        """
        url = f"{self.base_url}/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        logger.info(f"开始轮询任务: {task_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_poll_attempts):
                try:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code != 200:
                        logger.warning(f"轮询请求失败: {response.status_code}")
                        await asyncio.sleep(self.poll_interval)
                        continue
                    
                    data = response.json()
                    status = data.get("output", {}).get("task_status")
                    
                    logger.debug(
                        f"任务状态: {status}, 轮询次数: {attempt + 1}/{self.max_poll_attempts}"
                    )
                    
                    if status == "SUCCEEDED":
                        logger.info(f"任务{task_id}执行成功")
                        return data
                    
                    elif status == "FAILED":
                        error_msg = data.get("output", {}).get("message", "未知错误")
                        logger.error(f"任务{task_id}执行失败: {error_msg}")
                        raise ApiError(
                            message="任务执行失败",
                            detail=error_msg
                        )
                    
                    elif status in ["PENDING", "RUNNING"]:
                        await asyncio.sleep(self.poll_interval)
                    
                    else:
                        logger.warning(f"未知任务状态: {status}")
                        await asyncio.sleep(self.poll_interval)
                
                except httpx.HTTPError as e:
                    logger.warning(f"轮询请求异常: {e}")
                    await asyncio.sleep(self.poll_interval)
            
            # 超时
            logger.error(f"任务{task_id}轮询超时")
            raise ApiError(
                message="任务执行超时",
                detail=f"超过{self.max_poll_attempts * self.poll_interval}秒"
            )
    
    async def generate_image(
        self,
        prompt: str,
        reference_image_urls: Optional[List[str]] = None,
        size: str = "1024*1024",  # 保留参数兼容性，但不使用
        num_images: int = 1,
        **kwargs: Any
    ) -> List[str]:
        """生成图片（多图生图）.
        
        Args:
            prompt: 文本提示词（最长2000字符）
            reference_image_urls: 参考图片URL列表（最多2张）
            size: 图片尺寸（保留兼容性，实际不使用）
            num_images: 生成图片数量（1-4张）
            **kwargs: 其他参数（如seed、watermark等）
        
        Returns:
            生成的图片URL列表
        
        Raises:
            ApiError: 生成失败
        """
        # 创建任务
        task_id = await self._create_task(
            prompt=prompt,
            reference_image_urls=reference_image_urls,
            size=size,
            num_images=num_images,
            style=None,
            **kwargs
        )
        
        # 轮询结果
        result = await self._poll_task(task_id)
        
        # 提取图片URL
        results = result.get("output", {}).get("results", [])
        
        if not results:
            logger.error(f"任务{task_id}未返回图片")
            raise ApiError(
                message="未返回图片",
                detail="结果中没有图片URL"
            )
        
        temp_image_urls = [item.get("url") for item in results if item.get("url")]
        
        if not temp_image_urls:
            logger.error(f"任务{task_id}未返回有效图片URL")
            raise ApiError(
                message="未返回有效图片URL",
                detail="结果中的URL为空"
            )
        
        logger.info(f"成功生成 {len(temp_image_urls)} 张图片，开始转存到OSS...")
        
        # 转存所有图片到OSS（与通义千问保持一致）
        permanent_image_urls = []
        for idx, temp_url in enumerate(temp_image_urls):
            try:
                permanent_url = await self._save_image_to_oss(temp_url, size, idx + 1)
                permanent_image_urls.append(permanent_url)
            except Exception as e:
                logger.warning(f"转存第{idx + 1}张图片失败: {str(e)}，使用临时URL作为降级方案")
                # 转存失败时，使用临时URL作为降级方案
                permanent_image_urls.append(temp_url)
        
        logger.info(f"图片转存完成: {len(permanent_image_urls)} 张图片")
        return permanent_image_urls
    
    async def _save_image_to_oss(
        self,
        temp_image_url: str,
        size: str,
        index: int = 1
    ) -> str:
        """将临时图片URL转存到OSS并返回永久URL.
        
        Args:
            temp_image_url: 通义万相返回的临时图片URL
            size: 图片尺寸（用于文件命名）
            index: 图片序号（用于文件命名）
            
        Returns:
            OSS永久图片URL
            
        Raises:
            ApiError: 转存失败
        """
        try:
            logger.info(f"开始转存图片到OSS: size={size}, index={index}")
            
            # 生成文件名（带时间戳和尺寸标识）
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            size_tag = size.replace("*", "x")  # 1024*1024 -> 1024x1024
            filename = f"wanx_i2i_{size_tag}_{timestamp}_{index}.png"
            
            # 从临时URL下载并上传到OSS
            oss_result = await oss_service.upload_from_url(
                url=temp_image_url,
                filename=filename,
                category="images"
            )
            
            permanent_url = oss_result["url"]
            logger.info(
                f"图片转存成功: {filename}, "
                f"大小: {oss_result['size'] / 1024:.2f}KB, "
                f"OSS URL: {permanent_url[:100]}..."
            )
            
            return permanent_url
            
        except Exception as e:
            logger.error(f"图片转存OSS失败: {str(e)}")
            # 转存失败时，返回原临时URL作为降级方案
            logger.warning("使用临时URL作为降级方案（临时链接可能有过期时间）")
            return temp_image_url
    
    async def health_check(self) -> bool:
        """健康检查.
        
        Returns:
            服务是否可用
        """
        try:
            # 简单测试
            await self.generate_image("test", num_images=1)
            return True
        except Exception as e:
            logger.error(f"万相多图生图健康检查失败: {e}")
            return False


# 全局服务实例
wanx_i2i_service = WanxI2IService()

