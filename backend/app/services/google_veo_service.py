"""Google Veo视频生成服务.

封装与Google Veo API的交互逻辑，支持：
1. 视频扩展（Video Extension）
2. 图生视频（Image-to-Video）
"""

import asyncio
import os
import tempfile
from typing import Any, Dict, Optional

import httpx
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import ApiError
from app.services.oss_service import oss_service


class GoogleVeoService(LoggerMixin):
    """Google Veo视频生成服务类.
    
    使用Google Veo 3.1模型进行视频生成。
    
    核心功能：
    1. 视频扩展：基于原始视频生成扩展内容
    2. 图生视频：基于单图或首尾帧生成视频
    3. 异步任务轮询：处理长时间运行的生成任务
    4. 文件管理：上传到Google、下载并转存OSS
    
    Attributes:
        client: Google GenAI客户端
        model: 模型名称
        poll_interval: 轮询间隔（秒）
        max_wait_time: 最大等待时间（秒）
    """
    
    def __init__(self) -> None:
        """初始化Google Veo服务."""
        # 设置环境变量（Google SDK会自动读取）
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
        
        self.client = genai.Client()
        self.model = "veo-3.1-generate-preview"
        self.poll_interval = 10  # 每10秒轮询一次
        self.max_wait_time = 600  # 最多等待10分钟
        
        self.logger.info("GoogleVeoService初始化完成")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def extend_video(
        self,
        video_url: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """扩展视频.
        
        基于原始视频和提示词生成扩展内容。
        
        Args:
            video_url: 原始视频的OSS URL
            prompt: 扩展描述提示词
            aspect_ratio: 视频长宽比，可选"16:9"或"9:16"（默认"16:9"）
            negative_prompt: 反向提示词（可选）
            
        Returns:
            包含扩展视频信息的字典:
            {
                "extended_video_url": str,  # 扩展后视频OSS URL
                "original_video_url": str,  # 原始视频URL
                "prompt": str,
                "duration": int,  # 固定8秒
                "resolution": str,  # 固定720p
                "aspect_ratio": str,
                "model": str
            }
            
        Raises:
            ApiError: API调用失败
        """
        self.logger.info(
            f"开始视频扩展: video_url={video_url[:100]}, "
            f"aspect_ratio={aspect_ratio}, prompt_length={len(prompt)}"
        )
        
        try:
            # 步骤1: 从OSS下载视频到临时文件
            temp_video_path = await self._download_video_from_oss(video_url)
            
            # 步骤2: 上传视频到Google
            google_video = await self._upload_video_to_google(temp_video_path)
            
            # 步骤3: 创建视频扩展任务
            operation = await self._create_extension_task(
                video=google_video,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                negative_prompt=negative_prompt
            )
            
            # 步骤4: 轮询任务状态直到完成
            completed_operation = await self._poll_operation(operation)
            
            # 步骤5: 下载扩展后的视频
            extended_video = completed_operation.response.generated_videos[0]
            extended_video_path = await self._download_video_from_google(
                extended_video.video
            )
            
            # 步骤6: 上传扩展后的视频到OSS
            extended_video_url = await self._upload_video_to_oss(
                extended_video_path,
                aspect_ratio
            )
            
            # 步骤7: 清理临时文件
            self._cleanup_temp_files([temp_video_path, extended_video_path])
            
            # 构建返回结果
            result = {
                "extended_video_url": extended_video_url,
                "original_video_url": video_url,
                "prompt": prompt,
                "duration": 8,  # Veo 3.1扩展固定8秒
                "resolution": "720p",  # 扩展固定720p
                "aspect_ratio": aspect_ratio,
                "model": self.model
            }
            
            self.logger.info(
                f"视频扩展成功: extended_url={extended_video_url[:100]}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"视频扩展失败: {str(e)}")
            raise ApiError(
                message="视频扩展失败",
                details=str(e)
            )
    
    async def _download_video_from_oss(self, oss_url: str) -> str:
        """从OSS下载视频到本地临时文件.
        
        Args:
            oss_url: OSS视频URL
            
        Returns:
            临时文件路径
            
        Raises:
            ApiError: 下载失败
        """
        try:
            self.logger.info(f"从OSS下载视频: {oss_url[:100]}")
            
            # 创建临时文件
            temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(temp_fd)
            
            # 下载视频
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.get(oss_url)
                response.raise_for_status()
                
                with open(temp_path, "wb") as f:
                    f.write(response.content)
            
            file_size = os.path.getsize(temp_path)
            self.logger.info(
                f"视频下载成功: {temp_path}, 大小: {file_size / 1024 / 1024:.2f}MB"
            )
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"从OSS下载视频失败: {str(e)}")
            raise ApiError("从OSS下载视频失败", detail=str(e))
    
    async def _upload_video_to_google(self, video_path: str) -> types.File:
        """上传视频到Google.
        
        Args:
            video_path: 本地视频文件路径
            
        Returns:
            Google File对象
            
        Raises:
            ApiError: 上传失败
        """
        try:
            self.logger.info(f"上传视频到Google: {video_path}")
            
            # 在线程池中运行同步操作
            loop = asyncio.get_event_loop()
            google_file = await loop.run_in_executor(
                None,
                lambda: self.client.files.upload(path=video_path)
            )
            
            self.logger.info(f"视频上传Google成功: {google_file.name}")
            
            return google_file
            
        except Exception as e:
            self.logger.error(f"上传视频到Google失败: {str(e)}")
            raise ApiError("上传视频到Google失败", detail=str(e))
    
    async def _create_extension_task(
        self,
        video: types.File,
        prompt: str,
        aspect_ratio: str,
        negative_prompt: Optional[str]
    ) -> types.GenerateVideosOperation:
        """创建视频扩展任务.
        
        Args:
            video: Google视频对象
            prompt: 扩展提示词
            aspect_ratio: 长宽比
            negative_prompt: 反向提示词
            
        Returns:
            异步操作对象
            
        Raises:
            ApiError: 创建任务失败
        """
        try:
            self.logger.info(f"创建视频扩展任务: aspect_ratio={aspect_ratio}")
            
            # 构建配置
            config = types.GenerateVideosConfig(
                number_of_videos=1,
                resolution="720p",
                aspect_ratio=aspect_ratio,
                duration_seconds=8
            )
            
            # 添加反向提示词（如果提供）
            if negative_prompt:
                config.negative_prompt = negative_prompt
            
            # 创建任务（在线程池中运行）
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_videos(
                    model=self.model,
                    video=video,
                    prompt=prompt,
                    config=config
                )
            )
            
            self.logger.info(f"任务创建成功: operation.name={operation.name}")
            
            return operation
            
        except Exception as e:
            self.logger.error(f"创建视频扩展任务失败: {str(e)}")
            raise ApiError("创建视频扩展任务失败", detail=str(e))
    
    async def _poll_operation(
        self,
        operation: types.GenerateVideosOperation
    ) -> types.GenerateVideosOperation:
        """轮询任务状态直到完成.
        
        Args:
            operation: 异步操作对象
            
        Returns:
            完成后的操作对象
            
        Raises:
            ApiError: 任务失败或超时
        """
        self.logger.info(f"开始轮询任务状态: {operation.name}")
        
        elapsed_time = 0
        
        while not operation.done:
            if elapsed_time >= self.max_wait_time:
                raise ApiError(
                    "视频扩展超时",
                    details=f"等待超过{self.max_wait_time}秒"
                )
            
            self.logger.info(
                f"任务进行中... 已等待{elapsed_time}秒 "
                f"(最多{self.max_wait_time}秒)"
            )
            
            await asyncio.sleep(self.poll_interval)
            elapsed_time += self.poll_interval
            
            # 刷新操作状态（在线程池中运行）
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.operations.get(operation)
            )
        
        self.logger.info(f"任务完成: 总耗时{elapsed_time}秒")
        
        return operation
    
    async def _download_video_from_google(
        self,
        google_video: types.File
    ) -> str:
        """从Google下载视频到本地.
        
        Args:
            google_video: Google视频对象
            
        Returns:
            本地临时文件路径
            
        Raises:
            ApiError: 下载失败
        """
        try:
            # 尝试获取视频标识信息
            video_id = getattr(google_video, 'name', None) or getattr(google_video, 'uri', 'unknown')
            self.logger.info(f"从Google下载视频: {video_id}")
            
            # 创建临时文件
            temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(temp_fd)
            
            # 根据官方文档：先下载再保存
            # client.files.download(file=generated_video.video)
            # generated_video.video.save("parameters_example.mp4")
            loop = asyncio.get_event_loop()
            
            # 先调用 download 获取数据
            await loop.run_in_executor(
                None,
                lambda: self.client.files.download(file=google_video)
            )
            
            # 再调用 save 保存到文件
            await loop.run_in_executor(
                None,
                lambda: google_video.save(temp_path)
            )
            
            file_size = os.path.getsize(temp_path)
            self.logger.info(
                f"视频下载成功: {temp_path}, "
                f"大小: {file_size / 1024 / 1024:.2f}MB"
            )
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"从Google下载视频失败: {str(e)}")
            raise ApiError("从Google下载视频失败", detail=str(e))
    
    async def _upload_video_to_oss(
        self,
        video_path: str,
        aspect_ratio: str
    ) -> str:
        """上传视频到OSS.
        
        Args:
            video_path: 本地视频文件路径
            aspect_ratio: 视频长宽比（用于文件命名）
            
        Returns:
            OSS视频URL
            
        Raises:
            ApiError: 上传失败
        """
        try:
            self.logger.info(f"上传视频到OSS: {video_path}")
            
            # 生成文件名
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ratio_tag = aspect_ratio.replace(":", "x")  # 16:9 -> 16x9
            filename = f"veo_extended_{ratio_tag}_{timestamp}.mp4"
            
            # 读取视频文件
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            
            # 上传到OSS
            oss_result = await oss_service.upload_file(
                file_bytes=video_bytes,
                filename=filename,
                content_type="video/mp4",
                category="videos"
            )
            
            oss_url = oss_result["url"]
            self.logger.info(
                f"视频上传OSS成功: {filename}, "
                f"大小: {oss_result['size'] / 1024 / 1024:.2f}MB, "
                f"URL: {oss_url[:100]}"
            )
            
            return oss_url
            
        except Exception as e:
            self.logger.error(f"上传视频到OSS失败: {str(e)}")
            raise ApiError("上传视频到OSS失败", detail=str(e))
    
    def _cleanup_temp_files(self, file_paths: list[str]) -> None:
        """清理临时文件.
        
        Args:
            file_paths: 临时文件路径列表
        """
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    self.logger.info(f"临时文件已清理: {path}")
            except Exception as e:
                self.logger.warning(f"清理临时文件失败: {path}, 错误: {e}")
    
    async def _base64_to_google_file(self, image_base64: str) -> types.File:
        """将Base64图片转换为Google File对象.
        
        Args:
            image_base64: Base64编码的图片 (格式: data:image/{type};base64,{data})
            
        Returns:
            Google File对象
            
        Raises:
            ApiError: 转换失败
        """
        try:
            import base64
            
            self.logger.info("转换Base64图片到Google File...")
            
            # 解析Base64数据
            if "base64," in image_base64:
                base64_data = image_base64.split("base64,")[1]
            else:
                base64_data = image_base64
            
            # 解码
            image_bytes = base64.b64decode(base64_data)
            
            # 创建临时文件
            temp_fd, temp_path = tempfile.mkstemp(suffix=".png")
            os.close(temp_fd)
            
            with open(temp_path, "wb") as f:
                f.write(image_bytes)
            
            self.logger.info(f"Base64图片已保存到临时文件: {temp_path}")
            
            # 上传到Google
            loop = asyncio.get_event_loop()
            google_file = await loop.run_in_executor(
                None,
                lambda: self.client.files.upload(path=temp_path)
            )
            
            # 清理临时文件
            os.remove(temp_path)
            
            self.logger.info(f"图片已上传到Google: {google_file.name}")
            
            return google_file
            
        except Exception as e:
            self.logger.error(f"Base64图片转换失败: {str(e)}")
            raise ApiError("Base64图片转换失败", detail=str(e))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_text_to_video(
        self,
        prompt: str,
        duration: int = 6,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """文生视频（纯文本）.
        
        仅基于文本提示词生成视频，无需图片输入。
        
        Args:
            prompt: 视频描述提示词
            duration: 视频时长（4/6/8秒），默认6秒
            resolution: 分辨率（720p/1080p），默认720p
            aspect_ratio: 长宽比（16:9/9:16），默认16:9
            negative_prompt: 反向提示词（可选）
            
        Returns:
            包含生成视频信息的字典（同单图首帧）
            
        Raises:
            ApiError: API调用失败
        """
        self.logger.info(
            f"开始文生视频: duration={duration}s, "
            f"resolution={resolution}, aspect_ratio={aspect_ratio}"
        )
        
        try:
            # 构建配置
            config = types.GenerateVideosConfig(
                number_of_videos=1,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                duration_seconds=duration
            )
            
            if negative_prompt:
                config.negative_prompt = negative_prompt
            
            # 创建任务（纯文本，无图片）
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_videos(
                    model=self.model,
                    prompt=prompt,
                    config=config
                )
            )
            
            self.logger.info(f"文生视频任务创建成功: operation.name={operation.name}")
            
            # 轮询任务
            operation = await self._poll_operation(operation)
            
            # 下载视频
            generated_video = operation.response.generated_videos[0]
            video_path = await self._download_video_from_google(generated_video.video)
            
            # 上传到OSS
            video_url = await self._upload_video_to_oss(video_path, aspect_ratio)
            
            # 清理
            self._cleanup_temp_files([video_path])
            
            result = {
                "video_url": video_url,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "model": self.model
            }
            
            self.logger.info(f"文生视频成功: {video_url[:100]}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"文生视频失败: {str(e)}")
            raise ApiError("文生视频失败", detail=str(e))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_image_to_video_first(
        self,
        image_base64: str,
        prompt: str,
        duration: int = 6,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """单图首帧生成视频.
        
        基于单张图片作为首帧生成视频。
        
        Args:
            image_base64: 图片Base64编码
            prompt: 视频描述提示词
            duration: 视频时长（4/6/8秒），默认6秒
            resolution: 分辨率（720p/1080p），默认720p
            aspect_ratio: 长宽比（16:9/9:16），默认16:9
            negative_prompt: 反向提示词（可选）
            
        Returns:
            包含生成视频信息的字典:
            {
                "video_url": str,  # 生成视频OSS URL
                "prompt": str,
                "duration": int,
                "resolution": str,
                "aspect_ratio": str,
                "model": str
            }
            
        Raises:
            ApiError: API调用失败
        """
        self.logger.info(
            f"开始单图首帧生成视频: duration={duration}s, "
            f"resolution={resolution}, aspect_ratio={aspect_ratio}"
        )
        
        try:
            # 步骤1: Base64转Google File
            google_image = await self._base64_to_google_file(image_base64)
            
            # 步骤2: 构建配置
            config = types.GenerateVideosConfig(
                number_of_videos=1,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                duration_seconds=duration
            )
            
            if negative_prompt:
                config.negative_prompt = negative_prompt
            
            # 步骤3: 创建任务
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_videos(
                    model=self.model,
                    prompt=prompt,
                    image=google_image,
                    config=config
                )
            )
            
            self.logger.info(f"任务创建成功: operation.name={operation.name}")
            
            # 步骤4: 轮询任务
            operation = await self._poll_operation(operation)
            
            # 步骤5: 下载视频
            generated_video = operation.response.generated_videos[0]
            video_path = await self._download_video_from_google(generated_video.video)
            
            # 步骤6: 上传到OSS
            video_url = await self._upload_video_to_oss(video_path, aspect_ratio)
            
            # 步骤7: 清理
            self._cleanup_temp_files([video_path])
            
            result = {
                "video_url": video_url,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "model": self.model
            }
            
            self.logger.info(f"单图首帧生成成功: {video_url[:100]}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"单图首帧生成失败: {str(e)}")
            raise ApiError("单图首帧生成失败", detail=str(e))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_image_to_video_first_tail(
        self,
        first_image_base64: str,
        last_image_base64: str,
        prompt: str,
        duration: int = 8,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """首尾帧插值生成视频.
        
        基于首帧和尾帧生成中间过渡视频。
        
        Args:
            first_image_base64: 首帧图片Base64编码
            last_image_base64: 尾帧图片Base64编码
            prompt: 视频描述提示词
            duration: 视频时长（4/6/8秒），默认8秒
            resolution: 分辨率（720p/1080p），默认720p
            aspect_ratio: 长宽比（16:9/9:16），默认16:9
            negative_prompt: 反向提示词（可选）
            
        Returns:
            包含生成视频信息的字典（同单图首帧）
            
        Raises:
            ApiError: API调用失败
        """
        self.logger.info(
            f"开始首尾帧插值生成视频: duration={duration}s, "
            f"resolution={resolution}, aspect_ratio={aspect_ratio}"
        )
        
        try:
            # 步骤1: 转换两张图片
            google_first_image = await self._base64_to_google_file(first_image_base64)
            google_last_image = await self._base64_to_google_file(last_image_base64)
            
            # 步骤2: 构建配置
            config = types.GenerateVideosConfig(
                number_of_videos=1,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                duration_seconds=duration,
                last_frame=google_last_image
            )
            
            if negative_prompt:
                config.negative_prompt = negative_prompt
            
            # 步骤3: 创建任务
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_videos(
                    model=self.model,
                    prompt=prompt,
                    image=google_first_image,
                    config=config
                )
            )
            
            self.logger.info(f"首尾帧任务创建成功: operation.name={operation.name}")
            
            # 步骤4: 轮询任务
            operation = await self._poll_operation(operation)
            
            # 步骤5: 下载视频
            generated_video = operation.response.generated_videos[0]
            video_path = await self._download_video_from_google(generated_video.video)
            
            # 步骤6: 上传到OSS
            video_url = await self._upload_video_to_oss(video_path, aspect_ratio)
            
            # 步骤7: 清理
            self._cleanup_temp_files([video_path])
            
            result = {
                "video_url": video_url,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "model": self.model
            }
            
            self.logger.info(f"首尾帧插值生成成功: {video_url[:100]}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"首尾帧插值生成失败: {str(e)}")
            raise ApiError("首尾帧插值生成失败", detail=str(e))


# 全局服务实例
google_veo_service = GoogleVeoService()

