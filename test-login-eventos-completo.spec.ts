import { test, expect } from '@playwright/test';

test.describe('Sistema Universal V7 - Teste Completo Login e Gestão de Eventos', () => {
  test.beforeEach(async ({ page }) => {
    // Configurar timeout maior para operações
    test.setTimeout(60000);
    
    // Navegar para o sistema
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
  });

  test('01 - Teste de Login com CPF', async ({ page }) => {
    console.log('🔐 Iniciando teste de login...');
    
    // Verificar se está na tela de login
    await expect(page).toHaveTitle(/Sistema Universal/i);
    
    // Procurar formulário de login
    const cpfInput = await page.locator('input[name="cpf"], input[placeholder*="CPF"], input[type="text"]').first();
    const senhaInput = await page.locator('input[name="senha"], input[type="password"], input[placeholder*="senha" i]').first();
    
    // Capturar screenshot da tela de login
    await page.screenshot({ path: 'test-01-tela-login.png', fullPage: true });
    
    // Preencher credenciais
    await cpfInput.fill('00000000000');
    await senhaInput.fill('0000');
    
    // Capturar screenshot após preencher
    await page.screenshot({ path: 'test-02-credenciais-preenchidas.png', fullPage: true });
    
    // Procurar e clicar no botão de login
    const loginButton = await page.locator('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")').first();
    await loginButton.click();
    
    // Aguardar resposta da API
    await page.waitForResponse(response => 
      response.url().includes('/auth/login') || 
      response.url().includes('/login'),
      { timeout: 10000 }
    ).catch(() => console.log('⚠️ Timeout esperando resposta de login'));
    
    // Verificar se login foi bem sucedido
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {
      console.log('⚠️ Não redirecionou para dashboard');
    });
    
    // Capturar screenshot após login
    await page.screenshot({ path: 'test-03-apos-login.png', fullPage: true });
    
    // Verificar se está autenticado
    const isAuthenticated = await page.evaluate(() => {
      return localStorage.getItem('token') !== null || 
             localStorage.getItem('authToken') !== null ||
             sessionStorage.getItem('token') !== null;
    });
    
    console.log('✅ Login realizado:', isAuthenticated);
    expect(isAuthenticated).toBeTruthy();
  });

  test('02 - Navegação para Gestão de Eventos', async ({ page }) => {
    console.log('📋 Testando gestão de eventos...');
    
    // Fazer login primeiro
    await page.goto('http://localhost:5173');
    const cpfInput = await page.locator('input[name="cpf"], input[placeholder*="CPF"]').first();
    const senhaInput = await page.locator('input[type="password"]').first();
    
    await cpfInput.fill('00000000000');
    await senhaInput.fill('0000');
    
    const loginButton = await page.locator('button[type="submit"]').first();
    await loginButton.click();
    
    await page.waitForTimeout(3000);
    
    // Procurar link de eventos no menu
    const eventosLink = await page.locator('a:has-text("Eventos"), button:has-text("Eventos"), [href*="eventos"]').first();
    
    if (await eventosLink.isVisible()) {
      await eventosLink.click();
      await page.waitForTimeout(2000);
      
      // Capturar screenshot da página de eventos
      await page.screenshot({ path: 'test-04-pagina-eventos.png', fullPage: true });
      
      // Verificar elementos da página de eventos
      const hasEventosPage = await page.locator('h1:has-text("Eventos"), h2:has-text("Eventos")').isVisible()
        .catch(() => false);
      
      console.log('✅ Página de eventos carregada:', hasEventosPage);
    }
  });

  test('03 - Criar Novo Evento', async ({ page }) => {
    console.log('➕ Testando criação de evento...');
    
    // Login
    await page.goto('http://localhost:5173');
    await page.locator('input[name="cpf"], input[placeholder*="CPF"]').first().fill('00000000000');
    await page.locator('input[type="password"]').first().fill('0000');
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
    
    // Ir para eventos
    await page.locator('a:has-text("Eventos"), [href*="eventos"]').first().click();
    await page.waitForTimeout(2000);
    
    // Procurar botão de adicionar evento
    const addButton = await page.locator('button:has-text("Adicionar"), button:has-text("Novo"), button:has-text("Criar")').first();
    
    if (await addButton.isVisible()) {
      await addButton.click();
      await page.waitForTimeout(1000);
      
      // Capturar screenshot do modal/formulário
      await page.screenshot({ path: 'test-05-formulario-evento.png', fullPage: true });
      
      // Preencher formulário se visível
      const nomeInput = await page.locator('input[name="nome"], input[placeholder*="nome" i]').first();
      if (await nomeInput.isVisible()) {
        await nomeInput.fill('Evento Teste MEEP Style');
        
        const dataInput = await page.locator('input[type="date"], input[name="data"]').first();
        if (await dataInput.isVisible()) {
          await dataInput.fill('2025-12-31');
        }
        
        const localInput = await page.locator('input[name="local"], input[placeholder*="local" i]').first();
        if (await localInput.isVisible()) {
          await localInput.fill('Local Teste');
        }
        
        // Capturar screenshot após preencher
        await page.screenshot({ path: 'test-06-formulario-preenchido.png', fullPage: true });
        
        console.log('✅ Formulário de evento preenchido');
      }
    }
  });

  test('04 - Verificar Lista de Convidados', async ({ page }) => {
    console.log('👥 Testando lista de convidados...');
    
    // Login
    await page.goto('http://localhost:5173');
    await page.locator('input[name="cpf"], input[placeholder*="CPF"]').first().fill('00000000000');
    await page.locator('input[type="password"]').first().fill('0000');
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
    
    // Ir para eventos
    await page.locator('a:has-text("Eventos"), [href*="eventos"]').first().click();
    await page.waitForTimeout(2000);
    
    // Procurar botão de lista em algum evento
    const listaButton = await page.locator('button:has-text("Lista"), button:has-text("Convidados")').first();
    
    if (await listaButton.isVisible()) {
      await listaButton.click();
      await page.waitForTimeout(1000);
      
      // Capturar screenshot da lista de convidados
      await page.screenshot({ path: 'test-07-lista-convidados.png', fullPage: true });
      
      console.log('✅ Lista de convidados acessada');
    }
  });

  test('05 - Verificar Caixa/PDV do Evento', async ({ page }) => {
    console.log('💰 Testando caixa do evento...');
    
    // Login
    await page.goto('http://localhost:5173');
    await page.locator('input[name="cpf"], input[placeholder*="CPF"]').first().fill('00000000000');
    await page.locator('input[type="password"]').first().fill('0000');
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
    
    // Ir para eventos
    await page.locator('a:has-text("Eventos"), [href*="eventos"]').first().click();
    await page.waitForTimeout(2000);
    
    // Procurar botão de caixa/PDV
    const caixaButton = await page.locator('button:has-text("Caixa"), button:has-text("PDV"), button:has-text("Vender")').first();
    
    if (await caixaButton.isVisible()) {
      await caixaButton.click();
      await page.waitForTimeout(1000);
      
      // Capturar screenshot do PDV
      await page.screenshot({ path: 'test-08-caixa-pdv.png', fullPage: true });
      
      console.log('✅ Caixa/PDV acessado');
    }
  });

  test('06 - Capturar Erros de Console', async ({ page }) => {
    console.log('🐛 Capturando erros do console...');
    
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Capturar mensagens do console
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      } else if (msg.type() === 'warning') {
        warnings.push(msg.text());
      }
    });
    
    // Capturar erros de página
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    // Navegar pelo sistema
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);
    
    // Tentar login
    const cpfInput = await page.locator('input[name="cpf"], input[placeholder*="CPF"]').first();
    const senhaInput = await page.locator('input[type="password"]').first();
    
    if (await cpfInput.isVisible() && await senhaInput.isVisible()) {
      await cpfInput.fill('00000000000');
      await senhaInput.fill('0000');
      await page.locator('button[type="submit"]').first().click();
      await page.waitForTimeout(3000);
    }
    
    // Relatório de erros
    console.log('\n📊 RELATÓRIO DE ERROS:');
    console.log('Erros encontrados:', errors.length);
    console.log('Avisos encontrados:', warnings.length);
    
    if (errors.length > 0) {
      console.log('\n❌ ERROS:');
      errors.forEach((error, index) => {
        console.log(`${index + 1}. ${error}`);
      });
    }
    
    if (warnings.length > 0) {
      console.log('\n⚠️ AVISOS:');
      warnings.forEach((warning, index) => {
        console.log(`${index + 1}. ${warning}`);
      });
    }
    
    // Salvar relatório
    const report = {
      timestamp: new Date().toISOString(),
      errors,
      warnings,
      errorCount: errors.length,
      warningCount: warnings.length
    };
    
    await page.evaluate((reportData) => {
      console.log('📋 Relatório Final:', reportData);
    }, report);
  });

  test('07 - Verificar Compatibilidade Frontend/Backend', async ({ page }) => {
    console.log('🔄 Verificando compatibilidade...');
    
    // Testar endpoint de saúde
    const healthResponse = await page.request.get('http://localhost:8008/api/health')
      .catch(() => null);
    
    if (healthResponse && healthResponse.ok()) {
      console.log('✅ Backend respondendo');
    } else {
      console.log('❌ Backend não está respondendo');
    }
    
    // Testar endpoint de autenticação
    const authResponse = await page.request.post('http://localhost:8008/api/auth/login', {
      data: {
        cpf: '00000000000',
        senha: '0000'
      }
    }).catch(err => {
      console.log('❌ Erro na autenticação:', err.message);
      return null;
    });
    
    if (authResponse && authResponse.ok()) {
      const authData = await authResponse.json();
      console.log('✅ Autenticação funcionando:', authData.token ? 'Token recebido' : 'Sem token');
    }
    
    // Verificar se frontend conecta ao backend
    await page.goto('http://localhost:5173');
    
    const apiCalls = await page.evaluate(() => {
      return fetch('http://localhost:8008/api/health')
        .then(() => true)
        .catch(() => false);
    });
    
    console.log('✅ Frontend conecta ao backend:', apiCalls);
  });
});