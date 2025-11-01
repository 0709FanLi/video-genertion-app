# 视频扩展（Video Extension）详细分析

## 一、官方示例解析

### 1.1 官方示例代码

```python
import time
from google import genai

client = genai.Client()

prompt = "Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower."

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=butterfly_video,  # ⚠️ 关键：这里是 Video 对象，不是 File 对象
    prompt=prompt,
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        resolution="720p"
    ),
)

# 轮询任务状态
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# 下载视频
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3.1_extension.mp4")
```

### 1.2 关键参数说明

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `video` | `types.Video` | **必须是 Video 对象**，不能是 File 对象 | `generated_video.video` |
| `prompt` | `str` | 扩展内容的描述，应该描述**接下来**发生什么 | "Track the butterfly into the garden..." |
| `config.resolution` | `str` | 分辨率："720p" 或 "1080p" | "720p" |
| `config.aspect_ratio` | `str` | 长宽比："16:9" 或 "9:16" | "16:9" |
| `config.duration_seconds` | `int` | 视频时长：4、6、8秒 | 8 |
| `config.number_of_videos` | `int` | 生成视频数量 | 1 |

### 1.3 Video vs File 对象的区别

**Video 对象**：
- 从生成结果中获取：`generated_video.video`
- 包含视频的元数据和 URI
- URI 格式：`"files/xxx"`（这就是 File ID）
- **用于视频扩展**

**File 对象**：
- 通过上传文件创建：`client.files.upload(file=path)`
- 或者通过 File ID 创建：`types.File(name="files/xxx")`
- **不能直接用于视频扩展**

## 二、我们当前的实现问题

### 2.1 当前实现代码

```python
# 在 extend_video 方法中
if google_file_id:
    # ❌ 问题：创建的是 File 对象，不是 Video 对象
    google_video = types.File(name=google_file_id)
else:
    # 从 OSS 下载并上传
    temp_video_path = await self._download_video_from_oss(video_url)
    google_video = await self._upload_video_to_google(temp_video_path)

# 在 _create_extension_task 中
operation = await loop.run_in_executor(
    None,
    lambda: self.client.models.generate_videos(
        model=self.model,
        video=google_video,  # ❌ 传递的是 File 对象
        prompt=prompt,
        config=config
    )
)
```

### 2.2 问题分析

**核心问题**：我们传递的是 `File` 对象，而不是 `Video` 对象！

1. **Video 对象**包含视频的完整上下文信息，包括：
   - 视频帧序列
   - 时间戳信息
   - 视频元数据
   - 与原始生成任务的关联

2. **File 对象**只是一个文件引用，缺少：
   - 视频的上下文信息
   - 与原始视频的关联
   - 导致扩展视频与原始视频没有连续性

### 2.3 为什么视频没有关联？

当使用 `File` 对象时：
- Google Veo API 可能无法正确识别视频的最后一帧
- 无法理解视频的时间序列信息
- 导致扩展的视频与原始视频在视觉上不连贯

当使用 `Video` 对象时：
- API 可以访问完整的视频信息
- 能够准确识别最后一帧
- 可以保持时间连续性
- 扩展的视频会自然地接续原始视频

## 三、正确的实现方式

### 3.1 从生成的视频中获取 Video 对象

当我们生成视频时，会得到 `generated_video.video`，这是一个 `Video` 对象：

```python
# 生成视频后的处理
generated_video = operation.response.generated_videos[0]
video_obj = generated_video.video  # ✅ 这是 Video 对象
google_file_id = video_obj.uri  # 格式："files/xxx"
```

### 3.2 从 File ID 重新获取 Video 对象

如果只有 File ID，需要：
1. 使用 File ID 获取 File 对象
2. 从 File 对象构造 Video 对象
3. 或者通过其他方式获取 Video 对象

**方法1：使用 client.files.get() 获取 File，然后构造 Video**

```python
# 从 File ID 获取 File 对象
file_obj = client.files.get(name=google_file_id)

# 构造 Video 对象
video_obj = types.Video(uri=google_file_id)  # ⚠️ 需要验证是否正确
```

**方法2：直接使用 Video 对象（推荐）**

```python
# 直接使用 Video 对象，而不是 File 对象
video_obj = types.Video(uri=google_file_id)  # URI 格式："files/xxx"

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=video_obj,  # ✅ 使用 Video 对象
    prompt=prompt,
    config=config
)
```

### 3.3 修复后的代码

```python
async def extend_video(
    self,
    video_url: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    negative_prompt: Optional[str] = None,
    duration: int = 8,
    resolution: str = "720p",
    google_file_id: Optional[str] = None
) -> Dict[str, Any]:
    """扩展视频."""
    
    # 步骤1: 获取 Video 对象（不是 File 对象）
    if google_file_id:
        # ✅ 修复：使用 Video 对象，而不是 File 对象
        # Video 对象的 uri 格式是 "files/xxx"
        google_video = types.Video(uri=google_file_id)
    else:
        # 从 OSS 下载并上传到 Google
        temp_video_path = await self._download_video_from_oss(video_url)
        google_file = await self._upload_video_to_google(temp_video_path)
        # ✅ 修复：从 File 对象构造 Video 对象
        google_video = types.Video(uri=google_file.name)
        self._cleanup_temp_files([temp_video_path])
    
    # 步骤2: 创建视频扩展任务（使用 Video 对象）
    operation = await self._create_extension_task(
        video=google_video,  # ✅ 现在是 Video 对象
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt,
        duration=duration,
        resolution=resolution
    )
    
    # ... 后续处理
```

## 四、Prompt 编写建议

### 4.1 好的 Prompt 示例

✅ **正确**：描述接下来发生的事情
```
"Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower."
```

✅ **正确**：接续动作
```
"The car continues driving down the winding mountain road, revealing a beautiful sunset ahead."
```

✅ **正确**：自然延续
```
"The dancer completes the spin and gracefully moves into the next sequence, extending her arms upward."
```

### 4.2 不好的 Prompt 示例

❌ **错误**：重新描述整个场景
```
"A butterfly flies in a garden with flowers."  # 这更像是在生成新视频
```

❌ **错误**：不描述延续
```
"Make it longer."  # 太模糊
```

❌ **错误**：改变场景
```
"A dog runs in a park."  # 如果原视频是蝴蝶，这不连贯
```

### 4.3 Prompt 编写原则

1. **描述动作的延续**：说明接下来会发生什么
2. **保持场景一致**：延续原视频的场景和主题
3. **具体明确**：避免模糊的描述
4. **自然过渡**：描述的动作应该从原视频的最后一帧自然延伸

## 五、参数配置详解

### 5.1 GenerateVideosConfig 参数

```python
config = types.GenerateVideosConfig(
    number_of_videos=1,           # 生成视频数量（固定为1）
    resolution="720p",             # 分辨率："720p" 或 "1080p"
    aspect_ratio="16:9",           # 长宽比："16:9" 或 "9:16"
    duration_seconds=8,            # 时长：4、6、8秒
    negative_prompt="..."          # 反向提示词（可选）
)
```

### 5.2 参数限制

| 参数 | 限制 | 说明 |
|------|------|------|
| `resolution` | "720p" 或 "1080p" | 1080p 仅支持 8 秒时长 |
| `aspect_ratio` | "16:9" 或 "9:16" | 必须与原视频一致 |
| `duration_seconds` | 4、6、8 | 扩展视频必须为 8 秒（根据文档） |
| `video` | `types.Video` | **必须是 Video 对象** |

### 5.3 重要约束

根据官方文档：
- **扩展视频的时长必须为 8 秒**（当使用扩展功能时）
- **分辨率必须与原视频一致**
- **长宽比必须与原视频一致**

## 六、完整示例

### 6.1 完整的视频扩展流程

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

# 1. 生成原始视频（或从已有视频获取 Video 对象）
original_operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A butterfly flies out of a French door.",
    config=types.GenerateVideosConfig(
        resolution="720p",
        aspect_ratio="16:9",
        duration_seconds=4
    )
)

# 轮询原始视频
while not original_operation.done:
    time.sleep(10)
    original_operation = client.operations.get(original_operation)

# 获取 Video 对象
original_video = original_operation.response.generated_videos[0].video

# 2. 扩展视频（使用 Video 对象）
extension_prompt = "Track the butterfly into the garden as it lands on an orange origami flower."

extension_operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=original_video,  # ✅ 使用 Video 对象
    prompt=extension_prompt,
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        resolution="720p",  # 必须与原视频一致
        aspect_ratio="16:9",  # 必须与原视频一致
        duration_seconds=8  # 扩展必须为 8 秒
    )
)

# 轮询扩展视频
while not extension_operation.done:
    print("Waiting for video extension to complete...")
    time.sleep(10)
    extension_operation = client.operations.get(extension_operation)

# 下载扩展后的视频
extended_video = extension_operation.response.generated_videos[0]
client.files.download(file=extended_video.video)
extended_video.video.save("extended_video.mp4")
```

## 七、修复建议

### 7.1 立即修复

1. **修改 `extend_video` 方法**：使用 `types.Video` 而不是 `types.File`
2. **修改 `_create_extension_task` 方法**：确保接收的是 `Video` 对象
3. **更新文档**：说明 Video 和 File 的区别

### 7.2 代码修改点

**文件**：`backend/app/services/google_veo_service.py`

**修改位置1**：`extend_video` 方法（约第95-98行）
```python
# 修改前
if google_file_id:
    google_video = types.File(name=google_file_id)

# 修改后
if google_file_id:
    # ✅ 使用 Video 对象，URI 格式是 "files/xxx"
    google_video = types.Video(uri=google_file_id)
```

**修改位置2**：`extend_video` 方法（约第102-105行）
```python
# 修改前
temp_video_path = await self._download_video_from_oss(video_url)
google_video = await self._upload_video_to_google(temp_video_path)

# 修改后
temp_video_path = await self._download_video_from_oss(video_url)
google_file = await self._upload_video_to_google(temp_video_path)
# ✅ 从 File 对象构造 Video 对象
google_video = types.Video(uri=google_file.name)
```

**修改位置3**：`_create_extension_task` 方法签名（约第260行）
```python
# 修改前
async def _create_extension_task(
    self,
    video: types.File,  # ❌

# 修改后
async def _create_extension_task(
    self,
    video: types.Video,  # ✅
```

## 八、测试验证

### 8.1 测试步骤

1. 生成一个原始视频（4秒）
2. 保存 Video 对象的 URI（google_file_id）
3. 使用该 URI 创建 Video 对象
4. 进行视频扩展（8秒）
5. 检查扩展后的视频是否与原始视频连贯

### 8.2 预期结果

- ✅ 扩展视频应该从原始视频的最后一帧开始
- ✅ 动作应该自然延续
- ✅ 场景应该保持一致
- ✅ 视频应该连贯流畅

## 九、总结

**核心问题**：我们使用了 `File` 对象而不是 `Video` 对象进行视频扩展。

**解决方案**：
1. 使用 `types.Video(uri=google_file_id)` 创建 Video 对象
2. 确保 `generate_videos` 的 `video` 参数接收 Video 对象
3. 正确编写扩展 Prompt，描述接下来的动作

**关键要点**：
- Video 对象包含完整的视频上下文信息
- File 对象只是文件引用，缺少上下文
- Prompt 应该描述动作的延续，而不是重新描述场景

