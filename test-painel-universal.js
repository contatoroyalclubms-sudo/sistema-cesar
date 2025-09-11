const { chromium } = require('playwright');
const fs = require('fs');

// Painel Universal System Testing Automation
class PainelUniversalTester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.testResults = {
            authentication: {},
            modules: [],
            apis: [],
            functionalityTests: [],
            timestamp: new Date().toISOString()
        };
    }

    async initialize() {
        console.log('🚀 Iniciando testes do sistema Painel Universal...');
        this.browser = await chromium.launch({ 
            headless: false, 
            slowMo: 500 
        });
        this.page = await this.browser.newPage();
        
        // Setup network monitoring
        await this.setupNetworkMonitoring();
        
        console.log('✅ Browser de testes inicializado');
    }

    async setupNetworkMonitoring() {
        this.page.on('request', request => {
            if (request.url().includes('/api/')) {
                this.testResults.apis.push({
                    url: request.url(),
                    method: request.method(),
                    timestamp: new Date().toISOString()
                });
            }
        });

        this.page.on('response', response => {
            if (response.url().includes('/api/')) {
                console.log(`📡 API: ${response.status()} ${response.url()}`);
            }
        });
    }

    async testAuthentication() {
        console.log('🔐 Testando autenticação do Painel Universal...');
        
        try {
            await this.page.goto('http://localhost:5176', {
                waitUntil: 'networkidle'
            });

            // Take screenshot of login page
            await this.page.screenshot({ 
                path: 'painel-universal-login.png', 
                fullPage: true 
            });

            // Wait for login form
            await this.page.waitForSelector('input, form', { timeout: 10000 });

            // Try to find CPF and password fields
            const cpfField = await this.page.locator('input[name="cpf"], input[placeholder*="CPF" i], input[type="text"]').first();
            const passwordField = await this.page.locator('input[name="password"], input[name="senha"], input[type="password"]').first();
            const loginButton = await this.page.locator('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")').first();

            if (await cpfField.isVisible() && await passwordField.isVisible()) {
                console.log('✅ Campos de login identificados');
                
                // Fill with test credentials
                await cpfField.fill('00000000000');
                await passwordField.fill('0000');
                
                console.log('✅ Credenciais preenchidas: CPF 00000000000 / senha 0000');
                
                // Click login
                await loginButton.click();
                
                // Wait for redirect/response
                await this.page.waitForTimeout(3000);
                
                // Check if login was successful
                const currentUrl = this.page.url();
                const hasError = await this.page.locator('.error, .alert-error, [role="alert"]').isVisible().catch(() => false);
                
                if (currentUrl !== 'http://localhost:5176/' && !hasError) {
                    console.log('✅ Login realizado com sucesso!');
                    this.testResults.authentication = {
                        success: true,
                        redirectUrl: currentUrl,
                        message: 'Login successful with CPF 00000000000'
                    };
                } else if (hasError) {
                    console.log('❌ Login falhou - erro detectado na interface');
                    this.testResults.authentication = {
                        success: false,
                        error: 'Login error displayed on page'
                    };
                } else {
                    console.log('⚠️ Login status incerto - URL não mudou');
                    this.testResults.authentication = {
                        success: false,
                        error: 'No URL change after login attempt'
                    };
                }
                
                // Take screenshot after login attempt
                await this.page.screenshot({ 
                    path: 'painel-universal-after-login.png', 
                    fullPage: true 
                });
                
            } else {
                console.log('❌ Campos de login não encontrados');
                this.testResults.authentication = {
                    success: false,
                    error: 'Login form not found'
                };
            }
            
        } catch (error) {
            console.log(`❌ Erro na autenticação: ${error.message}`);
            this.testResults.authentication = {
                success: false,
                error: error.message
            };
        }
    }

    async testModules() {
        console.log('📋 Testando módulos do sistema...');
        
        if (!this.testResults.authentication.success) {
            console.log('⚠️ Pulando teste de módulos - autenticação falhou');
            return;
        }

        try {
            // Wait for dashboard to load
            await this.page.waitForTimeout(2000);
            
            // Look for navigation menu or module list
            const navigationElements = await this.page.locator('nav, .sidebar, .menu, [role="navigation"]').all();
            const moduleLinks = await this.page.locator('a, button, .module, .nav-item, .menu-item').all();
            
            console.log(`🔍 Encontrados ${moduleLinks.length} elementos de navegação`);
            
            for (let i = 0; i < Math.min(moduleLinks.length, 10); i++) {
                try {
                    const element = moduleLinks[i];
                    const text = await element.textContent();
                    const href = await element.getAttribute('href');
                    
                    if (text && text.trim().length > 0) {
                        const moduleInfo = {
                            name: text.trim(),
                            href: href,
                            isVisible: await element.isVisible(),
                            index: i
                        };
                        
                        this.testResults.modules.push(moduleInfo);
                        console.log(`📦 Módulo: ${text.trim()}`);
                    }
                } catch (error) {
                    console.log(`⚠️ Erro ao analisar elemento ${i}: ${error.message}`);
                }
            }
            
        } catch (error) {
            console.log(`❌ Erro ao testar módulos: ${error.message}`);
        }
    }

    async testFunctionalModules() {
        console.log('🔧 Testando funcionalidades específicas dos módulos...');
        
        if (!this.testResults.authentication.success) {
            console.log('⚠️ Pulando teste funcional - autenticação falhou');
            return;
        }

        const modulesToTest = [
            'Fidelidade', 'Dashboard', 'Eventos', 'PDV', 'Relatórios',
            'Estoque', 'Checkin', 'Configurações'
        ];

        for (const moduleName of modulesToTest) {
            try {
                console.log(`🔬 Testando módulo: ${moduleName}`);
                
                // Try to find and click module
                const moduleButton = await this.page.locator(`button:has-text("${moduleName}"), a:has-text("${moduleName}"), [title="${moduleName}"]`).first();
                
                if (await moduleButton.isVisible()) {
                    await moduleButton.click();
                    await this.page.waitForTimeout(2000);
                    
                    // Check if module loaded
                    const hasContent = await this.page.locator('main, .content, .module-content').isVisible();
                    const hasError = await this.page.locator('.error, .alert').isVisible().catch(() => false);
                    
                    const testResult = {
                        module: moduleName,
                        loaded: hasContent && !hasError,
                        url: this.page.url(),
                        hasForm: await this.page.locator('form').isVisible().catch(() => false),
                        hasTable: await this.page.locator('table').isVisible().catch(() => false),
                        hasButton: await this.page.locator('button').count() > 0,
                        timestamp: new Date().toISOString()
                    };
                    
                    this.testResults.functionalityTests.push(testResult);
                    console.log(`✅ ${moduleName}: ${testResult.loaded ? 'OK' : 'FALHA'}`);
                    
                    // Take screenshot of module
                    await this.page.screenshot({ 
                        path: `painel-universal-module-${moduleName.toLowerCase()}.png`, 
                        fullPage: true 
                    });
                    
                } else {
                    console.log(`⚠️ Módulo ${moduleName} não encontrado na interface`);
                    this.testResults.functionalityTests.push({
                        module: moduleName,
                        loaded: false,
                        error: 'Module not found in interface'
                    });
                }
                
            } catch (error) {
                console.log(`❌ Erro ao testar ${moduleName}: ${error.message}`);
                this.testResults.functionalityTests.push({
                    module: moduleName,
                    loaded: false,
                    error: error.message
                });
            }
        }
    }

    async generateReport() {
        console.log('📄 Gerando relatório de testes...');
        
        const report = {
            ...this.testResults,
            summary: {
                authenticationPassed: this.testResults.authentication.success,
                totalModulesFound: this.testResults.modules.length,
                functionalModulesTested: this.testResults.functionalityTests.length,
                functionalModulesPassed: this.testResults.functionalityTests.filter(t => t.loaded).length,
                totalApiCalls: this.testResults.apis.length,
                completionTime: new Date().toISOString()
            }
        };

        // Save JSON report
        fs.writeFileSync('PAINEL_UNIVERSAL_TEST_REPORT.json', JSON.stringify(report, null, 2));
        
        // Generate readable summary
        const summary = `# 📊 RELATÓRIO DE TESTES - PAINEL UNIVERSAL

## 🎯 Resumo Executivo
- **Data dos Testes:** ${new Date().toLocaleDateString('pt-BR')}
- **Autenticação:** ${report.summary.authenticationPassed ? '✅ PASSOU' : '❌ FALHOU'}
- **Módulos Encontrados:** ${report.summary.totalModulesFound}
- **Módulos Funcionais Testados:** ${report.summary.functionalModulesTested}
- **Módulos Funcionais OK:** ${report.summary.functionalModulesPassed}
- **Chamadas API:** ${report.summary.totalApiCalls}

## 🔐 Teste de Autenticação
- **Status:** ${report.authentication.success ? 'SUCESSO' : 'FALHA'}
- **Credenciais:** CPF 00000000000 / senha 0000
${report.authentication.redirectUrl ? `- **URL Pós-Login:** ${report.authentication.redirectUrl}` : ''}
${report.authentication.error ? `- **Erro:** ${report.authentication.error}` : ''}

## 📋 Módulos Identificados
${report.modules.map(m => `- **${m.name}** ${m.href ? `(${m.href})` : ''} ${m.isVisible ? '✅' : '❌'}`).join('\n')}

## 🔧 Testes Funcionais por Módulo
${report.functionalityTests.map(test => `
### ${test.module}
- **Status:** ${test.loaded ? '✅ FUNCIONANDO' : '❌ FALHA'}
- **URL:** ${test.url || 'N/A'}
- **Tem Formulário:** ${test.hasForm ? 'Sim' : 'Não'}
- **Tem Tabela:** ${test.hasTable ? 'Sim' : 'Não'}
- **Tem Botões:** ${test.hasButton ? 'Sim' : 'Não'}
${test.error ? `- **Erro:** ${test.error}` : ''}
`).join('\n')}

## 📡 APIs Descobertas
${report.apis.slice(0, 10).map(api => `- ${api.method} ${api.url}`).join('\n')}

---
*Relatório gerado automaticamente - ${new Date().toLocaleString('pt-BR')}*
`;

        fs.writeFileSync('PAINEL_UNIVERSAL_TEST_SUMMARY.md', summary);
        
        console.log('📄 Relatório salvo em: PAINEL_UNIVERSAL_TEST_REPORT.json');
        console.log('📋 Resumo salvo em: PAINEL_UNIVERSAL_TEST_SUMMARY.md');
    }

    async runCompleteTest() {
        console.log('🚀 Executando bateria completa de testes do Painel Universal...');
        
        try {
            await this.initialize();
            await this.testAuthentication();
            await this.testModules();
            await this.testFunctionalModules();
            
            console.log('✅ Todos os testes executados');
            
        } catch (error) {
            console.error('❌ Erro fatal durante os testes:', error);
        } finally {
            await this.generateReport();
            if (this.browser) {
                await this.browser.close();
            }
        }
    }
}

// Execute tests
if (require.main === module) {
    const tester = new PainelUniversalTester();
    tester.runCompleteTest()
        .then(() => {
            console.log('🎉 Bateria de testes do Painel Universal concluída!');
            process.exit(0);
        })
        .catch(error => {
            console.error('💥 Erro fatal nos testes:', error);
            process.exit(1);
        });
}

module.exports = PainelUniversalTester;