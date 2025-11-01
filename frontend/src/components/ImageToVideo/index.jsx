/**
 * 图生视频页面主组件
 * 整合所有子组件，实现完整的图生视频工作流
 */

import React from 'react';
import { Layout, Row, Col, Button, Space, message, Spin } from 'antd';
import { VideoCameraOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

import ImageUpload from './ImageUpload';
import FrameSwitch from './FrameSwitch';
import PromptInput from './PromptInput';
import ModelSelector from './ModelSelector';
import VideoResult from './VideoResult';

import useVideoStore from '../../store/videoStore';
import { imageToVideoAPI } from '../../services/api';

const { Content } = Layout;

const ImageToVideoPage = () => {
  const navigate = useNavigate();
  
  const {
    firstFrame,
    lastFrame,
    prompt,
    selectedModel,
    duration,
    resolution,
    aspectRatio,
    generating,
    setGenerating,
    setVideoResult,
    setError,
    clearError
  } = useVideoStore();
  
  /**
   * 验证输入
   */
  const validateInput = () => {
    // 检查提示词
    if (!prompt || prompt.trim().length === 0) {
      message.warning('请输入视频描述提示词');
      return false;
    }
    
    // 判断是否为 Sora 2 模型
    const isSoraV2 = selectedModel.startsWith('sora-v2');
    
    // 文生视频模式不需要图片（火山引擎、Google Veo、Sora 2）
    if (selectedModel === 'volc-t2v' || selectedModel === 'google-veo-t2v' || isSoraV2) {
      // Sora 2 支持文生视频，但如果上传了首帧图片，也可以进行图生视频
      // 这里只验证提示词，不强制要求图片
      return true;
    }
    
    // 图生视频模式需要首帧
    if (!firstFrame || !firstFrame.base64) {
      message.warning('请先上传首帧图片');
      return false;
    }
    
    // 检查首尾帧模式是否需要尾帧
    if (selectedModel === 'volc-i2v-first-tail' && (!lastFrame || !lastFrame.base64)) {
      message.warning('首尾帧模式需要上传尾帧图片');
      return false;
    }
    
    return true;
  };
  
  /**
   * 生成视频
   */
  const handleGenerateVideo = async () => {
    if (!validateInput()) {
      return;
    }
    
    clearError();
    setGenerating(true);
    
    try {
      // 判断是否为 Sora 2 模型
      const isSoraV2 = selectedModel.startsWith('sora-v2');
      
      // Sora 2 模型的时长由模型名控制
      const soraDuration = isSoraV2 ? (selectedModel.includes('15s') ? 15 : 10) : null;
      
      console.log('[生成视频] 开始...', {
        model: selectedModel,
        duration: isSoraV2 ? soraDuration : duration,
        resolution: isSoraV2 ? 'N/A (Sora 2)' : resolution,
        aspectRatio: isSoraV2 ? 'N/A (Sora 2)' : aspectRatio,
        hasFirstFrame: !!firstFrame,
        hasLastFrame: !!lastFrame,
        promptLength: prompt.length
      });
      
      const params = {
        model: selectedModel,
        first_frame_base64: firstFrame?.base64 || null, // 使用Base64
        last_frame_base64: lastFrame?.base64 || null, // 使用Base64
        prompt: prompt.trim(),
        duration: isSoraV2 ? soraDuration : duration,  // Sora 2 自动设置时长
        resolution: isSoraV2 ? undefined : resolution,  // Sora 2 不需要分辨率参数
        aspect_ratio: isSoraV2 ? undefined : aspectRatio  // Sora 2 不需要长宽比参数
      };
      
      const result = await imageToVideoAPI.generateVideo(params);
      
      console.log('[生成视频] 成功:', result);
      
      setVideoResult(result);
      message.success('视频生成成功！');
      
      // 滚动到结果区域
      setTimeout(() => {
        const resultElement = document.querySelector('#video-result');
        if (resultElement) {
          resultElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 300);
      
    } catch (error) {
      console.error('[生成视频] 失败:', error);
      const errorMessage = error.message || '视频生成失败';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setGenerating(false);
    }
  };
  
  return (
    <Content
      style={{
        padding: '24px',
        minHeight: 'calc(100vh - 64px)',
        backgroundColor: '#f0f2f5'
      }}
    >
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* 页面标题 */}
        <div style={{ marginBottom: '24px' }}>
          <Space size="large">
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/text-to-image')}
            >
              返回文生图
            </Button>
            <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 600 }}>
              <VideoCameraOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
              图生视频
            </h1>
          </Space>
          <p style={{ marginTop: '8px', color: '#666', fontSize: '14px' }}>
            上传图片，输入描述，生成动态视频。支持单图首帧和首尾帧插值两种模式。
          </p>
        </div>
        
        <Spin spinning={generating} tip="正在生成视频，请耐心等待...">
          <Row gutter={[24, 24]}>
            {/* 左侧：配置区域 */}
            <Col xs={24} lg={12}>
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                {/* 1. 模型选择（顶部） */}
                <ModelSelector />
                
                {/* 2. 图片上传（中间） */}
                <ImageUpload />
                
                {/* 3. 首尾帧交换按钮（中间） */}
                <FrameSwitch />
                
                {/* 4. 提示词输入（底部） */}
                <PromptInput />
                
                {/* 5. 生成按钮（底部） */}
                <div style={{ textAlign: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<VideoCameraOutlined />}
                    onClick={handleGenerateVideo}
                    loading={generating}
                    disabled={generating}
                    style={{
                      height: '48px',
                      fontSize: '16px',
                      fontWeight: 600,
                      paddingLeft: '32px',
                      paddingRight: '32px'
                    }}
                  >
                    {generating ? '生成中...' : '生成视频'}
                  </Button>
                  <div style={{ marginTop: '12px', fontSize: '12px', color: '#999' }}>
                    💡 预计生成时间：5-30分钟（取决于模型和排队情况）
                  </div>
                </div>
              </Space>
            </Col>
            
            {/* 右侧：结果区域 */}
            <Col xs={24} lg={12} id="video-result">
              <VideoResult />
            </Col>
          </Row>
        </Spin>
      </div>
    </Content>
  );
};

export default ImageToVideoPage;
