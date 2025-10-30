/**
 * 注册页面
 */

import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const { Title, Text, Link } = Typography;

const Register = () => {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [form] = Form.useForm();

  const handleRegister = async (values) => {
    console.log('[Register] 注册表单提交:', values.username);
    
    clearError();
    
    const success = await register(values.username, values.password);
    
    if (success) {
      message.success('注册成功！请登录');
      // 注册成功后跳转到登录页面
      setTimeout(() => {
        navigate('/login');
      }, 1000);
    } else {
      message.error(error || '注册失败，请重试');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: '400px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
          borderRadius: '12px'
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 标题 */}
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              创建账号
            </Title>
            <Text type="secondary">加入AI视频创作工作流</Text>
          </div>

          {/* 注册表单 */}
          <Form
            form={form}
            name="register"
            onFinish={handleRegister}
            autoComplete="off"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
                { max: 20, message: '用户名最多20个字符' },
                {
                  pattern: /^[a-zA-Z0-9_]+$/,
                  message: '用户名只能包含字母、数字和下划线'
                }
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名（3-20个字符）"
                disabled={isLoading}
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
                { max: 20, message: '密码最多20个字符' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码（6-20个字符）"
                disabled={isLoading}
                autoComplete="new-password"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="确认密码"
                disabled={isLoading}
                autoComplete="new-password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={isLoading}
                size="large"
              >
                注册
              </Button>
            </Form.Item>
          </Form>

          {/* 登录链接 */}
          <div style={{ textAlign: 'center' }}>
            <Text>
              已有账号？{' '}
              <Link onClick={() => navigate('/login')}>
                立即登录
              </Link>
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default Register;

