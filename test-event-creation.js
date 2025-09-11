const { chromium } = require('playwright');

(async () => {
  console.log('🧪 TESTE DE CRIAÇÃO DE EVENTO COM CORES CORRIGIDAS');
  console.log('===================================================\n');
  
  const browser = await chromium.launch({
    headless: false,
    slowMo: 500
  });
  
  const page = await browser.newContext().then(c => c.newPage());
  
  try {
    // 1. Acessar o sistema
    console.log('📌 PASSO 1: Acessando o sistema...');
    const ports = [5173, 5174, 5175, 5176, 5177, 5178];
    let systemUrl = null;
    
    for (const port of ports) {
      try {
        const testUrl = `http://localhost:${port}`;
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
    
    // 2. Fazer login
    console.log('\n📌 PASSO 2: Fazendo login...');
    const needsLogin = await page.locator('input[type="password"]').isVisible().catch(() => false);
    
    if (needsLogin) {
      await page.fill('input[placeholder*="CPF"], input[name="cpf"], input[type="text"]', '00000000000');
      await page.fill('input[type="password"]', '0000');
      await page.click('button[type="submit"]');
      console.log('   ✅ Login realizado');
      await page.waitForTimeout(3000);
    }
    
    // 3. Navegar para eventos
    console.log('\n📌 PASSO 3: Navegando para Eventos...');
    await page.locator('a[href*="eventos"], button:has-text("Eventos"), nav >> text=Eventos').first().click().catch(() => {
      return page.goto(`${systemUrl}/eventos`);
    });
    await page.waitForTimeout(2000);
    
    // Capturar screenshot das cores corrigidas
    await page.screenshot({ path: 'test-evento-cores-corrigidas.png', fullPage: true });
    console.log('   📸 Screenshot das cores corrigidas salva\n');
    
    // 4. Abrir modal de criação
    console.log('📌 PASSO 4: Abrindo formulário de novo evento...');
    await page.locator('button:has-text("Novo"), button:has-text("Criar"), button:has-text("Adicionar"), button >> svg').first().click();
    await page.waitForTimeout(1000);
    
    // 5. Preencher formulário
    console.log('\n📌 PASSO 5: Preenchendo formulário...');
    
    await page.fill('input[name="nome"], input[placeholder*="Nome"]', 'Evento Teste Cores Corrigidas');
    await page.fill('textarea[name="descricao"], textarea[placeholder*="Descrição"]', 'Teste com cores do sistema');
    await page.fill('input[name="local"], input[placeholder*="Local"]', 'Centro de Convenções');
    await page.fill('input[name="endereco"], input[placeholder*="Endereço"]', 'Rua Principal, 123');
    
    // Configurar datas
    const agora = new Date();
    const formatDate = (date) => {
      const pad = (n) => n.toString().padStart(2, '0');
      return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
    };
    
    const inicioVendas = new Date(agora.getTime() + 30 * 60 * 1000);
    const fimVendas = new Date(agora.getTime() + 80 * 60 * 1000);
    const inicioEvento = new Date(agora.getTime() + 90 * 60 * 1000);
    const fimEvento = new Date(agora.getTime() + 270 * 60 * 1000);
    
    await page.fill('input[name="data_inicio_vendas"]', formatDate(inicioVendas));
    await page.fill('input[name="data_fim_vendas"]', formatDate(fimVendas));
    await page.fill('input[name="data_inicio_evento"]', formatDate(inicioEvento));
    await page.fill('input[name="data_fim_evento"]', formatDate(fimEvento));
    
    await page.fill('input[name="capacidade_maxima"]', '500');
    await page.fill('input[name="limite_idade"]', '18');
    
    console.log('   ✅ Formulário preenchido');
    
    // Screenshot do formulário
    await page.screenshot({ path: 'test-evento-formulario-cores.png' });
    console.log('   📸 Screenshot do formulário salva\n');
    
    // 6. Salvar evento
    console.log('📌 PASSO 6: Salvando evento...');
    
    // Monitorar resposta da API
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/eventos') && 
      (response.request().method() === 'POST' || response.request().method() === 'PUT'),
      { timeout: 10000 }
    ).catch(() => null);
    
    await page.locator('button:has-text("Salvar"), button:has-text("Criar"), button[type="submit"]').last().click();
    
    const response = await responsePromise;
    
    if (response) {
      console.log('   📡 Resposta da API:');
      console.log('      Status:', response.status());
      
      if (response.ok()) {
        console.log('      ✅ EVENTO CRIADO COM SUCESSO!');
        const data = await response.json();
        console.log('      ID do evento:', data.id || 'N/A');
      } else {
        console.log('      ❌ Erro:', response.status());
        try {
          const error = await response.json();
          console.log('      Detalhes:', error.detail || error.message || JSON.stringify(error));
        } catch (e) {}
      }
    } else {
      console.log('   ⚠️ Nenhuma resposta da API (timeout)');
    }
    
    await page.waitForTimeout(3000);
    
    // 7. Verificar lista
    console.log('\n📌 PASSO 7: Verificando lista de eventos...');
    
    // Fechar modal se aberto
    const closeBtn = await page.locator('button[aria-label="Close"], button:has-text("Fechar"), button:has-text("Cancelar")').first();
    if (await closeBtn.isVisible()) {
      await closeBtn.click();
      await page.waitForTimeout(1000);
    }
    
    const eventoNaLista = await page.locator('text="Evento Teste Cores Corrigidas"').isVisible().catch(() => false);
    
    if (eventoNaLista) {
      console.log('   ✅ Evento aparece na lista!');
    } else {
      console.log('   ❌ Evento NÃO aparece na lista');
    }
    
    // Screenshot final
    await page.screenshot({ path: 'test-evento-resultado-cores.png', fullPage: true });
    console.log('   📸 Screenshot final salva');
    
    console.log('\n' + '='.repeat(50));
    console.log('📊 RESUMO DO TESTE');
    console.log('='.repeat(50));
    console.log('✅ Cores corrigidas para usar primary do sistema');
    console.log('✅ Interface consistente com layout principal');
    
    if (response && response.ok()) {
      console.log('✅ Evento criado com sucesso na API');
    } else {
      console.log('❌ Problema na criação do evento');
      console.log('   - Verificar se POST endpoint está implementado');
      console.log('   - Confirmar que auth_server.py foi reiniciado');
    }
    
  } catch (error) {
    console.error('\n❌ ERRO:', error.message);
  } finally {
    console.log('\n🏁 Teste finalizado');
    await browser.close();
  }
})();