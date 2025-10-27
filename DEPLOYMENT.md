# 部署指南

本文档介绍如何将AI视频创作工作流系统部署到生产环境。

## 环境要求

### 系统要求
- **操作系统**: Linux (Ubuntu 20.04+推荐) / macOS / Windows
- **Python**: 3.9.6 或更高版本
- **Node.js**: 18.0 或更高版本
- **内存**: 至少2GB可用内存
- **磁盘**: 至少5GB可用空间

### 依赖服务
- 阿里云DashScope API密钥
- 稳定的网络连接

## 本地开发环境部署

### 1. 克隆或下载项目

```bash
# 如果项目在Git仓库中
git clone <repository-url>
cd video_generation_app

# 或直接使用已有的项目目录
cd video_generation_app
```

### 2. 后端部署

#### 2.1 创建Python虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

#### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt`，手动安装：

```bash
pip install fastapi uvicorn python-multipart openai requests
```

#### 2.3 配置环境变量

创建 `.env` 文件：

```bash
DASHSCOPE_API_KEY=sk-8b6db5929e244a159deb8e77b08bcf5b
```

修改 `backend/main.py` 以使用环境变量：

```python
import os
from dotenv import load_dotenv

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
```

#### 2.4 启动后端服务

```bash
cd backend
python main.py
```

或使用uvicorn直接启动：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 前端部署

#### 3.1 安装依赖

```bash
cd frontend
npm install
```

#### 3.2 开发模式启动

```bash
npm run dev
```

#### 3.3 生产构建

```bash
npm run build
```

构建产物将生成在 `dist/` 目录下。

## 生产环境部署

### 方案一：使用Nginx + Gunicorn

#### 1. 后端部署

安装Gunicorn：

```bash
pip install gunicorn
```

创建Gunicorn配置文件 `gunicorn_config.py`：

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
```

启动后端：

```bash
gunicorn -c gunicorn_config.py backend.main:app
```

#### 2. 前端部署

构建前端：

```bash
cd frontend
npm run build
```

配置Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/video_generation_app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

重启Nginx：

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 方案二：使用Docker部署

#### 1. 创建Dockerfile（后端）

创建 `backend/Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. 创建Dockerfile（前端）

创建 `frontend/Dockerfile`：

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 3. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DASHSCOPE_API_KEY=sk-8b6db5929e244a159deb8e77b08bcf5b
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

#### 4. 启动服务

```bash
docker-compose up -d
```

### 方案三：云平台部署

#### 阿里云ECS部署

1. 购买ECS实例（推荐2核4G配置）
2. 安装Python和Node.js环境
3. 按照本地部署步骤配置
4. 配置安全组开放80和8000端口
5. 使用systemd管理服务

创建 `/etc/systemd/system/video-gen-backend.service`：

```ini
[Unit]
Description=Video Generation Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/video_generation_app/backend
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable video-gen-backend
sudo systemctl start video-gen-backend
```

## 性能优化建议

### 1. 后端优化

- 使用异步任务队列（Celery）处理长时间运行的任务
- 实现结果缓存机制
- 配置合理的worker数量
- 添加请求限流保护

### 2. 前端优化

- 启用Gzip压缩
- 配置CDN加速静态资源
- 实现图片懒加载
- 优化打包体积

### 3. 数据库（可选）

如需持久化存储任务记录，可集成数据库：

- PostgreSQL（推荐）
- MySQL
- MongoDB

## 监控与日志

### 1. 日志配置

修改 `backend/main.py` 添加日志：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 监控工具

推荐使用：
- Prometheus + Grafana
- ELK Stack (Elasticsearch + Logstash + Kibana)
- 云平台自带监控服务

## 安全建议

1. **API密钥保护**
   - 使用环境变量存储密钥
   - 不要将密钥提交到版本控制系统
   - 定期轮换API密钥

2. **HTTPS配置**
   - 使用Let's Encrypt免费SSL证书
   - 强制HTTPS访问

3. **访问控制**
   - 实现用户认证系统
   - 添加API访问频率限制
   - 配置CORS策略

4. **内容安全**
   - 实现敏感内容过滤
   - 记录所有生成请求
   - 遵守相关法律法规

## 故障排查

### 常见问题

1. **后端无法启动**
   - 检查端口8000是否被占用
   - 验证Python依赖是否完整安装
   - 查看错误日志

2. **前端无法访问后端**
   - 检查Vite proxy配置
   - 验证CORS设置
   - 确认后端服务正常运行

3. **API调用失败**
   - 验证API密钥是否有效
   - 检查网络连接
   - 查看阿里云控制台配额

## 备份与恢复

### 定期备份内容

1. 配置文件
2. 用户数据（如有）
3. 日志文件
4. 数据库（如有）

### 备份脚本示例

```bash
#!/bin/bash
BACKUP_DIR="/backup/video_gen_$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份配置
cp -r /path/to/video_generation_app $BACKUP_DIR/

# 压缩
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
```

## 扩展性建议

随着用户量增长，考虑：

1. **水平扩展**
   - 使用负载均衡器
   - 部署多个后端实例
   - 使用Redis共享会话

2. **异步处理**
   - 引入消息队列（RabbitMQ/Redis）
   - 使用Celery处理异步任务
   - 实现WebSocket实时通知

3. **微服务架构**
   - 拆分提示词生成服务
   - 独立图片生成服务
   - 独立视频生成服务

## 联系与支持

如遇到部署问题，请检查：
- 项目README.md
- 阿里云DashScope官方文档
- FastAPI官方文档
- Vite官方文档

