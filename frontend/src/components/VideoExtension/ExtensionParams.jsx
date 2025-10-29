/**
 * 扩展参数设置组件
 * 长宽比、反向提示词等
 */

import React from 'react';
import { Card, Space, Radio, Input, Tooltip, Tag } from 'antd';
import { InfoCircleOutlined, HighlightOutlined, BorderOutlined } from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';

const { TextArea } = Input;

const ExtensionParams = () => {
  const {
    aspectRatio,
    negativePrompt,
    setAspectRatio,
    setNegativePrompt,
    isExtending
  } = useVideoExtensionStore();
  
  return (
    <Card
      title={
        <Space>
          <HighlightOutlined />
          <span>扩展参数设置</span>
        </Space>
      }
      variant="borderless"
    >
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
        
        {/* 固定参数提示 */}
        <div style={{ 
          padding: '12px', 
          background: '#f0f5ff', 
          border: '1px solid #adc6ff',
          borderRadius: '8px'
        }}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ fontWeight: 500, color: '#1890ff' }}>
              📌 固定参数说明
            </div>
            <div style={{ fontSize: '12px', color: '#595959' }}>
              <Space direction="vertical" size="small">
                <div>• 分辨率: 固定 <Tag>720P</Tag></div>
                <div>• 时长: 固定 <Tag>8秒</Tag></div>
                <div>• 输出数量: <Tag>1个</Tag></div>
              </Space>
            </div>
          </Space>
        </div>
        
        {/* 反向提示词（可选） */}
        <div>
          <div style={{ marginBottom: '8px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>反向提示词</span>
            <Tag color="default">可选</Tag>
            <Tooltip title="描述不希望在视频中看到的内容">
              <InfoCircleOutlined style={{ color: '#1890ff', cursor: 'pointer' }} />
            </Tooltip>
          </div>
          <TextArea
            value={negativePrompt}
            onChange={(e) => setNegativePrompt(e.target.value)}
            placeholder="描述不希望出现的内容（可选）&#10;例如：cartoon, drawing, low quality, blurry"
            rows={3}
            maxLength={500}
            showCount
            disabled={isExtending}
          />
          <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
            💡 提示：可以用来避免生成卡通风格、低质量等不想要的效果
          </div>
        </div>
      </Space>
    </Card>
  );
};

export default ExtensionParams;

