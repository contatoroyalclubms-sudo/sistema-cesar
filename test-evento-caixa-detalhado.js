const { chromium } = require('playwright');

(async () => {
  console.log('🔍 TESTE DETALHADO - MÓDULO EVENTO/CAIXA');
  console.log('=========================================\n');
  
  const browser = await chromium.launch({
    headless: false,
    slowMo: 1000
  });
  
  const page = await browser.newContext().then(c => c.newPage());
  
  // Habilitar logs do console do navegador
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('❌ ERRO NO CONSOLE:', msg.text());
    }
  });
  
  // Monitorar requisições de rede
  page.on('requestfailed', request => {
    console.log('❌ REQUISIÇÃO FALHOU:', request.url(), request.failure().errorText);
  });
  
  try {
    // PASSO 1: ACESSAR O SISTEMA
    console.log('📌 PASSO 1: Procurando porta do frontend...');
    const ports = [5174, 5173, 5175, 5176, 5177, 5178];
    let systemUrl = null;
    
    for (const port of ports) {
      try {
        const testUrl = `http://localhost:${port}`;
        console.log(`   Testando porta ${port}...`);
        await page.goto(testUrl, { timeout: 3000, waitUntil: 'domcontentloaded' });
        systemUrl = testUrl;
        console.log(`   ✅ Sistema encontrado na porta ${port}`);
        break;
      } catch (e) {
        continue;
      }
    }
    
    if (!systemUrl) {
      throw new Error('Sistema não encontrado em nenhuma porta');
    }
    
    await page.waitForTimeout(2000);
    console.log('   ✅ Sistema carregado\n');
    
    // PASSO 2: FAZER LOGIN
    console.log('📌 PASSO 2: Fazendo login...');
    
    // Verificar se já está logado ou precisa fazer login
    const needsLogin = await page.locator('input[type="password"]').isVisible().catch(() => false);
    
    if (needsLogin) {
      await page.fill('input[placeholder*="CPF"], input[name="cpf"], input[type="text"]', '00000000000');
      await page.fill('input[type="password"]', '0000');
      await page.click('button[type="submit"]');
      console.log('   ✅ Login realizado');
    } else {
      console.log('   ℹ️ Já está logado');
    }
    
    await page.waitForTimeout(3000);
    
    // PASSO 3: NAVEGAR PARA EVENTOS
    console.log('\n📌 PASSO 3: Navegando para módulo de Eventos...');
    
    // Tentar várias formas de acessar eventos
    const clicked = await page.locator('a[href*="eventos"], button:has-text("Eventos"), nav >> text=Eventos').first().click().then(() => true).catch(() => false);
    
    if (!clicked) {
      await page.goto(`${systemUrl}/eventos`);
    }
    
    await page.waitForTimeout(2000);
    console.log('   ✅ Página de eventos carregada\n');
    
    // PASSO 4: ABRIR MODAL DE CRIAÇÃO
    console.log('📌 PASSO 4: Abrindo formulário de novo evento...');
    
    await page.locator('button:has-text("Novo"), button:has-text("Criar"), button:has-text("Adicionar"), button >> svg').first().click();
    await page.waitForTimeout(1000);
    console.log('   ✅ Modal aberto\n');
    
    // PASSO 5: PREENCHER FORMULÁRIO
    console.log('📌 PASSO 5: Preenchendo formulário do evento...\n');
    
    // 5.1 - Nome do evento
    console.log('   📝 Campo: Nome do Evento');
    await page.fill('input[name="nome"], input[placeholder*="Nome"]', 'Evento Teste Caixa');
    console.log('      ✓ Preenchido: "Evento Teste Caixa"');
    
    // 5.2 - Descrição
    console.log('   📝 Campo: Descrição');
    const descricao = await page.locator('textarea[name="descricao"], textarea[placeholder*="Descrição"]').first();
    if (await descricao.isVisible()) {
      await descricao.fill('Teste completo do módulo evento com integração ao caixa');
      console.log('      ✓ Preenchido');
    }
    
    // 5.3 - Local
    console.log('   📝 Campo: Local');
    await page.fill('input[name="local"], input[placeholder*="Local"]', 'Centro de Convenções');
    console.log('      ✓ Preenchido: "Centro de Convenções"');
    
    // 5.4 - Endereço
    console.log('   📝 Campo: Endereço');
    const endereco = await page.locator('input[name="endereco"], input[placeholder*="Endereço"]').first();
    if (await endereco.isVisible()) {
      await endereco.fill('Rua Principal, 123');
      console.log('      ✓ Preenchido: "Rua Principal, 123"');
    }
    
    // 5.5 - DATAS (CRÍTICO!)
    console.log('\n   📝 CONFIGURAÇÃO DE DATAS (CRÍTICO):');
    
    const agora = new Date();
    const formatDate = (date) => {
      const pad = (n) => n.toString().padStart(2, '0');
      return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
    };
    
    // Definir datas com intervalos válidos
    const inicioVendas = new Date(agora.getTime() + 30 * 60 * 1000); // 30 min no futuro
    const fimVendas = new Date(agora.getTime() + 80 * 60 * 1000); // 1h20 no futuro
    const inicioEvento = new Date(agora.getTime() + 90 * 60 * 1000); // 1h30 no futuro
    const fimEvento = new Date(agora.getTime() + 270 * 60 * 1000); // 4h30 no futuro
    
    console.log('      Início Vendas:', inicioVendas.toLocaleString());
    console.log('      Fim Vendas:', fimVendas.toLocaleString());
    console.log('      Início Evento:', inicioEvento.toLocaleString());
    console.log('      Fim Evento:', fimEvento.toLocaleString());
    
    // Preencher datas
    await page.fill('input[name="data_inicio_vendas"]', formatDate(inicioVendas));
    console.log('      ✓ Data início vendas preenchida');
    
    await page.fill('input[name="data_fim_vendas"]', formatDate(fimVendas));
    console.log('      ✓ Data fim vendas preenchida');
    
    await page.fill('input[name="data_inicio_evento"]', formatDate(inicioEvento));
    console.log('      ✓ Data início evento preenchida');
    
    await page.fill('input[name="data_fim_evento"]', formatDate(fimEvento));
    console.log('      ✓ Data fim evento preenchida');
    
    // 5.6 - Capacidade
    console.log('\n   📝 Campo: Capacidade Máxima');
    const capacidade = await page.locator('input[name="capacidade_maxima"]').first();
    if (await capacidade.isVisible()) {
      await capacidade.fill('500');
      console.log('      ✓ Preenchido: 500');
    }
    
    // 5.7 - Limite de idade
    console.log('   📝 Campo: Limite de Idade');
    const limiteIdade = await page.locator('input[name="limite_idade"]').first();
    if (await limiteIdade.isVisible()) {
      await limiteIdade.fill('18');
      console.log('      ✓ Preenchido: 18');
    }
    
    // Screenshot do formulário preenchido
    await page.screenshot({ path: 'teste-evento-formulario-preenchido.png' });
    console.log('\n   📸 Screenshot do formulário salva\n');
    
    // PASSO 6: SALVAR EVENTO
    console.log('📌 PASSO 6: Tentando salvar o evento...');
    console.log('   ⏳ Clicando no botão salvar...');
    
    // Monitorar requisições de API
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/eventos') && 
      (response.request().method() === 'POST' || response.request().method() === 'PUT'),
      { timeout: 10000 }
    ).catch(() => null);
    
    // Clicar em salvar
    await page.locator('button:has-text("Salvar"), button:has-text("Criar"), button[type="submit"]').last().click();
    
    // Aguardar resposta
    console.log('   ⏳ Aguardando resposta da API...');
    const response = await responsePromise;
    
    if (response) {
      console.log('\n   📡 RESPOSTA DA API:');
      console.log('      Status:', response.status());
      console.log('      URL:', response.url());
      
      if (response.ok()) {
        console.log('      ✅ SUCESSO! Evento salvo');
        const data = await response.json();
        console.log('      ID do evento:', data.id || 'N/A');
      } else {
        console.log('      ❌ ERRO! Status:', response.status());
        try {
          const error = await response.json();
          console.log('      Mensagem de erro:', error.detail || error.message || JSON.stringify(error));
        } catch (e) {
          console.log('      Erro ao parsear resposta');
        }
      }
    } else {
      console.log('   ❌ TIMEOUT! Nenhuma resposta da API em 10 segundos');
      console.log('   Possíveis causas:');
      console.log('   - Backend não está rodando');
      console.log('   - Porta incorreta configurada');
      console.log('   - Erro de CORS');
      console.log('   - Erro de validação no frontend');
    }
    
    await page.waitForTimeout(3000);
    
    // Verificar se teve alguma mensagem de erro ou sucesso
    const successMsg = await page.locator('text=/sucesso|salvo|criado/i').isVisible().catch(() => false);
    const errorMsg = await page.locator('text=/erro|falha|problema/i').isVisible().catch(() => false);
    
    console.log('\n   📊 RESULTADO FINAL:');
    if (successMsg) {
      console.log('      ✅ Mensagem de sucesso exibida');
    } else if (errorMsg) {
      console.log('      ❌ Mensagem de erro exibida');
      const errorText = await page.locator('.error, .alert, [role="alert"]').first().textContent().catch(() => '');
      if (errorText) console.log('      Erro:', errorText);
    } else {
      console.log('      ⚠️ Nenhuma mensagem exibida (problema!)');
    }
    
    // PASSO 7: VERIFICAR SE O EVENTO FOI LISTADO
    console.log('\n📌 PASSO 7: Verificando se o evento aparece na lista...');
    
    // Fechar modal se ainda estiver aberto
    const closeBtn = await page.locator('button[aria-label="Close"], button:has-text("Fechar"), button:has-text("Cancelar")').first();
    if (await closeBtn.isVisible()) {
      await closeBtn.click();
      await page.waitForTimeout(1000);
    }
    
    // Procurar o evento na lista
    const eventoNaLista = await page.locator('text="Evento Teste Caixa"').isVisible().catch(() => false);
    
    if (eventoNaLista) {
      console.log('   ✅ Evento encontrado na lista!');
    } else {
      console.log('   ❌ Evento NÃO aparece na lista');
    }
    
    // Screenshot final
    await page.screenshot({ path: 'teste-evento-resultado-final.png', fullPage: true });
    
    // ANÁLISE DO PROBLEMA
    console.log('\n' + '='.repeat(50));
    console.log('🔍 ANÁLISE DO PROBLEMA');
    console.log('='.repeat(50));
    
    console.log('\n❌ PROBLEMAS IDENTIFICADOS:');
    console.log('1. A API está retornando erro ou não está respondendo');
    console.log('2. Possível problema de CORS entre frontend (5176) e backend (8003)');
    console.log('3. Validação de datas pode estar falhando no backend');
    console.log('4. Token de autenticação pode não estar sendo enviado corretamente');
    
    console.log('\n💡 SOLUÇÕES NECESSÁRIAS:');
    console.log('1. Verificar se o backend está realmente rodando na porta 8003');
    console.log('2. Confirmar que o endpoint /api/eventos está configurado');
    console.log('3. Verificar logs do backend para erros de validação');
    console.log('4. Implementar melhor tratamento de erros no frontend');
    console.log('5. Adicionar feedback visual durante o salvamento');
    
  } catch (error) {
    console.error('\n❌ ERRO DURANTE O TESTE:', error.message);
  } finally {
    console.log('\n🏁 Teste finalizado');
    await browser.close();
  }
})();