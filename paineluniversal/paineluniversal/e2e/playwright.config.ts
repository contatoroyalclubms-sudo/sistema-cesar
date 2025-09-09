import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';

// Carregar variáveis de ambiente
dotenv.config();

/**
 * Configuração do Playwright para testes E2E
 */
export default defineConfig({
  // Diretório de testes
  testDir: './tests',
  
  // Configurações de execução
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }]
  ],
  
  // Configuração global de teste
  use: {
    // URL base
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    
    // Traces e screenshots
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Timeouts
    actionTimeout: 10000,
    navigationTimeout: 30000,
    
    // Headers customizados
    extraHTTPHeaders: {
      'Accept': 'application/json',
      'X-Test-Suite': 'playwright-e2e'
    },
    
    // Viewport padrão
    viewport: { width: 1280, height: 720 },
    
    // Ignorar erros HTTPS (desenvolvimento)
    ignoreHTTPSErrors: true,
    
    // Configurações de navegador
    launchOptions: {
      slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO) : 0,
    }
  },
  
  // Timeout global
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  
  // Projetos (diferentes navegadores e dispositivos)
  projects: [
    // Desktop browsers
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Mobile browsers
    {
      name: 'mobile',
      use: { ...devices['iPhone 13'] },
    },
    {
      name: 'tablet',
      use: { ...devices['iPad Pro'] },
    },
    
    // Branded browsers
    {
      name: 'edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    {
      name: 'chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],
  
  // Servidor web local (desenvolvimento)
  webServer: process.env.CI ? undefined : [
    {
      command: 'cd ../backend && poetry run uvicorn app.main:app --reload --port 8000',
      port: 8000,
      timeout: 120000,
      reuseExistingServer: true,
    },
    {
      command: 'cd ../frontend && npm run dev',
      port: 5173,
      timeout: 120000,
      reuseExistingServer: true,
    }
  ],
  
  // Diretório de saída
  outputDir: 'test-results/',
});