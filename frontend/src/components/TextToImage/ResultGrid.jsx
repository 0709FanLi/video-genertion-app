/**
 * 生成结果展示组件
 */

import React from 'react';
import { Card, Image, Button, Space, Tag, Tooltip, Empty, message, Modal } from 'antd';
import { 
  DownloadOutlined, 
  DeleteOutlined,
  CheckCircleOutlined,
  VideoCameraOutlined,
  InfoCircleOutlined 
} from '@ant-design/icons';
import useImageStore from '../../store/imageStore';
import useVideoStore from '../../store/videoStore';
import { useNavigate } from 'react-router-dom';

const ResultGrid = () => {
  const navigate = useNavigate();
  
  const {
    generatedImages,
    selectedImageId,
    selectImage,
    deleteGeneratedImage,
    clearGeneratedImages
  } = useImageStore();
  
  const { setFirstFrame } = useVideoStore();
  
  // 下载图片
  const handleDownload = async (imageUrl, index) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `generated-image-${index + 1}-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      message.success('图片下载成功');
    } catch (error) {
      console.error('下载图片失败:', error);
      message.error('下载图片失败');
    }
  };
  
  // 删除图片
  const handleDelete = (imageId, index) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除第 ${index + 1} 张图片吗？`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk() {
        deleteGeneratedImage(imageId);
        message.info('已删除图片');
      }
    });
  };
  
  // 清空所有
  const handleClearAll = () => {
    Modal.confirm({
      title: '确认清空',
      content: `确定要清空所有 ${generatedImages.length} 张图片吗？此操作不可恢复。`,
      okText: '清空',
      okType: 'danger',
      cancelText: '取消',
      onOk() {
        clearGeneratedImages();
        message.info('已清空所有图片');
      }
    });
  };
  
  // 将图片URL转换为Base64（使用后端代理避免CORS问题）
  const imageUrlToBase64 = async (url) => {
    try {
      // 使用后端代理下载接口
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const downloadUrl = `${apiBaseUrl}/api/files/download?url=${encodeURIComponent(url)}`;
      
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
  
  // 选择图片并跳转到图生视频
  const handleSelectForVideo = async (imageId) => {
    try {
      selectImage(imageId);
      const image = generatedImages.find(img => img.id === imageId);
      
      if (!image) {
        message.error('图片不存在');
        return;
      }
      
      message.loading({ content: '正在加载图片...', key: 'loading-image', duration: 0 });
      
      // 将图片URL转换为Base64
      const base64 = await imageUrlToBase64(image.url);
      
      message.destroy('loading-image');
      
      // 设置到图生视频的首帧
      setFirstFrame({
        url: image.url,
        base64: base64,
        objectKey: null, // 资源库图片没有objectKey
        size: null // 资源库图片没有size信息
      });
      
      message.success('已选择图片，正在跳转到图生视频页面...');
      setTimeout(() => {
        navigate('/image-to-video');
      }, 500);
    } catch (error) {
      message.destroy('loading-image');
      console.error('处理图片失败:', error);
      message.error('处理图片失败，请重试');
    }
  };
  
  // 格式化时间
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  return (
    <Card
      title={
        <Space>
          <span>🖼️ 生成结果</span>
          {generatedImages.length > 0 && (
            <Tag color="blue">{generatedImages.length} 张</Tag>
          )}
          <Tooltip title="生成的图片会保存在这里">
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>
      }
      extra={
        generatedImages.length > 0 && (
          <Button 
            type="link" 
            size="small" 
            danger 
            onClick={handleClearAll}
          >
            清空全部
          </Button>
        )
      }
      variant="borderless"
    >
      {generatedImages.length === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <Space direction="vertical" align="center">
              <span style={{ color: '#8c8c8c' }}>暂无生成的图片</span>
              <span style={{ fontSize: 12, color: '#bfbfbf' }}>
                输入提示词并点击生成按钮开始创作
              </span>
            </Space>
          }
          style={{ padding: '40px 0' }}
        />
      ) : (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
          gap: 16
        }}>
          {generatedImages.map((image, index) => (
            <div
              key={image.id}
              style={{
                position: 'relative',
                borderRadius: 8,
                overflow: 'hidden',
                border: selectedImageId === image.id ? '3px solid #1890ff' : '1px solid #d9d9d9',
                boxShadow: selectedImageId === image.id 
                  ? '0 4px 12px rgba(24, 144, 255, 0.3)'
                  : '0 2px 8px rgba(0,0,0,0.1)',
                transition: 'all 0.3s',
                cursor: 'pointer'
              }}
              onClick={() => selectImage(image.id)}
            >
              {/* 图片 */}
              <Image
                src={image.url}
                alt={`生成图片 ${index + 1}`}
                style={{ 
                  width: '100%', 
                  height: 240, 
                  objectFit: 'cover' 
                }}
                preview={{
                  mask: (
                    <Space direction="vertical" align="center">
                      <div>预览</div>
                      <div style={{ fontSize: 12 }}>点击查看大图</div>
                    </Space>
                  )
                }}
              />
              
              {/* 选中标记 */}
              {selectedImageId === image.id && (
                <div style={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  backgroundColor: '#1890ff',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: 4,
                  fontSize: 12,
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}>
                  <CheckCircleOutlined />
                  已选中
                </div>
              )}
              
              {/* 信息栏 */}
              <div style={{
                padding: 12,
                backgroundColor: 'white',
                borderTop: '1px solid #f0f0f0'
              }}>
                {/* 模型和时间 */}
                <Space direction="vertical" size={4} style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Tag color="green" style={{ margin: 0 }}>
                      {image.model || '未知模型'}
                    </Tag>
                    <span style={{ fontSize: 11, color: '#8c8c8c' }}>
                      {formatTime(image.timestamp)}
                    </span>
                  </div>
                  
                  {/* 提示词 */}
                  {image.prompt && (
                    <Tooltip title={image.prompt}>
                      <div style={{
                        fontSize: 12,
                        color: '#595959',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {image.prompt}
                      </div>
                    </Tooltip>
                  )}
                </Space>
                
                {/* 操作按钮 */}
                <Space style={{ marginTop: 12, width: '100%', justifyContent: 'space-between' }}>
                  <Space size={4}>
                    <Tooltip title="下载图片">
                      <Button
                        type="text"
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownload(image.url, index);
                        }}
                      />
                    </Tooltip>
                    
                    <Tooltip title="删除图片">
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(image.id, index);
                        }}
                      />
                    </Tooltip>
                  </Space>
                  
                  <Tooltip title="用这张图片生成视频">
                    <Button
                      type="primary"
                      size="small"
                      icon={<VideoCameraOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectForVideo(image.id);
                      }}
                    >
                      生成视频
                    </Button>
                  </Tooltip>
                </Space>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

export default ResultGrid;

