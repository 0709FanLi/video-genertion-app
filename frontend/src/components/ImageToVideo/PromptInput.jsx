/**
 * 视频提示词输入组件
 * 支持手动输入和智能分析
 */

import React, { useState } from 'react';
import { Card, Input, Button, Space, message, Tooltip, Select, Tag, Upload } from 'antd';
import { BulbOutlined, LoadingOutlined, ThunderboltOutlined } from '@ant-design/icons';
import useVideoStore from '../../store/videoStore';
import { imageToVideoAPI, textToImageAPI } from '../../services/api';

const { TextArea } = Input;

const PromptInput = () => {
  const {
    prompt,
    setPrompt,
    selectedModel
  } = useVideoStore();
  
  // 文生视频模式不支持图片分析
  const isTextToVideo = selectedModel === 'volc-t2v';
  
  // 优化模型和状态
  const [optimizeModel, setOptimizeModel] = useState('qwen-plus');
  const [optimizing, setOptimizing] = useState(false);
  const [originalPrompt, setOriginalPrompt] = useState('');
  
  // 图片分析状态
  const [analyzingImage, setAnalyzingImage] = useState(false);
  
  /**
   * 优化提示词
   */
  const handleOptimizePrompt = async () => {
    if (!prompt || prompt.trim().length === 0) {
      message.warning('请先输入提示词');
      return;
    }
    
    setOptimizing(true);
    setOriginalPrompt(prompt); // 保存原始提示词
    
    try {
      console.log('[优化提示词] 开始...', { prompt, model: optimizeModel });
      const result = await textToImageAPI.optimizePrompt(prompt, optimizeModel, 'zh');
      
      console.log('[优化提示词] 结果:', result);
      setPrompt(result.optimized_prompt);
      message.success('提示词优化完成！');
      
    } catch (error) {
      console.error('[优化提示词] 失败:', error);
      message.error(`提示词优化失败: ${error.message}`);
    } finally {
      setOptimizing(false);
    }
  };
  
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
   * 处理图片上传并分析
   */
  const handleAnalyzeImageUpload = async (file) => {
    // 验证文件类型
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件！');
      return false;
    }
    
    // 验证文件大小
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('图片大小不能超过10MB！');
      return false;
    }
    
    setAnalyzingImage(true);
    
    try {
      console.log('[分析图片] 开始转换Base64...');
      const base64 = await fileToBase64(file);
      
      console.log('[分析图片] 开始分析...');
      const result = await imageToVideoAPI.analyzeImage(base64, true);
      
      console.log('[分析图片] 结果:', result);
      setPrompt(result.description);
      message.success('图片分析完成！');
      
    } catch (error) {
      console.error('[分析图片] 失败:', error);
      message.error(`图片分析失败: ${error.message}`);
    } finally {
      setAnalyzingImage(false);
    }
    
    // 阻止Upload组件的默认上传行为
    return false;
  };
  
  return (
    <Card
      title="视频描述提示词"
      variant="borderless"
      styles={{ body: { padding: '16px' } }}
      extra={
        <Space>
          {/* 优化提示词 */}
          <Select
            value={optimizeModel}
            onChange={setOptimizeModel}
            style={{ width: '140px' }}
            size="small"
            options={[
              { value: 'qwen-plus', label: '通义千问Plus' },
              { value: 'deepseek-v3', label: 'DeepSeek V3' }
            ]}
          />
          <Tooltip title="使用AI优化提示词，使其更适合视频生成">
            <Button
              type="primary"
              icon={optimizing ? <LoadingOutlined /> : <ThunderboltOutlined />}
              onClick={handleOptimizePrompt}
              loading={optimizing}
              disabled={!prompt || optimizing}
            >
              {optimizing ? '优化中...' : '优化提示词'}
            </Button>
          </Tooltip>
          
          {/* 分析图片（上传本地图片进行分析） */}
          {!isTextToVideo && (
            <Tooltip title="上传图片让AI分析内容，自动生成适合视频的描述文本">
              <Upload
                accept="image/*"
                showUploadList={false}
                beforeUpload={handleAnalyzeImageUpload}
                disabled={analyzingImage}
              >
                <Button
                  icon={analyzingImage ? <LoadingOutlined /> : <BulbOutlined />}
                  loading={analyzingImage}
                  disabled={analyzingImage}
                >
                  {analyzingImage ? '分析中...' : '分析图片'}
                </Button>
              </Upload>
            </Tooltip>
          )}
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <TextArea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={`描述希望视频中发生什么样的运动或变化，例如：
- 镜头拉远，展现全景
- 花瓣飘落，微风吹过
- 人物向前奔跑

提示：点击上方"分析图片"按钮，AI将自动生成详细的视频描述`}
          rows={6}
          maxLength={800}
          showCount
          style={{ fontSize: '14px' }}
        />
        
        <div style={{ fontSize: '12px', color: '#666' }}>
          <div>💡 提示：</div>
          <div>• 可以手动输入视频描述，也可以点击"优化提示词"让AI增强描述效果</div>
          {!isTextToVideo && <div>• 也可以点击"分析图片"让AI根据图片生成描述</div>}
          <div>• 建议描述包含：主体、场景、动态变化、镜头移动等</div>
          <div>• 长度建议在200-400字，最长不超过800字</div>
        </div>
        
        {/* 显示原始提示词（如果已优化） */}
        {originalPrompt && originalPrompt !== prompt && (
          <div style={{ 
            padding: '12px', 
            background: '#f0f2f5', 
            borderRadius: '4px',
            fontSize: '12px'
          }}>
            <div style={{ marginBottom: '4px', color: '#666' }}>
              <strong>原始提示词：</strong>
            </div>
            <div style={{ color: '#999' }}>{originalPrompt}</div>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default PromptInput;

