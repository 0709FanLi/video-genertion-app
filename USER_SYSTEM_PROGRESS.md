# 用户系统开发进度总结文档

**最后更新：** 2025-10-29 18:45
**Context状态：** 即将切换新context继续开发

---

## 📊 总体进度

- **阶段1（用户认证系统）：** 100% ✅
- **阶段2（自动保存机制）：** 40% ⏳
- **阶段3（资源库弹窗）：** 0% ⏹️

---

## ✅ 阶段1：用户认证系统（已完成）

### 后端部分
#### 1. 数据库模型（4张表）
文件位置：`backend/app/models/`

- ✅ `user.py` - 用户表
  - username（唯一）
  - password（哈希）
  - created_at, last_login_at, is_active

- ✅ `prompt_history.py` - 提示词历史表
  - user_id, original_prompt, optimized_prompt
  - optimization_model, scene_type
  - created_at

- ✅ `user_image.py` - 图片库表
  - user_id, image_url, thumbnail_url
  - prompt, model, resolution, width, height
  - generation_type, file_size, created_at

- ✅ `user_video.py` - 视频库表
  - user_id, video_url, thumbnail_url
  - prompt, model, **is_google_veo** 🆕
  - duration, resolution, aspect_ratio
  - generation_type
  - first_frame_image_id, last_frame_image_id, source_video_id
  - file_size, created_at

#### 2. 数据库配置
- ✅ `backend/app/database/session.py` - 数据库会话管理
  - create_engine（SQLite）
  - SessionLocal（会话工厂）
  - Base（声明基类）
  - get_db（依赖注入）
  - init_db（初始化表）

- ✅ `backend/app/core/config.py` - 配置更新
  - database_url（默认SQLite）
  - secret_key（JWT密钥）
  - algorithm（HS256）
  - access_token_expire_days（7天）

- ✅ 数据库初始化集成到 `main.py` 的 lifespan

#### 3. 认证工具和服务
- ✅ `backend/app/utils/auth.py` - 认证工具
  - hash_password（密码哈希）
  - verify_password（密码验证）
  - create_access_token（生成JWT）
  - decode_access_token（解析JWT）

- ✅ `backend/app/services/auth_service.py` - 认证服务
  - register（用户注册）
  - login（用户登录）
  - get_user_by_id
  - get_user_by_username

- ✅ `backend/app/api/deps_auth.py` - 认证依赖
  - get_current_user（获取当前登录用户）
  - get_current_user_optional（可选登录）

#### 4. 认证API路由
- ✅ `backend/app/api/routes/auth.py`
  - POST /api/auth/register - 注册
  - POST /api/auth/login - 登录
  - GET /api/auth/me - 获取当前用户信息
  - POST /api/auth/logout - 登出

- ✅ 已注册到 `main.py` 的路由

#### 5. 数据模型
- ✅ `backend/app/schemas/auth.py`
  - UserRegister
  - UserLogin
  - Token
  - TokenData
  - UserInfo

#### 6. 依赖包
- ✅ `backend/requirements.txt` 已更新
  - sqlalchemy==2.0.36
  - alembic==1.14.0
  - passlib[bcrypt]==1.7.4
  - python-jose[cryptography]==3.3.0
  - google-genai==1.46.0

### 前端部分
#### 1. 状态管理
- ✅ `frontend/src/store/authStore.js` - Zustand认证store
  - user, token, isAuthenticated, isLoading, error
  - login（登录）
  - register（注册）
  - logout（登出）
  - refreshUser（刷新用户信息）
  - checkAuth（检查认证状态）
  - 持久化到localStorage

#### 2. 页面组件
- ✅ `frontend/src/pages/Login.jsx` - 登录页面
  - 用户名+密码表单
  - 表单验证
  - 登录成功跳转

- ✅ `frontend/src/pages/Register.jsx` - 注册页面
  - 用户名+密码+确认密码
  - 表单验证（用户名格式、密码长度、确认密码匹配）
  - 注册成功自动登录

#### 3. 路由保护
- ✅ `frontend/src/components/ProtectedRoute.jsx`
  - 检查Token
  - 未登录重定向到登录页

- ✅ `frontend/src/App.jsx` - 路由配置更新
  - 公开路由：/login, /register
  - 受保护路由：/, /text-to-image, /image-to-video, /video-extension

#### 4. 用户菜单
- ✅ `frontend/src/components/UserMenu.jsx`
  - 显示用户名和ID
  - "我的资源库"菜单项（待实现）
  - 退出登录

- ✅ `frontend/src/components/common/Header.jsx` - 已集成UserMenu
  - 右上角显示用户菜单（登录后）

#### 5. API服务
- ✅ `frontend/src/services/api.js` - 添加authAPI
  - register（注册）
  - login（登录）
  - getCurrentUser（获取当前用户）
  - logout（登出）

---

## ⏳ 阶段2：自动保存机制（进行中 - 40%）

### 已完成
#### 1. 内容库服务
- ✅ `backend/app/services/library_service.py`
  - save_prompt（保存提示词历史）
  - save_image（保存图片）
  - save_video（保存视频，支持is_google_veo标记）
  - get_user_prompts（查询提示词历史，分页）
  - get_user_images（查询图片库，分页+筛选）
  - get_user_videos（查询视频库，分页+筛选+google_veo_only）

#### 2. 开始修改文生图接口
- ✅ `backend/app/api/routes/text_to_image.py` - 部分修改
  - 已添加导入：LibraryService, get_current_user, User, get_db
  - 已修改 optimize_prompt 函数签名（添加认证依赖）

### 待完成
#### 1. 完成文生图接口自动保存
- ⏹️ 在 `optimize_prompt` 函数返回前添加保存逻辑
  ```python
  # 保存提示词历史
  library_service = LibraryService(db)
  library_service.save_prompt(
      user_id=current_user.id,
      original_prompt=request.prompt,
      optimized_prompt=optimized_prompt,
      optimization_model=request.model,
      scene_type="text_to_image"
  )
  ```

- ⏹️ 修改 `generate_image` 函数
  - 添加认证依赖：`current_user: User = Depends(get_current_user), db: Session = Depends(get_db)`
  - 生成图片成功后，遍历image_urls保存每张图片
  ```python
  # 保存生成的图片
  library_service = LibraryService(db)
  for image_url in response["image_urls"]:
      library_service.save_image(
          user_id=current_user.id,
          image_url=image_url,
          prompt=request.prompt,
          model=request.model,
          resolution=request.size,
          generation_type="text_to_image"
      )
  ```

#### 2. 修改图生视频接口
文件：`backend/app/api/routes/image_to_video.py`

- ⏹️ 添加导入：LibraryService, get_current_user, User, get_db
- ⏹️ 修改主接口 `generate_video` 添加认证依赖
- ⏹️ 在视频生成成功后保存
  ```python
  # 保存生成的视频
  library_service = LibraryService(db)
  
  # 判断是否为Google Veo模型
  is_google_veo = 'google-veo' in request.model.lower()
  
  library_service.save_video(
      user_id=current_user.id,
      video_url=result.video_url,
      model=request.model,
      prompt=request.prompt,
      is_google_veo=is_google_veo,  # 🆕 重要！
      duration=request.duration,
      resolution=request.resolution,
      aspect_ratio=request.aspect_ratio,
      generation_type=generation_type  # 根据模型确定类型
  )
  ```

#### 3. 修改视频延长接口
文件：`backend/app/api/routes/video_extension.py`

- ⏹️ 添加导入
- ⏹️ 修改接口添加认证依赖
- ⏹️ 在视频延长成功后保存
  ```python
  # 保存延长后的视频
  library_service = LibraryService(db)
  
  # 需要获取source_video_id（从video_url查询原视频记录）
  source_video = db.query(UserVideo).filter(
      UserVideo.video_url == request.video_url
  ).first()
  
  is_google_veo = 'google-veo' in request.model.lower()
  
  library_service.save_video(
      user_id=current_user.id,
      video_url=result.video_url,
      model=request.model,
      prompt=request.prompt,
      is_google_veo=is_google_veo,
      duration=8,  # Google Veo固定8秒
      resolution="720p",
      aspect_ratio=request.aspect_ratio,
      generation_type="video_extension",
      source_video_id=source_video.id if source_video else None
  )
  ```

---

## ⏹️ 阶段3：资源库弹窗（未开始）

### 后端部分
#### 1. 创建资源库查询API路由
文件：`backend/app/api/routes/library.py`（待创建）

需要创建的接口：
```python
GET /api/library/prompts
  - 参数: page, limit, search
  - 返回: 提示词历史列表（分页）
  - 需要认证

GET /api/library/images
  - 参数: page, limit, search, model
  - 返回: 用户图片列表（分页）
  - 需要认证

GET /api/library/videos
  - 参数: page, limit, search, model, google_veo_only
  - 返回: 用户视频列表（分页）
  - 需要认证
  - 🆕 支持 google_veo_only 筛选
```

#### 2. 注册路由
- 在 `main.py` 中注册 library 路由

### 前端部分
#### 1. 创建资源库状态管理
文件：`frontend/src/store/libraryStore.js`（待创建）

需要的状态：
- prompts, images, videos（数据列表）
- loading, error
- currentTab（当前Tab: 'prompt' | 'image' | 'video'）
- searchText（搜索关键词）
- filters（筛选条件）

需要的Actions：
- fetchPrompts
- fetchImages
- fetchVideos
- setCurrentTab
- setSearchText

#### 2. 创建LibraryModal组件
文件：`frontend/src/components/LibraryModal/`（待创建）

组件结构：
```
LibraryModal/
├── index.jsx              # 主弹窗组件（Tab切换）
├── PromptTab.jsx         # 提示词列表Tab
├── ImageTab.jsx          # 图片网格Tab
└── VideoTab.jsx          # 视频网格Tab（含Google Veo标记）
```

UI设计：
- 弹窗尺寸：屏幕的50%
- 三个Tab切换
- 搜索框
- 网格布局
- 无限滚动加载
- **VideoTab特别要求：**
  - 显示Google Veo蓝色徽章
  - 支持google_veo_only筛选

#### 3. 修改各功能页面集成弹窗

**文生图页面（TextToImage）：**
- 提示词输入框旁边添加"历史"按钮
- 参考图上传旁边添加"从图片库选择"按钮

**图生视频页面（ImageToVideo）：**
- 提示词输入框旁边添加"历史"按钮
- 首帧/尾帧上传旁边添加"从图片库选择"按钮

**视频延长页面（VideoExtension）：**
- 提示词输入框旁边添加"历史"按钮
- ⚠️ **视频选择改为必须从视频库选择（不支持本地上传）**
- ⚠️ **当选择Google Veo模型时，自动传递 `google_veo_only=true`**
- 显示提示："Google Veo 仅支持延长由其生成的视频"

---

## 🎯 下一步操作指南（新Context）

### 立即执行
1. **完成文生图接口自动保存**
   - 文件：`backend/app/api/routes/text_to_image.py`
   - 在 `optimize_prompt` 返回前添加保存
   - 修改 `generate_image` 添加认证和保存

2. **修改图生视频接口**
   - 文件：`backend/app/api/routes/image_to_video.py`
   - 添加认证依赖
   - 保存视频时设置 `is_google_veo`

3. **修改视频延长接口**
   - 文件：`backend/app/api/routes/video_extension.py`
   - 添加认证依赖
   - 保存视频时设置 `is_google_veo` 和 `source_video_id`

4. **创建资源库API路由**
   - 创建 `backend/app/api/routes/library.py`
   - 实现3个GET接口
   - 注册到 `main.py`

5. **前端LibraryModal开发**
   - 创建 libraryStore
   - 创建 LibraryModal 组件（4个文件）
   - 集成到各功能页面

### 测试验证
1. 测试登录注册
2. 测试生成内容后自动保存
3. 测试资源库弹窗查询
4. 测试从资源库选择内容
5. 测试Google Veo视频筛选

---

## 🗂️ 文件变更清单

### 已创建的文件
```
backend/app/
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── prompt_history.py
│   ├── user_image.py
│   └── user_video.py
├── database/
│   ├── __init__.py
│   └── session.py
├── schemas/
│   └── auth.py
├── services/
│   ├── auth_service.py
│   └── library_service.py
├── utils/
│   └── auth.py
└── api/
    ├── deps_auth.py
    └── routes/
        └── auth.py

frontend/src/
├── store/
│   └── authStore.js
├── pages/
│   ├── Login.jsx
│   └── Register.jsx
└── components/
    ├── ProtectedRoute.jsx
    └── UserMenu.jsx
```

### 已修改的文件
```
backend/
├── app/core/config.py（添加数据库和JWT配置）
├── app/main.py（集成数据库初始化和认证路由）
├── app/api/routes/text_to_image.py（部分修改，添加导入和认证依赖）
└── requirements.txt（添加依赖包）

frontend/src/
├── App.jsx（添加路由保护和登录/注册路由）
├── components/common/Header.jsx（集成UserMenu）
└── services/api.js（添加authAPI）
```

### 待创建的文件
```
backend/app/api/routes/
└── library.py

frontend/src/
├── store/
│   └── libraryStore.js
└── components/
    └── LibraryModal/
        ├── index.jsx
        ├── PromptTab.jsx
        ├── ImageTab.jsx
        └── VideoTab.jsx
```

### 待修改的文件
```
backend/app/api/routes/
├── text_to_image.py（完成自动保存）
├── image_to_video.py（添加认证和自动保存）
└── video_extension.py（添加认证和自动保存）

frontend/src/components/
├── TextToImage/（集成LibraryModal）
├── ImageToVideo/（集成LibraryModal）
└── VideoExtension/（集成LibraryModal，改为必须从库选择）
```

---

## 💡 重要注意事项

### Google Veo 视频标记
⚠️ **所有涉及视频保存的地方，必须判断模型并设置 `is_google_veo` 字段！**

```python
is_google_veo = 'google-veo' in model_name.lower()
```

这个字段用于视频延长时筛选可用视频。

### 认证依赖注入
所有需要保存用户内容的接口，都必须添加认证依赖：

```python
async def some_endpoint(
    ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ...
```

### 数据库状态
数据库文件：`video_generation_app.db`（SQLite）
启动日志确认：
```
✅ 数据库表创建成功
INFO: 数据库初始化成功
```

---

## 📞 如有问题

参考文件：
- 需求文档：`user.md`（完整需求设计）
- 模型列表：`models.md`（所有使用的AI模型）

当前服务状态：
- 后端：http://localhost:8000
- 前端：http://localhost:5173
- API文档：http://localhost:8000/docs

---

**准备在新Context继续开发！** 🚀

