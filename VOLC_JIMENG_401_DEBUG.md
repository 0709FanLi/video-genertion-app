# 火山引擎即梦 401 认证问题排查

## 问题现象
调用火山引擎即梦API时返回 `401 Unauthorized` 错误。

## 已完成的修复

### 1. 添加环境变量配置
已在 `.env` 文件中添加：
```bash
VOLC_ACCESS_KEY_ID=AKLTMjUzYmUyYjUzOTA5NGE2MWIyZTI4NzdjYzk3N2JhMjU
VOLC_SECRET_ACCESS_KEY=TmpRelpEZGxaVEF6TXpnMk5EWXhNemsyWlRKbU0ySTJaVGxsTnpnNVlqZw==
VOLC_BASE_URL=https://visual.volcengineapi.com
```

### 2. 修复签名头格式
根据官方Python示例，添加了缺失的 `X-Content-Sha256` 请求头：

**修复前**：
```python
headers = {
    "Content-Type": "application/json",
    "Host": "visual.volcengineapi.com",
    "X-Date": timestamp
}
```

**修复后**：
```python
payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

headers = {
    "Content-Type": "application/json",
    "Host": "visual.volcengineapi.com",
    "X-Date": timestamp,
    "X-Content-Sha256": payload_hash  # 新增
}

signed_headers = "content-type;host;x-content-sha256;x-date"
```

### 3. Secret Key 处理
移除了自动Base64解码逻辑，改为直接使用原始值（根据官方示例）。

---

## 待确认的问题

### Secret Key 格式
需要确认 `VOLC_SECRET_ACCESS_KEY` 的正确格式：

**选项A**: 原始 Secret Key
- 如果是原始值，格式应该类似：`3f4e7d0e03386461...`（纯字母数字）
- 当前配置：直接使用

**选项B**: Base64 编码后的 Secret Key
- 格式：`TmpRel...==`（包含 `==` 结尾）
- 当前配置：需要先解码

**测试解码**：
```bash
echo "TmpRelpEZGxaVEF6TXpnMk5EWXhNemsyWlRKbU0ySTJaVGxsTnpnNVlqZw==" | base64 -d
# 输出：4c5d746547...
```

---

## 官方示例签名流程

```python
# 1. 生成签名密钥
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode('utf-8'), dateStamp)       # ← key是原始字符串
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning

# 2. 构建 canonical_headers（必须包含这4个）
canonical_headers = 'content-type:' + content_type + '\n' + \
                   'host:' + host + '\n' + \
                   'x-content-sha256:' + payload_hash + '\n' + \
                   'x-date:' + current_date + '\n'

signed_headers = 'content-type;host;x-content-sha256;x-date'

# 3. 请求头
headers = {
    'X-Date': current_date,
    'Authorization': authorization_header,
    'X-Content-Sha256': payload_hash,
    'Content-Type': content_type
}
```

---

## 可能的原因

1. **Secret Key 格式错误**
   - 当前使用的是Base64编码值，但应该使用原始值
   - 或反之

2. **AccessKey ID 错误或已过期**
   - 需要在火山引擎控制台确认状态
   - 确认有"视觉智能"服务权限

3. **签名算法细节问题**
   - 虽然已添加 `X-Content-Sha256`，但可能还有其他细节差异

4. **API 版本或 Action 参数问题**
   - 当前使用：`CVSync2AsyncSubmitTask`
   - 官方示例使用：`CVProcess`
   - 需要确认即梦4.0使用哪个API

---

## 下一步排查方向

### 1. 确认 API Key 状态
登录火山引擎控制台：https://console.volcengine.com/
- 访问控制 → 访问密钥
- 确认 AccessKey 状态：启用/禁用
- 确认权限：是否有"视觉智能/即梦"权限

### 2. 测试 Secret Key 格式
提供以下信息（可部分遮蔽）：
- Secret Key 的前10个字符
- 是否以 `==` 结尾（判断是否Base64编码）
- 总长度

### 3. 尝试官方示例的 API
如果 `CVSync2AsyncSubmitTask` 不工作，尝试 `CVProcess`：
```python
query_params = {
    'Action': 'CVProcess',  # 改用同步API测试
    'Version': '2022-08-31',
}
```

---

## 参考资料

- 火山引擎官方文档：https://www.volcengine.com/docs/6348/69869
- AWS Signature V4：https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html

