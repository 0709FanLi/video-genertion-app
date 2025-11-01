/**
 * 扩展参数设置组件
 * 长宽比等参数设置
 */

import React from 'react';
import { Card, Space, Radio, Select, Tag } from 'antd';
import { HighlightOutlined, BorderOutlined, VideoCameraOutlined, ThunderboltOutlined } from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';

const ExtensionParams = () => {
  const {
    aspectRatio,
    duration,
    resolution,
    setAspectRatio,
    setDuration,
    setResolution,
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
    </Card>
  );
};

export default ExtensionParams;

