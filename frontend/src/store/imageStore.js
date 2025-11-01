/**
 * 图片生成状态管理
 * 使用Zustand进行轻量级状态管理
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

/**
 * 图片生成状态存储
 */
const useImageStore = create(
  devtools(
    (set, get) => ({
      // ==================== 状态 ====================
      
      // 提示词相关
      userPrompt: '', // 用户输入的原始提示词
      optimizedPrompt: '', // AI优化后的提示词
      useOptimizedPrompt: true, // 是否使用优化后的提示词（默认true）
      
      // 模型选择
      selectedImageModel: 'volc-jimeng', // 当前选择的文生图模型
      selectedPromptModel: 'qwen-plus', // 当前选择的提示词优化模型
      
      // 参考图
      referenceImages: [], // 参考图列表 { id, url, file }
      
      // 生成参数
      numImages: 1, // 生成图片数量（1-4）
      imageSize: '1024x1024', // 图片尺寸
      
      // 生成结果
      generatedImages: [], // 生成的图片列表 { id, url, prompt, model, timestamp }
      selectedImageId: null, // 当前选择的图片ID（用于图生视频）
      
      // 模型配置
      textToImageModels: {}, // 可用的文生图模型
      promptOptimizationModels: {}, // 可用的提示词优化模型
      
      // UI状态
      isOptimizing: false, // 是否正在优化提示词
      isGenerating: false, // 是否正在生成图片
      isLoadingModels: false, // 是否正在加载模型列表
      
      // 错误处理
      error: null, // 错误信息
      
      // 生成历史
      history: [], // 历史记录
      
      // ==================== Actions ====================
      
      /**
       * 设置用户提示词
       */
      setUserPrompt: (prompt) => set({ userPrompt: prompt }),
      
      /**
       * 设置优化后的提示词
       */
      setOptimizedPrompt: (prompt) => set({ optimizedPrompt: prompt }),
      
      /**
       * 切换是否使用优化提示词
       */
      toggleUseOptimizedPrompt: () => 
        set((state) => ({ useOptimizedPrompt: !state.useOptimizedPrompt })),
      
      /**
       * 选择文生图模型
       */
      selectImageModel: (model) => set({ selectedImageModel: model }),
      
      /**
       * 选择提示词优化模型
       */
      selectPromptModel: (model) => set({ selectedPromptModel: model }),
      
      /**
       * 添加参考图
       */
      addReferenceImage: (image) => 
        set((state) => ({
          referenceImages: [...state.referenceImages, {
            id: Date.now() + Math.random(),
            ...image
          }]
        })),
      
      /**
       * 删除参考图
       */
      removeReferenceImage: (imageId) => 
        set((state) => ({
          referenceImages: state.referenceImages.filter(img => img.id !== imageId)
        })),
      
      /**
       * 清空参考图
       */
      clearReferenceImages: () => set({ referenceImages: [] }),
      
      /**
       * 设置生成图片数量
       */
      setNumImages: (numImages) => set({ numImages }),
      
      /**
       * 设置图片尺寸
       */
      setImageSize: (imageSize) => set({ imageSize }),
      
      /**
       * 添加生成的图片
       */
      addGeneratedImage: (image) => 
        set((state) => ({
          generatedImages: [{
            id: Date.now() + Math.random(),
            timestamp: new Date().toISOString(),
            ...image
          }, ...state.generatedImages]
        })),
      
      /**
       * 添加多张生成的图片
       */
      addGeneratedImages: (images) => 
        set((state) => ({
          generatedImages: [
            ...images.map(img => ({
              id: Date.now() + Math.random(),
              timestamp: new Date().toISOString(),
              ...img
            })),
            ...state.generatedImages
          ]
        })),
      
      /**
       * 选择图片（用于后续图生视频）
       */
      selectImage: (imageId) => set({ selectedImageId: imageId }),
      
      /**
       * 删除生成的图片
       */
      deleteGeneratedImage: (imageId) => 
        set((state) => ({
          generatedImages: state.generatedImages.filter(img => img.id !== imageId),
          selectedImageId: state.selectedImageId === imageId ? null : state.selectedImageId
        })),
      
      /**
       * 清空生成的图片
       */
      clearGeneratedImages: () => set({ 
        generatedImages: [], 
        selectedImageId: null 
      }),
      
      /**
       * 设置模型列表
       */
      setModels: (textToImageModels, promptOptimizationModels) => 
        set({ textToImageModels, promptOptimizationModels }),
      
      /**
       * 设置优化中状态
       */
      setOptimizing: (isOptimizing) => set({ isOptimizing }),
      
      /**
       * 设置生成中状态
       */
      setGenerating: (isGenerating) => set({ isGenerating }),
      
      /**
       * 设置加载模型中状态
       */
      setLoadingModels: (isLoadingModels) => set({ isLoadingModels }),
      
      /**
       * 设置错误信息
       */
      setError: (error) => set({ error }),
      
      /**
       * 清除错误信息
       */
      clearError: () => set({ error: null }),
      
      /**
       * 添加到历史记录
       */
      addToHistory: (record) => 
        set((state) => ({
          history: [{
            id: Date.now() + Math.random(),
            timestamp: new Date().toISOString(),
            ...record
          }, ...state.history]
        })),
      
      /**
       * 清空历史记录
       */
      clearHistory: () => set({ history: [] }),
      
      /**
       * 重置所有状态
       */
      reset: () => set({
        userPrompt: '',
        optimizedPrompt: '',
        useOptimizedPrompt: false,
        referenceImages: [],
        generatedImages: [],
        selectedImageId: null,
        isOptimizing: false,
        isGenerating: false,
        error: null
      }),
      
      /**
       * 获取当前使用的提示词
       */
      getCurrentPrompt: () => {
        const state = get();
        return state.useOptimizedPrompt && state.optimizedPrompt 
          ? state.optimizedPrompt 
          : state.userPrompt;
      },
      
      /**
       * 获取选中的图片对象
       */
      getSelectedImage: () => {
        const state = get();
        return state.generatedImages.find(img => img.id === state.selectedImageId);
      }
    }),
    {
      name: 'image-store',
      enabled: import.meta.env.DEV
    }
  )
);

export default useImageStore;

