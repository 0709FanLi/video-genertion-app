/**
 * 用户菜单组件
 * 
 * 显示在Header右上角，包含用户信息和登出按钮
 */

import React from 'react';
import { Dropdown, Button, Space, Avatar, message } from 'antd';
import { UserOutlined, LogoutOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const UserMenu = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    message.success('已退出登录');
    navigate('/login');
  };

  const items = [
    {
      key: 'username',
      label: (
        <div style={{ padding: '4px 0' }}>
          <div style={{ fontWeight: 500 }}>{user?.username}</div>
          <div style={{ fontSize: '12px', color: '#999' }}>
            ID: {user?.id}
          </div>
        </div>
      ),
      disabled: true
    },
    {
      type: 'divider'
    },
    {
      key: 'library',
      label: '我的资源库',
      icon: <FolderOpenOutlined />,
      onClick: () => {
        // TODO: 打开资源库弹窗
        message.info('资源库功能开发中...');
      }
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
      danger: true,
      onClick: handleLogout
    }
  ];

  return (
    <Dropdown
      menu={{ items }}
      trigger={['click']}
      placement="bottomRight"
    >
      <Button type="text" style={{ padding: '4px 12px' }}>
        <Space>
          <Avatar
            size="small"
            icon={<UserOutlined />}
            style={{ backgroundColor: '#1890ff' }}
          />
          <span>{user?.username}</span>
        </Space>
      </Button>
    </Dropdown>
  );
};

export default UserMenu;

