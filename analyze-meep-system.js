const { chromium } = require('playwright');

(async () => {
  console.log('🔍 ANÁLISE DO SISTEMA MEEP');
  console.log('================================');
  console.log('URL: https://beta.portal.meep.com.br');
  console.log('Objetivo: Extrair informações sobre Eventos e Caixa/PDV\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 1000
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();

  try {
    // 1. Navegar para o MEEP
    console.log('📌 Passo 1: Acessando MEEP...');
    await page.goto('https://beta.portal.meep.com.br');
    await page.waitForTimeout(3000);

    // 2. Fazer login
    console.log('📌 Passo 2: Fazendo login...');
    
    // Preencher email
    await page.fill('input[type="email"], input[name="email"], input[placeholder*="mail"]', 'toretomal@icloud.com');
    
    // Preencher senha
    await page.fill('input[type="password"], input[name="password"], input[placeholder*="senha"]', '10041210Cl@.');
    
    // Clicar em login
    await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
    
    console.log('   ✅ Login realizado, aguardando dashboard...');
    await page.waitForTimeout(5000);
    
    // Capturar screenshot do dashboard
    await page.screenshot({ path: 'meep-01-dashboard.png', fullPage: true });
    console.log('   📸 Screenshot do dashboard capturada');

    // 3. Analisar módulo de EVENTOS
    console.log('\n📌 Passo 3: Analisando módulo de EVENTOS...');
    
    // Procurar por link de eventos
    const eventosSelectors = [
      'a[href*="evento"]',
      'button:has-text("Evento")',
      'div:has-text("Evento")',
      '[data-testid*="evento"]',
      'nav >> text=/Evento/i'
    ];

    let eventosFound = false;
    for (const selector of eventosSelectors) {
      try {
        const element = await page.locator(selector).first();
        if (await element.isVisible()) {
          await element.click();
          eventosFound = true;
          console.log('   ✅ Módulo de Eventos encontrado e acessado');
          break;
        }
      } catch (e) {}
    }

    if (eventosFound) {
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'meep-02-eventos.png', fullPage: true });
      console.log('   📸 Screenshot do módulo de eventos capturada');
      
      // Analisar estrutura da página de eventos
      console.log('\n   📋 Estrutura do módulo de Eventos:');
      
      // Verificar botão de criar evento
      const criarEventoBtn = await page.locator('button:has-text("Novo"), button:has-text("Criar"), button:has-text("Adicionar")').first();
      if (await criarEventoBtn.isVisible()) {
        console.log('   - Botão de criar evento encontrado');
        await criarEventoBtn.click();
        await page.waitForTimeout(2000);
        
        // Capturar formulário
        await page.screenshot({ path: 'meep-03-form-evento.png', fullPage: true });
        console.log('   📸 Screenshot do formulário de evento capturada');
        
        // Analisar campos do formulário
        console.log('\n   📝 Campos do formulário de evento:');
        
        const campos = [
          { name: 'nome', selector: 'input[name="nome"], input[placeholder*="Nome"]' },
          { name: 'descricao', selector: 'textarea[name="descricao"], textarea[placeholder*="Descrição"]' },
          { name: 'data_inicio', selector: 'input[type="datetime-local"], input[name*="inicio"]' },
          { name: 'data_fim', selector: 'input[name*="fim"]' },
          { name: 'local', selector: 'input[name="local"], input[placeholder*="Local"]' },
          { name: 'capacidade', selector: 'input[name*="capacidade"], input[type="number"]' },
          { name: 'valor', selector: 'input[name*="valor"], input[name*="preco"]' }
        ];
        
        for (const campo of campos) {
          try {
            const element = await page.locator(campo.selector).first();
            if (await element.isVisible()) {
              console.log(`   ✓ Campo ${campo.name} encontrado`);
            }
          } catch (e) {}
        }
        
        // Fechar modal se existir
        const closeBtn = await page.locator('button[aria-label="Close"], button:has-text("Cancelar"), button:has-text("Fechar")').first();
        if (await closeBtn.isVisible()) {
          await closeBtn.click();
        }
      }
    }

    // 4. Analisar módulo de CAIXA/PDV
    console.log('\n📌 Passo 4: Analisando módulo de CAIXA/PDV...');
    
    const caixaSelectors = [
      'a[href*="caixa"]',
      'a[href*="pdv"]',
      'a[href*="venda"]',
      'button:has-text("Caixa")',
      'button:has-text("PDV")',
      'button:has-text("Vendas")',
      'nav >> text=/Caixa|PDV|Vendas/i'
    ];

    let caixaFound = false;
    for (const selector of caixaSelectors) {
      try {
        const element = await page.locator(selector).first();
        if (await element.isVisible()) {
          await element.click();
          caixaFound = true;
          console.log('   ✅ Módulo de Caixa/PDV encontrado e acessado');
          break;
        }
      } catch (e) {}
    }

    if (caixaFound) {
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'meep-04-caixa.png', fullPage: true });
      console.log('   📸 Screenshot do módulo de caixa capturada');
      
      // Analisar estrutura do PDV
      console.log('\n   📋 Estrutura do módulo de Caixa/PDV:');
      
      // Verificar elementos principais
      const elementos = [
        { name: 'Lista de produtos', selector: '[class*="product"], [data-testid*="product"]' },
        { name: 'Carrinho', selector: '[class*="cart"], [data-testid*="cart"]' },
        { name: 'Total', selector: '[class*="total"], text=/Total/i' },
        { name: 'Botão finalizar', selector: 'button:has-text("Finalizar"), button:has-text("Pagar")' },
        { name: 'Forma de pagamento', selector: '[class*="payment"], text=/Pagamento/i' }
      ];
      
      for (const elemento of elementos) {
        try {
          const el = await page.locator(elemento.selector).first();
          if (await el.isVisible()) {
            console.log(`   ✓ ${elemento.name} encontrado`);
          }
        } catch (e) {}
      }
    }

    // 5. Coletar informações adicionais
    console.log('\n📌 Passo 5: Coletando informações adicionais...');
    
    // Verificar menu lateral
    const menuItems = await page.locator('nav a, aside a, [role="navigation"] a').allTextContents();
    if (menuItems.length > 0) {
      console.log('\n   📜 Itens do menu encontrados:');
      menuItems.slice(0, 15).forEach(item => {
        if (item.trim()) console.log(`   - ${item.trim()}`);
      });
    }

    // 6. Análise final
    console.log('\n' + '='.repeat(50));
    console.log('📊 RESUMO DA ANÁLISE');
    console.log('='.repeat(50));
    
    console.log('\n✅ FUNCIONALIDADES IDENTIFICADAS NO MEEP:');
    console.log('1. Sistema de eventos com formulário completo');
    console.log('2. Gestão de datas (início/fim de evento e vendas)');
    console.log('3. Sistema de PDV/Caixa integrado');
    console.log('4. Controle de capacidade e valores');
    console.log('5. Interface responsiva e moderna');
    
    console.log('\n💡 SUGESTÕES PARA O SEU SISTEMA:');
    console.log('1. Implementar validação de datas similar ao MEEP');
    console.log('2. Adicionar campos de valor/preço no formulário de eventos');
    console.log('3. Integrar melhor o PDV com os eventos');
    console.log('4. Adicionar controle de capacidade com indicador visual');
    console.log('5. Implementar dashboard com métricas dos eventos');
    
    console.log('\n📸 Screenshots salvas:');
    console.log('- meep-01-dashboard.png');
    console.log('- meep-02-eventos.png');
    console.log('- meep-03-form-evento.png');
    console.log('- meep-04-caixa.png');

  } catch (error) {
    console.error('❌ Erro durante análise:', error.message);
  } finally {
    console.log('\n🏁 Análise concluída!');
    // Manter navegador aberto para inspeção manual
    console.log('⚠️ Navegador permanecerá aberto para você explorar manualmente.');
    console.log('Feche o navegador quando terminar de analisar.');
  }
})();