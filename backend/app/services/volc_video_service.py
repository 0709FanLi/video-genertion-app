"""火山引擎即梦视频生成服务.

封装与火山引擎即梦视频生成API的交互逻辑。
支持文生视频、图生视频（首帧）、图生视频（首尾帧）。
"""

import asyncio
import base64
import hashlib
import hmac
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

import httpx

from app.core.config import settings
from app.core.logging import LoggerMixin
from app.exceptions import ApiError
from app.services.oss_service import oss_service
from app.utils.retry_decorator import retry_decorator


class VolcVideoService(LoggerMixin):
    """火山引擎即梦视频生成服务类.
    
    支持三种模式：
    1. 文生视频：jimeng_t2v_v30_1080p
    2. 图生视频（首帧）：jimeng_i2v_first_v30
    3. 图生视频（首尾帧）：jimeng_i2v_first_tail_v30
    4. 图文生视频（Pro）：jimeng_ti2v_v30_pro
    
    Attributes:
        base_url: API基础URL
        access_key_id: 访问密钥ID
        secret_access_key: 访问密钥Secret
        timeout: 请求超时时间
    """
    
    SERVICE_NAME = "cv"
    API_VERSION = "2022-08-31"
    REGION = "cn-north-1"
    
    def __init__(self) -> None:
        """初始化火山引擎视频服务."""
        self.access_key_id = settings.volc_access_key_id
        # Secret Key 直接使用原始值（根据官方文档和调试记录，不需要 Base64 解码）
        self.secret_access_key = settings.volc_secret_access_key
        self.base_url = settings.volc_base_url
        self.timeout = settings.request_timeout
        self.poll_interval = 5  # 视频生成轮询间隔（秒）
        self.max_poll_attempts = 360  # 最多轮询30分钟
        
        self.logger.info(
            f"火山引擎视频服务初始化: access_key_id={self.access_key_id[:10]}..."
        )
    
    def _generate_signature(
        self,
        method: str,
        uri: str,
        query_params: Dict[str, str],
        headers: Dict[str, str],
        body: str,
        timestamp: str
    ) -> str:
        """生成AWS Signature V4签名.
        
        Args:
            method: HTTP方法
            uri: 请求URI
            query_params: Query参数字典
            headers: 请求头字典
            body: 请求体
            timestamp: ISO 8601格式时间戳
            
        Returns:
            签名字符串
        """
        # 1. 构建CanonicalRequest
        canonical_headers = "\n".join([
            f"{k.lower()}:{v}" for k, v in sorted(headers.items())
        ])
        signed_headers = ";".join([k.lower() for k in sorted(headers.keys())])
        
        canonical_query = "&".join([
            f"{quote(k, safe='')}={quote(str(v), safe='')}"
            for k, v in sorted(query_params.items())
        ])
        
        hashed_payload = hashlib.sha256(body.encode('utf-8')).hexdigest()
        
        canonical_request = "\n".join([
            method,
            uri,
            canonical_query,
            canonical_headers,
            "",
            signed_headers,
            hashed_payload
        ])
        
        # 2. 构建StringToSign
        hashed_canonical_request = hashlib.sha256(
            canonical_request.encode('utf-8')
        ).hexdigest()
        
        credential_scope = f"{timestamp[:8]}/cn-north-1/{self.SERVICE_NAME}/request"
        
        string_to_sign = "\n".join([
            "HMAC-SHA256",
            timestamp,
            credential_scope,
            hashed_canonical_request
        ])
        
        # 3. 计算签名（按照官方示例，直接使用secret_key）
        k_date = hmac.new(
            self.secret_access_key.encode('utf-8'),
            timestamp[:8].encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        k_region = hmac.new(
            k_date,
            "cn-north-1".encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        k_service = hmac.new(
            k_region,
            self.SERVICE_NAME.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        k_signing = hmac.new(
            k_service,
            "request".encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        signature = hmac.new(
            k_signing,
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _build_auth_headers(
        self,
        method: str,
        uri: str,
        query_params: Dict[str, str],
        body: str
    ) -> Dict[str, str]:
        """构建包含签名的请求头.
        
        Args:
            method: HTTP方法
            uri: 请求URI
            query_params: Query参数字典
            body: 请求体
            
        Returns:
            包含签名的请求头字典
        """
        # 生成时间戳
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        # 计算payload hash
        payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
        
        # 构建headers
        headers = {
            "Content-Type": "application/json",
            "Host": "visual.volcengineapi.com",
            "X-Date": timestamp,
            "X-Content-Sha256": payload_hash
        }
        
        # 生成签名
        signature = self._generate_signature(
            method, uri, query_params, headers, body, timestamp
        )
        
        # 构建Authorization（格式必须与 volc_jimeng_service 一致）
        credential_scope = f"{timestamp[:8]}/cn-north-1/{self.SERVICE_NAME}/request"
        signed_headers = "content-type;host;x-content-sha256;x-date"
        
        authorization = (
            f"HMAC-SHA256 "
            f"Credential={self.access_key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        headers["Authorization"] = authorization
        
        return headers
    
    @retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
    async def _submit_task(
        self,
        req_key: str,
        prompt: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        frames: int = 121,
        aspect_ratio: str = "16:9"
    ) -> str:
        """提交视频生成任务.
        
        Args:
            req_key: 服务标识（jimeng_t2v_v30_1080p / jimeng_i2v_first_v30 / 
                     jimeng_i2v_first_tail_v30 / jimeng_ti2v_v30_pro）
            prompt: 提示词（文生视频必需，图生视频可选）
            image_urls: 图片URL列表（图生视频必需）
            frames: 总帧数（121=5秒, 241=10秒）
            aspect_ratio: 长宽比（文生视频场景使用）
            
        Returns:
            任务ID
            
        Raises:
            ApiError: API调用失败
        """
        uri = "/"
        query_params = {
            "Action": "CVSync2AsyncSubmitTask",
            "Version": self.API_VERSION
        }
        
        # 构建请求体
        body_dict: Dict[str, Any] = {
            "req_key": req_key,
            "seed": -1,
            "frames": frames
        }
        
        # 添加prompt（如果提供）
        if prompt:
            body_dict["prompt"] = prompt
        
        # 添加图片URLs（如果提供）
        if image_urls and len(image_urls) > 0:
            body_dict["image_urls"] = image_urls
        
        # 文生视频场景添加aspect_ratio
        if req_key in ["jimeng_t2v_v30_1080p"] and not image_urls:
            body_dict["aspect_ratio"] = aspect_ratio
        
        body = json.dumps(body_dict)
        
        self.logger.info(
            f"提交视频生成任务: req_key={req_key}, frames={frames}, "
            f"has_images={bool(image_urls)}, prompt长度={len(prompt) if prompt else 0}"
        )
        
        # 记录请求体内容（用于调试）
        self.logger.debug(f"请求体内容: {body}")
        
        # 构建请求头
        headers = self._build_auth_headers("POST", uri, query_params, body)
        
        # 使用与volc_jimeng_service完全相同的方式发送请求
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"{self.base_url}{uri}"
                
                # 记录请求详情（用于调试）
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"查询参数: {query_params}")
                self.logger.info(f"请求头Authorization: {headers.get('Authorization', '')[:100]}...")
                self.logger.info(f"请求头X-Date: {headers.get('X-Date', '')}")
                self.logger.info(f"请求头X-Content-Sha256: {headers.get('X-Content-Sha256', '')}")
                self.logger.info(f"请求体: {body}")
                
                response = await client.post(
                    url,
                    params=query_params,
                    headers=headers,
                    content=body
                )
                
                # 记录响应状态
                self.logger.debug(f"响应状态码: {response.status_code}")
                self.logger.debug(f"响应头: {dict(response.headers)}")
                
                response.raise_for_status()
                data = response.json()
                
                if data.get("code") != 10000:
                    error_msg = data.get("message", "未知错误")
                    error_code = data.get("code")
                    self.logger.error(
                        f"提交任务失败: code={error_code}, message={error_msg}, "
                        f"详情: {data}"
                    )
                    raise ApiError(
                        f"提交任务失败: {error_msg}",
                        details=str(data)
                    )
                
                task_id = data["data"]["task_id"]
                self.logger.info(f"任务提交成功: task_id={task_id}")
                return task_id
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                error_status = e.response.status_code
                self.logger.error(
                    f"火山即梦请求失败: status={error_status}, "
                    f"detail={error_detail}"
                )
                # 尝试解析错误响应
                try:
                    error_json = e.response.json()
                    error_code = error_json.get("code") or error_json.get("ResponseMetadata", {}).get("Error", {}).get("Code")
                    error_message = error_json.get("message") or error_json.get("ResponseMetadata", {}).get("Error", {}).get("Message")
                    if error_code == 50400 and "Access Denied" in str(error_message):
                        raise ApiError(
                            "火山即梦认证失败: Access Denied。请检查：\n"
                            "1. API Key 和 Secret Key 是否正确\n"
                            "2. 账号是否有视频生成权限\n"
                            "3. API Key 是否已启用",
                            detail=error_detail
                        )
                except:
                    pass
                raise ApiError("火山即梦请求失败", detail=error_detail)
            except Exception as e:
                self.logger.error(f"提交任务异常: {str(e)}")
                raise
    
    async def _get_task_result(self, req_key: str, task_id: str) -> dict[str, Any]:
        """查询任务结果.
        
        Args:
            req_key: 服务标识
            task_id: 任务ID
            
        Returns:
            任务结果数据
            
        Raises:
            ApiError: API调用失败
        """
        uri = "/"
        query_params = {
            "Action": "CVSync2AsyncGetResult",
            "Version": self.API_VERSION
        }
        
        body_dict = {
            "req_key": req_key,
            "task_id": task_id,
            "req_json": json.dumps({"return_url": True})
        }
        body = json.dumps(body_dict)
        
        headers = self._build_auth_headers("POST", uri, query_params, body)
        
        # 使用与volc_jimeng_service完全相同的方式发送请求
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"{self.base_url}{uri}"
                response = await client.post(
                    url,
                    params=query_params,
                    headers=headers,
                    content=body
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("code") != 10000:
                    error_msg = data.get("message", "未知错误")
                    raise ApiError(f"查询任务失败: {error_msg}", detail=str(data))
                
                return data["data"]
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                self.logger.error(f"查询任务失败: {error_detail}")
                raise ApiError("查询任务失败", detail=error_detail)
    
    async def _poll_task_result(self, req_key: str, task_id: str) -> dict[str, Any]:
        """轮询任务结果直到完成.
        
        Args:
            req_key: 服务标识
            task_id: 任务ID
            
        Returns:
            任务结果数据
            
        Raises:
            ApiError: 任务失败或超时
        """
        attempts = 0
        
        self.logger.info(f"开始轮询任务: task_id={task_id}")
        
        while attempts < self.max_poll_attempts:
            result = await self._get_task_result(req_key, task_id)
            status = result.get("status")
            
            self.logger.debug(f"任务状态: {status}, 尝试次数: {attempts + 1}")
            
            if status == "done":
                video_url = result.get("video_url")
                if not video_url:
                    raise ApiError("任务完成但未返回视频URL", detail=str(result))
                
                self.logger.info(f"任务完成: task_id={task_id}")
                return result
            
            elif status in ["not_found", "expired"]:
                raise ApiError(
                    f"任务{status}: task_id={task_id}",
                    details=str(result)
                )
            
            # in_queue 或 generating 状态，继续等待
            await asyncio.sleep(self.poll_interval)
            attempts += 1
        
        raise ApiError(
            f"任务超时: 轮询{self.max_poll_attempts}次后仍未完成",
            details=f"task_id={task_id}"
        )
    
    async def _save_video_to_oss(
        self,
        temp_video_url: str,
        video_type: str
    ) -> str:
        """将临时视频URL转存到OSS并返回永久URL.
        
        Args:
            temp_video_url: 火山引擎返回的临时视频URL（1小时有效期）
            video_type: 视频类型（t2v/i2v-first/i2v-first-tail）
            
        Returns:
            OSS永久视频URL
            
        Raises:
            ApiError: 转存失败
        """
        try:
            self.logger.info(f"开始转存视频到OSS: video_type={video_type}")
            
            # 生成文件名（带时间戳和类型标识）
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"volc_{video_type}_{timestamp}.mp4"
            
            # 从临时URL下载并上传到OSS
            oss_result = await oss_service.upload_from_url(
                url=temp_video_url,
                filename=filename,
                category="videos"  # 存储在videos目录下
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
            self.logger.warning("使用临时URL作为降级方案（1小时有效期）")
            return temp_video_url
    
    async def generate_text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9"
    ) -> dict[str, Any]:
        """文生视频.
        
        Args:
            prompt: 视频描述提示词（建议400字以内）
            duration: 时长（秒），5或10
            aspect_ratio: 长宽比（16:9, 4:3, 1:1, 3:4, 9:16, 21:9）
            
        Returns:
            包含video_url的结果数据（video_url已转存为OSS永久链接）
            
        Raises:
            ApiError: API调用失败
        """
        frames = 121 if duration == 5 else 241
        
        self.logger.info(
            f"文生视频: prompt长度={len(prompt)}, "
            f"duration={duration}s, aspect_ratio={aspect_ratio}"
        )
        
        task_id = await self._submit_task(
            req_key="jimeng_t2v_v30_1080p",
            prompt=prompt,
            frames=frames,
            aspect_ratio=aspect_ratio
        )
        
        result = await self._poll_task_result("jimeng_t2v_v30_1080p", task_id)
        
        # 转存视频到OSS
        temp_video_url = result.get("video_url")
        if temp_video_url:
            permanent_url = await self._save_video_to_oss(temp_video_url, "t2v")
            result["video_url"] = permanent_url
            result["temp_video_url"] = temp_video_url  # 保留原临时URL供调试
        
        return result
    
    async def generate_image_to_video_first(
        self,
        image_url: str,
        prompt: str,
        duration: int = 5
    ) -> dict[str, Any]:
        """图生视频（首帧模式）.
        
        Args:
            image_url: 首帧图片URL
            prompt: 视频描述提示词
            duration: 时长（秒），5或10
            
        Returns:
            包含video_url的结果数据（video_url已转存为OSS永久链接）
            
        Raises:
            ApiError: API调用失败
        """
        frames = 121 if duration == 5 else 241
        
        self.logger.info(
            f"图生视频（首帧）: prompt长度={len(prompt)}, duration={duration}s"
        )
        
        task_id = await self._submit_task(
            req_key="jimeng_i2v_first_v30",
            prompt=prompt,
            image_urls=[image_url],
            frames=frames
        )
        
        result = await self._poll_task_result("jimeng_i2v_first_v30", task_id)
        
        # 转存视频到OSS
        temp_video_url = result.get("video_url")
        if temp_video_url:
            permanent_url = await self._save_video_to_oss(temp_video_url, "i2v-first")
            result["video_url"] = permanent_url
            result["temp_video_url"] = temp_video_url
        
        return result
    
    async def generate_image_to_video_first_tail(
        self,
        first_image_url: str,
        last_image_url: str,
        prompt: str,
        duration: int = 5
    ) -> dict[str, Any]:
        """图生视频（首尾帧模式）.
        
        Args:
            first_image_url: 首帧图片URL
            last_image_url: 尾帧图片URL
            prompt: 视频描述提示词
            duration: 时长（秒），5或10
            
        Returns:
            包含video_url的结果数据（video_url已转存为OSS永久链接）
            
        Raises:
            ApiError: API调用失败
        """
        frames = 121 if duration == 5 else 241
        
        self.logger.info(
            f"图生视频（首尾帧）: prompt长度={len(prompt)}, duration={duration}s"
        )
        
        task_id = await self._submit_task(
            req_key="jimeng_i2v_first_tail_v30",
            prompt=prompt,
            image_urls=[first_image_url, last_image_url],
            frames=frames
        )
        
        result = await self._poll_task_result(
            "jimeng_i2v_first_tail_v30", 
            task_id
        )
        
        # 转存视频到OSS
        temp_video_url = result.get("video_url")
        if temp_video_url:
            permanent_url = await self._save_video_to_oss(temp_video_url, "i2v-first-tail")
            result["video_url"] = permanent_url
            result["temp_video_url"] = temp_video_url
        
        return result


# 全局服务实例
volc_video_service = VolcVideoService()

