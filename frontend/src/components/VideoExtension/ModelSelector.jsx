/**
 * 视频扩展模型选择组件（包含参数设置）
 */

import React from 'react';
import { Card, Select, Space, Tag, Tooltip, Divider, Radio } from 'antd';
import { 
  InfoCircleOutlined,
  CheckCircleOutlined,
  BorderOutlined,
  ThunderboltOutlined,
  VideoCameraOutlined
} from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';

const { Option } = Select;

const ModelSelector = () => {
  const {
    selectedModel,
    videoExtensionModels,
    isExtending,
    selectExtensionModel,
    aspectRatio,
    duration,
    resolution,
    setAspectRatio,
    setDuration,
    setResolution
  } = useVideoExtensionStore();
  
  // 获取当前模型信息
  const currentModel = videoExtensionModels[selectedModel] || {};
  
  return (
    <Card 
      title={
        <Space>
          <span>🎯 选择扩展模型</span>
          <Tooltip title="选择用于扩展视频的AI模型">
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>
      }
      variant="borderless"
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 模型选择 */}
        <Select
          value={selectedModel}
          onChange={selectExtensionModel}
          style={{ width: '100%' }}
          size="large"
          disabled={isExtending}
        >
          {Object.entries(videoExtensionModels).map(([key, model]) => (
            <Option key={key} value={key}>
              <Space>
                <span>{model.name}</span>
                {model.default && <Tag color="green">推荐</Tag>}
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
              {currentModel.description && (
                <div style={{ color: '#666', fontSize: 12, marginTop: 4 }}>
                  {currentModel.description}
                </div>
              )}
            </Space>
          </div>
        )}
        
        {/* 参数设置区域 */}
        <Divider style={{ margin: '16px 0' }} />
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 长宽比选择 */}
          <div>
            <div style={{ marginBottom: '12px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BorderOutlined />
              <span>视频长宽比</span>
              <Tag color="blue">{aspectRatio}</Tag>
            </div>
            <Radio.Group
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value)}
              disabled={isExtending}
              buttonStyle="solid"
            >
              <Radio.Button value="16:9">
                <Space>
                  <span>16:9</span>
                  <span style={{ fontSize: '20px' }}>▭</span>
                </Space>
              </Radio.Button>
              <Radio.Button value="9:16">
                <Space>
                  <span>9:16</span>
                  <span style={{ fontSize: '20px' }}>▯</span>
                </Space>
              </Radio.Button>
            </Radio.Group>
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              💡 提示：选择扩展后视频的输出长宽比
            </div>
          </div>
          
          {/* 分辨率选择 */}
          <div>
            <div style={{ marginBottom: '12px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ThunderboltOutlined />
              <span>视频分辨率</span>
              <Tag color="green">{resolution}</Tag>
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
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              💡 提示：选择扩展后视频的输出分辨率
            </div>
          </div>
          
          {/* 时长选择 */}
          <div>
            <div style={{ marginBottom: '12px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <VideoCameraOutlined />
              <span>视频时长</span>
              <Tag color="orange">{duration}秒</Tag>
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
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              💡 提示：选择扩展后视频的输出时长
            </div>
          </div>
        </Space>
      </Space>
    </Card>
  );
};

export default ModelSelector;

