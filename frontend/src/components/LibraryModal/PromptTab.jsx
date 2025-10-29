/**
 * 提示词历史Tab
 * 
 * 显示用户的提示词优化历史记录
 */

import React, { useEffect, useState } from 'react';
import useLibraryStore from '../../store/libraryStore';

function PromptTab({ onSelect }) {
  const {
    prompts,
    promptsTotal,
    promptsPage,
    promptsLimit,
    promptsLoading,
    searchText,
    setSearchText,
    fetchPrompts,
    search,
  } = useLibraryStore();
  
  const [localSearch, setLocalSearch] = useState(searchText);
  
  useEffect(() => {
    // 初次加载
    if (prompts.length === 0) {
      fetchPrompts(1);
    }
  }, []);
  
  const handleSearchChange = (e) => {
    setLocalSearch(e.target.value);
  };
  
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearchText(localSearch);
    search();
  };
  
  const handleSelectPrompt = (prompt) => {
    if (onSelect) {
      onSelect({
        type: 'prompt',
        data: prompt,
      });
    }
  };
  
  const handlePageChange = (newPage) => {
    fetchPrompts(newPage);
  };
  
  const totalPages = Math.ceil(promptsTotal / promptsLimit);
  
  return (
    <div className="library-tab-content">
      {/* 搜索栏 */}
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
      
      {/* 加载状态 */}
      {promptsLoading && (
        <div className="library-loading">
          <div className="loading-spinner"></div>
          <p>加载中...</p>
        </div>
      )}
      
      {/* 空状态 */}
      {!promptsLoading && prompts.length === 0 && (
        <div className="library-empty">
          <p>暂无提示词历史</p>
          <p className="library-empty-hint">开始使用提示词优化功能，这里会自动保存您的优化记录</p>
        </div>
      )}
      
      {/* 提示词列表 */}
      {!promptsLoading && prompts.length > 0 && (
        <>
          <div className="prompt-list">
            {prompts.map((prompt) => (
              <div
                key={prompt.id}
                className="prompt-item"
                onClick={() => handleSelectPrompt(prompt)}
              >
                <div className="prompt-item-header">
                  <span className="prompt-model-badge">
                    {prompt.optimization_model || '未知模型'}
                  </span>
                  <span className="prompt-scene-badge">
                    {prompt.scene_type || '未分类'}
                  </span>
                  <span className="prompt-date">
                    {new Date(prompt.created_at).toLocaleString('zh-CN')}
                  </span>
                </div>
                
                {prompt.original_prompt && (
                  <div className="prompt-item-section">
                    <div className="prompt-label">原始提示词：</div>
                    <div className="prompt-text">{prompt.original_prompt}</div>
                  </div>
                )}
                
                <div className="prompt-item-section">
                  <div className="prompt-label">优化后提示词：</div>
                  <div className="prompt-text optimized">{prompt.optimized_prompt}</div>
                </div>
              </div>
            ))}
          </div>
          
          {/* 分页 */}
          {totalPages > 1 && (
            <div className="library-pagination">
              <button
                className="pagination-btn"
                disabled={promptsPage === 1}
                onClick={() => handlePageChange(promptsPage - 1)}
              >
                上一页
              </button>
              <span className="pagination-info">
                第 {promptsPage} / {totalPages} 页（共 {promptsTotal} 条）
              </span>
              <button
                className="pagination-btn"
                disabled={promptsPage === totalPages}
                onClick={() => handlePageChange(promptsPage + 1)}
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

export default PromptTab;

