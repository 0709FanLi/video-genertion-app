# 全局重试配置说明

## 使用方法

### 1. 配置全局重试开关

在 `backend/app/core/config.py` 中设置：

```python
enable_retry: bool = True  # True = 启用重试, False = 禁用重试
```

或在环境变量中设置：
```bash
export ENABLE_RETRY=false
```

### 2. 在服务中使用重试装饰器

替换原有的 `@retry` 装饰器为 `@retry_decorator`：

**旧代码：**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def my_api_call():
    ...
```

**新代码：**
```python
from app.utils.retry_decorator import retry_decorator

@retry_decorator(max_attempts=3, wait_multiplier=1, wait_min=2, wait_max=10)
async def my_api_call():
    ...
```

### 3. 功能特性

- ✅ **全局开关控制**：可通过 `settings.enable_retry` 一键启用/禁用所有重试
- ✅ **智能配额检测**：自动检测 429 配额错误，不进行无效重试
- ✅ **向后兼容**：如果禁用重试，装饰器会返回原函数，不影响功能

### 4. 需要更新的服务文件

以下服务文件需要更新为使用新的 `retry_decorator`：

- ✅ `backend/app/services/google_veo_service.py` - 已更新
- ⏳ `backend/app/services/deepseek_service.py` - 已更新
- ⏳ `backend/app/services/volc_video_service.py`
- ⏳ `backend/app/services/qwen_image_service.py`
- ⏳ `backend/app/services/wanx_kf2v_service.py`
- ⏳ `backend/app/services/qwen_vl_service.py`
- ⏳ `backend/app/services/volc_jimeng_service.py`
- ⏳ `backend/app/services/wanx_i2i_service.py`
- ⏳ `backend/app/services/llm_service.py`
- ⏳ `backend/app/services/wanx_service.py`

### 5. 快速批量更新脚本

可以使用以下模式批量替换：

```bash
# 在服务文件中查找并替换
find backend/app/services -name "*.py" -exec sed -i '' \
  's/from tenacity import retry, stop_after_attempt, wait_exponential/from app.utils.retry_decorator import retry_decorator/g' {} \;
```

注意：需要手动检查每个文件的装饰器使用是否正确。

