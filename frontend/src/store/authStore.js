/**
 * 认证状态管理 Store
 * 
 * 使用Zustand管理用户登录状态、Token和用户信息
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { authAPI } from '../services/api';

const useAuthStore = create(
  devtools(
    persist(
      (set, get) => ({
        // ========== 状态 ==========
        
        /** 当前用户信息 */
        user: null,
        
        /** JWT Token */
        token: null,
        
        /** 是否已登录 */
        isAuthenticated: false,
        
        /** 是否正在加载 */
        isLoading: false,
        
        /** 错误信息 */
        error: null,
        
        // ========== Actions ==========
        
        /**
         * 用户登录
         * @param {string} username - 用户名
         * @param {string} password - 密码
         * @returns {Promise<boolean>} 登录是否成功
         */
        login: async (username, password) => {
          set({ isLoading: true, error: null });
          
          try {
            // 调用登录API
            const response = await authAPI.login(username, password);
            const { access_token } = response;
            
            // 获取用户信息
            const userInfo = await authAPI.getCurrentUser(access_token);
            
            // 更新状态
            set({
              user: userInfo,
              token: access_token,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
            
            console.log('[AuthStore] 登录成功:', userInfo);
            return true;
            
          } catch (error) {
            console.error('[AuthStore] 登录失败:', error);
            set({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
              error: error.response?.data?.detail || error.message || '登录失败'
            });
            return false;
          }
        },
        
        /**
         * 用户注册
         * @param {string} username - 用户名
         * @param {string} password - 密码
         * @returns {Promise<boolean>} 注册是否成功
         */
        register: async (username, password) => {
          set({ isLoading: true, error: null });
          
          try {
            // 调用注册API
            await authAPI.register(username, password);
            
            // 注册成功，不自动登录
            set({ isLoading: false });
            return true;
            
          } catch (error) {
            console.error('[AuthStore] 注册失败:', error);
            set({
              isLoading: false,
              error: error.response?.data?.detail || error.message || '注册失败'
            });
            return false;
          }
        },
        
        /**
         * 用户登出
         */
        logout: async () => {
          try {
            const { token } = get();
            if (token) {
              // 调用登出API（可选，因为JWT无状态）
              await authAPI.logout(token);
            }
          } catch (error) {
            console.error('[AuthStore] 登出API调用失败:', error);
          } finally {
            // 清除本地状态
            set({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
              error: null
            });
            console.log('[AuthStore] 登出成功');
          }
        },
        
        /**
         * 刷新用户信息
         */
        refreshUser: async () => {
          const { token } = get();
          if (!token) return;
          
          try {
            const userInfo = await authAPI.getCurrentUser(token);
            set({ user: userInfo });
            console.log('[AuthStore] 用户信息已刷新');
          } catch (error) {
            console.error('[AuthStore] 刷新用户信息失败:', error);
            // Token可能已过期，清除认证状态
            get().logout();
          }
        },
        
        /**
         * 清除错误
         */
        clearError: () => set({ error: null }),
        
        /**
         * 检查认证状态
         * @returns {boolean} 是否已登录
         */
        checkAuth: () => {
          const { token, isAuthenticated } = get();
          return !!(token && isAuthenticated);
        },
        
      }),
      {
        name: 'auth-storage', // localStorage key
        partialize: (state) => ({
          user: state.user,
          token: state.token,
          isAuthenticated: state.isAuthenticated
        }) // 只持久化部分状态
      }
    ),
    {
      name: 'AuthStore',
      enabled: import.meta.env.DEV // 只在开发环境启用devtools
    }
  )
);

export default useAuthStore;

