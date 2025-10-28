"""火山引擎即梦API服务.

提供文本生成图片的功能，使用火山引擎的图像生成API。
参考文档: https://www.volcengine.com/docs/85621/1817045
"""

import asyncio
import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.custom_exceptions import ApiError

logger = get_logger(__name__)


class VolcJiMengService:
    """火山引擎即梦服务类.
    
    封装火山引擎的文生图API调用逻辑。
    
    Attributes:
        access_key_id: 火山引擎AccessKeyId
        secret_access_key: 火山引擎SecretAccessKey
        base_url: API基础URL
        timeout: 请求超时时间
    """
    
    SERVICE_NAME = "cv"
    API_VERSION = "2022-08-31"
    
    def __init__(self) -> None:
        """初始化火山引擎服务."""
        self.access_key_id = settings.volc_access_key_id
        self.secret_access_key = settings.volc_secret_access_key
        self.base_url = settings.volc_base_url
        self.timeout = settings.request_timeout
        
        # 解码SecretAccessKey (base64编码)
        try:
            self.secret_access_key = base64.b64decode(
                self.secret_access_key
            ).decode('utf-8')
        except Exception as e:
            logger.warning(f"SecretAccessKey解码失败,使用原始值: {e}")
    
    def _generate_signature(
        self,
        method: str,
        uri: str,
        query_params: Dict[str, str],
        headers: Dict[str, str],
        body: str,
        timestamp: str
    ) -> str:
        """生成火山引擎API签名.
        
        Args:
            method: HTTP方法
            uri: 请求URI
            query_params: 查询参数
            headers: 请求头
            body: 请求体
            timestamp: 时间戳
            
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
        
        # 3. 计算签名
        k_date = hmac.new(
            f"VOLC{self.secret_access_key}".encode('utf-8'),
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
        """构建认证请求头.
        
        Args:
            method: HTTP方法
            uri: 请求URI
            query_params: 查询参数
            body: 请求体
            
        Returns:
            包含认证信息的请求头
        """
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        headers = {
            "Content-Type": "application/json",
            "Host": "visual.volcengineapi.com",
            "X-Date": timestamp
        }
        
        signature = self._generate_signature(
            method, uri, query_params, headers, body, timestamp
        )
        
        credential_scope = f"{timestamp[:8]}/cn-north-1/{self.SERVICE_NAME}/request"
        signed_headers = ";".join([k.lower() for k in sorted(headers.keys())])
        
        authorization = (
            f"HMAC-SHA256 "
            f"Credential={self.access_key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        headers["Authorization"] = authorization
        
        return headers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_image(
        self,
        prompt: str,
        model: str = "jimeng_t2i_v40",
        size: str = "1024x1024",
        num_images: int = 1,
        reference_image_urls: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[str]:
        """生成图片（即梦4.0）.
        
        Args:
            prompt: 提示词（最长800字符）
            model: 模型名称（固定为jimeng_t2i_v40）
            size: 图片尺寸
            num_images: 生成图片数量（通过force_single控制）
            reference_image_urls: 参考图URL列表（支持0-6张）
            **kwargs: 其他参数
            
        Returns:
            图片URL列表
            
        Raises:
            ApiError: API调用失败
        """
        logger.info(
            f"火山即梦4.0生成图片: prompt={prompt[:50]}..., "
            f"model={model}, size={size}, num={num_images}, "
            f"ref_images={len(reference_image_urls) if reference_image_urls else 0}"
        )
        
        # 构建请求（异步任务提交）
        uri = "/"
        query_params = {
            "Action": "CVSync2AsyncSubmitTask",
            "Version": self.API_VERSION
        }
        
        body_dict = {
            "req_key": "jimeng_t2i_v40",
            "prompt": prompt,
            "force_single": num_images == 1,  # 强制单图输出
        }
        
        # 添加参考图（如果提供）
        # 根据即梦4.0文档，参考图使用image_urls字段传递URL数组（支持0-6张）
        if reference_image_urls and len(reference_image_urls) > 0:
            # 限制最多6张
            body_dict["image_urls"] = reference_image_urls[:6]
            logger.info(f"使用{len(body_dict['image_urls'])}张参考图")
        
        # 解析尺寸
        if "x" in size:
            width, height = size.split("x")
            body_dict["width"] = int(width)
            body_dict["height"] = int(height)
        
        body = json.dumps(body_dict)
        
        # 构建认证头
        headers = self._build_auth_headers("POST", uri, query_params, body)
        
        # 发送请求（异步任务模式）
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{uri}"
                
                # 步骤1：提交任务
                response = await client.post(
                    url,
                    params=query_params,
                    headers=headers,
                    content=body
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"火山即梦提交任务响应: {result}")
                
                # 检查提交状态
                if result.get("code") != 10000:
                    error_msg = result.get("message", "未知错误")
                    logger.error(f"火山即梦提交任务失败: {error_msg}")
                    raise ApiError(
                        message="火山即梦提交任务失败",
                        detail=error_msg
                    )
                
                # 获取task_id
                task_id = result.get("data", {}).get("task_id")
                if not task_id:
                    raise ApiError(
                        message="火山即梦未返回task_id",
                        detail="提交任务成功但未返回task_id"
                    )
                
                logger.info(f"火山即梦任务已提交，task_id: {task_id}")
                
                # 步骤2：轮询查询结果
                query_params = {
                    "Action": "CVSync2AsyncGetResult",
                    "Version": self.API_VERSION
                }
                
                query_body_dict = {
                    "req_key": "jimeng_t2i_v40",
                    "task_id": task_id,
                    "req_json": json.dumps({"return_url": True})
                }
                
                query_body = json.dumps(query_body_dict)
                query_headers = self._build_auth_headers("POST", uri, query_params, query_body)
                
                # 轮询查询（最多30次，每次等待2秒）
                max_retries = 30
                for i in range(max_retries):
                    await asyncio.sleep(2)  # 等待2秒
                    
                    query_response = await client.post(
                        url,
                        params=query_params,
                        headers=query_headers,
                        content=query_body
                    )
                    
                    query_response.raise_for_status()
                    query_result = query_response.json()
                    
                    status = query_result.get("data", {}).get("status")
                    logger.info(f"火山即梦任务状态 ({i+1}/{max_retries}): {status}")
                    
                    if status == "done":
                        # 任务完成
                        if query_result.get("code") != 10000:
                            error_msg = query_result.get("message", "未知错误")
                            logger.error(f"火山即梦生成失败: {error_msg}")
                            raise ApiError(
                                message="火山即梦生成图片失败",
                                detail=error_msg
                            )
                        
                        # 提取图片URL
                        image_urls = query_result.get("data", {}).get("image_urls", [])
                        
                        if not image_urls:
                            raise ApiError(
                                message="火山即梦未返回图片",
                                detail="返回数据中没有image_urls字段"
                            )
                        
                        logger.info(f"火山即梦成功生成 {len(image_urls)} 张图片")
                        return image_urls
                    
                    elif status in ["in_queue", "generating"]:
                        # 任务处理中，继续等待
                        continue
                    
                    elif status == "not_found":
                        raise ApiError(
                            message="火山即梦任务未找到",
                            detail="任务可能已过期或不存在"
                        )
                    
                    elif status == "expired":
                        raise ApiError(
                            message="火山即梦任务已过期",
                            detail="请重新提交任务"
                        )
                    
                    else:
                        raise ApiError(
                            message="火山即梦任务状态未知",
                            detail=f"未知状态: {status}"
                        )
                
                # 超时
                raise ApiError(
                    message="火山即梦任务超时",
                    detail=f"轮询{max_retries}次后任务仍未完成"
                )
                
        except httpx.HTTPError as e:
            logger.error(f"火山即梦HTTP请求失败: {e}")
            raise ApiError(
                message="火山即梦请求失败",
                detail=str(e)
            )
        except ApiError:
            raise
        except Exception as e:
            logger.error(f"火山即梦调用异常: {e}")
            raise ApiError(
                message="火山即梦调用失败",
                detail=str(e)
            )
    
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
            logger.error(f"火山即梦健康检查失败: {e}")
            return False


# 全局服务实例
volc_jimeng_service = VolcJiMengService()

