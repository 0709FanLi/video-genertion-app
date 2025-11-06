/**
 * 资源库状态管理
 * 
 * 管理用户的提示词历史、图片库、视频库的查询和状态
 */

import { create } from 'zustand';
import { API_BASE_URL } from '../services/api';

const useLibraryStore = create((set, get) => ({
  // ========== 状态 ==========
  
  // 当前Tab
  currentTab: 'prompt', // 'prompt' | 'image' | 'video'
  
  // 搜索和筛选
  searchText: '',
  modelFilter: null,
  googleVeoOnly: false,
  
  // 提示词历史
  prompts: [],
  promptsTotal: 0,
  promptsPage: 1,
  promptsLimit: 20,
  promptsLoading: false,
  
  // 图片库
  images: [],
  imagesTotal: 0,
  imagesPage: 1,
  imagesLimit: 20,
  imagesLoading: false,
  
  // 视频库
  videos: [],
  videosTotal: 0,
  videosPage: 1,
  videosLimit: 20,
  videosLoading: false,
  
  // 错误状态
  error: null,
  
  // ========== Actions ==========
  
  /**
   * 设置当前Tab
   */
  setCurrentTab: (tab) => {
    set({ currentTab: tab });
    
    // 切换Tab时自动加载数据
    const state = get();
    switch (tab) {
      case 'prompt':
        if (state.prompts.length === 0) {
          get().fetchPrompts();
        }
        break;
      case 'image':
        if (state.images.length === 0) {
          get().fetchImages();
        }
        break;
      case 'video':
        if (state.videos.length === 0) {
          get().fetchVideos();
        }
        break;
    }
  },
  
  /**
   * 设置搜索文本
   */
  setSearchText: (text) => {
    set({ searchText: text });
  },
  
  /**
   * 设置模型筛选
   */
  setModelFilter: (model) => {
    set({ modelFilter: model });
  },
  
  /**
   * 设置Google Veo筛选
   */
  setGoogleVeoOnly: (value) => {
    set({ googleVeoOnly: value });
  },
  
  /**
   * 获取提示词历史
   */
  fetchPrompts: async (page = null) => {
    const state = get();
    const currentPage = page !== null ? page : state.promptsPage;
    
    set({ promptsLoading: true, error: null });
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('未登录');
      }
      
      const params = new URLSearchParams({
        page: currentPage,
        limit: state.promptsLimit,
      });
      
      if (state.searchText) {
        params.append('search', state.searchText);
      }
      
      const response = await fetch(
        `${API_BASE_URL}/api/library/prompts?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('获取提示词历史失败');
      }
      
      const data = await response.json();
      
      set({
        prompts: data.prompts,
        promptsTotal: data.total,
        promptsPage: data.page,
        promptsLoading: false,
      });
    } catch (error) {
      console.error('获取提示词历史失败:', error);
      set({
        error: error.message,
        promptsLoading: false,
      });
    }
  },
  
  /**
   * 获取图片库
   */
  fetchImages: async (page = null) => {
    const state = get();
    const currentPage = page !== null ? page : state.imagesPage;
    
    set({ imagesLoading: true, error: null });
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('未登录');
      }
      
      const params = new URLSearchParams({
        page: currentPage,
        limit: state.imagesLimit,
      });
      
      if (state.searchText) {
        params.append('search', state.searchText);
      }
      
      if (state.modelFilter) {
        params.append('model', state.modelFilter);
      }
      
      const response = await fetch(
        `${API_BASE_URL}/api/library/images?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('获取图片库失败');
      }
      
      const data = await response.json();
      
      set({
        images: data.images,
        imagesTotal: data.total,
        imagesPage: data.page,
        imagesLoading: false,
      });
    } catch (error) {
      console.error('获取图片库失败:', error);
      set({
        error: error.message,
        imagesLoading: false,
      });
    }
  },
  
  /**
   * 获取视频库
   */
  fetchVideos: async (page = null) => {
    const state = get();
    const currentPage = page !== null ? page : state.videosPage;
    
    set({ videosLoading: true, error: null });
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('未登录');
      }
      
      const params = new URLSearchParams({
        page: currentPage,
        limit: state.videosLimit,
      });
      
      if (state.searchText) {
        params.append('search', state.searchText);
      }
      
      if (state.modelFilter) {
        params.append('model', state.modelFilter);
      }
      
      if (state.googleVeoOnly) {
        params.append('google_veo_only', 'true');
      }
      
      const response = await fetch(
        `${API_BASE_URL}/api/library/videos?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('获取视频库失败');
      }
      
      const data = await response.json();
      
      set({
        videos: data.videos,
        videosTotal: data.total,
        videosPage: data.page,
        videosLoading: false,
      });
    } catch (error) {
      console.error('获取视频库失败:', error);
      set({
        error: error.message,
        videosLoading: false,
      });
    }
  },
  
  /**
   * 搜索（应用搜索并重置页码）
   */
  search: () => {
    const state = get();
    
    switch (state.currentTab) {
      case 'prompt':
        set({ promptsPage: 1 });
        get().fetchPrompts(1);
        break;
      case 'image':
        set({ imagesPage: 1 });
        get().fetchImages(1);
        break;
      case 'video':
        set({ videosPage: 1 });
        get().fetchVideos(1);
        break;
    }
  },
  
  /**
   * 重置所有筛选和搜索
   */
  resetFilters: () => {
    set({
      searchText: '',
      modelFilter: null,
      googleVeoOnly: false,
    });
    
    // 重新加载当前Tab数据
    const state = get();
    get().setCurrentTab(state.currentTab);
  },
  
  /**
   * 清空所有数据
   */
  clearAll: () => {
    set({
      prompts: [],
      promptsTotal: 0,
      promptsPage: 1,
      images: [],
      imagesTotal: 0,
      imagesPage: 1,
      videos: [],
      videosTotal: 0,
      videosPage: 1,
      searchText: '',
      modelFilter: null,
      googleVeoOnly: false,
      error: null,
    });
  },
}));

export default useLibraryStore;

