/**
 * 图生视频状态管理
 * 使用Zustand管理图生视频的全局状态
 */

import { create } from 'zustand';

const useVideoStore = create((set) => ({
  // 首帧图片
  firstFrame: null, // { url: string, file: File, base64: string }
  setFirstFrame: (frame) => set({ firstFrame: frame }),
  
  // 尾帧图片
  lastFrame: null, // { url: string, file: File, base64: string }
  setLastFrame: (frame) => set({ lastFrame: frame }),
  
  // 交换首尾帧
  swapFrames: () => set((state) => ({
    firstFrame: state.lastFrame,
    lastFrame: state.firstFrame
  })),
  
  // 清空所有帧
  clearFrames: () => set({ firstFrame: null, lastFrame: null }),
  
  // 视频提示词
  prompt: '',
  setPrompt: (prompt) => set({ prompt }),
  
  
  // 选择的模型
  selectedModel: 'volc-i2v-first', // 默认火山即梦单图首帧
  setSelectedModel: (model) => set({ selectedModel: model }),
  
  // 视频时长（秒）
  duration: 5,
  setDuration: (duration) => set({ duration }),
  
  // 视频分辨率
  resolution: '720P',
  setResolution: (resolution) => set({ resolution }),
  
  // 视频长宽比（仅文生视频使用）
  aspectRatio: '16:9',
  setAspectRatio: (aspectRatio) => set({ aspectRatio }),
  
  // 生成状态
  generating: false,
  setGenerating: (status) => set({ generating: status }),
  
  // 生成结果
  videoResult: null, // { video_url: string, task_id: string, ... }
  setVideoResult: (result) => set({ videoResult: result }),
  
  // 清空结果
  clearResult: () => set({ videoResult: null }),
  
  // 错误信息
  error: null,
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  
  // 重置所有状态
  reset: () => set({
    firstFrame: null,
    lastFrame: null,
    prompt: '',
    selectedModel: 'volc-i2v-first',
    duration: 5,
    resolution: '720P',
    aspectRatio: '16:9',
    generating: false,
    videoResult: null,
    error: null
  })
}));

export default useVideoStore;

