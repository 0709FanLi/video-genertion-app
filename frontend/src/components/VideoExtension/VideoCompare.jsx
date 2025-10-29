/**
 * 视频对比组件
 * 显示原始视频和扩展后的视频对比
 */

import React from 'react';
import { Card, Row, Col, Button, Space, Tag, Divider } from 'antd';
import {
  DownloadOutlined,
  PlayCircleOutlined,
  VideoCameraOutlined
} from '@ant-design/icons';
import useVideoExtensionStore from '../../store/videoExtensionStore';

const VideoCompare = () => {
  const {
    originalVideo,
    extendedVideo
  } = useVideoExtensionStore();
  
  if (!extendedVideo) {
    return null;
  }
  
  /**
   * 下载视频
   */
  const handleDownload = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <Card
      title={
        <Space>
          <VideoCameraOutlined />
          <span>生成结果</span>
          <Tag color="success">扩展成功</Tag>
        </Space>
      }
      variant="borderless"
      id="video-result"
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 视频对比 */}
        <Row gutter={[16, 16]}>
          {/* 原始视频 */}
          <Col xs={24} md={12}>
            <div style={{ 
              border: '2px solid #d9d9d9', 
              borderRadius: '8px', 
              padding: '12px',
              background: '#fafafa'
            }}>
              <div style={{ 
                marginBottom: '12px', 
                fontWeight: 500,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <Space>
                  <PlayCircleOutlined />
                  <span>原始视频</span>
                </Space>
                <Tag>{originalVideo?.duration}秒</Tag>
              </div>
              <video
                src={originalVideo?.previewUrl || originalVideo?.url}
                controls
                style={{
                  width: '100%',
                  borderRadius: '4px',
                  backgroundColor: '#000'
                }}
              />
            </div>
          </Col>
          
          {/* 扩展后的视频 */}
          <Col xs={24} md={12}>
            <div style={{ 
              border: '2px solid #52c41a', 
              borderRadius: '8px', 
              padding: '12px',
              background: '#f6ffed'
            }}>
              <div style={{ 
                marginBottom: '12px', 
                fontWeight: 500,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <Space>
                  <PlayCircleOutlined style={{ color: '#52c41a' }} />
                  <span style={{ color: '#52c41a' }}>扩展后视频</span>
                </Space>
                <Tag color="success">{extendedVideo.duration}秒</Tag>
              </div>
              <video
                src={extendedVideo.extended_video_url}
                controls
                autoPlay
                style={{
                  width: '100%',
                  borderRadius: '4px',
                  backgroundColor: '#000'
                }}
              />
              <div style={{ marginTop: '12px', textAlign: 'center' }}>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownload(
                    extendedVideo.extended_video_url,
                    `extended_video_${Date.now()}.mp4`
                  )}
                >
                  下载扩展视频
                </Button>
              </div>
            </div>
          </Col>
        </Row>
        
        <Divider />
        
        {/* 扩展信息 */}
        <div style={{ 
          padding: '16px', 
          background: '#f5f5f5', 
          borderRadius: '8px'
        }}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ fontWeight: 500, marginBottom: '8px' }}>📋 扩展信息</div>
            <Row gutter={[16, 8]}>
              <Col span={12}>
                <div style={{ fontSize: '12px', color: '#666' }}>使用模型</div>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>{extendedVideo.model}</div>
              </Col>
              <Col span={12}>
                <div style={{ fontSize: '12px', color: '#666' }}>视频分辨率</div>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>{extendedVideo.resolution}</div>
              </Col>
              <Col span={12}>
                <div style={{ fontSize: '12px', color: '#666' }}>长宽比</div>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>{extendedVideo.aspect_ratio}</div>
              </Col>
              <Col span={12}>
                <div style={{ fontSize: '12px', color: '#666' }}>总时长</div>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>{extendedVideo.duration}秒</div>
              </Col>
              <Col span={24}>
                <div style={{ fontSize: '12px', color: '#666' }}>扩展提示词</div>
                <div style={{ 
                  fontSize: '14px', 
                  padding: '8px', 
                  background: '#fff',
                  borderRadius: '4px',
                  marginTop: '4px'
                }}>
                  {extendedVideo.prompt}
                </div>
              </Col>
            </Row>
          </Space>
        </div>
      </Space>
    </Card>
  );
};

export default VideoCompare;

