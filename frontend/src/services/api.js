/**
 * API服务
 * 封装所有后端API调用
 */

import axios from 'axios';

// API基础URL
const resolveDefaultBaseUrl = () => {
  if (import.meta.env.MODE === 'development') {
    return 'http://localhost:8000';
  }

  if (typeof window !== 'undefined' && window.location?.origin) {
    return window.location.origin;
  }

  return 'http://localhost:8000';
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || resolveDefaultBaseUrl();

// 导出API_BASE_URL供其他模块使用（用于fetch等场景）
export { API_BASE_URL };

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 1200000, // 20分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('[API] 请求:', config.method.toUpperCase(), config.url);
    
    // 添加Token到请求头
    // Zustand persist存储在'auth-storage'键下
    let token = null;
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const authData = JSON.parse(authStorage);
        token = authData.state?.token || null;
      }
    } catch (e) {
      console.error('[API] 解析auth-storage失败:', e);
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    console.error('[API] 请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('[API] 响应:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('[API] 响应错误:', error.response?.data || error.message);
    
    // 统一错误处理
    const errorMessage = error.response?.data?.detail?.message 
      || error.response?.data?.message 
      || error.message 
      || '请求失败';
    
    const errorDetail = error.response?.data?.detail?.detail 
      || error.response?.data?.detail 
      || '';
    
    throw new Error(`${errorMessage}${errorDetail ? ': ' + errorDetail : ''}`);
  }
);

/**
 * 文生图API
 */
export const textToImageAPI = {
  /**
   * 获取模型列表
   */
  getModels: async () => {
    const response = await apiClient.get('/api/text-to-image/models');
    return response.data;
  },
  
  /**
   * 优化提示词
   * @param {string} prompt - 原始提示词
   * @param {string} model - 优化模型 (qwen-plus | deepseek-v3)
   * @param {string} language - 输出语言 (en | zh)
   */
  optimizePrompt: async (prompt, model = 'qwen-plus', language = 'en') => {
    const response = await apiClient.post('/api/text-to-image/optimize-prompt', {
      prompt,
      model,
      language
    });
    return response.data;
  },
  
  /**
   * 生成图片
   * @param {Object} params - 生成参数
   * @param {string} params.prompt - 提示词
   * @param {string} params.model - 生成模型
   * @param {string} params.size - 图片尺寸
   * @param {number} params.num_images - 生成数量
   * @param {string[]} params.reference_image_urls - 参考图URL列表
   * @param {string} params.style - 风格参数
   */
  generateImage: async ({
    prompt,
    model = 'volc-jimeng',
    size = '1024x1024',
    num_images = 1,
    reference_image_urls = null,
    style = null
  }) => {
    const response = await apiClient.post('/api/text-to-image/generate', {
      prompt,
      model,
      size,
      num_images,
      reference_image_urls,
      style
    });
    return response.data;
  },
  
  /**
   * 上传参考图
   * @param {File} file - 图片文件
   */
  uploadReferenceImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(
      '/api/text-to-image/upload-reference',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  },
  
  /**
   * 健康检查
   */
  healthCheck: async () => {
    const response = await apiClient.get('/api/text-to-image/health');
    return response.data;
  }
};

/**
 * 文件上传API
 */
export const fileUploadAPI = {
  /**
   * 上传文件到OSS
   * @param {File} file - 文件对象
   * @param {string} category - 文件类别 (images/videos/references/uploads)
   */
  uploadFile: async (file, category = 'uploads') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    
    const response = await apiClient.post('/api/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  
  /**
   * 上传参考图（便捷接口）
   * @param {File} file - 图片文件
   */
  uploadReferenceImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(
      '/api/files/upload/reference',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  },
  
  /**
   * 列举文件
   * @param {string} prefix - 路径前缀
   * @param {number} maxKeys - 最大返回数量
   */
  listFiles: async (prefix = '', maxKeys = 100) => {
    const response = await apiClient.get('/api/files/list', {
      params: { prefix, max_keys: maxKeys }
    });
    return response.data;
  },
  
  /**
   * 删除文件
   * @param {string} objectKey - OSS对象键
   */
  deleteFile: async (objectKey) => {
    const response = await apiClient.delete(`/api/files/${objectKey}`);
    return response.data;
  },
  
  /**
   * OSS健康检查
   */
  healthCheck: async () => {
    const response = await apiClient.get('/api/files/health');
    return response.data;
  },
  
  /**
   * 上传视频（便捷接口，支持进度回调）
   * @param {FormData} formData - 包含视频文件的FormData
   * @param {Object} config - axios配置（如onUploadProgress）
   */
  uploadVideo: async (formData, config = {}) => {
    // 从formData中获取file
    const file = formData.get('file');
    
    // 创建新的FormData
    const newFormData = new FormData();
    newFormData.append('file', file);
    newFormData.append('category', 'videos');
    
    const response = await apiClient.post('/api/files/upload', newFormData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    });
    return response.data;
  }
};

/**
 * 图生视频API
 */
export const imageToVideoAPI = {
  /**
   * 分析图片生成视频描述
   * @param {string} imageBase64 - 图片Base64编码 (格式: data:image/{type};base64,{data})
   * @param {boolean} enableThinking - 是否开启思考模式
   */
  analyzeImage: async (imageBase64, enableThinking = true) => {
    const response = await apiClient.post('/api/image-to-video/analyze-image', {
      image_base64: imageBase64,
      enable_thinking: enableThinking
    });
    return response.data;
  },
  
  /**
   * 生成视频
   * @param {Object} params - 生成参数
   * @param {string} params.model - 模型 (volc-t2v | volc-i2v-first | volc-i2v-first-tail | wanx-kf2v-flash | wanx-kf2v-plus)
   * @param {string} params.first_frame_base64 - 首帧图片Base64
   * @param {string} params.last_frame_base64 - 尾帧图片Base64 (可选)
   * @param {string} params.prompt - 视频描述提示词
   * @param {number} params.duration - 时长(秒) (5 | 10)
   * @param {string} params.resolution - 分辨率 (480P | 720P | 1080P)
   * @param {string} params.aspect_ratio - 长宽比 (16:9 | 4:3 | 1:1 | 3:4 | 9:16 | 21:9)，仅文生视频使用
   */
  generateVideo: async ({
    model = 'volc-i2v-first',
    first_frame_base64,
    last_frame_base64 = null,
    prompt,
    duration = 5,
    resolution = '720P',
    aspect_ratio = '16:9'
  }) => {
    const response = await apiClient.post('/api/image-to-video/generate', {
      model,
      first_frame_base64,
      last_frame_base64,
      prompt,
      duration,
      resolution,
      aspect_ratio
    });
    return response.data;
  }
};

/**
 * 原有API（保持兼容）
 */
export const api = {
  /**
   * 生成图片提示词
   */
  generateImagePrompts: async (idea) => {
    const response = await apiClient.post('/api/generate-image-prompts', {
      idea
    });
    return response.data;
  },
  
  /**
   * 生成图片
   */
  generateImages: async (prompt) => {
    const response = await apiClient.post('/api/generate-images', {
      prompt
    });
    return response.data;
  },
  
  /**
   * 优化视频提示词
   */
  optimiseVideoPrompt: async (prompt) => {
    const response = await apiClient.post('/api/optimise-video-prompt', {
      prompt
    });
    return response.data;
  },
  
  /**
   * 生成视频
   */
  generateVideo: async (imageUrl, prompt) => {
    const response = await apiClient.post('/api/generate-video', {
      image_url: imageUrl,
      prompt
    });
    return response.data;
  },
  
  /**
   * 健康检查
   */
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  }
};

/**
 * 视频扩展API
 */
export const videoExtensionAPI = {
  /**
   * 获取模型列表
   */
  getModels: async () => {
    const response = await apiClient.get('/api/video-extension/models');
    return response.data;
  },
  
  /**
   * 扩展视频
   * @param {Object} params - 扩展参数
   * @param {string} params.video_url - 原始视频OSS URL
   * @param {string} params.prompt - 扩展描述提示词
   * @param {string} params.model - 模型 (google-veo-3.1)
   * @param {string} params.aspect_ratio - 长宽比 (16:9 | 9:16)
   * @param {string} params.negative_prompt - 反向提示词（可选）
   */
  extendVideo: async ({
    video_url,
    prompt,
    model = 'google-veo-3.1',
    aspect_ratio = '16:9',
    negative_prompt = null
  }) => {
    const response = await apiClient.post('/api/video-extension/extend', {
      video_url,
      prompt,
      model,
      aspect_ratio,
      negative_prompt
    });
    return response.data;
  }
};

// ========== 认证API ==========
export const authAPI = {
  /**
   * 用户注册
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise<Object>} 用户信息
   */
  register: async (username, password) => {
    const response = await apiClient.post('/api/auth/register', {
      username,
      password
    });
    return response.data;
  },
  
  /**
   * 用户登录
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise<Object>} { access_token, token_type }
   */
  login: async (username, password) => {
    const response = await apiClient.post('/api/auth/login', {
      username,
      password
    });
    return response.data;
  },
  
  /**
   * 获取当前用户信息
   * @param {string} token - JWT Token
   * @returns {Promise<Object>} 用户信息
   */
  getCurrentUser: async (token) => {
    const response = await apiClient.get('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  /**
   * 用户登出
   * @param {string} token - JWT Token
   * @returns {Promise<Object>} 登出结果
   */
  logout: async (token) => {
    const response = await apiClient.post('/api/auth/logout', {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  }
};

/**
 * 资源库API
 */
export const libraryAPI = {
  /**
   * 获取各类内容总数
   * @returns {Promise<Object>} 包含各类数量的对象: {prompts: number, images: number, videos: number}
   */
  getCounts: async () => {
    const response = await apiClient.get('/api/library/counts');
    return response.data;
  },
  
  /**
   * 获取提示词历史
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.search - 搜索关键词
   * @returns {Promise<Object>} 提示词列表
   */
  getPrompts: async ({ page = 1, limit = 20, search } = {}) => {
    const params = { page, limit };
    if (search) params.search = search;
    
    const response = await apiClient.get('/api/library/prompts', { params });
    return response.data;
  },
  
  /**
   * 获取图片库
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.search - 搜索关键词
   * @param {string} params.model - 筛选模型
   * @returns {Promise<Object>} 图片列表
   */
  getImages: async ({ page = 1, limit = 20, search, model } = {}) => {
    const params = { page, limit };
    if (search) params.search = search;
    if (model) params.model = model;
    
    const response = await apiClient.get('/api/library/images', { params });
    return response.data;
  },
  
  /**
   * 获取视频库
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.search - 搜索关键词
   * @param {string} params.model - 筛选模型
   * @param {boolean} params.google_veo_only - 仅显示Google Veo视频
   * @returns {Promise<Object>} 视频列表
   */
  getVideos: async ({ page = 1, limit = 20, search, model, google_veo_only = false } = {}) => {
    const params = { page, limit, google_veo_only };
    if (search) params.search = search;
    if (model) params.model = model;
    
    const response = await apiClient.get('/api/library/videos', { params });
    return response.data;
  }
};

export default apiClient;

