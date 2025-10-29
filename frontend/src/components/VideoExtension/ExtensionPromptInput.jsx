/**
 * 扩展提示词输入组件
 * 支持提示词优化
 */

import React from 'react';
import { Card, Input, Button, Space, Tag, Tooltip, message } from 'antd';
import {
  EditOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  SwapOutlined
} from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';
import { textToImageAPI } from '../../services/api';

const { TextArea } = Input;

const ExtensionPromptInput = () => {
  const {
    extensionPrompt,
    optimizedPrompt,
    useOptimizedPrompt,
    selectedPromptModel,
    isOptimizing,
    isExtending,
    setExtensionPrompt,
    setOptimizedPrompt,
    toggleUseOptimizedPrompt,
    setOptimizing,
    getCurrentPrompt
  } = useVideoExtensionStore();
  
  const maxLength = 1000;
  
  /**
   * 处理提示词优化
   */
  const handleOptimize = async () => {
    if (!extensionPrompt.trim()) {
      message.warning('请先输入扩展提示词');
      return;
    }
    
    try {
      setOptimizing(true);
      message.loading({ content: '正在优化提示词...', key: 'optimize' });
      
      const result = await textToImageAPI.optimizePrompt({
        prompt: extensionPrompt,
        model: selectedPromptModel,
        language: 'zh'  // 固定返回中文
      });
      
      setOptimizedPrompt(result.optimized_prompt);
      message.success({ content: '提示词优化成功！', key: 'optimize' });
      
    } catch (error) {
      console.error('优化提示词失败:', error);
      message.error({ content: '提示词优化失败', key: 'optimize' });
    } finally {
      setOptimizing(false);
    }
  };
  
  const currentPrompt = getCurrentPrompt();
  const hasOptimized = optimizedPrompt.trim() !== '';
  
  return (
    <Card
      title={
        <Space>
          <EditOutlined />
          <span>扩展描述提示词</span>
          {hasOptimized && (
            <Tag color={useOptimizedPrompt ? 'blue' : 'default'}>
              {useOptimizedPrompt ? '使用优化版' : '使用原始版'}
            </Tag>
          )}
        </Space>
      }
      variant="borderless"
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {/* 原始提示词输入 */}
        <div>
          <div style={{ marginBottom: '8px', fontWeight: 500 }}>
            输入扩展内容描述
          </div>
          <TextArea
            value={extensionPrompt}
            onChange={(e) => setExtensionPrompt(e.target.value)}
            placeholder="描述你想要在视频中添加的扩展内容&#10;例如：镜头跟随蝴蝶飞入花园，落在一朵橙色的折纸花上。一只毛茸茸的白色小狗跑过来，轻轻拍打这朵花。"
            rows={4}
            maxLength={maxLength}
            showCount
            disabled={isExtending}
          />
        </div>
        
        {/* 操作按钮 */}
        <Space>
          <Button
            type="primary"
            icon={<BulbOutlined />}
            onClick={handleOptimize}
            loading={isOptimizing}
            disabled={!extensionPrompt.trim() || isExtending}
          >
            优化提示词
          </Button>
          
          {hasOptimized && (
            <Button
              icon={<SwapOutlined />}
              onClick={toggleUseOptimizedPrompt}
              disabled={isExtending}
            >
              {useOptimizedPrompt ? '切换到原始版' : '切换到优化版'}
            </Button>
          )}
        </Space>
        
        {/* 优化后的提示词预览 */}
        {hasOptimized && (
          <div
            style={{
              padding: '12px',
              background: useOptimizedPrompt ? '#e6f7ff' : '#f5f5f5',
              border: useOptimizedPrompt ? '1px solid #91d5ff' : '1px solid #d9d9d9',
              borderRadius: '8px'
            }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                <span style={{ fontWeight: 500, color: '#52c41a' }}>
                  优化后的提示词
                </span>
                {useOptimizedPrompt && (
                  <Tag color="blue" style={{ marginLeft: 'auto' }}>
                    当前使用
                  </Tag>
                )}
              </div>
              <div style={{ fontSize: '14px', color: '#595959', lineHeight: '1.6' }}>
                {optimizedPrompt}
              </div>
              <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                字数: {optimizedPrompt.length} / {maxLength}
              </div>
            </Space>
          </div>
        )}
        
        {/* 当前使用的提示词提示 */}
        {currentPrompt && (
          <div style={{ fontSize: '12px', color: '#1890ff' }}>
            💡 当前将使用{hasOptimized && useOptimizedPrompt ? '优化后的' : '原始'}提示词进行视频扩展
          </div>
        )}
        
        {/* 提示信息 */}
        <div style={{ fontSize: '12px', color: '#666' }}>
          <Space direction="vertical" size="small">
            <div>💡 提示：详细描述视频扩展的内容，包括动作、场景、角色等</div>
            <div>🎯 建议：使用提示词优化功能可以获得更好的扩展效果</div>
          </Space>
        </div>
      </Space>
    </Card>
  );
};

export default ExtensionPromptInput;

