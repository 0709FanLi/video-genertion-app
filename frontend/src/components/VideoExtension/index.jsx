/**
 * 视频扩展主页面
 * 整合所有子组件
 */

import React, { useEffect } from 'react';
import { Layout, Row, Col, Button, Space, message, Spin } from 'antd';
import { ExpandOutlined, ArrowLeftOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

import VideoUpload from './VideoUpload';
import ModelSelector from './ModelSelector';
import ExtensionPromptInput from './ExtensionPromptInput';
import VideoCompare from './VideoCompare';

import useVideoExtensionStore from '../../store/videoExtensionStore';
import { videoExtensionAPI, textToImageAPI } from '../../services/api';

const { Content } = Layout;

const VideoExtensionPage = () => {
  const navigate = useNavigate();
  
  const {
    originalVideo,
    isExtending,
    extendedVideo,
    selectedModel,
    aspectRatio,
    duration,
    resolution,
    error,
    setExtending,
    setExtendedVideo,
    setError,
    clearError,
    setLoadingModels,
    setModels,
    canStartExtension,
    getCurrentPrompt
  } = useVideoExtensionStore();
  
  // 加载模型列表
  useEffect(() => {
    const loadModels = async () => {
      try {
        setLoadingModels(true);
        
        // 加载视频扩展模型
        const extensionData = await videoExtensionAPI.getModels();
        
        // 加载提示词优化模型（复用文生图的）
        const promptData = await textToImageAPI.getModels();
        
        setModels(
          extensionData.video_extension_models,
          promptData.prompt_optimization_models
        );
      } catch (error) {
        console.error('加载模型列表失败:', error);
        message.error('加载模型列表失败');
      } finally {
        setLoadingModels(false);
      }
    };
    
    loadModels();
  }, []);
  
  /**
   * 开始视频扩展
   */
  const handleStartExtension = async () => {
    if (!canStartExtension()) {
      message.warning('请先上传视频并输入扩展提示词');
      return;
    }
    
    clearError();
    setExtending(true);
    
    try {
      console.log('[视频扩展] 开始...', {
        model: selectedModel,
        aspect_ratio: aspectRatio,
        duration: duration,
        resolution: resolution,
        video_url: originalVideo.url,
        promptLength: getCurrentPrompt().length
      });
      
      const params = {
        video_url: originalVideo.url,
        prompt: getCurrentPrompt(),
        model: selectedModel,
        aspect_ratio: aspectRatio,
        duration: duration,
        resolution: resolution
      };
      
      const result = await videoExtensionAPI.extendVideo(params);
      
      console.log('[视频扩展] 成功:', result);
      
      setExtendedVideo(result);
      message.success('视频扩展成功！');
      
      // 滚动到结果区域
      setTimeout(() => {
        const resultElement = document.querySelector('#video-result');
        if (resultElement) {
          resultElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 300);
      
    } catch (error) {
      console.error('[视频扩展] 失败:', error);
      const errorMessage = error.message || '视频扩展失败';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setExtending(false);
    }
  };
  
  return (
    <Content style={{
      minHeight: 'calc(100vh - 64px)',
      padding: '24px',
      backgroundColor: '#f0f2f5'
    }}>
      {/* 页面标题 */}
      <div style={{
        marginBottom: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Space size="large">
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/image-to-video')}
          >
            返回
          </Button>
          <div>
            <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 600 }}>
              <ExpandOutlined style={{ marginRight: '12px', color: '#1890ff' }} />
              视频扩展
            </h1>
            <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
              基于原始视频，使用AI技术生成扩展内容
            </div>
          </div>
        </Space>
      </div>
      
      {/* 主内容区域 */}
      <Row gutter={[24, 24]}>
        {/* 左侧：配置区域 */}
        <Col xs={24} lg={12}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 1. 模型选择（顶部） */}
            <ModelSelector />
            
            {/* 2. 视频上传（中间） */}
            <VideoUpload />
            
            {/* 3. 扩展提示词输入（底部） */}
            <ExtensionPromptInput />
            
            {/* 4. 生成按钮（底部） */}
            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={handleStartExtension}
              loading={isExtending}
              disabled={!canStartExtension()}
              block
              style={{ height: '56px', fontSize: '16px', fontWeight: 500 }}
            >
              {isExtending ? '正在扩展视频...' : '开始扩展视频'}
            </Button>
            
            {/* 错误提示 */}
            {error && (
              <div style={{
                padding: '12px',
                background: '#fff2e8',
                border: '1px solid #ffbb96',
                borderRadius: '8px',
                color: '#d4380d'
              }}>
                ❌ {error}
              </div>
            )}
            
            {/* 提示信息 */}
            {!originalVideo && (
              <div style={{
                padding: '16px',
                background: '#e6f7ff',
                border: '1px solid #91d5ff',
                borderRadius: '8px',
                color: '#0050b3'
              }}>
                <Space direction="vertical" size="small">
                  <div style={{ fontWeight: 500 }}>💡 使用说明</div>
                  <div style={{ fontSize: '12px' }}>
                    1. 上传原始视频（MP4/MOV格式）<br />
                    2. 输入扩展内容描述<br />
                    3. 可选：优化提示词以获得更好效果<br />
                    4. 设置长宽比和反向提示词（可选）<br />
                    5. 点击"开始扩展视频"生成结果
                  </div>
                </Space>
              </div>
            )}
          </Space>
        </Col>
        
        {/* 右侧：结果展示区域 */}
        <Col xs={24} lg={12}>
          {isExtending ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '500px',
              background: '#fff',
              borderRadius: '8px',
              border: '1px dashed #d9d9d9'
            }}>
              <Spin size="large" />
              <div style={{ marginTop: '24px', fontSize: '16px', color: '#666' }}>
                正在扩展视频，请耐心等待...
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>
                这可能需要几分钟时间
              </div>
            </div>
          ) : extendedVideo ? (
            <VideoCompare />
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '500px',
              background: '#fff',
              borderRadius: '8px',
              border: '1px dashed #d9d9d9'
            }}>
              <ExpandOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />
              <div style={{ marginTop: '24px', fontSize: '16px', color: '#999' }}>
                扩展后的视频将显示在这里
              </div>
            </div>
          )}
        </Col>
      </Row>
    </Content>
  );
};

export default VideoExtensionPage;
