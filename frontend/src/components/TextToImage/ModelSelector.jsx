/**
 * 模型选择组件（仅模型选择）
 */

import React from 'react';
import { Card, Select, Space, Tag, Tooltip, Divider, Slider } from 'antd';
import { 
  InfoCircleOutlined,
  CheckCircleOutlined 
} from '@ant-design/icons';
import useImageStore from '../../store/imageStore';

const { Option } = Select;

const ModelSelector = () => {
  const {
    selectedImageModel,
    textToImageModels,
    isGenerating,
    selectImageModel,
    numImages,
    imageSize,
    setNumImages,
    setImageSize
  } = useImageStore();
  
  // 获取当前模型信息
  const currentModel = textToImageModels[selectedImageModel] || {};
  const supportsReference = currentModel.supports_reference || false;
  const maxReferenceImages = currentModel.max_reference_images || 0;
  
  // 图片尺寸选项（根据模型动态生成）
  const sizeOptions = React.useMemo(() => {
    // 如果模型有自定义的available_sizes，使用它
    if (currentModel.available_sizes && currentModel.available_sizes.length > 0) {
      return currentModel.available_sizes;
    }
    
    // 默认尺寸选项（火山引擎即梦、通义万相）
    return [
      { label: '1024×1024 (正方形)', value: '1024x1024' },
      { label: '1024×768 (横向)', value: '1024x768' },
      { label: '768×1024 (竖向)', value: '768x1024' },
    ];
  }, [currentModel, selectedImageModel]);
  
  // 自动调整imageSize（当模型切换且当前size不在可选项中时）
  React.useEffect(() => {
    const currentSizeAvailable = sizeOptions.some(opt => opt.value === imageSize);
    if (!currentSizeAvailable && sizeOptions.length > 0) {
      // 尝试找到默认1:1的选项，否则使用第一个
      const defaultSize = sizeOptions.find(opt => opt.ratio === '1:1') || sizeOptions[0];
      setImageSize(defaultSize.value);
    }
  }, [selectedImageModel, sizeOptions, imageSize]);
  
  
  return (
    <Card 
      title={
        <Space>
          <span>🎯 选择生成模型</span>
          <Tooltip title="选择生成图片的AI模型">
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>
      }
      variant="borderless"
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 模型选择 */}
        <Select
          value={selectedImageModel}
          onChange={selectImageModel}
          style={{ width: '100%' }}
          size="large"
          disabled={isGenerating}
        >
          {Object.entries(textToImageModels).map(([key, model]) => (
            <Option key={key} value={key}>
              <Space>
                <span>{model.name}</span>
                {model.default && <Tag color="green">推荐</Tag>}
                {model.supports_reference && <Tag color="blue">支持参考图</Tag>}
              </Space>
            </Option>
          ))}
        </Select>
        
        {/* 模型说明 */}
        {currentModel.name && (
          <div style={{ 
            padding: 12, 
            backgroundColor: '#f0f2f5', 
            borderRadius: 4,
            fontSize: 13
          }}>
            <Space direction="vertical" size={4}>
              <div>
                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                当前: {currentModel.name}
              </div>
              {supportsReference && (
                <div>
                  <InfoCircleOutlined style={{ color: '#1890ff', marginRight: 8 }} />
                  支持最多 {maxReferenceImages} 张参考图
                </div>
              )}
              {currentModel.description && (
                <div style={{ color: '#595959', lineHeight: 1.4 }}>
                  {currentModel.description}
                </div>
              )}
            </Space>
          </div>
        )}
        
        {/* 参数设置区域 */}
        <Divider style={{ margin: '16px 0' }} />
        <div style={{ marginTop: '16px' }}>
          {/* 图片尺寸 */}
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
          
          {/* 生成数量 */}
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
              marks={{
                1: '1',
                2: '2',
                3: '3',
                4: '4'
              }}
              disabled={isGenerating}
            />
          </div>
        </div>
      </Space>
    </Card>
  );
};

export default ModelSelector;

