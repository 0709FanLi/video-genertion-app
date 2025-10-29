/**
 * 视频上传组件
 * 支持本地视频上传到OSS
 */

import React, { useRef } from 'react';
import { Card, Upload, Button, Space, message, Progress } from 'antd';
import { UploadOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';
import { fileUploadAPI } from '../../services/api';

const VideoUpload = () => {
  const {
    originalVideo,
    setOriginalVideo,
    clearOriginalVideo,
    uploadProgress,
    setUploadProgress,
    isExtending
  } = useVideoExtensionStore();
  
  const videoRef = useRef(null);
  
  /**
   * 处理文件选择
   */
  const handleFileSelect = async (file) => {
    console.log('[VideoUpload] handleFileSelect called:', file.name);
    
    try {
      setUploadProgress(0);
      message.loading({ content: '正在上传视频...', key: 'upload' });
      
      console.log('[VideoUpload] Creating preview URL...');
      // 先创建本地预览URL
      const previewUrl = URL.createObjectURL(file);
      console.log('[VideoUpload] Preview URL created:', previewUrl);
      
      console.log('[VideoUpload] Getting video duration...');
      // 获取视频时长
      const duration = await getVideoDuration(file);
      console.log('[VideoUpload] Duration:', duration);
      
      console.log('[VideoUpload] Uploading to OSS...');
      // 上传到OSS
      const formData = new FormData();
      formData.append('file', file);
      
      const result = await fileUploadAPI.uploadVideo(formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          console.log('[VideoUpload] Upload progress:', percentCompleted + '%');
          setUploadProgress(percentCompleted);
        }
      });
      
      console.log('[VideoUpload] Upload result:', result);
      
      // 保存到store（使用OSS URL）
      const videoData = {
        url: result.url,  // OSS URL用于后端API
        previewUrl: previewUrl,  // 本地Blob URL用于前端预览
        file: file,
        name: file.name,
        size: file.size,
        duration: duration
      };
      
      console.log('[VideoUpload] Saving to store:', videoData);
      setOriginalVideo(videoData);
      
      message.success({ content: '视频上传成功！', key: 'upload' });
      setUploadProgress(100);
      
      console.log('[VideoUpload] Upload complete');
      
    } catch (error) {
      console.error('[VideoUpload] Upload failed:', error);
      message.error({ content: '视频上传失败', key: 'upload' });
      setUploadProgress(0);
    }
  };
  
  /**
   * 获取视频时长
   */
  const getVideoDuration = (file) => {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      video.preload = 'metadata';
      
      video.onloadedmetadata = () => {
        window.URL.revokeObjectURL(video.src);
        resolve(Math.round(video.duration));
      };
      
      video.onerror = () => {
        resolve(0);
      };
      
      video.src = URL.createObjectURL(file);
    });
  };
  
  /**
   * 处理删除视频
   */
  const handleRemove = () => {
    clearOriginalVideo();
    setUploadProgress(0);
    message.info('已清除原始视频');
  };
  
  return (
    <Card
      title="上传原始视频"
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
        {!originalVideo ? (
          <>
            <Upload
              accept="video/mp4,video/quicktime"
              beforeUpload={(file) => {
                console.log('[VideoUpload] beforeUpload called:', {
                  name: file.name,
                  type: file.type,
                  size: file.size
                });
                
                // 检查文件类型
                const isVideo = file.type.startsWith('video/');
                if (!isVideo) {
                  console.error('[VideoUpload] Not a video file:', file.type);
                  message.error('只能上传视频文件！');
                  return Upload.LIST_IGNORE;
                }
                
                // 检查文件格式
                const isMP4orMOV = file.type === 'video/mp4' || file.type === 'video/quicktime';
                if (!isMP4orMOV) {
                  console.error('[VideoUpload] Unsupported format:', file.type);
                  message.error('只支持MP4和MOV格式！');
                  return Upload.LIST_IGNORE;
                }
                
                console.log('[VideoUpload] File validation passed');
                
                // 直接处理文件
                handleFileSelect(file);
                
                // 阻止Upload组件的默认行为
                return false;
              }}
              showUploadList={false}
              disabled={isExtending}
            >
              <Button 
                type="primary" 
                icon={<UploadOutlined />} 
                size="large"
                disabled={isExtending}
                block
                onClick={() => console.log('[VideoUpload] Button clicked')}
              >
                点击上传视频 (MP4/MOV)
              </Button>
            </Upload>
            
            {uploadProgress > 0 && uploadProgress < 100 && (
              <Progress percent={uploadProgress} status="active" />
            )}
            
            <div style={{ fontSize: '12px', color: '#666', textAlign: 'center' }}>
              💡 提示：支持MP4和MOV格式，无大小限制
            </div>
          </>
        ) : (
          <div>
            {/* 视频预览 */}
            <video
              ref={videoRef}
              src={originalVideo.previewUrl || originalVideo.url}
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
                <div>📄 文件名: {originalVideo.name}</div>
                <div>📏 大小: {(originalVideo.size / 1024 / 1024).toFixed(2)} MB</div>
                <div>⏱️ 时长: {originalVideo.duration} 秒</div>
                <div>🔗 OSS URL: {originalVideo.url.substring(0, 60)}...</div>
              </Space>
            </div>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default VideoUpload;

