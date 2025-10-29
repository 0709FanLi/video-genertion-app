/**
 * 视频参数设置组件
 * 长宽比、时长、分辨率设置
 */

import React from 'react';
import { Card, Slider, Select, Space, Tag } from 'antd';
import {
  ClockCircleOutlined,
  HighlightOutlined,
  BorderOutlined
} from '@ant-design/icons';
import useVideoStore from '../../store/videoStore';

const VideoParams = () => {
  const {
    duration,
    setDuration,
    resolution,
    setResolution,
    aspectRatio,
    setAspectRatio,
    selectedModel
  } = useVideoStore();
  
  // 判断模型类型
  const isVolcengine = selectedModel.startsWith('volc-');
  const isWanxiang = selectedModel.startsWith('wanx');
  const isGoogleVeo = selectedModel.startsWith('google-veo');
  const isTextToVideo = selectedModel === 'volc-t2v';
  const isVolcImageToVideo = selectedModel === 'volc-i2v-first' || selectedModel === 'volc-i2v-first-tail';
  
  // 长宽比配置（文生视频和Google Veo使用）
  const aspectRatioOptions = isGoogleVeo
    ? [
        // Google Veo仅支持16:9和9:16
        { value: '16:9', label: '16:9', icon: '▭' },
        { value: '9:16', label: '9:16', icon: '▯' }
      ]
    : [
        // 火山引擎文生视频支持更多比例
        { value: '16:9', label: '16:9', icon: '▭' },
        { value: '4:3', label: '4:3', icon: '▬' },
        { value: '1:1', label: '1:1', icon: '◻' },
        { value: '3:4', label: '3:4', icon: '▯' },
        { value: '9:16', label: '9:16', icon: '▯' },
        { value: '21:9', label: '21:9', icon: '▬' }
      ];
  
  // 时长配置（Google Veo支持4/6/8秒）
  const durationMarks = isGoogleVeo
    ? { 4: '4秒', 6: '6秒', 8: '8秒' }
    : { 5: '5秒', 10: '10秒' };
  
  const durationRange = isGoogleVeo
    ? { min: 4, max: 8, step: 2 }
    : { min: 5, max: 10, step: 5 };
  
  // 时长是否可用
  const isDurationEnabled = isVolcengine || isGoogleVeo;
  const durationHint = !isDurationEnabled
    ? '📌 当前模型固定生成 5 秒时长视频'
    : isGoogleVeo
      ? resolution === '1080P'
        ? '📌 当前选择1080p分辨率，时长固定为8秒'
        : '💡 提示：Google Veo支持4/6/8秒时长，选择1080p时仅支持8秒'
      : '💡 提示：较长时长可以展现更丰富的动态变化，但生成时间也会更长';
  
  // 分辨率配置（根据模型）
  const getResolutionConfig = () => {
    if (isGoogleVeo) {
      // Google Veo支持720p和1080p
      return {
        options: [
          { value: '720P', label: '720P', desc: '约92万像素（支持4/6/8秒）' },
          { value: '1080P', label: '1080P', desc: '约207万像素（仅限8秒）' }
        ],
        enabled: true,
        hint: resolution === '1080P' && duration !== 8
          ? '⚠️ 注意：1080p分辨率仅支持8秒时长，已自动调整'
          : '💡 提示：选择1080p时，时长将自动调整为8秒'
      };
    } else if (selectedModel === 'wanx-kf2v-flash') {
      return {
        options: [
          { value: '480P', label: '480P', desc: '约31万像素' },
          { value: '720P', label: '720P', desc: '约92万像素' },
          { value: '1080P', label: '1080P', desc: '约207万像素' }
        ],
        enabled: true,
        hint: '💡 提示：分辨率会根据输入图片的宽高比自动调整'
      };
    } else if (selectedModel === 'wanx2.1-kf2v-plus') {
      return {
        options: [{ value: '720P', label: '720P', desc: '约92万像素' }],
        enabled: false,
        hint: '📌 当前模型固定使用 720P 分辨率'
      };
    } else {
      // 火山引擎固定1080P
      return {
        options: [{ value: '1080P', label: '1080P', desc: '约207万像素' }],
        enabled: false,
        hint: '📌 当前模型固定使用 1080P 分辨率'
      };
    }
  };
  
  const resolutionConfig = getResolutionConfig();
  
  // 自动调整分辨率（当模型切换时）
  React.useEffect(() => {
    const currentResolutionAvailable = resolutionConfig.options.some(
      (opt) => opt.value === resolution
    );
    if (!currentResolutionAvailable && resolutionConfig.options.length > 0) {
      setResolution(resolutionConfig.options[0].value);
    }
  }, [selectedModel, resolution, resolutionConfig.options, setResolution]);
  
  // 自动调整时长
  React.useEffect(() => {
    if (isWanxiang && duration !== 5) {
      // 通义万相固定5秒
      setDuration(5);
    } else if (isGoogleVeo && ![4, 6, 8].includes(duration)) {
      // Google Veo支持4/6/8秒，默认6秒
      setDuration(6);
    }
  }, [selectedModel, duration, isWanxiang, isGoogleVeo, setDuration]);
  
  // 自动调整长宽比（Google Veo切换时）
  React.useEffect(() => {
    if (isGoogleVeo && !['16:9', '9:16'].includes(aspectRatio)) {
      setAspectRatio('16:9');
    }
  }, [selectedModel, aspectRatio, isGoogleVeo, setAspectRatio]);
  
  // Google Veo 分辨率和时长约束：1080p只支持8秒
  React.useEffect(() => {
    if (isGoogleVeo && resolution === '1080P' && duration !== 8) {
      // 如果选择了1080P但时长不是8秒，自动调整为8秒
      setDuration(8);
    }
  }, [isGoogleVeo, resolution, duration, setDuration]);
  
  return (
    <Card
      title="视频参数设置"
      variant="borderless"
      styles={{ body: { padding: '16px' } }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 长宽比设置（文生视频和Google Veo显示） */}
        {(isTextToVideo || isGoogleVeo) && (
          <div>
            <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BorderOutlined />
              <span style={{ fontWeight: 500 }}>选择比例</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '8px' }}>
              {aspectRatioOptions.map((option) => (
                <div
                  key={option.value}
                  onClick={() => setAspectRatio(option.value)}
                  style={{
                    padding: '12px 8px',
                    border: aspectRatio === option.value ? '2px solid #1890ff' : '1px solid #d9d9d9',
                    borderRadius: '8px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    background: aspectRatio === option.value ? '#e6f7ff' : '#fff',
                    transition: 'all 0.2s',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  <span style={{ fontSize: '18px' }}>{option.icon}</span>
                  <span style={{
                    fontSize: '12px',
                    fontWeight: aspectRatio === option.value ? 500 : 400,
                    color: aspectRatio === option.value ? '#1890ff' : '#666'
                  }}>
                    {option.label}
                  </span>
                </div>
              ))}
            </div>
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              💡 提示：选择视频的长宽比，模型会根据比例生成对应分辨率的视频
            </div>
          </div>
        )}
        
        {/* 时长设置 */}
        <div>
          <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ClockCircleOutlined />
            <span style={{ fontWeight: 500 }}>视频时长</span>
            <Tag color="blue">{duration}秒</Tag>
          </div>
          <Slider
            value={duration}
            onChange={setDuration}
            marks={durationMarks}
            step={durationRange.step}
            min={durationRange.min}
            max={durationRange.max}
            tooltip={{ formatter: (value) => `${value}秒` }}
            disabled={!isDurationEnabled || (isGoogleVeo && resolution === '1080P')}
          />
          <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
            {durationHint}
          </div>
        </div>
        
        {/* 分辨率设置 */}
        <div>
          <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HighlightOutlined />
            <span style={{ fontWeight: 500 }}>视频分辨率</span>
          </div>
          <Select
            value={resolution}
            onChange={setResolution}
            style={{ width: '100%' }}
            size="large"
            disabled={!resolutionConfig.enabled}
          >
            {resolutionConfig.options.map((opt) => (
              <Select.Option value={opt.value} key={opt.value}>
                <Space>
                  <span>{opt.label}</span>
                  <span style={{ color: '#999', fontSize: '12px' }}>
                    {opt.desc}
                  </span>
                </Space>
              </Select.Option>
            ))}
          </Select>
          <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
            {resolutionConfig.hint}
          </div>
        </div>
      </Space>
    </Card>
  );
};

export default VideoParams;
