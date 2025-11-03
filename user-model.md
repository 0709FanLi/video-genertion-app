# 项目使用的AI模型清单

本文档列出了项目中使用的所有AI模型及其详细信息。

---

## 📸 文生图模型 (Text-to-Image)

### 1. 火山引擎即梦4.0
- **模型ID**: `jimeng_t2i_v40`
- **显示名称**: 火山引擎即梦4.0
- **供应商**: 火山引擎
- **状态**: ✅ 默认模型
- **功能特性**:
  - 支持参考图（最多6张）
  - 高质量图片生成
- **价格**: 0.2元/次
- **配置文件**: `backend/app/core/config.py` → `text_to_image_models["volc-jimeng"]`

### 2. 通义万相多图生图
- **模型ID**: `wan2.5-i2i-preview`
- **显示名称**: 通义万相多图生图
- **供应商**: 阿里云DashScope
- **状态**: ⚠️ 非默认
- **功能特性**:
  - 支持参考图（最多2张）
  - 多图融合生图
- **配置文件**: `backend/app/core/config.py` → `text_to_image_models["aliyun-wanx-i2i"]`

### 3. 通义千问文生图
- **模型ID**: `qwen-image-plus`
- **显示名称**: 通义千问文生图
- **供应商**: 阿里云DashScope
- **状态**: ⚠️ 非默认
- **功能特性**:
  - 不支持参考图    
  - 支持多种分辨率：
    - 1664×928 (16:9)
    - 1472×1140 (4:3)
    - 1328×1328 (1:1)
    - 1140×1472 (3:4)
    - 928×1664 (9:16)
- **配置文件**: `backend/app/core/config.py` → `text_to_image_models["aliyun-qwen-image"]`

---

## 🎬 视频生成模型 (Video Generation)

### 火山引擎即梦系列

#### 1. 文生视频 (Text-to-Video)
- **模型标识**: `volc-t2v`
- **内部模型ID**: `jimeng_t2v_v30_1080p`
- **显示名称**: 火山即梦 - 文生视频
- **供应商**: 火山引擎
- **功能特性**:
  - 纯文本生成视频，无需图片
  - 1080P高清输出
  - 支持5秒/10秒视频
  - 支持多种长宽比（16:9, 4:3, 1:1, 3:4, 9:16, 21:9）
- **价格**: 
  - 1080P: 0.63元/秒
  - 720P: 0.28元/秒
- **代码位置**: `backend/app/services/volc_video_service.py`

#### 2. 单图首帧 (Image-to-Video First Frame)
- **模型标识**: `volc-i2v-first`
- **内部模型ID**: `jimeng_i2v_first_v30`
- **显示名称**: 火山即梦 - 单图首帧
- **供应商**: 火山引擎
- **状态**: ✅ 默认模型
- **功能特性**:
  - 图生视频（首帧模式）
  - 1080P高清输出
  - 支持5秒/10秒视频
- **价格**: 
  - 1080P: 0.63元/秒
  - 720P: 0.28元/秒
- **代码位置**: `backend/app/services/volc_video_service.py`

#### 3. 首尾帧插值 (First-Tail Frame Interpolation)
- **模型标识**: `volc-i2v-first-tail`
- **内部模型ID**: `jimeng_i2v_first_tail_v30`
- **显示名称**: 火山即梦 - 首尾帧
- **供应商**: 火山引擎
- **功能特性**:
  - 图生视频（首尾帧插值模式）
  - 1080P高清输出
  - 支持5秒/10秒视频
- **价格**: 
  - 1080P: 0.63元/秒
  - 720P: 0.28元/秒
- **代码位置**: `backend/app/services/volc_video_service.py`

### 通义万相系列

#### 4. 万相2.2极速版
- **模型标识**: `wanx-kf2v-flash`
- **内部模型ID**: `wan2.2-kf2v-flash`
- **显示名称**: 通义万相 - 极速版
- **供应商**: 阿里云DashScope
- **功能特性**:
  - 首尾帧生视频
  - 支持480P/720P/1080P分辨率
  - 固定5秒视频
  - 支持智能prompt改写
- **代码位置**: `backend/app/services/wanx_kf2v_service.py`

#### 5. 万相2.1专业版
- **模型标识**: `wanx-kf2v-plus`
- **内部模型ID**: `wanx2.1-kf2v-plus`
- **显示名称**: 通义万相 - 专业版
- **供应商**: 阿里云DashScope
- **功能特性**:
  - 首尾帧生视频
  - 支持480P/720P/1080P分辨率
  - 固定5秒视频
  - 支持智能prompt改写
- **代码位置**: `backend/app/services/wanx_kf2v_service.py`

### Google Veo 3.1系列

#### 6. Google Veo 文生视频
- **模型标识**: `google-veo-t2v`
- **内部模型ID**: `veo-3.1-generate-preview`
- **显示名称**: Google Veo 3.1 - 文生视频
- **供应商**: Google Gemini
- **功能特性**:
  - 纯文本生成视频
  - 固定720P分辨率
  - 支持4/6/8秒视频
  - 支持多种长宽比（16:9, 9:16）
  - 支持负面提示词（negative prompt）
- **代码位置**: `backend/app/services/google_veo_service.py`

#### 7. Google Veo 单图首帧
- **模型标识**: `google-veo-i2v-first`
- **内部模型ID**: `veo-3.1-generate-preview`
- **显示名称**: Google Veo 3.1 - 单图首帧
- **供应商**: Google Gemini
- **功能特性**:
  - 图生视频（单图首帧模式）
  - 固定720P分辨率
  - 支持4/6/8秒视频
  - 支持多种长宽比（16:9, 9:16）
  - 支持负面提示词（negative prompt）
  - **注意**: 可直接使用Base64格式，无需OSS
- **代码位置**: `backend/app/services/google_veo_service.py`

#### 8. Google Veo 首尾帧插值
- **模型标识**: `google-veo-i2v-first-tail`
- **内部模型ID**: `veo-3.1-generate-preview`
- **显示名称**: Google Veo 3.1 - 首尾帧插值
- **供应商**: Google Gemini
- **功能特性**:
  - 图生视频（首尾帧插值模式）
  - 固定720P分辨率
  - 支持4/6/8秒视频
  - 支持多种长宽比（16:9, 9:16）
  - 支持负面提示词（negative prompt）
  - **注意**: 可直接使用Base64格式，无需OSS
- **代码位置**: `backend/app/services/google_veo_service.py`

### Sora 2 系列

#### 9. Sora 2 竖屏 10秒
- **模型标识**: `sora-v2-portrait`
- **内部模型ID**: `sora_video2`
- **显示名称**: Sora 2 - 竖屏 10s
- **供应商**: Sora API (第三方)
- **功能特性**:
  - 文生视频/图生视频
  - 竖屏格式（9:16）
  - 固定10秒视频
- **代码位置**: `backend/app/services/sora_service.py`

#### 10. Sora 2 横屏 10秒
- **模型标识**: `sora-v2-landscape`
- **内部模型ID**: `sora_video2-landscape`
- **显示名称**: Sora 2 - 横屏 10s
- **供应商**: Sora API (第三方)
- **功能特性**:
  - 文生视频/图生视频
  - 横屏格式（16:9）
  - 固定10秒视频
- **代码位置**: `backend/app/services/sora_service.py`

#### 11. Sora 2 竖屏 15秒
- **模型标识**: `sora-v2-portrait-15s`
- **内部模型ID**: `sora_video2-15s`
- **显示名称**: Sora 2 - 竖屏 15s
- **供应商**: Sora API (第三方)
- **功能特性**:
  - 文生视频/图生视频
  - 竖屏格式（9:16）
  - 固定15秒视频
- **代码位置**: `backend/app/services/sora_service.py`

#### 12. Sora 2 横屏 15秒
- **模型标识**: `sora-v2-landscape-15s`
- **内部模型ID**: `sora_video2-landscape-15s`
- **显示名称**: Sora 2 - 横屏 15s
- **供应商**: Sora API (第三方)
- **功能特性**:
  - 文生视频/图生视频
  - 横屏格式（16:9）
  - 固定15秒视频
- **代码位置**: `backend/app/services/sora_service.py`

---

## 🎞️ 视频扩展模型 (Video Extension)

### Google Veo 3.1 视频扩展
- **模型标识**: `google-veo-3.1`
- **内部模型ID**: `veo-3.1-generate-preview`
- **显示名称**: Google Veo 3.1
- **供应商**: Google Gemini
- **功能特性**:
  - 视频时长扩展
  - 固定720P分辨率
  - 固定8秒输出
  - 支持16:9和9:16长宽比
  - 支持负面提示词（negative prompt）
- **配置文件**: `backend/app/core/config.py` → `video_extension_models["google-veo-3.1"]`
- **代码位置**: `backend/app/services/google_veo_service.py`

---

## 💬 提示词优化模型 (Prompt Optimization)

### 1. 通义千问
- **模型ID**: `qwen-plus`
- **显示名称**: 通义千问 (系统默认)
- **供应商**: 阿里云DashScope
- **状态**: ✅ 默认模型
- **功能特性**:
  - 提示词优化和扩展
  - 支持JSON格式输出
- **配置文件**: `backend/app/core/config.py` → `prompt_optimization_models["qwen-plus"]`
- **代码位置**: `backend/app/services/llm_service.py`

### 2. DeepSeek-V3.2-Exp
- **模型ID**: `deepseek-chat`
- **显示名称**: DeepSeek-V3.2-Exp
- **供应商**: DeepSeek
- **状态**: ⚠️ 非默认
- **功能特性**:
  - 提示词优化和扩展
  - 长文本处理能力强
- **配置文件**: `backend/app/core/config.py` → `prompt_optimization_models["deepseek-v3"]`
- **代码位置**: `backend/app/services/deepseek_service.py`

---

## 👁️ 视觉理解模型 (Vision Understanding)

### 通义千问视觉理解
- **模型ID**: `qwen3-vl-plus`
- **显示名称**: 通义千问视觉理解
- **供应商**: 阿里云DashScope
- **功能特性**:
  - 图片内容分析
  - 生成适合视频生成的描述文本
  - 支持思考模式（thinking mode）
  - 支持Base64和URL格式图片输入
- **代码位置**: `backend/app/services/qwen_vl_service.py`
- **使用场景**: 图片智能分析功能，将图片转换为视频描述提示词

---

## 🔄 遗留/备用模型 (Legacy/Backup Models)

以下模型在代码中存在，但可能不是主要使用的模型：

### 1. 通义万相 v1 (文生图)
- **模型ID**: `wanx-v1`
- **供应商**: 阿里云DashScope
- **状态**: ⚠️ 遗留代码
- **使用位置**: `backend/app/services/wanx_service.py`
- **说明**: 旧版文生图模型，新版本使用 `wan2.5-i2i-preview`

### 2. 通义万相 2.5 (图生视频预览版)
- **模型ID**: `wan2.5-i2v-preview`
- **供应商**: 阿里云DashScope
- **状态**: ⚠️ 遗留代码
- **使用位置**: `backend/app/services/wanx_service.py`
- **说明**: 旧版图生视频模型，新版本使用 `wan2.2-kf2v-flash` 和 `wanx2.1-kf2v-plus`

---

## 📊 模型使用统计

### 按供应商分类

| 供应商 | 活跃模型数 | 遗留模型数 | 模型类型 |
|--------|----------|----------|---------|
| 火山引擎 | 4 | 0 | 文生图(1) + 视频生成(3) |
| 阿里云DashScope | 6 | 2 | 文生图(2) + 视频生成(2) + 提示词优化(1) + 视觉理解(1) |
| Google Gemini | 4 | 0 | 视频生成(3) + 视频扩展(1) |
| Sora API | 4 | 0 | 视频生成(4) |
| DeepSeek | 1 | 0 | 提示词优化(1) |

### 按功能分类

| 功能类型 | 活跃模型数 | 遗留模型数 |
|---------|----------|----------|
| 文生图 | 3 | 1 |
| 视频生成 | 12 | 1 |
| 视频扩展 | 1 | 0 |
| 提示词优化 | 2 | 0 |
| 视觉理解 | 1 | 0 |

---

## 🔧 配置说明

### 环境变量要求

1. **火山引擎**
   - `VOLC_ACCESS_KEY_ID`
   - `VOLC_SECRET_ACCESS_KEY`

2. **阿里云DashScope**
   - `DASHSCOPE_API_KEY`

3. **Google Gemini/Veo**
   - `GEMINI_API_KEY`

4. **Sora API**
   - `SORA_API_KEY`

5. **DeepSeek**
   - `DEEPSEEK_API_KEY`

6. **OSS存储**（用于图片/视频存储）
   - `OSS_ACCESS_KEY_ID`
   - `OSS_ACCESS_KEY_SECRET`
   - `OSS_BUCKET_NAME`
   - `OSS_ENDPOINT`（可选）

### 配置文件位置

- **主要配置**: `backend/app/core/config.py`
- **模型枚举**: `backend/app/schemas/image_to_video.py` → `VideoModel`
- **前端模型选择**: `frontend/src/components/ImageToVideo/ModelSelector.jsx`

---

## 📝 更新记录

- **2025-11-01**: 初始版本，包含所有已集成的模型
- 本文档会根据模型更新而持续维护

---

## 📌 注意事项

1. **Google Veo模型**可以直接使用Base64格式图片，无需OSS服务
2. **其他视频生成模型**需要先将Base64图片上传到OSS，转换为URL格式
3. **Sora 2模型**固定时长，不支持自定义时长
4. **火山引擎模型**支持多种分辨率，价格根据分辨率不同
5. 所有模型配置都可以通过修改 `backend/app/core/config.py` 进行调整

