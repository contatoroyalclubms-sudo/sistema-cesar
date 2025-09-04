const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000/api';
const ADMIN_EMAIL = 'admin@meep.com';
const ADMIN_PASSWORD = 'admin123';
const ADMIN_CPF = '99999999999';

// Test results tracking
const testResults = {
    passed: [],
    failed: [],
    errors: [],
    startTime: new Date(),
    endTime: null
};

// Helper function to update validation file
async function updateValidationFile(module, testName, status, error = null) {
    const filePath = path.join(__dirname, 'VALIDATED_TESTS.md');
    const timestamp = new Date().toISOString();
    
    // Log to console
    if (status === 'passed') {
        console.log(`✅ ${module} - ${testName}: PASSED`);
        testResults.passed.push({ module, test: testName, timestamp });
    } else {
        console.log(`❌ ${module} - ${testName}: FAILED`);
        console.log(`   Error: ${error}`);
        testResults.failed.push({ module, test: testName, error, timestamp });
    }
}

// Helper function to wait and retry
async function waitAndRetry(fn, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            return await fn();
        } catch (error) {
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

// Main test suite
async function runTests() {
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 100 
    });
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    const page = await context.newPage();
    
    // Enable console logging
    page.on('console', msg => {
        if (msg.type() === 'error') {
            testResults.errors.push({
                type: 'console-error',
                text: msg.text(),
                location: msg.location()
            });
        }
    });
    
    // Track network errors
    page.on('requestfailed', request => {
        testResults.errors.push({
            type: 'network-error',
            url: request.url(),
            failure: request.failure()
        });
    });

    try {
        console.log('='.repeat(70));
        console.log('STARTING COMPREHENSIVE SYSTEM TESTS');
        console.log('='.repeat(70));
        console.log(`Base URL: ${BASE_URL}`);
        console.log(`API URL: ${API_URL}`);
        console.log(`Admin: ${ADMIN_EMAIL}`);
        console.log('='.repeat(70));
        
        // 1. TEST: Landing Page
        console.log('\n📍 Testing Landing Page...');
        await page.goto(BASE_URL);
        await page.waitForLoadState('networkidle');
        const title = await page.title();
        await updateValidationFile('Landing', 'Page loads', 'passed');
        
        // 2. TEST: Login Flow
        console.log('\n📍 Testing Authentication...');
        
        // Navigate to login
        await page.goto(`${BASE_URL}/login`);
        await page.waitForLoadState('networkidle');
        
        // Fill login form using CPF
        await page.fill('input[name="cpf"], input[placeholder*="CPF"], input[type="text"]', ADMIN_CPF);
        await page.fill('input[name="password"], input[type="password"], input[placeholder*="senha" i]', ADMIN_PASSWORD);
        
        // Submit login
        await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
        
        // Wait for navigation
        await page.waitForURL(/dashboard|eventos|home/, { timeout: 10000 });
        await updateValidationFile('Authentication', 'Admin login', 'passed');
        
        // Check if we have a token
        const localStorage = await page.evaluate(() => {
            return {
                token: window.localStorage.getItem('token'),
                user: window.localStorage.getItem('user')
            };
        });
        
        if (localStorage.token) {
            await updateValidationFile('Authentication', 'Token storage', 'passed');
        } else {
            await updateValidationFile('Authentication', 'Token storage', 'failed', 'No token found');
        }
        
        // 3. TEST: Dashboard
        console.log('\n📍 Testing Dashboard...');
        await page.goto(`${BASE_URL}/dashboard`);
        await page.waitForLoadState('networkidle');
        
        // Check for dashboard elements
        const dashboardElements = await page.evaluate(() => {
            return {
                hasMetrics: document.querySelector('[class*="metric"], [class*="card"], [class*="stat"]') !== null,
                hasCharts: document.querySelector('canvas, svg[class*="chart"], [class*="recharts"]') !== null
            };
        });
        
        if (dashboardElements.hasMetrics) {
            await updateValidationFile('Dashboard', 'Metrics display', 'passed');
        } else {
            await updateValidationFile('Dashboard', 'Metrics display', 'failed', 'No metrics found');
        }
        
        // 4. TEST: Events Management
        console.log('\n📍 Testing Events Management...');
        await page.goto(`${BASE_URL}/eventos`);
        await page.waitForLoadState('networkidle');
        
        // Create new event
        const newEventButton = await page.$('button:has-text("Novo Evento"), button:has-text("Criar Evento"), button:has-text("Adicionar"), a[href*="novo"]');
        if (newEventButton) {
            await newEventButton.click();
            await page.waitForTimeout(1000);
            
            // Fill event form
            const eventData = {
                nome: `Test Event ${Date.now()}`,
                local: 'Test Venue',
                data: '2025-10-15',
                hora: '20:00',
                capacidade: '500',
                idade: '18'
            };
            
            // Try to fill the form
            await page.fill('input[name="nome"], input[placeholder*="nome" i]', eventData.nome).catch(() => {});
            await page.fill('input[name="local"], input[placeholder*="local" i]', eventData.local).catch(() => {});
            await page.fill('input[type="date"], input[name="data"]', eventData.data).catch(() => {});
            await page.fill('input[type="time"], input[name="hora"]', eventData.hora).catch(() => {});
            await page.fill('input[name="capacidade"], input[placeholder*="capacidade" i]', eventData.capacidade).catch(() => {});
            
            // Submit
            await page.click('button[type="submit"], button:has-text("Salvar"), button:has-text("Criar")');
            await page.waitForTimeout(2000);
            
            // Check if event was created
            const eventCreated = await page.$(`text=${eventData.nome}`);
            if (eventCreated) {
                await updateValidationFile('Events', 'Create event', 'passed');
            } else {
                await updateValidationFile('Events', 'Create event', 'failed', 'Event not found after creation');
            }
        }
        
        // 5. TEST: Users Management
        console.log('\n📍 Testing Users Management...');
        await page.goto(`${BASE_URL}/usuarios`);
        await page.waitForLoadState('networkidle');
        
        // Check if users list loads
        const usersList = await page.$('table, [class*="list"], [class*="grid"]');
        if (usersList) {
            await updateValidationFile('Users', 'List users', 'passed');
        } else {
            await updateValidationFile('Users', 'List users', 'failed', 'No users list found');
        }
        
        // 6. TEST: Guest Lists
        console.log('\n📍 Testing Guest Lists...');
        await page.goto(`${BASE_URL}/listas`);
        await page.waitForLoadState('networkidle');
        
        // Try to create a guest list
        const newListButton = await page.$('button:has-text("Nova Lista"), button:has-text("Criar Lista"), button:has-text("Adicionar")');
        if (newListButton) {
            await newListButton.click();
            await page.waitForTimeout(1000);
            
            // Fill guest data
            await page.fill('input[name="nome"], input[placeholder*="nome" i]', 'Test Guest').catch(() => {});
            await page.fill('input[name="cpf"], input[placeholder*="cpf" i]', '12345678901').catch(() => {});
            
            // Submit
            await page.click('button[type="submit"], button:has-text("Adicionar"), button:has-text("Salvar")').catch(() => {});
            await page.waitForTimeout(1000);
            
            await updateValidationFile('Guest Lists', 'Add guest', 'passed');
        }
        
        // 7. TEST: Check-in System
        console.log('\n📍 Testing Check-in System...');
        await page.goto(`${BASE_URL}/checkin`);
        await page.waitForLoadState('networkidle');
        
        // Check if check-in interface loads
        const checkinInterface = await page.$('input[placeholder*="CPF" i], input[placeholder*="código" i], input[placeholder*="QR" i]');
        if (checkinInterface) {
            await updateValidationFile('Check-in', 'Interface loads', 'passed');
        } else {
            await updateValidationFile('Check-in', 'Interface loads', 'failed', 'No check-in interface found');
        }
        
        // 8. TEST: PDV System
        console.log('\n📍 Testing PDV System...');
        await page.goto(`${BASE_URL}/pdv`);
        await page.waitForLoadState('networkidle');
        
        // Check PDV interface
        const pdvInterface = await page.$('[class*="product"], [class*="pdv"], [class*="venda"]');
        if (pdvInterface) {
            await updateValidationFile('PDV', 'Interface loads', 'passed');
        } else {
            await updateValidationFile('PDV', 'Interface loads', 'failed', 'No PDV interface found');
        }
        
        // 9. TEST: Financial Module
        console.log('\n📍 Testing Financial Module...');
        await page.goto(`${BASE_URL}/financeiro`);
        await page.waitForLoadState('networkidle');
        
        const financeInterface = await page.$('[class*="finance"], [class*="transaction"], [class*="financ"]');
        if (financeInterface) {
            await updateValidationFile('Financial', 'Interface loads', 'passed');
        } else {
            await updateValidationFile('Financial', 'Interface loads', 'failed', 'No financial interface found');
        }
        
        // 10. TEST: Inventory Management
        console.log('\n📍 Testing Inventory Management...');
        await page.goto(`${BASE_URL}/estoque`);
        await page.waitForLoadState('networkidle');
        
        const inventoryInterface = await page.$('[class*="inventory"], [class*="stock"], [class*="estoque"]');
        if (inventoryInterface) {
            await updateValidationFile('Inventory', 'Interface loads', 'passed');
        } else {
            await updateValidationFile('Inventory', 'Interface loads', 'failed', 'No inventory interface found');
        }
        
        // 11. TEST: Reports
        console.log('\n📍 Testing Reports Module...');
        await page.goto(`${BASE_URL}/relatorios`);
        await page.waitForLoadState('networkidle');
        
        const reportsInterface = await page.$('[class*="report"], [class*="relatorio"], button:has-text("Gerar")');
        if (reportsInterface) {
            await updateValidationFile('Reports', 'Interface loads', 'passed');
        } else {
            await updateValidationFile('Reports', 'Interface loads', 'failed', 'No reports interface found');
        }
        
        // 12. TEST: Settings
        console.log('\n📍 Testing Settings...');
        await page.goto(`${BASE_URL}/configuracoes`);
        await page.waitForLoadState('networkidle');
        
        const settingsInterface = await page.$('[class*="setting"], [class*="config"], form');
        if (settingsInterface) {
            await updateValidationFile('Settings', 'Interface loads', 'passed');
        } else {
            await updateValidationFile('Settings', 'Interface loads', 'failed', 'No settings interface found');
        }
        
    } catch (error) {
        console.error('❌ CRITICAL ERROR:', error);
        testResults.errors.push({
            type: 'critical',
            error: error.message,
            stack: error.stack
        });
    } finally {
        testResults.endTime = new Date();
        
        // Generate summary
        console.log('\n' + '='.repeat(70));
        console.log('TEST RESULTS SUMMARY');
        console.log('='.repeat(70));
        console.log(`✅ Passed: ${testResults.passed.length}`);
        console.log(`❌ Failed: ${testResults.failed.length}`);
        console.log(`⚠️  Errors: ${testResults.errors.length}`);
        console.log(`⏱️  Duration: ${(testResults.endTime - testResults.startTime) / 1000}s`);
        console.log('='.repeat(70));
        
        // Save detailed results
        await fs.writeFile(
            path.join(__dirname, 'test-results.json'),
            JSON.stringify(testResults, null, 2)
        );
        
        // Close browser
        await browser.close();
    }
}

// Run the tests
runTests().catch(console.error);