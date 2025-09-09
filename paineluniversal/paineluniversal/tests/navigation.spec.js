// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * TESTES DE NAVEGAÇÃO E INTERFACE - Sistema Universal
 */

const TEST_CREDENTIALS = {
  cpf: '06601206154',
  password: '101112'
};

// Helper para fazer login
async function loginHelper(page) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  
  if (page.url().includes('login')) {
    await page.fill('input[name="cpf"], input[placeholder*="CPF"]', TEST_CREDENTIALS.cpf);
    await page.fill('input[name="password"], input[placeholder*="Senha"], input[type="password"]', TEST_CREDENTIALS.password);
    await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
    await page.waitForTimeout(3000);
  }
}

test.describe('🧭 Navegação e Interface', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginHelper(page);
  });

  test('🏠 Dashboard carrega corretamente', async ({ page }) => {
    // Verificar se está no dashboard
    const isDashboard = !page.url().includes('login');
    expect(isDashboard).toBe(true);
    
    // Verificar elementos básicos do dashboard
    const hasNavigation = await page.locator('nav, .navbar, .sidebar, .menu').count() > 0;
    expect(hasNavigation).toBe(true);
  });

  test('📱 Menu lateral funcional', async ({ page }) => {
    // Procurar por itens de menu
    const menuItems = [
      'Produtos', 'Usuários', 'Eventos', 'Listas',
      'Dashboard', 'Relatórios', 'Configurações'
    ];
    
    let foundMenuItems = 0;
    for (const item of menuItems) {
      const itemExists = await page.locator(`a:has-text("${item}"), button:has-text("${item}"), .menu-item:has-text("${item}")`).count() > 0;
      if (itemExists) foundMenuItems++;
    }
    
    expect(foundMenuItems).toBeGreaterThan(2);
  });

  test('🔗 Navegação entre páginas principais', async ({ page }) => {
    const pages = [
      { name: 'Produtos', selectors: ['a:has-text("Produtos")', '[href*="produtos"]'] },
      { name: 'Usuários', selectors: ['a:has-text("Usuários")', '[href*="usuarios"]'] },
      { name: 'Eventos', selectors: ['a:has-text("Eventos")', '[href*="eventos"]'] }
    ];
    
    for (const pageInfo of pages) {
      let navigated = false;
      
      for (const selector of pageInfo.selectors) {
        try {
          if (await page.locator(selector).count() > 0) {
            await page.click(selector);
            await page.waitForTimeout(2000);
            navigated = true;
            break;
          }
        } catch {}
      }
      
      if (navigated) {
        // Verificar se a navegação funcionou
        const isOnCorrectPage = page.url().toLowerCase().includes(pageInfo.name.toLowerCase()) ||
                               await page.locator(`h1:has-text("${pageInfo.name}"), .title:has-text("${pageInfo.name}")`).count() > 0;
        
        console.log(`✅ ${pageInfo.name}: ${isOnCorrectPage ? 'OK' : 'FALHOU'}`);
      }
    }
  });

  test('📋 Formulários básicos funcionam', async ({ page }) => {
    // Ir para página de produtos para testar formulário
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Procurar por botão "Novo"
    const newButtons = [
      'button:has-text("Novo")', 'button:has-text("Adicionar")',
      'button:has-text("Criar")', 'button:has-text("+")'
    ];
    
    let formOpened = false;
    for (const selector of newButtons) {
      if (await page.locator(selector).count() > 0) {
        await page.click(selector);
        await page.waitForTimeout(1000);
        
        // Verificar se modal/formulário abriu
        const hasForm = await page.locator('.modal, .dialog, form, [role="dialog"]').count() > 0;
        if (hasForm) {
          formOpened = true;
          break;
        }
      }
    }
    
    expect(formOpened).toBe(true);
  });

  test('🔍 Campos de busca responsivos', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Verificar se há campo de busca
    const searchField = await page.locator('input[type="search"], input[placeholder*="buscar"], input[name="search"]').count() > 0;
    
    if (searchField) {
      const searchInput = page.locator('input[type="search"], input[placeholder*="buscar"], input[name="search"]').first();
      
      // Testar digitação
      await searchInput.fill('teste');
      await page.waitForTimeout(500);
      
      const value = await searchInput.inputValue();
      expect(value).toBe('teste');
    }
  });

  test('📱 Responsividade em mobile', async ({ page }) => {
    // Simular viewport mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // Verificar se página ainda é navegável
    const hasNavigation = await page.locator('nav, .navbar, .sidebar, .menu, .hamburger').count() > 0;
    expect(hasNavigation).toBe(true);
    
    // Voltar para desktop
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('⚡ Performance básica', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/produtos');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Página deve carregar em menos de 10 segundos
    expect(loadTime).toBeLessThan(10000);
    
    console.log(`⏱️ Tempo de carregamento de produtos: ${loadTime}ms`);
  });
});
