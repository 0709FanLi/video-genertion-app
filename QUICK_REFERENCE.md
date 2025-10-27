# 快速参考卡

## 🚀 服务管理

### 启动服务
```bash
./start.sh
```

### 停止服务
```bash
./stop.sh
```

### 查看状态
```bash
./status.sh
```

### 查看日志
```bash
./logs.sh
```

### 重启服务
```bash
./stop.sh && ./start.sh
```

## 🔗 访问地址

- **前端应用**: http://localhost:5173
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🎬 使用流程

1. **输入想法** → 生成3个图片提示词
2. **选择提示词** → 生成4张图片 (1-2分钟)
3. **选择图片** → 作为视频首帧
4. **输入视频描述** → 生成视频 (3-5分钟)

## 🤖 当前模型

### 文生图
- **模型**: `wanx-v1`
- **功能**: 文本 → 图片
- **数量**: 4张/次
- **分辨率**: 1024x1024

### 图生视频
- **模型**: `wan2.5-i2v-preview` ✨ (最新)
- **功能**: 图片 + 提示词 → 视频
- **时长**: 3-10秒
- **首帧**: 使用选中的图片

## ⚙️ 配置文件

### 环境变量
```bash
# 文件位置
backend/.env

# 关键配置
DASHSCOPE_API_KEY=your-api-key-here
LOG_LEVEL=INFO
```

### 模型配置
```bash
# 文生图模型
backend/app/services/wanx_service.py:98
model: "wanx-v1"

# 视频生成模型  
backend/app/services/wanx_service.py:237
model: "wan2.5-i2v-preview"
```

## 🐛 常见问题

### Q: 视频生成失败 "Model not exist"
**A**: 
1. 确认已重启服务
2. 检查模型名称是否为 `wan2.5-i2v-preview`
3. 清理Python缓存：`find backend -name "*.pyc" -delete`

### Q: 图片生成很慢
**A**: 正常现象，通常需要1-2分钟，请耐心等待

### Q: 前端无法连接后端
**A**:
1. 检查后端是否启动：`./status.sh`
2. 查看后端日志：`tail backend.log`
3. 确认端口8000未被占用

### Q: 如何修改API密钥
**A**:
1. 编辑 `backend/.env`
2. 修改 `DASHSCOPE_API_KEY=新密钥`
3. 重启服务：`./stop.sh && ./start.sh`

## 📁 项目结构

```
video_generation_app/
├── backend/
│   ├── app/              # 应用代码
│   │   ├── api/         # API路由
│   │   ├── services/    # 业务逻辑
│   │   ├── schemas/     # 数据模型
│   │   └── main.py      # 入口文件
│   ├── .env             # 环境配置
│   └── requirements.txt # 依赖列表
├── frontend/
│   └── src/
│       └── App.jsx      # React主组件
├── start.sh             # 启动脚本
├── stop.sh              # 停止脚本
└── logs.sh              # 日志查看
```

## 📊 日志位置

- **后端日志**: `backend.log`
- **前端日志**: `frontend.log`  
- **应用日志**: `backend/app.log`

查看实时日志：
```bash
tail -f backend.log
```

## 🔧 开发命令

### 安装依赖
```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 运行测试
```bash
cd backend
pytest
```

### 代码格式化
```bash
cd backend
black app/ tests/
```

### 类型检查
```bash
cd backend
mypy app/
```

## 💡 提示词技巧

### 图片提示词
```
A photorealistic [主体] [动作] in [场景],
[光线描述], [风格], [画质要求]
```

### 视频提示词
```
[主体]的[小动作]，[环境变化]，
镜头[运动方式]，[画质要求]
```

**示例**:
```
猫的尾巴轻轻摇摆，海浪轻拍沙滩，
镜头缓慢推进，电影级画质
```

## 🎯 性能优化

### 减少等待时间
1. 文生图：将数量从4张改为1张（测试用）
2. 提前准备好提示词
3. 选择清晰、简单的图片

### 提高成功率
1. 提示词要具体且详细
2. 避免描述剧烈动作
3. 图片主体要清晰

## 🔒 安全提醒

1. **不要泄露API密钥**
2. **不要提交 .env 文件到Git**
3. **定期更换API密钥**
4. **监控API使用量和费用**

## 📞 获取帮助

### 文档
- `README.md` - 项目说明
- `backend/README.md` - 后端详细文档
- `MIGRATION_GUIDE.md` - 迁移指南
- `TROUBLESHOOTING_VIDEO_API.md` - 故障排查

### 日志
```bash
./logs.sh  # 交互式日志查看
```

### 状态检查
```bash
./status.sh  # 查看所有服务状态
```

---

**快速参考卡版本**: 1.0  
**最后更新**: 2025-10-24  
**保持这份文档在手边，随时查阅！** 📖

