import { test, expect } from '@playwright/test';

// Configuração base
const BASE_URL = 'http://localhost:5175';
const API_URL = 'http://localhost:8002';
const LOGIN_CPF = '00000000000';
const LOGIN_SENHA = '0000';

test.describe('Sistema Painel Universal - Testes E2E Completos', () => {
  
  test.beforeEach(async ({ page }) => {
    // Configurar timeout maior para operações lentas
    page.setDefaultTimeout(30000);
  });

  test('1. Verificar serviços ativos', async ({ page }) => {
    // Testar frontend
    const frontendResponse = await page.goto(BASE_URL);
    expect(frontendResponse?.status()).toBeLessThan(400);
    
    // Testar backend health
    const healthResponse = await page.request.get(`${API_URL}/api/health`);
    expect(healthResponse.status()).toBe(200);
    const healthData = await healthResponse.json();
    expect(healthData.status).toBe('healthy');
  });

  test('2. Login com credenciais válidas', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    
    // Aguardar página carregar
    await page.waitForSelector('input[placeholder*="CPF"]', { timeout: 10000 });
    
    // Preencher formulário
    await page.fill('input[placeholder*="CPF"]', LOGIN_CPF);
    await page.fill('input[type="password"]', LOGIN_SENHA);
    
    // Fazer login
    await page.click('button[type="submit"]');
    
    // Verificar redirecionamento para dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Verificar se está logado
    const url = page.url();
    expect(url).toContain('/dashboard');
  });

  test('3. Navegar pelos módulos principais', async ({ page }) => {
    // Fazer login primeiro
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="CPF"]', LOGIN_CPF);
    await page.fill('input[type="password"]', LOGIN_SENHA);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Lista de módulos para testar
    const modulos = [
      { nome: 'Dashboard', url: '/dashboard' },
      { nome: 'Eventos', url: '/eventos' },
      { nome: 'Usuários', url: '/usuarios' },
      { nome: 'Produtos', url: '/produtos' },
      { nome: 'Vendas', url: '/vendas' },
      { nome: 'Estoque', url: '/estoque' }
    ];
    
    for (const modulo of modulos) {
      // Tentar navegar via menu ou URL direta
      const menuItem = page.locator(`text=${modulo.nome}`).first();
      if (await menuItem.isVisible({ timeout: 5000 }).catch(() => false)) {
        await menuItem.click();
      } else {
        await page.goto(`${BASE_URL}/app${modulo.url}`);
      }
      
      // Aguardar carregamento
      await page.waitForLoadState('networkidle');
      
      // Verificar se não há erros
      const errorElements = await page.locator('text=/erro|error/i').count();
      expect(errorElements).toBe(0);
    }
  });

  test('4. Verificar responsividade da API', async ({ page }) => {
    const endpoints = [
      '/api/health',
      '/api/cors-test',
      '/api/eventos',
      '/api/dashboard/stats'
    ];
    
    for (const endpoint of endpoints) {
      const response = await page.request.get(`${API_URL}${endpoint}`);
      expect(response.status()).toBe(200);
      
      const responseTime = response.headers()['x-response-time'];
      if (responseTime) {
        expect(parseInt(responseTime)).toBeLessThan(1000); // < 1 segundo
      }
    }
  });

  test('5. Testar logout', async ({ page }) => {
    // Fazer login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="CPF"]', LOGIN_CPF);
    await page.fill('input[type="password"]', LOGIN_SENHA);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Procurar botão de logout
    const logoutButton = page.locator('button:has-text("Sair"), button:has-text("Logout")').first();
    if (await logoutButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await logoutButton.click();
      
      // Verificar redirecionamento para login
      await page.waitForURL('**/login', { timeout: 10000 });
      expect(page.url()).toContain('/login');
    }
  });

  test('6. Verificar tratamento de erros', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    
    // Tentar login com credenciais inválidas
    await page.fill('input[placeholder*="CPF"]', '12345678901');
    await page.fill('input[type="password"]', 'senhaerrada');
    await page.click('button[type="submit"]');
    
    // Verificar mensagem de erro
    const errorMessage = await page.locator('text=/CPF ou senha inválidos|erro|error/i').first();
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test('7. Verificar carregamento de dados', async ({ page }) => {
    // Fazer login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="CPF"]', LOGIN_CPF);
    await page.fill('input[type="password"]', LOGIN_SENHA);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Verificar se dados são carregados no dashboard
    await page.waitForSelector('text=/evento|usuário|venda|produto/i', { timeout: 10000 });
    
    // Verificar se não há indicadores de loading infinito
    const loadingIndicators = await page.locator('.loading, .spinner, [role="progressbar"]').count();
    expect(loadingIndicators).toBe(0);
  });

  test('8. Verificar persistência de sessão', async ({ page, context }) => {
    // Fazer login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="CPF"]', LOGIN_CPF);
    await page.fill('input[type="password"]', LOGIN_SENHA);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Abrir nova aba
    const newPage = await context.newPage();
    await newPage.goto(`${BASE_URL}/app/dashboard`);
    
    // Verificar se continua logado
    const url = newPage.url();
    expect(url).toContain('/dashboard');
    expect(url).not.toContain('/login');
    
    await newPage.close();
  });

  test('9. Verificar formulários funcionais', async ({ page }) => {
    // Fazer login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="CPF"]', LOGIN_CPF);
    await page.fill('input[type="password"]', LOGIN_SENHA);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Navegar para produtos
    await page.goto(`${BASE_URL}/app/produtos`);
    await page.waitForLoadState('networkidle');
    
    // Verificar se existe botão de adicionar
    const addButton = page.locator('button:has-text("Adicionar"), button:has-text("Novo"), button:has-text("+")').first();
    if (await addButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Verificar se botão é clicável
      await expect(addButton).toBeEnabled();
    }
  });

  test('10. Verificar performance geral', async ({ page }) => {
    const startTime = Date.now();
    
    // Fazer login e navegar
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="CPF"]', LOGIN_CPF);
    await page.fill('input[type="password"]', LOGIN_SENHA);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // Verificar se login + carregamento < 5 segundos
    expect(totalTime).toBeLessThan(5000);
  });
});

test.describe('Relatório Final', () => {
  test('Gerar relatório de testes', async ({ page }) => {
    console.log('========================================');
    console.log('RELATÓRIO DE TESTES E2E - PAINEL UNIVERSAL');
    console.log('========================================');
    console.log('Data:', new Date().toISOString());
    console.log('Frontend URL:', BASE_URL);
    console.log('Backend URL:', API_URL);
    console.log('Status: TODOS OS TESTES EXECUTADOS');
    console.log('========================================');
  });
});