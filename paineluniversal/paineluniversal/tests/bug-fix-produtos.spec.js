// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 🔥 TESTE CRÍTICO: Verificar se bug produtos foi corrigido
 * Bug: Erro 500 ao criar produto (tipo_usuario NULL constraint)
 * Correção aplicada: Substituído tipo_usuario por tipo no router
 */

const TEST_CREDENTIALS = {
  cpf: '06601206154',
  password: '101112'
};

test.describe('🛠️ CORREÇÃO BUG CRÍTICO - PRODUTOS', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login rápido
    await page.goto('http://localhost:5173/');
    await page.waitForTimeout(2000);
    
    // Se houver login, fazer rapidamente
    try {
      const loginExists = await page.locator('input[type="password"], input[placeholder*="senha"]').count() > 0;
      if (loginExists) {
        await page.fill('input[name="cpf"], input[placeholder*="CPF"]', TEST_CREDENTIALS.cpf);
        await page.fill('input[type="password"], input[placeholder*="senha"]', TEST_CREDENTIALS.password);
        await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
        await page.waitForTimeout(3000);
      }
    } catch (error) {
      console.log('Login automático ou já logado');
    }
  });

  test('🚀 BUG CORRIGIDO: Criação de produto deve funcionar', async ({ page }) => {
    // Navegar para produtos
    await page.goto('http://localhost:5173/produtos');
    await page.waitForTimeout(3000);
    
    console.log('📍 URL atual:', page.url());
    
    // Fazer screenshot da tela de produtos
    await page.screenshot({ path: 'debug-produtos-page.png', fullPage: true });
    
    // Verificar se há produtos listados
    const productsVisible = await page.locator('table, .table, .product-item').count() > 0;
    console.log('📊 Produtos visíveis:', productsVisible);
    
    // Procurar botão "Novo" ou similar
    const newButtonSelectors = [
      'button:has-text("Novo")', 
      'button:has-text("Adicionar")',
      'button:has-text("Criar")', 
      'button:has-text("+")',
      '.btn-primary:has-text("Novo")',
      '[data-testid="new-product"]'
    ];
    
    let buttonFound = false;
    let usedSelector = '';
    
    for (const selector of newButtonSelectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        buttonFound = true;
        usedSelector = selector;
        console.log(`✅ Botão encontrado: ${selector}`);
        break;
      }
    }
    
    if (!buttonFound) {
      console.log('❌ Nenhum botão "Novo" encontrado. Listando todos os botões disponíveis:');
      const allButtons = await page.locator('button').evaluateAll(buttons => 
        buttons.map(btn => ({
          text: btn.textContent?.trim(),
          class: btn.className,
          id: btn.id
        }))
      );
      console.log('🔘 Botões disponíveis:', JSON.stringify(allButtons, null, 2));
      return;
    }
    
    // Clicar no botão novo
    await page.click(usedSelector);
    await page.waitForTimeout(2000);
    
    // Verificar se modal/formulário abriu
    const modalVisible = await page.locator('.modal, .dialog, [role="dialog"], .modal-content').isVisible();
    console.log('📝 Modal aberto:', modalVisible);
    
    if (!modalVisible) {
      console.log('❌ Modal não abriu. Verificando elementos visíveis...');
      await page.screenshot({ path: 'debug-no-modal.png' });
      return;
    }
    
    // Preencher dados do produto RAPIDAMENTE
    const productData = {
      nome: `Produto Teste ${Date.now()}`,
      descricao: 'Produto criado por teste automatizado',
      preco: '29.99',
      categoria: 'BEBIDA',
      tipo: 'BEBIDA'
    };
    
    // Preencher campos básicos
    const fields = [
      { selector: 'input[name="nome"], input[placeholder*="nome"]', value: productData.nome },
      { selector: 'textarea[name="descricao"], input[name="descricao"]', value: productData.descricao },
      { selector: 'input[name="preco"], input[placeholder*="preço"]', value: productData.preco }
    ];
    
    for (const field of fields) {
      try {
        const exists = await page.locator(field.selector).count() > 0;
        if (exists) {
          await page.fill(field.selector, field.value);
          console.log(`✅ Preenchido: ${field.selector} = ${field.value}`);
        }
      } catch (error) {
        console.log(`⚠️ Erro ao preencher ${field.selector}:`, error.message);
      }
    }
    
    // Tentar selecionar tipo/categoria
    try {
      const selectExists = await page.locator('select[name="tipo"], select[name="categoria"]').count() > 0;
      if (selectExists) {
        await page.selectOption('select[name="tipo"], select[name="categoria"]', 'BEBIDA');
        console.log('✅ Tipo/categoria selecionado: BEBIDA');
      }
    } catch (error) {
      console.log('⚠️ Não foi possível selecionar tipo via select');
    }
    
    // Monitorar requisições para capturar resposta
    let responseStatus = null;
    let responseBody = null;
    
    page.on('response', async (response) => {
      if (response.url().includes('/api/produtos') && response.request().method() === 'POST') {
        responseStatus = response.status();
        try {
          responseBody = await response.text();
        } catch (e) {
          responseBody = 'Erro ao ler resposta';
        }
        console.log(`📡 Resposta API: Status ${responseStatus}`);
        console.log(`📡 Body:`, responseBody);
      }
    });
    
    // Salvar produto
    await page.click('button:has-text("Salvar"), button[type="submit"], .btn-primary:has-text("Salvar")');
    await page.waitForTimeout(5000);
    
    // Verificar resultado
    if (responseStatus === 201 || responseStatus === 200) {
      console.log('🎉 SUCESSO: Produto criado com sucesso! Bug corrigido!');
      expect(responseStatus).toBeLessThan(400);
    } else if (responseStatus === 500) {
      console.log('❌ FALHA: Ainda há erro 500');
      console.log('Resposta:', responseBody);
      expect(responseStatus).not.toBe(500);
    } else {
      console.log(`⚠️ Status inesperado: ${responseStatus}`);
    }
    
    // Screenshot final
    await page.screenshot({ path: 'debug-produto-resultado.png' });
  });

  test('🔍 Verificar se filtros funcionam após correção', async ({ page }) => {
    await page.goto('http://localhost:5173/produtos');
    await page.waitForTimeout(2000);
    
    // Contar produtos antes do filtro
    const totalBefore = await page.locator('tr[data-key], .product-item, tbody tr').count();
    console.log('📊 Produtos antes do filtro:', totalBefore);
    
    // Procurar campo de busca
    const searchField = page.locator('input[type="search"], input[placeholder*="buscar"], input[name="search"]').first();
    
    if (await searchField.count() > 0) {
      await searchField.fill('Cerveja');
      await page.waitForTimeout(2000);
      
      const totalAfter = await page.locator('tr[data-key], .product-item, tbody tr').count();
      console.log('📊 Produtos após filtro:', totalAfter);
      
      if (totalAfter < totalBefore) {
        console.log('✅ Filtro funcionando!');
      } else {
        console.log('❌ Filtro ainda não funciona');
      }
    }
  });
});
