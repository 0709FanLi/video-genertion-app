"""Sora 2 API 视频生成服务.

封装与 Sora 2 API 的交互逻辑，支持：
1. 文生视频（Text-to-Video）
2. 图生视频（Image-to-Video）
3. 流式响应解析（Server-Sent Events）
4. 视频转存到OSS（视频仅保留1天）
"""

import asyncio
import json
import re
import tempfile
import uuid
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import ApiError
from app.services.oss_service import oss_service
from app.utils.retry_decorator import retry_decorator


class SoraService(LoggerMixin):
    """Sora 2 API 视频生成服务类.
    
    使用 Sora 2 API 进行视频生成，支持文生视频和图生视频。
    
    Attributes:
        api_key: Sora API 密钥
        base_url: API 基础URL
        timeout: 请求超时时间（秒）
    """
    
    def __init__(self) -> None:
        """初始化 Sora 服务."""
        self.api_key = settings.sora_api_key
        self.base_url = settings.sora_base_url
        self.timeout = 600  # 视频生成需要3-5分钟，设置10分钟超时
        
        if not self.api_key:
            self.logger.warning("Sora API Key 未配置，Sora 功能将不可用")
        else:
            self.logger.info(
                f"SoraService初始化完成: base_url={self.base_url}, "
                f"api_key={self.api_key[:10]}..."
            )
    
    async def _parse_stream_response(
        self,
        response: httpx.Response
    ) -> Optional[str]:
        """解析 SSE 流式响应，提取视频链接.
        
        Args:
            response: httpx 响应对象（流式）
            
        Returns:
            视频URL，如果未找到则返回None
            
        Raises:
            ApiError: 解析失败或内容审核失败
        """
        video_url = None
        error_message = None
        
        try:
            async for line in response.aiter_lines():
                if not line:
                    continue
                
                # SSE 格式: data: {...} 或 data: [DONE]
                if line.startswith('data: '):
                    data_str = line[6:]  # 移除 'data: ' 前缀
                    
                    if data_str == '[DONE]':
                        break
                    
                    try:
                        data_json = json.loads(data_str)
                        content = data_json.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        
                        if content:
                            # 打印进度信息
                            if '进度' in content or '队列' in content or '成功' in content:
                                self.logger.info(f"Sora生成进度: {content.strip()}")
                            
                            # 检查错误信息
                            if 'error' in content.lower() or '失败' in content or '错误' in content:
                                error_message = content.strip()
                                self.logger.error(f"Sora生成错误: {error_message}")
                            
                            # 提取视频链接
                            if '视频生成成功' in content:
                                # 正则提取 markdown 链接中的 URL
                                match = re.search(r'\[点击这里\]\((https?://[^\)]+)\)', content)
                                if match:
                                    video_url = match.group(1)
                                    self.logger.info(f"提取到视频链接: {video_url[:100]}...")
                    
                    except json.JSONDecodeError:
                        # 忽略无效的JSON行
                        continue
        
        except httpx.ChunkedEncodingError as e:
            error_msg = "连接中断，可能是内容审核未通过"
            self.logger.error(f"{error_msg}: {str(e)}")
            raise ApiError(
                message="视频生成失败",
                detail=f"{error_msg}。请修改提示词，避免真实人物、敏感内容描述"
            )
        
        except Exception as e:
            self.logger.error(f"解析流式响应失败: {str(e)}", exc_info=True)
            raise ApiError(
                message="解析视频生成响应失败",
                detail=str(e)
            )
        
        if error_message:
            raise ApiError(
                message="视频生成失败",
                detail=error_message
            )
        
        if not video_url:
            raise ApiError(
                message="未能获取视频链接",
                detail="视频生成可能失败，请稍后重试"
            )
        
        return video_url
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def _save_video_to_oss(
        self,
        temp_video_url: str,
        model: str
    ) -> str:
        """从临时URL下载视频并上传到OSS.
        
        Args:
            temp_video_url: Sora API返回的临时视频URL（仅保留1天）
            model: 模型名称（用于命名）
            
        Returns:
            OSS永久URL
            
        Raises:
            ApiError: 下载或上传失败
        """
        temp_path = None
        
        try:
            self.logger.info(f"开始下载视频: {temp_video_url[:100]}...")
            
            # 下载视频到临时文件
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(temp_video_url)
                response.raise_for_status()
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    temp_path = tmp_file.name
                    tmp_file.write(response.content)
            
            file_size = len(response.content) / 1024 / 1024
            self.logger.info(f"视频下载成功: {temp_path}, 大小: {file_size:.2f}MB")
            
            # 上传到OSS
            category = "videos"
            filename = f"sora_{model}_{uuid.uuid4().hex[:8]}.mp4"
            
            with open(temp_path, 'rb') as f:
                result = oss_service.upload_file(
                    file_data=f,
                    filename=filename,
                    category=category,
                    content_type="video/mp4"
                )
            
            self.logger.info(f"视频已转存到OSS: {result['url']}")
            
            return result['url']
            
        except httpx.HTTPError as e:
            self.logger.error(f"下载视频失败: {str(e)}")
            raise ApiError(
                message="下载视频失败",
                detail=f"无法从临时URL下载视频: {str(e)}"
            )
        
        except Exception as e:
            self.logger.error(f"转存视频到OSS失败: {str(e)}", exc_info=True)
            raise ApiError(
                message="转存视频失败",
                detail=str(e)
            )
        
        finally:
            # 清理临时文件
            if temp_path:
                try:
                    import os
                    os.unlink(temp_path)
                    self.logger.debug(f"已删除临时文件: {temp_path}")
                except Exception as e:
                    self.logger.warning(f"删除临时文件失败: {str(e)}")
    
    async def generate_text_to_video(
        self,
        prompt: str,
        model: str = "sora_video2",
        duration: int = 10
    ) -> dict[str, Any]:
        """文生视频.
        
        Args:
            prompt: 视频描述提示词
            model: 模型名称（sora_video2 / sora_video2-landscape / sora_video2-15s / sora_video2-landscape-15s）
            duration: 时长（10或15秒，与模型名对应）
            
        Returns:
            包含 video_url (OSS永久链接) 的结果数据
            
        Raises:
            ApiError: API调用失败
        """
        if not self.api_key:
            raise ApiError(
                message="Sora API Key 未配置",
                detail="请在配置文件中设置 SORA_API_KEY"
            )
        
        self.logger.info(
            f"开始文生视频: model={model}, prompt长度={len(prompt)}, duration={duration}s"
        )
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "stream": True,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                # 解析流式响应
                video_url = await self._parse_stream_response(response)
                
                # 转存视频到OSS
                permanent_url = await self._save_video_to_oss(video_url, model)
                
                self.logger.info(f"文生视频完成: video_url={permanent_url}")
                
                return {
                    "video_url": permanent_url,
                    "temp_video_url": video_url,  # 保留原临时URL供调试
                    "model": model,
                    "duration": duration,
                    "prompt": prompt
                }
        
        except httpx.HTTPError as e:
            self.logger.error(f"Sora API请求失败: {str(e)}")
            raise ApiError(
                message="Sora API请求失败",
                detail=str(e)
            )
        
        except ApiError:
            # 重新抛出ApiError
            raise
        
        except Exception as e:
            self.logger.error(f"文生视频失败: {str(e)}", exc_info=True)
            raise ApiError(
                message="文生视频失败",
                detail=str(e)
            )
    
    async def generate_image_to_video(
        self,
        image_url: str,
        prompt: str,
        model: str = "sora_video2",
        duration: int = 10
    ) -> dict[str, Any]:
        """图生视频.
        
        Args:
            image_url: 图片URL（OSS URL 或 Base64 data URI）
            prompt: 视频描述提示词
            model: 模型名称
            duration: 时长（10或15秒）
            
        Returns:
            包含 video_url (OSS永久链接) 的结果数据
            
        Raises:
            ApiError: API调用失败
        """
        if not self.api_key:
            raise ApiError(
                message="Sora API Key 未配置",
                detail="请在配置文件中设置 SORA_API_KEY"
            )
        
        self.logger.info(
            f"开始图生视频: model={model}, prompt长度={len(prompt)}, "
            f"duration={duration}s, image_url={image_url[:100] if len(image_url) > 100 else image_url}..."
        )
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "stream": True,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                # 解析流式响应
                video_url = await self._parse_stream_response(response)
                
                # 转存视频到OSS
                permanent_url = await self._save_video_to_oss(video_url, model)
                
                self.logger.info(f"图生视频完成: video_url={permanent_url}")
                
                return {
                    "video_url": permanent_url,
                    "temp_video_url": video_url,  # 保留原临时URL供调试
                    "model": model,
                    "duration": duration,
                    "prompt": prompt,
                    "image_url": image_url
                }
        
        except httpx.HTTPError as e:
            self.logger.error(f"Sora API请求失败: {str(e)}")
            raise ApiError(
                message="Sora API请求失败",
                detail=str(e)
            )
        
        except ApiError:
            # 重新抛出ApiError
            raise
        
        except Exception as e:
            self.logger.error(f"图生视频失败: {str(e)}", exc_info=True)
            raise ApiError(
                message="图生视频失败",
                detail=str(e)
            )


# 全局服务实例
sora_service = SoraService()

