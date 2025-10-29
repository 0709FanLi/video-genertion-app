/**
 * 路由保护组件
 * 
 * 用于保护需要登录才能访问的路由
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  
  // 检查是否已登录
  const isLoggedIn = checkAuth();
  
  if (!isLoggedIn) {
    // 未登录，重定向到登录页
    console.log('[ProtectedRoute] 未登录，重定向到登录页');
    return <Navigate to="/login" replace />;
  }
  
  // 已登录，渲染子组件
  return children;
};

export default ProtectedRoute;

