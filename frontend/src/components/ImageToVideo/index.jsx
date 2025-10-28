/**
 * 图生视频页面组件（占位）
 */

import React from 'react';
import { Layout, Result, Button } from 'antd';
import { VideoCameraOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Content } = Layout;

const ImageToVideoPage = () => {
  const navigate = useNavigate();
  
  return (
    <Content style={{ 
      padding: '50px',
      minHeight: 'calc(100vh - 64px)',
      backgroundColor: '#f0f2f5',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Result
        icon={<VideoCameraOutlined style={{ color: '#1890ff' }} />}
        title="图生视频功能"
        subTitle="此功能正在开发中，敬请期待..."
        extra={[
          <Button 
            type="primary" 
            key="back"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/text-to-image')}
          >
            返回文生图
          </Button>,
          <Button key="home" onClick={() => navigate('/')}>
            返回首页
          </Button>
        ]}
      />
    </Content>
  );
};

export default ImageToVideoPage;

