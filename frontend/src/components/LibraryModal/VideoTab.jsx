/**
 * 视频库Tab
 * 
 * 显示用户生成的视频库（网格布局，支持Google Veo标记）
 */

import React, { useEffect, useState } from 'react';
import useLibraryStore from '../../store/libraryStore';

function VideoTab({ onSelect, googleVeoOnlyMode = false }) {
  const {
    videos,
    videosTotal,
    videosPage,
    videosLimit,
    videosLoading,
    searchText,
    modelFilter,
    googleVeoOnly,
    setSearchText,
    setModelFilter,
    setGoogleVeoOnly,
    fetchVideos,
    search,
  } = useLibraryStore();
  
  const [localSearch, setLocalSearch] = useState(searchText);
  const [localModelFilter, setLocalModelFilter] = useState(modelFilter || '');
  
  useEffect(() => {
    // 如果传入googleVeoOnlyMode，自动设置筛选
    if (googleVeoOnlyMode) {
      setGoogleVeoOnly(true);
      // 重新加载视频列表
      fetchVideos(1);
    } else if (videos.length === 0) {
      // 初次加载
      fetchVideos(1);
    }
  }, [googleVeoOnlyMode]);
  
  const handleSearchChange = (e) => {
    setLocalSearch(e.target.value);
  };
  
  const handleModelFilterChange = (e) => {
    const value = e.target.value;
    setLocalModelFilter(value);
    setModelFilter(value || null);
    search();
  };
  
  const handleGoogleVeoToggle = (e) => {
    setGoogleVeoOnly(e.target.checked);
    search();
  };
  
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearchText(localSearch);
    search();
  };
  
  const handleSelectVideo = (video) => {
    if (onSelect) {
      onSelect({
        type: 'video',
        data: video,
      });
    }
  };
  
  const handlePageChange = (newPage) => {
    fetchVideos(newPage);
  };
  
  const totalPages = Math.ceil(videosTotal / videosLimit);
  
  return (
    <div className="library-tab-content">
      {/* 搜索和筛选栏 */}
      <div className="library-filters">
        <form className="library-search-bar" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            placeholder="搜索提示词..."
            value={localSearch}
            onChange={handleSearchChange}
            className="library-search-input"
          />
          <button type="submit" className="library-search-btn">
            🔍 搜索
          </button>
        </form>
        
        <select
          value={localModelFilter}
          onChange={handleModelFilterChange}
          className="library-filter-select"
        >
          <option value="">全部模型</option>
          <option value="volc-t2v">火山引擎-文生视频</option>
          <option value="volc-i2v-first">火山引擎-单图首帧</option>
          <option value="volc-i2v-first-tail">火山引擎-首尾帧</option>
          <option value="wanx-kf2v-flash">通义万相-Flash</option>
          <option value="wanx-kf2v-plus">通义万相-Plus</option>
          <option value="google-veo-t2v">Google Veo-文生视频</option>
          <option value="google-veo-i2v-first">Google Veo-单图首帧</option>
          <option value="google-veo-i2v-first-tail">Google Veo-首尾帧</option>
        </select>
        
        <label className="library-checkbox-label">
          <input
            type="checkbox"
            checked={googleVeoOnly}
            onChange={handleGoogleVeoToggle}
            disabled={googleVeoOnlyMode}
          />
          仅显示 Google Veo 视频
        </label>
      </div>
      
      {/* Google Veo提示 */}
      {googleVeoOnlyMode && (
        <div className="library-hint">
          ℹ️ Google Veo 视频延长仅支持延长由其生成的视频
        </div>
      )}
      
      {/* 加载状态 */}
      {videosLoading && (
        <div className="library-loading">
          <div className="loading-spinner"></div>
          <p>加载中...</p>
        </div>
      )}
      
      {/* 空状态 */}
      {!videosLoading && videos.length === 0 && (
        <div className="library-empty">
          <p>暂无视频</p>
          <p className="library-empty-hint">
            {googleVeoOnly
              ? '您还没有使用 Google Veo 生成过视频'
              : '开始使用图生视频功能，生成的视频会自动保存到这里'}
          </p>
        </div>
      )}
      
      {/* 视频网格 */}
      {!videosLoading && videos.length > 0 && (
        <>
          <div className="video-grid">
            {videos.map((video) => (
              <div
                key={video.id}
                className="video-grid-item"
                onClick={() => handleSelectVideo(video)}
              >
                <div className="video-wrapper">
                  <video
                    src={video.video_url}
                    className="video-thumbnail"
                    preload="metadata"
                    muted
                    onMouseEnter={(e) => e.target.play()}
                    onMouseLeave={(e) => {
                      e.target.pause();
                      e.target.currentTime = 0;
                    }}
                  />
                  <div className="video-overlay">
                    <div className="video-info">
                      <span className="video-model-badge">{video.model}</span>
                      {video.is_google_veo && (
                        <span className="video-google-badge">Google Veo</span>
                      )}
                      {video.duration && (
                        <span className="video-duration-badge">{video.duration}s</span>
                      )}
                      {video.resolution && (
                        <span className="video-resolution-badge">{video.resolution}</span>
                      )}
                    </div>
                  </div>
                </div>
                {video.prompt && (
                  <div className="video-prompt" title={video.prompt}>
                    {video.prompt.length > 50
                      ? `${video.prompt.substring(0, 50)}...`
                      : video.prompt}
                  </div>
                )}
                <div className="video-meta">
                  <span className="video-type">{video.generation_type}</span>
                  <span className="video-date">
                    {new Date(video.created_at).toLocaleDateString('zh-CN')}
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          {/* 分页 */}
          {totalPages > 1 && (
            <div className="library-pagination">
              <button
                className="pagination-btn"
                disabled={videosPage === 1}
                onClick={() => handlePageChange(videosPage - 1)}
              >
                上一页
              </button>
              <span className="pagination-info">
                第 {videosPage} / {totalPages} 页（共 {videosTotal} 个）
              </span>
              <button
                className="pagination-btn"
                disabled={videosPage === totalPages}
                onClick={() => handlePageChange(videosPage + 1)}
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default VideoTab;

