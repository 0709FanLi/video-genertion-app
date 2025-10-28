# OSS文件上传功能集成文档

## 📦 功能概述

已成功集成阿里云OSS文件存储服务，实现参考图上传到云端存储。

---

## ✅ 已实现功能

### 后端功能
1. ✅ **OSS服务类** (`oss_service.py`)
   - 文件上传到OSS
   - 从URL下载并上传到OSS（用于AI生成结果）
   - 文件删除
   - 文件列表
   - 健康检查

2. ✅ **文件上传API** (`/api/files`)
   - `POST /api/files/upload` - 通用文件上传
   - `POST /api/files/upload/reference` - 参考图上传（便捷接口）
   - `GET /api/files/list` - 列举文件
   - `DELETE /api/files/{path}` - 删除文件
   - `GET /api/files/health` - OSS健康检查

3. ✅ **配置管理**
   - OSS配置添加到 `config.py`
   - AccessKey、Bucket、Endpoint等参数

### 前端功能
1. ✅ **参考图上传集成**
   - 用户上传参考图 → 自动上传到OSS
   - 显示上传进度
   - 上传成功后使用OSS URL
   - 替换原有的本地base64方案

2. ✅ **API服务层** (`api.js`)
   - `fileUploadAPI.uploadFile()` - 通用文件上传
   - `fileUploadAPI.uploadReferenceImage()` - 参考图上传
   - `fileUploadAPI.listFiles()` - 列举文件
   - `fileUploadAPI.deleteFile()` - 删除文件

---

## 🔧 配置信息

### OSS配置
```python
# backend/app/core/config.py
oss_access_key_id: str = os.getenv("OSS_ACCESS_KEY_ID", "")
oss_access_key_secret: str = os.getenv("OSS_ACCESS_KEY_SECRET", "")
oss_endpoint: str = "https://oss-cn-shanghai.aliyuncs.com"  # 华东2上海
oss_bucket_name: str = "tool251027"
oss_public_read: bool = True  # Bucket为公共读
oss_url_expire_seconds: int = 3600  # 签名URL有效期
oss_max_file_size: int = 10 * 1024 * 1024  # 最大10MB
```

### 目录结构
```
tool251027/  (OSS Bucket)
├── images/              # 生成的图片
│   └── 2025/01/27/     # 按日期分类
├── videos/              # 生成的视频
│   └── 2025/01/27/
├── references/          # 参考图（用户上传）
│   └── 2025/01/27/
│       └── abc12345_cat.jpg
└── uploads/             # 其他上传文件
```

---

## 🎯 使用方式

### 1. 前端上传参考图

**用户操作**:
1. 在文生图页面点击"上传参考图"
2. 选择图片文件（最大10MB）
3. 自动上传到OSS
4. 显示上传进度
5. 成功后显示图片预览

**技术实现**:
```javascript
// frontend/src/components/TextToImage/ReferenceUpload.jsx
const handleUpload = async ({ file }) => {
  const result = await fileUploadAPI.uploadReferenceImage(file);
  addReferenceImage({
    url: result.url,  // OSS URL
    objectKey: result.object_key,
    name: file.name,
    size: result.size
  });
};
```

### 2. API调用示例

**上传文件**:
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.jpg" \
  -F "category=references"
```

**响应**:
```json
{
  "object_key": "references/2025/01/27/abc12345_test.jpg",
  "url": "https://tool251027.oss-cn-shanghai.aliyuncs.com/references/2025/01/27/abc12345_test.jpg",
  "size": 102400,
  "content_type": "image/jpeg",
  "bucket": "tool251027"
}
```

**健康检查**:
```bash
curl http://localhost:8000/api/files/health
```

**响应**:
```json
{
  "status": "healthy",
  "bucket": "tool251027",
  "endpoint": "https://oss-cn-shanghai.aliyuncs.com",
  "public_read": true
}
```

---

## 📝 API文档

完整API文档: http://localhost:8000/docs

### 主要接口

#### 1. 上传文件
- **URL**: `POST /api/files/upload`
- **参数**:
  - `file`: 文件（必填）
  - `category`: 类别（可选，默认uploads）
- **返回**: UploadResponse

#### 2. 上传参考图
- **URL**: `POST /api/files/upload/reference`
- **参数**:
  - `file`: 图片文件（必填）
- **返回**: UploadResponse

#### 3. 列举文件
- **URL**: `GET /api/files/list`
- **参数**:
  - `prefix`: 路径前缀（可选）
  - `max_keys`: 最大数量（可选，默认100）
- **返回**: FileListResponse

#### 4. 删除文件
- **URL**: `DELETE /api/files/{path}`
- **参数**:
  - `path`: 文件路径（必填）
- **返回**: DeleteResponse

---

## 🔒 安全说明

### 已实现的安全措施
1. ✅ **文件大小限制**: 最大10MB
2. ✅ **文件类型验证**: 前后端双重验证
3. ✅ **唯一文件名**: UUID + 原始文件名
4. ✅ **按日期分类**: 便于管理和清理
5. ✅ **公共读权限**: Bucket设置为公共读

### 建议的改进措施
1. ⚠️ **AccessKey加密**: 
   - 当前硬编码在config.py
   - 建议: 移到环境变量 `.env` 文件
   
2. ⚠️ **ECS生产环境**: 
   - 如果部署到ECS，建议使用实例RAM角色
   - 参考 `oss.md` 的最佳实践

3. ⚠️ **定期清理**: 
   - 建议定期清理临时文件
   - 可使用OSS生命周期规则

---

## 🧪 测试验证

### 1. 健康检查测试
```bash
curl http://localhost:8000/api/files/health
```
✅ **结果**: 
```json
{
  "status": "healthy",
  "bucket": "tool251027",
  "endpoint": "https://oss-cn-shanghai.aliyuncs.com",
  "public_read": true
}
```

### 2. 手动测试清单

#### 前端测试
- [ ] 打开 http://localhost:5173/text-to-image
- [ ] 选择"通义万相多图生图"模型
- [ ] 点击"上传参考图"
- [ ] 选择一张图片（<10MB）
- [ ] 观察上传进度提示
- [ ] 验证图片预览是否显示
- [ ] 检查浏览器Network，确认调用了 `/api/files/upload/reference`
- [ ] 在阿里云OSS控制台查看文件是否上传成功

#### 后端测试
```bash
# 1. 创建测试图片
echo "test" > test.jpg

# 2. 上传测试
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@test.jpg" \
  -F "category=uploads"

# 3. 列举文件
curl "http://localhost:8000/api/files/list?prefix=uploads/"

# 4. 删除文件
curl -X DELETE "http://localhost:8000/api/files/uploads/2025/01/27/xxxxx_test.jpg"
```

---

## 📊 文件清单

### 新增文件 (3个)
1. `backend/app/services/oss_service.py` - OSS服务类
2. `backend/app/api/routes/file_upload.py` - 文件上传API
3. `OSS_INTEGRATION.md` - 本文档

### 修改文件 (6个)
1. `backend/requirements.txt` - 添加 `oss2==2.18.4`
2. `backend/app/core/config.py` - 添加OSS配置
3. `backend/app/main.py` - 注册文件上传路由
4. `frontend/src/services/api.js` - 添加 `fileUploadAPI`
5. `frontend/src/components/TextToImage/ReferenceUpload.jsx` - 集成OSS上传
6. `frontend/src/store/imageStore.js` - 支持objectKey字段

---

## 🚀 下一步计划

### 待实现功能

#### 1. AI生成结果自动上传OSS (TODO)
当前AI生成的图片/视频URL是临时的，需要：
- 修改 `text_to_image.py` 的 `/generate` 接口
- AI生成完成后，调用 `oss_service.upload_from_url()`
- 将临时URL转为永久OSS URL
- 返回给前端

**实现代码**（示例）:
```python
# backend/app/api/routes/text_to_image.py
async def generate_image(request: TextToImageRequest):
    # ... AI生成图片 ...
    temp_image_urls = result.image_urls
    
    # 上传到OSS
    oss_image_urls = []
    for i, temp_url in enumerate(temp_image_urls):
        filename = f"generated_{i+1}.png"
        oss_result = oss_service.upload_from_url(
            url=temp_url,
            filename=filename,
            category="images"
        )
        oss_image_urls.append(oss_result['url'])
    
    return TextToImageResponse(
        image_urls=oss_image_urls,  # 返回OSS URL
        model=request.model,
        num_images=len(oss_image_urls)
    )
```

#### 2. 文件管理界面 (可选)
- 前端添加"文件管理"页面
- 列举已上传的文件
- 支持删除、预览

#### 3. OSS配置优化
- 将AccessKey移到 `.env` 文件
- 添加OSS配置验证
- 支持多Bucket配置

---

## ❓ 常见问题

### Q1: 上传失败，提示"AccessDenied"
**原因**: AccessKey权限不足或配置错误

**解决**:
1. 检查 `config.py` 中的AccessKey是否正确
2. 登录阿里云RAM控制台，确认用户有OSS权限
3. 检查Bucket名称和地域是否匹配

### Q2: 上传成功但无法访问图片
**原因**: Bucket权限设置为私有

**解决**:
1. 登录OSS控制台
2. 进入Bucket管理 → 权限管理
3. 设置为"公共读"或"公共读写"
4. 或使用签名URL访问

### Q3: 上传速度很慢
**原因**: 文件过大或网络问题

**解决**:
1. 压缩图片后上传
2. 检查网络连接
3. 考虑使用OSS加速域名

### Q4: 文件大小超过限制
**原因**: 当前限制10MB

**解决**:
1. 修改 `config.py` 的 `oss_max_file_size`
2. 压缩文件
3. 使用分片上传（大文件）

---

## 📞 技术支持

- **API文档**: http://localhost:8000/docs
- **OSS控制台**: https://oss.console.aliyun.com/
- **参考文档**: 查看 `oss.md`

---

## ✨ 技术亮点

1. **企业级架构**: 参考 `oss.md` 最佳实践
2. **安全措施**: 文件大小、类型验证，唯一文件名
3. **用户体验**: 上传进度提示，实时反馈
4. **可扩展性**: 支持多种文件类别，易于扩展
5. **错误处理**: 完善的异常捕获和用户提示

---

**开发完成时间**: 2025-01-27  
**开发者**: AI助手  
**状态**: ✅ 基础功能已完成，可以进行测试

