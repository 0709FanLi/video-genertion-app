/**
 * 扩展参数设置组件
 * 长宽比等参数设置
 */

import React from 'react';
import { Card, Space, Radio, Tag } from 'antd';
import { HighlightOutlined, BorderOutlined } from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';

const ExtensionParams = () => {
  const {
    aspectRatio,
    setAspectRatio,
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
      </Space>
    </Card>
  );
};

export default ExtensionParams;

