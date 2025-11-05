// Playwright配置文件
module.exports = {
  testDir: './tests',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://106.14.204.36:5000',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...require('@playwright/test').devices['Desktop Chrome'] },
    },
  ],
  reporter: [
    ['list'],
    ['html', { outputFolder: 'test-results/html-report' }],
  ],
};

