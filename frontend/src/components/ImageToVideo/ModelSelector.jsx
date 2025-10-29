/**
 * 模型选择组件
 * 支持多个视频生成模型的选择
 */

import React from 'react';
import { Card, Select, Tag, Space } from 'antd';
import { ThunderboltOutlined, RocketOutlined } from '@ant-design/icons';
import useVideoStore from '../../store/videoStore';

const ModelSelector = () => {
  const { selectedModel, setSelectedModel, lastFrame } = useVideoStore();
  
  // 模型配置
  const models = [
    {
      value: 'volc-t2v',
      label: '火山即梦 - 文生视频',
      description: '纯文本生成视频，无需图片，1080P高清，5s/10s',
      icon: <RocketOutlined />,
      tags: ['纯文本', '高性价比'],
      needLastFrame: false,
      needFirstFrame: false
    },
    {
      value: 'volc-i2v-first',
      label: '火山即梦 - 单图首帧',
      description: '图生视频（首帧模式），1080P高清，5s/10s',
      icon: <RocketOutlined />,
      tags: ['推荐', '单图'],
      needLastFrame: false,
      needFirstFrame: true,
      default: true
    },
    {
      value: 'volc-i2v-first-tail',
      label: '火山即梦 - 首尾帧',
      description: '图生视频（首尾帧插值），1080P高清，5s/10s',
      icon: <RocketOutlined />,
      tags: ['首尾帧'],
      needLastFrame: true,
      needFirstFrame: true
    },
    {
      value: 'wanx-kf2v-flash',
      label: '通义万相 - 极速版',
      description: '万相2.2极速版，480P/720P/1080P，5s',
      icon: <ThunderboltOutlined />,
      tags: ['极速', '首尾帧'],
      needLastFrame: false, // 可选尾帧
      needFirstFrame: true
    },
    {
      value: 'wanx-kf2v-plus',
      label: '通义万相 - 专业版',
      description: '万相2.1专业版，复杂运动，720P，5s',
      icon: <ThunderboltOutlined />,
      tags: ['专业', '首尾帧'],
      needLastFrame: false, // 可选尾帧
      needFirstFrame: true
    }
  ];
  
  /**
   * 处理模型切换
   */
  const handleModelChange = (value) => {
    setSelectedModel(value);
  };
  
  /**
   * 渲染模型选项
   */
  const renderModelOption = (model) => (
    <Select.Option value={model.value} key={model.value}>
      <Space>
        {model.icon}
        <span>{model.label}</span>
        {model.tags.map((tag, index) => (
          <Tag 
            key={index} 
            color={tag === '推荐' ? 'gold' : tag === '单图' ? 'blue' : 'green'}
            style={{ marginLeft: '4px' }}
          >
            {tag}
          </Tag>
        ))}
      </Space>
    </Select.Option>
  );
  
  // 获取当前选中模型的详细信息
  const currentModel = models.find((m) => m.value === selectedModel);
  
  return (
    <Card
      title="视频生成模型"
      variant="borderless"
      styles={{ body: { padding: '16px' } }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Select
          value={selectedModel}
          onChange={handleModelChange}
          style={{ width: '100%' }}
          size="large"
        >
          {models.map(renderModelOption)}
        </Select>
        
        {/* 模型说明 */}
        {currentModel && (
          <div
            style={{
              padding: '12px',
              background: '#f0f2f5',
              borderRadius: '4px',
              fontSize: '13px'
            }}
          >
            <div style={{ marginBottom: '8px', color: '#666' }}>
              <strong>模型说明：</strong>
            </div>
            <div style={{ color: '#666' }}>
              {currentModel.description}
            </div>
            
            {currentModel.needLastFrame && !lastFrame && (
              <div style={{ marginTop: '8px', color: '#ff4d4f' }}>
                ⚠️ 此模型需要上传尾帧图片
              </div>
            )}
            
            {!currentModel.needLastFrame && lastFrame && (
              <div style={{ marginTop: '8px', color: '#52c41a' }}>
                ✅ 已上传尾帧，将使用首尾帧插值模式
              </div>
            )}
          </div>
        )}
      </Space>
    </Card>
  );
};

export default ModelSelector;

