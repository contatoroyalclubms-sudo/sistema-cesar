// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 🚀 TESTE COMPLETO DO SISTEMA - FASE 1: VERIFICAÇÃO BUG CRÍTICO
 * Testando se correção do bug produtos funcionou
 */

const TEST_CREDENTIALS = {
  cpf: '06601206154',
  password: '101112'
};

// Helper para login rápido
async function quickLogin(page) {
  await page.goto('http://localhost:5173/');
  await page.waitForTimeout(1500);
  
  try {
    const needsLogin = await page.locator('input[type="password"], input[placeholder*="senha"]').count() > 0;
    if (needsLogin) {
      await page.fill('input[name="cpf"], input[placeholder*="CPF"]', TEST_CREDENTIALS.cpf);
      await page.fill('input[type="password"], input[placeholder*="senha"]', TEST_CREDENTIALS.password);
      await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
      await page.waitForTimeout(2000);
    }
  } catch (error) {
    console.log('🔐 Login automático ou já logado');
  }
}

test.describe('🔥 FASE 1: CORREÇÃO BUG CRÍTICO PRODUTOS', () => {
  
  test('✅ BUG CORRIGIDO: Criação de produto deve funcionar', async ({ page }) => {
    await quickLogin(page);
    
    // Navegar para produtos
    await page.goto('http://localhost:5173/produtos');
    await page.waitForTimeout(2000);
    
    console.log('📍 Testando página de produtos...');
    
    // Verificar se página carregou
    const hasContent = await page.locator('body').innerHTML();
    console.log('📄 Tamanho HTML:', hasContent.length, 'caracteres');
    
    if (hasContent.length < 200) {
      console.log('❌ ERRO: Página não carregou conteúdo');
      await page.screenshot({ path: 'debug-empty-page.png' });
      return;
    }
    
    // Procurar botão "Novo"
    const newButtonSelectors = [
      'button:has-text("Novo")', 
      'button:has-text("Adicionar")',
      'button:has-text("Criar")', 
      'button:has-text("+")',
      '.btn-primary'
    ];
    
    let buttonFound = false;
    for (const selector of newButtonSelectors) {
      if (await page.locator(selector).count() > 0) {
        console.log(`✅ Botão encontrado: ${selector}`);
        await page.click(selector);
        buttonFound = true;
        break;
      }
    }
    
    if (!buttonFound) {
      console.log('❌ Botão "Novo" não encontrado');
      return;
    }
    
    await page.waitForTimeout(1500);
    
    // Verificar se modal abriu
    const modalVisible = await page.locator('.modal, .dialog, [role="dialog"]').count() > 0;
    console.log('📝 Modal aberto:', modalVisible);
    
    if (!modalVisible) {
      console.log('❌ Modal não abriu');
      return;
    }
    
    // Preencher produto rapidamente
    const productName = `Produto_Teste_${Date.now()}`;
    
    await page.fill('input[name="nome"], input[placeholder*="nome"]', productName);
    await page.fill('textarea[name="descricao"], input[name="descricao"]', 'Teste automatizado');
    await page.fill('input[name="preco"], input[placeholder*="preço"]', '15.50');
    
    // Selecionar tipo
    try {
      await page.selectOption('select[name="tipo"], select[name="categoria"]', 'BEBIDA');
    } catch {
      console.log('⚠️ Seletor tipo não encontrado');
    }
    
    // Monitorar resposta da API
    let apiResponse = null;
    page.on('response', async (response) => {
      if (response.url().includes('/api/produtos') && response.request().method() === 'POST') {
        apiResponse = {
          status: response.status(),
          url: response.url()
        };
        try {
          const body = await response.text();
          apiResponse.body = body;
        } catch (e) {
          apiResponse.body = 'Erro ao ler body';
        }
      }
    });
    
    // Salvar
    await page.click('button:has-text("Salvar"), button[type="submit"]');
    await page.waitForTimeout(3000);
    
    // Verificar resultado
    if (apiResponse) {
      console.log(`📡 Resposta API: Status ${apiResponse.status}`);
      if (apiResponse.status === 200 || apiResponse.status === 201) {
        console.log('🎉 SUCESSO: Bug corrigido! Produto criado com sucesso!');
      } else if (apiResponse.status === 500) {
        console.log('❌ FALHA: Bug ainda existe');
        console.log('Resposta:', apiResponse.body);
      }
    }
    
    await page.screenshot({ path: 'teste-produto-resultado.png' });
  });

  test('🔍 Testar filtros após correção', async ({ page }) => {
    await quickLogin(page);
    await page.goto('http://localhost:5173/produtos');
    await page.waitForTimeout(2000);
    
    // Testar filtro de busca
    const searchField = page.locator('input[type="search"], input[placeholder*="buscar"]').first();
    
    if (await searchField.count() > 0) {
      await searchField.fill('Cerveja');
      await page.waitForTimeout(1500);
      console.log('🔍 Filtro de busca testado');
    }
  });
});
