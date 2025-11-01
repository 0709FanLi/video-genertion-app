# Sora 2 API 集成开发方案

## 一、概述

### 1.1 目标
将 Sora 2 API 集成到现有的视频生成系统中，支持文生视频和图生视频功能。

### 1.2 API 特点
- **API 地址**: `https://api.apiyi.com/v1/chat/completions`
- **认证方式**: Bearer Token
- **请求方式**: POST (JSON)
- **输出格式**: 流式输出 (Server-Sent Events, SSE)
- **视频存储**: 生成的视频链接仅保留 1 天，需及时转存到 OSS

### 1.3 支持的模型
| 模型名 | 描述 | 分辨率 | 时长 | 价格 |
|--------|------|--------|------|------|
| `sora_video2` | 竖屏视频（默认） | 704 × 1280 | 10s | $0.15/次 |
| `sora_video2-landscape` | 横屏视频 | 1280 × 704 | 10s | $0.15/次 |
| `sora_video2-15s` | 竖屏视频 | 704 × 1280 | 15s | $0.15/次 |
| `sora_video2-landscape-15s` | 横屏视频 | 1280 × 704 | 15s | $0.15/次 |

---

## 二、开发步骤

### 2.1 配置管理（`backend/app/core/config.py`）

**添加配置项**：
```python
# Sora 2 API 配置
sora_api_key: str = os.getenv("SORA_API_KEY", "")
sora_base_url: str = "https://api.apiyi.com/v1"
```

**位置**: 在 `Settings` 类中添加，与其他 API 配置项一起

---

### 2.2 创建 Sora 服务类（`backend/app/services/sora_service.py`）

**主要功能**：
1. **流式请求处理**: 使用 `httpx.AsyncClient` 处理 SSE 流式输出
2. **视频链接解析**: 从流式响应中提取视频 URL（使用正则表达式）
3. **视频转存**: 下载视频并上传到 OSS（视频仅保留1天）
4. **错误处理**: 处理内容审核失败、网络错误等异常情况

**核心方法**：

#### 2.2.1 文生视频 (`generate_text_to_video`)
```python
async def generate_text_to_video(
    self,
    prompt: str,
    model: str = "sora_video2",  # 支持4种模型
    duration: int = 10  # 10s 或 15s（通过模型名控制）
) -> dict[str, Any]:
    """
    文生视频
    
    Args:
        prompt: 视频描述提示词
        model: 模型名称（控制横竖屏和时长）
        duration: 时长（10或15秒，与模型名对应）
    
    Returns:
        包含 video_url (OSS永久链接) 的结果数据
    """
```

#### 2.2.2 图生视频 (`generate_image_to_video`)
```python
async def generate_image_to_video(
    self,
    image_url: str,  # OSS URL 或 Base64 data URI
    prompt: str,
    model: str = "sora_video2",
    duration: int = 10
) -> dict[str, Any]:
    """
    图生视频
    
    Args:
        image_url: 图片URL或Base64 data URI
        prompt: 视频描述提示词
        model: 模型名称
        duration: 时长
    
    Returns:
        包含 video_url (OSS永久链接) 的结果数据
    """
```

#### 2.2.3 流式响应解析 (`_parse_stream_response`)
```python
async def _parse_stream_response(
    self,
    response: httpx.Response
) -> Optional[str]:
    """
    解析 SSE 流式响应，提取视频链接
    
    响应格式示例:
    data: {"choices":[{"delta":{"content":"视频生成中..."}}]}
    data: {"choices":[{"delta":{"content":"视频生成成功！[点击这里](https://example.com/video.mp4)"}}]}
    data: [DONE]
    
    Returns:
        视频URL，如果未找到则返回None
    """
```

#### 2.2.4 视频转存 (`_save_video_to_oss`)
```python
async def _save_video_to_oss(
    self,
    temp_video_url: str,
    model: str
) -> str:
    """
    从临时URL下载视频并上传到OSS
    
    Args:
        temp_video_url: Sora API返回的临时视频URL（仅保留1天）
        model: 模型名称（用于命名）
    
    Returns:
        OSS永久URL
    """
```

**实现要点**：
- 使用 `httpx.AsyncClient` 的 `stream=True` 处理流式响应
- 逐行解析 `data: ` 开头的 SSE 格式数据
- 使用正则表达式提取视频链接: `r'\[点击这里\]\((https?://[^\)]+)\)'`
- 捕获 `ChunkedEncodingError` 异常（可能是内容审核失败）
- 下载视频时设置合适的超时时间（建议60秒）

---

### 2.3 更新 Schema（`backend/app/schemas/image_to_video.py`）

**在 `VideoModel` 枚举中添加 Sora 模型**：
```python
class VideoModel(str, Enum):
    # ... 现有模型 ...
    
    # Sora 2 模型
    SORA_V2_PORTRAIT = "sora-v2-portrait"  # 竖屏 10s
    SORA_V2_LANDSCAPE = "sora-v2-landscape"  # 横屏 10s
    SORA_V2_PORTRAIT_15S = "sora-v2-portrait-15s"  # 竖屏 15s
    SORA_V2_LANDSCAPE_15S = "sora-v2-landscape-15s"  # 横屏 15s
```

**注意**: Schema 中的枚举值与实际 Sora API 的模型名映射关系：
- `sora-v2-portrait` → `sora_video2`
- `sora-v2-landscape` → `sora_video2-landscape`
- `sora-v2-portrait-15s` → `sora_video2-15s`
- `sora-v2-landscape-15s` → `sora_video2-landscape-15s`

---

### 2.4 更新路由（`backend/app/api/routes/image_to_video.py`）

**在 `generate_video` 函数中添加 Sora 模型处理**：
```python
@router.post("/generate", response_model=ImageToVideoResponse)
async def generate_video(...):
    # ... 现有代码 ...
    
    # 根据模型选择不同的服务
    if request.model in [VideoModel.SORA_V2_PORTRAIT, VideoModel.SORA_V2_LANDSCAPE, 
                         VideoModel.SORA_V2_PORTRAIT_15S, VideoModel.SORA_V2_LANDSCAPE_15S]:
        # Sora 2 API
        result = await _generate_sora_video(request, first_frame_url)
    
    # ... 其他模型处理 ...
```

**添加辅助函数 `_generate_sora_video`**：
```python
async def _generate_sora_video(
    request: ImageToVideoRequest,
    first_frame_url: Optional[str]
) -> ImageToVideoResponse:
    """
    调用 Sora 2 API 生成视频
    
    Args:
        request: 视频生成请求
        first_frame_url: 首帧图片URL（文生视频时为None）
    
    Returns:
        视频生成结果
    """
    from app.services.sora_service import sora_service
    
    # 映射模型名
    model_mapping = {
        VideoModel.SORA_V2_PORTRAIT: "sora_video2",
        VideoModel.SORA_V2_LANDSCAPE: "sora_video2-landscape",
        VideoModel.SORA_V2_PORTRAIT_15S: "sora_video2-15s",
        VideoModel.SORA_V2_LANDSCAPE_15S: "sora_video2-landscape-15s",
    }
    sora_model = model_mapping[request.model]
    
    # 确定时长（从模型名推断）
    duration = 15 if "15s" in sora_model else 10
    
    # 调用服务
    if first_frame_url:
        # 图生视频
        result = await sora_service.generate_image_to_video(
            image_url=first_frame_url,
            prompt=request.prompt,
            model=sora_model,
            duration=duration
        )
    else:
        # 文生视频
        result = await sora_service.generate_text_to_video(
            prompt=request.prompt,
            model=sora_model,
            duration=duration
        )
    
    return ImageToVideoResponse(
        video_url=result["video_url"],
        task_id=result.get("task_id", ""),
        model=request.model.value,
        duration=duration,
        orig_prompt=request.prompt,
        actual_prompt=request.prompt  # Sora 不修改提示词
    )
```

---

### 2.5 依赖安装

**在 `requirements.txt` 中添加**（如未安装）：
```
httpx>=0.24.0  # 用于异步HTTP请求和流式响应
```

---

## 三、技术要点

### 3.1 流式响应处理
- 使用 `httpx.AsyncClient` 的 `stream=True` 参数
- 逐行读取响应，解析 `data: ` 前缀的 SSE 格式
- 遇到 `[DONE]` 时停止解析

### 3.2 错误处理
- **内容审核失败**: 捕获 `ChunkedEncodingError`，提示用户修改提示词
- **网络超时**: 设置合理的超时时间（建议600秒用于生成，60秒用于下载）
- **视频链接未找到**: 返回 None，记录错误日志

### 3.3 视频转存
- **及时性**: 生成后立即转存（视频仅保留1天）
- **重试机制**: 使用现有的 `retry_decorator` 装饰器
- **临时文件清理**: 下载后及时删除临时文件

### 3.4 日志记录
- 记录请求参数、模型选择、生成进度
- 记录视频转存结果
- 记录错误详情

---

## 四、测试要点

### 4.1 后端功能测试
1. **文生视频**: 测试4种模型（竖屏/横屏 × 10s/15s）
2. **图生视频**: 测试4种模型，使用 OSS URL 和 Base64 两种方式
3. **错误处理**: 测试内容审核失败、网络错误等场景
4. **流式响应**: 测试 SSE 流式输出的正确解析
5. **视频转存**: 测试视频下载和OSS上传功能

### 4.2 前端功能测试
1. **模型选择**: 测试4个 Sora 2 模型选项是否正确显示
2. **参数处理**: 测试时长和分辨率参数是否正确处理
3. **图片上传**: 测试文生视频和图生视频模式的图片上传逻辑
4. **结果展示**: 测试视频结果正确显示和标识
5. **错误提示**: 测试各种错误场景的用户提示

### 4.3 性能测试
- 流式响应解析速度
- 视频下载和转存速度
- 并发请求处理能力
- 前端加载和渲染性能

### 4.4 集成测试
- 与现有路由的集成
- 与用户视频库的集成
- 与OSS服务的集成
- 前后端完整流程测试

---

## 五、前端修改方案

### 5.1 模型选择器更新（`frontend/src/components/ImageToVideo/ModelSelector.jsx`）

**添加 Sora 2 模型选项**：
```javascript
// 在 models 数组中添加4个 Sora 模型
{
  value: 'sora-v2-portrait',
  label: 'Sora 2 - 竖屏 10s',
  description: 'Sora 2 竖屏视频，704×1280，10秒，$0.15/次',
  icon: <VideoCameraOutlined />, // 需要导入 VideoCameraOutlined
  tags: ['Sora', '竖屏', '10s'],
  needLastFrame: false,
  needFirstFrame: false  // 支持文生视频
},
{
  value: 'sora-v2-landscape',
  label: 'Sora 2 - 横屏 10s',
  description: 'Sora 2 横屏视频，1280×704，10秒，$0.15/次',
  icon: <VideoCameraOutlined />,
  tags: ['Sora', '横屏', '10s'],
  needLastFrame: false,
  needFirstFrame: false
},
{
  value: 'sora-v2-portrait-15s',
  label: 'Sora 2 - 竖屏 15s',
  description: 'Sora 2 竖屏视频，704×1280，15秒，$0.15/次',
  icon: <VideoCameraOutlined />,
  tags: ['Sora', '竖屏', '15s'],
  needLastFrame: false,
  needFirstFrame: false
},
{
  value: 'sora-v2-landscape-15s',
  label: 'Sora 2 - 横屏 15s',
  description: 'Sora 2 横屏视频，1280×704，15秒，$0.15/次',
  icon: <VideoCameraOutlined />,
  tags: ['Sora', '横屏', '15s'],
  needLastFrame: false,
  needFirstFrame: false
}
```

**注意**：
- Sora 2 模型支持文生视频和图生视频两种模式
- 图生视频时 `needFirstFrame: true`，文生视频时 `needFirstFrame: false`
- 根据模型名自动判断时长（10s 或 15s）

**图标导入**：
```javascript
import { 
  ThunderboltOutlined, 
  RocketOutlined, 
  GoogleOutlined,
  VideoCameraOutlined  // 新增
} from '@ant-design/icons';
```

---

### 5.2 视频参数组件更新（`frontend/src/components/ImageToVideo/VideoParams.jsx`）

**添加 Sora 模型判断逻辑**：
```javascript
const isSoraV2 = selectedModel.startsWith('sora-v2');

// 在渲染逻辑中添加
{isSoraV2 && (
  <div style={{ color: '#666', fontSize: '12px', marginTop: '8px' }}>
    ℹ️ Sora 2 模型时长由模型名控制（10s 或 15s），分辨率固定（竖屏 704×1280，横屏 1280×704）
  </div>
)}
```

**注意事项**：
- Sora 2 模型的时长和分辨率由模型名控制，不需要用户选择
- 时长参数需要根据模型名自动设置（10s 或 15s）
- 分辨率参数对 Sora 2 无效，可隐藏或禁用

---

### 5.3 主页面组件更新（`frontend/src/components/ImageToVideo/index.jsx`）

**更新验证逻辑**：
```javascript
// 在 validateInput 函数中添加 Sora 模型判断
const isSoraV2 = selectedModel.startsWith('sora-v2');
const isTextToVideo = selectedModel === 'volc-t2v' || 
                      selectedModel === 'google-veo-t2v' || 
                      isSoraV2;

// 文生视频模式（包括 Sora 2）
if (isTextToVideo) {
  return true;
}

// 图生视频模式（Sora 2 也支持）
if (isSoraV2 || selectedModel.startsWith('volc-i2v') || ...) {
  if (!firstFrame || !firstFrame.base64) {
    message.warning('请先上传首帧图片');
    return false;
  }
}
```

**更新生成参数**：
```javascript
// 在 handleGenerateVideo 函数中
const params = {
  model: selectedModel,
  first_frame_base64: firstFrame?.base64 || null,
  last_frame_base64: lastFrame?.base64 || null,
  prompt: prompt.trim(),
  duration: isSoraV2 ? (selectedModel.includes('15s') ? 15 : 10) : duration,  // Sora 2 自动设置时长
  resolution: isSoraV2 ? undefined : resolution,  // Sora 2 不需要分辨率参数
  aspect_ratio: isSoraV2 ? undefined : aspectRatio  // Sora 2 不需要长宽比参数
};
```

---

### 5.4 图片上传组件更新（`frontend/src/components/ImageToVideo/ImageUpload.jsx`）

**更新文生视频判断**：
```javascript
const isTextToVideo = selectedModel === 'volc-t2v' || 
                      selectedModel === 'google-veo-t2v' || 
                      selectedModel.startsWith('sora-v2');
```

**添加 Sora 2 图生视频支持**：
- Sora 2 模型支持图生视频，需要首帧图片
- 当选择 Sora 2 模型时，允许上传首帧图片（即使模型也支持文生视频）

---

### 5.5 视频结果组件更新（`frontend/src/components/ImageToVideo/VideoResult.jsx`）

**添加 Sora 2 模型标识**：
```javascript
// 在显示模型信息时
const isSoraV2 = videoResult.model.toLowerCase().includes('sora-v2');

{isSoraV2 && (
  <Tag color="purple" icon={<VideoCameraOutlined />}>
    Sora 2
  </Tag>
)}
```

---

### 5.6 Store 更新（`frontend/src/store/videoStore.js`）

**默认模型保持不变**，但确保支持 Sora 2 模型值：
```javascript
// 确保 store 可以处理新的模型值
selectedModel: 'volc-i2v-first', // 默认模型保持不变
```

---

### 5.7 API 服务更新（`frontend/src/services/api.js`）

**确认 API 调用支持 Sora 模型**：
```javascript
// imageToVideoAPI.generateVideo 方法应该已经支持所有模型值
// 无需修改，但确保参数传递正确
```

---

## 六、文件清单

### 6.1 后端新增文件
- `backend/app/services/sora_service.py` - Sora 2 API 服务类

### 6.2 后端修改文件
- `backend/app/core/config.py` - 添加 Sora API Key 配置
- `backend/app/schemas/image_to_video.py` - 添加 Sora 模型枚举
- `backend/app/api/routes/image_to_video.py` - 添加 Sora 模型路由处理

### 6.3 前端修改文件
- `frontend/src/components/ImageToVideo/ModelSelector.jsx` - 添加 Sora 2 模型选项
- `frontend/src/components/ImageToVideo/VideoParams.jsx` - 添加 Sora 2 参数处理
- `frontend/src/components/ImageToVideo/index.jsx` - 更新验证和生成逻辑
- `frontend/src/components/ImageToVideo/ImageUpload.jsx` - 更新文生视频判断
- `frontend/src/components/ImageToVideo/VideoResult.jsx` - 添加 Sora 2 标识

### 6.4 配置文件
- `requirements.txt` - 确认 httpx 依赖（如未安装需添加）

---

## 七、开发顺序建议

### 7.1 后端开发（按顺序）
1. ✅ **第一步**: 创建 `sora_service.py`，实现基础框架和文生视频功能
2. ✅ **第二步**: 实现流式响应解析和视频链接提取
3. ✅ **第三步**: 实现视频转存到OSS功能
4. ✅ **第四步**: 实现图生视频功能
5. ✅ **第五步**: 更新 Schema 和路由，集成到现有系统
6. ✅ **第六步**: 添加错误处理和日志
7. ✅ **第七步**: 后端测试和优化

### 7.2 前端开发（与后端并行或稍后）
1. ✅ **第一步**: 更新 `ModelSelector.jsx`，添加 Sora 2 模型选项
2. ✅ **第二步**: 更新 `VideoParams.jsx`，处理 Sora 2 特殊参数
3. ✅ **第三步**: 更新 `index.jsx`，添加 Sora 2 验证和生成逻辑
4. ✅ **第四步**: 更新 `ImageUpload.jsx` 和 `VideoResult.jsx`
5. ✅ **第五步**: 前端测试和UI优化

### 7.3 集成测试
1. ✅ **第一步**: 后端API测试（使用 Postman 或 curl）
2. ✅ **第二步**: 前后端联调测试
3. ✅ **第三步**: 完整流程测试（文生视频 + 图生视频）
4. ✅ **第四步**: 错误场景测试
5. ✅ **第五步**: 性能测试

---

## 八、注意事项

1. **API Key 安全**: 确保 API Key 通过环境变量配置，不要硬编码
2. **视频时效性**: 生成的视频链接仅保留1天，必须在生成后立即转存
3. **内容审核**: 提示用户避免真实人物、敏感内容描述
4. **超时设置**: 视频生成需要3-5分钟，设置合适的超时时间
5. **错误提示**: 友好的错误提示，帮助用户理解失败原因
6. **成本控制**: Sora API 按次计费（$0.15/次），注意使用量

---

## 九、后续优化（可选）

1. **WebSocket 支持**: 实时推送生成进度到前端
2. **队列管理**: 对于高并发场景，实现任务队列
3. **缓存机制**: 缓存常用提示词的生成结果
4. **批量处理**: 支持批量生成视频
5. **预览功能**: 生成缩略图预览

---

## 十、参考文档

- Sora API 文档: `sora-api.txt`
- API易文档: https://docs.apiyi.com
- 现有服务参考: `volc_video_service.py`, `google_veo_service.py`

