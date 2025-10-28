"""文件上传API路由.

提供文件上传到OSS的接口。
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.oss_service import oss_service
from app.exceptions.custom_exceptions import ApiError

router = APIRouter(prefix="/api/files", tags=["files"])
logger = get_logger(__name__)


# ==================== Schemas ====================

class UploadResponse(BaseModel):
    """文件上传响应."""
    
    object_key: str = Field(..., description="OSS对象键")
    url: str = Field(..., description="文件访问URL")
    size: int = Field(..., description="文件大小（字节）")
    content_type: str = Field(None, description="文件MIME类型")
    bucket: str = Field(..., description="Bucket名称")


class FileListResponse(BaseModel):
    """文件列表响应."""
    
    files: List[Dict[str, Any]] = Field(..., description="文件列表")
    total: int = Field(..., description="文件总数")


class DeleteResponse(BaseModel):
    """删除响应."""
    
    success: bool = Field(..., description="是否删除成功")
    object_key: str = Field(..., description="被删除的对象键")


# ==================== API Endpoints ====================

@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="上传文件到OSS",
    description="上传图片或视频文件到阿里云OSS存储"
)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    category: str = Form(default="uploads", description="文件类别: images/videos/references")
) -> UploadResponse:
    """上传文件API.
    
    Args:
        file: 上传的文件
        category: 文件类别
    
    Returns:
        文件信息
    
    Raises:
        HTTPException: 上传失败
    """
    try:
        logger.info(
            f"收到文件上传请求: filename={file.filename}, "
            f"content_type={file.content_type}, category={category}"
        )
        
        # 验证文件类型
        if not file.content_type:
            raise ApiError(
                message="无效的文件类型",
                detail="无法识别文件MIME类型"
            )
        
        # 验证类别
        valid_categories = ["images", "videos", "references", "uploads"]
        if category not in valid_categories:
            raise ApiError(
                message="无效的文件类别",
                detail=f"category必须是: {', '.join(valid_categories)}"
            )
        
        # 上传文件
        result = oss_service.upload_file(
            file_data=file.file,
            filename=file.filename,
            category=category,
            content_type=file.content_type
        )
        
        logger.info(f"文件上传成功: {result['object_key']}")
        
        return UploadResponse(**result)
        
    except ApiError as e:
        logger.error(f"上传文件失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )


@router.post(
    "/upload/reference",
    response_model=UploadResponse,
    summary="上传参考图",
    description="上传参考图到OSS，用于多图生图功能"
)
async def upload_reference_image(
    file: UploadFile = File(..., description="参考图文件")
) -> UploadResponse:
    """上传参考图API（便捷接口）.
    
    Args:
        file: 参考图文件
    
    Returns:
        文件信息
    
    Raises:
        HTTPException: 上传失败
    """
    try:
        logger.info(f"收到参考图上传请求: {file.filename}")
        
        # 验证是否为图片
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ApiError(
                message="无效的文件类型",
                detail="仅支持图片文件"
            )
        
        # 上传到references目录
        result = oss_service.upload_file(
            file_data=file.file,
            filename=file.filename,
            category="references",
            content_type=file.content_type
        )
        
        logger.info(f"参考图上传成功: {result['object_key']}")
        
        return UploadResponse(**result)
        
    except ApiError as e:
        logger.error(f"上传参考图失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )


@router.get(
    "/list",
    response_model=FileListResponse,
    summary="列举文件",
    description="列举OSS中的文件"
)
async def list_files(
    prefix: str = "",
    max_keys: int = 100
) -> FileListResponse:
    """列举文件API.
    
    Args:
        prefix: 文件路径前缀
        max_keys: 最大返回数量
    
    Returns:
        文件列表
    
    Raises:
        HTTPException: 列举失败
    """
    try:
        logger.info(f"列举文件: prefix={prefix}, max_keys={max_keys}")
        
        files = oss_service.list_files(prefix=prefix, max_keys=max_keys)
        
        return FileListResponse(
            files=files,
            total=len(files)
        )
        
    except ApiError as e:
        logger.error(f"列举文件失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )


@router.delete(
    "/{path:path}",
    response_model=DeleteResponse,
    summary="删除文件",
    description="删除OSS中的文件"
)
async def delete_file(path: str) -> DeleteResponse:
    """删除文件API.
    
    Args:
        path: 文件路径（object_key）
    
    Returns:
        删除结果
    
    Raises:
        HTTPException: 删除失败
    """
    try:
        logger.info(f"删除文件: {path}")
        
        success = oss_service.delete_file(path)
        
        return DeleteResponse(
            success=success,
            object_key=path
        )
        
    except ApiError as e:
        logger.error(f"删除文件失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"message": e.message, "detail": e.detail}
        )
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"message": "服务器内部错误", "detail": str(e)}
        )


@router.get(
    "/health",
    summary="OSS健康检查",
    description="检查OSS服务是否正常"
)
async def health_check() -> Dict[str, Any]:
    """OSS健康检查API.
    
    Returns:
        健康状态
    """
    logger.info("执行OSS健康检查")
    
    is_healthy = oss_service.health_check()
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "bucket": oss_service.bucket_name,
        "endpoint": oss_service.endpoint,
        "public_read": oss_service.public_read
    }

