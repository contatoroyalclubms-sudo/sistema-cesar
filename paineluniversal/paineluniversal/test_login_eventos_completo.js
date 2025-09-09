/**
 * TESTE COMPLETO - LOGIN E GESTÃO DE EVENTOS
 * Sistema Universal v5 - Engenharia Reversa MEEP
 * Testa compatibilidade frontend-backend-database
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function testarSistemaCompleto() {
  console.log('🚀 INICIANDO TESTE COMPLETO - LOGIN E GESTÃO DE EVENTOS');
  console.log('='.repeat(70));

  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: './test-results/videos/' }
  });
  
  const page = await context.newPage();
  
  let errosEncontrados = [];
  let sucessos = [];

  // Interceptar erros de console
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errosEncontrados.push({
        tipo: 'Console Error',
        mensagem: msg.text(),
        timestamp: new Date().toISOString()
      });
      console.log('❌ ERRO CONSOLE:', msg.text());
    }
  });

  // Interceptar erros de rede
  page.on('response', (response) => {
    if (response.status() >= 400) {
      errosEncontrados.push({
        tipo: 'Network Error',
        url: response.url(),
        status: response.status(),
        statusText: response.statusText(),
        timestamp: new Date().toISOString()
      });
      console.log(`❌ ERRO REDE: ${response.status()} - ${response.url()}`);
    }
  });

  try {
    console.log('📱 FASE 1: NAVEGAÇÃO INICIAL');
    
    // 1. Carregar página inicial
    await page.goto('http://localhost:5177');
    await page.waitForTimeout(2000);
    
    await page.screenshot({ path: './screenshot_01_inicial.png' });
    sucessos.push('✅ Página inicial carregada');
    
    // Verificar se está na landing page ou já no login
    const isLandingPage = await page.$('text=Entrar') !== null;
    
    if (isLandingPage) {
      console.log('🏠 Detectada landing page - clicando em Entrar');
      await page.click('text=Entrar');
      await page.waitForTimeout(1500);
    }

    // 2. Aguardar página de login
    console.log('🔐 FASE 2: TESTE DE LOGIN');
    
    await page.waitForSelector('#cpf, input[placeholder*="CPF"], input[name="cpf"]', { timeout: 10000 });
    await page.screenshot({ path: './screenshot_02_login.png' });
    sucessos.push('✅ Página de login acessível');

    // 3. Preencher credenciais
    console.log('📝 Preenchendo credenciais: CPF 00000000000, Senha 0000');
    
    // Tentar diferentes seletores para CPF
    const cpfField = await page.$('#cpf') || 
                     await page.$('input[placeholder*="CPF"]') ||
                     await page.$('input[name="cpf"]') ||
                     await page.$('input[type="text"]');
    
    if (cpfField) {
      await cpfField.fill('00000000000');
      sucessos.push('✅ CPF preenchido');
    } else {
      errosEncontrados.push({
        tipo: 'UI Error',
        mensagem: 'Campo CPF não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    // Tentar diferentes seletores para senha
    const senhaField = await page.$('#senha') || 
                       await page.$('input[type="password"]') ||
                       await page.$('input[placeholder*="senha"]') ||
                       await page.$('input[placeholder*="Senha"]');
    
    if (senhaField) {
      await senhaField.fill('0000');
      sucessos.push('✅ Senha preenchida');
    } else {
      errosEncontrados.push({
        tipo: 'UI Error',
        mensagem: 'Campo senha não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    await page.screenshot({ path: './screenshot_03_preenchido.png' });

    // 4. Tentar fazer login
    console.log('🚀 Tentando fazer login...');
    
    const loginButton = await page.$('button[type="submit"]') ||
                        await page.$('button:has-text("Entrar")') ||
                        await page.$('button:has-text("Login")') ||
                        await page.$('.login-button');

    if (loginButton) {
      await loginButton.click();
      sucessos.push('✅ Botão de login clicado');
    } else {
      errosEncontrados.push({
        tipo: 'UI Error',
        mensagem: 'Botão de login não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    // 5. Aguardar resultado do login
    await page.waitForTimeout(3000);

    // Verificar se login foi bem-sucedido
    const currentUrl = page.url();
    console.log('🌐 URL atual após login:', currentUrl);

    if (currentUrl.includes('/app') || currentUrl.includes('/dashboard') || 
        await page.$('text=Dashboard') || await page.$('text=Sair') ||
        await page.$('.sidebar') || await page.$('.menu-lateral')) {
      
      sucessos.push('✅ Login realizado com sucesso');
      console.log('✅ LOGIN BEM-SUCEDIDO!');
      
      await page.screenshot({ path: './screenshot_04_dashboard.png' });

      // 6. TESTE DA GESTÃO DE EVENTOS
      console.log('📅 FASE 3: TESTE GESTÃO DE EVENTOS');

      // Procurar menu de eventos
      const eventosMenu = await page.$('text=Eventos') ||
                          await page.$('a[href*="eventos"]') ||
                          await page.$('.nav-item:has-text("Eventos")') ||
                          await page.$('li:has-text("Eventos")');

      if (eventosMenu) {
        await eventosMenu.click();
        await page.waitForTimeout(2000);
        sucessos.push('✅ Menu Eventos acessado');
        
        await page.screenshot({ path: './screenshot_05_eventos.png' });

        // Verificar se página de eventos carregou
        if (page.url().includes('eventos') || await page.$('text=Gestão de Eventos') || 
            await page.$('.eventos-container') || await page.$('table')) {
          
          sucessos.push('✅ Página de Gestão de Eventos carregada');
          
          // Testar criação de evento
          const novoEventoBtn = await page.$('text=Novo Evento') ||
                                await page.$('button:has-text("Criar")') ||
                                await page.$('.btn-novo') ||
                                await page.$('[data-testid="novo-evento"]');

          if (novoEventoBtn) {
            await novoEventoBtn.click();
            await page.waitForTimeout(1500);
            sucessos.push('✅ Modal/formulário de novo evento aberto');
            
            await page.screenshot({ path: './screenshot_06_novo_evento.png' });

            // Preencher dados básicos do evento
            const nomeEvento = await page.$('#nome') || 
                              await page.$('input[name="nome"]') ||
                              await page.$('input[placeholder*="nome"]');
            
            if (nomeEvento) {
              await nomeEvento.fill('Evento Teste MEEP - ' + new Date().toLocaleString());
              sucessos.push('✅ Nome do evento preenchido');
            }

            // Tentar salvar
            const salvarBtn = await page.$('button[type="submit"]') ||
                             await page.$('button:has-text("Salvar")') ||
                             await page.$('button:has-text("Criar")');

            if (salvarBtn) {
              await salvarBtn.click();
              await page.waitForTimeout(2000);
              sucessos.push('✅ Tentativa de salvar evento executada');
              
              await page.screenshot({ path: './screenshot_07_evento_salvo.png' });
            }
          } else {
            errosEncontrados.push({
              tipo: 'UI Error',
              mensagem: 'Botão "Novo Evento" não encontrado',
              timestamp: new Date().toISOString()
            });
          }

        } else {
          errosEncontrados.push({
            tipo: 'Navigation Error',
            mensagem: 'Página de Gestão de Eventos não carregou corretamente',
            timestamp: new Date().toISOString()
          });
        }

      } else {
        errosEncontrados.push({
          tipo: 'UI Error',
          mensagem: 'Menu Eventos não encontrado no dashboard',
          timestamp: new Date().toISOString()
        });
      }

    } else {
      errosEncontrados.push({
        tipo: 'Authentication Error',
        mensagem: 'Login falhou - não foi redirecionado para dashboard',
        url: currentUrl,
        timestamp: new Date().toISOString()
      });
      
      await page.screenshot({ path: './screenshot_04_login_falhou.png' });
    }

    // 7. TESTE FINAL - Verificar localStorage e sessão
    console.log('🔍 FASE 4: VERIFICAÇÃO DE SESSÃO');
    
    const token = await page.evaluate(() => localStorage.getItem('token') || localStorage.getItem('access_token'));
    const userData = await page.evaluate(() => localStorage.getItem('user') || localStorage.getItem('userData'));
    
    if (token) {
      sucessos.push('✅ Token JWT encontrado no localStorage');
      console.log('🔐 Token encontrado:', token.substring(0, 50) + '...');
    } else {
      errosEncontrados.push({
        tipo: 'Session Error',
        mensagem: 'Token JWT não encontrado no localStorage',
        timestamp: new Date().toISOString()
      });
    }

    if (userData) {
      sucessos.push('✅ Dados do usuário encontrados no localStorage');
      console.log('👤 Dados do usuário:', JSON.parse(userData));
    }

    await page.screenshot({ path: './screenshot_08_final.png' });

  } catch (error) {
    errosEncontrados.push({
      tipo: 'Runtime Error',
      mensagem: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
    
    console.log('❌ ERRO DURANTE EXECUÇÃO:', error.message);
    await page.screenshot({ path: './screenshot_erro.png' });
  }

  await browser.close();

  // 8. GERAR RELATÓRIO
  console.log('\n' + '='.repeat(70));
  console.log('📊 RELATÓRIO FINAL DE TESTES');
  console.log('='.repeat(70));
  
  console.log(`\n✅ SUCESSOS (${sucessos.length}):`);
  sucessos.forEach((sucesso, index) => {
    console.log(`${index + 1}. ${sucesso}`);
  });

  console.log(`\n❌ ERROS ENCONTRADOS (${errosEncontrados.length}):`);
  errosEncontrados.forEach((erro, index) => {
    console.log(`${index + 1}. [${erro.tipo}] ${erro.mensagem}`);
    if (erro.url) console.log(`   URL: ${erro.url}`);
    if (erro.status) console.log(`   Status: ${erro.status}`);
  });

  // Salvar relatório em arquivo
  const relatorio = {
    dataHora: new Date().toISOString(),
    totalSucessos: sucessos.length,
    totalErros: errosEncontrados.length,
    sucessos: sucessos,
    erros: errosEncontrados,
    status: errosEncontrados.length === 0 ? 'SUCESSO_COMPLETO' : 'ERROS_ENCONTRADOS'
  };

  fs.writeFileSync('./RELATORIO_TESTE_LOGIN_EVENTOS.json', JSON.stringify(relatorio, null, 2));
  
  console.log(`\n📋 Relatório salvo em: RELATORIO_TESTE_LOGIN_EVENTOS.json`);
  
  if (errosEncontrados.length === 0) {
    console.log('\n🎉 TESTE COMPLETO: SUCESSO! Sistema funcionando perfeitamente.');
  } else {
    console.log(`\n⚠️ TESTE COMPLETO: ${errosEncontrados.length} erro(s) encontrado(s). Correções necessárias.`);
  }

  return relatorio;
}

// Executar teste
testarSistemaCompleto().catch(console.error);