/**
 * 主应用组件
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import Header from './components/common/Header';
import Home from './components/Home';
import TextToImagePage from './components/TextToImage';
import ImageToVideoPage from './components/ImageToVideo';
import VideoExtensionPage from './components/VideoExtension';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

const App = () => {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Routes>
          {/* 公开路由 */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* 受保护的路由（需要登录） */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <>
                  <Header />
                  <Home />
                </>
              </ProtectedRoute>
            }
          />
          <Route
            path="/text-to-image"
            element={
              <ProtectedRoute>
                <>
                  <Header />
                  <TextToImagePage />
                </>
              </ProtectedRoute>
            }
          />
          <Route
            path="/image-to-video"
            element={
              <ProtectedRoute>
                <>
                  <Header />
                  <ImageToVideoPage />
                </>
              </ProtectedRoute>
            }
          />
          <Route
            path="/video-extension"
            element={
              <ProtectedRoute>
                <>
                  <Header />
                  <VideoExtensionPage />
                </>
              </ProtectedRoute>
            }
          />
          
          {/* 404重定向 */}
          <Route path="*" element={<Navigate to="/text-to-image" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
