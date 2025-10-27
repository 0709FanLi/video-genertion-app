"""服务层测试.

测试LLMService和WanxService的核心功能。
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.services.llm_service import LLMService
from app.services.wanx_service import WanxService
from app.exceptions import DashScopeApiError, TaskFailedError


class TestLLMService:
    """LLMService测试类."""
    
    @patch("app.services.llm_service.OpenAI")
    def test_generate_image_prompts_success(self, mock_openai):
        """测试图片提示词生成 - 成功场景."""
        # 配置mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message=Mock(content='{"prompts": ["prompt1", "prompt2", "prompt3"]}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        
        # 执行测试
        service = LLMService()
        result = service.generate_image_prompts("测试想法")
        
        # 验证结果
        assert len(result) == 3
        assert result[0] == "prompt1"
    
    @patch("app.services.llm_service.OpenAI")
    def test_generate_image_prompts_api_error(self, mock_openai):
        """测试图片提示词生成 - API错误."""
        # 配置mock抛出异常
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        
        # 执行测试并验证异常
        service = LLMService()
        with pytest.raises(DashScopeApiError):
            service.generate_image_prompts("测试想法")
    
    @patch("app.services.llm_service.OpenAI")
    def test_optimise_video_prompt_success(self, mock_openai):
        """测试视频提示词优化 - 成功场景."""
        # 配置mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message=Mock(content='{"optimised_prompt": "优化后的提示词"}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        
        # 执行测试
        service = LLMService()
        result = service.optimise_video_prompt("原始提示词")
        
        # 验证结果
        assert result == "优化后的提示词"


class TestWanxService:
    """WanxService测试类."""
    
    @pytest.mark.asyncio
    @patch("app.services.wanx_service.httpx.AsyncClient")
    async def test_create_task_success(self, mock_client):
        """测试创建任务 - 成功场景."""
        # 配置mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {"task_id": "test-task-123"}
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 执行测试
        service = WanxService()
        task_id = await service._create_task(
            "/test-endpoint",
            {"test": "payload"}
        )
        
        # 验证结果
        assert task_id == "test-task-123"
    
    @pytest.mark.asyncio
    @patch("app.services.wanx_service.httpx.AsyncClient")
    async def test_poll_task_success(self, mock_client):
        """测试轮询任务 - 成功场景."""
        # 配置mock返回成功状态
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {
                "task_status": "SUCCEEDED",
                "results": [{"url": "https://example.com/result.jpg"}]
            }
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 执行测试
        service = WanxService()
        result = await service._poll_task("test-task-123", max_attempts=5)
        
        # 验证结果
        assert result["output"]["task_status"] == "SUCCEEDED"
    
    @pytest.mark.asyncio
    @patch("app.services.wanx_service.httpx.AsyncClient")
    async def test_poll_task_failed(self, mock_client):
        """测试轮询任务 - 任务失败."""
        # 配置mock返回失败状态
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {
                "task_status": "FAILED",
                "message": "任务执行失败"
            }
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 执行测试并验证异常
        service = WanxService()
        with pytest.raises(TaskFailedError):
            await service._poll_task("test-task-123", max_attempts=5)

