/**
 * 🎯 PAGE OBJECTS
 * Abstração das páginas para reutilização
 */

import { Page, Locator, expect } from '@playwright/test';

// ===== BASE PAGE =====

export class BasePage {
  constructor(protected page: Page) {}
  
  /**
   * Navega para uma URL
   */
  async goto(path: string) {
    await this.page.goto(path);
    await this.page.waitForLoadState('networkidle');
  }
  
  /**
   * Aguarda elemento estar visível
   */
  async waitForElement(selector: string) {
    await this.page.waitForSelector(selector, { state: 'visible' });
  }
  
  /**
   * Clica em elemento
   */
  async click(selector: string) {
    await this.page.click(selector);
  }
  
  /**
   * Preenche campo
   */
  async fill(selector: string, value: string) {
    await this.page.fill(selector, value);
  }
  
  /**
   * Verifica toast de notificação
   */
  async expectToast(message: string, type: 'success' | 'error' = 'success') {
    const toastSelector = type === 'success' ? '.Toastify__toast--success' : '.Toastify__toast--error';
    await this.page.waitForSelector(toastSelector);
    const toast = await this.page.locator(toastSelector).textContent();
    expect(toast).toContain(message);
  }
  
  /**
   * Tira screenshot
   */
  async screenshot(name: string) {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png`, fullPage: true });
  }
}

// ===== LOGIN PAGE =====

export class LoginPage extends BasePage {
  // Locators
  private cpfInput = '#cpf';
  private senhaInput = '#senha';
  private loginButton = 'button[type="submit"]';
  private errorMessage = '.error-message';
  
  /**
   * Navega para página de login
   */
  async goto() {
    await super.goto('/login');
  }
  
  /**
   * Realiza login
   */
  async login(cpf: string, senha: string) {
    await this.fill(this.cpfInput, cpf);
    await this.fill(this.senhaInput, senha);
    await this.click(this.loginButton);
  }
  
  /**
   * Verifica se está logado
   */
  async expectLoggedIn() {
    // Aguarda redirecionamento para dashboard (pode ser /app/dashboard ou /dashboard)
    await this.page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Verifica se está na URL correta
    const url = this.page.url();
    expect(url).toContain('dashboard');
  }
  
  /**
   * Verifica mensagem de erro
   */
  async expectError(message: string) {
    await this.waitForElement(this.errorMessage);
    const error = await this.page.locator(this.errorMessage).textContent();
    expect(error).toContain(message);
  }
  
  /**
   * Faz logout
   */
  async logout() {
    await this.page.click('[data-testid="user-menu"]');
    await this.page.click('[data-testid="logout-button"]');
    await this.page.waitForURL('**/login');
  }
}

// ===== EVENTOS PAGE =====

export class EventosPage extends BasePage {
  // Locators
  private createButton = '[data-testid="create-evento-button"]';
  private nomeInput = '#nome';
  private dataInput = '#data';
  private horarioInput = '#horario';
  private localInput = '#local';
  private submitButton = 'button[type="submit"]';
  private eventoCard = '.evento-card';
  private searchInput = '[data-testid="search-eventos"]';
  
  /**
   * Navega para página de eventos
   */
  async goto() {
    await super.goto('/eventos');
  }
  
  /**
   * Cria novo evento
   */
  async createEvento(data: any) {
    await this.click(this.createButton);
    await this.fill(this.nomeInput, data.nome);
    await this.fill(this.dataInput, data.data);
    await this.fill(this.horarioInput, data.horario);
    await this.fill(this.localInput, data.local);
    
    // Campos opcionais
    if (data.descricao) {
      await this.fill('#descricao', data.descricao);
    }
    if (data.capacidade_maxima) {
      await this.fill('#capacidade_maxima', data.capacidade_maxima.toString());
    }
    
    await this.click(this.submitButton);
  }
  
  /**
   * Busca evento
   */
  async searchEvento(nome: string) {
    await this.fill(this.searchInput, nome);
    await this.page.keyboard.press('Enter');
    await this.page.waitForLoadState('networkidle');
  }
  
  /**
   * Abre detalhes do evento
   */
  async openEvento(nome: string) {
    const evento = this.page.locator(this.eventoCard).filter({ hasText: nome }).first();
    await evento.click();
  }
  
  /**
   * Verifica se evento foi criado
   */
  async expectEventoCreated(nome: string) {
    await this.page.waitForSelector(this.eventoCard);
    const evento = this.page.locator(this.eventoCard).filter({ hasText: nome });
    await expect(evento).toBeVisible();
  }
  
  /**
   * Edita evento
   */
  async editEvento(nome: string, updates: any) {
    await this.openEvento(nome);
    await this.click('[data-testid="edit-evento-button"]');
    
    for (const [field, value] of Object.entries(updates)) {
      await this.fill(`#${field}`, value.toString());
    }
    
    await this.click(this.submitButton);
  }
  
  /**
   * Cancela evento
   */
  async cancelEvento(nome: string) {
    await this.openEvento(nome);
    await this.click('[data-testid="cancel-evento-button"]');
    await this.page.click('[data-testid="confirm-cancel"]');
  }
}

// ===== CHECK-IN PAGE =====

export class CheckinPage extends BasePage {
  // Locators
  private cpfInput = '#cpf-checkin';
  private checkinButton = '[data-testid="checkin-button"]';
  private searchInput = '[data-testid="search-checkin"]';
  private checkinList = '.checkin-list';
  private checkinItem = '.checkin-item';
  private qrCodeButton = '[data-testid="qr-code-button"]';
  
  /**
   * Navega para página de check-in de um evento
   */
  async goto(eventoId: number) {
    await super.goto(`/eventos/${eventoId}/checkin`);
  }
  
  /**
   * Realiza check-in por CPF
   */
  async checkinByCPF(cpf: string) {
    await this.fill(this.cpfInput, cpf);
    await this.click(this.checkinButton);
  }
  
  /**
   * Busca check-in
   */
  async searchCheckin(search: string) {
    await this.fill(this.searchInput, search);
    await this.page.keyboard.press('Enter');
  }
  
  /**
   * Verifica se check-in foi realizado
   */
  async expectCheckinCompleted(nome: string) {
    await this.waitForElement(this.checkinItem);
    const checkin = this.page.locator(this.checkinItem).filter({ hasText: nome });
    await expect(checkin).toBeVisible();
    
    // Verifica badge de confirmado
    const badge = checkin.locator('.badge-success');
    await expect(badge).toHaveText('CONFIRMADO');
  }
  
  /**
   * Cancela check-in
   */
  async cancelCheckin(nome: string) {
    const checkin = this.page.locator(this.checkinItem).filter({ hasText: nome });
    await checkin.locator('[data-testid="cancel-checkin"]').click();
    await this.page.click('[data-testid="confirm-cancel"]');
  }
  
  /**
   * Abre leitor de QR Code
   */
  async openQRScanner() {
    await this.click(this.qrCodeButton);
    // Aguardar permissão de câmera ou mock
    await this.page.waitForTimeout(1000);
  }
}

// ===== PDV PAGE =====

export class PDVPage extends BasePage {
  // Locators
  private productCard = '.product-card';
  private cartItem = '.cart-item';
  private cartTotal = '[data-testid="cart-total"]';
  private checkoutButton = '[data-testid="checkout-button"]';
  private paymentMethod = '[data-testid="payment-method"]';
  private confirmButton = '[data-testid="confirm-sale"]';
  private clientSearch = '#client-search';
  private addToCartButton = '[data-testid="add-to-cart"]';
  private quantityInput = '[data-testid="quantity-input"]';
  
  /**
   * Navega para PDV de um evento
   */
  async goto(eventoId: number) {
    await super.goto(`/eventos/${eventoId}/pdv`);
  }
  
  /**
   * Seleciona cliente
   */
  async selectClient(cpf: string) {
    await this.fill(this.clientSearch, cpf);
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(500);
    await this.page.click('.client-option:first-child');
  }
  
  /**
   * Adiciona produto ao carrinho
   */
  async addProduct(productName: string, quantity: number = 1) {
    const product = this.page.locator(this.productCard).filter({ hasText: productName });
    
    // Seleciona quantidade
    if (quantity > 1) {
      await product.locator(this.quantityInput).fill(quantity.toString());
    }
    
    // Adiciona ao carrinho
    await product.locator(this.addToCartButton).click();
  }
  
  /**
   * Remove produto do carrinho
   */
  async removeProduct(productName: string) {
    const item = this.page.locator(this.cartItem).filter({ hasText: productName });
    await item.locator('[data-testid="remove-item"]').click();
  }
  
  /**
   * Finaliza venda
   */
  async checkout(paymentMethod: 'DINHEIRO' | 'CARTAO' | 'PIX' = 'DINHEIRO') {
    await this.click(this.checkoutButton);
    
    // Seleciona forma de pagamento
    await this.page.click(`${this.paymentMethod}[value="${paymentMethod}"]`);
    
    // Confirma venda
    await this.click(this.confirmButton);
  }
  
  /**
   * Verifica total do carrinho
   */
  async expectCartTotal(expectedTotal: string) {
    const total = await this.page.locator(this.cartTotal).textContent();
    expect(total).toContain(expectedTotal);
  }
  
  /**
   * Verifica se venda foi concluída
   */
  async expectSaleCompleted() {
    await this.expectToast('Venda realizada com sucesso', 'success');
    
    // Verifica se carrinho foi limpo
    const cartItems = await this.page.locator(this.cartItem).count();
    expect(cartItems).toBe(0);
  }
  
  /**
   * Cancela última venda
   */
  async cancelLastSale() {
    await this.page.click('[data-testid="sales-history"]');
    await this.page.click('.sale-item:first-child [data-testid="cancel-sale"]');
    await this.page.fill('#cancel-reason', 'Teste de cancelamento');
    await this.page.click('[data-testid="confirm-cancel"]');
  }
}

// ===== DASHBOARD PAGE =====

export class DashboardPage extends BasePage {
  // Locators
  private statsCard = '.stats-card';
  private chartContainer = '.chart-container';
  private recentActivity = '.recent-activity';
  private quickActions = '.quick-actions';
  
  /**
   * Navega para dashboard
   */
  async goto() {
    await super.goto('/dashboard');
  }
  
  /**
   * Verifica estatísticas
   */
  async expectStats(statName: string, expectedValue: string) {
    const stat = this.page.locator(this.statsCard).filter({ hasText: statName });
    await expect(stat).toContainText(expectedValue);
  }
  
  /**
   * Verifica se gráfico está visível
   */
  async expectChartVisible(chartTitle: string) {
    const chart = this.page.locator(this.chartContainer).filter({ hasText: chartTitle });
    await expect(chart).toBeVisible();
  }
  
  /**
   * Acessa ação rápida
   */
  async quickAction(actionName: string) {
    await this.page.click(`${this.quickActions} button:has-text("${actionName}")`);
  }
  
  /**
   * Filtra período do dashboard
   */
  async filterPeriod(period: 'hoje' | 'semana' | 'mes' | 'ano') {
    await this.page.click('[data-testid="period-filter"]');
    await this.page.click(`[data-testid="period-${period}"]`);
    await this.page.waitForLoadState('networkidle');
  }
}

// ===== ADMIN PAGE =====

export class AdminPage extends BasePage {
  // Locators
  private usersTab = '[data-testid="users-tab"]';
  private settingsTab = '[data-testid="settings-tab"]';
  private reportsTab = '[data-testid="reports-tab"]';
  private auditTab = '[data-testid="audit-tab"]';
  
  /**
   * Navega para painel admin
   */
  async goto() {
    await super.goto('/admin');
  }
  
  /**
   * Navega para aba específica
   */
  async goToTab(tab: 'users' | 'settings' | 'reports' | 'audit') {
    const tabMap = {
      users: this.usersTab,
      settings: this.settingsTab,
      reports: this.reportsTab,
      audit: this.auditTab
    };
    
    await this.click(tabMap[tab]);
  }
  
  /**
   * Cria novo usuário
   */
  async createUser(userData: any) {
    await this.goToTab('users');
    await this.click('[data-testid="create-user-button"]');
    
    await this.fill('#nome', userData.nome);
    await this.fill('#email', userData.email);
    await this.fill('#cpf', userData.cpf);
    await this.fill('#senha', userData.senha);
    await this.page.selectOption('#role', userData.role);
    
    await this.click('button[type="submit"]');
  }
  
  /**
   * Gera relatório
   */
  async generateReport(reportType: string, startDate: string, endDate: string) {
    await this.goToTab('reports');
    await this.page.selectOption('#report-type', reportType);
    await this.fill('#start-date', startDate);
    await this.fill('#end-date', endDate);
    await this.click('[data-testid="generate-report"]');
    
    // Aguarda download
    const downloadPromise = this.page.waitForEvent('download');
    await this.click('[data-testid="download-report"]');
    const download = await downloadPromise;
    
    return download;
  }
  
  /**
   * Visualiza logs de auditoria
   */
  async viewAuditLogs(filters?: { user?: string; action?: string; date?: string }) {
    await this.goToTab('audit');
    
    if (filters) {
      if (filters.user) {
        await this.fill('#audit-user-filter', filters.user);
      }
      if (filters.action) {
        await this.page.selectOption('#audit-action-filter', filters.action);
      }
      if (filters.date) {
        await this.fill('#audit-date-filter', filters.date);
      }
      
      await this.click('[data-testid="apply-filters"]');
    }
    
    await this.page.waitForSelector('.audit-log-item');
  }
}