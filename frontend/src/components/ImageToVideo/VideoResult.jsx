/**
 * 视频结果展示组件
 * 显示生成的视频，支持预览和下载
 */

import React from 'react';
import { Card, Button, Space, Empty, Tag, message } from 'antd';
import {
  DownloadOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  ExpandOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import useVideoStore from '../../store/videoStore';
import useVideoExtensionStore from '../../store/videoExtensionStore';

const VideoResult = () => {
  const { videoResult, clearResult } = useVideoStore();
  const navigate = useNavigate();
  const { setOriginalVideo } = useVideoExtensionStore();
  
  /**
   * 下载视频
   */
  const handleDownload = () => {
    if (!videoResult || !videoResult.video_url) {
      message.error('视频URL无效');
      return;
    }
    
    // 直接创建下载链接（OSS视频无跨域限制）
    const link = document.createElement('a');
    link.href = videoResult.video_url;
    link.download = `video_${videoResult.task_id || Date.now()}.mp4`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    message.success('视频下载已开始');
  };
  
  /**
   * 视频延长
   * 跳转到视频扩展页面，并将当前视频作为原始视频
   */
  const handleExtendVideo = () => {
    if (!videoResult || !videoResult.video_url) {
      message.error('视频URL无效');
      return;
    }
    
    // 判断是否为 Google Veo 视频（Google Veo 视频延长仅支持延长由其生成的视频）
    const isGoogleVeo = videoResult.model && 
      videoResult.model.toLowerCase().includes('google-veo');
    
    // 设置视频信息到视频扩展 store
    setOriginalVideo({
      url: videoResult.video_url,
      name: videoResult.orig_prompt || videoResult.actual_prompt || '已生成的视频',
      model: videoResult.model || '',
      duration: videoResult.duration || 0,
      resolution: videoResult.resolution || '',
      is_google_veo: isGoogleVeo
    });
    
    // 跳转到视频扩展页面
    navigate('/video-extension');
    message.success('已跳转到视频延长页面');
  };
  
  /**
   * 重新生成
   */
  const handleRegenerate = () => {
    clearResult();
    message.info('已清空结果，可以重新生成');
  };
  
  if (!videoResult) {
    return (
      <Card
        title="生成结果"
        variant="borderless"
        styles={{ body: { padding: '24px' } }}
      >
        <Empty
          image={<PlayCircleOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />}
          description="暂无生成结果"
        >
          <p style={{ color: '#999', fontSize: '13px' }}>
            上传图片、输入提示词后，点击"生成视频"按钮开始生成
          </p>
        </Empty>
      </Card>
    );
  }
  
  return (
    <Card
      title={
        <Space>
          <span>生成结果</span>
          <Tag icon={<CheckCircleOutlined />} color="success">
            生成完成
          </Tag>
        </Space>
      }
          variant="borderless"
          styles={{ body: { padding: '16px' } }}
          extra={
            <Space>
              <Button
                type="primary"
                icon={<ExpandOutlined />}
                onClick={handleExtendVideo}
              >
                视频延长
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleDownload}
              >
                下载视频
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleRegenerate}
              >
                重新生成
              </Button>
            </Space>
          }
        >
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {/* 视频播放器 */}
            <div
              style={{
                width: '100%',
                background: '#000',
                borderRadius: '8px',
                overflow: 'hidden'
              }}
            >
              <video
                src={videoResult.video_url}
                controls
                playsInline
                style={{
                  width: '100%',
                  height: 'auto',
                  display: 'block'
                }}
                preload="metadata"
              >
                您的浏览器不支持视频播放
              </video>
            </div>
        
        {/* 视频信息 */}
        <div
          style={{
            padding: '12px',
            background: '#f0f2f5',
            borderRadius: '4px',
            fontSize: '13px'
          }}
        >
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div>
              <strong>模型：</strong>
              <Tag style={{ marginLeft: '8px' }}>{videoResult.model}</Tag>
            </div>
            
            <div>
              <strong>时长：</strong>
              <span style={{ marginLeft: '8px' }}>{videoResult.duration}秒</span>
            </div>
            
            {videoResult.task_id && (
              <div style={{ wordBreak: 'break-all' }}>
                <strong>任务ID：</strong>
                <span style={{ marginLeft: '8px', color: '#666' }}>
                  {videoResult.task_id}
                </span>
              </div>
            )}
            
            {videoResult.orig_prompt && (
              <div>
                <strong>原始提示词：</strong>
                <div
                  style={{
                    marginTop: '4px',
                    padding: '8px',
                    background: '#fff',
                    borderRadius: '4px',
                    color: '#666'
                  }}
                >
                  {videoResult.orig_prompt}
                </div>
              </div>
            )}
            
            {videoResult.actual_prompt && videoResult.actual_prompt !== videoResult.orig_prompt && (
              <div>
                <strong>优化后提示词：</strong>
                <div
                  style={{
                    marginTop: '4px',
                    padding: '8px',
                    background: '#fff',
                    borderRadius: '4px',
                    color: '#666'
                  }}
                >
                  {videoResult.actual_prompt}
                </div>
              </div>
            )}
          </Space>
        </div>
        
            {/* 提示信息 */}
            <div style={{ fontSize: '12px', color: '#999' }}>
              💡 提示：视频已保存到云端，可随时播放和下载
            </div>
      </Space>
    </Card>
  );
};

export default VideoResult;

