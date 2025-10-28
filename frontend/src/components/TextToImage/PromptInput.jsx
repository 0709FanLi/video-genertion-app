/**
 * 提示词输入组件
 */

import React from 'react';
import { Card, Input, Button, Space, Select, Switch, Tag, Tooltip } from 'antd';
import { 
  ThunderboltOutlined, 
  SwapOutlined,
  InfoCircleOutlined 
} from '@ant-design/icons';
import useImageStore from '../../store/imageStore';
import { textToImageAPI } from '../../services/api';

const { TextArea } = Input;
const { Option } = Select;

const PromptInput = () => {
  const {
    userPrompt,
    optimizedPrompt,
    useOptimizedPrompt,
    selectedPromptModel,
    promptOptimizationModels,
    isOptimizing,
    setUserPrompt,
    setOptimizedPrompt,
    toggleUseOptimizedPrompt,
    selectPromptModel,
    setOptimizing,
    setError,
    clearError
  } = useImageStore();
  
  // 优化提示词
  const handleOptimize = async () => {
    if (!userPrompt.trim()) {
      setError('请先输入提示词');
      return;
    }
    
    clearError();
    setOptimizing(true);
    
    try {
      const result = await textToImageAPI.optimizePrompt(
        userPrompt,
        selectedPromptModel,
        'zh' // 生成中文提示词
      );
      
      setOptimizedPrompt(result.optimized_prompt);
      
      // 自动启用优化后的提示词
      if (!useOptimizedPrompt) {
        toggleUseOptimizedPrompt();
      }
      
    } catch (error) {
      console.error('优化提示词失败:', error);
      setError(error.message || '优化提示词失败');
    } finally {
      setOptimizing(false);
    }
  };
  
  // 获取当前显示的提示词
  const displayPrompt = useOptimizedPrompt && optimizedPrompt 
    ? optimizedPrompt 
    : userPrompt;
  
  return (
    <Card 
      title={
        <Space>
          <span>✍️ 提示词</span>
          <Tooltip title="描述你想要生成的图片内容，AI会帮你优化成专业的提示词">
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>
      }
      variant="borderless"
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 原始提示词输入 */}
        <div>
          <div style={{ marginBottom: 8 }}>
            <Space>
              <span style={{ fontWeight: 500 }}>输入你的想法</span>
              {userPrompt && (
                <Tag color="blue">{userPrompt.length} 字符</Tag>
              )}
            </Space>
          </div>
          <TextArea
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder="例如: 一只可爱的橘猫在阳光下打盹&#10;或: A fluffy orange cat napping in the sunlight"
            autoSize={{ minRows: 3, maxRows: 6 }}
            maxLength={500}
            showCount
          />
        </div>
        
        {/* 模型选择和优化按钮 */}
        <Space wrap>
          <Select
            value={selectedPromptModel}
            onChange={selectPromptModel}
            style={{ width: 200 }}
            disabled={isOptimizing}
          >
            {Object.entries(promptOptimizationModels).map(([key, model]) => (
              <Option key={key} value={key}>
                {model.name}
                {model.default && <Tag color="green" style={{ marginLeft: 8 }}>推荐</Tag>}
              </Option>
            ))}
          </Select>
          
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleOptimize}
            loading={isOptimizing}
            disabled={!userPrompt.trim()}
          >
            {isOptimizing ? '优化中...' : 'AI优化提示词'}
          </Button>
        </Space>
        
        {/* 优化后的提示词 */}
        {optimizedPrompt && (
          <div>
            <div style={{ marginBottom: 8 }}>
              <Space>
                <span style={{ fontWeight: 500 }}>优化后的提示词</span>
                <Tag color="success">已优化</Tag>
                <Tag color="blue">{optimizedPrompt.length} 字符</Tag>
                <Switch
                  checked={useOptimizedPrompt}
                  onChange={toggleUseOptimizedPrompt}
                  checkedChildren="使用"
                  unCheckedChildren="不使用"
                />
              </Space>
            </div>
            <TextArea
              value={optimizedPrompt}
              onChange={(e) => setOptimizedPrompt(e.target.value)}
              autoSize={{ minRows: 3, maxRows: 8 }}
              style={{
                backgroundColor: useOptimizedPrompt ? '#f6ffed' : undefined,
                borderColor: useOptimizedPrompt ? '#52c41a' : undefined
              }}
            />
          </div>
        )}
        
        {/* 当前使用的提示词提示 */}
        {optimizedPrompt && (
          <div style={{ 
            padding: '8px 12px', 
            backgroundColor: '#e6f7ff', 
            borderRadius: 4,
            fontSize: 12
          }}>
            <InfoCircleOutlined style={{ marginRight: 8, color: '#1890ff' }} />
            将使用
            <Tag color={useOptimizedPrompt ? 'success' : 'default'} style={{ margin: '0 4px' }}>
              {useOptimizedPrompt ? '优化后' : '原始'}
            </Tag>
            提示词生成图片
          </div>
        )}
      </Space>
    </Card>
  );
};

export default PromptInput;

