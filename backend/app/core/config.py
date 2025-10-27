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
        dashscope_api_key: 阿里云DashScope API密钥
        qwen_base_url: 通义千问API基础URL
        wanx_base_url: 通义万相API基础URL
        request_timeout: 请求超时时间（秒）
        task_poll_interval: 任务轮询间隔（秒）
        max_retry_attempts: 最大重试次数
        log_level: 日志级别
    """
    
    # 应用基础配置
    app_name: str = "AI视频创作工作流系统"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api"
    
    # CORS配置
    cors_origins: list[str] = ["*"]
    
    # 阿里云API配置
    dashscope_api_key: str = os.getenv(
        "DASHSCOPE_API_KEY", 
        "sk-8b6db5929e244a159deb8e77b08bcf5b"
    )
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    wanx_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # 请求配置
    request_timeout: int = 300
    task_poll_interval: int = 5
    max_retry_attempts: int = 3
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        """Pydantic配置."""
        
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()

