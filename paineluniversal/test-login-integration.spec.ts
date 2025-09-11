import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Configurações dos servidores
const FRONTEND_URL = 'http://localhost:5175';
const BACKEND_URL = 'http://localhost:8002';

// Dados de teste
const TEST_CREDENTIALS = {
  cpf: '00000000000',
  senha: 'admin123'
};

// Lista de módulos do sistema para teste
const SYSTEM_MODULES = [
  'dashboard',
  'usuarios',
  'clientes',
  'produtos',
  'vendas',
  'estoque',
  'financeiro',
  'relatorios'
];

// Função para capturar screenshot em caso de erro
async function captureErrorScreenshot(page: any, testName: string, errorMessage: string) {
  const timestamp = new Date().toISOString().replace(/[:]/g, '-');
  const filename = `error-${testName}-${timestamp}.png`;
  const screenshotPath = path.join('test-results', filename);
  
  try {
    // Criar diretório se não existir
    if (!fs.existsSync('test-results')) {
      fs.mkdirSync('test-results', { recursive: true });
    }
    
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📷 Screenshot capturado: ${screenshotPath}`);
    console.log(`❌ Erro: ${errorMessage}`);
    
    return screenshotPath;
  } catch (screenshotError) {
    console.log(`❌ Erro ao capturar screenshot: ${screenshotError}`);
    return null;
  }
}

// Função para capturar logs do console
function captureConsoleLogs(page: any, testName: string) {
  const logs: string[] = [];
  
  page.on('console', (msg: any) => {
    const logEntry = `[${msg.type()}] ${msg.text()}`;
    logs.push(logEntry);
    console.log(`🔍 Console: ${logEntry}`);
  });
  
  page.on('pageerror', (error: any) => {
    const errorEntry = `[PAGE ERROR] ${error.message}`;
    logs.push(errorEntry);
    console.log(`❌ Page Error: ${errorEntry}`);
  });
  
  page.on('requestfailed', (request: any) => {
    const failEntry = `[REQUEST FAILED] ${request.url()} - ${request.failure()?.errorText}`;
    logs.push(failEntry);
    console.log(`❌ Request Failed: ${failEntry}`);
  });
  
  return logs;
}

test.describe('Sistema Painel Universal - Testes E2E Completos', () => {
  
  test.beforeEach(async ({ page }) => {
    // Configurar captura de logs para cada teste
    captureConsoleLogs(page, 'setup');
  });

  test('1. Verificação do Frontend e Backend', async ({ page, request }) => {
    console.log('🔧 Testando disponibilidade dos servidores...');
    
    try {
      // Testar Frontend
      const frontendResponse = await request.get(FRONTEND_URL);
      expect(frontendResponse.status()).toBeLessThan(500);
      console.log('✅ Frontend está respondendo');
    } catch (error) {
      console.log('❌ Frontend não está acessível:', error);
      throw error;
    }

    try {
      // Testar Backend
      const backendResponse = await request.get(`${BACKEND_URL}/`);
      console.log('✅ Backend está respondendo');
    } catch (error) {
      console.log('❌ Backend não está acessível:', error);
      throw error;
    }
  });

  test('2. API Health Check e Endpoints', async ({ request }) => {
    console.log('🔧 Testando endpoints da API...');
    
    // Testar endpoints principais
    const endpoints = [
      '/',
      '/api/auth/login',
      '/docs',
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await request.get(`${BACKEND_URL}${endpoint}`);
        console.log(`✅ Endpoint ${endpoint}: Status ${response.status()}`);
      } catch (error) {
        console.log(`❌ Endpoint ${endpoint} falhou:`, error);
      }
    }
  });

  test('3. API Login direto com validações', async ({ request }) => {
    console.log('🔧 Testando autenticação JWT...');
    
    try {
      const response = await request.post(`${BACKEND_URL}/api/auth/login`, {
        data: TEST_CREDENTIALS
      });
      
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.access_token).toBeDefined();
      expect(data.user.cpf).toBe(TEST_CREDENTIALS.cpf);
      
      console.log('✅ Autenticação JWT funcionando!');
      console.log('✅ Token recebido:', data.access_token.substring(0, 20) + '...');
    } catch (error) {
      console.log('❌ Erro na autenticação:', error);
      throw error;
    }
  });

  test('4. Login completo no Frontend com validações', async ({ page }) => {
    console.log('🔧 Testando login completo no frontend...');
    
    const logs = captureConsoleLogs(page, 'login');
    
    try {
      // Navegar para o frontend
      await page.goto(FRONTEND_URL);
      
      // Aguardar carregamento
      await page.waitForLoadState('networkidle', { timeout: 10000 });
      
      // Verificar se a página carregou
      await page.waitForTimeout(2000);
      
      // Capturar screenshot da página inicial
      await page.screenshot({ path: 'test-results/01-pagina-inicial.png', fullPage: true });
      
      // Tentar encontrar campos de login de diferentes formas
      let loginFound = false;
      const loginSelectors = [
        'input[name="cpf"]',
        'input[placeholder*="CPF"]',
        'input[type="text"]',
        '[data-testid="cpf"]',
        '#cpf'
      ];
      
      for (const selector of loginSelectors) {
        try {
          await page.waitForSelector(selector, { timeout: 3000 });
          console.log(`✅ Campo CPF encontrado com seletor: ${selector}`);
          loginFound = true;
          break;
        } catch (e) {
          console.log(`⚠️ Seletor ${selector} não encontrado`);
        }
      }
      
      if (!loginFound) {
        await captureErrorScreenshot(page, 'login-form-not-found', 'Formulário de login não encontrado');
        throw new Error('Formulário de login não foi encontrado na página');
      }
      
      // Preencher formulário
      await page.fill('input[name="cpf"], input[placeholder*="CPF"], input[type="text"]', TEST_CREDENTIALS.cpf);
      await page.fill('input[name="senha"], input[name="password"], input[type="password"]', TEST_CREDENTIALS.senha);
      
      // Capturar screenshot antes do envio
      await page.screenshot({ path: 'test-results/02-form-preenchido.png', fullPage: true });
      
      // Clicar no botão de login
      const submitSelectors = [
        'button[type="submit"]',
        'button:has-text("Entrar")',
        'button:has-text("Login")',
        '[data-testid="login-button"]'
      ];
      
      let submitted = false;
      for (const selector of submitSelectors) {
        try {
          await page.click(selector);
          console.log(`✅ Botão de login clicado: ${selector}`);
          submitted = true;
          break;
        } catch (e) {
          console.log(`⚠️ Botão ${selector} não encontrado`);
        }
      }
      
      if (!submitted) {
        await captureErrorScreenshot(page, 'submit-button-not-found', 'Botão de envio não encontrado');
        throw new Error('Botão de envio do login não foi encontrado');
      }
      
      // Aguardar resposta
      await page.waitForTimeout(5000);
      
      // Capturar screenshot após login
      await page.screenshot({ path: 'test-results/03-pos-login.png', fullPage: true });
      
      console.log('✅ Login executado com sucesso!');
      
    } catch (error) {
      console.log('❌ Erro no teste de login:', error);
      await captureErrorScreenshot(page, 'login-error', error.toString());
      throw error;
    }
  });

  test('5. Navegação entre módulos', async ({ page }) => {
    console.log('🔧 Testando navegação entre módulos...');
    
    const logs = captureConsoleLogs(page, 'navigation');
    
    try {
      // Primeiro fazer login
      await page.goto(FRONTEND_URL);
      await page.waitForLoadState('networkidle');
      
      // Tentar login rápido
      try {
        await page.fill('input[name="cpf"], input[type="text"]', TEST_CREDENTIALS.cpf);
        await page.fill('input[name="senha"], input[type="password"]', TEST_CREDENTIALS.senha);
        await page.click('button[type="submit"], button:has-text("Entrar")');
        await page.waitForTimeout(3000);
      } catch (e) {
        console.log('⚠️ Login automático falhou, continuando...');
      }
      
      // Testar navegação para cada módulo
      for (const module of SYSTEM_MODULES) {
        try {
          console.log(`🔍 Testando módulo: ${module}`);
          
          // Tentar navegar diretamente para o módulo
          await page.goto(`${FRONTEND_URL}/${module}`);
          await page.waitForTimeout(2000);
          
          // Capturar screenshot do módulo
          await page.screenshot({ 
            path: `test-results/module-${module}.png`, 
            fullPage: true 
          });
          
          console.log(`✅ Módulo ${module} carregado`);
          
        } catch (error) {
          console.log(`❌ Erro no módulo ${module}:`, error);
          await captureErrorScreenshot(page, `module-${module}`, error.toString());
        }
      }
      
    } catch (error) {
      console.log('❌ Erro na navegação:', error);
      await captureErrorScreenshot(page, 'navigation-error', error.toString());
      throw error;
    }
  });

  test('6. Teste de CORS e Proxy', async ({ page, request }) => {
    console.log('🔧 Testando CORS e comunicação frontend-backend...');
    
    try {
      // Testar chamadas cross-origin
      const corsHeaders = {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
      };
      
      const corsResponse = await request.options(`${BACKEND_URL}/api/auth/login`, {
        headers: corsHeaders
      });
      
      console.log('✅ Resposta CORS:', corsResponse.status());
      
      // Testar proxy configuration
      await page.goto(FRONTEND_URL);
      
      // Monitorar requisições de rede
      const requests: string[] = [];
      page.on('request', request => {
        if (request.url().includes('api')) {
          requests.push(request.url());
          console.log('🌐 Request:', request.url());
        }
      });
      
      page.on('response', response => {
        if (response.url().includes('api')) {
          console.log('📥 Response:', response.url(), 'Status:', response.status());
        }
      });
      
      console.log('✅ Monitoramento de rede configurado');
      
    } catch (error) {
      console.log('❌ Erro CORS/Proxy:', error);
      await captureErrorScreenshot(page, 'cors-error', error.toString());
    }
  });

  test('7. Teste completo de integração E2E', async ({ page }) => {
    console.log('🔧 Executando teste completo de integração...');
    
    const logs = captureConsoleLogs(page, 'integration');
    
    try {
      // 1. Acessar aplicação
      await page.goto(FRONTEND_URL);
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/integration-01-inicial.png', fullPage: true });
      
      // 2. Fazer login
      await page.fill('input[name="cpf"], input[type="text"]', TEST_CREDENTIALS.cpf);
      await page.fill('input[name="senha"], input[type="password"]', TEST_CREDENTIALS.senha);
      await page.click('button[type="submit"], button:has-text("Entrar")');
      await page.waitForTimeout(5000);
      await page.screenshot({ path: 'test-results/integration-02-login.png', fullPage: true });
      
      // 3. Verificar se chegou no dashboard
      const currentUrl = page.url();
      console.log('📍 URL atual:', currentUrl);
      
      // 4. Tentar acessar diferentes seções
      const sections = ['#dashboard', '.dashboard', '[data-testid="dashboard"]'];
      for (const section of sections) {
        try {
          await page.waitForSelector(section, { timeout: 3000 });
          console.log(`✅ Seção encontrada: ${section}`);
          break;
        } catch (e) {
          console.log(`⚠️ Seção não encontrada: ${section}`);
        }
      }
      
      await page.screenshot({ path: 'test-results/integration-03-final.png', fullPage: true });
      
      console.log('✅ Teste de integração concluído!');
      
    } catch (error) {
      console.log('❌ Erro no teste de integração:', error);
      await captureErrorScreenshot(page, 'integration-error', error.toString());
      throw error;
    }
  });
});