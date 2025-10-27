"""Pytest配置文件.

定义测试夹具和共享配置。
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def test_app():
    """创建测试应用实例.
    
    Returns:
        FastAPI应用实例
    """
    app = create_app()
    return app


@pytest.fixture
def test_client(test_app):
    """创建测试客户端.
    
    Args:
        test_app: 测试应用实例
        
    Returns:
        TestClient实例
    """
    return TestClient(test_app)

