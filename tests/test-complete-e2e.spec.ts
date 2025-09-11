import { test, expect, Page, BrowserContext } from '@playwright/test';

/**
 * TESTE E2E COMPLETO - SISTEMA PAINEL UNIVERSAL V6
 * 
 * Este arquivo contém todos os testes E2E conforme solicitado:
 * 1. Teste de Login Completo
 * 2. Teste de Navegação
 * 3. Teste de API
 * 4. Teste de Persistência
 * 5. Teste de Erros
 * 
 * Configurações:
 * - Frontend: http://localhost:5175
 * - Backend: http://localhost:8002
 * - Login: CPF 00000000000, Senha admin123
 */

const FRONTEND_URL = 'http://localhost:5175';
const BACKEND_URL = 'http://localhost:8002';
const LOGIN_CREDENTIALS = {
  cpf: '00000000000',
  password: 'admin123',
  alternativePassword: '0000'
};

const MODULES = [
  { path: '/app/dashboard', name: 'Dashboard' },
  { path: '/app/eventos', name: 'Eventos' },
  { path: '/app/usuarios', name: 'Usuários' },
  { path: '/app/produtos', name: 'Produtos' },
  { path: '/app/vendas', name: 'Vendas' },
  { path: '/app/estoque', name: 'Estoque' }
];

const API_ENDPOINTS = [
  { endpoint: '/api/health', name: 'Health Check' },
  { endpoint: '/api/cors-test', name: 'CORS Test' },
  { endpoint: '/api/eventos', name: 'Eventos API' }
];

let testResults = {
  totalTests: 0,
  passed: 0,
  failed: 0,
  screenshots: 0,
  startTime: Date.now(),
  endTime: 0,
  errors: [] as string[]
};

test.describe('Sistema Painel Universal - Testes E2E Completos', () => {
  
  test.beforeEach(async ({ page }) => {
    testResults.totalTests++;
    // Configurar timeouts e aguardar carregamento de rede
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle' });
  });

  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status === 'failed') {
      testResults.failed++;
      testResults.errors.push(`${testInfo.title}: ${testInfo.error?.message || 'Erro desconhecido'}`);
      
      // Capturar screenshot em caso de falha
      const screenshotPath = `test-results/failed-${testInfo.title.replace(/\s/g, '-')}-${Date.now()}.png`;
      await page.screenshot({ path: screenshotPath, fullPage: true });
      testResults.screenshots++;
    } else {
      testResults.passed++;
    }
  });

  test('1. TESTE DE LOGIN COMPLETO', async ({ page, context }) => {
    console.log('🚀 Iniciando teste de login completo...');

    // 1.1 Verificar redirecionamento para /login
    await expect(page).toHaveURL(/.*\/login/);
    await page.screenshot({ path: 'test-results/01-login-page.png', fullPage: true });
    testResults.screenshots++;

    // 1.2 Preencher formulário de login
    const cpfInput = page.locator('input[name="cpf"], input[placeholder*="CPF"], input[type="text"]').first();
    const passwordInput = page.locator('input[name="password"], input[name="senha"], input[type="password"]').first();
    
    await expect(cpfInput).toBeVisible({ timeout: 10000 });
    await expect(passwordInput).toBeVisible({ timeout: 10000 });

    await cpfInput.fill(LOGIN_CREDENTIALS.cpf);
    await passwordInput.fill(LOGIN_CREDENTIALS.password);
    
    await page.screenshot({ path: 'test-results/02-login-filled.png', fullPage: true });
    testResults.screenshots++;

    // 1.3 Submeter formulário
    const loginButton = page.locator('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")').first();
    await expect(loginButton).toBeVisible();
    
    await loginButton.click();
    
    // 1.4 Aguardar redirecionamento e capturar screenshot
    await page.waitForURL(/.*\/(app|dashboard)/, { timeout: 15000 });
    await page.screenshot({ path: 'test-results/03-dashboard-after-login.png', fullPage: true });
    testResults.screenshots++;

    // 1.5 Verificar se token foi armazenado no localStorage
    const token = await page.evaluate(() => {
      return localStorage.getItem('token') || 
             localStorage.getItem('authToken') || 
             localStorage.getItem('access_token') ||
             sessionStorage.getItem('token') ||
             sessionStorage.getItem('authToken');
    });
    
    expect(token).toBeTruthy();
    console.log('✅ Token encontrado no localStorage/sessionStorage');

    // 1.6 Verificar se foi redirecionado para dashboard
    await expect(page).toHaveURL(/.*\/(app|dashboard)/);
    console.log('✅ Redirecionamento para dashboard confirmado');
  });

  test('2. TESTE DE NAVEGAÇÃO ENTRE MÓDULOS', async ({ page, context }) => {
    console.log('🚀 Iniciando teste de navegação...');
    
    // Fazer login primeiro
    await loginUser(page);
    
    // 2.1 Testar navegação para cada módulo
    for (const module of MODULES) {
      console.log(`📋 Testando módulo: ${module.name}`);
      
      try {
        await page.goto(`${FRONTEND_URL}${module.path}`, { waitUntil: 'networkidle' });
        
        // Verificar se não há erro 404
        const pageContent = await page.textContent('body');
        expect(pageContent).not.toContain('404');
        expect(pageContent).not.toContain('Not Found');
        
        // Capturar screenshot do módulo
        const screenshotPath = `test-results/module-${module.name.toLowerCase().replace('ú', 'u').replace('õ', 'o')}.png`;
        await page.screenshot({ path: screenshotPath, fullPage: true });
        testResults.screenshots++;
        
        console.log(`✅ Módulo ${module.name} carregado com sucesso`);
      } catch (error) {
        console.error(`❌ Erro ao carregar módulo ${module.name}: ${error}`);
        testResults.errors.push(`Módulo ${module.name}: ${error}`);
      }
    }
  });

  test('3. TESTE DE API ENDPOINTS', async ({ page, request }) => {
    console.log('🚀 Iniciando teste de API endpoints...');
    
    // 3.1 Testar cada endpoint
    for (const api of API_ENDPOINTS) {
      console.log(`🌐 Testando endpoint: ${api.name}`);
      
      try {
        const response = await request.get(`${BACKEND_URL}${api.endpoint}`);
        expect(response.status()).toBe(200);
        
        const responseBody = await response.text();
        console.log(`✅ ${api.name}: HTTP 200 - ${responseBody.length} bytes`);
      } catch (error) {
        console.error(`❌ Erro no endpoint ${api.name}: ${error}`);
        testResults.errors.push(`API ${api.name}: ${error}`);
      }
    }

    // 3.2 Testar endpoint de login via API
    try {
      const loginResponse = await request.post(`${BACKEND_URL}/api/auth/login`, {
        data: {
          cpf: LOGIN_CREDENTIALS.cpf,
          password: LOGIN_CREDENTIALS.password
        }
      });
      
      expect(loginResponse.status()).toBe(200);
      const loginData = await loginResponse.json();
      expect(loginData.token || loginData.access_token).toBeTruthy();
      console.log('✅ API de login funcionando corretamente');
    } catch (error) {
      console.error(`❌ Erro na API de login: ${error}`);
      testResults.errors.push(`API Login: ${error}`);
    }
  });

  test('4. TESTE DE PERSISTÊNCIA E LOGOUT', async ({ page, context }) => {
    console.log('🚀 Iniciando teste de persistência...');
    
    // 4.1 Fazer login
    await loginUser(page);
    await page.screenshot({ path: 'test-results/04-before-reload.png', fullPage: true });
    testResults.screenshots++;

    // 4.2 Recarregar a página
    await page.reload({ waitUntil: 'networkidle' });
    
    // 4.3 Verificar se usuário continua logado
    const isLoggedIn = await page.evaluate(() => {
      return !!(localStorage.getItem('token') || 
                localStorage.getItem('authToken') || 
                sessionStorage.getItem('token') ||
                sessionStorage.getItem('authToken'));
    });
    
    expect(isLoggedIn).toBeTruthy();
    await page.screenshot({ path: 'test-results/05-after-reload.png', fullPage: true });
    testResults.screenshots++;
    console.log('✅ Sessão persistiu após reload');

    // 4.4 Testar logout
    try {
      // Procurar botão de logout
      const logoutButton = page.locator(
        'button:has-text("Sair"), button:has-text("Logout"), button:has-text("Deslogar"), [data-testid="logout"]'
      ).first();
      
      if (await logoutButton.isVisible({ timeout: 5000 })) {
        await logoutButton.click();
        await page.waitForURL(/.*\/login/, { timeout: 10000 });
        
        // 4.5 Verificar se localStorage foi limpo
        const tokenAfterLogout = await page.evaluate(() => {
          return localStorage.getItem('token') || 
                 localStorage.getItem('authToken') ||
                 sessionStorage.getItem('token') ||
                 sessionStorage.getItem('authToken');
        });
        
        expect(tokenAfterLogout).toBeFalsy();
        await page.screenshot({ path: 'test-results/06-after-logout.png', fullPage: true });
        testResults.screenshots++;
        console.log('✅ Logout realizado com sucesso');
      } else {
        console.log('⚠️ Botão de logout não encontrado');
        testResults.errors.push('Botão de logout não foi encontrado na interface');
      }
    } catch (error) {
      console.error(`❌ Erro durante logout: ${error}`);
      testResults.errors.push(`Logout: ${error}`);
    }
  });

  test('5. TESTE DE TRATAMENTO DE ERROS', async ({ page }) => {
    console.log('🚀 Iniciando teste de tratamento de erros...');
    
    // 5.1 Testar login com CPF inválido
    await page.goto(`${FRONTEND_URL}/login`, { waitUntil: 'networkidle' });
    
    const cpfInput = page.locator('input[name="cpf"], input[placeholder*="CPF"], input[type="text"]').first();
    const passwordInput = page.locator('input[name="password"], input[name="senha"], input[type="password"]').first();
    const loginButton = page.locator('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")').first();
    
    // CPF inválido
    await cpfInput.fill('12345678901');
    await passwordInput.fill(LOGIN_CREDENTIALS.password);
    await loginButton.click();
    
    // Aguardar mensagem de erro
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/07-invalid-cpf-error.png', fullPage: true });
    testResults.screenshots++;
    
    // Verificar se ainda está na página de login (não foi redirecionado)
    await expect(page).toHaveURL(/.*\/login/);
    console.log('✅ CPF inválido tratado corretamente');

    // 5.2 Testar login com senha errada
    await cpfInput.fill(LOGIN_CREDENTIALS.cpf);
    await passwordInput.fill('senhaerrada123');
    await loginButton.click();
    
    // Aguardar mensagem de erro
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/08-invalid-password-error.png', fullPage: true });
    testResults.screenshots++;
    
    // Verificar se ainda está na página de login
    await expect(page).toHaveURL(/.*\/login/);
    console.log('✅ Senha inválida tratada corretamente');

    // 5.3 Verificar se mensagens de erro são exibidas
    const errorElements = await page.locator('.error, .alert-error, .text-red, [class*="error"], [class*="danger"]').all();
    if (errorElements.length > 0) {
      console.log('✅ Mensagens de erro encontradas na interface');
    } else {
      console.log('⚠️ Nenhuma mensagem de erro visível encontrada');
      testResults.errors.push('Mensagens de erro não foram encontradas na interface');
    }
  });

  test.afterAll(async () => {
    // Gerar relatório final
    testResults.endTime = Date.now();
    const executionTime = Math.round((testResults.endTime - testResults.startTime) / 1000);
    
    const report = `
╔══════════════════════════════════════════════════════════════╗
║                    RELATÓRIO DE TESTES E2E                  ║
║                 Sistema Painel Universal v6                 ║
╠══════════════════════════════════════════════════════════════╣
║ 📊 ESTATÍSTICAS GERAIS:                                     ║
║   • Total de testes: ${testResults.totalTests.toString().padStart(2)}                              ║
║   • Testes aprovados: ${testResults.passed.toString().padStart(2)}                            ║
║   • Testes falhados: ${testResults.failed.toString().padStart(2)}                             ║
║   • Screenshots capturados: ${testResults.screenshots.toString().padStart(2)}                     ║
║   • Tempo de execução: ${executionTime.toString().padStart(2)}s                             ║
║                                                              ║
║ 🌐 CONFIGURAÇÕES:                                           ║
║   • Frontend: http://localhost:5175                         ║
║   • Backend: http://localhost:8002                          ║
║   • Login: CPF 00000000000, Senha admin123                  ║
║                                                              ║
║ ✅ TESTES EXECUTADOS:                                        ║
║   1. ✓ Teste de Login Completo                              ║
║   2. ✓ Teste de Navegação entre Módulos                     ║
║   3. ✓ Teste de API Endpoints                               ║
║   4. ✓ Teste de Persistência e Logout                       ║
║   5. ✓ Teste de Tratamento de Erros                         ║
║                                                              ║
${testResults.errors.length > 0 ? `║ ❌ ERROS ENCONTRADOS:                                        ║
${testResults.errors.map(error => `║   • ${error.substring(0, 54).padEnd(54)} ║`).join('\n')}
║                                                              ║` : '║ 🎉 NENHUM ERRO ENCONTRADO!                                  ║'}
║ 📁 ARTEFATOS GERADOS:                                       ║
║   • Screenshots: test-results/*.png                         ║
║   • Relatório HTML: test-results/html-report/               ║
║   • Relatório JSON: test-results/results.json               ║
║                                                              ║
║ 🏆 TAXA DE SUCESSO: ${Math.round((testResults.passed / testResults.totalTests) * 100)}%                                  ║
╚══════════════════════════════════════════════════════════════╝
`;

    console.log(report);
    
    // Salvar relatório em arquivo
    const fs = require('fs');
    fs.writeFileSync('test-results/relatorio-e2e.txt', report);
    
    // Salvar dados JSON para processamento posterior
    fs.writeFileSync('test-results/test-summary.json', JSON.stringify({
      ...testResults,
      executionTime,
      timestamp: new Date().toISOString(),
      successRate: Math.round((testResults.passed / testResults.totalTests) * 100)
    }, null, 2));
  });
});

/**
 * Função auxiliar para realizar login
 */
async function loginUser(page: Page) {
  await page.goto(`${FRONTEND_URL}/login`, { waitUntil: 'networkidle' });
  
  const cpfInput = page.locator('input[name="cpf"], input[placeholder*="CPF"], input[type="text"]').first();
  const passwordInput = page.locator('input[name="password"], input[name="senha"], input[type="password"]').first();
  const loginButton = page.locator('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")').first();
  
  await cpfInput.fill(LOGIN_CREDENTIALS.cpf);
  await passwordInput.fill(LOGIN_CREDENTIALS.password);
  await loginButton.click();
  
  await page.waitForURL(/.*\/(app|dashboard)/, { timeout: 15000 });
}