/**
 * API服务
 * 封装所有后端API调用
 */

import axios from 'axios';

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('[API] 请求:', config.method.toUpperCase(), config.url);
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

export default apiClient;

