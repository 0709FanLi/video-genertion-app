# 安全配置指南

## 概述

本项目已配置为使用环境变量管理所有敏感信息（API密钥、AccessKey等），禁止在代码中硬编码任何密钥。

## 环境变量配置

### 快速开始

1. 复制环境变量示例文件：
   ```bash
   cd backend
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入真实的密钥值：
   ```bash
   # 使用你喜欢的编辑器
   nano .env
   # 或
   vim .env
   ```

3. 确保 `.env` 文件已被 Git 忽略（已在 `.gitignore` 中配置）

### 必需的环境变量

#### 阿里云DashScope（通义千问/通义万相）
- `DASHSCOPE_API_KEY`: 阿里云DashScope API密钥
  - 获取地址：https://dashscope.console.aliyun.com/apiKey

#### 火山引擎即梦
- `VOLC_ACCESS_KEY_ID`: 火山引擎AccessKeyId
- `VOLC_SECRET_ACCESS_KEY`: 火山引擎SecretAccessKey
  - 获取地址：https://console.volcengine.com/iam/keymanage/

#### DeepSeek
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
  - 获取地址：https://platform.deepseek.com/api_keys

#### Google Gemini/Veo
- `GEMINI_API_KEY`: Google Gemini API密钥
  - 获取地址：https://aistudio.google.com/app/apikey

#### Sora 2 API
- `SORA_API_KEY`: Sora API密钥
  - 获取地址：请联系Sora API服务提供商

#### 阿里云OSS（图片/视频存储）
- `OSS_ACCESS_KEY_ID`: OSS AccessKeyId
- `OSS_ACCESS_KEY_SECRET`: OSS AccessKeySecret
- `OSS_BUCKET_NAME`: OSS Bucket名称
- `OSS_ENDPOINT`: OSS Endpoint（可选，默认：https://oss-cn-shanghai.aliyuncs.com）
  - 获取地址：https://ram.console.aliyun.com/manage/ak

#### JWT认证
- `SECRET_KEY`: JWT签名密钥（生产环境必须设置强密钥）
- `ACCESS_TOKEN_EXPIRE_DAYS`: Token有效期（默认：7天）

#### 数据库
- `DATABASE_URL`: 数据库连接URL（默认：SQLite）

## Git Secret Scanning 问题处理

### ✅ 历史记录已清理

所有历史提交中的硬编码密钥已被清理。当前代码库不包含任何硬编码的敏感信息。

### 验证清理结果

```bash
# 检查历史记录中是否还有硬编码密钥
git log --all -p -- backend/app/core/config.py | grep -E "(sk-|AIzaSy|LTAI|tool251027)"

# 应该只显示在 diff 中被删除的行（带 - 号），不应该有当前版本的硬编码密钥
```

### 如果将来遇到 Secret Scanning 问题

1. **确认当前代码状态**
   - 检查配置文件中是否有硬编码密钥
   - 确保所有密钥都从环境变量读取

2. **从 Git 历史中移除密钥**
   - 参考本仓库已执行的清理流程
   - 使用 `git filter-branch` 或 `git filter-repo` 工具

3. **旋转已泄露的密钥**
   - 在服务商控制台删除/禁用旧密钥
   - 生成新密钥并更新 `.env` 文件

## 最佳实践

1. **永远不要提交 `.env` 文件**
   - `.env` 文件已在 `.gitignore` 中配置
   - 使用 `.env.example` 作为模板

2. **代码审查时检查**
   - 确保没有硬编码密钥
   - 确保所有敏感信息都从环境变量读取

3. **使用密钥管理服务（生产环境）**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - 云服务商提供的密钥管理服务

4. **定期轮换密钥**
   - 建议每3-6个月轮换一次
   - 发现泄露立即轮换

## 配置文件说明

- `backend/app/core/config.py`: 主配置文件，使用Pydantic Settings管理
- `backend/.env.example`: 环境变量示例文件（可提交到Git）
- `backend/.env`: 实际环境变量文件（已忽略，不提交）

## 相关资源

- [Git Secret Scanning 文档](https://docs.github.com/en/code-security/secret-scanning)
- [Pydantic Settings 文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [OWASP 密钥管理最佳实践](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

