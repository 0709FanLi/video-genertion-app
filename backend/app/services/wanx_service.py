"""通义万相服务.

封装与通义万相图片和视频生成API的交互逻辑。
"""

import asyncio
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import DashScopeApiError, TaskFailedError, TaskTimeoutError
from app.utils.retry_decorator import retry_decorator


class WanxService(LoggerMixin):
    """通义万相服务类.
    
    负责调用通义万相API进行图片生成和视频生成。
    
    Attributes:
        base_url: API基础URL
        api_key: API密钥
        timeout: 请求超时时间
    """
    
    def __init__(self) -> None:
        """初始化通义万相服务."""
        self.base_url = settings.wanx_base_url
        self.api_key = settings.dashscope_api_key
        self.timeout = settings.request_timeout
        self.logger.info("WanxService初始化完成")
    
    def _get_headers(self) -> dict[str, str]:
        """获取请求头.
        
        Returns:
            包含认证信息的请求头字典
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def _create_task(
        self,
        endpoint: str,
        payload: dict[str, Any]
    ) -> str:
        """创建异步任务.
        
        Args:
            endpoint: API端点
            payload: 请求负载
            
        Returns:
            任务ID
            
        Raises:
            DashScopeApiError: 创建任务失败时抛出
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.logger.info(f"创建异步任务: {endpoint}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload
                )
                
                if response.status_code != 200:
                    raise DashScopeApiError(
                        message="创建任务失败",
                        status_code=response.status_code,
                        detail=response.text
                    )
                
                data = response.json()
                task_id = data.get("output", {}).get("task_id")
                
                if not task_id:
                    raise DashScopeApiError(
                        message="未获取到任务ID",
                        detail=data
                    )
                
                self.logger.info(f"任务创建成功，任务ID: {task_id}")
                return task_id
                
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP请求失败: {str(e)}", exc_info=True)
            raise DashScopeApiError(
                message="HTTP请求失败",
                detail=str(e)
            )
    
    async def _poll_task(
        self,
        task_id: str,
        max_attempts: int = 120
    ) -> dict[str, Any]:
        """轮询任务结果.
        
        Args:
            task_id: 任务ID
            max_attempts: 最大轮询次数，默认120次（10分钟）
            
        Returns:
            任务结果数据
            
        Raises:
            TaskFailedError: 任务失败时抛出
            TaskTimeoutError: 轮询超时时抛出
        """
        url = f"{self.base_url}/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        self.logger.info(f"开始轮询任务: {task_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code != 200:
                        self.logger.warning(
                            f"轮询请求失败，状态码: {response.status_code}"
                        )
                        await asyncio.sleep(settings.task_poll_interval)
                        continue
                    
                    data = response.json()
                    status = data.get("output", {}).get("task_status")
                    
                    self.logger.debug(
                        f"任务状态: {status}，轮询次数: {attempt + 1}/{max_attempts}"
                    )
                    
                    if status == "SUCCEEDED":
                        self.logger.info(f"任务{task_id}执行成功")
                        return data
                    elif status == "FAILED":
                        error_msg = data.get("output", {}).get("message", "未知错误")
                        self.logger.error(f"任务{task_id}执行失败: {error_msg}")
                        raise TaskFailedError(
                            message="任务执行失败",
                            task_id=task_id,
                            detail=data
                        )
                    elif status in ["PENDING", "RUNNING"]:
                        await asyncio.sleep(settings.task_poll_interval)
                    else:
                        self.logger.warning(f"未知任务状态: {status}")
                        await asyncio.sleep(settings.task_poll_interval)
                        
                except httpx.HTTPError as e:
                    self.logger.warning(f"轮询请求异常: {str(e)}")
                    await asyncio.sleep(settings.task_poll_interval)
            
            # 超过最大轮询次数
            timeout_seconds = max_attempts * settings.task_poll_interval
            self.logger.error(f"任务{task_id}轮询超时")
            raise TaskTimeoutError(
                message="任务执行超时",
                task_id=task_id,
                timeout=timeout_seconds
            )
    
    async def generate_images(self, prompt: str, n: int = 4) -> dict[str, Any]:
        """生成图片.
        
        根据提示词生成图片。
        
        Args:
            prompt: 图片生成提示词
            n: 生成图片数量，默认4张
            
        Returns:
            包含图片URL的结果数据
            
        Raises:
            DashScopeApiError: API调用失败
            TaskFailedError: 任务失败
            TaskTimeoutError: 任务超时
        """
        self.logger.info(f"开始生成图片，提示词长度: {len(prompt)}，数量: {n}")
        
        payload = {
            "model": "wanx-v1",
            "input": {"prompt": prompt},
            "parameters": {"n": n, "size": "1024*1024"}
        }
        
        endpoint = "/services/aigc/text2image/image-synthesis"
        task_id = await self._create_task(endpoint, payload)
        result = await self._poll_task(task_id)
        
        self.logger.info(f"图片生成完成，任务ID: {task_id}")
        return result
    
    async def generate_video(
        self,
        image_url: str,
        prompt: str
    ) -> dict[str, Any]:
        """生成视频.
        
        根据图片和提示词生成视频。
        
        Args:
            image_url: 首帧图片URL
            prompt: 视频动态描述提示词
            
        Returns:
            包含视频URL的结果数据
            
        Raises:
            DashScopeApiError: API调用失败
            TaskFailedError: 任务失败
            TaskTimeoutError: 任务超时
        """
        self.logger.info(
            f"开始生成视频，图片URL: {image_url}, 提示词长度: {len(prompt)}"
        )
        
        payload = {
            "model": "wan2.5-i2v-preview",
            "input": {
                "prompt": prompt,
                "img_url": image_url
            }
        }
        
        endpoint = "/services/aigc/video-generation/video-synthesis"
        task_id = await self._create_task(endpoint, payload)
        result = await self._poll_task(task_id, max_attempts=180)  # 视频生成需要更长时间
        
        self.logger.info(f"视频生成完成，任务ID: {task_id}")
        return result


# 全局服务实例
wanx_service = WanxService()

