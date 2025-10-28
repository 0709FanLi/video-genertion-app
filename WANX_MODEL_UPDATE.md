# 通义万相模型更新文档

## 📋 更新时间
2025-10-28

## 🎯 更新内容

### 1. **删除 wanx-v1 模型**
根据用户需求，文生图功能暂不需要 `wanx-v1` 模型，已完全移除相关代码。

### 2. **修复 wan2.5-i2i-preview 模型**
根据官方文档（通义万相多图生图接口文档），修复了 `wan2.5-i2i-preview` 模型的实现。

---

## 📝 具体修改

### 1. 配置文件 `/backend/app/core/config.py`

#### 删除的模型：
```python
# ❌ 已删除
"aliyun-wanx": {
    "name": "通义万相 wanx-v1", 
    "model_id": "wanx-v1",
    "default": False,
    "supports_reference": False
}
```

#### 更新的配置：
```python
text_to_image_models: dict = {
    "volc-jimeng": {
        "name": "火山引擎即梦4.0",
        "model_id": "jimeng_t2i_v40",
        "default": True,
        "supports_reference": True,
        "max_reference_images": 6  # 最多6张参考图
    },
    "aliyun-wanx-i2i": {
        "name": "通义万相多图生图",
        "model_id": "wan2.5-i2i-preview",
        "default": False,
        "supports_reference": True,
        "max_reference_images": 2  # ✅ 改为2张（根据文档）
    }
}
```

---

### 2. 服务层 `/backend/app/services/wanx_i2i_service.py`

#### 关键修复：

1. **参考图数量限制**
```python
# 之前：4张
MAX_REFERENCE_IMAGES = 4

# 现在：2张（根据文档）
MAX_REFERENCE_IMAGES = 2
```

2. **API URL修复**
```python
# ❌ 之前：错误的URL
url = f"{self.base_url}/services/aigc/multimodal-generation/generation"

# ✅ 现在：正确的URL
url = f"{self.base_url}/services/aigc/image2image/image-synthesis"
```

3. **参数名修复**
```python
# ❌ 之前：错误的参数名
input_data = {
    "prompt": prompt,
    "ref_img": reference_image_urls[0],
    "ref_imgs": reference_image_urls
}

# ✅ 现在：正确的参数名
input_data = {
    "prompt": prompt,
    "images": reference_image_urls  # 参数名为 images
}
```

4. **移除不存在的参数**
```python
# ❌ 之前：文档中没有 size 参数
payload = {
    "model": self.MODEL_ID,
    "input": input_data,
    "parameters": {
        "size": size,  # 文档中没有这个参数
        "n": num_images
    }
}

# ✅ 现在：只传递文档中的参数
payload = {
    "model": self.MODEL_ID,
    "input": input_data,
    "parameters": {
        "n": num_images  # 只传 n 参数
    }
}
```

5. **基础URL和轮询间隔优化**
```python
# 之前
self.base_url = settings.wanx_base_url  # 可能不正确
self.poll_interval = settings.task_poll_interval  # 可能太短

# 现在：根据文档固定配置
self.base_url = "https://dashscope.aliyuncs.com/api/v1"  # 固定URL
self.poll_interval = 10  # 10秒轮询间隔（文档建议）
self.max_poll_attempts = 36  # 最多6分钟（36次 * 10秒）
```

---

### 3. API路由 `/backend/app/api/routes/text_to_image.py`

#### 删除的代码：
```python
# ❌ 已删除 wanx-v1 相关导入和处理
from app.services.wanx_service import wanx_service

elif request.model == "aliyun-wanx":
    # 通义万相 wanx-v1
    result = await wanx_service.generate_images(
        prompt=request.prompt,
        n=request.num_images
    )
    results = result.get("output", {}).get("results", [])
    image_urls = [item.get("url") for item in results if item.get("url")]
```

#### 简化的代码：
```python
# ✅ 只保留两个模型
if request.model == "volc-jimeng":
    # 火山引擎即梦4.0（支持最多6张参考图）
    image_urls = await volc_jimeng_service.generate_image(...)

elif request.model == "aliyun-wanx-i2i":
    # 通义万相多图生图（支持最多2张参考图）
    image_urls = await wanx_i2i_service.generate_image(
        prompt=request.prompt,
        reference_image_urls=request.reference_image_urls,
        size=request.size,
        num_images=request.num_images
    )
```

---

## 📊 通义万相多图生图 API 详解

### 核心参数对照

| 参数路径 | 类型 | 必选 | 限制 | 说明 |
|---------|------|------|------|------|
| `model` | string | ✅ | - | 固定值：`wan2.5-i2i-preview` |
| `input.prompt` | string | ✅ | ≤2000字符 | 正向提示词 |
| **`input.images`** | **array** | ✅ | **≤2张** | **参考图URL数组** ⭐ |
| `input.negative_prompt` | string | ❌ | ≤500字符 | 反向提示词 |
| `parameters.n` | integer | ❌ | 1-4 | 生成图片数量，默认4 |
| `parameters.watermark` | boolean | ❌ | - | 是否添加水印 |
| `parameters.seed` | integer | ❌ | [0, 2147483647] | 随机数种子 |

### 图片限制

| 项目 | 限制 |
|------|------|
| **格式** | JPEG、JPG、PNG（不支持透明通道）、BMP、WEBP |
| **分辨率** | 宽高范围均为 [384, 5000] 像素 |
| **文件大小** | 不超过 10MB |
| **数量** | **最多2张** ⭐ |

### API调用流程

```
步骤1: 创建任务
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis
Headers:
  - Authorization: Bearer sk-xxxx
  - X-DashScope-Async: enable
  - Content-Type: application/json

Body:
{
  "model": "wan2.5-i2i-preview",
  "input": {
    "prompt": "将图1中的闹钟放置到图2的餐桌的花瓶旁边位置",
    "images": [
      "https://example.com/image1.png",
      "https://example.com/image2.png"
    ]
  },
  "parameters": {
    "n": 1
  }
}

Response:
{
  "output": {
    "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx",
    "task_status": "PENDING"
  }
}

↓

步骤2: 轮询查询结果（建议10秒间隔）
GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}
Headers:
  - Authorization: Bearer sk-xxxx

Response (完成):
{
  "output": {
    "task_id": "7f4836cd-1c47-41b3-b3a4-xxxxxx",
    "task_status": "SUCCEEDED",
    "results": [
      {
        "orig_prompt": "...",
        "url": "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/xxx.png?Expires=xxx"
      }
    ]
  },
  "usage": {
    "image_count": 1
  }
}
```

### 任务状态流转

```
PENDING (排队中) 
   ↓
RUNNING (处理中)
   ↓
SUCCEEDED (成功) / FAILED (失败) / CANCELED (取消)
```

---

## ✅ 修复总结

### 已删除
- ✅ wanx-v1 模型配置
- ✅ wanx_service 导入和调用
- ✅ aliyun-wanx 路由处理

### 已修复
- ✅ wan2.5-i2i-preview 参考图数量：4张 → 2张
- ✅ API URL：错误路径 → 正确路径
- ✅ 参数名：`ref_img`/`ref_imgs` → `images`
- ✅ 移除不存在的 `size` 参数
- ✅ 优化轮询间隔：根据文档建议设为10秒
- ✅ 固定基础URL：使用正确的阿里云地址

---

## 📚 参考文档

- **通义万相多图生图**: https://bailian.console.aliyun.com/
- **API签名**: https://help.aliyun.com/document_detail/xxx.html
- **本地文档**: `/tongyi.md`

---

## 🎯 当前支持的模型

| 模型 | 模型ID | 默认 | 支持参考图 | 最多张数 |
|------|--------|------|-----------|---------|
| 火山引擎即梦4.0 | `jimeng_t2i_v40` | ✅ | ✅ | 6张 |
| 通义万相多图生图 | `wan2.5-i2i-preview` | ❌ | ✅ | 2张 |

---

## ⚠️ 注意事项

1. **图片URL有效期**: 返回的图片URL仅保留24小时，请及时下载
2. **任务查询**: 建议采用10秒轮询间隔
3. **内容审核**: 输入和输出都会经过内容安全审核
4. **数量限制**: wan2.5-i2i-preview 最多支持2张参考图
5. **提示词长度**: 最长2000字符

---

## 🚀 测试用例

### 单图参考
```bash
curl -X POST http://localhost:8000/api/text-to-image/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "aliyun-wanx-i2i",
    "prompt": "将背景换成演唱会现场",
    "num_images": 1,
    "size": "1024x1024",
    "reference_image_urls": ["https://example.com/image1.jpg"]
  }'
```

### 双图参考
```bash
curl -X POST http://localhost:8000/api/text-to-image/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "aliyun-wanx-i2i",
    "prompt": "将图1中的闹钟放置到图2的餐桌旁边",
    "num_images": 1,
    "size": "1024x1024",
    "reference_image_urls": [
      "https://example.com/image1.jpg",
      "https://example.com/image2.jpg"
    ]
  }'
```

---

**修复完成！现在 wan2.5-i2i-preview 模型已按照官方文档正确实现。** 🎉

