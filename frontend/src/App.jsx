/**
 * 主应用组件
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Header from './components/common/Header';
import Home from './components/Home';
import TextToImagePage from './components/TextToImage';
import ImageToVideoPage from './components/ImageToVideo';
import VideoExtensionPage from './components/VideoExtension';
import './App.css';

const App = () => {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/text-to-image" element={<TextToImagePage />} />
          <Route path="/image-to-video" element={<ImageToVideoPage />} />
          <Route path="/video-extension" element={<VideoExtensionPage />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
