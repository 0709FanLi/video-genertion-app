"""阿里云OSS服务.

提供文件上传、下载、删除等OSS操作功能。
参考文档: https://help.aliyun.com/document_detail/32026.html
"""

import os
import uuid
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, BinaryIO
from urllib.parse import quote

import oss2
from oss2.exceptions import OssError

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.custom_exceptions import ApiError

logger = get_logger(__name__)


class OSSService:
    """阿里云OSS服务类.
    
    封装OSS文件操作，提供上传、下载、删除等功能。
    
    Attributes:
        auth: OSS认证对象
        bucket: OSS Bucket对象
        endpoint: OSS访问端点
        bucket_name: Bucket名称
        public_read: 是否为公共读Bucket
    """
    
    def __init__(self) -> None:
        """初始化OSS服务."""
        self.access_key_id = settings.oss_access_key_id
        self.access_key_secret = settings.oss_access_key_secret
        self.endpoint = settings.oss_endpoint
        self.bucket_name = settings.oss_bucket_name
        self.public_read = settings.oss_public_read
        self.url_expire_seconds = settings.oss_url_expire_seconds
        self.max_file_size = settings.oss_max_file_size
        
        # 初始化OSS客户端
        try:
            self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(
                self.auth, 
                self.endpoint, 
                self.bucket_name
            )
            logger.info(f"OSSService初始化完成: bucket={self.bucket_name}")
        except Exception as e:
            logger.error(f"OSS初始化失败: {e}")
            raise ApiError(
                message="OSS服务初始化失败",
                detail=str(e)
            )
    
    def _generate_object_key(
        self, 
        category: str, 
        filename: str,
        use_date_path: bool = True
    ) -> str:
        """生成OSS对象键（文件路径）.
        
        Args:
            category: 文件类别 (images/videos/references)
            filename: 原始文件名
            use_date_path: 是否使用日期路径
        
        Returns:
            OSS对象键，如 "images/2025/01/27/uuid_filename.jpg"
        """
        # 生成唯一ID
        unique_id = uuid.uuid4().hex[:8]
        
        # 处理文件名（保留扩展名）
        name, ext = os.path.splitext(filename)
        safe_filename = f"{unique_id}_{name}{ext}"
        
        # 构建路径
        if use_date_path:
            now = datetime.now()
            date_path = now.strftime("%Y/%m/%d")
            object_key = f"{category}/{date_path}/{safe_filename}"
        else:
            object_key = f"{category}/{safe_filename}"
        
        return object_key
    
    def _get_public_url(self, object_key: str) -> str:
        """获取公共访问URL.
        
        Args:
            object_key: OSS对象键
        
        Returns:
            公共访问URL
        """
        # 公共读Bucket直接返回URL
        return f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{quote(object_key)}"
    
    def _get_signed_url(self, object_key: str, expires: int = None) -> str:
        """获取带签名的URL（用于私有Bucket）.
        
        Args:
            object_key: OSS对象键
            expires: 过期时间（秒），默认使用配置值
        
        Returns:
            带签名的URL
        """
        if expires is None:
            expires = self.url_expire_seconds
        
        try:
            url = self.bucket.sign_url('GET', object_key, expires)
            return url
        except Exception as e:
            logger.error(f"生成签名URL失败: {e}")
            # 如果签名失败，返回公共URL
            return self._get_public_url(object_key)
    
    def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        category: str = "uploads",
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """上传文件到OSS.
        
        Args:
            file_data: 文件数据流
            filename: 原始文件名
            category: 文件类别 (images/videos/references)
            content_type: 文件MIME类型
        
        Returns:
            包含文件信息的字典
        
        Raises:
            ApiError: 上传失败
        """
        try:
            # 读取文件内容
            file_content = file_data.read()
            file_size = len(file_content)
            
            # 检查文件大小
            if file_size > self.max_file_size:
                raise ApiError(
                    message="文件大小超过限制",
                    detail=f"文件大小: {file_size / 1024 / 1024:.2f}MB, 限制: {self.max_file_size / 1024 / 1024:.2f}MB"
                )
            
            # 生成对象键
            object_key = self._generate_object_key(category, filename)
            
            # 设置请求头
            headers = {}
            if content_type:
                headers['Content-Type'] = content_type
            
            # 上传文件
            logger.info(f"开始上传文件: {object_key}, 大小: {file_size / 1024:.2f}KB")
            
            result = self.bucket.put_object(
                object_key, 
                file_content,
                headers=headers
            )
            
            # 获取访问URL
            if self.public_read:
                url = self._get_public_url(object_key)
            else:
                url = self._get_signed_url(object_key)
            
            logger.info(f"文件上传成功: {object_key}")
            
            return {
                "object_key": object_key,
                "url": url,
                "size": file_size,
                "content_type": content_type,
                "etag": result.etag,
                "bucket": self.bucket_name
            }
            
        except OssError as e:
            logger.error(f"OSS上传失败: {e}")
            raise ApiError(
                message="文件上传失败",
                detail=f"OSS错误: {e.code} - {e.message}"
            )
        except Exception as e:
            logger.error(f"上传文件异常: {e}")
            raise ApiError(
                message="文件上传失败",
                detail=str(e)
            )
    
    async def upload_from_url(
        self,
        url: str,
        filename: str,
        category: str = "images"
    ) -> Dict[str, Any]:
        """从URL下载文件并上传到OSS（异步）.
        
        用于将AI生成的图片/视频从临时URL保存到OSS。
        支持大文件下载（如视频），超时时间为5分钟。
        
        Args:
            url: 源文件URL
            filename: 保存的文件名
            category: 文件类别 (images/videos/references)
        
        Returns:
            包含文件信息的字典
        
        Raises:
            ApiError: 上传失败
        """
        import httpx
        
        try:
            logger.info(f"从URL下载文件: {url[:100]}...")
            
            # 下载文件（异步，支持大文件）
            # 视频文件可能较大，设置超时为5分钟
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                file_content = response.content
                content_type = response.headers.get('Content-Type')
                file_size_mb = len(file_content) / 1024 / 1024
            
            logger.info(f"文件下载完成，大小: {file_size_mb:.2f}MB")
            
            # 检查文件大小（视频文件可能超过10MB，需要临时调整限制检查）
            # 这里我们信任AI生成的视频，不做严格限制
            
            # 上传到OSS
            file_stream = BytesIO(file_content)
            
            # 临时保存原限制，上传视频时不检查大小限制
            original_max_size = self.max_file_size
            self.max_file_size = float('inf')  # 临时取消限制
            
            try:
                result = self.upload_file(
                    file_stream,
                    filename,
                    category,
                    content_type
                )
            finally:
                # 恢复原限制
                self.max_file_size = original_max_size
            
            logger.info(f"文件已成功转存到OSS: {result['object_key']}")
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"下载文件失败: {e}")
            raise ApiError(
                message="下载文件失败",
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"从URL上传失败: {e}")
            raise ApiError(
                message="从URL上传失败",
                detail=str(e)
            )
    
    def delete_file(self, object_key: str) -> bool:
        """删除OSS文件.
        
        Args:
            object_key: OSS对象键
        
        Returns:
            是否删除成功
        
        Raises:
            ApiError: 删除失败
        """
        try:
            logger.info(f"删除文件: {object_key}")
            self.bucket.delete_object(object_key)
            logger.info(f"文件删除成功: {object_key}")
            return True
            
        except OssError as e:
            logger.error(f"OSS删除失败: {e}")
            raise ApiError(
                message="文件删除失败",
                detail=f"OSS错误: {e.code} - {e.message}"
            )
        except Exception as e:
            logger.error(f"删除文件异常: {e}")
            raise ApiError(
                message="文件删除失败",
                detail=str(e)
            )
    
    def list_files(
        self,
        prefix: str = "",
        max_keys: int = 100
    ) -> List[Dict[str, Any]]:
        """列举OSS文件.
        
        Args:
            prefix: 文件前缀（路径）
            max_keys: 最大返回数量
        
        Returns:
            文件列表
        
        Raises:
            ApiError: 列举失败
        """
        try:
            logger.info(f"列举文件: prefix={prefix}, max_keys={max_keys}")
            
            result = self.bucket.list_objects(
                prefix=prefix,
                max_keys=max_keys
            )
            
            files = []
            for obj in result.object_list:
                file_info = {
                    "object_key": obj.key,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag,
                    "url": self._get_public_url(obj.key) if self.public_read else self._get_signed_url(obj.key)
                }
                files.append(file_info)
            
            logger.info(f"列举成功，共 {len(files)} 个文件")
            return files
            
        except OssError as e:
            logger.error(f"OSS列举失败: {e}")
            raise ApiError(
                message="列举文件失败",
                detail=f"OSS错误: {e.code} - {e.message}"
            )
        except Exception as e:
            logger.error(f"列举文件异常: {e}")
            raise ApiError(
                message="列举文件失败",
                detail=str(e)
            )
    
    def file_exists(self, object_key: str) -> bool:
        """检查文件是否存在.
        
        Args:
            object_key: OSS对象键
        
        Returns:
            文件是否存在
        """
        try:
            return self.bucket.object_exists(object_key)
        except Exception as e:
            logger.error(f"检查文件存在异常: {e}")
            return False
    
    def get_file_url(
        self, 
        object_key: str, 
        expires: int = None
    ) -> str:
        """获取文件访问URL.
        
        Args:
            object_key: OSS对象键
            expires: 过期时间（秒）
        
        Returns:
            文件访问URL
        """
        if self.public_read:
            return self._get_public_url(object_key)
        else:
            return self._get_signed_url(object_key, expires)
    
    def health_check(self) -> bool:
        """健康检查.
        
        Returns:
            服务是否可用
        """
        try:
            # 尝试列举文件（限制1个）
            self.bucket.list_objects(max_keys=1)
            return True
        except Exception as e:
            logger.error(f"OSS健康检查失败: {e}")
            return False


# 全局服务实例
oss_service = OSSService()

