/**
 * 图片上传组件
 * 支持首帧和尾帧上传、预览、删除
 */

import React, { useState } from 'react';
import { Upload, Card, Button, Image, message, Space } from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  CloudUploadOutlined,
  FolderOutlined
} from '@ant-design/icons';
import useVideoStore from '../../store/videoStore';
import { fileUploadAPI, API_BASE_URL } from '../../services/api';
import UserLibraryModal from '../UserLibraryModal';

const ImageUpload = () => {
  const {
    firstFrame,
    lastFrame,
    setFirstFrame,
    setLastFrame,
    selectedModel
  } = useVideoStore();
  
  // 资源库弹窗状态
  const [libraryModalOpen, setLibraryModalOpen] = useState(false);
  const [selectingFrame, setSelectingFrame] = useState(null); // 'first' or 'last'
  
  // 是否需要图片（文生视频模型不需要）
  const isTextToVideo = selectedModel === 'volc-t2v' || 
                        selectedModel === 'google-veo-t2v' || 
                        selectedModel.startsWith('sora-v2');
  
  // 是否需要尾帧（根据模型判断）
  const needLastFrame = selectedModel.includes('tail') || selectedModel.includes('wanx');
  
  // 如果是文生视频模型，不显示上传区域
  if (isTextToVideo) {
    return (
      <Card
        title="文生视频模式"
        variant="borderless"
        styles={{ body: { padding: '16px' } }}
      >
        <div style={{ 
          padding: '40px 20px',
          textAlign: 'center',
          background: '#f0f2f5',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎬</div>
          <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
            纯文本生成视频
          </div>
          <div style={{ fontSize: '13px', color: '#666' }}>
            无需上传图片，直接输入提示词即可生成视频
          </div>
        </div>
      </Card>
    );
  }
  
  /**
   * 将File转换为Base64
   */
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };
  
  /**
   * 将图片URL转换为Base64（使用后端代理避免CORS问题）
   */
  const imageUrlToBase64 = async (url) => {
    try {
      // 使用后端代理下载接口
      const downloadUrl = `${API_BASE_URL}/api/files/download?url=${encodeURIComponent(url)}`;
      
      const response = await fetch(downloadUrl);
      if (!response.ok) {
        throw new Error('下载图片失败');
      }
      
      const blob = await response.blob();
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onload = () => resolve(reader.result);
        reader.onerror = (error) => reject(error);
      });
    } catch (error) {
      console.error('图片转换失败:', error);
      throw error;
    }
  };
  
  /**
   * 从资源库选择图片
   */
  const handleSelectFromLibrary = (frameType) => {
    setSelectingFrame(frameType);
    setLibraryModalOpen(true);
  };
  
  /**
   * 处理从资源库选择的图片
   */
  const handleLibraryImageSelect = async (image) => {
    try {
      message.loading({ content: '正在加载图片...', key: 'loading-library-image', duration: 0 });
      
      // 将图片URL转换为Base64
      const base64 = await imageUrlToBase64(image.image_url);
      
      message.destroy('loading-library-image');
      
      const frameData = {
        url: image.image_url,
        base64: base64,
        objectKey: null, // 资源库图片没有objectKey
        size: image.file_size || null
      };
      
      if (selectingFrame === 'first') {
        setFirstFrame(frameData);
        message.success('已选择首帧图片');
      } else if (selectingFrame === 'last') {
        setLastFrame(frameData);
        message.success('已选择尾帧图片');
      }
      
      setLibraryModalOpen(false);
      setSelectingFrame(null);
    } catch (error) {
      message.destroy('loading-library-image');
      console.error('加载图片失败:', error);
      message.error('加载图片失败，请重试');
    }
  };
  
  /**
   * 处理上传前的验证
   */
  const beforeUpload = (file) => {
    console.log('[ImageUpload] beforeUpload called', file.name);
    
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件！');
      return Upload.LIST_IGNORE;
    }
    
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('图片大小不能超过10MB！');
      return Upload.LIST_IGNORE;
    }
    
    console.log('[ImageUpload] Validation passed, proceeding to customRequest');
    return true; // 允许继续，会触发customRequest
  };
  
  /**
   * 处理首帧上传
   */
  const handleFirstFrameUpload = async ({ file }) => {
    console.log('[ImageUpload] handleFirstFrameUpload called', file.name);
    const loadingKey = `uploading-first-frame`;
    
    try {
      message.loading({ content: `正在上传首帧图片...`, key: loadingKey, duration: 0 });
      console.log('[ImageUpload] Start uploading to OSS...');
      
      // 上传到OSS
      const result = await fileUploadAPI.uploadReferenceImage(file);
      console.log('[ImageUpload] OSS upload result:', result);
      
      // 同时生成Base64（用于预览和某些API调用）
      const base64 = await fileToBase64(file);
      console.log('[ImageUpload] Base64 generated, length:', base64.length);
      
      message.destroy(loadingKey);
      
      const frameData = {
        file,
        url: result.url, // OSS URL
        base64,
        objectKey: result.object_key,
        size: result.size
      };
      
      console.log('[ImageUpload] Setting first frame:', frameData);
      setFirstFrame(frameData);
      
      message.success('首帧图片上传成功');
    } catch (error) {
      message.destroy(loadingKey);
      console.error('[ImageUpload] 首帧上传失败:', error);
      message.error(`首帧上传失败: ${error.message || '未知错误'}`);
    }
  };
  
  /**
   * 处理尾帧上传
   */
  const handleLastFrameUpload = async ({ file }) => {
    const loadingKey = `uploading-last-frame`;
    
    try {
      message.loading({ content: `正在上传尾帧图片...`, key: loadingKey, duration: 0 });
      
      // 上传到OSS
      const result = await fileUploadAPI.uploadReferenceImage(file);
      
      // 同时生成Base64（用于预览和某些API调用）
      const base64 = await fileToBase64(file);
      
      message.destroy(loadingKey);
      
      setLastFrame({
        file,
        url: result.url, // OSS URL
        base64,
        objectKey: result.object_key,
        size: result.size
      });
      
      message.success('尾帧图片上传成功');
    } catch (error) {
      message.destroy(loadingKey);
      console.error('尾帧上传失败:', error);
      message.error(`尾帧上传失败: ${error.message || '未知错误'}`);
    }
  };
  
  /**
   * 删除首帧
   */
  const handleDeleteFirstFrame = () => {
    setFirstFrame(null);
    message.info('已删除首帧图片');
  };
  
  /**
   * 删除尾帧
   */
  const handleDeleteLastFrame = () => {
    setLastFrame(null);
    message.info('已删除尾帧图片');
  };
  
  /**
   * 渲染上传区域
   */
  const renderUploadArea = (frame, onUpload, onDelete, title, description, frameType) => (
    <Card
      title={title}
      variant="borderless"
      styles={{ body: { padding: '16px' } }}
      extra={
        frame ? (
          <Space>
            <Button
              type="text"
              size="small"
              icon={<FolderOutlined />}
              onClick={() => handleSelectFromLibrary(frameType)}
            >
              更换
            </Button>
            <Button
              type="text"
              danger
              size="small"
              icon={<DeleteOutlined />}
              onClick={onDelete}
            >
              删除
            </Button>
          </Space>
        ) : (
          <Button
            type="text"
            size="small"
            icon={<FolderOutlined />}
            onClick={() => handleSelectFromLibrary(frameType)}
          >
            从资源库选择
          </Button>
        )
      }
    >
      {frame ? (
        // 显示预览
        <div style={{ textAlign: 'center' }}>
          <Image
            src={frame.url}
            alt={title}
            style={{
              maxWidth: '100%',
              maxHeight: '300px',
              objectFit: 'contain'
            }}
            preview={{
              mask: '查看大图'
            }}
          />
          {frame.file && (
            <div style={{ marginTop: '8px', color: '#666', fontSize: '12px' }}>
              {frame.file.name} ({(frame.file.size / 1024).toFixed(1)} KB)
            </div>
          )}
        </div>
      ) : (
        // 显示上传区域
        <Upload.Dragger
          name="file"
          multiple={false}
          beforeUpload={beforeUpload}
          customRequest={onUpload}
          showUploadList={false}
          style={{ padding: '20px' }}
        >
          <p className="ant-upload-drag-icon">
            <CloudUploadOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
          </p>
          <p className="ant-upload-text">{description}</p>
          <p className="ant-upload-hint" style={{ fontSize: '12px', color: '#999' }}>
            支持JPEG、PNG、BMP、WEBP格式，最大10MB
          </p>
        </Upload.Dragger>
      )}
    </Card>
  );
  
  return (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: needLastFrame ? '1fr 1fr' : '1fr', gap: '16px' }}>
        {/* 首帧上传 */}
        {renderUploadArea(
          firstFrame,
          handleFirstFrameUpload,
          handleDeleteFirstFrame,
          '首帧图片',
          '点击或拖拽上传首帧图片',
          'first'
        )}
        
        {/* 尾帧上传（可选） */}
        {needLastFrame && renderUploadArea(
          lastFrame,
          handleLastFrameUpload,
          handleDeleteLastFrame,
          '尾帧图片',
          '点击或拖拽上传尾帧图片',
          'last'
        )}
      </div>
      
      {/* 资源库弹窗 */}
      <UserLibraryModal
        open={libraryModalOpen}
        onClose={() => {
          setLibraryModalOpen(false);
          setSelectingFrame(null);
        }}
        onSelectImage={handleLibraryImageSelect}
      />
    </>
  );
};

export default ImageUpload;

