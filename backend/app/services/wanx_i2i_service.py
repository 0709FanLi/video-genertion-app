"""通义万相多图生图服务.

支持使用参考图片生成新图片，基于wan2.5-i2i-preview模型。
参考文档: https://bailian.console.aliyun.com/
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.custom_exceptions import ApiError

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
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
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
        
        image_urls = [item.get("url") for item in results if item.get("url")]
        
        logger.info(f"成功生成 {len(image_urls)} 张图片")
        return image_urls
    
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

