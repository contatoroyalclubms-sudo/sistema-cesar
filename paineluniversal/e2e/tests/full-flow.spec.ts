/**
 * 🔄 TESTE DE FLUXO COMPLETO
 * Teste E2E do fluxo principal: Login → Criar Evento → Check-in → PDV
 */

import { test, expect } from '@playwright/test';
import { 
  LoginPage, 
  EventosPage, 
  CheckinPage, 
  PDVPage, 
  DashboardPage 
} from './fixtures/page-objects';
import { testUsers, TestDataFactory, staticTestData } from './fixtures/test-data';

test.describe('Fluxo Completo do Sistema', () => {
  let loginPage: LoginPage;
  let eventosPage: EventosPage;
  let checkinPage: CheckinPage;
  let pdvPage: PDVPage;
  let dashboardPage: DashboardPage;
  
  // Dados compartilhados entre testes
  let eventoId: number;
  let eventoData: any;
  let clienteData: any;
  
  test.beforeAll(async () => {
    // Gerar dados para o teste
    eventoData = {
      ...staticTestData.defaultEvento,
      nome: `Evento E2E ${Date.now()}` // Nome único
    };
    
    clienteData = TestDataFactory.generateUser();
  });
  
  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    eventosPage = new EventosPage(page);
    checkinPage = new CheckinPage(page);
    pdvPage = new PDVPage(page);
    dashboardPage = new DashboardPage(page);
  });
  
  test('@critical Fluxo completo: Admin cria evento e gerencia operações', async ({ page }) => {
    test.setTimeout(120000); // 2 minutos para fluxo completo
    
    // ===== ETAPA 1: LOGIN =====
    await test.step('Login como admin', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.admin.cpf, testUsers.admin.senha);
      await loginPage.expectLoggedIn();
    });
    
    // ===== ETAPA 2: CRIAR EVENTO =====
    await test.step('Criar novo evento', async () => {
      await eventosPage.goto();
      await eventosPage.createEvento(eventoData);
      await eventosPage.expectEventoCreated(eventoData.nome);
      await eventosPage.expectToast('Evento criado com sucesso', 'success');
      
      // Capturar ID do evento
      const url = page.url();
      const match = url.match(/eventos\/(\d+)/);
      if (match) {
        eventoId = parseInt(match[1]);
      }
    });
    
    // ===== ETAPA 3: CONFIGURAR LISTAS =====
    await test.step('Configurar listas do evento', async () => {
      await page.goto(`/eventos/${eventoId}/listas`);
      
      // Criar lista VIP
      await page.click('[data-testid="create-lista"]');
      await page.fill('#nome', staticTestData.listas.vip.nome);
      await page.selectOption('#tipo', staticTestData.listas.vip.tipo);
      await page.fill('#limite', staticTestData.listas.vip.limite.toString());
      await page.click('button[type="submit"]');
      
      await expect(page.locator('.lista-card')).toContainText(staticTestData.listas.vip.nome);
    });
    
    // ===== ETAPA 4: ADICIONAR PRODUTOS AO ESTOQUE =====
    await test.step('Adicionar produtos para venda', async () => {
      await page.goto(`/eventos/${eventoId}/produtos`);
      
      for (const produto of staticTestData.defaultProdutos) {
        await page.click('[data-testid="add-produto"]');
        await page.fill('#nome', produto.nome);
        await page.selectOption('#categoria', produto.categoria);
        await page.fill('#preco_venda', produto.preco_venda.toString());
        await page.fill('#codigo_barras', produto.codigo_barras);
        await page.fill('#quantidade_inicial', '100');
        await page.click('button[type="submit"]');
        
        await expect(page.locator('.produto-card')).toContainText(produto.nome);
      }
    });
    
    // ===== ETAPA 5: REGISTRAR CLIENTE =====
    await test.step('Registrar novo cliente', async () => {
      await page.goto('/admin');
      await page.click('[data-testid="users-tab"]');
      await page.click('[data-testid="create-user-button"]');
      
      await page.fill('#nome', clienteData.nome);
      await page.fill('#email', clienteData.email);
      await page.fill('#cpf', clienteData.cpf);
      await page.fill('#telefone', clienteData.telefone);
      await page.fill('#senha', clienteData.senha);
      await page.selectOption('#role', 'CLIENTE');
      
      await page.click('button[type="submit"]');
      await page.waitForSelector('.success-message');
    });
    
    // ===== ETAPA 6: REALIZAR CHECK-IN =====
    await test.step('Realizar check-in do cliente', async () => {
      await checkinPage.goto(eventoId);
      await checkinPage.checkinByCPF(clienteData.cpf);
      await checkinPage.expectCheckinCompleted(clienteData.nome);
      await checkinPage.expectToast('Check-in realizado com sucesso', 'success');
      
      // Verificar contador de check-ins
      const counter = page.locator('[data-testid="checkin-counter"]');
      await expect(counter).toContainText('1');
    });
    
    // ===== ETAPA 7: REALIZAR VENDA NO PDV =====
    await test.step('Realizar venda no PDV', async () => {
      await pdvPage.goto(eventoId);
      
      // Selecionar cliente
      await pdvPage.selectClient(clienteData.cpf);
      
      // Adicionar produtos
      await pdvPage.addProduct('Água Mineral', 2);
      await pdvPage.addProduct('Cerveja Lata', 3);
      await pdvPage.addProduct('Hambúrguer', 1);
      
      // Verificar total
      const expectedTotal = (5.00 * 2) + (8.00 * 3) + (25.00 * 1); // 59.00
      await pdvPage.expectCartTotal(`R$ ${expectedTotal.toFixed(2)}`);
      
      // Finalizar venda
      await pdvPage.checkout('PIX');
      await pdvPage.expectSaleCompleted();
    });
    
    // ===== ETAPA 8: VERIFICAR DASHBOARD =====
    await test.step('Verificar métricas no dashboard', async () => {
      await dashboardPage.goto();
      
      // Verificar estatísticas
      await dashboardPage.expectStats('Eventos Ativos', '1');
      await dashboardPage.expectStats('Check-ins Hoje', '1');
      await dashboardPage.expectStats('Vendas Hoje', 'R$ 59,00');
      
      // Verificar gráficos
      await dashboardPage.expectChartVisible('Vendas por Hora');
      await dashboardPage.expectChartVisible('Check-ins por Tipo');
    });
    
    // ===== ETAPA 9: GERAR RELATÓRIO =====
    await test.step('Gerar relatório do evento', async () => {
      await page.goto(`/eventos/${eventoId}/relatorios`);
      
      // Selecionar relatório de vendas
      await page.selectOption('#tipo-relatorio', 'vendas');
      await page.click('[data-testid="generate-report"]');
      
      // Aguardar e baixar relatório
      const downloadPromise = page.waitForEvent('download');
      await page.click('[data-testid="download-pdf"]');
      const download = await downloadPromise;
      
      // Verificar nome do arquivo
      expect(download.suggestedFilename()).toContain('relatorio_vendas');
      expect(download.suggestedFilename()).toContain('.pdf');
    });
    
    // ===== ETAPA 10: CANCELAR CHECK-IN E VENDA =====
    await test.step('Testar cancelamentos', async () => {
      // Cancelar venda
      await pdvPage.goto(eventoId);
      await pdvPage.cancelLastSale();
      await pdvPage.expectToast('Venda cancelada com sucesso', 'success');
      
      // Verificar estorno no dashboard
      await dashboardPage.goto();
      await dashboardPage.expectStats('Vendas Hoje', 'R$ 0,00');
      
      // Cancelar check-in
      await checkinPage.goto(eventoId);
      await checkinPage.cancelCheckin(clienteData.nome);
      await checkinPage.expectToast('Check-in cancelado', 'success');
      
      // Verificar contador
      const counter = page.locator('[data-testid="checkin-counter"]');
      await expect(counter).toContainText('0');
    });
    
    // ===== ETAPA 11: FINALIZAR EVENTO =====
    await test.step('Finalizar evento', async () => {
      await eventosPage.goto();
      await eventosPage.openEvento(eventoData.nome);
      
      // Mudar status para finalizado
      await page.click('[data-testid="edit-evento-button"]');
      await page.selectOption('#status', 'FINALIZADO');
      await page.click('button[type="submit"]');
      
      await eventosPage.expectToast('Evento atualizado', 'success');
      
      // Verificar que não permite mais operações
      await checkinPage.goto(eventoId);
      await expect(page.locator('.alert-warning')).toContainText('Evento finalizado');
    });
  });
  
  test('@smoke Fluxo rápido: Promoter gerencia check-in e vendas', async ({ page }) => {
    // Login como promoter
    await loginPage.goto();
    await loginPage.login(testUsers.promoter.cpf, testUsers.promoter.senha);
    await loginPage.expectLoggedIn();
    
    // Buscar evento ativo
    await eventosPage.goto();
    await page.click('.evento-card.status-ativo:first-child');
    
    // Obter ID do evento
    const url = page.url();
    const match = url.match(/eventos\/(\d+)/);
    const eventId = match ? parseInt(match[1]) : 1;
    
    // Realizar check-in rápido
    await checkinPage.goto(eventId);
    const testClient = TestDataFactory.generateUser();
    await checkinPage.checkinByCPF(testClient.cpf);
    
    // Realizar venda rápida
    await pdvPage.goto(eventId);
    await pdvPage.selectClient(testClient.cpf);
    await pdvPage.addProduct('Água Mineral', 1);
    await pdvPage.checkout('DINHEIRO');
    await pdvPage.expectSaleCompleted();
    
    // Verificar comissão no dashboard
    await dashboardPage.goto();
    await dashboardPage.expectStats('Minhas Vendas', '1');
    await dashboardPage.expectStats('Comissão Estimada', 'R$');
  });
  
  test('@regression Fluxo com múltiplos usuários simultâneos', async ({ browser }) => {
    // Criar contextos para diferentes usuários
    const adminContext = await browser.newContext();
    const promoterContext = await browser.newContext();
    const clienteContext = await browser.newContext();
    
    // Páginas para cada usuário
    const adminPage = await adminContext.newPage();
    const promoterPage = await promoterContext.newPage();
    const clientePage = await clienteContext.newPage();
    
    try {
      // Admin cria evento
      const adminLogin = new LoginPage(adminPage);
      await adminLogin.goto();
      await adminLogin.login(testUsers.admin.cpf, testUsers.admin.senha);
      
      const adminEventos = new EventosPage(adminPage);
      await adminEventos.goto();
      const uniqueEventName = `Evento Simultâneo ${Date.now()}`;
      await adminEventos.createEvento({
        ...staticTestData.defaultEvento,
        nome: uniqueEventName
      });
      
      // Promoter acessa o mesmo evento
      const promoterLogin = new LoginPage(promoterPage);
      await promoterLogin.goto();
      await promoterLogin.login(testUsers.promoter.cpf, testUsers.promoter.senha);
      
      const promoterEventos = new EventosPage(promoterPage);
      await promoterEventos.goto();
      await promoterEventos.searchEvento(uniqueEventName);
      await promoterEventos.openEvento(uniqueEventName);
      
      // Cliente tenta acessar (deve ser negado)
      const clienteLogin = new LoginPage(clientePage);
      await clienteLogin.goto();
      await clienteLogin.login(testUsers.cliente.cpf, testUsers.cliente.senha);
      
      await clientePage.goto('/eventos');
      await expect(clientePage.locator('.alert')).toContainText('Acesso restrito');
      
      // Verificar que ambos admin e promoter veem as mesmas informações
      await expect(adminPage.locator('h1')).toContainText(uniqueEventName);
      await expect(promoterPage.locator('h1')).toContainText(uniqueEventName);
      
    } finally {
      // Limpar contextos
      await adminContext.close();
      await promoterContext.close();
      await clienteContext.close();
    }
  });
  
  test('Performance: Teste de carga com múltiplas operações', async ({ page }) => {
    test.setTimeout(180000); // 3 minutos
    
    // Login
    await loginPage.goto();
    await loginPage.login(testUsers.admin.cpf, testUsers.admin.senha);
    
    // Criar evento para teste de carga
    await eventosPage.goto();
    const loadTestEvent = {
      ...staticTestData.defaultEvento,
      nome: `Load Test ${Date.now()}`,
      capacidade_maxima: 1000
    };
    await eventosPage.createEvento(loadTestEvent);
    
    // Obter ID do evento
    const url = page.url();
    const match = url.match(/eventos\/(\d+)/);
    const eventId = match ? parseInt(match[1]) : 1;
    
    // Medir tempo de resposta para operações em lote
    const startTime = Date.now();
    
    // Realizar 50 check-ins
    console.log('Iniciando teste de carga: 50 check-ins');
    for (let i = 0; i < 50; i++) {
      const user = TestDataFactory.generateUser();
      await page.goto(`/api/checkin`, {
        waitUntil: 'networkidle'
      });
      
      // Fazer check-in via API para ser mais rápido
      await page.evaluate(async (data) => {
        await fetch('/api/checkin', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
      }, {
        evento_id: eventId,
        cpf: user.cpf,
        nome: user.nome,
        tipo_ingresso: 'NORMAL'
      });
      
      if (i % 10 === 0) {
        console.log(`Progress: ${i}/50 check-ins`);
      }
    }
    
    const endTime = Date.now();
    const totalTime = (endTime - startTime) / 1000;
    
    console.log(`Teste de carga concluído em ${totalTime}s`);
    console.log(`Média: ${totalTime/50}s por check-in`);
    
    // Verificar que o sistema ainda responde
    await dashboardPage.goto();
    await dashboardPage.expectStats('Check-ins Hoje', '50');
    
    // Performance deve ser aceitável (menos de 1s por operação em média)
    expect(totalTime / 50).toBeLessThan(1);
  });
});