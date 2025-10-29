# 用户系统功能需求设计文档

## 一、核心功能概述

### 1.1 用户认证系统
- 用户需要登录才能使用系统功能
- 登录后的内容（提示词、图片、视频）按用户隔离存储
- 用户可管理自己的历史生成内容

### 1.2 内容管理系统
- 优化后的提示词历史记录
- 生成的图片库
- 生成的视频库
- 统一的资源选择弹窗

### 1.3 资源复用功能
- 图生视频时可选择已生成的图片作为首尾帧
- 视频延长时必须从已生成的视频中选择

---

## 二、详细功能设计

### 2.1 用户认证模块

#### 2.1.1 登录/注册功能
**需确认的问题：**
1. **注册方式选择：**
   - [ ] A. 邮箱 + 密码注册
   - [ ] B. 手机号 + 验证码注册
   - [ ] C. 第三方登录（微信、GitHub等）
   - [ ] D. 简化方案：仅用户名 + 密码（无需邮箱验证）

2. **是否需要找回密码功能？**
   - [ ] 是（需要邮箱/手机号）
   - [ ] 否（初期可不做）

3. **登录状态保持时长：**
   - [ ] 7天自动登录
   - [ ] 30天自动登录
   - [ ] 自定义时长

**推荐方案：** 初期使用用户名+密码，Token保持7天，后期扩展其他方式

#### 2.1.2 权限控制
- 未登录用户：重定向到登录页
- 登录用户：可访问所有功能
- Token过期：自动退出并提示重新登录

---

### 2.2 内容分类管理

#### 2.2.1 数据结构设计

**需确认的问题：**
1. **提示词历史记录保存哪些内容？**
   - [ ] A. 仅保存优化后的提示词
   - [ ] B. 保存原始提示词 + 优化后的提示词（推荐）
   - [ ] C. 包含使用的优化模型、时间戳等元数据

2. **图片分类方式：**
   - [ ] A. 按生成时间分类（日期）
   - [ ] B. 按模型分类（通义、火山等）
   - [ ] C. 按用途分类（文生图、参考图等）
   - [ ] D. 支持用户自定义标签/文件夹
   - [ ] E. 以上多种方式结合

3. **视频分类方式：**
   - [ ] A. 按生成时间分类
   - [ ] B. 按类型分类（文生视频、图生视频、视频延长）
   - [ ] C. 按模型分类
   - [ ] D. 支持用户自定义标签/文件夹
   - [ ] E. 以上多种方式结合

**推荐方案：**
- 提示词：保存原始+优化后，包含模型和时间
- 图片/视频：默认按时间+类型分类，支持搜索和筛选

#### 2.2.2 存储容量限制

**需确认的问题：**
1. **是否设置存储上限？**
   - [ ] A. 不限制（所有内容永久保存）
   - [ ] B. 按数量限制（如：最多保存100张图片、50个视频）
   - [ ] C. 按容量限制（如：用户总空间5GB）
   - [ ] D. 按时间限制（如：保留最近30天的内容）

2. **超出限制后的处理：**
   - [ ] A. 自动删除最旧的内容
   - [ ] B. 提示用户手动删除
   - [ ] C. 升级会员扩容

**推荐方案：** 初期不限制，后期可按需添加限制

---

### 2.3 统一资源选择弹窗

#### 2.3.1 弹窗功能设计

**1. 提示词历史弹窗**
- **触发位置：** 
  - 文生图提示词输入框旁边（"历史"按钮）
  - 图生视频描述提示词输入框旁边
  - 视频延长提示词输入框旁边

- **显示内容：**
  - 提示词文本（原始 + 优化后）
  - 使用的优化模型
  - 生成时间
  - 预览图（如果有关联的生成结果）

- **操作：**
  - 点击选中：将提示词填充到输入框
  - 删除：删除该历史记录
  - 搜索：按关键词搜索提示词

**2. 图片库弹窗**
- **触发位置：**
  - 文生图参考图上传时（"从图片库选择"按钮）
  - 图生视频首帧上传时
  - 图生视频尾帧上传时

- **显示内容：**
  - 缩略图网格展示
  - 图片生成时间
  - 图片尺寸/分辨率
  - 使用的模型
  - 关联的提示词（鼠标悬停显示）

- **操作：**
  - 单选/多选模式（根据场景）
  - 预览大图
  - 删除图片
  - 筛选：按时间、模型、尺寸筛选
  - 搜索：按提示词搜索

**3. 视频库弹窗**
- **触发位置：**
  - 视频延长上传视频时（**必须从库中选择，不允许上传本地**）

- **显示内容：**
  - 视频缩略图/第一帧预览
  - 视频时长
  - 分辨率和长宽比
  - 生成类型（文生视频/图生视频/已延长）
  - 生成时间
  - 使用的模型

- **操作：**
  - 单选模式
  - 播放预览
  - 删除视频
  - 筛选：按类型、时间、模型筛选
  - 搜索：按描述/提示词搜索

#### 2.3.2 弹窗UI设计

**需确认的问题：**
1. **弹窗尺寸和布局：**
   - [ ] A. 全屏遮罩，左侧筛选、右侧网格展示
   - [ ] B. 中等尺寸弹窗（800x600），顶部筛选、下方网格
   - [ ] C. 侧边栏滑出（右侧滑出抽屉）

2. **网格展示方式：**
   - [ ] A. 固定3列网格
   - [ ] B. 固定4列网格
   - [ ] C. 响应式自适应列数
   - [ ] D. 列表+网格切换

3. **分页方式：**
   - [ ] A. 传统分页器（上一页/下一页）
   - [ ] B. 无限滚动加载
   - [ ] C. 加载更多按钮

**推荐方案：** 中等尺寸弹窗 + 响应式网格 + 无限滚动

---

### 2.4 自动保存机制

#### 2.4.1 保存时机

**1. 提示词保存：**
- 用户点击"优化提示词"后，自动保存原始+优化后的提示词
- 关联当前使用的优化模型

**2. 图片保存：**
- 图片生成成功后，自动保存到用户图片库
- 记录生成参数（提示词、模型、分辨率等）

**3. 视频保存：**
- 视频生成成功后，自动保存到用户视频库
- 记录生成参数（提示词、模型、时长、分辨率、长宽比等）
- 如果是图生视频，关联使用的首尾帧图片ID

**需确认的问题：**
1. **是否需要用户确认才保存？**
   - [ ] A. 自动保存所有生成内容（推荐）
   - [ ] B. 生成后询问用户是否保存
   - [ ] C. 提供"加入收藏"按钮，用户主动保存

2. **失败的生成记录是否保存？**
   - [ ] A. 不保存失败记录
   - [ ] B. 保存失败记录（用于分析和重试）

**推荐方案：** 自动保存成功的内容，不保存失败记录

---

### 2.5 数据库设计

#### 2.5.1 用户表 (users)
```sql
- id: 主键
- username: 用户名（唯一）
- password: 密码（哈希）
- email: 邮箱（可选）
- created_at: 注册时间
- last_login_at: 最后登录时间
- is_active: 是否启用
```

#### 2.5.2 提示词历史表 (prompt_history)
```sql
- id: 主键
- user_id: 用户ID（外键）
- original_prompt: 原始提示词
- optimized_prompt: 优化后的提示词
- optimization_model: 使用的优化模型
- scene_type: 使用场景（text_to_image/image_to_video/video_extension）
- created_at: 创建时间
```

#### 2.5.3 图片库表 (user_images)
```sql
- id: 主键
- user_id: 用户ID（外键）
- image_url: OSS图片URL
- thumbnail_url: 缩略图URL（可选）
- prompt: 生成提示词
- model: 使用的模型
- resolution: 分辨率
- width: 宽度
- height: 高度
- generation_type: 生成类型（text_to_image/reference_image）
- file_size: 文件大小
- created_at: 创建时间
```

#### 2.5.4 视频库表 (user_videos)
```sql
- id: 主键
- user_id: 用户ID（外键）
- video_url: OSS视频URL
- thumbnail_url: 缩略图URL
- prompt: 生成提示词
- model: 使用的模型
- duration: 时长（秒）
- resolution: 分辨率
- aspect_ratio: 长宽比
- generation_type: 生成类型（text_to_video/image_to_video_first/image_to_video_tail/video_extension）
- first_frame_image_id: 首帧图片ID（外键，可null）
- last_frame_image_id: 尾帧图片ID（外键，可null）
- source_video_id: 源视频ID（视频延长时使用，外键，可null）
- file_size: 文件大小
- created_at: 创建时间
```

**需确认的问题：**
1. **是否需要软删除（逻辑删除）？**
   - [ ] A. 是，添加 deleted_at 字段，用户删除时不真删除
   - [ ] B. 否，用户删除时直接物理删除

2. **是否需要添加标签系统？**
   - [ ] A. 是，用户可以给图片/视频打标签
   - [ ] B. 否，仅使用现有字段筛选

**推荐方案：** 使用软删除，初期不做标签系统

---

## 三、技术实现要点

### 3.1 后端实现

#### 3.1.1 认证方案
- 使用 **JWT Token** 进行身份验证
- Token 存储在 HTTP-only Cookie 或 LocalStorage
- 后端中间件验证 Token 有效性

#### 3.1.2 API设计
**用户认证相关：**
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息

**内容管理相关：**
- `GET /api/prompts` - 获取提示词历史（分页）
- `DELETE /api/prompts/{id}` - 删除提示词记录
- `GET /api/images` - 获取用户图片库（分页+筛选）
- `DELETE /api/images/{id}` - 删除图片
- `GET /api/videos` - 获取用户视频库（分页+筛选）
- `DELETE /api/videos/{id}` - 删除视频

**自动保存相关：**
- 在现有生成接口成功后，自动调用保存逻辑
- 不需要新增API，在现有接口中集成

### 3.2 前端实现

#### 3.2.1 状态管理
- 新增 `authStore`：管理登录状态、用户信息
- 新增 `libraryStore`：管理图片库、视频库、提示词历史

#### 3.2.2 路由保护
- 未登录用户访问主功能页时重定向到登录页
- 登录页和注册页公开访问

#### 3.2.3 组件开发
**新增组件：**
- `Login.jsx` - 登录页面
- `Register.jsx` - 注册页面（可选）
- `PromptHistoryModal.jsx` - 提示词历史弹窗
- `ImageLibraryModal.jsx` - 图片库弹窗
- `VideoLibraryModal.jsx` - 视频库弹窗
- `UserMenu.jsx` - 用户菜单（头部右上角）

**修改组件：**
- `Header.jsx` - 添加用户菜单
- 各个提示词输入组件 - 添加"历史"按钮
- 图片上传组件 - 添加"从图片库选择"按钮
- 视频上传组件 - 改为"从视频库选择"（必选）

---

## 四、开发优先级和分阶段实施

### 第一阶段：基础认证（必须）
1. 用户注册/登录功能
2. JWT Token认证
3. 路由保护
4. 用户信息展示

### 第二阶段：自动保存（核心）
1. 数据库表设计和创建
2. 生成成功后自动保存逻辑
3. 提示词历史保存
4. 图片自动保存
5. 视频自动保存

### 第三阶段：内容管理（重要）
1. 提示词历史查看和选择
2. 图片库查看和选择
3. 视频库查看和选择
4. 删除功能

### 第四阶段：优化和扩展（可选）
1. 搜索和筛选功能
2. 缩略图生成
3. 标签系统
4. 用户设置页面
5. 存储容量管理

---

## 五、需要确认的核心问题汇总

### 🔴 必须确认（影响架构）
1. **注册方式：** 用户名+密码 还是 邮箱+密码？
2. **视频延长限制：** 确认必须从视频库选择，不允许上传本地视频？
3. **存储策略：** 是否需要设置容量/数量限制？

### 🟡 重要确认（影响体验）
4. **分类方式：** 图片和视频按什么维度分类？
5. **弹窗UI：** 选择哪种弹窗展示方式？
6. **保存机制：** 自动保存 还是 手动保存？

### 🟢 次要确认（可后期调整）
7. **软删除：** 是否需要回收站功能？
8. **标签系统：** 是否需要用户自定义标签？
9. **找回密码：** 初期是否实现？

---

## 六、预估工作量

- **第一阶段（认证）：** 2-3天
- **第二阶段（保存）：** 2-3天
- **第三阶段（管理）：** 3-4天
- **第四阶段（优化）：** 2-3天

**总计：** 约 9-13 个工作日

---

## 七、确认的需求（2025-10-29）

### ✅ 已确认的核心决策

1. **注册方式：** 用户名 + 密码
2. **资源管理弹窗：** 
   - 统一弹窗，三个Tab分类（优化提示词、生成图片、生成视频）
   - 弹窗尺寸：屏幕的二分之一大小
   - 布局：顶部Tab切换，下方内容网格展示
3. **保存机制：** 自动保存所有成功生成的内容
4. **删除功能：** 暂不实现（初期只保存不删除）
5. **标签系统：** 暂不实现
6. **找回密码：** 暂不实现

### ⚠️ 重要限制：Google Veo 视频特殊标记

**视频延长模型限制：**
- Google Veo 3.1 模型进行视频延长时，**只能选择由 Google Veo 生成的视频**
- 其他模型（火山引擎、通义万相）生成的视频不能用于 Google Veo 视频延长

**实现要点：**
1. **数据库设计：**
   ```sql
   user_videos 表增加字段：
   - is_google_veo: BOOLEAN  -- 标记是否为Google Veo生成
   ```

2. **前端视频库弹窗：**
   - 在视频缩略图上添加醒目的"Google Veo"标签（蓝色徽章）
   - 非 Google Veo 视频显示普通标签（模型名称）

3. **视频延长选择逻辑：**
   ```
   IF 当前选择的模型 = Google Veo:
       THEN 视频库弹窗只显示 is_google_veo = true 的视频
       AND 添加提示文案："Google Veo 模型仅支持延长由其生成的视频"
   ELSE:
       显示所有视频（包括Google Veo生成的视频）
   ```

4. **UI提示：**
   - 当用户在视频延长页面选择 Google Veo 模型时
   - 视频选择按钮旁边显示说明：
     ```
     ⚠️ 注意：Google Veo 仅支持延长由 Google Veo 生成的视频
     ```

---

## 八、修订后的统一资源弹窗设计

### 8.1 弹窗结构

```
┌─────────────────────────────────────────────────────────┐
│  我的创作库                                     [×]      │
├─────────────────────────────────────────────────────────┤
│  [优化提示词] [生成图片] [生成视频]  ← Tab切换          │
├─────────────────────────────────────────────────────────┤
│  🔍 搜索框                          [最新▼] [网格视图▼] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                     │
│  │     │ │     │ │     │ │     │  ← 内容网格         │
│  │     │ │     │ │     │ │     │                     │
│  └─────┘ └─────┘ └─────┘ └─────┘                     │
│                                                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                     │
│  │     │ │     │ │     │ │     │                     │
│  │     │ │     │ │     │ │     │                     │
│  └─────┘ └─────┘ └─────┘ └─────┘                     │
│                                                         │
│                                      [加载更多...]      │
└─────────────────────────────────────────────────────────┘
```

### 8.2 各Tab内容展示

**Tab 1: 优化提示词**
```
┌────────────────────────────────────────────┐
│ 一只可爱的橘猫在清澈的溪流中游泳...      │
│ 模型: DeepSeek-V3.2 | 2025-10-29 16:30   │
│ [选择使用]                                 │
└────────────────────────────────────────────┘
```

**Tab 2: 生成图片**
```
┌──────────┐  ← 缩略图
│          │
│  [图片]  │
│          │
└──────────┘
通义千问 | 1024x1024
2025-10-29 16:30
[选择使用]
```

**Tab 3: 生成视频**
```
┌──────────┐  ← 视频缩略图/第一帧
│  ▶️      │  [Google Veo] ← 特殊标记（蓝色徽章）
│  [视频]  │
│          │
└──────────┘
Google Veo | 8秒 | 1080P | 9:16
图生视频 | 2025-10-29 16:30
[选择使用]

或者

┌──────────┐
│  ▶️      │
│  [视频]  │  火山即梦 ← 普通标签
│          │
└──────────┘
火山即梦 | 10秒 | 1080P | 16:9
文生视频 | 2025-10-29 16:28
[选择使用]
```

### 8.3 视频延长时的筛选逻辑

**场景1：选择 Google Veo 模型进行视频延长**
```
用户点击"选择视频"按钮
  ↓
弹出视频库弹窗
  ↓
顶部显示提示：
  "⚠️ Google Veo 仅支持延长由其生成的视频，已自动筛选"
  ↓
只显示带有 [Google Veo] 标记的视频
  ↓
用户选择后关闭弹窗
```

**场景2：非 Google Veo 模型（暂未实现，为未来预留）**
```
用户点击"选择视频"按钮
  ↓
弹出视频库弹窗
  ↓
显示所有视频（包括Google Veo生成的）
  ↓
用户选择后关闭弹窗
```

---

## 九、数据库设计更新

### 9.1 用户表 (users)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- 哈希后的密码
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 9.2 提示词历史表 (prompt_history)
```sql
CREATE TABLE prompt_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    original_prompt TEXT,                -- 原始提示词
    optimized_prompt TEXT NOT NULL,      -- 优化后的提示词
    optimization_model VARCHAR(50),      -- 优化模型（如：deepseek-v3.2）
    scene_type VARCHAR(50),              -- 使用场景（text_to_image/image_to_video/video_extension）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 9.3 图片库表 (user_images)
```sql
CREATE TABLE user_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,     -- OSS完整URL
    thumbnail_url VARCHAR(500),          -- 缩略图URL（可选）
    prompt TEXT,                         -- 生成提示词
    model VARCHAR(50),                   -- 使用的模型
    resolution VARCHAR(20),              -- 分辨率（如：1024x1024）
    width INT,                           -- 宽度
    height INT,                          -- 高度
    generation_type VARCHAR(50),         -- 生成类型（text_to_image/reference_image）
    file_size BIGINT,                    -- 文件大小（字节）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_created (user_id, created_at DESC)
);
```

### 9.4 视频库表 (user_videos) - 新增 is_google_veo 字段
```sql
CREATE TABLE user_videos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    video_url VARCHAR(500) NOT NULL,     -- OSS完整URL
    thumbnail_url VARCHAR(500),          -- 缩略图URL
    prompt TEXT,                         -- 生成提示词
    model VARCHAR(50) NOT NULL,          -- 使用的模型
    is_google_veo BOOLEAN DEFAULT FALSE, -- 🆕 是否为Google Veo生成
    duration INT,                        -- 时长（秒）
    resolution VARCHAR(20),              -- 分辨率（如：1080P）
    aspect_ratio VARCHAR(10),            -- 长宽比（如：16:9）
    generation_type VARCHAR(50),         -- 生成类型（text_to_video/image_to_video_first/image_to_video_tail/video_extension）
    first_frame_image_id INT,            -- 首帧图片ID（外键，可null）
    last_frame_image_id INT,             -- 尾帧图片ID（外键，可null）
    source_video_id INT,                 -- 源视频ID（视频延长时使用，外键，可null）
    file_size BIGINT,                    -- 文件大小（字节）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (first_frame_image_id) REFERENCES user_images(id),
    FOREIGN KEY (last_frame_image_id) REFERENCES user_images(id),
    FOREIGN KEY (source_video_id) REFERENCES user_videos(id),
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_google_veo (user_id, is_google_veo)  -- 🆕 优化筛选查询
);
```

---

## 十、API设计更新

### 10.1 用户认证
- `POST /api/auth/register` - 注册（用户名+密码）
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户信息

### 10.2 资源查询（统一弹窗使用）
```
GET /api/library/prompts
  参数：page, limit, search
  返回：提示词历史列表（分页）

GET /api/library/images
  参数：page, limit, search, model（可选）
  返回：用户图片列表（分页）

GET /api/library/videos
  参数：page, limit, search, model（可选）, google_veo_only（true/false）
  返回：用户视频列表（分页）
  
  🆕 新增参数说明：
  - google_veo_only=true：只返回 is_google_veo=true 的视频
  - google_veo_only=false 或不传：返回所有视频
```

### 10.3 自动保存（在现有生成接口中集成）
- 文生图成功后：自动保存到 `user_images`
- 图生视频成功后：自动保存到 `user_videos`
  - **如果 model 包含 "google-veo"，设置 is_google_veo=true**
- 视频延长成功后：自动保存到 `user_videos`，并关联 `source_video_id`

---

## 十一、前端组件设计

### 11.1 新增组件

**1. Login.jsx - 登录页面**
```jsx
- 用户名输入框
- 密码输入框
- 登录按钮
- 注册按钮（跳转注册页）
```

**2. Register.jsx - 注册页面**
```jsx
- 用户名输入框（唯一性验证）
- 密码输入框
- 确认密码输入框
- 注册按钮
```

**3. LibraryModal.jsx - 统一资源库弹窗**
```jsx
props:
  - visible: 是否显示
  - onClose: 关闭回调
  - onSelect: 选择回调
  - mode: 'prompt' | 'image' | 'video' | 'all'
  - filterGoogleVeo: boolean (仅视频库模式有效)
  
children:
  - PromptTab: 提示词列表
  - ImageTab: 图片网格
  - VideoTab: 视频网格
```

**4. UserMenu.jsx - 用户菜单**
```jsx
- 显示用户名
- 我的资源库（打开LibraryModal）
- 退出登录
```

### 11.2 修改组件

**1. Header.jsx**
```jsx
// 右上角添加
{isLoggedIn ? <UserMenu /> : <Button onClick={goToLogin}>登录</Button>}
```

**2. PromptInput.jsx（文生图/图生视频/视频延长的提示词输入）**
```jsx
// 输入框旁边添加
<Button 
  icon={<HistoryOutlined />} 
  onClick={() => openLibrary('prompt')}
>
  历史提示词
</Button>
```

**3. ImageUpload.jsx（参考图、首帧、尾帧上传）**
```jsx
// 上传按钮旁边添加
<Button 
  icon={<FolderOpenOutlined />}
  onClick={() => openLibrary('image')}
>
  从图片库选择
</Button>
```

**4. VideoUpload.jsx（视频延长的视频选择）**
```jsx
// 改为只能从库选择，不支持本地上传
<Button 
  icon={<FolderOpenOutlined />}
  onClick={() => openLibrary('video', { filterGoogleVeo: isGoogleVeoModel })}
>
  选择视频
</Button>

{isGoogleVeoModel && (
  <Alert 
    type="info" 
    message="Google Veo 仅支持延长由其生成的视频"
  />
)}
```

---

## 十二、开发计划（修订）

### 阶段1：用户认证系统（2-3天）
**后端：**
- [ ] 创建数据库表（users）
- [ ] 实现注册接口（用户名+密码+哈希）
- [ ] 实现登录接口（JWT Token）
- [ ] 实现认证中间件
- [ ] 实现获取当前用户接口

**前端：**
- [ ] 创建 authStore（Zustand）
- [ ] 开发 Login.jsx 页面
- [ ] 开发 Register.jsx 页面
- [ ] 实现路由保护
- [ ] 开发 UserMenu 组件
- [ ] 修改 Header 添加用户菜单

### 阶段2：自动保存机制（2-3天）
**后端：**
- [ ] 创建数据库表（prompt_history, user_images, user_videos）
- [ ] 修改文生图接口：成功后保存到 user_images
- [ ] 修改图生视频接口：成功后保存到 user_videos
  - [ ] **判断模型，设置 is_google_veo 字段**
- [ ] 修改视频延长接口：成功后保存到 user_videos
  - [ ] **判断模型，设置 is_google_veo 字段**
  - [ ] 关联 source_video_id
- [ ] 提示词优化时保存到 prompt_history

**测试：**
- [ ] 验证各类内容自动保存
- [ ] 验证 Google Veo 视频标记正确

### 阶段3：资源库和弹窗（3-4天）
**后端：**
- [ ] 实现 GET /api/library/prompts（分页+搜索）
- [ ] 实现 GET /api/library/images（分页+搜索+模型筛选）
- [ ] 实现 GET /api/library/videos（分页+搜索+google_veo_only筛选）

**前端：**
- [ ] 创建 libraryStore（Zustand）
- [ ] 开发 LibraryModal 组件
  - [ ] Tab切换逻辑
  - [ ] 三个Tab子组件（PromptTab, ImageTab, VideoTab）
  - [ ] 搜索功能
  - [ ] 无限滚动加载
  - [ ] **视频Tab显示 Google Veo 标记（蓝色徽章）**
- [ ] 修改提示词输入组件，添加"历史"按钮
- [ ] 修改图片上传组件，添加"从图片库选择"按钮
- [ ] 修改视频上传组件：
  - [ ] 改为"选择视频"按钮（移除本地上传）
  - [ ] **根据当前模型传递 filterGoogleVeo 参数**
  - [ ] **显示 Google Veo 限制提示**

**测试：**
- [ ] 验证弹窗打开/关闭
- [ ] 验证三个Tab切换
- [ ] 验证选择功能
- [ ] **验证 Google Veo 筛选逻辑**
- [ ] 验证搜索功能

---

## 十三、特别注意事项

### 🎯 Google Veo 视频标记实现清单

1. **保存时自动标记：**
   ```python
   # 在 image_to_video.py 或 video_extension.py 中
   if 'google-veo' in request.model.lower():
       is_google_veo = True
   else:
       is_google_veo = False
   
   # 保存到数据库时带上这个字段
   ```

2. **API查询时支持筛选：**
   ```python
   # GET /api/library/videos?google_veo_only=true
   if google_veo_only:
       query = query.filter(user_videos.is_google_veo == True)
   ```

3. **前端视频卡片显示标记：**
   ```jsx
   {video.is_google_veo && (
     <Tag color="blue" icon={<GoogleOutlined />}>
       Google Veo
     </Tag>
   )}
   ```

4. **视频延长页面自动筛选：**
   ```jsx
   const openVideoLibrary = () => {
     const filterGoogleVeo = selectedModel.includes('google-veo');
     setLibraryModal({
       visible: true,
       mode: 'video',
       filterGoogleVeo
     });
   };
   ```

---

**预估总工作量：7-10 个工作日**

**准备开始开发？请确认以上需求是否完整！**

