/**
 * 资源库弹窗 - 主组件
 * 
 * 提供三个Tab切换：提示词历史、图片库、视频库
 */

import React, { useEffect } from 'react';
import useLibraryStore from '../../store/libraryStore';
import PromptTab from './PromptTab';
import ImageTab from './ImageTab';
import VideoTab from './VideoTab';
import './styles.css';

function LibraryModal({ isOpen, onClose, onSelect, selectMode = 'prompt', googleVeoOnlyMode = false }) {
  const { currentTab, setCurrentTab, clearAll } = useLibraryStore();
  
  useEffect(() => {
    if (isOpen) {
      // 打开时根据selectMode设置默认Tab
      setCurrentTab(selectMode);
    } else {
      // 关闭时清空数据（可选，节省内存）
      // clearAll();
    }
  }, [isOpen, selectMode, setCurrentTab]);
  
  if (!isOpen) return null;
  
  const handleTabClick = (tab) => {
    setCurrentTab(tab);
  };
  
  return (
    <div className="library-modal-overlay" onClick={onClose}>
      <div className="library-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* 头部 */}
        <div className="library-modal-header">
          <h2 className="library-modal-title">我的资源库</h2>
          <button className="library-modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>
        
        {/* Tab切换 */}
        <div className="library-modal-tabs">
          <button
            className={`library-tab-btn ${currentTab === 'prompt' ? 'active' : ''}`}
            onClick={() => handleTabClick('prompt')}
          >
            📝 提示词历史
          </button>
          <button
            className={`library-tab-btn ${currentTab === 'image' ? 'active' : ''}`}
            onClick={() => handleTabClick('image')}
          >
            🖼️ 图片库
          </button>
          <button
            className={`library-tab-btn ${currentTab === 'video' ? 'active' : ''}`}
            onClick={() => handleTabClick('video')}
          >
            🎬 视频库
          </button>
        </div>
        
        {/* Tab内容 */}
        <div className="library-modal-content">
          {currentTab === 'prompt' && <PromptTab onSelect={onSelect} />}
          {currentTab === 'image' && <ImageTab onSelect={onSelect} />}
          {currentTab === 'video' && <VideoTab onSelect={onSelect} googleVeoOnlyMode={googleVeoOnlyMode} />}
        </div>
      </div>
    </div>
  );
}

export default LibraryModal;

