/**
 * MEEP SYSTEM - COMPREHENSIVE REVERSE ENGINEERING v2
 * Focused analysis with specific credentials and deep module exploration
 * 
 * Target: https://beta.portal.meep.com.br
 * Login: toretomal@icloud.com
 * Password: 10041210Cl@
 * 
 * OBJETIVO: Mapear 100% das funcionalidades para replicar no sistema atual
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class MEEPSystemAnalyzer {
    constructor() {
        this.browser = null;
        this.page = null;
        this.analysis = {
            loginSuccessful: false,
            timestamp: new Date().toISOString(),
            credentials: {
                email: 'toretomal@icloud.com',
                password: '10041210Cl@'
            },
            platform: {
                name: 'MEEP Beta Portal',
                url: 'https://beta.portal.meep.com.br',
                technologies: {},
                apiEndpoints: [],
                networkRequests: []
            },
            modules: {
                eventos: { analyzed: false, data: {} },
                eventoCaixa: { analyzed: false, data: {} },
                convidados: { analyzed: false, data: {} },
                pdv: { analyzed: false, data: {} },
                checkin: { analyzed: false, data: {} },
                relatorios: { analyzed: false, data: {} },
                mesas: { analyzed: false, data: {} },
                cashless: { analyzed: false, data: {} },
                kds: { analyzed: false, data: {} },
                dashboard: { analyzed: false, data: {} }
            },
            ui: {
                components: [],
                layouts: [],
                colors: [],
                typography: {},
                navigation: {}
            },
            business: {
                workflows: {},
                dataModels: {},
                validations: {},
                calculations: {}
            },
            screenshots: []
        };
        
        this.screenshotCounter = 1;
        this.setupDirectories();
    }

    setupDirectories() {
        const dirs = [
            'meep-screenshots',
            'meep-data',
            'meep-reports'
        ];
        
        dirs.forEach(dir => {
            const fullPath = path.join(__dirname, dir);
            if (!fs.existsSync(fullPath)) {
                fs.mkdirSync(fullPath, { recursive: true });
            }
        });
    }

    async init() {
        console.log('🔥 INICIANDO ENGENHARIA REVERSA COMPLETA DO MEEP');
        console.log('================================================');
        console.log(`🎯 Target: ${this.analysis.platform.url}`);
        console.log(`📧 Login: ${this.analysis.credentials.email}`);
        console.log(`⏰ Timestamp: ${this.analysis.timestamp}\n`);
        
        this.browser = await chromium.launch({ 
            headless: false,
            slowMo: 1000,
            args: [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        });
        
        const context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        });
        
        this.page = await context.newPage();
        
        // Monitor all network activity
        this.page.on('request', (request) => {
            this.analysis.platform.networkRequests.push({
                type: 'request',
                timestamp: new Date().toISOString(),
                url: request.url(),
                method: request.method(),
                headers: request.headers(),
                postData: request.postData()
            });
        });

        this.page.on('response', async (response) => {
            try {
                const request = response.request();
                const responseBody = await response.text();
                
                this.analysis.platform.networkRequests.push({
                    type: 'response',
                    timestamp: new Date().toISOString(),
                    url: response.url(),
                    status: response.status(),
                    headers: response.headers(),
                    body: responseBody.length > 2000 ? responseBody.substring(0, 2000) + '...' : responseBody
                });
                
                // Extract API endpoints
                if (request.url().includes('/api/') || request.url().includes('api')) {
                    this.analysis.platform.apiEndpoints.push({
                        method: request.method(),
                        url: request.url(),
                        status: response.status(),
                        category: this.categorizeEndpoint(request.url())
                    });
                }
            } catch (e) {
                // Response body not available
            }
        });

        console.log('✅ Browser e monitoramento de rede configurados\n');
    }

    categorizeEndpoint(url) {
        const lowerUrl = url.toLowerCase();
        if (lowerUrl.includes('auth') || lowerUrl.includes('login')) return 'Authentication';
        if (lowerUrl.includes('evento') || lowerUrl.includes('event')) return 'Events';
        if (lowerUrl.includes('usuario') || lowerUrl.includes('user')) return 'Users';
        if (lowerUrl.includes('produto') || lowerUrl.includes('product')) return 'Products';
        if (lowerUrl.includes('caixa') || lowerUrl.includes('financial')) return 'Financial';
        if (lowerUrl.includes('convidado') || lowerUrl.includes('guest')) return 'Guests';
        if (lowerUrl.includes('pdv') || lowerUrl.includes('sale')) return 'Sales';
        if (lowerUrl.includes('checkin')) return 'CheckIn';
        if (lowerUrl.includes('relatorio') || lowerUrl.includes('report')) return 'Reports';
        return 'Other';
    }

    async screenshot(name, description = '') {
        const fileName = `${String(this.screenshotCounter).padStart(3, '0')}-${name.replace(/[^a-zA-Z0-9]/g, '-')}.png`;
        const filePath = path.join(__dirname, 'meep-screenshots', fileName);
        
        await this.page.screenshot({ 
            path: filePath, 
            fullPage: true 
        });
        
        this.analysis.screenshots.push({
            counter: this.screenshotCounter,
            name,
            description,
            fileName,
            url: this.page.url(),
            timestamp: new Date().toISOString()
        });
        
        console.log(`📸 [${this.screenshotCounter}] ${name}${description ? ' - ' + description : ''}`);
        this.screenshotCounter++;
        
        return fileName;
    }

    async performLogin() {
        console.log('🔐 EXECUTANDO LOGIN NO MEEP');
        console.log('============================');
        
        try {
            console.log('📍 Navegando para página de login...');
            await this.page.goto(this.analysis.platform.url, { 
                waitUntil: 'domcontentloaded',
                timeout: 30000 
            });
            
            await this.page.waitForTimeout(3000);
            await this.screenshot('01-homepage', 'Página inicial do MEEP');
            
            // Procurar diferentes seletores para o campo de email
            console.log('🔍 Procurando campo de email...');
            const emailSelectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="username"]',
                'input[name="login"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="e-mail" i]',
                'input[placeholder*="usuário" i]',
                'input[id*="email"]',
                'input[id*="user"]',
                'input[class*="email"]',
                'input[class*="user"]'
            ];
            
            let emailFound = false;
            for (const selector of emailSelectors) {
                try {
                    const element = await this.page.$(selector);
                    if (element) {
                        await element.fill(this.analysis.credentials.email);
                        emailFound = true;
                        console.log(`✅ Email preenchido com seletor: ${selector}`);
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!emailFound) {
                console.log('⚠️ Campo de email não encontrado, tentando abordagem genérica...');
                const inputs = await this.page.$$('input');
                if (inputs.length > 0) {
                    await inputs[0].fill(this.analysis.credentials.email);
                    emailFound = true;
                    console.log('✅ Email preenchido no primeiro input encontrado');
                }
            }
            
            // Procurar campo de senha
            console.log('🔍 Procurando campo de senha...');
            const passwordSelectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[name="senha"]',
                'input[placeholder*="senha" i]',
                'input[placeholder*="password" i]',
                'input[id*="password"]',
                'input[id*="senha"]'
            ];
            
            let passwordFound = false;
            for (const selector of passwordSelectors) {
                try {
                    const element = await this.page.$(selector);
                    if (element) {
                        await element.fill(this.analysis.credentials.password);
                        passwordFound = true;
                        console.log(`✅ Senha preenchida com seletor: ${selector}`);
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            await this.page.waitForTimeout(2000);
            await this.screenshot('02-login-filled', 'Formulário de login preenchido');
            
            // Procurar e clicar no botão de login
            console.log('🔍 Procurando botão de login...');
            const loginButtonSelectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Entrar")',
                'button:has-text("Login")',
                'button:has-text("ENTRAR")',
                'button:has-text("ACESSAR")',
                'button:has-text("Sign In")',
                '.btn-login',
                '.login-btn',
                '.btn-primary',
                '.submit-btn',
                'button.btn'
            ];
            
            let loginClicked = false;
            for (const selector of loginButtonSelectors) {
                try {
                    const element = await this.page.$(selector);
                    if (element) {
                        await element.click();
                        loginClicked = true;
                        console.log(`✅ Botão de login clicado: ${selector}`);
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!loginClicked) {
                console.log('⚠️ Botão não encontrado, tentando Enter...');
                await this.page.keyboard.press('Enter');
            }
            
            // Aguardar redirecionamento
            console.log('⏳ Aguardando redirecionamento...');
            try {
                await this.page.waitForNavigation({ 
                    waitUntil: 'domcontentloaded', 
                    timeout: 15000 
                });
            } catch (e) {
                console.log('⚠️ Timeout na navegação, verificando estado atual...');
                await this.page.waitForTimeout(5000);
            }
            
            await this.screenshot('03-after-login', 'Estado após tentativa de login');
            
            // Verificar se o login foi bem-sucedido
            const currentUrl = this.page.url();
            const pageTitle = await this.page.title();
            
            console.log(`📍 URL atual: ${currentUrl}`);
            console.log(`📄 Título da página: ${pageTitle}`);
            
            // Indicadores de sucesso no login
            const successIndicators = [
                'dashboard',
                'painel',
                'admin',
                'portal',
                'inicio',
                'home',
                'eventos',
                'main'
            ];
            
            const loginSuccess = successIndicators.some(indicator => 
                currentUrl.toLowerCase().includes(indicator) || 
                pageTitle.toLowerCase().includes(indicator)
            ) && !currentUrl.includes('/login');
            
            this.analysis.loginSuccessful = loginSuccess;
            
            if (loginSuccess) {
                console.log('🎉 LOGIN BEM-SUCEDIDO!');
                console.log('======================\n');
                return true;
            } else {
                console.log('❌ Login falhou ou redirecionamento não detectado');
                console.log('Continuando análise do que for acessível...\n');
                return false;
            }
            
        } catch (error) {
            console.error('❌ Erro durante o login:', error.message);
            await this.screenshot('error-login', 'Erro no processo de login');
            return false;
        }
    }

    async analyzeCurrentPage() {
        console.log('🔍 Analisando estrutura da página atual...');
        
        const pageAnalysis = await this.page.evaluate(() => {
            // Função auxiliar para extrair informações de elementos
            const extractElementInfo = (selector, attributes = []) => {
                return Array.from(document.querySelectorAll(selector)).map(el => {
                    const info = {
                        tag: el.tagName.toLowerCase(),
                        text: el.textContent?.trim().substring(0, 100) || '',
                        visible: el.offsetWidth > 0 && el.offsetHeight > 0
                    };
                    
                    attributes.forEach(attr => {
                        if (el[attr]) {
                            info[attr] = el[attr];
                        }
                    });
                    
                    return info;
                });
            };
            
            // Detectar tecnologias frontend
            const detectTechnologies = () => {
                return {
                    react: !!(window.React || document.querySelector('[data-reactroot]')),
                    vue: !!(window.Vue || document.querySelector('[data-v-]')),
                    angular: !!(window.angular || document.querySelector('[ng-app]')),
                    jquery: !!window.jQuery,
                    bootstrap: !!document.querySelector('.container, .row, .col'),
                    materialUI: !!document.querySelector('[class*="Mui"]'),
                    antd: !!document.querySelector('[class*="ant-"]'),
                    tailwind: !!document.querySelector('[class*="bg-"], [class*="text-"], [class*="p-"]')
                };
            };
            
            return {
                url: window.location.href,
                title: document.title,
                technologies: detectTechnologies(),
                navigation: {
                    menus: extractElementInfo('nav, .nav, .navbar, .sidebar, .menu'),
                    links: extractElementInfo('nav a, .nav a, .menu a', ['href', 'className'])
                },
                forms: {
                    forms: extractElementInfo('form', ['action', 'method']),
                    inputs: extractElementInfo('input', ['type', 'name', 'placeholder']),
                    selects: extractElementInfo('select', ['name']),
                    buttons: extractElementInfo('button', ['type', 'className'])
                },
                dataDisplay: {
                    tables: extractElementInfo('table', ['className']),
                    cards: extractElementInfo('.card, .panel, .widget'),
                    lists: extractElementInfo('ul, ol'),
                    charts: extractElementInfo('canvas, svg')
                },
                ui: {
                    modals: extractElementInfo('.modal, .dialog, [role="dialog"]'),
                    dropdowns: extractElementInfo('.dropdown, .select'),
                    tabs: extractElementInfo('.tab, [role="tab"]'),
                    alerts: extractElementInfo('.alert, .notification, .message')
                }
            };
        });
        
        return pageAnalysis;
    }

    async exploreModule(moduleName, searchTerms) {
        console.log(`\n🎯 EXPLORANDO MÓDULO: ${moduleName.toUpperCase()}`);
        console.log('='.repeat(50));
        
        try {
            // Tentar encontrar e clicar no módulo
            let moduleFound = false;
            
            for (const term of searchTerms) {
                try {
                    // Procurar por links/botões com o termo
                    const selectors = [
                        `a:has-text("${term}")`,
                        `button:has-text("${term}")`,
                        `[href*="${term.toLowerCase()}"]`,
                        `.nav-${term.toLowerCase()}`,
                        `[data-testid*="${term.toLowerCase()}"]`,
                        `[aria-label*="${term}"]`
                    ];
                    
                    for (const selector of selectors) {
                        try {
                            const element = await this.page.$(selector);
                            if (element && await element.isVisible()) {
                                console.log(`✅ Encontrado com seletor: ${selector}`);
                                await element.click();
                                await this.page.waitForTimeout(3000);
                                moduleFound = true;
                                break;
                            }
                        } catch (e) {
                            continue;
                        }
                    }
                    
                    if (moduleFound) break;
                } catch (e) {
                    continue;
                }
            }
            
            if (!moduleFound) {
                console.log(`❌ Módulo ${moduleName} não encontrado`);
                this.analysis.modules[moduleName].analyzed = false;
                return;
            }
            
            console.log(`🎉 Módulo ${moduleName} acessado com sucesso!`);
            
            await this.screenshot(`module-${moduleName}`, `Módulo ${moduleName} - Visão Geral`);
            
            // Analisar a página do módulo
            const moduleData = await this.analyzeCurrentPage();
            
            // Análise específica do módulo
            const specificAnalysis = await this.performSpecificModuleAnalysis(moduleName);
            
            // Explorar funcionalidades CRUD
            const crudAnalysis = await this.exploreCRUDOperations(moduleName);
            
            // Salvar dados do módulo
            this.analysis.modules[moduleName] = {
                analyzed: true,
                data: {
                    general: moduleData,
                    specific: specificAnalysis,
                    crud: crudAnalysis,
                    screenshots: []
                }
            };
            
            console.log(`✅ Análise do módulo ${moduleName} concluída\n`);
            
        } catch (error) {
            console.error(`❌ Erro explorando módulo ${moduleName}:`, error.message);
            this.analysis.modules[moduleName].analyzed = false;
        }
    }

    async performSpecificModuleAnalysis(moduleName) {
        console.log(`🔬 Análise específica do módulo: ${moduleName}`);
        
        const analysis = await this.page.evaluate((module) => {
            const data = { moduleName: module, features: {} };
            
            switch (module.toLowerCase()) {
                case 'eventos':
                    data.features = {
                        eventCreationForms: document.querySelectorAll('form, .create-event, .novo-evento').length,
                        eventTypes: Array.from(document.querySelectorAll('select option')).map(opt => opt.textContent?.trim()),
                        dateFields: document.querySelectorAll('input[type="date"], input[type="datetime-local"]').length,
                        statusFields: Array.from(document.querySelectorAll('.status, .situacao')).map(el => el.textContent?.trim()),
                        actionButtons: Array.from(document.querySelectorAll('button')).map(btn => btn.textContent?.trim()),
                        dataTable: document.querySelectorAll('table, .table').length > 0
                    };
                    break;
                    
                case 'eventocaixa':
                case 'caixa':
                    data.features = {
                        transactionTypes: Array.from(document.querySelectorAll('.transaction, .transacao')).length,
                        paymentMethods: Array.from(document.querySelectorAll('.payment, .pagamento')).map(el => el.textContent?.trim()),
                        totals: Array.from(document.querySelectorAll('.total, .valor')).map(el => el.textContent?.trim()),
                        charts: document.querySelectorAll('canvas, svg[class*="chart"]').length,
                        exportButtons: document.querySelectorAll('[class*="export"], .exportar').length
                    };
                    break;
                    
                case 'convidados':
                    data.features = {
                        guestTypes: Array.from(document.querySelectorAll('.guest-type, .tipo-convidado')).map(el => el.textContent?.trim()),
                        statusOptions: Array.from(document.querySelectorAll('.status option, .situacao option')).map(opt => opt.textContent?.trim()),
                        importExport: document.querySelectorAll('[class*="import"], [class*="export"]').length,
                        searchFilters: document.querySelectorAll('input[type="search"], .filter').length,
                        bulkActions: document.querySelectorAll('.bulk, .lote').length
                    };
                    break;
                    
                case 'pdv':
                    data.features = {
                        productCategories: Array.from(document.querySelectorAll('.category, .categoria')).map(el => el.textContent?.trim()),
                        products: document.querySelectorAll('.product, .produto').length,
                        cart: document.querySelectorAll('.cart, .carrinho').length,
                        paymentMethods: Array.from(document.querySelectorAll('.payment-method')).map(el => el.textContent?.trim()),
                        priceDisplays: document.querySelectorAll('.price, .preco').length
                    };
                    break;
                    
                case 'checkin':
                    data.features = {
                        qrCodeScanner: document.querySelectorAll('.qr, .scanner').length,
                        validation: document.querySelectorAll('.validation, .validacao').length,
                        guestSearch: document.querySelectorAll('[placeholder*="convidado"], [placeholder*="guest"]').length,
                        statusDisplay: document.querySelectorAll('.check-status').length
                    };
                    break;
                    
                default:
                    data.features = {
                        forms: document.querySelectorAll('form').length,
                        tables: document.querySelectorAll('table').length,
                        buttons: document.querySelectorAll('button').length,
                        inputs: document.querySelectorAll('input').length
                    };
            }
            
            return data;
        }, moduleName);
        
        return analysis;
    }

    async exploreCRUDOperations(moduleName) {
        console.log(`🔧 Explorando operações CRUD para: ${moduleName}`);
        
        const crud = {
            create: null,
            read: null,
            update: null,
            delete: null
        };
        
        // Explorar CREATE
        const createSelectors = [
            'button:has-text("Criar")',
            'button:has-text("Novo")',
            'button:has-text("Adicionar")',
            'a:has-text("Criar")',
            '.btn-create',
            '.btn-new',
            '+', // Botão de adicionar
            'button[title*="criar"], button[title*="novo"]'
        ];
        
        for (const selector of createSelectors) {
            try {
                const element = await this.page.$(selector);
                if (element && await element.isVisible()) {
                    console.log(`📝 CREATE encontrado: ${selector}`);
                    
                    // Clicar e analisar
                    await element.click();
                    await this.page.waitForTimeout(2000);
                    
                    await this.screenshot(`${moduleName}-create`, 'Tela de criação');
                    
                    crud.create = await this.analyzeCurrentPage();
                    
                    // Voltar
                    try {
                        await this.page.goBack();
                    } catch (e) {
                        await this.page.keyboard.press('Escape');
                    }
                    await this.page.waitForTimeout(1000);
                    
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Explorar READ (listas, tabelas)
        const tables = await this.page.$$('table, .table, .data-table');
        const lists = await this.page.$$('.list, ul, ol');
        const cards = await this.page.$$('.card, .item');
        
        if (tables.length > 0 || lists.length > 0 || cards.length > 0) {
            console.log(`📖 READ encontrado: ${tables.length} tabelas, ${lists.length} listas, ${cards.length} cards`);
            crud.read = {
                tables: tables.length,
                lists: lists.length,
                cards: cards.length,
                hasFilters: (await this.page.$$('.filter, input[type="search"]')).length > 0,
                hasPagination: (await this.page.$$('.pagination, .page')).length > 0,
                hasSorting: (await this.page.$$('th[class*="sort"], .sortable')).length > 0
            };
        }
        
        // Explorar UPDATE
        const editSelectors = [
            'button:has-text("Editar")',
            'a:has-text("Editar")',
            '.btn-edit',
            '.edit',
            'button[title*="editar"]'
        ];
        
        for (const selector of editSelectors) {
            try {
                const element = await this.page.$(selector);
                if (element && await element.isVisible()) {
                    console.log(`✏️ UPDATE encontrado: ${selector}`);
                    crud.update = { found: true, selector };
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Explorar DELETE
        const deleteSelectors = [
            'button:has-text("Excluir")',
            'button:has-text("Remover")',
            'a:has-text("Excluir")',
            '.btn-delete',
            '.delete',
            'button[title*="excluir"], button[title*="remover"]'
        ];
        
        for (const selector of deleteSelectors) {
            try {
                const element = await this.page.$(selector);
                if (element && await element.isVisible()) {
                    console.log(`🗑️ DELETE encontrado: ${selector}`);
                    crud.delete = { found: true, selector };
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        return crud;
    }

    async generateComprehensiveReport() {
        console.log('\n📊 GERANDO RELATÓRIO COMPLETO');
        console.log('=============================');
        
        // Compilar estatísticas
        const stats = {
            loginSuccessful: this.analysis.loginSuccessful,
            screenshotsCaptured: this.analysis.screenshots.length,
            modulesAnalyzed: Object.values(this.analysis.modules).filter(m => m.analyzed).length,
            apiEndpointsFound: this.analysis.platform.apiEndpoints.length,
            networkRequestsCaptured: this.analysis.platform.networkRequests.length
        };
        
        // Gerar relatório JSON completo
        const reportPath = path.join(__dirname, 'meep-reports', 'MEEP_COMPLETE_ANALYSIS.json');
        fs.writeFileSync(reportPath, JSON.stringify(this.analysis, null, 2));
        
        // Gerar resumo executivo em Markdown
        const summaryMarkdown = this.generateExecutiveSummary(stats);
        const summaryPath = path.join(__dirname, 'meep-reports', 'MEEP_EXECUTIVE_SUMMARY.md');
        fs.writeFileSync(summaryPath, summaryMarkdown);
        
        // Gerar guia de implementação
        const implementationGuide = this.generateImplementationGuide();
        const guidePath = path.join(__dirname, 'meep-reports', 'MEEP_IMPLEMENTATION_GUIDE.md');
        fs.writeFileSync(guidePath, implementationGuide);
        
        console.log('\n✅ RELATÓRIOS GERADOS:');
        console.log(`📄 Análise completa: ${reportPath}`);
        console.log(`📄 Resumo executivo: ${summaryPath}`);
        console.log(`📄 Guia de implementação: ${guidePath}`);
        console.log(`📁 Screenshots: ./meep-screenshots/ (${stats.screenshotsCaptured} arquivos)`);
        
        return {
            stats,
            reportPath,
            summaryPath,
            guidePath
        };
    }

    generateExecutiveSummary(stats) {
        const modulesAnalyzed = Object.entries(this.analysis.modules)
            .filter(([name, data]) => data.analyzed)
            .map(([name, data]) => name);
        
        const apisByCategory = {};
        this.analysis.platform.apiEndpoints.forEach(api => {
            apisByCategory[api.category] = (apisByCategory[api.category] || 0) + 1;
        });
        
        return `# MEEP - Relatório Executivo de Engenharia Reversa

## Resumo da Análise

**Data**: ${this.analysis.timestamp}  
**Plataforma**: ${this.analysis.platform.name}  
**URL**: ${this.analysis.platform.url}  
**Status do Login**: ${stats.loginSuccessful ? '✅ Sucesso' : '❌ Falha'}

## Estatísticas Gerais

- **Screenshots Capturados**: ${stats.screenshotsCaptured}
- **Módulos Analisados**: ${stats.modulesAnalyzed} / ${Object.keys(this.analysis.modules).length}
- **Endpoints API Descobertos**: ${stats.apiEndpointsFound}
- **Requisições de Rede**: ${stats.networkRequestsCaptured}

## Módulos Descobertos

${modulesAnalyzed.length > 0 ? 
    modulesAnalyzed.map(module => {
        const moduleData = this.analysis.modules[module];
        return `### ${module.toUpperCase()}
- **Status**: ✅ Analisado
- **Funcionalidades**: ${Object.keys(moduleData.data?.specific?.features || {}).length} características identificadas
- **CRUD**: ${Object.values(moduleData.data?.crud || {}).filter(Boolean).length} operações encontradas`;
    }).join('\n\n') :
    'Nenhum módulo foi completamente analisado.'
}

## APIs Descobertas

${Object.keys(apisByCategory).length > 0 ?
    Object.entries(apisByCategory).map(([category, count]) => 
        `- **${category}**: ${count} endpoints`
    ).join('\n') :
    'Nenhuma API foi capturada.'
}

## Tecnologias Identificadas

${this.analysis.platform.technologies && Object.keys(this.analysis.platform.technologies).length > 0 ?
    Object.entries(this.analysis.platform.technologies)
        .filter(([tech, detected]) => detected)
        .map(([tech, detected]) => `- ${tech}: ${detected ? '✅' : '❌'}`)
        .join('\n') :
    'Tecnologias não detectadas.'
}

## Recomendações Imediatas

### Para o Sistema Painel Universal

1. **Autenticação CPF**: ✅ Já implementada
2. **Módulo de Eventos**: Expandir com base nos padrões MEEP
3. **Sistema de Caixa**: Implementar relatórios financeiros detalhados
4. **Lista de Convidados**: Adicionar tipos VIP/FREE/PAGANTE
5. **PDV Avançado**: Implementar categorias de produtos
6. **Check-in Inteligente**: QR codes + validação CPF

### Próximos Passos

1. **Revisar Screenshots**: Analisar capturas para padrões de UI/UX
2. **Implementar APIs**: Criar endpoints baseados nos descobertos
3. **Desenvolver Frontend**: Componentes baseados nos padrões identificados
4. **Testar Fluxos**: Validar workflows críticos

---

*Relatório gerado automaticamente pelo Sistema de Engenharia Reversa MEEP v2*
`;
    }

    generateImplementationGuide() {
        return `# MEEP - Guia de Implementação

## Estrutura de Implementação

### Backend (FastAPI)

\`\`\`python
# Expandir modelos existentes em app/models.py
class Evento(Base):
    # Adicionar campos baseados na análise MEEP
    tipo_evento = Column(Enum(TipoEvento))
    status_financeiro = Column(String)
    caixa_ativo = Column(Boolean)
    
class EventoCaixa(Base):
    # Sistema financeiro detalhado
    transacoes = relationship("TransacaoEvento")
    relatorios = relationship("RelatorioFinanceiro")
\`\`\`

### Frontend (React + TypeScript)

\`\`\`tsx
// Componentes baseados na análise
const EventosModule = () => {
    // Implementar baseado nos padrões descobertos
};

const EventoCaixaModule = () => {
    // Sistema financeiro
};

const ConvidadosModule = () => {
    // Lista com tipos VIP/FREE/PAGANTE
};
\`\`\`

### APIs Descobertas

${this.analysis.platform.apiEndpoints.slice(0, 10).map(api => 
    `- **${api.method}** ${api.url} (${api.category})`
).join('\n')}

## Funcionalidades por Módulo

${Object.entries(this.analysis.modules)
    .filter(([name, data]) => data.analyzed)
    .map(([name, data]) => {
        return `### ${name.toUpperCase()}

**Características Identificadas**:
${Object.entries(data.data?.specific?.features || {}).map(([feature, value]) => 
    `- ${feature}: ${typeof value === 'object' ? JSON.stringify(value) : value}`
).join('\n')}

**Operações CRUD**:
${Object.entries(data.data?.crud || {}).map(([operation, data]) => 
    `- ${operation.toUpperCase()}: ${data ? '✅ Disponível' : '❌ Não encontrado'}`
).join('\n')}
`;
    }).join('\n\n')
}

## Comandos de Implementação

\`\`\`bash
# Backend
cd paineluniversal/backend
poetry run uvicorn app.main:app --reload --port 8000

# Frontend  
cd paineluniversal/frontend
npm run dev

# Deploy
./deploy-production.sh
\`\`\`

---

*Este guia deve ser usado em conjunto com as screenshots capturadas para implementação completa.*
`;
    }

    async run() {
        try {
            await this.init();
            
            // Passo 1: Login
            const loginSuccess = await this.performLogin();
            
            // Passo 2: Análise da página principal
            console.log('📊 Analisando página principal...');
            await this.screenshot('04-main-page', 'Página principal após login');
            
            // Passo 3: Explorar módulos prioritários
            const moduleMap = {
                'eventos': ['Eventos', 'Events', 'Evento'],
                'eventoCaixa': ['Caixa', 'Financeiro', 'Financial', 'Evento Caixa'],
                'convidados': ['Convidados', 'Lista', 'Guests', 'Participantes'],
                'pdv': ['PDV', 'Vendas', 'Sales', 'Ponto de Venda'],
                'checkin': ['Check-in', 'Checkin', 'Check in', 'Entrada'],
                'relatorios': ['Relatórios', 'Reports', 'Analytics', 'Análises'],
                'mesas': ['Mesas', 'Tables', 'Mesas do Local'],
                'cashless': ['Cashless', 'Pagamentos', 'Carteira Digital'],
                'kds': ['KDS', 'Kitchen', 'Cozinha', 'Display'],
                'dashboard': ['Dashboard', 'Painel', 'Início', 'Home']
            };
            
            for (const [moduleName, searchTerms] of Object.entries(moduleMap)) {
                await this.exploreModule(moduleName, searchTerms);
            }
            
            // Passo 4: Gerar relatórios
            const reports = await this.generateComprehensiveReport();
            
            console.log('\n🎉 ENGENHARIA REVERSA CONCLUÍDA COM SUCESSO!');
            console.log('='.repeat(50));
            console.log(`📊 Status: ${loginSuccess ? 'Login Bem-Sucedido' : 'Análise Limitada'}`);
            console.log(`📸 Screenshots: ${reports.stats.screenshotsCaptured}`);
            console.log(`🔍 Módulos: ${reports.stats.modulesAnalyzed} analisados`);
            console.log(`🌐 APIs: ${reports.stats.apiEndpointsFound} descobertas`);
            console.log(`📝 Relatórios: 3 arquivos gerados`);
            
        } catch (error) {
            console.error('❌ ERRO CRÍTICO:', error);
            await this.screenshot('error-critical', 'Erro crítico durante análise');
        } finally {
            if (this.browser) {
                await this.browser.close();
            }
        }
    }
}

// Executar análise
console.log('🚀 INICIANDO MEEP SYSTEM ANALYZER V2');
console.log('==================================\n');

const analyzer = new MEEPSystemAnalyzer();
analyzer.run().catch(console.error);