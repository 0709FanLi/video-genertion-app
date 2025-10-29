/**
 * 图片库Tab
 * 
 * 显示用户生成的图片库（网格布局）
 */

import React, { useEffect, useState } from 'react';
import useLibraryStore from '../../store/libraryStore';

function ImageTab({ onSelect }) {
  const {
    images,
    imagesTotal,
    imagesPage,
    imagesLimit,
    imagesLoading,
    searchText,
    modelFilter,
    setSearchText,
    setModelFilter,
    fetchImages,
    search,
  } = useLibraryStore();
  
  const [localSearch, setLocalSearch] = useState(searchText);
  const [localModelFilter, setLocalModelFilter] = useState(modelFilter || '');
  
  useEffect(() => {
    // 初次加载
    if (images.length === 0) {
      fetchImages(1);
    }
  }, []);
  
  const handleSearchChange = (e) => {
    setLocalSearch(e.target.value);
  };
  
  const handleModelFilterChange = (e) => {
    const value = e.target.value;
    setLocalModelFilter(value);
    setModelFilter(value || null);
    search();
  };
  
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearchText(localSearch);
    search();
  };
  
  const handleSelectImage = (image) => {
    if (onSelect) {
      onSelect({
        type: 'image',
        data: image,
      });
    }
  };
  
  const handlePageChange = (newPage) => {
    fetchImages(newPage);
  };
  
  const totalPages = Math.ceil(imagesTotal / imagesLimit);
  
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
          <option value="volc-jimeng">火山引擎即梦</option>
          <option value="aliyun-wanx-i2i">通义万相多图生图</option>
          <option value="aliyun-qwen-image">通义千问文生图</option>
        </select>
      </div>
      
      {/* 加载状态 */}
      {imagesLoading && (
        <div className="library-loading">
          <div className="loading-spinner"></div>
          <p>加载中...</p>
        </div>
      )}
      
      {/* 空状态 */}
      {!imagesLoading && images.length === 0 && (
        <div className="library-empty">
          <p>暂无图片</p>
          <p className="library-empty-hint">开始使用文生图功能，生成的图片会自动保存到这里</p>
        </div>
      )}
      
      {/* 图片网格 */}
      {!imagesLoading && images.length > 0 && (
        <>
          <div className="image-grid">
            {images.map((image) => (
              <div
                key={image.id}
                className="image-grid-item"
                onClick={() => handleSelectImage(image)}
              >
                <div className="image-wrapper">
                  <img
                    src={image.image_url}
                    alt={image.prompt || '生成的图片'}
                    className="image-thumbnail"
                  />
                  <div className="image-overlay">
                    <div className="image-info">
                      <span className="image-model-badge">{image.model}</span>
                      {image.resolution && (
                        <span className="image-resolution-badge">{image.resolution}</span>
                      )}
                    </div>
                  </div>
                </div>
                {image.prompt && (
                  <div className="image-prompt" title={image.prompt}>
                    {image.prompt.length > 50
                      ? `${image.prompt.substring(0, 50)}...`
                      : image.prompt}
                  </div>
                )}
                <div className="image-date">
                  {new Date(image.created_at).toLocaleDateString('zh-CN')}
                </div>
              </div>
            ))}
          </div>
          
          {/* 分页 */}
          {totalPages > 1 && (
            <div className="library-pagination">
              <button
                className="pagination-btn"
                disabled={imagesPage === 1}
                onClick={() => handlePageChange(imagesPage - 1)}
              >
                上一页
              </button>
              <span className="pagination-info">
                第 {imagesPage} / {totalPages} 页（共 {imagesTotal} 张）
              </span>
              <button
                className="pagination-btn"
                disabled={imagesPage === totalPages}
                onClick={() => handlePageChange(imagesPage + 1)}
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

export default ImageTab;

