/**
 * 生成参数配置和生成按钮组件
 */

import React from 'react';
import { Card, Select, Space, Slider, Tag, Tooltip, Button } from 'antd';
import { 
  RocketOutlined, 
  InfoCircleOutlined
} from '@ant-design/icons';
import useImageStore from '../../store/imageStore';

const { Option } = Select;

const GenerateParams = ({ onGenerate }) => {
  const {
    selectedImageModel,
    textToImageModels,
    userPrompt,
    optimizedPrompt,
    isGenerating
  } = useImageStore();
  
  const [numImages, setNumImages] = React.useState(1);
  const [imageSize, setImageSize] = React.useState('1024x1024');
  
  // 获取当前模型信息
  const currentModel = textToImageModels[selectedImageModel] || {};
  
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
          <span>⚙️ 生成参数</span>
          <Tooltip title="配置图片尺寸和生成数量">
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>
      }
      variant="borderless"
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
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

export default GenerateParams;

