# AI 视频创作工作流系统

这是一个基于阿里云大模型的完整视频创作工作流系统，支持从文本想法到最终视频的全流程创作。

## 功能特性

1. **智能提示词生成**：输入简单想法，AI自动生成多个专业的图片提示词
2. **多图片生成**：根据选定的提示词生成多张候选图片
3. **视频提示词优化**：AI智能优化视频动态描述
4. **图生视频**：基于选定图片和提示词生成视频

## 技术栈

### 后端
- **框架**: FastAPI
- **Python版本**: 3.9.6+
- **AI服务**: 
  - 通义千问 (文本生成/提示词优化)
  - 通义万相 (文生图、图生视频)

### 前端
- **框架**: React 18
- **构建工具**: Vite 7
- **样式**: 原生CSS

## 项目结构

```
video_generation_app/
├── backend/
│   └── main.py          # FastAPI后端应用
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # React主组件
│   │   ├── App.css      # 样式文件
│   │   ├── main.jsx     # React入口
│   │   └── index.css    # 全局样式
│   ├── index.html       # HTML模板
│   ├── package.json     # 前端依赖
│   └── vite.config.js   # Vite配置
└── README.md            # 项目文档
```

## 安装与运行

### 1. 安装后端依赖

```bash
pip3 install fastapi uvicorn python-multipart openai requests
```

### 2. 配置API密钥

创建 `backend/.env` 文件（如果不存在），并添加您的API密钥：
```bash
# 复制示例文件
cp backend/.env.example backend/.env

# 编辑 .env 文件，填入您的API密钥
# DASHSCOPE_API_KEY=your-api-key-here
```

**重要**：请勿将真实的API密钥提交到Git仓库！

### 3. 启动后端服务

```bash
cd video_generation_app/backend
python3 main.py
```

后端将在 `http://localhost:8000` 启动

### 4. 安装前端依赖

```bash
cd video_generation_app/frontend
npm install
```

### 5. 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动（如果端口被占用会自动使用其他端口）

## 使用流程

1. **输入想法**：在第一步输入框中输入您的创意想法
2. **生成提示词**：点击"生成图片提示词"按钮，AI会生成3个专业提示词
3. **选择提示词**：从候选提示词中选择一个最符合您需求的
4. **生成图片**：点击"生成图片"按钮，等待1-2分钟生成4张图片
5. **选择图片**：点击选择一张最满意的图片
6. **输入视频描述**：描述您希望图片如何动起来
7. **优化提示词（可选）**：点击"优化提示词"让AI优化您的描述
8. **生成视频**：点击"生成视频"按钮，等待3-5分钟生成最终视频

## API接口说明

### 后端API

#### 1. 生成图片提示词
- **接口**: `POST /api/generate-image-prompts`
- **请求体**: `{"idea": "用户想法"}`
- **响应**: JSON格式的提示词列表

#### 2. 生成图片
- **接口**: `POST /api/generate-images`
- **请求体**: `{"prompt": "图片提示词"}`
- **响应**: 包含图片URL的结果

#### 3. 优化视频提示词
- **接口**: `POST /api/optimise-video-prompt`
- **请求体**: `{"prompt": "视频描述"}`
- **响应**: 优化后的提示词

#### 4. 生成视频
- **接口**: `POST /api/generate-video`
- **请求体**: `{"image_url": "图片URL", "prompt": "视频提示词"}`
- **响应**: 包含视频URL的结果

## 注意事项

1. **API调用时长**：
   - 图片生成：约1-2分钟
   - 视频生成：约3-5分钟
   - 请耐心等待，不要重复提交

2. **资源有效期**：
   - 生成的图片和视频URL有效期为24小时
   - 建议及时下载保存

3. **成本控制**：
   - 每次生成图片会产生4张图片的费用
   - 建议测试时将 `parameters.n` 设置为1

4. **模型选择**：
   - 文生图使用 `wanx-v1` 模型
   - 图生视频使用 `wanx-i2v-v1` 模型
   - 可根据需要调整为其他版本

## 常见问题

### Q: 为什么生成失败？
A: 请检查：
- API密钥是否正确
- 网络连接是否正常
- 提示词是否符合内容安全规范

### Q: 如何修改生成参数？
A: 在 `backend/main.py` 中修改对应API调用的 `parameters` 参数

### Q: 前端无法连接后端？
A: 检查：
- 后端服务是否正常运行在8000端口
- vite.config.js中的proxy配置是否正确

## 开发者信息

- **开发工具**: Manus AI
- **文档版本**: 1.0
- **最后更新**: 2025-10-24

## 许可证

本项目仅供学习和研究使用。

