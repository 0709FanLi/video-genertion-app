/**
 * 视频扩展状态管理
 * 使用Zustand进行轻量级状态管理
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

/**
 * 视频扩展状态存储
 */
const useVideoExtensionStore = create(
  devtools(
    (set, get) => ({
      // ==================== 状态 ====================
      
      // 原始视频
      originalVideo: null, // { url, file, name, size, duration }
      
      // 扩展提示词相关
      extensionPrompt: '', // 用户输入的扩展提示词
      optimizedPrompt: '', // AI优化后的提示词
      useOptimizedPrompt: true, // 是否使用优化后的提示词
      
      // 模型选择
      selectedModel: 'google-veo-3.1', // 当前选择的视频扩展模型
      selectedPromptModel: 'qwen-plus', // 提示词优化模型
      
      // 参数设置
      aspectRatio: '16:9', // 视频长宽比
      negativePrompt: '', // 反向提示词（可选）
      
      // 生成结果
      extendedVideo: null, // 扩展后的视频 { url, duration, resolution, aspect_ratio }
      
      // 模型配置
      videoExtensionModels: {}, // 可用的视频扩展模型
      promptOptimizationModels: {}, // 可用的提示词优化模型
      
      // UI状态
      isOptimizing: false, // 是否正在优化提示词
      isExtending: false, // 是否正在扩展视频
      isLoadingModels: false, // 是否正在加载模型列表
      uploadProgress: 0, // 视频上传进度
      
      // 错误处理
      error: null, // 错误信息
      
      // ==================== Actions ====================
      
      /**
       * 设置原始视频
       */
      setOriginalVideo: (video) => set({ originalVideo: video }),
      
      /**
       * 清除原始视频
       */
      clearOriginalVideo: () => set({ originalVideo: null }),
      
      /**
       * 设置扩展提示词
       */
      setExtensionPrompt: (prompt) => set({ extensionPrompt: prompt }),
      
      /**
       * 设置优化后的提示词
       */
      setOptimizedPrompt: (prompt) => set({ optimizedPrompt: prompt }),
      
      /**
       * 切换是否使用优化提示词
       */
      toggleUseOptimizedPrompt: () => set((state) => ({
        useOptimizedPrompt: !state.useOptimizedPrompt
      })),
      
      /**
       * 获取当前使用的提示词
       */
      getCurrentPrompt: () => {
        const state = get();
        if (state.useOptimizedPrompt && state.optimizedPrompt.trim()) {
          return state.optimizedPrompt;
        }
        return state.extensionPrompt;
      },
      
      /**
       * 设置视频扩展模型
       */
      selectExtensionModel: (model) => set({ selectedModel: model }),
      
      /**
       * 设置提示词优化模型
       */
      selectPromptModel: (model) => set({ selectedPromptModel: model }),
      
      /**
       * 设置长宽比
       */
      setAspectRatio: (ratio) => set({ aspectRatio: ratio }),
      
      /**
       * 设置反向提示词
       */
      setNegativePrompt: (prompt) => set({ negativePrompt: prompt }),
      
      /**
       * 设置扩展后的视频
       */
      setExtendedVideo: (video) => set({ extendedVideo: video }),
      
      /**
       * 设置模型列表
       */
      setModels: (extensionModels, promptModels) => set({
        videoExtensionModels: extensionModels,
        promptOptimizationModels: promptModels
      }),
      
      /**
       * 设置优化中状态
       */
      setOptimizing: (isOptimizing) => set({ isOptimizing }),
      
      /**
       * 设置扩展中状态
       */
      setExtending: (isExtending) => set({ isExtending }),
      
      /**
       * 设置加载模型状态
       */
      setLoadingModels: (isLoading) => set({ isLoadingModels: isLoading }),
      
      /**
       * 设置上传进度
       */
      setUploadProgress: (progress) => set({ uploadProgress: progress }),
      
      /**
       * 设置错误信息
       */
      setError: (error) => set({ error }),
      
      /**
       * 清除错误信息
       */
      clearError: () => set({ error: null }),
      
      /**
       * 重置所有状态
       */
      reset: () => set({
        originalVideo: null,
        extensionPrompt: '',
        optimizedPrompt: '',
        useOptimizedPrompt: true,
        negativePrompt: '',
        extendedVideo: null,
        isOptimizing: false,
        isExtending: false,
        uploadProgress: 0,
        error: null
      }),
      
      /**
       * 验证是否可以开始扩展
       */
      canStartExtension: () => {
        const state = get();
        return (
          state.originalVideo !== null &&
          (state.extensionPrompt.trim() || state.optimizedPrompt.trim()) &&
          !state.isExtending
        );
      }
    }),
    {
      name: 'video-extension-store', // Redux DevTools中显示的名称
    }
  )
);

export default useVideoExtensionStore;

