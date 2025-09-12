import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * SISTEMA COMPLETO DE ENGENHARIA REVERSA
 * Para Sistema de Eventos - Painel Universal
 * 
 * Captura TUDO:
 * - Todas as APIs e endpoints
 * - Fluxos de autenticação completos
 * - WebSockets e eventos real-time
 * - Estrutura de dados e schemas
 * - Tokens e sessões
 * - Payloads e responses
 */

class EngenhariaReversaSistemaEventos {
    constructor() {
        this.config = {
            baseUrl: 'http://localhost:5173',
            backendUrl: 'http://localhost:8000',
            railwayBackend: 'https://backend-painel-universal-production.up.railway.app',
            testCredentials: {
                cpf: '00000000000',
                senha: 'admin123'
            }
        };

        this.capturedData = {
            apis: new Map(),
            websockets: [],
            authentication: {},
            dataSchemas: new Map(),
            userFlows: [],
            errors: [],
            performanceMetrics: [],
            securityHeaders: new Map()
        };

        this.browser = null;
        this.context = null;
        this.page = null;
    }

    async inicializar() {
        console.log('🚀 ENGENHARIA REVERSA - SISTEMA DE EVENTOS');
        console.log('=' .repeat(60));
        console.log('Alvo: Painel Universal - Sistema Completo');
        console.log('=' .repeat(60) + '\n');

        // Criar diretórios
        await this.criarDiretorios();

        // Configurar browser com máxima captura
        this.browser = await chromium.launch({
            headless: false,
            devtools: true,
            args: [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--allow-insecure-localhost',
                '--ignore-certificate-errors'
            ]
        });

        // Contexto com captura completa
        this.context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 },
            recordHar: {
                path: 'reverse-engineering/sistema-eventos.har',
                mode: 'full',
                content: 'attach',
                urlFilter: '**/*'
            },
            recordVideo: {
                dir: 'reverse-engineering/videos/',
                size: { width: 1920, height: 1080 }
            },
            ignoreHTTPSErrors: true,
            extraHTTPHeaders: {
                'X-Debug-Mode': 'true'
            }
        });

        this.page = await this.context.newPage();
        
        // Configurar interceptadores avançados
        await this.configurarInterceptadoresAvancados();
        
        return this;
    }

    async criarDiretorios() {
        const dirs = [
            'reverse-engineering',
            'reverse-engineering/apis',
            'reverse-engineering/schemas',
            'reverse-engineering/flows',
            'reverse-engineering/security',
            'reverse-engineering/videos',
            'reverse-engineering/screenshots',
            'reverse-engineering/websockets',
            'reverse-engineering/postman',
            'reverse-engineering/tests'
        ];

        for (const dir of dirs) {
            await fs.mkdir(dir, { recursive: true });
        }
    }

    async configurarInterceptadoresAvancados() {
        console.log('🔧 Configurando interceptadores avançados...\n');

        // 1. INTERCEPTAR TODAS AS REQUISIÇÕES
        this.page.on('request', async request => {
            const url = request.url();
            const method = request.method();
            const headers = request.headers();
            const postData = request.postData();

            // Analisar e categorizar
            if (url.includes('/api/')) {
                const endpoint = this.extrairEndpoint(url);
                const apiData = {
                    method,
                    endpoint,
                    url,
                    headers,
                    body: postData ? this.parseBody(postData) : null,
                    timestamp: new Date().toISOString(),
                    curl: this.gerarCurlAvancado(method, url, headers, postData)
                };

                // Armazenar por categoria
                const categoria = this.categorizarAPI(endpoint);
                if (!this.capturedData.apis.has(categoria)) {
                    this.capturedData.apis.set(categoria, []);
                }
                this.capturedData.apis.get(categoria).push(apiData);

                console.log(`📤 ${method} ${endpoint} [${categoria}]`);
            }
        });

        // 2. INTERCEPTAR TODAS AS RESPOSTAS
        this.page.on('response', async response => {
            const url = response.url();
            const status = response.status();
            const headers = response.headers();

            if (url.includes('/api/')) {
                try {
                    const body = await response.json().catch(() => null);
                    
                    if (body) {
                        // Extrair schema da resposta
                        const schema = this.extrairSchema(body);
                        const endpoint = this.extrairEndpoint(url);
                        
                        this.capturedData.dataSchemas.set(endpoint, {
                            requestUrl: url,
                            responseStatus: status,
                            responseHeaders: headers,
                            responseBody: body,
                            schema: schema,
                            timestamp: new Date().toISOString()
                        });

                        // Detectar tokens e sessões
                        if (body.token || body.access_token || body.jwt) {
                            this.capturedData.authentication = {
                                ...this.capturedData.authentication,
                                token: body.token || body.access_token || body.jwt,
                                refreshToken: body.refresh_token,
                                expiresIn: body.expires_in,
                                tokenType: body.token_type || 'Bearer'
                            };
                            console.log('🔑 Token capturado!');
                        }
                    }
                } catch (e) {
                    // Não é JSON
                }

                // Capturar headers de segurança
                this.analisarHeadersSeguranca(headers, url);
            }

            // Detectar erros
            if (status >= 400) {
                this.capturedData.errors.push({
                    url,
                    status,
                    timestamp: new Date().toISOString()
                });
                console.log(`❌ Erro ${status}: ${url}`);
            }
        });

        // 3. INTERCEPTAR WEBSOCKETS
        this.page.on('websocket', ws => {
            console.log('🔌 WebSocket detectado:', ws.url());
            
            const wsData = {
                url: ws.url(),
                messages: [],
                opened: new Date().toISOString(),
                closed: null
            };

            ws.on('framereceived', ({ payload }) => {
                wsData.messages.push({
                    type: 'received',
                    payload,
                    timestamp: new Date().toISOString()
                });
                console.log('📥 WS:', payload.substring(0, 100));
            });

            ws.on('framesent', ({ payload }) => {
                wsData.messages.push({
                    type: 'sent',
                    payload,
                    timestamp: new Date().toISOString()
                });
            });

            ws.on('close', () => {
                wsData.closed = new Date().toISOString();
                this.capturedData.websockets.push(wsData);
            });
        });

        // 4. INJETAR SCRIPT DE MONITORAMENTO
        await this.page.addInitScript(() => {
            // Interceptar fetch
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                console.log('[FETCH]', args[0]);
                const response = await originalFetch(...args);
                console.log('[FETCH RESPONSE]', response.status);
                return response;
            };

            // Interceptar XMLHttpRequest
            const XHR = XMLHttpRequest.prototype;
            const originalOpen = XHR.open;
            const originalSend = XHR.send;

            XHR.open = function(method, url) {
                console.log('[XHR]', method, url);
                this._method = method;
                this._url = url;
                return originalOpen.apply(this, arguments);
            };

            XHR.send = function(data) {
                console.log('[XHR SEND]', this._method, this._url, data);
                return originalSend.apply(this, arguments);
            };

            // Monitorar localStorage
            const originalSetItem = localStorage.setItem;
            localStorage.setItem = function(key, value) {
                console.log('[STORAGE]', key, value);
                return originalSetItem.apply(this, arguments);
            };
        });

        // 5. CAPTURAR CONSOLE
        this.page.on('console', msg => {
            const text = msg.text();
            if (text.includes('[FETCH]') || text.includes('[XHR]') || text.includes('[STORAGE]')) {
                console.log('🔍', text);
            }
        });

        // 6. PERFORMANCE METRICS
        this.page.on('load', async () => {
            const metrics = await this.page.evaluate(() => {
                const perf = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                    loadComplete: perf.loadEventEnd - perf.loadEventStart,
                    domInteractive: perf.domInteractive,
                    firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime
                };
            });
            this.capturedData.performanceMetrics.push({
                url: this.page.url(),
                metrics,
                timestamp: new Date().toISOString()
            });
        });
    }

    async executarFluxoCompleto() {
        console.log('\n🎯 EXECUTANDO FLUXO COMPLETO DO SISTEMA\n');
        console.log('-' .repeat(60));

        const fluxos = [
            this.fluxoAutenticacao.bind(this),
            this.fluxoEventos.bind(this),
            this.fluxoPDV.bind(this),
            this.fluxoCheckin.bind(this),
            this.fluxoRelatorios.bind(this),
            this.fluxoWebSocket.bind(this)
        ];

        for (const fluxo of fluxos) {
            try {
                await fluxo();
            } catch (error) {
                console.error(`❌ Erro no fluxo: ${error.message}`);
            }
        }
    }

    async fluxoAutenticacao() {
        console.log('\n🔐 FLUXO: Autenticação\n');
        
        // Ir para login
        await this.page.goto(`${this.config.baseUrl}`, { waitUntil: 'networkidle' });
        await this.capturarTela('01-home');

        // Verificar se já tem formulário de login
        const loginForm = await this.page.locator('input[name="cpf"], input[placeholder*="CPF"]').first();
        
        if (await loginForm.isVisible()) {
            // Preencher login
            await this.page.fill('input[name="cpf"], input[placeholder*="CPF"]', this.config.testCredentials.cpf);
            await this.page.fill('input[type="password"]', this.config.testCredentials.senha);
            await this.capturarTela('02-login-filled');
            
            // Fazer login
            await this.page.click('button[type="submit"]');
            
            // Aguardar navegação
            await this.page.waitForLoadState('networkidle');
            await this.capturarTela('03-dashboard');
            
            // Capturar token do localStorage
            const authData = await this.page.evaluate(() => {
                return {
                    token: localStorage.getItem('token'),
                    user: localStorage.getItem('user'),
                    permissions: localStorage.getItem('permissions'),
                    allStorage: { ...localStorage }
                };
            });
            
            this.capturedData.authentication = {
                ...this.capturedData.authentication,
                ...authData
            };
            
            console.log('✅ Autenticação capturada com sucesso');
        }
    }

    async fluxoEventos() {
        console.log('\n📅 FLUXO: Gestão de Eventos\n');
        
        // Navegar para eventos
        await this.page.click('text=Eventos, a[href*="eventos"]', { timeout: 5000 }).catch(() => {});
        await this.page.waitForLoadState('networkidle');
        await this.capturarTela('eventos-lista');
        
        // Tentar criar novo evento
        const novoEventoBtn = await this.page.locator('text=Novo Evento, button:has-text("Novo")').first();
        if (await novoEventoBtn.isVisible()) {
            await novoEventoBtn.click();
            await this.capturarTela('eventos-novo');
            
            // Capturar estrutura do formulário
            const formStructure = await this.page.evaluate(() => {
                const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
                return inputs.map(input => ({
                    name: input.name,
                    type: input.type,
                    required: input.required,
                    placeholder: input.placeholder,
                    options: input.tagName === 'SELECT' ? 
                        Array.from(input.options).map(o => o.value) : null
                }));
            });
            
            this.capturedData.dataSchemas.set('evento-form', formStructure);
        }
    }

    async fluxoPDV() {
        console.log('\n💰 FLUXO: PDV (Ponto de Venda)\n');
        
        // Navegar para PDV
        await this.page.click('text=PDV, a[href*="pdv"]', { timeout: 5000 }).catch(() => {});
        await this.page.waitForLoadState('networkidle');
        await this.capturarTela('pdv-home');
        
        // Capturar estrutura do PDV
        const pdvData = await this.page.evaluate(() => {
            return {
                produtos: Array.from(document.querySelectorAll('[class*="produto"]')).length,
                categorias: Array.from(document.querySelectorAll('[class*="categoria"]')).length,
                carrinho: document.querySelector('[class*="carrinho"]') !== null
            };
        });
        
        this.capturedData.dataSchemas.set('pdv-structure', pdvData);
    }

    async fluxoCheckin() {
        console.log('\n✅ FLUXO: Check-in\n');
        
        // Navegar para Check-in
        await this.page.click('text=Check-in, a[href*="checkin"]', { timeout: 5000 }).catch(() => {});
        await this.page.waitForLoadState('networkidle');
        await this.capturarTela('checkin-home');
        
        // Verificar se tem QR scanner
        const hasQRScanner = await this.page.locator('[class*="qr"], [class*="scanner"]').count() > 0;
        const hasCPFInput = await this.page.locator('input[placeholder*="CPF"]').count() > 0;
        
        this.capturedData.dataSchemas.set('checkin-features', {
            hasQRScanner,
            hasCPFInput,
            timestamp: new Date().toISOString()
        });
    }

    async fluxoRelatorios() {
        console.log('\n📊 FLUXO: Relatórios\n');
        
        // Navegar para Relatórios
        await this.page.click('text=Relatórios, a[href*="relatorio"]', { timeout: 5000 }).catch(() => {});
        await this.page.waitForLoadState('networkidle');
        await this.capturarTela('relatorios-home');
        
        // Capturar tipos de relatórios disponíveis
        const relatorios = await this.page.evaluate(() => {
            const links = Array.from(document.querySelectorAll('a, button'));
            return links
                .filter(l => l.textContent.toLowerCase().includes('relatório'))
                .map(l => l.textContent.trim());
        });
        
        this.capturedData.dataSchemas.set('relatorios-tipos', relatorios);
    }

    async fluxoWebSocket() {
        console.log('\n🔌 FLUXO: WebSocket / Real-time\n');
        
        // Tentar acessar PDV ou Check-in que geralmente tem WebSocket
        await this.page.goto(`${this.config.baseUrl}/pdv`, { waitUntil: 'networkidle' }).catch(() => {});
        
        // Aguardar possível conexão WebSocket
        await this.page.waitForTimeout(5000);
        
        console.log(`📊 WebSockets capturados: ${this.capturedData.websockets.length}`);
    }

    async gerarDocumentacao() {
        console.log('\n📚 GERANDO DOCUMENTAÇÃO COMPLETA\n');
        console.log('-' .repeat(60));

        // 1. Gerar documentação das APIs
        const apiDoc = {
            title: 'Sistema de Eventos - API Documentation',
            version: '1.0.0',
            baseUrl: this.config.backendUrl,
            authentication: this.capturedData.authentication,
            endpoints: {}
        };

        for (const [categoria, apis] of this.capturedData.apis.entries()) {
            apiDoc.endpoints[categoria] = apis.map(api => ({
                method: api.method,
                endpoint: api.endpoint,
                headers: api.headers,
                body: api.body,
                curl: api.curl
            }));
        }

        await fs.writeFile(
            'reverse-engineering/API-DOCUMENTATION.json',
            JSON.stringify(apiDoc, null, 2)
        );

        // 2. Gerar coleção Postman
        await this.gerarPostmanCollection();

        // 3. Gerar testes automatizados
        await this.gerarTestesAutomatizados();

        // 4. Gerar relatório de segurança
        await this.gerarRelatorioSeguranca();

        // 5. Gerar mapa de fluxos
        await this.gerarMapaFluxos();

        console.log('✅ Documentação completa gerada!');
    }

    async gerarPostmanCollection() {
        const collection = {
            info: {
                name: 'Sistema de Eventos - Reverse Engineered',
                description: 'Coleção gerada automaticamente por engenharia reversa',
                schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            auth: {
                type: 'bearer',
                bearer: [{
                    key: 'token',
                    value: '{{token}}',
                    type: 'string'
                }]
            },
            item: []
        };

        for (const [categoria, apis] of this.capturedData.apis.entries()) {
            const folder = {
                name: categoria,
                item: apis.map(api => ({
                    name: `${api.method} ${api.endpoint}`,
                    request: {
                        method: api.method,
                        header: Object.entries(api.headers || {}).map(([key, value]) => ({
                            key,
                            value
                        })),
                        url: {
                            raw: api.url,
                            protocol: new URL(api.url).protocol.replace(':', ''),
                            host: new URL(api.url).hostname.split('.'),
                            path: new URL(api.url).pathname.split('/').filter(Boolean),
                            query: Array.from(new URL(api.url).searchParams.entries()).map(([key, value]) => ({
                                key,
                                value
                            }))
                        },
                        body: api.body ? {
                            mode: 'raw',
                            raw: JSON.stringify(api.body, null, 2),
                            options: {
                                raw: {
                                    language: 'json'
                                }
                            }
                        } : undefined
                    }
                }))
            };
            collection.item.push(folder);
        }

        await fs.writeFile(
            'reverse-engineering/postman/Sistema-Eventos.postman_collection.json',
            JSON.stringify(collection, null, 2)
        );

        // Environment
        const environment = {
            name: 'Sistema Eventos - Dev',
            values: [
                { key: 'baseUrl', value: this.config.backendUrl },
                { key: 'token', value: this.capturedData.authentication.token || '' },
                { key: 'cpf', value: this.config.testCredentials.cpf },
                { key: 'senha', value: this.config.testCredentials.senha }
            ]
        };

        await fs.writeFile(
            'reverse-engineering/postman/Sistema-Eventos.postman_environment.json',
            JSON.stringify(environment, null, 2)
        );
    }

    async gerarTestesAutomatizados() {
        let testCode = `import { test, expect } from '@playwright/test';

// Testes gerados automaticamente por engenharia reversa
// Sistema de Eventos - ${new Date().toISOString()}

const config = {
    baseUrl: '${this.config.baseUrl}',
    backendUrl: '${this.config.backendUrl}',
    testCredentials: {
        cpf: '${this.config.testCredentials.cpf}',
        senha: '${this.config.testCredentials.senha}'
    }
};

test.describe('Sistema de Eventos - Testes Automatizados', () => {
    let token;
    
    test.beforeAll(async ({ request }) => {
        // Fazer login e obter token
        const response = await request.post(\`\${config.backendUrl}/api/auth/login\`, {
            data: config.testCredentials
        });
        const data = await response.json();
        token = data.token;
    });
`;

        // Gerar testes para cada endpoint
        for (const [categoria, apis] of this.capturedData.apis.entries()) {
            testCode += `\n    test.describe('${categoria}', () => {\n`;
            
            for (const api of apis) {
                const testName = `${api.method} ${api.endpoint}`;
                testCode += `        test('${testName}', async ({ request }) => {\n`;
                testCode += `            const response = await request.${api.method.toLowerCase()}(\`\${config.backendUrl}${api.endpoint}\`, {\n`;
                testCode += `                headers: {\n`;
                testCode += `                    'Authorization': \`Bearer \${token}\`\n`;
                testCode += `                }`;
                
                if (api.body) {
                    testCode += `,\n                data: ${JSON.stringify(api.body, null, 20).replace(/\n/g, '\n                ')}`;
                }
                
                testCode += `\n            });\n`;
                testCode += `            expect(response.status()).toBeLessThan(400);\n`;
                testCode += `        });\n\n`;
            }
            
            testCode += `    });\n`;
        }

        testCode += `});\n`;

        await fs.writeFile(
            'reverse-engineering/tests/sistema-eventos.spec.js',
            testCode
        );
    }

    async gerarRelatorioSeguranca() {
        const relatorio = {
            timestamp: new Date().toISOString(),
            sistema: 'Painel Universal - Sistema de Eventos',
            analise: {
                headers_seguranca: Array.from(this.capturedData.securityHeaders.entries()),
                autenticacao: {
                    tipo: 'JWT',
                    token_presente: !!this.capturedData.authentication.token,
                    refresh_token: !!this.capturedData.authentication.refreshToken,
                    expiracao: this.capturedData.authentication.expiresIn
                },
                endpoints_publicos: [],
                endpoints_protegidos: [],
                vulnerabilidades_potenciais: [],
                recomendacoes: []
            }
        };

        // Analisar endpoints
        for (const [categoria, apis] of this.capturedData.apis.entries()) {
            for (const api of apis) {
                const needsAuth = api.headers?.authorization || api.headers?.Authorization;
                if (needsAuth) {
                    relatorio.analise.endpoints_protegidos.push(api.endpoint);
                } else {
                    relatorio.analise.endpoints_publicos.push(api.endpoint);
                }
            }
        }

        // Verificar vulnerabilidades comuns
        if (!this.capturedData.securityHeaders.has('x-frame-options')) {
            relatorio.analise.vulnerabilidades_potenciais.push('Falta header X-Frame-Options (Clickjacking)');
        }
        if (!this.capturedData.securityHeaders.has('content-security-policy')) {
            relatorio.analise.vulnerabilidades_potenciais.push('Falta Content-Security-Policy');
        }
        if (!this.capturedData.securityHeaders.has('strict-transport-security')) {
            relatorio.analise.vulnerabilidades_potenciais.push('Falta Strict-Transport-Security (HSTS)');
        }

        await fs.writeFile(
            'reverse-engineering/security/SECURITY-REPORT.json',
            JSON.stringify(relatorio, null, 2)
        );
    }

    async gerarMapaFluxos() {
        const mapa = {
            titulo: 'Mapa de Fluxos - Sistema de Eventos',
            timestamp: new Date().toISOString(),
            fluxos: [
                {
                    nome: 'Autenticação',
                    passos: [
                        'Acessar página inicial',
                        'Preencher CPF e senha',
                        'Submeter formulário',
                        'Receber token JWT',
                        'Armazenar em localStorage',
                        'Redirecionar para dashboard'
                    ]
                },
                {
                    nome: 'Criar Evento',
                    passos: [
                        'Navegar para /eventos',
                        'Clicar em Novo Evento',
                        'Preencher formulário',
                        'POST /api/eventos',
                        'Receber ID do evento',
                        'Redirecionar para detalhes'
                    ]
                },
                {
                    nome: 'PDV - Venda',
                    passos: [
                        'Selecionar evento',
                        'Adicionar produtos ao carrinho',
                        'Escolher forma de pagamento',
                        'POST /api/pdv/venda',
                        'Atualizar estoque via WebSocket',
                        'Gerar recibo'
                    ]
                },
                {
                    nome: 'Check-in',
                    passos: [
                        'Selecionar evento',
                        'Escanear QR ou digitar CPF',
                        'POST /api/checkin',
                        'Atualizar contador em tempo real',
                        'Mostrar confirmação'
                    ]
                }
            ],
            websockets: this.capturedData.websockets.map(ws => ({
                url: ws.url,
                proposito: this.identificarPropositoWebSocket(ws.url),
                mensagens: ws.messages.length
            }))
        };

        await fs.writeFile(
            'reverse-engineering/flows/FLUXOS-MAPEADOS.json',
            JSON.stringify(mapa, null, 2)
        );

        // Gerar diagrama Mermaid
        let mermaid = 'graph TD\n';
        mermaid += '    A[Início] --> B[Login]\n';
        mermaid += '    B --> C{Autenticado?}\n';
        mermaid += '    C -->|Sim| D[Dashboard]\n';
        mermaid += '    C -->|Não| B\n';
        mermaid += '    D --> E[Eventos]\n';
        mermaid += '    D --> F[PDV]\n';
        mermaid += '    D --> G[Check-in]\n';
        mermaid += '    D --> H[Relatórios]\n';
        mermaid += '    E --> I[Criar Evento]\n';
        mermaid += '    F --> J[Realizar Venda]\n';
        mermaid += '    G --> K[Fazer Check-in]\n';
        mermaid += '    H --> L[Gerar Relatório]\n';

        await fs.writeFile(
            'reverse-engineering/flows/diagrama.mermaid',
            mermaid
        );
    }

    // Métodos auxiliares
    extrairEndpoint(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.pathname;
        } catch {
            return url;
        }
    }

    categorizarAPI(endpoint) {
        if (endpoint.includes('auth')) return 'Autenticação';
        if (endpoint.includes('evento')) return 'Eventos';
        if (endpoint.includes('pdv')) return 'PDV';
        if (endpoint.includes('checkin')) return 'Check-in';
        if (endpoint.includes('relatorio')) return 'Relatórios';
        if (endpoint.includes('usuario')) return 'Usuários';
        if (endpoint.includes('produto')) return 'Produtos';
        if (endpoint.includes('estoque')) return 'Estoque';
        return 'Outros';
    }

    parseBody(data) {
        try {
            return JSON.parse(data);
        } catch {
            return data;
        }
    }

    extrairSchema(obj) {
        const schema = {};
        for (const [key, value] of Object.entries(obj)) {
            if (value === null) {
                schema[key] = 'null';
            } else if (Array.isArray(value)) {
                schema[key] = value.length > 0 ? 
                    `array<${typeof value[0]}>` : 'array';
            } else if (typeof value === 'object') {
                schema[key] = this.extrairSchema(value);
            } else {
                schema[key] = typeof value;
            }
        }
        return schema;
    }

    gerarCurlAvancado(method, url, headers, postData) {
        let curl = `curl -X ${method} '${url}'`;
        
        for (const [key, value] of Object.entries(headers)) {
            if (!key.startsWith(':') && key.toLowerCase() !== 'content-length') {
                curl += ` \\\n  -H '${key}: ${value}'`;
            }
        }
        
        if (postData) {
            curl += ` \\\n  --data '${postData}'`;
        }
        
        curl += ` \\\n  --compressed`;
        curl += ` \\\n  --insecure`;
        curl += ` \\\n  -w '\\n%{http_code}'`;
        
        return curl;
    }

    analisarHeadersSeguranca(headers, url) {
        const securityHeaders = [
            'x-frame-options',
            'x-content-type-options',
            'x-xss-protection',
            'strict-transport-security',
            'content-security-policy',
            'referrer-policy'
        ];

        for (const header of securityHeaders) {
            if (headers[header]) {
                this.capturedData.securityHeaders.set(header, headers[header]);
            }
        }
    }

    identificarPropositoWebSocket(url) {
        if (url.includes('pdv')) return 'PDV Real-time';
        if (url.includes('checkin')) return 'Check-in Real-time';
        if (url.includes('chat')) return 'Chat';
        if (url.includes('notification')) return 'Notificações';
        return 'Desconhecido';
    }

    async capturarTela(nome) {
        await this.page.screenshot({
            path: `reverse-engineering/screenshots/${nome}.png`,
            fullPage: false
        });
    }

    async finalizar() {
        console.log('\n📊 GERANDO RELATÓRIO FINAL\n');
        console.log('=' .repeat(60));

        // Fechar contexto para salvar HAR
        await this.context.close();

        const relatorioFinal = {
            sistema: 'Painel Universal - Sistema de Eventos',
            timestamp: new Date().toISOString(),
            duracao: Date.now() - this.startTime,
            estatisticas: {
                total_apis_capturadas: Array.from(this.capturedData.apis.values()).flat().length,
                categorias_mapeadas: this.capturedData.apis.size,
                websockets_detectados: this.capturedData.websockets.length,
                schemas_extraidos: this.capturedData.dataSchemas.size,
                erros_capturados: this.capturedData.errors.length,
                headers_seguranca: this.capturedData.securityHeaders.size
            },
            arquivos_gerados: [
                'API-DOCUMENTATION.json',
                'Sistema-Eventos.postman_collection.json',
                'Sistema-Eventos.postman_environment.json',
                'sistema-eventos.spec.js',
                'SECURITY-REPORT.json',
                'FLUXOS-MAPEADOS.json',
                'diagrama.mermaid',
                'sistema-eventos.har'
            ],
            proximos_passos: [
                '1. Importar coleção no Postman',
                '2. Executar testes automatizados',
                '3. Revisar relatório de segurança',
                '4. Implementar melhorias identificadas',
                '5. Completar endpoints faltantes'
            ]
        };

        await fs.writeFile(
            'reverse-engineering/RELATORIO-FINAL.json',
            JSON.stringify(relatorioFinal, null, 2)
        );

        // Exibir resumo
        console.log('🎯 ENGENHARIA REVERSA COMPLETA!\n');
        console.log(`✅ APIs Capturadas: ${relatorioFinal.estatisticas.total_apis_capturadas}`);
        console.log(`✅ Categorias: ${relatorioFinal.estatisticas.categorias_mapeadas}`);
        console.log(`✅ WebSockets: ${relatorioFinal.estatisticas.websockets_detectados}`);
        console.log(`✅ Schemas: ${relatorioFinal.estatisticas.schemas_extraidos}`);
        console.log(`✅ Headers de Segurança: ${relatorioFinal.estatisticas.headers_seguranca}`);
        console.log('\n📁 Arquivos gerados em: reverse-engineering/');
        console.log('\n🚀 Próximos passos:');
        relatorioFinal.proximos_passos.forEach(passo => console.log(`   ${passo}`));

        if (this.browser) {
            await this.browser.close();
        }
    }
}

// Executar engenharia reversa completa
async function executar() {
    const engenharia = new EngenhariaReversaSistemaEventos();
    engenharia.startTime = Date.now();
    
    try {
        await engenharia.inicializar();
        await engenharia.executarFluxoCompleto();
        await engenharia.gerarDocumentacao();
    } catch (error) {
        console.error('❌ Erro fatal:', error);
    } finally {
        await engenharia.finalizar();
    }
}

console.log('🔧 ENGENHARIA REVERSA - SISTEMA DE EVENTOS');
console.log('🎯 Objetivo: Capturar TUDO para completar o sistema\n');
executar().catch(console.error);