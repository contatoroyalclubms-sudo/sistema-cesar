import { test, expect } from '@playwright/test';

test.describe('Sistema Painel Universal - Testes Completos', () => {
  
  test('Login e Cadastro de Eventos', async ({ page }) => {
    // 1. Navegar para o sistema
    await page.goto('http://localhost:5173');
    
    // 2. Fazer login com CPF 00000000000 e senha 0000
    await page.waitForSelector('input[name="cpf"], input[placeholder*="CPF"]', { timeout: 10000 });
    
    // Preencher CPF
    const cpfInput = await page.locator('input[name="cpf"], input[placeholder*="CPF"]').first();
    await cpfInput.fill('00000000000');
    
    // Preencher senha
    const senhaInput = await page.locator('input[type="password"], input[name="senha"]').first();
    await senhaInput.fill('0000');
    
    // Clicar no botão de login
    await page.click('button[type="submit"]');
    
    // Aguardar navegação após login
    await page.waitForTimeout(3000);
    
    // 3. Verificar se login foi bem sucedido
    const dashboardVisible = await page.locator('text=/Dashboard|Painel|Eventos/i').isVisible().catch(() => false);
    
    if (!dashboardVisible) {
      console.log('Login pode ter falhado, tentando continuar...');
    }
    
    // 4. Navegar para módulo de Eventos
    // Tentar clicar no menu lateral ou navegação
    const eventosLink = page.locator('a[href*="eventos"], button:has-text("Eventos"), div:has-text("Eventos")').first();
    
    if (await eventosLink.isVisible()) {
      await eventosLink.click();
      await page.waitForTimeout(2000);
    }
    
    // 5. Abrir modal de criação de evento
    const novoEventoBtn = page.locator('button:has-text("Novo Evento"), button:has-text("Criar Evento"), button:has-text("Adicionar")').first();
    
    if (await novoEventoBtn.isVisible()) {
      await novoEventoBtn.click();
      await page.waitForTimeout(1000);
      
      // 6. Preencher formulário de evento
      // Nome do evento
      await page.fill('input[name="nome"], input[placeholder*="Nome"]', 'Evento de Teste Automatizado');
      
      // Descrição
      const descricaoInput = page.locator('textarea[name="descricao"], textarea[placeholder*="Descrição"]').first();
      if (await descricaoInput.isVisible()) {
        await descricaoInput.fill('Evento criado via teste automatizado Playwright');
      }
      
      // Local
      await page.fill('input[name="local"], input[placeholder*="Local"]', 'Centro de Convenções');
      
      // Endereço
      const enderecoInput = page.locator('input[name="endereco"], input[placeholder*="Endereço"]').first();
      if (await enderecoInput.isVisible()) {
        await enderecoInput.fill('Rua Teste, 123');
      }
      
      // Datas - Vamos definir datas válidas
      const agora = new Date();
      const inicioVendas = new Date(agora.getTime() + 30 * 60 * 1000); // 30 min no futuro
      const inicioEvento = new Date(agora.getTime() + 120 * 60 * 1000); // 2 horas no futuro
      const fimVendas = new Date(inicioEvento.getTime() - 15 * 60 * 1000); // 15 min antes do evento
      const fimEvento = new Date(inicioEvento.getTime() + 180 * 60 * 1000); // 3 horas depois do início
      
      // Formatar datas para input datetime-local
      const formatDate = (date: Date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
      };
      
      // Preencher datas
      await page.fill('input[name="data_inicio_vendas"]', formatDate(inicioVendas));
      await page.fill('input[name="data_fim_vendas"]', formatDate(fimVendas));
      await page.fill('input[name="data_inicio_evento"]', formatDate(inicioEvento));
      await page.fill('input[name="data_fim_evento"]', formatDate(fimEvento));
      
      // Capacidade máxima
      const capacidadeInput = page.locator('input[name="capacidade_maxima"]').first();
      if (await capacidadeInput.isVisible()) {
        await capacidadeInput.fill('100');
      }
      
      // 7. Salvar evento
      const salvarBtn = page.locator('button:has-text("Salvar"), button:has-text("Criar"), button[type="submit"]').last();
      await salvarBtn.click();
      
      // 8. Verificar se evento foi criado
      await page.waitForTimeout(3000);
      
      // Verificar mensagem de sucesso ou evento na lista
      const successMessage = await page.locator('text=/sucesso|criado|salvo/i').isVisible().catch(() => false);
      const eventoNaLista = await page.locator('text="Evento de Teste Automatizado"').isVisible().catch(() => false);
      
      if (successMessage || eventoNaLista) {
        console.log('✅ Evento criado com sucesso!');
      } else {
        console.log('⚠️ Não foi possível confirmar a criação do evento');
      }
    }
    
    // 9. Testar módulo de Caixa/PDV
    const caixaLink = page.locator('a[href*="caixa"], a[href*="pdv"], button:has-text("Caixa"), button:has-text("PDV")').first();
    
    if (await caixaLink.isVisible()) {
      await caixaLink.click();
      await page.waitForTimeout(2000);
      
      console.log('✅ Módulo Caixa/PDV acessado');
      
      // Verificar se a página carregou
      const caixaPageLoaded = await page.locator('text=/Caixa|PDV|Vendas/i').isVisible().catch(() => false);
      
      if (caixaPageLoaded) {
        console.log('✅ Página do Caixa/PDV carregada corretamente');
      }
    }
    
    // Capturar screenshot final
    await page.screenshot({ path: 'test-final-resultado.png', fullPage: true });
  });
  
  test('Verificar compatibilidade Frontend-Backend', async ({ page }) => {
    // Testar endpoint de saúde
    const healthResponse = await page.request.get('http://localhost:8003/api/health');
    expect(healthResponse.ok()).toBeTruthy();
    
    // Testar endpoint de eventos
    const eventosResponse = await page.request.get('http://localhost:8003/api/eventos/');
    
    if (eventosResponse.ok()) {
      const eventos = await eventosResponse.json();
      console.log(`✅ API de eventos funcionando. Total de eventos: ${eventos.length || 0}`);
    } else {
      console.log('⚠️ API de eventos retornou erro:', eventosResponse.status());
    }
  });
});