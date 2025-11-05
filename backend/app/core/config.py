"""应用配置管理.

使用Pydantic Settings进行配置管理，支持环境变量加载。
所有敏感信息（API密钥、AccessKey等）必须通过环境变量配置，禁止硬编码。
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类.
    
    所有配置项都可以通过环境变量覆盖。
    敏感信息（API密钥等）必须通过环境变量配置，禁止硬编码。
    
    Attributes:
        app_name: 应用名称
        app_version: 应用版本
        debug: 是否开启调试模式
        api_prefix: API路由前缀
        cors_origins: 跨域允许的源列表
        
        # 阿里云DashScope配置
        dashscope_api_key: 阿里云DashScope API密钥（从环境变量读取）
        qwen_base_url: 通义千问API基础URL
        wanx_base_url: 通义万相API基础URL
        
        # 火山引擎即梦配置
        volc_access_key_id: 火山引擎AccessKeyId（从环境变量读取）
        volc_secret_access_key: 火山引擎SecretAccessKey（从环境变量读取）
        volc_base_url: 火山引擎API基础URL
        
        # DeepSeek配置
        deepseek_api_key: DeepSeek API密钥（从环境变量读取）
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
    # 从环境变量读取，如果未设置则使用默认值
    # 开发环境可以设置为 "*" 允许所有源（不安全，仅用于开发）
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:5174",  # Vite可能使用不同端口
        "http://localhost:5175",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://106.14.204.36:5000",  # 生产环境前端
        "http://106.14.204.36",  # 生产环境前端（如果使用80端口）
    ]
    
    # 阿里云DashScope配置
    # 注意：敏感信息必须通过环境变量配置，禁止硬编码
    dashscope_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    wanx_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # 火山引擎即梦配置
    # 注意：敏感信息必须通过环境变量配置，禁止硬编码
    volc_access_key_id: str = ""
    volc_secret_access_key: str = ""
    volc_base_url: str = "https://visual.volcengineapi.com"
    
    # DeepSeek配置
    # 注意：敏感信息必须通过环境变量配置，禁止硬编码
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # Google Gemini/Veo配置
    # 注意：敏感信息必须通过环境变量配置，禁止硬编码
    gemini_api_key: str = ""
    
    # Sora 2 API配置
    # 注意：敏感信息必须通过环境变量配置，禁止硬编码
    sora_api_key: str = ""
    sora_base_url: str = "https://api.apiyi.com/v1"
    
    # 请求配置
    request_timeout: int = 300
    task_poll_interval: int = 5
    max_retry_attempts: int = 3
    enable_retry: bool = True  # 全局重试开关，False 时禁用所有重试
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 数据库配置
    database_url: str = "sqlite:///./video_generation_app.db"  # 默认使用SQLite
    
    # JWT认证配置
    # 注意：生产环境必须通过环境变量设置强密钥
    secret_key: str = "your-secret-key-change-in-production-please-use-a-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_days: int = 7  # Token有效期7天
    
    # 阿里云OSS配置
    # 注意：敏感信息必须通过环境变量配置，禁止硬编码
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_endpoint: str = "https://oss-cn-shanghai.aliyuncs.com"  # 华东2上海
    oss_bucket_name: str = ""
    oss_public_read: bool = True  # Bucket为公共读
    oss_url_expire_seconds: int = 3600  # 签名URL有效期（秒）
    oss_max_file_size: int = 50 * 1024 * 1024  # 最大文件大小 50MB
    
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
        },
        "aliyun-qwen-image": {
            "name": "通义千问文生图",
            "model_id": "qwen-image-plus",
            "default": False,
            "supports_reference": False,  # 不支持参考图
            "max_reference_images": 0,
            "available_sizes": [  # 支持的分辨率
                {"value": "1664*928", "label": "1664×928 (16:9)", "ratio": "16:9"},
                {"value": "1472*1140", "label": "1472×1140 (4:3)", "ratio": "4:3"},
                {"value": "1328*1328", "label": "1328×1328 (1:1)", "ratio": "1:1"},
                {"value": "1140*1472", "label": "1140×1472 (3:4)", "ratio": "3:4"},
                {"value": "928*1664", "label": "928×1664 (9:16)", "ratio": "9:16"}
            ]
        },
        "google-gemini-image": {
            "name": "Google Gemini 文生图",
            "model_id": "gemini-2.5-flash-image",
            "default": False,
            "supports_reference": False,
            "max_reference_images": 0,
            "description": (
                "Google Gemini 2.5 Flash 图片生成，支持多种宽高比，"
                "仅支持纯文本与多轮对话提示，输出包含SynthID水印。"
            ),
            "available_sizes": [
                {"value": "1024x1024", "label": "1024×1024 (1:1)", "ratio": "1:1"},
                {"value": "1344x768", "label": "1344×768 (16:9)", "ratio": "16:9"},
                {"value": "768x1344", "label": "768×1344 (9:16)", "ratio": "9:16"},
                {"value": "1184x864", "label": "1184×864 (4:3)", "ratio": "4:3"},
                {"value": "864x1184", "label": "864×1184 (3:4)", "ratio": "3:4"},
                {"value": "1152x896", "label": "1152×896 (5:4)", "ratio": "5:4"},
                {"value": "896x1152", "label": "896×1152 (4:5)", "ratio": "4:5"},
                {"value": "1248x832", "label": "1248×832 (3:2)", "ratio": "3:2"},
                {"value": "832x1248", "label": "832×1248 (2:3)", "ratio": "2:3"},
                {"value": "1536x672", "label": "1536×672 (21:9)", "ratio": "21:9"}
            ]
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
    
    # 视频扩展模型配置
    video_extension_models: dict = {
        "google-veo-3.1": {
            "name": "Google Veo 3.1",
            "model_id": "veo-3.1-generate-preview",
            "default": True,
            "specs": {
                "resolution": "720p",  # 固定720p
                "duration": 8,  # 固定8秒
                "aspect_ratios": ["16:9", "9:16"],  # 支持的长宽比
                "supports_negative_prompt": True
            }
        }
    }
    
    class Config:
        """Pydantic配置."""
        
        # 确保.env文件路径正确（相对于backend目录）
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
