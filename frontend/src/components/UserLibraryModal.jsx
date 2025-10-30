/**
 * 资源库弹窗组件
 * 
 * 展示用户的所有生成内容：提示词历史、图片库、视频库
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Tabs, Card, Row, Col, Spin, Empty, Input, Select, Tag, Image, Space, Button, Typography, Pagination, message } from 'antd';
import { SearchOutlined, PictureOutlined, VideoCameraOutlined, FileTextOutlined, DownloadOutlined, EyeOutlined } from '@ant-design/icons';
import { libraryAPI } from '../services/api';
import './UserLibraryModal.css';

const { Search } = Input;
const { Option } = Select;
const { Text, Paragraph } = Typography;

const UserLibraryModal = ({ open, onClose }) => {
  const [activeTab, setActiveTab] = useState('prompts');
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [modelFilter, setModelFilter] = useState(null);
  const [googleVeoOnly, setGoogleVeoOnly] = useState(false);
  
  // 数据状态
  const [prompts, setPrompts] = useState([]);
  const [images, setImages] = useState([]);
  const [videos, setVideos] = useState([]);
  
  // 分页状态
  const [promptsPage, setPromptsPage] = useState(1);
  const [imagesPage, setImagesPage] = useState(1);
  const [videosPage, setVideosPage] = useState(1);
  const [promptsTotal, setPromptsTotal] = useState(0);
  const [imagesTotal, setImagesTotal] = useState(0);
  const [videosTotal, setVideosTotal] = useState(0);
  const pageSize = 12;
  
  // 预览状态
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewContent, setPreviewContent] = useState(null);

  // 加载提示词历史
  const loadPrompts = useCallback(async (page = 1) => {
    setLoading(true);
    try {
      const response = await libraryAPI.getPrompts({
        page,
        limit: pageSize,
        search: searchText || undefined
      });
      setPrompts(response.prompts || []);
      setPromptsTotal(response.total || 0);
      setPromptsPage(page);
    } catch (error) {
      console.error('加载提示词失败:', error);
      message.error('加载提示词失败');
    } finally {
      setLoading(false);
    }
  }, [searchText, pageSize]);

  // 加载图片库
  const loadImages = useCallback(async (page = 1) => {
    setLoading(true);
    try {
      const response = await libraryAPI.getImages({
        page,
        limit: pageSize,
        search: searchText || undefined,
        model: modelFilter || undefined
      });
      setImages(response.images || []);
      setImagesTotal(response.total || 0);
      setImagesPage(page);
    } catch (error) {
      console.error('加载图片失败:', error);
      message.error('加载图片失败');
    } finally {
      setLoading(false);
    }
  }, [searchText, modelFilter, pageSize]);

  // 加载视频库
  const loadVideos = useCallback(async (page = 1) => {
    setLoading(true);
    try {
      const response = await libraryAPI.getVideos({
        page,
        limit: pageSize,
        search: searchText || undefined,
        model: modelFilter || undefined,
        google_veo_only: googleVeoOnly
      });
      setVideos(response.videos || []);
      setVideosTotal(response.total || 0);
      setVideosPage(page);
    } catch (error) {
      console.error('加载视频失败:', error);
      message.error('加载视频失败');
    } finally {
      setLoading(false);
    }
  }, [searchText, modelFilter, googleVeoOnly, pageSize]);

  // 打开弹窗时加载数据
  useEffect(() => {
    if (open) {
      if (activeTab === 'prompts') {
        loadPrompts(1);
      } else if (activeTab === 'images') {
        loadImages(1);
      } else if (activeTab === 'videos') {
        loadVideos(1);
      }
    }
  }, [open, activeTab, loadPrompts, loadImages, loadVideos]);

  // 搜索或筛选变化时重新加载
  useEffect(() => {
    if (!open) return;
    
    const timer = setTimeout(() => {
      if (activeTab === 'prompts') {
        loadPrompts(1);
      } else if (activeTab === 'images') {
        loadImages(1);
      } else if (activeTab === 'videos') {
        loadVideos(1);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchText, modelFilter, googleVeoOnly, activeTab, open, loadPrompts, loadImages, loadVideos]);

  // 预览提示词
  const handlePreviewPrompt = (prompt) => {
    setPreviewContent(prompt);
    setPreviewVisible(true);
  };

  // 预览图片
  const handlePreviewImage = (image) => {
    setPreviewContent(image);
    setPreviewVisible(true);
  };

  // 预览视频
  const handlePreviewVideo = (video) => {
    setPreviewContent(video);
    setPreviewVisible(true);
  };

  // 复制提示词
  const handleCopyPrompt = (text) => {
    navigator.clipboard.writeText(text);
    message.success('已复制到剪贴板');
  };

  // 下载资源
  const handleDownload = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
  };

  // 渲染提示词列表
  const renderPrompts = () => (
    <div>
      <Row gutter={[16, 16]}>
        {prompts.map((prompt) => (
          <Col xs={24} sm={24} md={12} lg={8} key={prompt.id}>
            <Card
              hoverable
              className="library-card"
              onClick={() => handlePreviewPrompt(prompt)}
            >
              <div className="prompt-card">
                <div className="prompt-header">
                  <FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {new Date(prompt.created_at).toLocaleString('zh-CN')}
                  </Text>
                </div>
                
                {prompt.original_prompt && (
                  <div className="prompt-section">
                    <Text strong>原始提示词：</Text>
                    <Paragraph 
                      ellipsis={{ rows: 2 }} 
                      style={{ marginBottom: 8 }}
                    >
                      {prompt.original_prompt}
                    </Paragraph>
                  </div>
                )}
                
                <div className="prompt-section">
                  <Text strong>优化后：</Text>
                  <Paragraph ellipsis={{ rows: 3 }}>
                    {prompt.optimized_prompt}
                  </Paragraph>
                </div>
                
                <div className="prompt-footer">
                  {prompt.optimization_model && (
                    <Tag color="blue">{prompt.optimization_model}</Tag>
                  )}
                  {prompt.scene_type && (
                    <Tag>{prompt.scene_type}</Tag>
                  )}
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
      
      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <Pagination
          current={promptsPage}
          pageSize={pageSize}
          total={promptsTotal}
          onChange={loadPrompts}
          showSizeChanger={false}
          showTotal={(total) => `共 ${total} 条`}
        />
      </div>
    </div>
  );

  // 渲染图片列表
  const renderImages = () => (
    <div>
      <Row gutter={[16, 16]}>
        {images.map((image) => (
          <Col xs={12} sm={8} md={6} lg={4} key={image.id}>
            <Card
              hoverable
              className="library-card image-card"
              cover={
                <div className="image-cover">
                  <Image
                    src={image.image_url}
                    alt="Generated Image"
                    preview={false}
                    style={{ width: '100%', height: '200px', objectFit: 'cover' }}
                  />
                </div>
              }
              actions={[
                <EyeOutlined key="view" onClick={() => handlePreviewImage(image)} />,
                <DownloadOutlined 
                  key="download" 
                  onClick={() => handleDownload(image.image_url, `image_${image.id}.png`)} 
                />
              ]}
            >
              <Card.Meta
                description={
                  <div>
                    <Paragraph ellipsis={{ rows: 2 }} style={{ fontSize: '12px' }}>
                      {image.prompt}
                    </Paragraph>
                    <div>
                      {image.model && <Tag color="blue">{image.model}</Tag>}
                      {image.resolution && <Tag>{image.resolution}</Tag>}
                    </div>
                    <Text type="secondary" style={{ fontSize: '11px' }}>
                      {new Date(image.created_at).toLocaleDateString('zh-CN')}
                    </Text>
                  </div>
                }
              />
            </Card>
          </Col>
        ))}
      </Row>
      
      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <Pagination
          current={imagesPage}
          pageSize={pageSize}
          total={imagesTotal}
          onChange={loadImages}
          showSizeChanger={false}
          showTotal={(total) => `共 ${total} 条`}
        />
      </div>
    </div>
  );

  // 渲染视频列表
  const renderVideos = () => (
    <div>
      <Row gutter={[16, 16]}>
        {videos.map((video) => (
          <Col xs={12} sm={8} md={6} lg={6} key={video.id}>
            <Card
              hoverable
              className="library-card video-card"
              cover={
                <div className="video-cover">
                  <video
                    src={video.video_url}
                    style={{ width: '100%', height: '200px', objectFit: 'cover' }}
                    muted
                  />
                  {video.is_google_veo && (
                    <Tag 
                      color="gold" 
                      style={{ position: 'absolute', top: 8, right: 8 }}
                    >
                      Google Veo
                    </Tag>
                  )}
                </div>
              }
              actions={[
                <EyeOutlined key="view" onClick={() => handlePreviewVideo(video)} />,
                <DownloadOutlined 
                  key="download" 
                  onClick={() => handleDownload(video.video_url, `video_${video.id}.mp4`)} 
                />
              ]}
            >
              <Card.Meta
                description={
                  <div>
                    <Paragraph ellipsis={{ rows: 2 }} style={{ fontSize: '12px' }}>
                      {video.prompt}
                    </Paragraph>
                    <div>
                      {video.model && <Tag color="blue">{video.model}</Tag>}
                      {video.duration && <Tag>{video.duration}秒</Tag>}
                      {video.resolution && <Tag>{video.resolution}</Tag>}
                    </div>
                    <Text type="secondary" style={{ fontSize: '11px' }}>
                      {new Date(video.created_at).toLocaleDateString('zh-CN')}
                    </Text>
                  </div>
                }
              />
            </Card>
          </Col>
        ))}
      </Row>
      
      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <Pagination
          current={videosPage}
          pageSize={pageSize}
          total={videosTotal}
          onChange={loadVideos}
          showSizeChanger={false}
          showTotal={(total) => `共 ${total} 条`}
        />
      </div>
    </div>
  );

  // Tab items
  const tabItems = [
    {
      key: 'prompts',
      label: (
        <span>
          <FileTextOutlined />
          提示词历史 ({promptsTotal})
        </span>
      ),
      children: loading ? (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" />
        </div>
      ) : prompts.length === 0 ? (
        <Empty description="暂无提示词历史" />
      ) : (
        renderPrompts()
      )
    },
    {
      key: 'images',
      label: (
        <span>
          <PictureOutlined />
          图片库 ({imagesTotal})
        </span>
      ),
      children: loading ? (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" />
        </div>
      ) : images.length === 0 ? (
        <Empty description="暂无图片" />
      ) : (
        renderImages()
      )
    },
    {
      key: 'videos',
      label: (
        <span>
          <VideoCameraOutlined />
          视频库 ({videosTotal})
        </span>
      ),
      children: loading ? (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" />
        </div>
      ) : videos.length === 0 ? (
        <Empty description="暂无视频" />
      ) : (
        renderVideos()
      )
    }
  ];

  return (
    <>
      <Modal
        title="📚 我的资源库"
        open={open}
        onCancel={onClose}
        footer={null}
        width={1200}
        style={{ top: 20 }}
        styles={{ body: { padding: '24px', maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' } }}
      >
        {/* 搜索和筛选栏 */}
        <div style={{ marginBottom: 24 }}>
          <Space size="large">
            <Search
              placeholder="搜索内容..."
              allowClear
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
              prefix={<SearchOutlined />}
            />
            
            {activeTab !== 'prompts' && (
              <Select
                placeholder="筛选模型"
                allowClear
                value={modelFilter}
                onChange={setModelFilter}
                style={{ width: 200 }}
              >
                <Option value="wanx">通义万相</Option>
                <Option value="qwen">通义千问</Option>
                <Option value="google-veo">Google Veo</Option>
                <Option value="volc">火山引擎</Option>
              </Select>
            )}
            
            {activeTab === 'videos' && (
              <Select
                placeholder="Google Veo筛选"
                value={googleVeoOnly}
                onChange={setGoogleVeoOnly}
                style={{ width: 200 }}
              >
                <Option value={false}>全部视频</Option>
                <Option value={true}>仅Google Veo</Option>
              </Select>
            )}
          </Space>
        </div>
        
        {/* Tab内容 */}
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
        />
      </Modal>
      
      {/* 预览弹窗 */}
      <Modal
        title={
          previewContent?.optimized_prompt ? '提示词详情' :
          previewContent?.image_url ? '图片预览' : '视频预览'
        }
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>,
          previewContent?.optimized_prompt && (
            <Button 
              key="copy" 
              type="primary"
              onClick={() => handleCopyPrompt(previewContent.optimized_prompt)}
            >
              复制优化后的提示词
            </Button>
          )
        ]}
        width={800}
      >
        {previewContent?.optimized_prompt && (
          <div>
            {previewContent.original_prompt && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>原始提示词：</Text>
                <Paragraph>{previewContent.original_prompt}</Paragraph>
              </div>
            )}
            <div style={{ marginBottom: 16 }}>
              <Text strong>优化后的提示词：</Text>
              <Paragraph copyable>{previewContent.optimized_prompt}</Paragraph>
            </div>
            <div>
              {previewContent.optimization_model && (
                <Tag color="blue">{previewContent.optimization_model}</Tag>
              )}
              {previewContent.scene_type && (
                <Tag>{previewContent.scene_type}</Tag>
              )}
              <Text type="secondary" style={{ marginLeft: 16 }}>
                {new Date(previewContent.created_at).toLocaleString('zh-CN')}
              </Text>
            </div>
          </div>
        )}
        
        {previewContent?.image_url && (
          <div>
            <Image src={previewContent.image_url} alt="Preview" style={{ width: '100%' }} />
            <div style={{ marginTop: 16 }}>
              <Paragraph>{previewContent.prompt}</Paragraph>
              <div>
                {previewContent.model && <Tag color="blue">{previewContent.model}</Tag>}
                {previewContent.resolution && <Tag>{previewContent.resolution}</Tag>}
                {previewContent.width && previewContent.height && (
                  <Tag>{previewContent.width} × {previewContent.height}</Tag>
                )}
              </div>
            </div>
          </div>
        )}
        
        {previewContent?.video_url && (
          <div>
            <video 
              src={previewContent.video_url} 
              controls 
              style={{ width: '100%' }}
            />
            <div style={{ marginTop: 16 }}>
              <Paragraph>{previewContent.prompt}</Paragraph>
              <div>
                {previewContent.model && <Tag color="blue">{previewContent.model}</Tag>}
                {previewContent.is_google_veo && <Tag color="gold">Google Veo</Tag>}
                {previewContent.duration && <Tag>{previewContent.duration}秒</Tag>}
                {previewContent.resolution && <Tag>{previewContent.resolution}</Tag>}
                {previewContent.aspect_ratio && <Tag>{previewContent.aspect_ratio}</Tag>}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
};

export default UserLibraryModal;

