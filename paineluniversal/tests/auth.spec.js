// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * TESTES DE AUTENTICAÇÃO - Sistema Universal
 * Baseado no arquivo TESTES_VALIDADOS_CONTROLE.md
 */

const TEST_CREDENTIALS = {
  cpf: '06601206154',
  password: '101112'
};

test.describe('🔐 Autenticação', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('✅ Login com credenciais válidas', async ({ page }) => {
    // Aguardar página carregar
    await page.waitForLoadState('networkidle');
    
    // Verificar se está na página de login
    await expect(page).toHaveURL(/login/);
    
    // Preencher formulário de login
    await page.fill('input[name="cpf"], input[placeholder*="CPF"]', TEST_CREDENTIALS.cpf);
    await page.fill('input[name="password"], input[placeholder*="Senha"], input[type="password"]', TEST_CREDENTIALS.password);
    
    // Clicar em entrar
    await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
    
    // Aguardar redirecionamento
    await page.waitForTimeout(3000);
    
    // Verificar se foi redirecionado para dashboard/home
    const currentUrl = page.url();
    expect(currentUrl).not.toContain('login');
    
    // Verificar se existe algum elemento que indica login successful
    const dashboardIndicators = [
      'nav', 'sidebar', '.sidebar', '#sidebar',
      'button:has-text("Sair")', 'button:has-text("Logout")',
      '.dashboard', '#dashboard', '[data-testid="dashboard"]'
    ];
    
    let foundIndicator = false;
    for (const selector of dashboardIndicators) {
      try {
        await page.locator(selector).waitFor({ timeout: 2000 });
        foundIndicator = true;
        break;
      } catch {}
    }
    
    expect(foundIndicator).toBe(true);
  });

  test('❌ Login com credenciais inválidas', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    
    // Tentar login com credenciais inválidas
    await page.fill('input[name="cpf"], input[placeholder*="CPF"]', '11111111111');
    await page.fill('input[name="password"], input[placeholder*="Senha"], input[type="password"]', 'senha_errada');
    
    await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
    
    // Aguardar mensagem de erro
    await page.waitForTimeout(2000);
    
    // Verificar se permanece na página de login ou mostra erro
    const hasErrorMessage = await page.locator('.error, .alert-danger, .text-red, [role="alert"]').count() > 0;
    const stillOnLogin = page.url().includes('login') || await page.locator('input[type="password"]').count() > 0;
    
    expect(hasErrorMessage || stillOnLogin).toBe(true);
  });

  test('🚪 Logout funcional', async ({ page }) => {
    // Fazer login primeiro
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    if (page.url().includes('login')) {
      await page.fill('input[name="cpf"], input[placeholder*="CPF"]', TEST_CREDENTIALS.cpf);
      await page.fill('input[name="password"], input[placeholder*="Senha"], input[type="password"]', TEST_CREDENTIALS.password);
      await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
      await page.waitForTimeout(3000);
    }
    
    // Procurar botão de logout
    const logoutSelectors = [
      'button:has-text("Sair")', 'button:has-text("Logout")',
      'a:has-text("Sair")', 'a:has-text("Logout")',
      '[data-testid="logout"]', '.logout'
    ];
    
    let loggedOut = false;
    for (const selector of logoutSelectors) {
      try {
        if (await page.locator(selector).count() > 0) {
          await page.click(selector);
          await page.waitForTimeout(2000);
          loggedOut = true;
          break;
        }
      } catch {}
    }
    
    // Verificar se foi redirecionado para login
    expect(page.url()).toContain('login');
  });

  test('⏰ Verificação de sessão ativa', async ({ page }) => {
    // Fazer login
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    if (page.url().includes('login')) {
      await page.fill('input[name="cpf"], input[placeholder*="CPF"]', TEST_CREDENTIALS.cpf);
      await page.fill('input[name="password"], input[placeholder*="Senha"], input[type="password"]', TEST_CREDENTIALS.password);
      await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
      await page.waitForTimeout(3000);
    }
    
    // Atualizar página para verificar se sessão persiste
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Verificar se ainda está logado (não redirecionou para login)
    expect(page.url()).not.toContain('login');
  });
});
