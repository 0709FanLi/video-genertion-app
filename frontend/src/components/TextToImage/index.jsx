/**
 * 文生图主页面组件
 */

import React, { useEffect } from 'react';
import { Layout, Row, Col, Alert, Spin, message } from 'antd';
import PromptInput from './PromptInput';
import ModelSelector from './ModelSelector';
import ReferenceUpload from './ReferenceUpload';
import ResultGrid from './ResultGrid';
import useImageStore from '../../store/imageStore';
import { textToImageAPI } from '../../services/api';

const { Content } = Layout;

const TextToImagePage = () => {
  const {
    selectedImageModel,
    referenceImages,
    textToImageModels,
    isGenerating,
    isLoadingModels,
    error,
    getCurrentPrompt,
    setModels,
    setGenerating,
    setError,
    clearError,
    setLoadingModels,
    addGeneratedImages,
    addToHistory
  } = useImageStore();
  
  // 加载模型列表
  useEffect(() => {
    const loadModels = async () => {
      setLoadingModels(true);
      try {
        const data = await textToImageAPI.getModels();
        setModels(data.text_to_image_models, data.prompt_optimization_models);
      } catch (error) {
        console.error('加载模型列表失败:', error);
        message.error('加载模型列表失败');
      } finally {
        setLoadingModels(false);
      }
    };
    
    loadModels();
  }, []);
  
  // 生成图片
  const handleGenerate = async ({ numImages, size }) => {
    const prompt = getCurrentPrompt();
    
    if (!prompt || !prompt.trim()) {
      message.warning('请先输入提示词');
      return;
    }
    
    clearError();
    setGenerating(true);
    
    try {
      // 准备参考图URL（如果有）
      let referenceImageUrls = null;
      const currentModel = textToImageModels[selectedImageModel];
      
      if (currentModel?.supports_reference && referenceImages.length > 0) {
        // TODO: 这里应该先上传参考图到服务器,获取URL
        // 目前暂时使用本地base64 URL（实际可能不work，需要实现上传功能）
        referenceImageUrls = referenceImages.map(img => img.url);
        message.info(`使用 ${referenceImages.length} 张参考图生成`);
      }
      
      message.loading({ content: '正在生成图片...', key: 'generating', duration: 0 });
      
      // 调用API
      const result = await textToImageAPI.generateImage({
        prompt,
        model: selectedImageModel,
        size,
        num_images: numImages,
        reference_image_urls: referenceImageUrls
      });
      
      message.destroy('generating');
      
      // 添加到结果列表
      const images = result.image_urls.map(url => ({
        url,
        prompt,
        model: result.model
      }));
      
      addGeneratedImages(images);
      
      // 添加到历史记录
      addToHistory({
        type: 'text-to-image',
        prompt,
        model: result.model,
        numImages: result.num_images,
        referenceCount: referenceImages.length,
        images
      });
      
      message.success(`成功生成 ${result.num_images} 张图片！`);
      
    } catch (error) {
      console.error('生成图片失败:', error);
      message.destroy('generating');
      setError(error.message || '生成图片失败');
      message.error(error.message || '生成图片失败');
    } finally {
      setGenerating(false);
    }
  };
  
  if (isLoadingModels) {
    return (
      <Content style={{ padding: '50px', textAlign: 'center' }}>
        <Spin size="large" tip="加载中..." spinning>
          <div style={{ minHeight: 200 }} />
        </Spin>
      </Content>
    );
  }
  
  return (
    <Content style={{ padding: '24px', minHeight: 'calc(100vh - 64px)', backgroundColor: '#f0f2f5' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto' }}>
        {/* 页面标题 */}
        <div style={{ 
          marginBottom: 24, 
          padding: '24px 0',
          textAlign: 'center'
        }}>
          <h1 style={{ 
            fontSize: 32, 
            fontWeight: 'bold', 
            margin: 0,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            ✨ 文本生成图片
          </h1>
          <p style={{ 
            fontSize: 14, 
            color: '#8c8c8c', 
            marginTop: 8,
            marginBottom: 0
          }}>
            输入你的想法，AI帮你创作精美图片 | 支持多种模型和参考图功能
          </p>
        </div>
        
        {/* 错误提示 */}
        {error && (
          <Alert
            message="生成失败"
            description={error}
            type="error"
            closable
            onClose={clearError}
            style={{ marginBottom: 24 }}
            showIcon
          />
        )}
        
        {/* 主要内容区域 */}
        <Row gutter={[24, 24]}>
          {/* 左侧：输入和配置 */}
          <Col xs={24} lg={10}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {/* 提示词输入 */}
              <PromptInput />
              
              {/* 参考图上传 */}
              <ReferenceUpload />
              
              {/* 模型选择和生成按钮 */}
              <ModelSelector onGenerate={handleGenerate} />
            </div>
          </Col>
          
          {/* 右侧：结果展示 */}
          <Col xs={24} lg={14}>
            <ResultGrid />
          </Col>
        </Row>
      </div>
    </Content>
  );
};

export default TextToImagePage;

