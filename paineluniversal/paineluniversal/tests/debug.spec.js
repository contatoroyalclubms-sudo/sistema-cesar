// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * TESTE DE INVESTIGAÇÃO - Verificar estrutura da página
 */

test.describe('🔍 Investigação da Interface', () => {
  
  test('📋 Capturar estrutura da página inicial', async ({ page }) => {
    // Ir para página inicial
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');
    
    // Fazer screenshot
    await page.screenshot({ path: 'debug-homepage.png', fullPage: true });
    
    // Verificar URL atual
    console.log('🌐 URL atual:', page.url());
    
    // Verificar título da página
    const title = await page.title();
    console.log('📄 Título:', title);
    
    // Verificar se há formulário de login
    const loginForms = await page.locator('form').count();
    console.log('📝 Formulários encontrados:', loginForms);
    
    // Verificar campos de input
    const inputs = await page.locator('input').count();
    console.log('⌨️ Inputs encontrados:', inputs);
    
    // Listar todos os inputs e seus atributos
    const inputsDetails = await page.locator('input').evaluateAll((inputs) => {
      return inputs.map(input => ({
        type: input.type,
        name: input.name,
        placeholder: input.placeholder,
        id: input.id,
        className: input.className
      }));
    });
    console.log('📝 Detalhes dos inputs:', JSON.stringify(inputsDetails, null, 2));
    
    // Verificar botões
    const buttons = await page.locator('button').count();
    console.log('🔘 Botões encontrados:', buttons);
    
    // Listar textos dos botões
    const buttonTexts = await page.locator('button').evaluateAll((buttons) => {
      return buttons.map(btn => btn.textContent?.trim());
    });
    console.log('🔘 Textos dos botões:', buttonTexts);
    
    // Verificar se há texto indicando login
    const hasLoginText = await page.locator('text=/login|entrar|senha|cpf/i').count();
    console.log('🔐 Elementos com texto de login:', hasLoginText);
    
    // Verificar se há navegação/menu
    const hasNav = await page.locator('nav, .nav, .navbar, .sidebar, .menu').count();
    console.log('🧭 Elementos de navegação:', hasNav);
    
    // Verificar elementos principais
    const mainElements = await page.locator('main, .main, .content, .app, .container').count();
    console.log('🏠 Elementos principais:', mainElements);
    
    // Verificar se há tabelas (produtos, usuários, etc.)
    const tables = await page.locator('table, .table').count();
    console.log('📊 Tabelas encontradas:', tables);
    
    // Capturar HTML do body para análise
    const bodyHTML = await page.locator('body').innerHTML();
    console.log('📄 Tamanho do HTML:', bodyHTML.length, 'caracteres');
    
    // Verificar se há erros JavaScript no console
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.log('❌ Erro JS:', msg.text());
      }
    });
    
    // Aguardar um pouco mais para capturar possíveis erros
    await page.waitForTimeout(3000);
  });

  test('🔗 Verificar todas as rotas possíveis', async ({ page }) => {
    const routes = [
      '/',
      '/login',
      '/dashboard',
      '/produtos',
      '/usuarios',
      '/eventos'
    ];
    
    for (const route of routes) {
      try {
        await page.goto(`http://localhost:5173${route}`);
        await page.waitForTimeout(2000);
        
        const url = page.url();
        const title = await page.title();
        
        console.log(`📍 Rota ${route}:`);
        console.log(`   URL final: ${url}`);
        console.log(`   Título: ${title}`);
        
        // Fazer screenshot da rota
        await page.screenshot({ path: `debug-route-${route.replace('/', 'home')}.png` });
        
      } catch (error) {
        console.log(`❌ Erro na rota ${route}:`, error.message);
      }
    }
  });
});
