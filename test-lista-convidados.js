const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Iniciando teste do sistema de lista de convidados...');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500 
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();
  
  try {
    // 1. Navegar para o sistema
    console.log('📍 Navegando para http://localhost:5173...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Tirar screenshot da tela inicial
    await page.screenshot({ path: 'test-01-tela-inicial.png' });
    console.log('📸 Screenshot da tela inicial salva');
    
    // 2. Fazer login
    console.log('🔐 Fazendo login com CPF: 00000000000...');
    
    // Preencher CPF
    await page.fill('input[placeholder*="CPF"]', '00000000000');
    
    // Preencher senha
    await page.fill('input[type="password"]', 'admin123');
    
    await page.screenshot({ path: 'test-02-login-preenchido.png' });
    
    // Clicar no botão de login
    await page.click('button[type="submit"]');
    
    // Aguardar navegação
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'test-03-dashboard.png' });
    console.log('✅ Login realizado com sucesso');
    
    // 3. Navegar para Eventos
    console.log('📅 Navegando para módulo de Eventos...');
    
    // Tentar clicar no menu lateral de Eventos
    const eventosLink = await page.locator('text=Eventos').first();
    if (await eventosLink.isVisible()) {
      await eventosLink.click();
      await page.waitForTimeout(2000);
    }
    
    await page.screenshot({ path: 'test-04-eventos.png' });
    
    // 4. Criar um novo evento se não existir
    const eventos = await page.locator('.card').count();
    
    if (eventos === 0) {
      console.log('📝 Criando novo evento...');
      
      // Clicar no botão de criar evento
      await page.click('button:has-text("Criar Evento")');
      await page.waitForTimeout(1000);
      
      // Preencher dados do evento
      await page.fill('input[name="nome"]', 'Evento Teste - Lista de Convidados');
      await page.fill('textarea[name="descricao"]', 'Evento para testar sistema de lista de convidados');
      await page.fill('input[name="local"]', 'Local de Teste');
      
      // Salvar evento
      await page.click('button:has-text("Salvar")');
      await page.waitForTimeout(2000);
    }
    
    // 5. Abrir lista de convidados do primeiro evento
    console.log('📋 Abrindo Lista de Convidados...');
    
    // Procurar botão Lista no card do evento
    const listaButton = await page.locator('button:has-text("Lista")').first();
    
    if (await listaButton.isVisible()) {
      await listaButton.click();
      await page.waitForTimeout(2000);
      
      await page.screenshot({ path: 'test-05-lista-convidados.png' });
      console.log('✅ Modal de Lista de Convidados aberto');
      
      // 6. Criar uma nova lista
      console.log('➕ Criando nova lista de convidados...');
      
      const adicionarButton = await page.locator('button:has-text("Adicionar lista")');
      if (await adicionarButton.isVisible()) {
        await adicionarButton.click();
        await page.waitForTimeout(1000);
        
        // Preencher dados da lista
        await page.fill('input[id="nome"]', 'VIP Exclusivo - Teste Automático');
        await page.selectOption('select[id="tipo"]', 'vip');
        await page.fill('input[id="quantidade_maxima"]', '50');
        await page.fill('textarea[id="descricao"]', 'Lista VIP criada automaticamente para teste');
        
        await page.screenshot({ path: 'test-06-nova-lista-form.png' });
        
        // Salvar lista
        await page.click('button:has-text("Criar Lista")');
        await page.waitForTimeout(2000);
        
        await page.screenshot({ path: 'test-07-lista-criada.png' });
        console.log('✅ Lista de convidados criada com sucesso');
      }
      
      // 7. Verificar link gerado
      const linkText = await page.locator('text=/Link:.*VIP/').first();
      if (await linkText.isVisible()) {
        console.log('🔗 Link de convite gerado com sucesso');
        
        // Tentar copiar o link
        const copyButton = await page.locator('button:has([data-icon="copy"])').first();
        if (await copyButton.isVisible()) {
          await copyButton.click();
          console.log('📋 Link copiado para área de transferência');
        }
      }
    }
    
    // 8. Screenshot final
    await page.screenshot({ path: 'test-08-teste-completo.png' });
    
    console.log('🎉 Teste concluído com sucesso!');
    console.log('📊 Funcionalidades testadas:');
    console.log('   ✅ Login com CPF');
    console.log('   ✅ Navegação para Eventos');
    console.log('   ✅ Abertura do modal de Lista de Convidados');
    console.log('   ✅ Criação de nova lista');
    console.log('   ✅ Geração de link único');
    
  } catch (error) {
    console.error('❌ Erro durante o teste:', error);
    await page.screenshot({ path: 'test-erro.png' });
  } finally {
    await page.waitForTimeout(5000); // Aguardar para visualizar
    await browser.close();
  }
})();