"""应用配置管理.

使用Pydantic Settings进行配置管理，支持环境变量加载。
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类.
    
    所有配置项都可以通过环境变量覆盖。
    
    Attributes:
        app_name: 应用名称
        app_version: 应用版本
        debug: 是否开启调试模式
        api_prefix: API路由前缀
        cors_origins: 跨域允许的源列表
        
        # 阿里云DashScope配置
        dashscope_api_key: 阿里云DashScope API密钥
        qwen_base_url: 通义千问API基础URL
        wanx_base_url: 通义万相API基础URL
        
        # 火山引擎即梦配置
        volc_access_key_id: 火山引擎AccessKeyId
        volc_secret_access_key: 火山引擎SecretAccessKey
        volc_base_url: 火山引擎API基础URL
        
        # DeepSeek配置
        deepseek_api_key: DeepSeek API密钥
        deepseek_base_url: DeepSeek API基础URL
        
        request_timeout: 请求超时时间（秒）
        task_poll_interval: 任务轮询间隔（秒）
        max_retry_attempts: 最大重试次数
        log_level: 日志级别
    """
    
    # 应用基础配置
    app_name: str = "AI创意生成平台"
    app_version: str = "2.0.0"
    debug: bool = False
    api_prefix: str = "/api"
    
    # CORS配置
    cors_origins: list[str] = ["*"]
    
    # 阿里云DashScope配置
    dashscope_api_key: str = os.getenv(
        "DASHSCOPE_API_KEY", 
        "sk-8b6db5929e244a159deb8e77b08bcf5b"
    )
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    wanx_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # 火山引擎即梦配置
    volc_access_key_id: str = os.getenv("VOLC_ACCESS_KEY_ID", "")
    volc_secret_access_key: str = os.getenv("VOLC_SECRET_ACCESS_KEY", "")
    volc_base_url: str = "https://visual.volcengineapi.com"
    
    # DeepSeek配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # 请求配置
    request_timeout: int = 300
    task_poll_interval: int = 5
    max_retry_attempts: int = 3
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 阿里云OSS配置
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_endpoint: str = "https://oss-cn-shanghai.aliyuncs.com"  # 华东2上海
    oss_bucket_name: str = ""
    oss_public_read: bool = True  # Bucket为公共读
    oss_url_expire_seconds: int = 3600  # 签名URL有效期（秒）
    oss_max_file_size: int = 10 * 1024 * 1024  # 最大文件大小 10MB
    
    # 文生图模型配置
    text_to_image_models: dict = {
        "volc-jimeng": {
            "name": "火山引擎即梦4.0",
            "model_id": "jimeng_t2i_v40",
            "default": True,
            "supports_reference": True,  # 支持参考图
            "max_reference_images": 6  # 最多6张参考图
        },
        "aliyun-wanx-i2i": {
            "name": "通义万相多图生图",
            "model_id": "wan2.5-i2i-preview",
            "default": False,
            "supports_reference": True,
            "max_reference_images": 2  # 根据文档，最多2张参考图
        }
    }
    
    # 提示词优化模型配置
    prompt_optimization_models: dict = {
        "qwen-plus": {
            "name": "通义千问 (系统默认)",
            "model_id": "qwen-plus",
            "default": True
        },
        "deepseek-v3": {
            "name": "DeepSeek-V3.2-Exp",
            "model_id": "deepseek-chat",
            "default": False
        }
    }
    
    class Config:
        """Pydantic配置."""
        
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
