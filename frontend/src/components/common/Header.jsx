/**
 * 页面头部组件
 */

import React, { useState } from 'react';
import { Layout, Menu, Typography, Button, Space, Tooltip } from 'antd';
import { 
  PictureOutlined, 
  VideoCameraOutlined, 
  ExpandOutlined,
  HomeOutlined,
  FolderOpenOutlined
} from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';
import UserMenu from '../UserMenu';
import UserLibraryModal from '../UserLibraryModal';
import useAuthStore from '../../store/authStore';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [isLibraryModalOpen, setIsLibraryModalOpen] = useState(false);
  
  // 导航菜单项
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页'
    },
    {
      key: '/text-to-image',
      icon: <PictureOutlined />,
      label: '文生图'
    },
    {
      key: '/image-to-video',
      icon: <VideoCameraOutlined />,
      label: '图生视频'
    },
    {
      key: '/video-extension',
      icon: <ExpandOutlined />,
      label: '视频扩展'
    }
  ];
  
  // 处理菜单点击
  const handleMenuClick = ({ key }) => {
    navigate(key);
  };
  
  return (
    <AntHeader 
      style={{ 
        display: 'flex', 
        alignItems: 'center',
        backgroundColor: '#001529',
        padding: '0 50px'
      }}
    >
      <Title 
        level={3} 
        style={{ 
          color: 'white', 
          margin: 0,
          marginRight: '50px'
        }}
      >
        🎨 AI创意生成平台0.2
      </Title>
      
      <Menu
        theme="dark"
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ 
          flex: 1, 
          minWidth: 0,
          borderBottom: 'none'
        }}
      />
      
      {/* 右侧按钮组 */}
      {isAuthenticated && (
        <Space size="middle" style={{ marginLeft: 'auto' }}>
          {/* 资源库按钮 */}
          <Tooltip title="我的资源库">
            <Button
              type="text"
              icon={<FolderOpenOutlined style={{ fontSize: '18px' }} />}
              onClick={() => setIsLibraryModalOpen(true)}
              style={{ 
                color: 'rgba(255, 255, 255, 0.65)',
                padding: '4px 15px'
              }}
            >
              资源库
            </Button>
          </Tooltip>
          
          {/* 用户菜单 */}
          <UserMenu />
        </Space>
      )}
      
      {/* 资源库弹窗 */}
      <UserLibraryModal
        open={isLibraryModalOpen}
        onClose={() => setIsLibraryModalOpen(false)}
      />
    </AntHeader>
  );
};

export default Header;

