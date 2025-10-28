/**
 * 模型选择和生成参数配置组件
 */

import React from 'react';
import { Card, Select, Space, Slider, Tag, Tooltip, Row, Col, Button } from 'antd';
import { 
  RocketOutlined, 
  InfoCircleOutlined,
  CheckCircleOutlined 
} from '@ant-design/icons';
import useImageStore from '../../store/imageStore';

const { Option } = Select;

const ModelSelector = ({ onGenerate }) => {
  const {
    selectedImageModel,
    textToImageModels,
    userPrompt,
    optimizedPrompt,
    isGenerating,
    selectImageModel
  } = useImageStore();
  
  const [numImages, setNumImages] = React.useState(1);
  const [imageSize, setImageSize] = React.useState('1024x1024');
  
  // 获取当前模型信息
  const currentModel = textToImageModels[selectedImageModel] || {};
  const supportsReference = currentModel.supports_reference || false;
  const maxReferenceImages = currentModel.max_reference_images || 0;
  
  // 图片尺寸选项
  const sizeOptions = [
    { label: '1024×1024 (正方形)', value: '1024x1024' },
    { label: '1024×768 (横向)', value: '1024x768' },
    { label: '768×1024 (竖向)', value: '768x1024' },
  ];
  
  // 检查是否可以生成
  const canGenerate = (userPrompt.trim() || optimizedPrompt.trim()) && !isGenerating;
  
  // 处理生成按钮点击
  const handleGenerate = () => {
    if (onGenerate) {
      onGenerate({
        numImages,
        size: imageSize
      });
    }
  };
  
  return (
    <Card 
      title={
        <Space>
          <span>⚙️ 生成配置</span>
          <Tooltip title="选择生成模型和配置参数">
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>
      }
      variant="borderless"
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 模型选择 */}
        <div>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>
            选择生成模型
          </div>
          <Select
            value={selectedImageModel}
            onChange={selectImageModel}
            style={{ width: '100%' }}
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
              marginTop: 8, 
              padding: 8, 
              backgroundColor: '#f0f0f0', 
              borderRadius: 4,
              fontSize: 12
            }}>
              <Space direction="vertical" size={4}>
                <div><CheckCircleOutlined style={{ color: '#52c41a' }} /> 当前: {currentModel.name}</div>
                {supportsReference && (
                  <div>
                    <InfoCircleOutlined style={{ color: '#1890ff' }} />
                    {' '}支持最多 {maxReferenceImages} 张参考图
                  </div>
                )}
              </Space>
            </div>
          )}
        </div>
        
        {/* 图片尺寸 */}
        <div>
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
        
        {/* 生成按钮 */}
        <Button 
          type="primary"
          icon={<RocketOutlined />}
          size="large"
          block
          loading={isGenerating}
          disabled={!canGenerate}
          onClick={handleGenerate}
          style={{
            height: 50,
            fontSize: 16,
            fontWeight: 'bold',
            background: canGenerate 
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : undefined,
            border: 'none',
            cursor: canGenerate ? 'pointer' : 'not-allowed',
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            boxShadow: canGenerate ? '0 4px 12px rgba(102, 126, 234, 0.4)' : 'none',
            transition: 'all 0.3s'
          }}
          onMouseEnter={(e) => {
            if (canGenerate) {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.5)';
            }
          }}
          onMouseLeave={(e) => {
            if (canGenerate) {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
            }
          }}
        >
          {isGenerating ? '生成中...' : '🚀 开始生成图片'}
        </Button>
        
        {/* 提示信息 */}
        {!canGenerate && !isGenerating && (
          <div style={{ 
            padding: '8px 12px', 
            backgroundColor: '#fff7e6', 
            borderRadius: 4,
            fontSize: 12,
            color: '#d46b08'
          }}>
            <InfoCircleOutlined style={{ marginRight: 8 }} />
            请先输入提示词
          </div>
        )}
        
        {isGenerating && (
          <div style={{ 
            padding: '8px 12px', 
            backgroundColor: '#e6f7ff', 
            borderRadius: 4,
            fontSize: 12,
            color: '#1890ff'
          }}>
            <InfoCircleOutlined style={{ marginRight: 8 }} />
            正在生成图片，通常需要 30-60 秒...
          </div>
        )}
      </Space>
    </Card>
  );
};

export default ModelSelector;

