# 已泄露密钥报告

## 📋 曾经在Git历史中暴露的密钥清单

根据清理前的Git历史记录分析，以下密钥曾经被硬编码在代码中并提交到了版本库：

### 1. DeepSeek API Key
- **密钥值**: `sk-1c800af6...` (已掩码，请轮换此密钥)
- **位置**: `backend/app/core/config.py`
- **暴露时间**: 在提交 `c3706cf` 中首次出现
- **状态**: ✅ 已从历史中清理

### 2. Google Gemini API Keys（多个版本）
- **密钥值1**: `AIzaSyCSES6...` (已掩码，请轮换此密钥)
- **密钥值2**: `AIzaSyAemKS...` (已掩码，请轮换此密钥)
- **位置**: `backend/app/core/config.py`
- **暴露时间**: 在多个提交中反复出现
- **状态**: ✅ 已从历史中清理

### 3. Sora API Key
- **密钥值**: `sk-xwr8Ej6...` (已掩码，请轮换此密钥)
- **位置**: `backend/app/core/config.py`
- **暴露时间**: 在提交历史中出现
- **状态**: ✅ 已从历史中清理

### 4. DashScope API Key
- **密钥值**: `sk-8b6db59...` (已掩码，已更换)
- **位置**: `backend/app/core/config.py`
- **暴露时间**: 在提交历史中出现
- **状态**: ✅ 已从历史中清理

### 5. 阿里云OSS AccessKey ID
- **密钥值**: `LTAI5tE43w...` (已掩码，请轮换此密钥)
- **位置**: `backend/app/core/config.py`
- **暴露时间**: 在提交历史中出现
- **状态**: ✅ 已从历史中清理

### 6. 阿里云OSS AccessKey Secret
- **密钥值**: `l3YNdvqHSO...` (已掩码，请轮换此密钥)
- **位置**: `backend/app/core/config.py`
- **暴露时间**: 在提交历史中出现
- **状态**: ✅ 已从历史中清理

### 7. 阿里云OSS Bucket Name
- **Bucket名称**: `tool251027`
- **位置**: `backend/app/core/config.py`
- **暴露时间**: 在提交历史中出现
- **状态**: ✅ 已从历史中清理

## ⚠️ 重要提醒

**以上所有密钥都曾经暴露在Git历史记录中**，即使已经从历史中清理，也建议：

1. **立即轮换所有密钥**
   - 在对应服务商控制台删除/禁用这些密钥
   - 生成新的密钥
   - 更新本地 `.env` 文件

2. **检查访问日志**
   - 检查是否有异常访问记录
   - 确认是否有未授权的使用

3. **通知团队成员**
   - 如果仓库是共享的，通知所有成员更新密钥
   - 确保所有成员都使用新的密钥

## 🔒 密钥轮换指南

### DeepSeek
1. 访问：https://platform.deepseek.com/api_keys
2. 删除旧密钥（前缀：`sk-1c800af6...`）
3. 创建新密钥
4. 更新 `.env` 文件中的 `DEEPSEEK_API_KEY`

### Google Gemini
1. 访问：https://aistudio.google.com/app/apikey
2. 删除旧密钥（前缀：`AIzaSyCSES6...` 和 `AIzaSyAemKS...`）
3. 创建新密钥
4. 更新 `.env` 文件中的 `GEMINI_API_KEY`

### Sora API
1. 联系Sora API服务提供商
2. 删除/禁用旧密钥（前缀：`sk-xwr8Ej6...`）
3. 创建新密钥
4. 更新 `.env` 文件中的 `SORA_API_KEY`

### 阿里云DashScope
1. 访问：https://dashscope.console.aliyun.com/apiKey
2. 删除旧密钥（前缀：`sk-8b6db59...`，已更换）
3. 创建新密钥
4. 更新 `.env` 文件中的 `DASHSCOPE_API_KEY`

### 阿里云OSS
1. 访问：https://ram.console.aliyun.com/manage/ak
2. 删除旧AccessKey（前缀：`LTAI5tE43w...`）
3. 创建新AccessKey
4. 更新 `.env` 文件中的 `OSS_ACCESS_KEY_ID` 和 `OSS_ACCESS_KEY_SECRET`
5. 检查Bucket `tool251027` 的访问权限设置

## 📊 清理统计

- **清理的提交数**: 13个提交
- **清理的密钥类型**: 7种
- **清理的密钥数量**: 8个唯一密钥值
- **清理状态**: ✅ 完成

## 🔐 强制推送说明

### 强制推送的作用

**是的，强制推送可以改变远程仓库的历史记录。**

当你执行 `git push --force` 时：

1. **覆盖远程历史**: 远程仓库的历史记录会被本地重写后的历史替换
2. **永久删除**: 旧的提交（包含密钥的版本）将从远程仓库中移除
3. **无法恢复**: 一旦强制推送完成，远程仓库中的旧历史就无法通过正常方式访问

### 强制推送的注意事项

⚠️ **重要警告**：

1. **影响所有协作者**
   - 其他团队成员需要重新克隆仓库或强制拉取
   - 他们的本地提交历史会与远程不一致

2. **可能破坏保护分支**
   - 如果远程仓库有分支保护规则，可能需要临时禁用
   - 某些CI/CD流程可能需要重新配置

3. **无法完全删除**
   - 如果有人已经克隆了仓库，他们本地仍有旧历史
   - GitHub/GitLab等平台可能保留一些备份

4. **GitHub Secret Scanning仍然可能检测到**
   - 即使强制推送，GitHub的Secret Scanning可能仍会标记
   - 需要联系GitHub支持清除扫描结果

### 推荐的推送流程

```bash
# 1. 确认本地历史已清理
git log --all -p -- backend/app/core/config.py | grep -E "(sk-|AIzaSy|LTAI)"

# 2. 创建备份标签（可选）
git tag backup-before-force-push

# 3. 强制推送
git push origin main --force

# 4. 如果有保护分支，可能需要先禁用保护
# 在GitHub/GitLab设置中临时禁用分支保护

# 5. 通知团队成员
# 让他们执行：git fetch origin && git reset --hard origin/main
```

### 替代方案（如果不想强制推送）

如果不想强制推送，可以考虑：

1. **创建新仓库**
   - 将清理后的代码推送到新仓库
   - 旧仓库标记为已废弃

2. **使用新分支**
   - 创建新分支（如 `main-cleaned`）
   - 设置为默认分支
   - 删除旧分支

3. **联系平台支持**
   - 联系GitHub/GitLab支持清除Secret Scanning结果
   - 可能需要提供密钥轮换证明

## ✅ 当前状态

- ✅ Git历史已清理
- ✅ 当前代码无硬编码密钥
- ✅ 备份分支已创建：`backup-before-secret-cleanup`
- ⚠️ 需要轮换所有暴露的密钥
- ⚠️ 需要强制推送才能更新远程历史

