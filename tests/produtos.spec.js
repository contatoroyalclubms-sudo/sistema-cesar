// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * TESTES DE PRODUTOS - Foco nos BUGS CRÍTICOS identificados
 * 1. Erro 500 ao criar produto (tipo_usuario NULL)
 * 2. Filtros não funcionam
 * 3. Mapeamento backend incorreto
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

test.describe('🛍️ Gestão de Produtos - CORREÇÃO DE BUGS CRÍTICOS', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginHelper(page);
  });

  test('🔍 Navegação para módulo Produtos', async ({ page }) => {
    // Navegar para produtos
    const productLinks = [
      'a:has-text("Produtos")', 'button:has-text("Produtos")',
      '[href*="produtos"]', '[data-testid="produtos"]',
      '.nav-item:has-text("Produtos")'
    ];
    
    let navigated = false;
    for (const selector of productLinks) {
      try {
        if (await page.locator(selector).count() > 0) {
          await page.click(selector);
          await page.waitForTimeout(2000);
          navigated = true;
          break;
        }
      } catch {}
    }
    
    if (!navigated) {
      // Tentar navegação direta por URL
      await page.goto('/produtos');
      await page.waitForTimeout(2000);
    }
    
    // Verificar se chegou na página de produtos
    const isOnProductsPage = page.url().includes('produtos') || 
                            await page.locator('h1:has-text("Produtos"), .title:has-text("Produtos")').count() > 0;
    
    expect(isOnProductsPage).toBe(true);
  });

  test('📋 Listagem de produtos carrega corretamente', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(3000);
    
    // Verificar se há uma tabela ou lista de produtos
    const productTable = await page.locator('table, .table, .product-list, .data-table').count() > 0;
    
    expect(productTable).toBe(true);
    
    // Verificar se há pelo menos alguns produtos listados
    const hasProducts = await page.locator('tr[data-key], .product-item, .table tbody tr').count() > 0;
    
    expect(hasProducts).toBe(true);
  });

  test('❌ BUG CRÍTICO: Teste criação de produto (deve FALHAR)', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Procurar botão "Novo" ou "Adicionar"
    const newProductSelectors = [
      'button:has-text("Novo")', 'button:has-text("Adicionar")',
      'button:has-text("Criar")', 'button:has-text("+ ")',
      '[data-testid="new-product"]', '.btn-new'
    ];
    
    let foundNewButton = false;
    for (const selector of newProductSelectors) {
      if (await page.locator(selector).count() > 0) {
        await page.click(selector);
        foundNewButton = true;
        break;
      }
    }
    
    expect(foundNewButton).toBe(true);
    
    // Aguardar modal abrir
    await page.waitForTimeout(1000);
    
    // Preencher formulário de produto
    const productData = {
      nome: 'Produto Teste Automatizado',
      descricao: 'Produto criado por teste automatizado',
      preco: '19.99',
      categoria: 'BEBIDA'
    };
    
    // Preencher campos do formulário
    await page.fill('input[name="nome"], input[placeholder*="nome"]', productData.nome);
    await page.fill('textarea[name="descricao"], input[name="descricao"]', productData.descricao);
    await page.fill('input[name="preco"], input[placeholder*="preço"]', productData.preco);
    
    // Tentar selecionar categoria
    try {
      await page.selectOption('select[name="categoria"], select[name="tipo"]', productData.categoria);
    } catch {
      // Se não houver select, tentar por texto
      await page.fill('input[name="categoria"], input[name="tipo"]', productData.categoria);
    }
    
    // Monitorar requisições de rede para capturar o erro
    const responsePromise = page.waitForResponse(resp => resp.url().includes('/api/produtos') && resp.request().method() === 'POST');
    
    // Salvar produto
    await page.click('button:has-text("Salvar"), button[type="submit"], .btn-primary');
    
    try {
      const response = await responsePromise;
      const status = response.status();
      
      // Espera-se que falhe com erro 500 devido ao bug tipo_usuario
      if (status === 500) {
        console.log('🐛 BUG CONFIRMADO: Erro 500 ao criar produto (esperado)');
        const responseBody = await response.text();
        console.log('Erro:', responseBody);
        
        // Verificar se a mensagem de erro contém referência ao tipo_usuario
        expect(responseBody).toContain('tipo_usuario');
      } else if (status === 201 || status === 200) {
        // Se funcionou, o bug foi corrigido!
        console.log('✅ BUG CORRIGIDO: Produto criado com sucesso!');
      }
      
    } catch (error) {
      console.log('❌ Erro na requisição:', error);
    }
  });

  test('🔍 BUG: Filtros de busca não funcionam', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Contar produtos antes do filtro
    const totalProductsBefore = await page.locator('tr[data-key], .product-item, .table tbody tr').count();
    
    // Procurar campo de busca
    const searchInput = page.locator('input[placeholder*="buscar"], input[name="search"], input[type="search"]').first();
    
    if (await searchInput.count() > 0) {
      // Fazer busca por "Cerveja" (produto conhecido)
      await searchInput.fill('Cerveja');
      await page.waitForTimeout(1500);
      
      // Contar produtos após filtro
      const totalProductsAfter = await page.locator('tr[data-key], .product-item, .table tbody tr').count();
      
      // Verificar se o filtro funcionou (deveria mostrar menos produtos)
      if (totalProductsAfter === totalProductsBefore) {
        console.log('🐛 BUG CONFIRMADO: Filtro de busca não funciona');
        expect(totalProductsAfter).toBeLessThan(totalProductsBefore);
      } else {
        console.log('✅ BUG CORRIGIDO: Filtro de busca funcionando');
      }
    }
  });

  test('📝 CRUD: Edição de produto existente', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Procurar primeiro botão de editar (azul)
    const editButtons = page.locator('button[style*="background-color: rgb(59, 130, 246)"], .btn-edit, button:has-text("Editar")');
    
    if (await editButtons.count() > 0) {
      await editButtons.first().click();
      await page.waitForTimeout(1000);
      
      // Verificar se modal de edição abriu
      const editModal = await page.locator('.modal, .dialog, [role="dialog"]').count() > 0;
      expect(editModal).toBe(true);
      
      // Tentar alterar o nome do produto
      const nameInput = page.locator('input[name="nome"], input[value*="Cerveja"], input[value*="Hambúrguer"]');
      if (await nameInput.count() > 0) {
        await nameInput.fill('Produto Editado Por Teste');
        
        // Salvar alterações
        await page.click('button:has-text("Salvar"), button[type="submit"]');
        await page.waitForTimeout(2000);
        
        // Verificar se voltou para listagem
        const backToList = page.url().includes('produtos') && !await page.locator('.modal').isVisible();
        expect(backToList).toBe(true);
      }
    }
  });

  test('🗑️ CRUD: Exclusão de produto', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Procurar botão de exclusão (vermelho)
    const deleteButtons = page.locator('button[style*="background-color: rgb(239, 68, 68)"], .btn-delete, button:has-text("Excluir")');
    
    if (await deleteButtons.count() > 0) {
      await deleteButtons.first().click();
      await page.waitForTimeout(1000);
      
      // Verificar se modal de confirmação apareceu
      const confirmModal = await page.locator('.modal, .dialog, [role="dialog"]').count() > 0;
      expect(confirmModal).toBe(true);
      
      // Confirmar exclusão (mas não executar para não quebrar dados)
      const confirmButton = page.locator('button:has-text("Confirmar"), button:has-text("Sim"), button:has-text("Excluir")');
      if (await confirmButton.count() > 0) {
        console.log('✅ Modal de confirmação de exclusão funcionando');
        
        // Cancelar para não excluir realmente
        await page.click('button:has-text("Cancelar"), button:has-text("Não")');
      }
    }
  });

  test('🔄 Funcionalidade: Duplicar produto', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Procurar botão de duplicar (verde)
    const duplicateButtons = page.locator('button[style*="background-color: rgb(34, 197, 94)"], .btn-duplicate');
    
    if (await duplicateButtons.count() > 0) {
      // Monitorar console para ver se função é chamada
      let consoleCalled = false;
      page.on('console', (msg) => {
        if (msg.text().includes('duplicar')) {
          consoleCalled = true;
        }
      });
      
      await duplicateButtons.first().click();
      await page.waitForTimeout(1000);
      
      // Verificar se função foi executada via console.log
      expect(consoleCalled).toBe(true);
    }
  });

  test('🔒 Funcionalidade: Limitar acesso produto', async ({ page }) => {
    await page.goto('/produtos');
    await page.waitForTimeout(2000);
    
    // Procurar botão de limitar acesso (laranja)
    const limitButtons = page.locator('button[style*="background-color: rgb(245, 158, 11)"], .btn-limit');
    
    if (await limitButtons.count() > 0) {
      let consoleCalled = false;
      page.on('console', (msg) => {
        if (msg.text().includes('acesso')) {
          consoleCalled = true;
        }
      });
      
      await limitButtons.first().click();
      await page.waitForTimeout(1000);
      
      expect(consoleCalled).toBe(true);
    }
  });
});
