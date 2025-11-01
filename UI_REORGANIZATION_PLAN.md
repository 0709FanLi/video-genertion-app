# UI 重组开发方案：参数设置合并到模型选择

## 一、概述

### 1.1 目标
将文生图、图生视频、视频扩展三个页面中的参数设置内容合并到模型选择组件下方，取消独立的"参数设置"组件，简化UI结构。

### 1.2 影响范围
- **文生图页面** (`TextToImage/index.jsx`)
- **图生视频页面** (`ImageToVideo/index.jsx`)
- **视频扩展页面** (`VideoExtension/index.jsx`)

---

## 二、当前结构分析

### 2.1 文生图页面

**当前组件顺序**：
1. `ModelSelector` - 模型选择
2. `ReferenceUpload` - 参考图上传
3. `PromptInput` - 提示词输入
4. `GenerateParams` - 生成参数（图片尺寸、生成数量、生成按钮）

**参数设置内容**（在 `GenerateParams.jsx` 中）：
- 图片尺寸选择（Select下拉框）
- 生成数量滑块（Slider，1-4张）
- 生成按钮（包含在参数组件中）

---

### 2.2 图生视频页面

**当前组件顺序**：
1. `ModelSelector` - 模型选择
2. `ImageUpload` - 图片上传
3. `FrameSwitch` - 首尾帧交换
4. `PromptInput` - 提示词输入
5. `VideoParams` - 视频参数设置
6. 生成按钮（独立）

**参数设置内容**（在 `VideoParams.jsx` 中）：
- 长宽比选择（仅文生视频和Google Veo显示，网格布局）
- 视频时长滑块（Slider，根据模型支持4/5/6/8/10/15秒）
- 视频分辨率选择（Select下拉框，根据模型动态选项）
- Sora 2 模型特殊说明（信息提示）

---

### 2.3 视频扩展页面

**当前组件顺序**：
1. `ModelSelector` - 模型选择
2. `VideoUpload` - 视频上传
3. `ExtensionPromptInput` - 扩展提示词输入
4. `ExtensionParams` - 扩展参数设置
5. 生成按钮（独立）

**参数设置内容**（在 `ExtensionParams.jsx` 中）：
- 视频长宽比（Radio.Group，16:9 / 9:16）
- 视频分辨率（Radio.Group，720P / 1080P）
- 视频时长（Radio.Group，4秒 / 6秒 / 8秒）

---

## 三、重组方案

### 3.1 总体策略

1. **保持模型选择组件核心功能不变**：模型选择、模型说明等功能保留
2. **将参数设置内容集成到模型选择组件底部**：作为模型选择Card的一部分
3. **移除独立的参数设置组件**：不再在主页面中使用
4. **保持所有参数逻辑不变**：参数验证、自动调整等逻辑保留

---

### 3.2 文生图页面重组

#### 3.2.1 修改文件
- `frontend/src/components/TextToImage/ModelSelector.jsx` - 添加参数设置
- `frontend/src/components/TextToImage/index.jsx` - 移除 `GenerateParams` 组件

#### 3.2.2 ModelSelector 修改内容

**在模型选择Card底部添加参数设置区域**：

```javascript
// 在 ModelSelector 组件中
<Card>
  {/* 现有的模型选择内容 */}
  <Select>...</Select>
  {currentModel && <div>模型说明...</div>}
  
  {/* 新增：参数设置区域 */}
  <Divider style={{ margin: '16px 0' }} />
  <div style={{ marginTop: '16px' }}>
    {/* 图片尺寸选择 */}
    <div style={{ marginBottom: '16px' }}>
      <div style={{ marginBottom: 8, fontWeight: 500 }}>
        图片尺寸
      </div>
      <Select
        value={imageSize}
        onChange={setImageSize}
        style={{ width: '100%' }}
        disabled={isGenerating}
      >
        {sizeOptions.map(option => (
          <Option key={option.value} value={option.value}>
            {option.label}
          </Option>
        ))}
      </Select>
    </div>
    
    {/* 生成数量滑块 */}
    <div>
      <div style={{ marginBottom: 8 }}>
        <Space>
          <span style={{ fontWeight: 500 }}>生成数量</span>
          <Tag color="blue">{numImages} 张</Tag>
        </Space>
      </div>
      <Slider
        min={1}
        max={4}
        step={1}
        value={numImages}
        onChange={setNumImages}
        marks={{ 1: '1', 2: '2', 3: '3', 4: '4' }}
        disabled={isGenerating}
      />
    </div>
  </div>
</Card>
```

**注意**：
- 生成按钮保留在 `GenerateParams` 中，但 `GenerateParams` 只保留按钮部分
- 或者将生成按钮移到主页面（推荐）

#### 3.2.3 主页面修改

**移除 `GenerateParams` 组件，将生成按钮移到主页面**：

```javascript
// TextToImage/index.jsx
<Space direction="vertical" style={{ width: '100%' }} size="large">
  <ModelSelector />
  <ReferenceUpload />
  <PromptInput />
  
  {/* 生成按钮（从 GenerateParams 移过来） */}
  <Button 
    type="primary"
    icon={<RocketOutlined />}
    size="large"
    block
    loading={isGenerating}
    disabled={!canGenerate}
    onClick={handleGenerate}
  >
    {isGenerating ? '生成中...' : '🚀 开始生成图片'}
  </Button>
</Space>
```

---

### 3.3 图生视频页面重组

#### 3.3.1 修改文件
- `frontend/src/components/ImageToVideo/ModelSelector.jsx` - 添加参数设置
- `frontend/src/components/ImageToVideo/index.jsx` - 移除 `VideoParams` 组件

#### 3.3.2 ModelSelector 修改内容

**在模型选择Card底部添加参数设置区域**：

```javascript
// 在 ModelSelector 组件中导入必要的hooks和组件
import useVideoStore from '../../store/videoStore';
import { Slider, Select, Space, Tag, Divider } from 'antd';
import { ClockCircleOutlined, HighlightOutlined, BorderOutlined } from '@ant-design/icons';

// 在组件中获取参数状态
const {
  duration,
  setDuration,
  resolution,
  setResolution,
  aspectRatio,
  setAspectRatio,
  selectedModel,
  generating
} = useVideoStore();

// 在Card底部添加参数设置
<Card>
  {/* 现有的模型选择内容 */}
  <Select>...</Select>
  {currentModel && <div>模型说明...</div>}
  
  {/* 新增：参数设置区域 */}
  <Divider style={{ margin: '16px 0' }} />
  <div style={{ marginTop: '16px' }}>
    {/* 长宽比设置（仅文生视频和Google Veo） */}
    {(isTextToVideo || isGoogleVeo) && (
      <div style={{ marginBottom: '16px' }}>
        {/* 长宽比选择网格 */}
      </div>
    )}
    
    {/* 时长设置 */}
    <div style={{ marginBottom: '16px' }}>
      {/* 时长滑块 */}
    </div>
    
    {/* 分辨率设置（非Sora 2模型） */}
    {!isSoraV2 && (
      <div>
        {/* 分辨率下拉框 */}
      </div>
    )}
    
    {/* Sora 2 特殊说明 */}
    {isSoraV2 && (
      <div>
        {/* Sora 2 参数说明 */}
      </div>
    )}
  </div>
</Card>
```

**注意**：
- 所有参数逻辑从 `VideoParams.jsx` 复制过来
- 保持参数验证和自动调整逻辑

#### 3.3.3 主页面修改

**移除 `VideoParams` 组件**：

```javascript
// ImageToVideo/index.jsx
<Space direction="vertical" style={{ width: '100%' }} size="large">
  <ModelSelector />  {/* 现在包含参数设置 */}
  <ImageUpload />
  <FrameSwitch />
  <PromptInput />
  {/* VideoParams 已移除 */}
  {/* 生成按钮保持不变 */}
</Space>
```

---

### 3.4 视频扩展页面重组

#### 3.4.1 修改文件
- `frontend/src/components/VideoExtension/ModelSelector.jsx` - 添加参数设置
- `frontend/src/components/VideoExtension/index.jsx` - 移除 `ExtensionParams` 组件

#### 3.4.2 ModelSelector 修改内容

**在模型选择Card底部添加参数设置区域**：

```javascript
// 在 ModelSelector 组件中导入必要的hooks和组件
import useVideoExtensionStore from '../../store/videoExtensionStore';
import { Radio, Space, Tag, Divider } from 'antd';
import { BorderOutlined, ThunderboltOutlined, VideoCameraOutlined } from '@ant-design/icons';

// 在组件中获取参数状态
const {
  aspectRatio,
  duration,
  resolution,
  setAspectRatio,
  setDuration,
  setResolution,
  isExtending
} = useVideoExtensionStore();

// 在Card底部添加参数设置
<Card>
  {/* 现有的模型选择内容 */}
  <Select>...</Select>
  {currentModel && <div>模型说明...</div>}
  
  {/* 新增：参数设置区域 */}
  <Divider style={{ margin: '16px 0' }} />
  <Space direction="vertical" style={{ width: '100%' }} size="large">
    {/* 长宽比选择 */}
    <div>
      <div style={{ marginBottom: '12px', fontWeight: 500 }}>
        <BorderOutlined /> 视频长宽比 <Tag color="blue">{aspectRatio}</Tag>
      </div>
      <Radio.Group
        value={aspectRatio}
        onChange={(e) => setAspectRatio(e.target.value)}
        disabled={isExtending}
        buttonStyle="solid"
      >
        <Radio.Button value="16:9">16:9 ▭</Radio.Button>
        <Radio.Button value="9:16">9:16 ▯</Radio.Button>
      </Radio.Group>
    </div>
    
    {/* 分辨率选择 */}
    <div>
      <div style={{ marginBottom: '12px', fontWeight: 500 }}>
        <ThunderboltOutlined /> 视频分辨率 <Tag color="green">{resolution}</Tag>
      </div>
      <Radio.Group
        value={resolution}
        onChange={(e) => setResolution(e.target.value)}
        disabled={isExtending}
        buttonStyle="solid"
      >
        <Radio.Button value="720p">720P</Radio.Button>
        <Radio.Button value="1080p">1080P</Radio.Button>
      </Radio.Group>
    </div>
    
    {/* 时长选择 */}
    <div>
      <div style={{ marginBottom: '12px', fontWeight: 500 }}>
        <VideoCameraOutlined /> 视频时长 <Tag color="orange">{duration}秒</Tag>
      </div>
      <Radio.Group
        value={duration}
        onChange={(e) => setDuration(e.target.value)}
        disabled={isExtending}
        buttonStyle="solid"
      >
        <Radio.Button value={4}>4秒</Radio.Button>
        <Radio.Button value={6}>6秒</Radio.Button>
        <Radio.Button value={8}>8秒</Radio.Button>
      </Radio.Group>
    </div>
  </Space>
</Card>
```

#### 3.4.3 主页面修改

**移除 `ExtensionParams` 组件**：

```javascript
// VideoExtension/index.jsx
<Space direction="vertical" style={{ width: '100%' }} size="large">
  <ModelSelector />  {/* 现在包含参数设置 */}
  <VideoUpload />
  <ExtensionPromptInput />
  {/* ExtensionParams 已移除 */}
  {/* 生成按钮保持不变 */}
</Space>
```

---

## 四、详细实施步骤

### 4.1 文生图页面

**步骤1**：修改 `ModelSelector.jsx`
- ✅ 导入 `useImageStore` 获取参数状态
- ✅ 导入 `Divider`, `Select`, `Slider`, `Tag` 等组件
- ✅ 在模型说明下方添加 Divider
- ✅ 添加图片尺寸选择组件
- ✅ 添加生成数量滑块组件
- ✅ 添加参数状态管理逻辑（从 `GenerateParams.jsx` 复制）

**步骤2**：修改 `index.jsx`
- ✅ 移除 `GenerateParams` 组件导入
- ✅ 移除 `<GenerateParams onGenerate={handleGenerate} />` 组件调用
- ✅ 将生成按钮移到主页面（从 `GenerateParams` 移过来）
- ✅ 确保 `handleGenerate` 函数能正确获取参数（从 store 获取）

**步骤3**：可选 - 简化 `GenerateParams.jsx`
- 方案A：保留文件但只保留生成按钮部分（如果不想改动太大）
- 方案B：删除文件，生成按钮移到主页面（推荐）

---

### 4.2 图生视频页面

**步骤1**：修改 `ModelSelector.jsx`
- ✅ 导入 `useVideoStore` 获取参数状态
- ✅ 导入 `Divider`, `Slider`, `Select`, `Space`, `Tag` 等组件
- ✅ 导入图标组件（`ClockCircleOutlined`, `HighlightOutlined`, `BorderOutlined`）
- ✅ 在模型说明下方添加 Divider
- ✅ 复制 `VideoParams.jsx` 中的所有参数设置逻辑
- ✅ 添加长宽比选择（条件渲染）
- ✅ 添加时长滑块
- ✅ 添加分辨率选择（条件渲染）
- ✅ 添加 Sora 2 特殊说明（条件渲染）
- ✅ 复制所有 useEffect 逻辑（自动调整参数）

**步骤2**：修改 `index.jsx`
- ✅ 移除 `VideoParams` 组件导入
- ✅ 移除 `<VideoParams />` 组件调用

**步骤3**：可选 - 删除 `VideoParams.jsx`
- 如果不再需要，可以删除文件

---

### 4.3 视频扩展页面

**步骤1**：修改 `ModelSelector.jsx`
- ✅ 导入 `useVideoExtensionStore` 获取参数状态
- ✅ 导入 `Divider`, `Radio`, `Space`, `Tag` 等组件
- ✅ 导入图标组件（`BorderOutlined`, `ThunderboltOutlined`, `VideoCameraOutlined`）
- ✅ 在模型说明下方添加 Divider
- ✅ 复制 `ExtensionParams.jsx` 中的所有参数设置逻辑
- ✅ 添加长宽比 Radio.Group
- ✅ 添加分辨率 Radio.Group
- ✅ 添加时长 Radio.Group

**步骤2**：修改 `index.jsx`
- ✅ 移除 `ExtensionParams` 组件导入
- ✅ 移除 `<ExtensionParams />` 组件调用

**步骤3**：可选 - 删除 `ExtensionParams.jsx`
- 如果不再需要，可以删除文件

---

## 五、技术要点

### 5.1 状态管理
- 所有参数状态已经在各自的 Store 中管理
- 只需要在 `ModelSelector` 中通过 `useStore` hook 获取状态和更新函数
- 不需要额外的状态提升

### 5.2 样式统一
- 参数设置区域使用 `Divider` 分隔
- 保持与原有参数设置组件相同的样式风格
- 确保在不同屏幕尺寸下正常显示

### 5.3 条件渲染
- 根据模型类型动态显示/隐藏参数选项
- 保持原有的参数验证和自动调整逻辑
- 确保参数设置与模型选择联动

### 5.4 代码复用
- 参数设置逻辑可以直接从原参数组件复制
- 保持所有 useEffect 逻辑（自动调整）
- 保持所有验证逻辑

---

## 六、文件清单

### 6.1 需要修改的文件

**文生图**：
- `frontend/src/components/TextToImage/ModelSelector.jsx` - 添加参数设置
- `frontend/src/components/TextToImage/index.jsx` - 移除 GenerateParams，添加生成按钮

**图生视频**：
- `frontend/src/components/ImageToVideo/ModelSelector.jsx` - 添加参数设置
- `frontend/src/components/ImageToVideo/index.jsx` - 移除 VideoParams

**视频扩展**：
- `frontend/src/components/VideoExtension/ModelSelector.jsx` - 添加参数设置
- `frontend/src/components/VideoExtension/index.jsx` - 移除 ExtensionParams

### 6.2 可选删除的文件

- `frontend/src/components/TextToImage/GenerateParams.jsx` - 如果功能完全移到 ModelSelector
- `frontend/src/components/ImageToVideo/VideoParams.jsx` - 如果功能完全移到 ModelSelector
- `frontend/src/components/VideoExtension/ExtensionParams.jsx` - 如果功能完全移到 ModelSelector

---

## 七、注意事项

### 7.1 向后兼容
- 确保所有参数功能保持不变
- 确保参数验证逻辑不变
- 确保自动调整逻辑不变

### 7.2 用户体验
- 参数设置区域应该清晰可见
- 使用 Divider 分隔模型选择和参数设置
- 保持响应式布局

### 7.3 代码维护
- 保持代码结构清晰
- 添加必要的注释
- 确保组件职责单一（虽然合并了UI，但逻辑要清晰）

---

## 八、开发顺序建议

1. ✅ **第一步**：文生图页面重组（最简单，参数最少）
2. ✅ **第二步**：视频扩展页面重组（参数较简单）
3. ✅ **第三步**：图生视频页面重组（参数最复杂，有多个条件渲染）

---

## 九、预期效果

### 9.1 UI结构变化

**文生图页面**：
```
[模型选择 + 参数设置]（合并为一个Card）
[参考图上传]
[提示词输入]
[生成按钮]
```

**图生视频页面**：
```
[模型选择 + 参数设置]（合并为一个Card）
[图片上传]
[首尾帧交换]
[提示词输入]
[生成按钮]
```

**视频扩展页面**：
```
[模型选择 + 参数设置]（合并为一个Card）
[视频上传]
[扩展提示词输入]
[生成按钮]
```

### 9.2 用户体验提升
- ✅ 减少组件数量，UI更简洁
- ✅ 模型选择和参数设置在同一位置，关联性更强
- ✅ 减少页面滚动，提高操作效率

---

## 十、风险评估

### 10.1 潜在问题
1. **组件复杂度增加**：ModelSelector 组件会变大
   - **缓解方案**：保持代码结构清晰，添加注释

2. **参数逻辑耦合**：参数设置与模型选择在同一个组件
   - **缓解方案**：保持逻辑分离，使用清晰的函数命名

3. **响应式布局**：参数设置可能在小屏幕上显示不佳
   - **缓解方案**：测试不同屏幕尺寸，确保布局正常

### 10.2 测试要点
- ✅ 测试所有模型的参数设置是否正确显示
- ✅ 测试参数切换是否正常工作
- ✅ 测试自动调整逻辑是否正常
- ✅ 测试不同屏幕尺寸下的显示效果
- ✅ 测试生成功能是否正常（参数是否正确传递）

