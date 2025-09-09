const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

class MEEPAnalyzer {
    constructor() {
        this.baseUrl = 'https://beta.portal.meep.com.br';
        this.credentials = {
            email: 'toretomal@icloud.com',
            password: '10041210Cl@'
        };
        this.analysisData = {
            timestamp: new Date().toISOString(),
            modules: {},
            dataStructures: {},
            workflows: {},
            apis: [],
            integrations: [],
            permissions: {}
        };
    }

    async initialize() {
        console.log('🚀 Iniciando análise do sistema MEEP...');
        this.browser = await puppeteer.launch({
            headless: false,
            defaultViewport: null,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        });
        this.page = await this.browser.newPage();
        
        // Interceptar requisições de rede
        await this.page.setRequestInterception(true);
        
        this.page.on('request', request => {
            const url = request.url();
            if (url.includes('/api/') || url.includes('/v1/') || url.includes('/v2/')) {
                this.captureAPIEndpoint(request);
            }
            request.continue();
        });

        this.page.on('response', response => {
            const url = response.url();
            if (url.includes('/api/') || url.includes('/v1/') || url.includes('/v2/')) {
                this.captureAPIResponse(response);
            }
        });

        await this.page.goto(this.baseUrl, { waitUntil: 'networkidle2' });
    }

    captureAPIEndpoint(request) {
        const endpoint = {
            url: request.url(),
            method: request.method(),
            headers: request.headers(),
            postData: request.postData(),
            timestamp: new Date().toISOString()
        };
        
        if (!this.analysisData.apis.find(api => api.url === endpoint.url && api.method === endpoint.method)) {
            this.analysisData.apis.push(endpoint);
            console.log(`📡 API capturada: ${endpoint.method} ${endpoint.url}`);
        }
    }

    async captureAPIResponse(response) {
        try {
            const url = response.url();
            const status = response.status();
            
            if (status === 200) {
                const contentType = response.headers()['content-type'];
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json().catch(() => null);
                    if (data) {
                        this.analyzeDataStructure(url, data);
                    }
                }
            }
        } catch (error) {
            // Silently handle errors
        }
    }

    analyzeDataStructure(url, data) {
        const endpoint = url.replace(this.baseUrl, '');
        const structure = this.extractStructure(data);
        
        if (!this.analysisData.dataStructures[endpoint]) {
            this.analysisData.dataStructures[endpoint] = structure;
            console.log(`📊 Estrutura de dados capturada: ${endpoint}`);
        }
    }

    extractStructure(obj, depth = 0) {
        if (depth > 5) return 'object';
        
        if (Array.isArray(obj)) {
            if (obj.length > 0) {
                return [this.extractStructure(obj[0], depth + 1)];
            }
            return [];
        }
        
        if (obj && typeof obj === 'object') {
            const structure = {};
            for (const key in obj) {
                const value = obj[key];
                structure[key] = typeof value === 'object' ? 
                    this.extractStructure(value, depth + 1) : 
                    typeof value;
            }
            return structure;
        }
        
        return typeof obj;
    }

    async login() {
        console.log('🔐 Realizando login...');
        
        try {
            // Aguardar o formulário de login carregar
            await this.page.waitForSelector('input[type="email"], input[type="text"], input[name="email"], input[name="username"]', { timeout: 10000 });
            
            // Identificar campos de login
            const emailField = await this.page.$('input[type="email"], input[type="text"], input[name="email"], input[name="username"], input[placeholder*="mail"], input[placeholder*="usuário"]');
            const passwordField = await this.page.$('input[type="password"], input[name="password"], input[name="senha"], input[placeholder*="senha"], input[placeholder*="password"]');
            
            if (emailField && passwordField) {
                await emailField.type(this.credentials.email, { delay: 50 });
                await passwordField.type(this.credentials.password, { delay: 50 });
                
                // Procurar botão de submit
                const submitButton = await this.page.$('button[type="submit"], input[type="submit"], button:has-text("Entrar"), button:has-text("Login"), button:has-text("Acessar")');
                
                if (submitButton) {
                    await Promise.all([
                        this.page.waitForNavigation({ waitUntil: 'networkidle2' }),
                        submitButton.click()
                    ]);
                    
                    console.log('✅ Login realizado com sucesso!');
                    await this.page.waitForTimeout(3000);
                    return true;
                }
            }
            
            console.log('❌ Não foi possível identificar os campos de login');
            return false;
        } catch (error) {
            console.error('❌ Erro no login:', error.message);
            return false;
        }
    }

    async analyzeModule(moduleName, selector) {
        console.log(`\n📦 Analisando módulo: ${moduleName}`);
        
        try {
            const moduleData = {
                name: moduleName,
                timestamp: new Date().toISOString(),
                elements: [],
                forms: [],
                tables: [],
                buttons: [],
                links: []
            };

            // Navegar para o módulo se houver selector
            if (selector) {
                const element = await this.page.$(selector);
                if (element) {
                    await element.click();
                    await this.page.waitForTimeout(2000);
                }
            }

            // Capturar elementos da página
            moduleData.elements = await this.page.evaluate(() => {
                const elements = [];
                
                // Inputs
                document.querySelectorAll('input, textarea, select').forEach(el => {
                    elements.push({
                        type: 'input',
                        tag: el.tagName.toLowerCase(),
                        name: el.name || el.id,
                        inputType: el.type,
                        placeholder: el.placeholder,
                        required: el.required,
                        pattern: el.pattern,
                        maxLength: el.maxLength
                    });
                });
                
                // Buttons
                document.querySelectorAll('button, a.btn, input[type="submit"]').forEach(el => {
                    elements.push({
                        type: 'button',
                        text: el.textContent.trim(),
                        href: el.href,
                        onclick: el.onclick ? 'has-handler' : null
                    });
                });
                
                // Tables
                document.querySelectorAll('table').forEach(table => {
                    const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
                    elements.push({
                        type: 'table',
                        headers: headers,
                        rowCount: table.querySelectorAll('tbody tr').length
                    });
                });
                
                return elements;
            });

            this.analysisData.modules[moduleName] = moduleData;
            console.log(`✅ Módulo ${moduleName} analisado: ${moduleData.elements.length} elementos encontrados`);
            
        } catch (error) {
            console.error(`❌ Erro ao analisar módulo ${moduleName}:`, error.message);
        }
    }

    async analyzeAllModules() {
        const modules = [
            { name: 'Dashboard', selector: 'a[href*="dashboard"], nav a:has-text("Dashboard"), button:has-text("Dashboard")' },
            { name: 'Eventos/Caixa', selector: 'a[href*="evento"], a[href*="caixa"], nav a:has-text("Evento"), nav a:has-text("Caixa")' },
            { name: 'Clientes', selector: 'a[href*="cliente"], nav a:has-text("Cliente"), nav a:has-text("Informações")' },
            { name: 'Equipe', selector: 'a[href*="equipe"], a[href*="colaborador"], nav a:has-text("Equipe")' },
            { name: 'Cardápio', selector: 'a[href*="cardapio"], a[href*="produto"], nav a:has-text("Cardápio")' },
            { name: 'Vendas', selector: 'a[href*="venda"], nav a:has-text("Venda"), nav a:has-text("Gestão de venda")' },
            { name: 'Soluções Online', selector: 'a[href*="online"], a[href*="ingresso"], nav a:has-text("Soluções Online")' },
            { name: 'Relatórios', selector: 'a[href*="relatorio"], nav a:has-text("Relatório")' },
            { name: 'Estoque', selector: 'a[href*="estoque"], nav a:has-text("Estoque"), nav a:has-text("Gestão de estoque")' },
            { name: 'PDV', selector: 'a[href*="pdv"], nav a:has-text("PDV"), nav a:has-text("Ponto de Venda")' },
            { name: 'Equipamentos', selector: 'a[href*="equipamento"], a[href*="impressora"], nav a:has-text("Equipamento")' },
            { name: 'Pedidos', selector: 'a[href*="pedido"], nav a:has-text("Pedido"), nav a:has-text("Gestor de pedidos")' },
            { name: 'Financeiro', selector: 'a[href*="financeiro"], nav a:has-text("Financeiro")' },
            { name: 'Pagamentos', selector: 'a[href*="pagamento"], nav a:has-text("Pagamento")' },
            { name: 'Split', selector: 'a[href*="split"], nav a:has-text("Split")' },
            { name: 'Mapa Operação', selector: 'a[href*="mapa"], nav a:has-text("Mapa")' },
            { name: 'Mesas/Comandas', selector: 'a[href*="mesa"], a[href*="comanda"], nav a:has-text("Mesa")' },
            { name: 'Cartões', selector: 'a[href*="cartao"], nav a:has-text("Cartão"), nav a:has-text("Pré-ativação")' },
            { name: 'Marketing', selector: 'a[href*="marketing"], a[href*="fidelidade"], nav a:has-text("Marketing")' },
            { name: 'Cupons', selector: 'a[href*="cupom"], a[href*="desconto"], nav a:has-text("Cupom")' },
            { name: 'BI', selector: 'a[href*="bi"], a[href*="analytics"], nav a:has-text("BI"), nav a:has-text("Business Intelligence")' },
            { name: 'ERP', selector: 'a[href*="erp"], nav a:has-text("ERP")' },
            { name: 'Automações', selector: 'a[href*="automacao"], a[href*="integracao"], nav a:has-text("Automação")' }
        ];

        for (const module of modules) {
            await this.analyzeModule(module.name, module.selector);
            await this.page.waitForTimeout(1000);
        }
    }

    async captureMenuStructure() {
        console.log('\n🗂️ Capturando estrutura do menu...');
        
        const menuStructure = await this.page.evaluate(() => {
            const menus = [];
            
            // Procurar por diferentes tipos de menu
            const menuSelectors = [
                'nav ul li',
                '.sidebar ul li',
                '.menu ul li',
                '[role="navigation"] a',
                '.nav-menu a'
            ];
            
            menuSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(item => {
                    const text = item.textContent.trim();
                    const href = item.querySelector('a')?.href || item.href;
                    if (text && !menus.find(m => m.text === text)) {
                        menus.push({ text, href });
                    }
                });
            });
            
            return menus;
        });
        
        this.analysisData.menuStructure = menuStructure;
        console.log(`✅ Estrutura do menu capturada: ${menuStructure.length} itens`);
    }

    async captureScreenshot(name) {
        const screenshotPath = path.join(__dirname, 'screenshots', `${name}_${Date.now()}.png`);
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`📸 Screenshot salva: ${screenshotPath}`);
    }

    async saveAnalysis() {
        const outputPath = path.join(__dirname, `meep_analysis_${Date.now()}.json`);
        await fs.writeFile(outputPath, JSON.stringify(this.analysisData, null, 2));
        console.log(`\n💾 Análise salva em: ${outputPath}`);
        
        // Gerar relatório markdown
        const report = this.generateMarkdownReport();
        const reportPath = path.join(__dirname, `MEEP_REVERSE_ENGINEERING.md`);
        await fs.writeFile(reportPath, report);
        console.log(`📄 Relatório gerado: ${reportPath}`);
    }

    generateMarkdownReport() {
        let report = `# MEEP - Engenharia Reversa Completa
        
## 📅 Data da Análise: ${this.analysisData.timestamp}

## 🌐 URL Base: ${this.baseUrl}

## 📊 Resumo da Análise

- **Módulos Analisados**: ${Object.keys(this.analysisData.modules).length}
- **APIs Capturadas**: ${this.analysisData.apis.length}
- **Estruturas de Dados**: ${Object.keys(this.analysisData.dataStructures).length}

---

## 🗂️ Estrutura de Módulos

`;

        // Módulos
        Object.entries(this.analysisData.modules).forEach(([name, data]) => {
            report += `\n### 📦 ${name}\n\n`;
            report += `**Elementos Capturados**: ${data.elements.length}\n\n`;
            
            // Inputs
            const inputs = data.elements.filter(e => e.type === 'input');
            if (inputs.length > 0) {
                report += `#### Campos de Entrada\n\n`;
                inputs.forEach(input => {
                    report += `- **${input.name || 'unnamed'}**: ${input.inputType} ${input.required ? '(obrigatório)' : ''}\n`;
                    if (input.placeholder) report += `  - Placeholder: "${input.placeholder}"\n`;
                    if (input.pattern) report += `  - Pattern: \`${input.pattern}\`\n`;
                });
                report += '\n';
            }
            
            // Tables
            const tables = data.elements.filter(e => e.type === 'table');
            if (tables.length > 0) {
                report += `#### Tabelas\n\n`;
                tables.forEach(table => {
                    report += `- **Colunas**: ${table.headers.join(', ')}\n`;
                    report += `  - Linhas: ${table.rowCount}\n`;
                });
                report += '\n';
            }
        });

        // APIs
        if (this.analysisData.apis.length > 0) {
            report += `\n## 🔌 APIs e Endpoints\n\n`;
            
            const groupedApis = {};
            this.analysisData.apis.forEach(api => {
                const path = new URL(api.url).pathname;
                const base = path.split('/').slice(0, 3).join('/');
                if (!groupedApis[base]) groupedApis[base] = [];
                groupedApis[base].push(api);
            });
            
            Object.entries(groupedApis).forEach(([base, apis]) => {
                report += `### ${base}\n\n`;
                apis.forEach(api => {
                    const path = new URL(api.url).pathname;
                    report += `- **${api.method}** \`${path}\`\n`;
                });
                report += '\n';
            });
        }

        // Estruturas de Dados
        if (Object.keys(this.analysisData.dataStructures).length > 0) {
            report += `\n## 📋 Estruturas de Dados\n\n`;
            
            Object.entries(this.analysisData.dataStructures).forEach(([endpoint, structure]) => {
                report += `### ${endpoint}\n\n\`\`\`json\n${JSON.stringify(structure, null, 2)}\n\`\`\`\n\n`;
            });
        }

        return report;
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async run() {
        try {
            await this.initialize();
            
            const loggedIn = await this.login();
            
            if (loggedIn) {
                await this.captureScreenshot('dashboard');
                await this.captureMenuStructure();
                await this.analyzeAllModules();
            }
            
            await this.saveAnalysis();
            
        } catch (error) {
            console.error('❌ Erro durante análise:', error);
        } finally {
            await this.close();
        }
    }
}

// Executar análise
(async () => {
    const analyzer = new MEEPAnalyzer();
    await analyzer.run();
})();