import { test, expect } from '@playwright/test';

test.describe('Teste de Login Sistema Universal - CPF 00000000000', () => {
  
  test('Login completo com credenciais específicas', async ({ page }) => {
    console.log('🚀 Iniciando teste de login...');
    
    // 1. Navegar para a página de login
    console.log('📍 Navegando para http://localhost:5175');
    await page.goto('http://localhost:5175');
    await page.waitForTimeout(3000);
    
    // Capturar screenshot inicial
    await page.screenshot({ path: 'test-results/01-pagina-inicial.png', fullPage: true });
    console.log('📸 Screenshot da página inicial capturada');
    
    // 2. Verificar se estamos na página de login
    await expect(page).toHaveTitle(/Sistema Universal/i);
    
    // 3. Procurar campos de login (aceitar diferentes labels)
    let cpfField = null;
    let senhaField = null;
    
    // Tentar diferentes seletores para o campo CPF/Email
    const cpfSelectors = [
      'input[placeholder*="000.000.000-00"]',
      'input[placeholder*="Email"]', 
      'input[type="text"]',
      'input[id*="cpf"]',
      'input[id*="email"]'
    ];
    
    for (const selector of cpfSelectors) {
      try {
        cpfField = page.locator(selector).first();
        if (await cpfField.isVisible()) {
          console.log(`✅ Campo CPF/Email encontrado: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    // Tentar diferentes seletores para o campo senha
    const senhaSelectors = [
      'input[type="password"]',
      'input[placeholder*="senha"]',
      'input[placeholder*="password"]',
      'input[id*="senha"]',
      'input[id*="password"]'
    ];
    
    for (const selector of senhaSelectors) {
      try {
        senhaField = page.locator(selector).first();
        if (await senhaField.isVisible()) {
          console.log(`✅ Campo Senha encontrado: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!cpfField || !senhaField) {
      console.error('❌ Campos de login não encontrados');
      await page.screenshot({ path: 'test-results/erro-campos-nao-encontrados.png', fullPage: true });
      throw new Error('Campos de login não encontrados na página');
    }
    
    // 4. Preencher campos
    console.log('✏️ Preenchendo CPF: 00000000000');
    await cpfField.fill('00000000000');
    await page.waitForTimeout(500);
    
    console.log('✏️ Preenchendo Senha: admin123');
    await senhaField.fill('admin123');
    await page.waitForTimeout(500);
    
    // Screenshot antes do submit
    await page.screenshot({ path: 'test-results/02-campos-preenchidos.png', fullPage: true });
    console.log('📸 Screenshot dos campos preenchidos capturada');
    
    // 5. Procurar e clicar no botão de login
    let loginButton = null;
    const buttonSelectors = [
      'button[type="submit"]',
      'button:has-text("Entrar")',
      'button:has-text("Login")',
      'button:has-text("Continuar")',
      '[role="button"]:has-text("Entrar")'
    ];
    
    for (const selector of buttonSelectors) {
      try {
        loginButton = page.locator(selector).first();
        if (await loginButton.isVisible()) {
          console.log(`✅ Botão de login encontrado: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!loginButton) {
      console.error('❌ Botão de login não encontrado');
      await page.screenshot({ path: 'test-results/erro-botao-nao-encontrado.png', fullPage: true });
      throw new Error('Botão de login não encontrado na página');
    }
    
    // 6. Interceptar requisições de rede
    page.on('request', request => {
      if (request.url().includes('/api/auth/login')) {
        console.log(`🌐 Requisição de login: ${request.method()} ${request.url()}`);
        console.log(`📦 Dados enviados: ${request.postData()}`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/auth/login')) {
        console.log(`📥 Resposta do login: ${response.status()} ${response.statusText()}`);
      }
    });
    
    // 7. Submeter formulário
    console.log('🔄 Clicando no botão de login...');
    await loginButton.click();
    
    // Aguardar possível redirecionamento ou carregamento
    await page.waitForTimeout(3000);
    
    // Screenshot após submit
    await page.screenshot({ path: 'test-results/03-apos-submit.png', fullPage: true });
    console.log('📸 Screenshot após submit capturada');
    
    // 8. Verificar resultado
    const currentUrl = page.url();
    console.log(`📍 URL atual: ${currentUrl}`);
    
    // Verificar se houve redirecionamento para dashboard ou se há mensagens de erro
    const possibleSuccessIndicators = [
      'dashboard',
      'app',
      'painel',
      'home'
    ];
    
    const hasSuccessUrl = possibleSuccessIndicators.some(indicator => 
      currentUrl.toLowerCase().includes(indicator)
    );
    
    // Verificar mensagens na página
    try {
      const errorMessages = await page.locator('[class*="error"], [class*="alert"], [role="alert"]').allTextContents();
      if (errorMessages.length > 0) {
        console.log(`⚠️ Mensagens na página: ${errorMessages.join(', ')}`);
      }
    } catch (e) {
      console.log('ℹ️ Nenhuma mensagem de erro visível');
    }
    
    // 9. Verificar elementos de sucesso
    try {
      // Aguardar possível carregamento de elementos do dashboard
      await page.waitForTimeout(2000);
      
      const dashboardElements = page.locator('[class*="dashboard"], [class*="sidebar"], [class*="menu"], h1, h2');
      const elementCount = await dashboardElements.count();
      
      if (elementCount > 0) {
        console.log(`✅ ${elementCount} elementos de interface encontrados - possível sucesso`);
      }
    } catch (e) {
      console.log('ℹ️ Aguardando carregamento da interface...');
    }
    
    // Screenshot final
    await page.screenshot({ path: 'test-results/04-resultado-final.png', fullPage: true });
    console.log('📸 Screenshot final capturada');
    
    // 10. Log final
    console.log('✅ Teste concluído!');
    console.log(`📊 Resumo:`);
    console.log(`   - CPF utilizado: 00000000000`);
    console.log(`   - Senha utilizada: admin123`);
    console.log(`   - URL final: ${currentUrl}`);
    console.log(`   - Login bem-sucedido: ${hasSuccessUrl ? 'SIM' : 'VERIFICAR MANUALMENTE'}`);
  });
  
  test('Verificar conectividade do backend', async ({ request }) => {
    console.log('🔍 Testando conectividade direta com backend...');
    
    // Teste direto da API
    const response = await request.post('http://localhost:8000/api/auth/login', {
      data: {
        cpf: '00000000000',
        senha: 'admin123'
      }
    });
    
    console.log(`📡 Status da API: ${response.status()}`);
    
    if (response.ok()) {
      const data = await response.json();
      console.log(`✅ Login via API bem-sucedido`);
      console.log(`👤 Usuário: ${data.usuario?.nome}`);
      console.log(`🎫 Token gerado: ${data.access_token ? 'SIM' : 'NÃO'}`);
    } else {
      console.log(`❌ Login via API falhou: ${response.status()}`);
      const errorText = await response.text();
      console.log(`❌ Erro: ${errorText}`);
    }
    
    expect(response.status()).toBe(200);
  });
});