/**
 * 首页组件
 */

import React from 'react';
import { Layout, Card, Row, Col, Button, Typography } from 'antd';
import { 
  PictureOutlined, 
  VideoCameraOutlined, 
  ExpandOutlined,
  RightOutlined 
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Content } = Layout;
const { Title, Paragraph } = Typography;

const Home = () => {
  const navigate = useNavigate();
  
  const features = [
    {
      icon: <PictureOutlined style={{ fontSize: 48, color: '#667eea' }} />,
      title: '文本生成图片',
      description: '输入文字描述，AI为你创作精美图片。支持多种模型和参考图功能。',
      path: '/text-to-image',
      color: '#667eea',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      icon: <VideoCameraOutlined style={{ fontSize: 48, color: '#f093fb' }} />,
      title: '图片生成视频',
      description: '选择一张图片，AI将其转化为动态视频，赋予静态图片生命。',
      path: '/image-to-video',
      color: '#f093fb',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    },
    {
      icon: <ExpandOutlined style={{ fontSize: 48, color: '#4facfe' }} />,
      title: '视频扩展',
      description: '延长视频时长，让短视频变得更长，创作更丰富的内容。',
      path: '/video-extension',
      color: '#4facfe',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    }
  ];
  
  return (
    <Content style={{ 
      minHeight: 'calc(100vh - 64px)',
      background: 'linear-gradient(180deg, #f0f2f5 0%, #ffffff 100%)',
      padding: '60px 24px'
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* Hero Section */}
        <div style={{ textAlign: 'center', marginBottom: 80 }}>
          <Title 
            level={1} 
            style={{ 
              fontSize: 48,
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              marginBottom: 16
            }}
          >
            🎨 AI创意生成平台0.2
          </Title>
          <Paragraph 
            style={{ 
              fontSize: 18, 
              color: '#595959',
              maxWidth: 600,
              margin: '0 auto'
            }}
          >
            将你的创意想法转化为精美的图片和视频<br />
            强大的AI技术，简单的操作流程，无限的创作可能
          </Paragraph>
        </div>
        
        {/* Features Grid */}
        <Row gutter={[32, 32]}>
          {features.map((feature, index) => (
            <Col xs={24} md={8} key={index}>
              <Card
                hoverable
                style={{
                  height: '100%',
                  borderRadius: 16,
                  border: 'none',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                  transition: 'all 0.3s'
                }}
                styles={{
                  body: {
                    padding: 32,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    textAlign: 'center'
                  }
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-8px)';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
                }}
              >
                <div style={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: feature.gradient,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 24,
                  boxShadow: `0 4px 12px ${feature.color}40`
                }}>
                  {React.cloneElement(feature.icon, { style: { fontSize: 40, color: 'white' } })}
                </div>
                
                <Title level={3} style={{ marginBottom: 12, fontSize: 22 }}>
                  {feature.title}
                </Title>
                
                <Paragraph style={{ color: '#8c8c8c', marginBottom: 24, fontSize: 14 }}>
                  {feature.description}
                </Paragraph>
                
                <Button
                  type="primary"
                  size="large"
                  icon={<RightOutlined />}
                  onClick={() => navigate(feature.path)}
                  style={{
                    background: feature.gradient,
                    border: 'none',
                    borderRadius: 8,
                    height: 48,
                    fontWeight: 'bold',
                    boxShadow: `0 4px 12px ${feature.color}40`
                  }}
                >
                  立即体验
                </Button>
              </Card>
            </Col>
          ))}
        </Row>
        
        {/* Bottom Info */}
        <div style={{ 
          textAlign: 'center', 
          marginTop: 80,
          padding: 32,
          backgroundColor: 'white',
          borderRadius: 16,
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
        }}>
          <Title level={3} style={{ marginBottom: 16 }}>
            💡 使用技巧
          </Title>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={8}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>
                  详细描述
                </div>
                <div style={{ fontSize: 14, color: '#8c8c8c' }}>
                  提示词越详细，生成的图片质量越高
                </div>
              </div>
            </Col>
            <Col xs={24} md={8}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>
                  AI优化
                </div>
                <div style={{ fontSize: 14, color: '#8c8c8c' }}>
                  使用AI优化功能让提示词更专业
                </div>
              </div>
            </Col>
            <Col xs={24} md={8}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>
                  参考图片
                </div>
                <div style={{ fontSize: 14, color: '#8c8c8c' }}>
                  上传参考图获得更符合预期的结果
                </div>
              </div>
            </Col>
          </Row>
        </div>
      </div>
    </Content>
  );
};

export default Home;

