import { test, expect, Page } from '@playwright/test';

test.describe('Sistema de Gestão de Eventos - Teste Completo', () => {
  let page: Page;
  const baseUrl = 'http://localhost:5174';
  const apiUrl = 'http://localhost:8000';
  const cpf = '06601206154';
  const password = '101112';
  const errors: Array<{module: string, error: string, screenshot?: string}> = [];

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();
    
    // Capture console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push({
          module: 'Console',
          error: msg.text()
        });
      }
    });

    // Capture page errors
    page.on('pageerror', error => {
      errors.push({
        module: 'Page',
        error: error.message
      });
    });

    // Capture failed requests
    page.on('requestfailed', request => {
      errors.push({
        module: 'Network',
        error: `Failed request: ${request.url()} - ${request.failure()?.errorText}`
      });
    });
  });

  test.afterAll(async () => {
    // Save errors to file
    if (errors.length > 0) {
      const fs = require('fs');
      fs.writeFileSync('test-errors.json', JSON.stringify(errors, null, 2));
      console.log(`Found ${errors.length} errors. Saved to test-errors.json`);
    }
    await page.close();
  });

  test('01 - Login', async () => {
    console.log('Testing Login...');
    await page.goto(baseUrl);
    
    // Wait for login page
    await page.waitForSelector('input[name="cpf"], input[type="text"]', { timeout: 10000 });
    
    // Try to login
    const cpfInput = await page.$('input[name="cpf"], input[type="text"]');
    const passwordInput = await page.$('input[name="senha"], input[type="password"]');
    
    if (cpfInput && passwordInput) {
      await cpfInput.fill(cpf);
      await passwordInput.fill(password);
      
      // Find and click login button
      const loginButton = await page.$('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
      if (loginButton) {
        await loginButton.click();
        
        // Wait for navigation or error
        try {
          await page.waitForURL(`${baseUrl}/dashboard`, { timeout: 10000 });
          console.log('✓ Login successful');
        } catch (e) {
          // Check for error message
          const errorMessage = await page.$('.text-red-500, .error, .alert-danger');
          if (errorMessage) {
            const errorText = await errorMessage.textContent();
            errors.push({
              module: 'Login',
              error: `Login failed: ${errorText}`
            });
            console.log('✗ Login failed:', errorText);
          }
          
          // Take screenshot
          await page.screenshot({ path: 'login-error.png' });
          errors.push({
            module: 'Login',
            error: 'Login failed - see screenshot',
            screenshot: 'login-error.png'
          });
        }
      }
    } else {
      errors.push({
        module: 'Login',
        error: 'Could not find login form fields'
      });
    }
  });

  test('02 - Dashboard', async () => {
    console.log('Testing Dashboard...');
    try {
      await page.goto(`${baseUrl}/dashboard`);
      await page.waitForSelector('.dashboard, main, #root', { timeout: 5000 });
      
      // Check for main dashboard elements
      const dashboardElements = await page.$$('.card, .stat, .widget');
      if (dashboardElements.length === 0) {
        errors.push({
          module: 'Dashboard',
          error: 'No dashboard elements found'
        });
      }
      console.log('✓ Dashboard loaded');
    } catch (e) {
      errors.push({
        module: 'Dashboard',
        error: `Dashboard failed to load: ${e}`
      });
      await page.screenshot({ path: 'dashboard-error.png' });
    }
  });

  test('03 - Eventos Module', async () => {
    console.log('Testing Eventos Module...');
    try {
      await page.goto(`${baseUrl}/eventos`);
      await page.waitForSelector('h1:has-text("Eventos"), .eventos-list, .eventos-container', { timeout: 5000 });
      
      // Try to create a new event
      const newEventButton = await page.$('button:has-text("Novo Evento"), button:has-text("Criar Evento"), button:has-text("Adicionar")');
      if (newEventButton) {
        await newEventButton.click();
        await page.waitForTimeout(1000);
        
        // Check if form opened
        const eventForm = await page.$('form, .modal, dialog');
        if (!eventForm) {
          errors.push({
            module: 'Eventos',
            error: 'Event creation form did not open'
          });
        }
        
        // Close modal if opened
        const closeButton = await page.$('button:has-text("Cancelar"), button:has-text("Fechar"), .close');
        if (closeButton) await closeButton.click();
      }
      console.log('✓ Eventos module loaded');
    } catch (e) {
      errors.push({
        module: 'Eventos',
        error: `Eventos module failed: ${e}`
      });
      await page.screenshot({ path: 'eventos-error.png' });
    }
  });

  test('04 - PDV Module', async () => {
    console.log('Testing PDV Module...');
    try {
      await page.goto(`${baseUrl}/pdv`);
      await page.waitForSelector('h1:has-text("PDV"), .pdv-container, .point-of-sale', { timeout: 5000 });
      
      // Check for PDV elements
      const pdvElements = await page.$$('.product-grid, .cart, .pdv-products');
      if (pdvElements.length === 0) {
        errors.push({
          module: 'PDV',
          error: 'PDV elements not found'
        });
      }
      console.log('✓ PDV module loaded');
    } catch (e) {
      errors.push({
        module: 'PDV',
        error: `PDV module failed: ${e}`
      });
      await page.screenshot({ path: 'pdv-error.png' });
    }
  });

  test('05 - Checkin Module', async () => {
    console.log('Testing Checkin Module...');
    try {
      await page.goto(`${baseUrl}/checkin`);
      await page.waitForSelector('h1:has-text("Check"), .checkin-container', { timeout: 5000 });
      console.log('✓ Checkin module loaded');
    } catch (e) {
      errors.push({
        module: 'Checkin',
        error: `Checkin module failed: ${e}`
      });
      await page.screenshot({ path: 'checkin-error.png' });
    }
  });

  test('06 - Estoque Module', async () => {
    console.log('Testing Estoque Module...');
    try {
      await page.goto(`${baseUrl}/estoque`);
      await page.waitForSelector('h1:has-text("Estoque"), .inventory, .stock', { timeout: 5000 });
      
      // Check for inventory elements
      const inventoryElements = await page.$$('.product-list, .stock-table, table');
      if (inventoryElements.length === 0) {
        errors.push({
          module: 'Estoque',
          error: 'Inventory elements not found'
        });
      }
      console.log('✓ Estoque module loaded');
    } catch (e) {
      errors.push({
        module: 'Estoque',
        error: `Estoque module failed: ${e}`
      });
      await page.screenshot({ path: 'estoque-error.png' });
    }
  });

  test('07 - Financeiro Module', async () => {
    console.log('Testing Financeiro Module...');
    try {
      await page.goto(`${baseUrl}/financeiro`);
      await page.waitForSelector('h1:has-text("Financeiro"), .financial, .finance', { timeout: 5000 });
      console.log('✓ Financeiro module loaded');
    } catch (e) {
      errors.push({
        module: 'Financeiro',
        error: `Financeiro module failed: ${e}`
      });
      await page.screenshot({ path: 'financeiro-error.png' });
    }
  });

  test('08 - Listas Module', async () => {
    console.log('Testing Listas Module...');
    try {
      await page.goto(`${baseUrl}/listas`);
      await page.waitForSelector('h1:has-text("Lista"), .lists, .guest-list', { timeout: 5000 });
      console.log('✓ Listas module loaded');
    } catch (e) {
      errors.push({
        module: 'Listas',
        error: `Listas module failed: ${e}`
      });
      await page.screenshot({ path: 'listas-error.png' });
    }
  });

  test('09 - API Health Check', async () => {
    console.log('Testing API Health...');
    try {
      const response = await page.request.get(`${apiUrl}/docs`);
      if (response.status() !== 200) {
        errors.push({
          module: 'API',
          error: `API docs returned status ${response.status()}`
        });
      }
      console.log('✓ API is healthy');
    } catch (e) {
      errors.push({
        module: 'API',
        error: `API health check failed: ${e}`
      });
    }
  });

  test('10 - Generate Error Report', async () => {
    console.log('\n=== ERROR REPORT ===');
    if (errors.length === 0) {
      console.log('✓ No errors found!');
    } else {
      console.log(`✗ Found ${errors.length} errors:`);
      errors.forEach((err, index) => {
        console.log(`\n${index + 1}. Module: ${err.module}`);
        console.log(`   Error: ${err.error}`);
        if (err.screenshot) {
          console.log(`   Screenshot: ${err.screenshot}`);
        }
      });
    }
  });
});