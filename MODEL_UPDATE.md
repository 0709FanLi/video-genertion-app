# 模型更新记录

## ✅ 视频生成模型更新 (2025-10-24)

### 问题
使用旧模型 `wanx-i2v-v1` 时报错：
```json
{
    "code": "InvalidParameter",
    "message": "Model not exist"
}
```

### 解决方案
更新为新模型：`wan2.5-i2v-preview`

### 更新的文件

#### 1. backend/app/services/wanx_service.py
**第237行**：
```python
# 旧版本
"model": "wanx-i2v-v1"

# 新版本
"model": "wan2.5-i2v-preview"
```

#### 2. backend/main.py (旧版本)
**第137行**：
```python
# 旧版本
"model": "wanx-i2v-v1"

# 新版本
"model": "wan2.5-i2v-preview"
```

### 模型信息

#### wan2.5-i2v-preview
- **类型**: 图生视频 (Image-to-Video)
- **状态**: Preview版本
- **功能**: 基于输入图片和提示词生成视频
- **输入参数**:
  - `img_url`: 参考图片URL
  - `prompt`: 视频动态描述提示词

### 重启服务

更新后需要重启后端服务：

```bash
# 方式1：使用脚本
./stop.sh
./start.sh

# 方式2：手动重启
# 停止旧进程
lsof -ti:8000 | xargs kill -9

# 启动新进程
cd backend
source venv/bin/activate
python -m app.main
```

### 验证更新

访问 API 文档查看更新：
- http://localhost:8000/docs

测试视频生成接口：
1. 先生成图片
2. 选择一张图片
3. 输入视频描述
4. 生成视频

### 注意事项

1. **Preview版本**: 这是预览版本，可能会有变化
2. **性能**: 新模型的性能和质量可能与旧版本不同
3. **定价**: 可能有不同的定价策略
4. **限制**: 注意API调用频率和配额限制

### 未来更新

当阿里云发布正式版本时，可能需要再次更新模型名称：
- `wan2.5-i2v-preview` → `wan2.5-i2v-v1`（猜测）

建议定期检查官方文档以获取最新信息。

---

**更新时间**: 2025-10-24  
**更新人**: AI Assistant  
**验证状态**: ✅ 已更新，待测试

