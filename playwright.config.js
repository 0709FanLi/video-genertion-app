// Playwright配置文件 - 部署环境检测
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 60000, // 60秒超时（考虑API调用可能需要时间）
  retries: 1,
  fullyParallel: false, // 顺序执行测试
  forbidOnly: !!process.env.CI,
  workers: 1,
  
  use: {
    baseURL: 'http://106.14.204.36',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  reporter: [
    ['list'],
    ['html', { outputFolder: 'test-results/html-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],

  webServer: {
    // 不需要本地服务器，直接测试远程部署的应用
    command: 'echo "Testing deployed application"',
    port: 80,
    reuseExistingServer: true,
  },
});

