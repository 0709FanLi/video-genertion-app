/**
 * 参考图上传组件
 */

import React from 'react';
import { Card, Upload, Space, Image, Button, Tag, Tooltip, message } from 'antd';
import { 
  PlusOutlined, 
  DeleteOutlined,
  InfoCircleOutlined,
  WarningOutlined 
} from '@ant-design/icons';
import useImageStore from '../../store/imageStore';
import { fileUploadAPI } from '../../services/api';

const ReferenceUpload = () => {
  const {
    referenceImages,
    selectedImageModel,
    textToImageModels,
    isGenerating,
    addReferenceImage,
    removeReferenceImage,
    clearReferenceImages
  } = useImageStore();
  
  // 获取当前模型信息
  const currentModel = textToImageModels[selectedImageModel] || {};
  const supportsReference = currentModel.supports_reference || false;
  const maxReferenceImages = currentModel.max_reference_images || 0;
  
  // 不支持参考图的情况
  if (!supportsReference) {
    return (
      <Card 
        title={
          <Space>
            <span>📷 参考图 (可选)</span>
            <Tooltip title="上传参考图片,AI会参考其风格和内容生成新图">
              <InfoCircleOutlined style={{ color: '#1890ff' }} />
            </Tooltip>
          </Space>
        }
        variant="borderless"
      >
        <div style={{ 
          padding: '20px', 
          textAlign: 'center', 
          backgroundColor: '#fff7e6',
          borderRadius: 8,
          border: '1px dashed #ffa940'
        }}>
          <WarningOutlined style={{ fontSize: 32, color: '#fa8c16', marginBottom: 12 }} />
          <div style={{ fontSize: 14, color: '#d46b08' }}>
            当前模型 <Tag color="orange">{currentModel.name}</Tag> 不支持参考图功能
          </div>
          <div style={{ fontSize: 12, color: '#8c8c8c', marginTop: 8 }}>
            请选择 "通义万相多图生图" 模型以使用参考图功能
          </div>
        </div>
      </Card>
    );
  }
  
  // 上传前校验
  const beforeUpload = (file) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件！');
      return Upload.LIST_IGNORE; // 忽略此文件
    }
    
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('图片大小不能超过 10MB！');
      return Upload.LIST_IGNORE;
    }
    
    if (referenceImages.length >= maxReferenceImages) {
      message.warning(`最多只能上传 ${maxReferenceImages} 张参考图！`);
      return Upload.LIST_IGNORE;
    }
    
    return true; // 允许上传
  };
  
  // 自定义上传处理 - 上传到OSS
  const handleUpload = async ({ file }) => {
    const loadingKey = `uploading-${file.name}`;
    
    try {
      message.loading({ content: `正在上传 ${file.name}...`, key: loadingKey, duration: 0 });
      
      // 上传到OSS
      const result = await fileUploadAPI.uploadReferenceImage(file);
      
      message.destroy(loadingKey);
      
      // 添加到状态（使用OSS URL）
      addReferenceImage({
        url: result.url,
        objectKey: result.object_key,
        file: file,
        name: file.name,
        size: result.size
      });
      
      message.success(`上传成功: ${file.name}`);
      
    } catch (error) {
      message.destroy(loadingKey);
      console.error('上传参考图失败:', error);
      message.error(`上传失败: ${error.message || '未知错误'}`);
    }
  };
  
  // 删除参考图
  const handleRemove = (imageId) => {
    removeReferenceImage(imageId);
    message.info('已删除参考图');
  };
  
  // 清空所有参考图
  const handleClearAll = () => {
    clearReferenceImages();
    message.info('已清空所有参考图');
  };
  
  return (
    <Card 
      title={
        <Space>
          <span>📷 参考图 (可选)</span>
          <Tag color="blue">
            {referenceImages.length} / {maxReferenceImages}
          </Tag>
          <Tooltip title="上传参考图片,AI会参考其风格和内容生成新图">
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>
      }
      extra={
        referenceImages.length > 0 && (
          <Button 
            type="link" 
            size="small" 
            danger 
            onClick={handleClearAll}
            disabled={isGenerating}
          >
            清空全部
          </Button>
        )
      }
      variant="borderless"
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 说明 */}
        <div style={{ 
          padding: '8px 12px', 
          backgroundColor: '#e6f7ff', 
          borderRadius: 4,
          fontSize: 12
        }}>
          <InfoCircleOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          最多上传 {maxReferenceImages} 张参考图，AI会参考其风格、构图和色彩生成新图片
        </div>
        
        {/* 上传区域 */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          {/* 已上传的参考图 */}
          {referenceImages.map((img) => (
            <div 
              key={img.id}
              style={{
                position: 'relative',
                width: 120,
                height: 120,
                borderRadius: 8,
                overflow: 'hidden',
                border: '2px solid #1890ff',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}
            >
              <Image
                src={img.url}
                alt="参考图"
                style={{ 
                  width: '100%', 
                  height: '100%', 
                  objectFit: 'cover' 
                }}
                preview={{
                  mask: (
                    <Space direction="vertical" align="center">
                      <div>预览</div>
                    </Space>
                  )
                }}
              />
              <Button
                type="primary"
                danger
                size="small"
                icon={<DeleteOutlined />}
                onClick={() => handleRemove(img.id)}
                disabled={isGenerating}
                style={{
                  position: 'absolute',
                  top: 4,
                  right: 4,
                  zIndex: 1
                }}
              />
              {img.name && (
                <div style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  padding: '4px 8px',
                  backgroundColor: 'rgba(0,0,0,0.6)',
                  color: 'white',
                  fontSize: 10,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {img.name}
                </div>
              )}
            </div>
          ))}
          
          {/* 上传按钮 */}
          {referenceImages.length < maxReferenceImages && (
            <Upload
              beforeUpload={beforeUpload}
              customRequest={handleUpload}
              showUploadList={false}
              accept="image/*"
              disabled={isGenerating}
            >
              <div
                style={{
                  width: 120,
                  height: 120,
                  border: '2px dashed #d9d9d9',
                  borderRadius: 8,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: isGenerating ? 'not-allowed' : 'pointer',
                  backgroundColor: '#fafafa',
                  transition: 'all 0.3s',
                  ':hover': {
                    borderColor: '#1890ff',
                    backgroundColor: '#f0f5ff'
                  }
                }}
                onMouseEnter={(e) => {
                  if (!isGenerating) {
                    e.currentTarget.style.borderColor = '#1890ff';
                    e.currentTarget.style.backgroundColor = '#f0f5ff';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isGenerating) {
                    e.currentTarget.style.borderColor = '#d9d9d9';
                    e.currentTarget.style.backgroundColor = '#fafafa';
                  }
                }}
              >
                <PlusOutlined style={{ fontSize: 24, color: '#8c8c8c' }} />
                <div style={{ marginTop: 8, fontSize: 12, color: '#8c8c8c' }}>
                  上传图片
                </div>
              </div>
            </Upload>
          )}
        </div>
        
        {/* 提示信息 */}
        {referenceImages.length === 0 && (
          <div style={{ 
            padding: '20px', 
            textAlign: 'center',
            backgroundColor: '#fafafa',
            borderRadius: 8,
            border: '1px dashed #d9d9d9'
          }}>
            <div style={{ fontSize: 14, color: '#8c8c8c' }}>
              暂无参考图
            </div>
            <div style={{ fontSize: 12, color: '#bfbfbf', marginTop: 4 }}>
              点击上方按钮上传参考图片
            </div>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default ReferenceUpload;

