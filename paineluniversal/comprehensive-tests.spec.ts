import { test, expect, Page, BrowserContext } from '@playwright/test';
import { chromium, firefox, webkit } from '@playwright/test';

// Test Configuration
const FRONTEND_URL = 'http://localhost:5177';
const BACKEND_URL = 'http://localhost:8001';
const TEST_CREDENTIALS = {
  cpf: '00000000000',
  password: '0000'
};

// Global test state
let testResults: any[] = [];
let networkRequests: any[] = [];
let consoleMessages: any[] = [];
let errors: any[] = [];

test.describe('🔍 Sistema Painel Universal - Comprehensive Test Suite', () => {
  
  test.beforeEach(async ({ page, context }) => {
    // Setup network monitoring
    page.on('request', request => {
      networkRequests.push({
        timestamp: new Date().toISOString(),
        method: request.method(),
        url: request.url(),
        headers: request.headers(),
        postData: request.postData()
      });
    });

    page.on('response', response => {
      const request = networkRequests.find(req => req.url === response.url());
      if (request) {
        request.status = response.status();
        request.statusText = response.statusText();
        request.responseHeaders = response.headers();
        if (response.status() >= 400) {
          errors.push({
            type: 'Network Error',
            url: response.url(),
            status: response.status(),
            statusText: response.statusText(),
            timestamp: new Date().toISOString()
          });
        }
      }
    });

    // Setup console monitoring
    page.on('console', msg => {
      consoleMessages.push({
        timestamp: new Date().toISOString(),
        type: msg.type(),
        text: msg.text(),
        location: msg.location()
      });
      
      if (msg.type() === 'error') {
        errors.push({
          type: 'Console Error',
          message: msg.text(),
          location: msg.location(),
          timestamp: new Date().toISOString()
        });
      }
    });

    // Setup page error monitoring
    page.on('pageerror', error => {
      errors.push({
        type: 'Page Error',
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });
    });

    // Setup request failure monitoring
    page.on('requestfailed', request => {
      errors.push({
        type: 'Request Failed',
        url: request.url(),
        failure: request.failure(),
        timestamp: new Date().toISOString()
      });
    });
  });

  test('🚀 1. SISTEMA - Verificação inicial e conectividade', async ({ page }) => {
    console.log('\n=== TESTE 1: VERIFICAÇÃO INICIAL ===');
    
    // Test backend availability
    const backendHealthResponse = await page.request.get(`${BACKEND_URL}/docs`);
    expect(backendHealthResponse.status()).toBe(200);
    console.log('✅ Backend accessible at', BACKEND_URL);
    
    // Test frontend loading
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    
    const title = await page.title();
    console.log('📱 Frontend title:', title);
    
    // Take initial screenshot
    await page.screenshot({ path: 'screenshots/01-initial-load.png', fullPage: true });
    
    testResults.push({
      test: 'Sistema - Conectividade',
      status: 'PASSED',
      details: 'Backend and Frontend accessible',
      timestamp: new Date().toISOString()
    });
  });

  test('🔐 2. AUTENTICAÇÃO - Login com credenciais válidas', async ({ page }) => {
    console.log('\n=== TESTE 2: AUTENTICAÇÃO ===');
    
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Take screenshot before login
    await page.screenshot({ path: 'screenshots/02-before-login.png', fullPage: true });
    
    // Wait for login form
    await page.waitForSelector('input[type="text"], input[name="cpf"], input[placeholder*="CPF"]', { timeout: 10000 });
    
    // Try multiple possible selectors for CPF field
    const cpfSelectors = [
      'input[name="cpf"]',
      'input[placeholder*="CPF"]',
      'input[placeholder*="cpf"]',
      'input[type="text"]:first-of-type',
      'input:first-of-type'
    ];
    
    let cpfInput = null;
    for (const selector of cpfSelectors) {
      try {
        cpfInput = await page.$(selector);
        if (cpfInput) {
          console.log(`✅ Found CPF input with selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!cpfInput) {
      await page.screenshot({ path: 'screenshots/02-login-form-not-found.png', fullPage: true });
      throw new Error('CPF input field not found');
    }
    
    // Fill CPF
    await page.fill(cpfSelectors[0], TEST_CREDENTIALS.cpf);
    console.log('📝 CPF filled:', TEST_CREDENTIALS.cpf);
    
    // Try multiple possible selectors for password field
    const passwordSelectors = [
      'input[name="password"]',
      'input[name="senha"]',
      'input[type="password"]',
      'input[placeholder*="senha"]',
      'input[placeholder*="Senha"]'
    ];
    
    let passwordInput = null;
    for (const selector of passwordSelectors) {
      try {
        passwordInput = await page.$(selector);
        if (passwordInput) {
          console.log(`✅ Found password input with selector: ${selector}`);
          await page.fill(selector, TEST_CREDENTIALS.password);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!passwordInput) {
      await page.screenshot({ path: 'screenshots/02-password-field-not-found.png', fullPage: true });
      throw new Error('Password input field not found');
    }
    
    console.log('📝 Password filled');
    
    // Take screenshot after filling form
    await page.screenshot({ path: 'screenshots/02-form-filled.png', fullPage: true });
    
    // Try to find and click login button
    const loginButtonSelectors = [
      'button[type="submit"]',
      'button:has-text("Entrar")',
      'button:has-text("Login")',
      'button:has-text("ENTRAR")',
      '.login-button',
      '#login-button',
      'input[type="submit"]'
    ];
    
    let loginClicked = false;
    for (const selector of loginButtonSelectors) {
      try {
        const button = await page.$(selector);
        if (button) {
          console.log(`🔘 Found login button with selector: ${selector}`);
          await button.click();
          loginClicked = true;
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!loginClicked) {
      // Try pressing Enter as fallback
      await page.keyboard.press('Enter');
      console.log('⌨️ Pressed Enter as fallback for login');
    }
    
    // Wait for navigation or error message
    try {
      await page.waitForURL('**/dashboard*', { timeout: 5000 });
      console.log('✅ Successfully redirected to dashboard');
      
      await page.screenshot({ path: 'screenshots/02-after-login-success.png', fullPage: true });
      
      testResults.push({
        test: 'Autenticação - Login válido',
        status: 'PASSED',
        details: 'Login successful, redirected to dashboard',
        timestamp: new Date().toISOString()
      });
    } catch (e) {
      await page.waitForTimeout(2000); // Wait for any error messages
      await page.screenshot({ path: 'screenshots/02-after-login-failed.png', fullPage: true });
      
      // Check for error messages
      const errorSelectors = [
        '.error',
        '.alert',
        '.error-message',
        '[role="alert"]',
        '.toast',
        '.notification'
      ];
      
      let errorMessage = '';
      for (const selector of errorSelectors) {
        try {
          const errorEl = await page.$(selector);
          if (errorEl) {
            errorMessage = await errorEl.textContent() || '';
            break;
          }
        } catch (e) {
          continue;
        }
      }
      
      testResults.push({
        test: 'Autenticação - Login válido',
        status: 'FAILED',
        details: `Login failed. Error: ${errorMessage || 'No error message found'}`,
        timestamp: new Date().toISOString()
      });
    }
  });

  test('🧭 3. NAVEGAÇÃO - Teste completo de todos os módulos', async ({ page }) => {
    console.log('\n=== TESTE 3: NAVEGAÇÃO COMPLETA ===');
    
    // First login
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    try {
      await page.fill('input[name="cpf"], input[type="text"]:first-of-type', TEST_CREDENTIALS.cpf);
      await page.fill('input[name="password"], input[type="password"]', TEST_CREDENTIALS.password);
      await page.click('button[type="submit"], button:has-text("Entrar")');
      await page.waitForTimeout(3000);
    } catch (e) {
      console.log('⚠️ Login process in navigation test failed, continuing...');
    }
    
    await page.screenshot({ path: 'screenshots/03-navigation-start.png', fullPage: true });
    
    // Define expected modules based on MEEP analysis
    const expectedModules = [
      'Dashboard',
      'Eventos',
      'PDV',
      'Check-in',
      'Estoque',
      'Produtos',
      'Relatórios',
      'Financeiro',
      'Configurações',
      'Usuários',
      'Mesas',
      'KDS',
      'Cashless',
      'Satisfação',
      'Equipamentos',
      'Gamificação'
    ];
    
    let accessibleModules = [];
    let inaccessibleModules = [];
    
    for (const module of expectedModules) {
      try {
        // Try multiple ways to find the module link
        const moduleSelectors = [
          `a[href*="${module.toLowerCase()}"]`,
          `a:has-text("${module}")`,
          `li:has-text("${module}") a`,
          `[data-testid="${module.toLowerCase()}"]`,
          `button:has-text("${module}")`,
          `.menu-item:has-text("${module}")`,
          `.nav-link:has-text("${module}")`
        ];
        
        let moduleFound = false;
        for (const selector of moduleSelectors) {
          try {
            const moduleEl = await page.$(selector);
            if (moduleEl) {
              console.log(`🔍 Found module: ${module} with selector: ${selector}`);
              
              // Click the module
              await moduleEl.click();
              await page.waitForTimeout(1500);
              
              // Take screenshot of the module
              await page.screenshot({ 
                path: `screenshots/03-module-${module.toLowerCase()}.png`, 
                fullPage: true 
              });
              
              // Check if module loaded successfully
              const currentUrl = page.url();
              const hasContent = await page.locator('main, .content, .module-content, .page-content').count() > 0;
              
              if (hasContent || currentUrl.includes(module.toLowerCase())) {
                accessibleModules.push({
                  name: module,
                  status: 'ACCESSIBLE',
                  url: currentUrl,
                  selector: selector
                });
                console.log(`✅ ${module} module accessible`);
              } else {
                accessibleModules.push({
                  name: module,
                  status: 'LOADED_BUT_EMPTY',
                  url: currentUrl,
                  selector: selector
                });
                console.log(`⚠️ ${module} module found but appears empty`);
              }
              
              moduleFound = true;
              break;
            }
          } catch (e) {
            continue;
          }
        }
        
        if (!moduleFound) {
          inaccessibleModules.push({
            name: module,
            status: 'NOT_FOUND',
            error: 'Module link not found in DOM'
          });
          console.log(`❌ ${module} module not found`);
        }
        
      } catch (error) {
        inaccessibleModules.push({
          name: module,
          status: 'ERROR',
          error: error.message
        });
        console.log(`❌ Error accessing ${module}:`, error.message);
      }
      
      // Small delay between modules
      await page.waitForTimeout(500);
    }
    
    testResults.push({
      test: 'Navegação - Módulos acessíveis',
      status: accessibleModules.length > inaccessibleModules.length ? 'PASSED' : 'PARTIAL',
      details: {
        accessible: accessibleModules,
        inaccessible: inaccessibleModules,
        summary: `${accessibleModules.length}/${expectedModules.length} modules accessible`
      },
      timestamp: new Date().toISOString()
    });
  });

  test('🔧 4. CRUD - Teste de funcionalidades básicas', async ({ page }) => {
    console.log('\n=== TESTE 4: FUNCIONALIDADES CRUD ===');
    
    // Login first
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    try {
      await page.fill('input[name="cpf"], input[type="text"]:first-of-type', TEST_CREDENTIALS.cpf);
      await page.fill('input[name="password"], input[type="password"]', TEST_CREDENTIALS.password);
      await page.click('button[type="submit"], button:has-text("Entrar")');
      await page.waitForTimeout(3000);
    } catch (e) {
      console.log('⚠️ Login for CRUD test failed');
    }
    
    const crudModules = [
      {
        name: 'Eventos',
        createButton: 'button:has-text("Novo"), button:has-text("Criar"), button:has-text("Adicionar")',
        formFields: ['input[name="nome"], input[placeholder*="nome"]', 'textarea[name="descricao"]'],
        listSelector: '.table, .list, .grid, .eventos-list'
      },
      {
        name: 'Produtos',
        createButton: 'button:has-text("Novo"), button:has-text("Criar"), button:has-text("Adicionar")',
        formFields: ['input[name="nome"], input[placeholder*="nome"]', 'input[name="preco"], input[placeholder*="preço"]'],
        listSelector: '.table, .list, .grid, .produtos-list'
      },
      {
        name: 'Usuários',
        createButton: 'button:has-text("Novo"), button:has-text("Criar"), button:has-text("Adicionar")',
        formFields: ['input[name="nome"], input[placeholder*="nome"]', 'input[name="cpf"], input[placeholder*="CPF"]'],
        listSelector: '.table, .list, .grid, .usuarios-list'
      }
    ];
    
    let crudResults = [];
    
    for (const module of crudModules) {
      try {
        console.log(`🔧 Testing CRUD for ${module.name}...`);
        
        // Navigate to module
        const moduleLink = await page.$(`a:has-text("${module.name}"), a[href*="${module.name.toLowerCase()}"]`);
        if (moduleLink) {
          await moduleLink.click();
          await page.waitForTimeout(2000);
          
          // Take screenshot of module
          await page.screenshot({ 
            path: `screenshots/04-crud-${module.name.toLowerCase()}-list.png`, 
            fullPage: true 
          });
          
          // Check if list exists
          const hasListView = await page.locator(module.listSelector).count() > 0;
          
          // Try to find create button
          const createButton = await page.$(module.createButton);
          const hasCreateButton = createButton !== null;
          
          if (hasCreateButton) {
            // Click create button
            await createButton.click();
            await page.waitForTimeout(1500);
            
            // Take screenshot of create form
            await page.screenshot({ 
              path: `screenshots/04-crud-${module.name.toLowerCase()}-create.png`, 
              fullPage: true 
            });
            
            // Check if form fields exist
            let formFieldsFound = 0;
            for (const fieldSelector of module.formFields) {
              const field = await page.$(fieldSelector);
              if (field) {
                formFieldsFound++;
              }
            }
            
            crudResults.push({
              module: module.name,
              listView: hasListView,
              createButton: hasCreateButton,
              formFields: `${formFieldsFound}/${module.formFields.length}`,
              status: hasListView && hasCreateButton && formFieldsFound > 0 ? 'FUNCTIONAL' : 'PARTIAL'
            });
            
          } else {
            crudResults.push({
              module: module.name,
              listView: hasListView,
              createButton: false,
              formFields: '0/0',
              status: hasListView ? 'READ_ONLY' : 'NOT_FUNCTIONAL'
            });
          }
          
        } else {
          crudResults.push({
            module: module.name,
            listView: false,
            createButton: false,
            formFields: '0/0',
            status: 'NOT_FOUND'
          });
        }
        
      } catch (error) {
        crudResults.push({
          module: module.name,
          error: error.message,
          status: 'ERROR'
        });
      }
    }
    
    testResults.push({
      test: 'CRUD - Funcionalidades básicas',
      status: crudResults.some(r => r.status === 'FUNCTIONAL') ? 'PARTIAL' : 'FAILED',
      details: crudResults,
      timestamp: new Date().toISOString()
    });
  });

  test('🌐 5. API - Compatibilidade Frontend-Backend', async ({ page }) => {
    console.log('\n=== TESTE 5: COMPATIBILIDADE API ===');
    
    // Clear previous network requests
    networkRequests = [];
    
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Perform login to generate API calls
    try {
      await page.fill('input[name="cpf"], input[type="text"]:first-of-type', TEST_CREDENTIALS.cpf);
      await page.fill('input[name="password"], input[type="password"]', TEST_CREDENTIALS.password);
      await page.click('button[type="submit"], button:has-text("Entrar")');
      await page.waitForTimeout(3000);
    } catch (e) {
      console.log('⚠️ Login for API test failed');
    }
    
    // Navigate through different modules to generate more API calls
    const moduleLinks = await page.$$('a[href*="/"], nav a, .menu a');
    
    for (let i = 0; i < Math.min(moduleLinks.length, 5); i++) {
      try {
        await moduleLinks[i].click();
        await page.waitForTimeout(1000);
      } catch (e) {
        continue;
      }
    }
    
    // Analyze API calls
    const apiCalls = networkRequests.filter(req => 
      req.url.includes('localhost:8001') || 
      req.url.includes('/api/') ||
      req.method !== 'GET' || 
      req.url.includes('backend')
    );
    
    const successfulCalls = apiCalls.filter(call => call.status && call.status < 400);
    const failedCalls = apiCalls.filter(call => call.status && call.status >= 400);
    const corsErrors = errors.filter(error => 
      error.message?.includes('CORS') || 
      error.message?.includes('Access-Control')
    );
    
    console.log(`📊 API Analysis:`);
    console.log(`   Total API calls: ${apiCalls.length}`);
    console.log(`   Successful: ${successfulCalls.length}`);
    console.log(`   Failed: ${failedCalls.length}`);
    console.log(`   CORS errors: ${corsErrors.length}`);
    
    testResults.push({
      test: 'API - Compatibilidade Frontend-Backend',
      status: failedCalls.length > successfulCalls.length ? 'FAILED' : 'PASSED',
      details: {
        totalCalls: apiCalls.length,
        successful: successfulCalls.length,
        failed: failedCalls.length,
        corsErrors: corsErrors.length,
        failedCallDetails: failedCalls.map(call => ({
          url: call.url,
          method: call.method,
          status: call.status
        }))
      },
      timestamp: new Date().toISOString()
    });
  });

  test('📱 6. RESPONSIVIDADE - Teste mobile e desktop', async ({ page }) => {
    console.log('\n=== TESTE 6: RESPONSIVIDADE ===');
    
    const viewports = [
      { name: 'Desktop', width: 1920, height: 1080 },
      { name: 'Tablet', width: 768, height: 1024 },
      { name: 'Mobile', width: 375, height: 667 }
    ];
    
    let responsiveResults = [];
    
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto(FRONTEND_URL);
      await page.waitForLoadState('networkidle');
      
      // Take screenshot
      await page.screenshot({ 
        path: `screenshots/06-responsive-${viewport.name.toLowerCase()}.png`, 
        fullPage: true 
      });
      
      // Check if layout adapts properly
      const hasHamburgerMenu = await page.locator('.hamburger, .menu-toggle, [aria-label*="menu"]').count() > 0;
      const hasSidebar = await page.locator('.sidebar, .navigation, .nav-menu').count() > 0;
      const contentOverflows = await page.evaluate(() => {
        return document.body.scrollWidth > window.innerWidth;
      });
      
      responsiveResults.push({
        viewport: viewport.name,
        size: `${viewport.width}x${viewport.height}`,
        hamburgerMenu: hasHamburgerMenu,
        sidebar: hasSidebar,
        contentOverflow: contentOverflows,
        status: !contentOverflows ? 'GOOD' : 'NEEDS_IMPROVEMENT'
      });
      
      console.log(`📱 ${viewport.name}: ${!contentOverflows ? '✅ Good' : '⚠️ Content overflow'}`);
    }
    
    testResults.push({
      test: 'Responsividade - Multi-device',
      status: responsiveResults.every(r => r.status === 'GOOD') ? 'PASSED' : 'PARTIAL',
      details: responsiveResults,
      timestamp: new Date().toISOString()
    });
  });

  test('🔍 7. PERFORMANCE - Análise de carregamento', async ({ page }) => {
    console.log('\n=== TESTE 7: PERFORMANCE ===');
    
    const performanceMetrics = {};
    
    // Test initial page load
    const startTime = Date.now();
    await page.goto(FRONTEND_URL);
    const loadTime = Date.now() - startTime;
    
    await page.waitForLoadState('networkidle');
    const networkIdleTime = Date.now() - startTime;
    
    // Get performance metrics
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
      };
    });
    
    // Count resources loaded
    const resources = await page.evaluate(() => {
      return performance.getEntriesByType('resource').length;
    });
    
    performanceMetrics.initialLoad = {
      loadTime: loadTime,
      networkIdleTime: networkIdleTime,
      domContentLoaded: metrics.domContentLoaded,
      firstContentfulPaint: metrics.firstContentfulPaint,
      resourcesLoaded: resources
    };
    
    console.log(`⚡ Performance Results:`);
    console.log(`   Load Time: ${loadTime}ms`);
    console.log(`   Network Idle: ${networkIdleTime}ms`);
    console.log(`   Resources: ${resources}`);
    console.log(`   FCP: ${metrics.firstContentfulPaint}ms`);
    
    const performanceScore = 
      (loadTime < 3000 ? 25 : 0) +
      (networkIdleTime < 5000 ? 25 : 0) +
      (metrics.firstContentfulPaint < 2000 ? 25 : 0) +
      (resources < 50 ? 25 : 0);
    
    testResults.push({
      test: 'Performance - Carregamento',
      status: performanceScore >= 75 ? 'PASSED' : performanceScore >= 50 ? 'PARTIAL' : 'FAILED',
      score: `${performanceScore}/100`,
      details: performanceMetrics,
      timestamp: new Date().toISOString()
    });
  });

  test.afterAll(async () => {
    // Generate comprehensive report
    const report = {
      timestamp: new Date().toISOString(),
      testSummary: {
        total: testResults.length,
        passed: testResults.filter(t => t.status === 'PASSED').length,
        partial: testResults.filter(t => t.status === 'PARTIAL').length,
        failed: testResults.filter(t => t.status === 'FAILED').length
      },
      systemInfo: {
        frontend: FRONTEND_URL,
        backend: BACKEND_URL,
        credentials: TEST_CREDENTIALS
      },
      detailedResults: testResults,
      networkAnalysis: {
        totalRequests: networkRequests.length,
        apiCalls: networkRequests.filter(req => req.url.includes('/api/')).length,
        failedRequests: networkRequests.filter(req => req.status >= 400).length
      },
      errors: errors,
      consoleMessages: consoleMessages.filter(msg => msg.type === 'error'),
      recommendations: [
        'Fix CORS configuration between frontend and backend',
        'Implement proper error handling in frontend components', 
        'Add loading states for better UX',
        'Optimize bundle size and lazy loading',
        'Add proper form validation',
        'Implement comprehensive test coverage',
        'Add proper authentication token management'
      ]
    };
    
    // Save report to file
    await require('fs').promises.writeFile(
      'comprehensive-test-report.json',
      JSON.stringify(report, null, 2)
    );
    
    console.log('\n' + '='.repeat(60));
    console.log('🎯 COMPREHENSIVE TEST REPORT SUMMARY');
    console.log('='.repeat(60));
    console.log(`📊 Tests Run: ${report.testSummary.total}`);
    console.log(`✅ Passed: ${report.testSummary.passed}`);
    console.log(`⚠️ Partial: ${report.testSummary.partial}`);
    console.log(`❌ Failed: ${report.testSummary.failed}`);
    console.log(`🌐 Network Requests: ${report.networkAnalysis.totalRequests}`);
    console.log(`🚫 Errors Found: ${report.errors.length}`);
    console.log('\n📄 Full report saved to: comprehensive-test-report.json');
    console.log('='.repeat(60));
  });
});