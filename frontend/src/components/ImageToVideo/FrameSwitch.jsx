/**
 * 首尾帧交换按钮组件
 * 用于快速交换首尾帧图片
 */

import React from 'react';
import { Button, Tooltip } from 'antd';
import { SwapOutlined } from '@ant-design/icons';
import useVideoStore from '../../store/videoStore';

const FrameSwitch = () => {
  const { firstFrame, lastFrame, swapFrames, selectedModel } = useVideoStore();
  
  // 是否显示交换按钮（只有首尾帧模式且两张图片都存在时才显示）
  const needLastFrame = selectedModel.includes('tail') || selectedModel.includes('wanx');
  const canSwap = needLastFrame && firstFrame && lastFrame;
  
  if (!canSwap) {
    return null;
  }
  
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      margin: '16px 0'
    }}>
      <Tooltip title="交换首尾帧，改变视频演变方向">
        <Button
          type="primary"
          icon={<SwapOutlined />}
          onClick={swapFrames}
          style={{
            borderRadius: '50%',
            width: '48px',
            height: '48px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        />
      </Tooltip>
    </div>
  );
};

export default FrameSwitch;

