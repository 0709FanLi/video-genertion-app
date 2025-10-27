"""API接口测试.

测试所有API端点的功能。
"""

import pytest
from unittest.mock import Mock, patch


def test_health_check(test_client):
    """测试健康检查接口.
    
    Args:
        test_client: 测试客户端
    """
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@patch("app.services.llm_service.LLMService.generate_image_prompts")
def test_generate_image_prompts_success(mock_generate, test_client):
    """测试图片提示词生成接口 - 成功场景.
    
    Args:
        mock_generate: Mock的生成方法
        test_client: 测试客户端
    """
    # Mock返回值
    mock_generate.return_value = [
        "A cat on the beach",
        "A realistic cat on sandy beach",
        "An artistic cat on tropical beach"
    ]
    
    response = test_client.post(
        "/api/generate-image-prompts",
        json={"idea": "一只猫在沙滩上"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "prompts" in data
    assert len(data["prompts"]) == 3


def test_generate_image_prompts_validation_error(test_client):
    """测试图片提示词生成接口 - 验证错误.
    
    Args:
        test_client: 测试客户端
    """
    response = test_client.post(
        "/api/generate-image-prompts",
        json={"idea": ""}  # 空字符串应该验证失败
    )
    
    assert response.status_code == 422


@patch("app.services.wanx_service.WanxService.generate_images")
@pytest.mark.asyncio
async def test_generate_images_success(mock_generate, test_client):
    """测试图片生成接口 - 成功场景.
    
    Args:
        mock_generate: Mock的生成方法
        test_client: 测试客户端
    """
    # Mock返回值
    mock_generate.return_value = {
        "output": {
            "task_id": "test-task-123",
            "task_status": "SUCCEEDED",
            "results": [
                {"url": "https://example.com/image1.jpg"},
                {"url": "https://example.com/image2.jpg"}
            ]
        }
    }
    
    response = test_client.post(
        "/api/generate-images",
        json={"prompt": "A cat on the beach"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "output" in data


@patch("app.services.llm_service.LLMService.optimise_video_prompt")
def test_optimise_video_prompt_success(mock_optimise, test_client):
    """测试视频提示词优化接口 - 成功场景.
    
    Args:
        mock_optimise: Mock的优化方法
        test_client: 测试客户端
    """
    # Mock返回值
    mock_optimise.return_value = "海浪轻轻拍打沙滩，泛起白色泡沫，猫咪的尾巴优雅地摇摆"
    
    response = test_client.post(
        "/api/optimise-video-prompt",
        json={"prompt": "海浪拍打，猫尾巴摇摆"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "optimised_prompt" in data
    assert len(data["optimised_prompt"]) > 0


@patch("app.services.wanx_service.WanxService.generate_video")
@pytest.mark.asyncio
async def test_generate_video_success(mock_generate, test_client):
    """测试视频生成接口 - 成功场景.
    
    Args:
        mock_generate: Mock的生成方法
        test_client: 测试客户端
    """
    # Mock返回值
    mock_generate.return_value = {
        "output": {
            "task_id": "test-video-task-456",
            "task_status": "SUCCEEDED",
            "video_url": "https://example.com/video.mp4"
        }
    }
    
    response = test_client.post(
        "/api/generate-video",
        json={
            "image_url": "https://example.com/image.jpg",
            "prompt": "海浪轻轻拍打"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "output" in data

