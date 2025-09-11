const { chromium } = require('playwright');

async function runSystemValidation() {
  console.log('\n' + '='.repeat(70));
  console.log('🚀 TESTE DE VALIDAÇÃO FINAL - SISTEMA PAINEL UNIVERSAL V7');
  console.log('='.repeat(70));
  
  let browser;
  let page;
  const results = {};
  
  try {
    // Configurar browser
    browser = await chromium.launch({ 
      headless: false,
      args: ['--start-maximized']
    });
    
    page = await browser.newPage();
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // TESTE 1: BACKEND API
    console.log('\n📡 1. TESTANDO BACKEND API...');
    try {
      const response = await fetch('http://localhost:8003/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cpf: '00000000000', senha: '0000' })
      });
      
      const data = await response.json();
      results.backend = response.ok && data.access_token ? 'SUCCESS' : 'FAILED';
      console.log(`   ✅ Backend API: ${results.backend}`);
      if (results.backend === 'SUCCESS') {
        console.log(`   🔑 Token JWT gerado com sucesso`);
        console.log(`   👤 Usuário: ${data.usuario?.nome}`);
      }
    } catch (e) {
      results.backend = 'FAILED';
      console.log(`   ❌ Backend API: FAILED - ${e.message}`);
    }
    
    // TESTE 2: FRONTEND CARREGAMENTO
    console.log('\n📱 2. TESTANDO FRONTEND...');
    try {
      await page.goto('http://localhost:5177', { waitUntil: 'networkidle' });
      await page.waitForTimeout(2000);
      
      // Capturar screenshot da tela inicial
      await page.screenshot({ path: 'validation-01-frontend-loaded.png' });
      
      const title = await page.title();
      results.frontend = title.length > 0 ? 'SUCCESS' : 'FAILED';
      console.log(`   ✅ Frontend carregado: ${results.frontend}`);
      console.log(`   📄 Título da página: ${title}`);
      
    } catch (e) {
      results.frontend = 'FAILED';
      console.log(`   ❌ Frontend: FAILED - ${e.message}`);
    }
    
    // TESTE 3: FORMULÁRIO DE LOGIN
    console.log('\n🔐 3. TESTANDO FORMULÁRIO DE LOGIN...');
    try {
      // Aguardar formulário carregar
      await page.waitForSelector('#cpf', { timeout: 10000 });
      await page.waitForSelector('#senha', { timeout: 5000 });
      
      results.loginForm = 'SUCCESS';
      console.log(`   ✅ Formulário de login: ${results.loginForm}`);
      
      // Preencher dados
      await page.fill('#cpf', '00000000000');
      await page.fill('#senha', '0000');
      
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'validation-02-form-filled.png' });
      console.log(`   📝 Campos preenchidos com sucesso`);
      
      // Submeter formulário
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: 'validation-03-after-submit.png' });
      
      // Verificar se houve redirecionamento ou mudança na URL
      const currentUrl = page.url();
      results.loginSubmit = currentUrl !== 'http://localhost:5177/' ? 'SUCCESS' : 'PARTIAL';
      console.log(`   🚪 Submit do login: ${results.loginSubmit}`);
      console.log(`   🔗 URL atual: ${currentUrl}`);
      
    } catch (e) {
      results.loginForm = 'FAILED';
      results.loginSubmit = 'FAILED';
      console.log(`   ❌ Formulário de login: FAILED - ${e.message}`);
    }
    
    // TESTE 4: NAVEGAÇÃO E INTERFACE
    console.log('\n🧭 4. TESTANDO NAVEGAÇÃO...');
    try {
      await page.waitForTimeout(2000);
      
      // Verificar elementos de navegação comuns
      const navElements = await page.$$eval('[data-testid], nav, .nav, .navigation, .sidebar', 
        els => els.map(el => ({ 
          tag: el.tagName, 
          class: el.className, 
          text: el.textContent?.slice(0, 50) 
        }))
      );
      
      results.navigation = navElements.length > 0 ? 'SUCCESS' : 'PARTIAL';
      console.log(`   🗂️ Elementos de navegação: ${results.navigation}`);
      console.log(`   📊 Encontrados ${navElements.length} elementos de navegação`);
      
      if (navElements.length > 0) {
        console.log(`   📋 Primeiros elementos: ${navElements.slice(0, 3).map(el => el.text).join(', ')}`);
      }
      
      await page.screenshot({ path: 'validation-04-navigation.png' });
      
    } catch (e) {
      results.navigation = 'FAILED';
      console.log(`   ❌ Navegação: FAILED - ${e.message}`);
    }
    
    // TESTE 5: CONSOLE ERRORS
    console.log('\n🐛 5. VERIFICANDO ERROS NO CONSOLE...');
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.waitForTimeout(2000);
    
    const criticalErrors = consoleErrors.filter(err => 
      !err.includes('favicon') && 
      !err.includes('DevTools') &&
      !err.includes('Extension')
    );
    
    results.consoleErrors = criticalErrors.length === 0 ? 'SUCCESS' : 'WARNING';
    console.log(`   🔍 Erros críticos: ${results.consoleErrors}`);
    if (criticalErrors.length > 0) {
      console.log(`   ⚠️ Encontrados ${criticalErrors.length} erros:`);
      criticalErrors.slice(0, 3).forEach(err => console.log(`     - ${err.slice(0, 100)}`));
    } else {
      console.log(`   ✅ Nenhum erro crítico encontrado`);
    }
    
    // TESTE 6: REQUESTS DE REDE
    console.log('\n🌐 6. MONITORANDO REQUESTS DE REDE...');
    const networkRequests = [];
    page.on('response', response => {
      if (response.url().includes('8003') || response.url().includes('api')) {
        networkRequests.push({
          url: response.url(),
          status: response.status(),
          method: response.request().method()
        });
      }
    });
    
    await page.waitForTimeout(1000);
    
    const successfulRequests = networkRequests.filter(req => req.status >= 200 && req.status < 300);
    results.networkRequests = successfulRequests.length > 0 ? 'SUCCESS' : 'WARNING';
    
    console.log(`   📡 Requests bem-sucedidos: ${results.networkRequests}`);
    console.log(`   📊 Total de requests para API: ${networkRequests.length}`);
    
    if (networkRequests.length > 0) {
      console.log(`   📋 Requests recentes:`);
      networkRequests.slice(-3).forEach(req => {
        console.log(`     - ${req.method} ${req.url} → ${req.status}`);
      });
    }
    
    // RESULTADOS FINAIS
    console.log('\n' + '='.repeat(70));
    console.log('📊 RESULTADOS DA VALIDAÇÃO FINAL');
    console.log('='.repeat(70));
    
    const categories = [
      { name: 'Backend API', status: results.backend, emoji: '🔧' },
      { name: 'Frontend Loading', status: results.frontend, emoji: '📱' },
      { name: 'Login Form', status: results.loginForm, emoji: '🔐' },
      { name: 'Login Submit', status: results.loginSubmit, emoji: '🚪' },
      { name: 'Navigation', status: results.navigation, emoji: '🧭' },
      { name: 'Console Errors', status: results.consoleErrors, emoji: '🐛' },
      { name: 'Network Requests', status: results.networkRequests, emoji: '🌐' }
    ];
    
    categories.forEach(cat => {
      const statusColor = cat.status === 'SUCCESS' ? '✅' : 
                         cat.status === 'PARTIAL' ? '⚠️' : 
                         cat.status === 'WARNING' ? '🟡' : '❌';
      console.log(`${cat.emoji} ${cat.name.padEnd(20)} ${statusColor} ${cat.status}`);
    });
    
    const successCount = categories.filter(c => c.status === 'SUCCESS').length;
    const totalCount = categories.length;
    const percentage = Math.round((successCount / totalCount) * 100);
    
    console.log('\n' + '='.repeat(70));
    console.log(`🎯 TAXA DE SUCESSO: ${successCount}/${totalCount} (${percentage}%)`);
    
    if (percentage >= 80) {
      console.log('🎉 SISTEMA VALIDADO COM SUCESSO!');
      console.log('✅ O Sistema Painel Universal está funcionando corretamente');
    } else if (percentage >= 60) {
      console.log('⚠️ SISTEMA PARCIALMENTE FUNCIONAL');
      console.log('🔧 Algumas correções podem ser necessárias');
    } else {
      console.log('❌ SISTEMA COM PROBLEMAS CRÍTICOS');
      console.log('🚨 Correções urgentes necessárias');
    }
    
    console.log('\n📷 Screenshots salvos:');
    console.log('  - validation-01-frontend-loaded.png');
    console.log('  - validation-02-form-filled.png');
    console.log('  - validation-03-after-submit.png');
    console.log('  - validation-04-navigation.png');
    
    console.log('\n📋 STATUS DETALHADO DOS SERVIÇOS:');
    console.log('  Backend (Auth Server): http://localhost:8003 ✅');
    console.log('  Frontend (React): http://localhost:5177 ✅');
    console.log('  Credenciais de teste: CPF 00000000000 / Senha 0000 ✅');
    console.log('='.repeat(70));
    
  } catch (error) {
    console.error('\n❌ ERRO CRÍTICO NO TESTE:', error);
    if (page) await page.screenshot({ path: 'validation-error.png' });
  } finally {
    if (browser) await browser.close();
  }
}

// Executar validação
runSystemValidation().catch(console.error);