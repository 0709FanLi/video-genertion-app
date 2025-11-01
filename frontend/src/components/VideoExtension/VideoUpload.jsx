/**
 * 视频选择组件
 * 从视频库选择视频（不支持本地上传）
 */

import React, { useRef, useState } from 'react';
import { Card, Button, Space, message, Alert } from 'antd';
import { SelectOutlined, DeleteOutlined, InfoCircleOutlined } from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';
import UserLibraryModal from '../UserLibraryModal';

const VideoUpload = () => {
  const {
    originalVideo,
    setOriginalVideo,
    clearOriginalVideo,
    isExtending,
    selectedModel
  } = useVideoExtensionStore();
  
  const videoRef = useRef(null);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  
  // 判断是否需要Google Veo筛选
  const needsGoogleVeo = selectedModel && selectedModel.includes('google-veo');
  
  /**
   * 从资源库选择视频
   */
  const handleSelectFromLibrary = (video) => {
    // 检查Google Veo兼容性
    if (needsGoogleVeo && !video.is_google_veo) {
      message.warning('Google Veo 视频延长仅支持延长由其生成的视频，请选择带有 Google Veo 标记的视频');
      return;
    }
    
    // 保存到store
    const videoData = {
      url: video.video_url,
      name: video.prompt || '已保存的视频',
      model: video.model,
      duration: video.duration,
      resolution: video.resolution,
      is_google_veo: video.is_google_veo
    };
    
    setOriginalVideo(videoData);
    setIsLibraryOpen(false);
    message.success('已选择视频');
  };
  
  /**
   * 处理删除视频
   */
  const handleRemove = () => {
    clearOriginalVideo();
    message.info('已清除选择的视频');
  };
  
  return (
    <>
    <Card
      title="选择原始视频"
      variant="borderless"
      extra={
        originalVideo && (
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={handleRemove}
            disabled={isExtending}
          >
            清除
          </Button>
        )
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* Google Veo 提示 */}
        {needsGoogleVeo && (
          <Alert
            message="Google Veo 视频延长"
            description="Google Veo 仅支持延长由其生成的视频。请从视频库中选择带有 Google Veo 标记的视频。"
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
          />
        )}
        
        {!originalVideo ? (
          <>
            <Button 
              type="primary" 
              icon={<SelectOutlined />} 
              size="large"
              disabled={isExtending}
              block
              onClick={() => setIsLibraryOpen(true)}
            >
              从资源库选择
            </Button>
            
            <div style={{ fontSize: '12px', color: '#666', textAlign: 'center' }}>
              💡 提示：请从资源库中选择要延长的视频
              {needsGoogleVeo && <div style={{ color: '#1890ff', marginTop: 4 }}>
                ⚠️ 当前模型仅支持延长 Google Veo 生成的视频
              </div>}
            </div>
          </>
        ) : (
          <div>
            {/* 视频预览 */}
            <video
              ref={videoRef}
              src={originalVideo.url}
              controls
              style={{
                width: '100%',
                maxHeight: '400px',
                borderRadius: '8px',
                backgroundColor: '#000'
              }}
            />
            
            {/* 视频信息 */}
            <div style={{ marginTop: '12px', fontSize: '12px', color: '#666' }}>
              <Space direction="vertical" size="small">
                <div>📝 描述: {originalVideo.name}</div>
                {originalVideo.model && <div>🎬 模型: {originalVideo.model}</div>}
                {originalVideo.duration && <div>⏱️ 时长: {originalVideo.duration} 秒</div>}
                {originalVideo.resolution && <div>📺 分辨率: {originalVideo.resolution}</div>}
                {originalVideo.is_google_veo && (
                  <div style={{ color: '#1890ff', fontWeight: 'bold' }}>
                    ✅ Google Veo 视频
                  </div>
                )}
                <div>🔗 URL: {originalVideo.url.substring(0, 60)}...</div>
              </Space>
            </div>
          </div>
        )}
      </Space>
    </Card>
    
    {/* 资源库弹窗 */}
    <UserLibraryModal 
      open={isLibraryOpen}
      onClose={() => setIsLibraryOpen(false)}
      onSelectVideo={handleSelectFromLibrary}
      googleVeoOnlyMode={needsGoogleVeo}
    />
    </>
  );
};

export default VideoUpload;

