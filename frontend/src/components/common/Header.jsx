/**
 * 页面头部组件
 */

import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { 
  PictureOutlined, 
  VideoCameraOutlined, 
  ExpandOutlined,
  HomeOutlined
} from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';
import UserMenu from '../UserMenu';
import useAuthStore from '../../store/authStore';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
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
        🎨 AI创意生成平台
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
      
      {/* 用户菜单 */}
      {isAuthenticated && (
        <div style={{ marginLeft: 'auto' }}>
          <UserMenu />
        </div>
      )}
    </AntHeader>
  );
};

export default Header;

