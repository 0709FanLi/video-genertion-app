"""通义万相首尾帧生视频服务.

封装与通义万相图生视频API的交互逻辑，支持首尾帧生成视频。
"""

import asyncio
from typing import Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import DashScopeApiError, TaskFailedError, TaskTimeoutError
from app.services.oss_service import oss_service


class WanxKf2vService(LoggerMixin):
    """通义万相首尾帧生视频服务类.
    
    负责调用通义万相首尾帧生视频API。
    支持wan2.2-kf2v-flash（推荐）和wanx2.1-kf2v-plus模型。
    
    Attributes:
        base_url: API基础URL
        api_key: API密钥
        timeout: 请求超时时间
        poll_interval: 轮询间隔（秒）
        max_poll_attempts: 最大轮询次数
    """
    
    def __init__(self) -> None:
        """初始化通义万相首尾帧生视频服务."""
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.api_key = settings.dashscope_api_key
        self.timeout = settings.request_timeout
        self.poll_interval = 15  # 视频生成建议15秒轮询间隔
        self.max_poll_attempts = 240  # 最多轮询60分钟
        self.logger.info("WanxKf2vService初始化完成")
    
    def _get_headers(self) -> dict[str, str]:
        """获取请求头.
        
        Returns:
            包含认证信息的请求头字典
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"  # 必须设置为异步模式
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _create_task(
        self,
        model: str,
        first_frame_url: str,
        prompt: str,
        last_frame_url: Optional[str] = None,
        resolution: str = "720P",
        prompt_extend: bool = True
    ) -> str:
        """创建视频生成任务.
        
        Args:
            model: 模型名称（wan2.2-kf2v-flash 或 wanx2.1-kf2v-plus）
            first_frame_url: 首帧图片URL（支持公网URL或Base64）
            prompt: 视频描述提示词（最长800字符）
            last_frame_url: 尾帧图片URL（可选）
            resolution: 分辨率档位（480P/720P/1080P，取决于模型）
            prompt_extend: 是否开启prompt智能改写
            
        Returns:
            任务ID
            
        Raises:
            DashScopeApiError: API调用失败
        """
        url = f"{self.base_url}/services/aigc/image2video/video-synthesis"
        
        # 构建输入参数
        input_data: dict[str, Any] = {
            "first_frame_url": first_frame_url,
            "prompt": prompt
        }
        
        # 添加尾帧（如果提供）
        if last_frame_url:
            input_data["last_frame_url"] = last_frame_url
        
        payload = {
            "model": model,
            "input": input_data,
            "parameters": {
                "resolution": resolution,
                "prompt_extend": prompt_extend
            }
        }
        
        self.logger.info(
            f"创建视频生成任务: model={model}, resolution={resolution}, "
            f"has_last_frame={bool(last_frame_url)}"
        )
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                if "output" not in data or "task_id" not in data["output"]:
                    raise DashScopeApiError(
                        "创建任务失败：响应格式错误",
                        details=str(data)
                    )
                
                task_id = data["output"]["task_id"]
                self.logger.info(f"任务创建成功，task_id={task_id}")
                return task_id
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                self.logger.error(f"通义万相请求失败: {error_detail}")
                raise DashScopeApiError(
                    "通义万相请求失败",
                    details=error_detail
                )
            except Exception as e:
                self.logger.error(f"创建任务异常: {str(e)}")
                raise
    
    async def _poll_task(self, task_id: str) -> dict[str, Any]:
        """轮询任务状态直到完成.
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果数据
            
        Raises:
            TaskFailedError: 任务失败
            TaskTimeoutError: 轮询超时
            DashScopeApiError: API调用失败
        """
        url = f"{self.base_url}/tasks/{task_id}"
        attempts = 0
        
        self.logger.info(f"开始轮询任务状态: task_id={task_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while attempts < self.max_poll_attempts:
                try:
                    response = await client.get(url, headers=self._get_headers())
                    response.raise_for_status()
                    data = response.json()
                    
                    if "output" not in data:
                        raise DashScopeApiError(
                            "查询任务失败：响应格式错误",
                            details=str(data)
                        )
                    
                    output = data["output"]
                    task_status = output.get("task_status", "UNKNOWN")
                    
                    self.logger.debug(
                        f"任务状态: {task_status}, 尝试次数: {attempts + 1}"
                    )
                    
                    if task_status == "SUCCEEDED":
                        self.logger.info(f"任务完成: task_id={task_id}")
                        return output
                    
                    elif task_status in ["FAILED", "CANCELED", "UNKNOWN"]:
                        error_message = data.get("message", "未知错误")
                        self.logger.error(
                            f"任务失败: task_id={task_id}, "
                            f"status={task_status}, message={error_message}"
                        )
                        raise TaskFailedError(
                            f"任务{task_status}: {error_message}",
                            details=str(data)
                        )
                    
                    # PENDING 或 RUNNING 状态，继续等待
                    await asyncio.sleep(self.poll_interval)
                    attempts += 1
                    
                except httpx.HTTPStatusError as e:
                    error_detail = e.response.text
                    self.logger.error(f"查询任务状态失败: {error_detail}")
                    raise DashScopeApiError(
                        "查询任务状态失败",
                        details=error_detail
                    )
                except (TaskFailedError, DashScopeApiError):
                    raise
                except Exception as e:
                    self.logger.error(f"轮询任务异常: {str(e)}")
                    raise
        
        raise TaskTimeoutError(
            f"任务超时: 轮询{self.max_poll_attempts}次后仍未完成",
            details=f"task_id={task_id}"
        )
    
    async def _save_video_to_oss(
        self,
        temp_video_url: str,
        model: str
    ) -> str:
        """将临时视频URL转存到OSS并返回永久URL.
        
        Args:
            temp_video_url: 通义万相返回的临时视频URL（24小时有效期）
            model: 模型名称
            
        Returns:
            OSS永久视频URL
            
        Raises:
            ApiError: 转存失败
        """
        try:
            self.logger.info(f"开始转存视频到OSS: model={model}")
            
            # 生成文件名（带时间戳和模型标识）
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_short = model.replace(".", "_").replace("-", "_")
            filename = f"wanx_{model_short}_{timestamp}.mp4"
            
            # 从临时URL下载并上传到OSS
            oss_result = await oss_service.upload_from_url(
                url=temp_video_url,
                filename=filename,
                category="videos"
            )
            
            permanent_url = oss_result["url"]
            self.logger.info(
                f"视频转存成功: {filename}, "
                f"大小: {oss_result['size'] / 1024 / 1024:.2f}MB, "
                f"OSS URL: {permanent_url[:100]}..."
            )
            
            return permanent_url
            
        except Exception as e:
            self.logger.error(f"视频转存OSS失败: {str(e)}")
            # 转存失败时，返回原临时URL作为降级方案
            self.logger.warning("使用临时URL作为降级方案（24小时有效期）")
            return temp_video_url
    
    async def generate_video(
        self,
        first_frame_url: str,
        prompt: str,
        last_frame_url: Optional[str] = None,
        model: str = "wan2.2-kf2v-flash",
        resolution: str = "720P"
    ) -> dict[str, Any]:
        """生成视频（首尾帧模式）.
        
        Args:
            first_frame_url: 首帧图片URL（支持公网URL或Base64）
            prompt: 视频描述提示词
            last_frame_url: 尾帧图片URL（可选，如不提供则为单图首帧模式）
            model: 模型名称（默认wan2.2-kf2v-flash）
            resolution: 分辨率档位（480P/720P/1080P）
            
        Returns:
            包含video_url等信息的结果数据
            
        Raises:
            DashScopeApiError: API调用失败
            TaskFailedError: 任务失败
            TaskTimeoutError: 任务超时
        """
        mode = "首尾帧" if last_frame_url else "单图首帧"
        self.logger.info(
            f"开始生成视频（{mode}模式）: model={model}, "
            f"prompt长度={len(prompt)}"
        )
        
        # 创建任务
        task_id = await self._create_task(
            model=model,
            first_frame_url=first_frame_url,
            prompt=prompt,
            last_frame_url=last_frame_url,
            resolution=resolution,
            prompt_extend=True
        )
        
        # 轮询任务结果
        result = await self._poll_task(task_id)
        
        # 转存视频到OSS
        temp_video_url = result.get("video_url")
        if temp_video_url:
            permanent_url = await self._save_video_to_oss(temp_video_url, model)
            result["video_url"] = permanent_url
            result["temp_video_url"] = temp_video_url  # 保留原临时URL供调试
        
        self.logger.info(
            f"视频生成完成: task_id={task_id}, "
            f"video_url={result.get('video_url', 'N/A')}"
        )
        
        return result


# 全局服务实例
wanx_kf2v_service = WanxKf2vService()

