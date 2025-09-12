import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * MEEP ULTIMATE CAPTURE - MISSÃO TOTAL
 * Captura ABSOLUTAMENTE TUDO sem parar
 */

class MEEPUltimateCapture {
    constructor() {
        this.config = {
            portalUrl: 'https://beta.portal.meep.com.br/',
            apiUrl: 'https://api.meep.com.br',
            credentials: {
                email: 'toretomal@icloud.com',
                password: '10041210Cl@'
            },
            maxRetries: 10,
            captureEverything: true
        };

        this.capturedData = {
            totalRequests: 0,
            apis: new Map(),
            cookies: [],
            localStorage: {},
            sessionStorage: {},
            tokens: [],
            websockets: [],
            forms: [],
            buttons: [],
            links: [],
            images: [],
            scripts: [],
            styles: [],
            iframes: [],
            videos: [],
            audios: [],
            canvas: [],
            webgl: [],
            workers: [],
            manifests: [],
            performance: [],
            errors: [],
            console: [],
            navigation: [],
            screenshots: [],
            har: null
        };

        this.curlCommands = [];
        this.postmanRequests = [];
    }

    async iniciar() {
        console.log('🔥 MEEP ULTIMATE CAPTURE - MISSÃO TOTAL');
        console.log('=' .repeat(80));
        console.log('Objetivo: Capturar ABSOLUTAMENTE TUDO');
        console.log('Modo: NON-STOP - Sem interrupções');
        console.log('=' .repeat(80) + '\n');

        await this.criarEstrutura();

        this.browser = await chromium.launch({
            headless: false,
            devtools: true,
            args: [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--allow-insecure-localhost',
                '--ignore-certificate-errors',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        });

        this.context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 },
            recordHar: {
                path: 'meep-ultimate/capture.har',
                mode: 'full',
                content: 'attach',
                urlFilter: '**/*'
            },
            recordVideo: {
                dir: 'meep-ultimate/videos/',
                size: { width: 1920, height: 1080 }
            },
            ignoreHTTPSErrors: true,
            locale: 'pt-BR',
            timezoneId: 'America/Sao_Paulo',
            permissions: ['geolocation', 'notifications', 'camera', 'microphone', 'clipboard-read', 'clipboard-write'],
            colorScheme: 'light',
            reducedMotion: 'no-preference',
            forcedColors: 'none',
            extraHTTPHeaders: {
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });

        // Criar múltiplas páginas para captura paralela
        this.pages = {
            main: await this.context.newPage(),
            api: await this.context.newPage(),
            monitor: await this.context.newPage()
        };

        await this.configurarCapturaTotal();
        await this.executarMissaoTotal();
    }

    async criarEstrutura() {
        const dirs = [
            'meep-ultimate',
            'meep-ultimate/apis',
            'meep-ultimate/screenshots',
            'meep-ultimate/videos',
            'meep-ultimate/har',
            'meep-ultimate/postman',
            'meep-ultimate/curl',
            'meep-ultimate/data',
            'meep-ultimate/analysis',
            'meep-ultimate/integration',
            'meep-ultimate/documentation'
        ];

        for (const dir of dirs) {
            await fs.mkdir(dir, { recursive: true });
        }
    }

    async configurarCapturaTotal() {
        console.log('🔧 Configurando captura TOTAL...\n');

        // Configurar interceptadores em TODAS as páginas
        for (const [name, page] of Object.entries(this.pages)) {
            console.log(`  Configurando página: ${name}`);

            // Interceptar TODAS as requisições
            page.on('request', request => {
                this.capturedData.totalRequests++;
                const url = request.url();
                const method = request.method();
                const headers = request.headers();
                const postData = request.postData();

                // Gerar cURL para TUDO
                const curl = this.gerarCurlCompleto(method, url, headers, postData);
                this.curlCommands.push(curl);

                // Categorizar e armazenar
                const categoria = this.categorizar(url);
                if (!this.capturedData.apis.has(categoria)) {
                    this.capturedData.apis.set(categoria, []);
                }

                this.capturedData.apis.get(categoria).push({
                    timestamp: Date.now(),
                    method,
                    url,
                    headers,
                    body: postData,
                    curl
                });

                console.log(`  [${name}] ${method} ${url.substring(0, 60)}...`);
            });

            // Interceptar TODAS as respostas
            page.on('response', async response => {
                const url = response.url();
                const status = response.status();
                
                try {
                    const body = await response.body();
                    const headers = response.headers();
                    
                    // Tentar parse como JSON
                    try {
                        const json = JSON.parse(body.toString());
                        
                        // Procurar tokens em qualquer lugar
                        this.extrairTokens(json);
                        
                        // Salvar resposta
                        const filename = `meep-ultimate/data/response-${Date.now()}.json`;
                        await fs.writeFile(filename, JSON.stringify({
                            url,
                            status,
                            headers,
                            body: json
                        }, null, 2));
                    } catch {}
                } catch {}

                if (status >= 400) {
                    this.capturedData.errors.push({
                        url,
                        status,
                        timestamp: Date.now()
                    });
                }
            });

            // WebSockets
            page.on('websocket', ws => {
                console.log(`  [${name}] WebSocket: ${ws.url()}`);
                
                const wsData = {
                    url: ws.url(),
                    messages: [],
                    opened: Date.now()
                };

                ws.on('framereceived', ({ payload }) => {
                    wsData.messages.push({
                        type: 'received',
                        payload,
                        timestamp: Date.now()
                    });
                });

                ws.on('framesent', ({ payload }) => {
                    wsData.messages.push({
                        type: 'sent',
                        payload,
                        timestamp: Date.now()
                    });
                });

                ws.on('close', () => {
                    wsData.closed = Date.now();
                    this.capturedData.websockets.push(wsData);
                });
            });

            // Console
            page.on('console', msg => {
                this.capturedData.console.push({
                    type: msg.type(),
                    text: msg.text(),
                    timestamp: Date.now()
                });
            });

            // Erros
            page.on('pageerror', error => {
                this.capturedData.errors.push({
                    message: error.message,
                    stack: error.stack,
                    timestamp: Date.now()
                });
            });

            // Downloads
            page.on('download', async download => {
                const path = await download.path();
                console.log(`  [${name}] Download: ${path}`);
            });

            // Diálogos
            page.on('dialog', async dialog => {
                console.log(`  [${name}] Dialog: ${dialog.message()}`);
                await dialog.accept();
            });

            // Workers
            page.on('worker', worker => {
                console.log(`  [${name}] Worker: ${worker.url()}`);
                this.capturedData.workers.push({
                    url: worker.url(),
                    timestamp: Date.now()
                });
            });

            // Injetar super monitor
            await page.addInitScript(() => {
                // Capturar TUDO no browser
                window.__MEEP_CAPTURE__ = {
                    requests: [],
                    responses: [],
                    events: [],
                    storage: {},
                    performance: []
                };

                // Override fetch
                const originalFetch = window.fetch;
                window.fetch = async function(...args) {
                    window.__MEEP_CAPTURE__.requests.push({
                        type: 'fetch',
                        args,
                        timestamp: Date.now()
                    });
                    
                    const response = await originalFetch.apply(this, args);
                    const cloned = response.clone();
                    
                    try {
                        const data = await cloned.json();
                        window.__MEEP_CAPTURE__.responses.push({
                            url: args[0],
                            data,
                            timestamp: Date.now()
                        });
                    } catch {}
                    
                    return response;
                };

                // Override XMLHttpRequest
                const XHR = XMLHttpRequest.prototype;
                const originalOpen = XHR.open;
                const originalSend = XHR.send;
                
                XHR.open = function(method, url) {
                    this._method = method;
                    this._url = url;
                    window.__MEEP_CAPTURE__.requests.push({
                        type: 'xhr',
                        method,
                        url,
                        timestamp: Date.now()
                    });
                    return originalOpen.apply(this, arguments);
                };
                
                XHR.send = function(data) {
                    window.__MEEP_CAPTURE__.requests.push({
                        type: 'xhr-send',
                        data,
                        timestamp: Date.now()
                    });
                    return originalSend.apply(this, arguments);
                };

                // Capturar todos os eventos
                const events = ['click', 'submit', 'change', 'input', 'focus', 'blur', 'load', 'error'];
                events.forEach(eventType => {
                    document.addEventListener(eventType, (e) => {
                        window.__MEEP_CAPTURE__.events.push({
                            type: eventType,
                            target: e.target?.tagName,
                            timestamp: Date.now()
                        });
                    }, true);
                });

                // Monitor de performance
                if (window.PerformanceObserver) {
                    const observer = new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            window.__MEEP_CAPTURE__.performance.push({
                                name: entry.name,
                                type: entry.entryType,
                                duration: entry.duration,
                                timestamp: Date.now()
                            });
                        }
                    });
                    observer.observe({ entryTypes: ['navigation', 'resource', 'paint', 'measure'] });
                }

                // Capturar localStorage e sessionStorage
                setInterval(() => {
                    window.__MEEP_CAPTURE__.storage = {
                        local: { ...localStorage },
                        session: { ...sessionStorage },
                        cookies: document.cookie
                    };
                }, 1000);

                console.log('[MEEP] Super monitor ativado!');
            });
        }
    }

    async executarMissaoTotal() {
        console.log('\n🚀 EXECUTANDO MISSÃO TOTAL - NON-STOP\n');
        console.log('-' .repeat(80));

        const tarefas = [];

        // Tarefa 1: Login e navegação principal
        tarefas.push(this.tarefaPrincipal());

        // Tarefa 2: Scanner de APIs
        tarefas.push(this.tarefaScannerAPIs());

        // Tarefa 3: Monitor contínuo
        tarefas.push(this.tarefaMonitorContinuo());

        // Executar todas em paralelo
        await Promise.all(tarefas);
    }

    async tarefaPrincipal() {
        const page = this.pages.main;
        
        console.log('\n📱 TAREFA PRINCIPAL: Login e exploração\n');

        // Login
        await page.goto(this.config.portalUrl, { waitUntil: 'networkidle' });
        await this.screenshot(page, 'main-01-home');

        // Tentar todos os seletores possíveis para login
        const emailSelectors = [
            'input[type="email"]',
            'input[name="email"]',
            'input[name="username"]',
            'input[name="user"]',
            'input[placeholder*="email" i]',
            'input[placeholder*="e-mail" i]',
            'input[placeholder*="usuário" i]',
            '#email',
            '#username',
            '#user',
            '.email-input',
            '.username-input'
        ];

        const passwordSelectors = [
            'input[type="password"]',
            'input[name="password"]',
            'input[name="senha"]',
            'input[placeholder*="senha" i]',
            'input[placeholder*="password" i]',
            '#password',
            '#senha',
            '.password-input'
        ];

        // Preencher email
        let emailPreenchido = false;
        for (const selector of emailSelectors) {
            try {
                const element = page.locator(selector).first();
                if (await element.isVisible({ timeout: 1000 })) {
                    await element.fill(this.config.credentials.email);
                    console.log(`  ✅ Email preenchido: ${selector}`);
                    emailPreenchido = true;
                    break;
                }
            } catch {}
        }

        // Preencher senha
        let senhaPreenchida = false;
        for (const selector of passwordSelectors) {
            try {
                const element = page.locator(selector).first();
                if (await element.isVisible({ timeout: 1000 })) {
                    await element.fill(this.config.credentials.password);
                    console.log(`  ✅ Senha preenchida: ${selector}`);
                    senhaPreenchida = true;
                    break;
                }
            } catch {}
        }

        await this.screenshot(page, 'main-02-filled');

        // Submeter formulário
        if (emailPreenchido && senhaPreenchida) {
            const submitSelectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Entrar")',
                'button:has-text("Login")',
                'button:has-text("Acessar")',
                'button:has-text("Conectar")',
                '.submit-button',
                '.login-button'
            ];

            for (const selector of submitSelectors) {
                try {
                    const element = page.locator(selector).first();
                    if (await element.isVisible({ timeout: 1000 })) {
                        await element.click();
                        console.log(`  ✅ Login submetido: ${selector}`);
                        break;
                    }
                } catch {}
            }
        }

        // Aguardar navegação
        await page.waitForTimeout(5000);
        await this.screenshot(page, 'main-03-after-login');

        // Explorar TUDO
        await this.explorarTudo(page);
    }

    async tarefaScannerAPIs() {
        const page = this.pages.api;
        
        console.log('\n🔍 TAREFA SCANNER: Descobrindo APIs\n');

        // Lista de endpoints comuns para testar
        const endpoints = [
            '/api/auth/login',
            '/api/auth/logout',
            '/api/auth/refresh',
            '/api/auth/user',
            '/api/users',
            '/api/eventos',
            '/api/events',
            '/api/analytics',
            '/api/metrics',
            '/api/reports',
            '/api/dashboard',
            '/api/statistics',
            '/api/config',
            '/api/settings',
            '/api/profile',
            '/api/notifications',
            '/api/webhooks',
            '/api/integrations',
            '/api/export',
            '/api/import',
            '/graphql',
            '/api/v1',
            '/api/v2',
            '/api/health',
            '/api/status'
        ];

        for (const endpoint of endpoints) {
            try {
                const url = `https://beta.portal.meep.com.br${endpoint}`;
                console.log(`  Testando: ${endpoint}`);
                
                const response = await page.request.get(url, {
                    timeout: 5000,
                    headers: {
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${this.capturedData.tokens[0] || ''}`
                    }
                });
                
                const status = response.status();
                const body = await response.json().catch(() => null);
                
                if (status < 500) {
                    console.log(`    ✅ ${status} - Endpoint existe`);
                    
                    this.postmanRequests.push({
                        name: `GET ${endpoint}`,
                        request: {
                            method: 'GET',
                            url,
                            headers: response.headers()
                        },
                        response: {
                            status,
                            body
                        }
                    });
                }
            } catch (error) {
                // Endpoint não existe ou erro
            }
        }
    }

    async tarefaMonitorContinuo() {
        const page = this.pages.monitor;
        
        console.log('\n📊 TAREFA MONITOR: Captura contínua\n');

        // Loop infinito de monitoramento
        let contador = 0;
        while (contador < 100) { // Limitar para não rodar eternamente
            contador++;
            
            try {
                // Capturar dados do browser
                const capturedData = await page.evaluate(() => {
                    return window.__MEEP_CAPTURE__ || {};
                });
                
                if (capturedData.requests?.length > 0) {
                    console.log(`  📡 Capturadas ${capturedData.requests.length} requisições`);
                }
                
                // Salvar periodicamente
                if (contador % 10 === 0) {
                    await this.salvarDadosParciais(contador);
                }
                
                await page.waitForTimeout(1000);
            } catch {}
        }
    }

    async explorarTudo(page) {
        console.log('\n🗺️ EXPLORANDO TUDO NO PORTAL\n');

        // Capturar TODOS os elementos
        const elementos = await page.evaluate(() => {
            const resultado = {
                links: [],
                botoes: [],
                formularios: [],
                inputs: [],
                imagens: [],
                videos: [],
                iframes: [],
                scripts: [],
                styles: []
            };

            // Links
            document.querySelectorAll('a').forEach(a => {
                resultado.links.push({
                    href: a.href,
                    text: a.textContent?.trim(),
                    target: a.target
                });
            });

            // Botões
            document.querySelectorAll('button').forEach(btn => {
                resultado.botoes.push({
                    text: btn.textContent?.trim(),
                    type: btn.type,
                    onclick: btn.onclick?.toString()
                });
            });

            // Formulários
            document.querySelectorAll('form').forEach(form => {
                const campos = [];
                form.querySelectorAll('input, select, textarea').forEach(campo => {
                    campos.push({
                        name: campo.name,
                        type: campo.type,
                        value: campo.value,
                        placeholder: campo.placeholder
                    });
                });
                resultado.formularios.push({
                    action: form.action,
                    method: form.method,
                    campos
                });
            });

            // Imagens
            document.querySelectorAll('img').forEach(img => {
                resultado.imagens.push({
                    src: img.src,
                    alt: img.alt
                });
            });

            // Scripts
            document.querySelectorAll('script').forEach(script => {
                if (script.src) {
                    resultado.scripts.push(script.src);
                }
            });

            // Styles
            document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                resultado.styles.push(link.href);
            });

            return resultado;
        });

        // Salvar elementos capturados
        await fs.writeFile(
            'meep-ultimate/analysis/elementos.json',
            JSON.stringify(elementos, null, 2)
        );

        console.log(`  ✅ Capturados:`);
        console.log(`     - ${elementos.links.length} links`);
        console.log(`     - ${elementos.botoes.length} botões`);
        console.log(`     - ${elementos.formularios.length} formulários`);
        console.log(`     - ${elementos.imagens.length} imagens`);
        console.log(`     - ${elementos.scripts.length} scripts`);

        // Tentar clicar em links importantes
        const linksImportantes = elementos.links.filter(link => 
            link.href?.includes('evento') ||
            link.href?.includes('dashboard') ||
            link.href?.includes('relatorio') ||
            link.href?.includes('analytics')
        );

        for (const link of linksImportantes.slice(0, 5)) {
            try {
                console.log(`  Navegando para: ${link.text}`);
                await page.goto(link.href, { waitUntil: 'networkidle', timeout: 10000 });
                await this.screenshot(page, `explore-${Date.now()}`);
                await page.waitForTimeout(2000);
            } catch {}
        }
    }

    async salvarDadosParciais(iteracao) {
        console.log(`\n💾 Salvando dados parciais (iteração ${iteracao})\n`);

        const relatorio = {
            timestamp: Date.now(),
            iteracao,
            estatisticas: {
                totalRequests: this.capturedData.totalRequests,
                apis: this.capturedData.apis.size,
                curlCommands: this.curlCommands.length,
                postmanRequests: this.postmanRequests.length,
                websockets: this.capturedData.websockets.length,
                errors: this.capturedData.errors.length,
                screenshots: this.capturedData.screenshots.length
            },
            dados: this.capturedData
        };

        await fs.writeFile(
            `meep-ultimate/analysis/relatorio-${iteracao}.json`,
            JSON.stringify(relatorio, null, 2)
        );

        // Salvar cURLs
        if (this.curlCommands.length > 0) {
            const curlScript = '#!/bin/bash\n\n' + this.curlCommands.join('\n\n');
            await fs.writeFile(
                `meep-ultimate/curl/commands-${iteracao}.sh`,
                curlScript
            );
        }

        // Salvar Postman
        if (this.postmanRequests.length > 0) {
            const collection = {
                info: {
                    name: `MEEP Capture - ${iteracao}`,
                    schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
                },
                item: this.postmanRequests
            };

            await fs.writeFile(
                `meep-ultimate/postman/collection-${iteracao}.json`,
                JSON.stringify(collection, null, 2)
            );
        }
    }

    async screenshot(page, nome) {
        const filename = `meep-ultimate/screenshots/${nome}.png`;
        await page.screenshot({ path: filename, fullPage: false });
        this.capturedData.screenshots.push(filename);
        return filename;
    }

    categorizar(url) {
        if (url.includes('/api/')) return 'API';
        if (url.includes('.js')) return 'JavaScript';
        if (url.includes('.css')) return 'CSS';
        if (url.includes('image') || url.includes('.png') || url.includes('.jpg')) return 'Imagem';
        if (url.includes('font')) return 'Fonte';
        if (url.includes('analytics')) return 'Analytics';
        if (url.includes('track')) return 'Tracking';
        return 'Outros';
    }

    gerarCurlCompleto(method, url, headers, postData) {
        let curl = `curl -X ${method} '${url}'`;
        
        for (const [key, value] of Object.entries(headers)) {
            if (!key.startsWith(':')) {
                curl += ` \\\n  -H '${key}: ${value}'`;
            }
        }
        
        if (postData) {
            curl += ` \\\n  --data '${postData}'`;
        }
        
        curl += ` \\\n  --compressed --insecure -w '\\n%{http_code}\\n'`;
        
        return curl;
    }

    extrairTokens(obj) {
        const procurar = (o) => {
            if (!o || typeof o !== 'object') return;
            
            for (const [key, value] of Object.entries(o)) {
                if (typeof value === 'string' && value.length > 20) {
                    if (key.toLowerCase().includes('token') ||
                        key.toLowerCase().includes('jwt') ||
                        key.toLowerCase().includes('auth') ||
                        key.toLowerCase().includes('key') ||
                        key.toLowerCase().includes('secret')) {
                        this.capturedData.tokens.push({
                            key,
                            value: value.substring(0, 20) + '...',
                            timestamp: Date.now()
                        });
                        console.log(`    🔑 Token encontrado: ${key}`);
                    }
                } else if (typeof value === 'object') {
                    procurar(value);
                }
            }
        };
        
        procurar(obj);
    }

    async finalizar() {
        console.log('\n📊 FINALIZANDO CAPTURA ULTIMATE\n');
        
        // Fechar contexto para salvar HAR
        await this.context.close();
        
        // Relatório final
        const relatorioFinal = {
            titulo: 'MEEP ULTIMATE CAPTURE - Relatório Final',
            timestamp: Date.now(),
            estatisticas: {
                totalRequests: this.capturedData.totalRequests,
                totalAPIs: Array.from(this.capturedData.apis.values()).flat().length,
                categorias: this.capturedData.apis.size,
                curlCommands: this.curlCommands.length,
                postmanRequests: this.postmanRequests.length,
                tokens: this.capturedData.tokens.length,
                websockets: this.capturedData.websockets.length,
                errors: this.capturedData.errors.length,
                console: this.capturedData.console.length,
                screenshots: this.capturedData.screenshots.length,
                workers: this.capturedData.workers.length
            },
            arquivosGerados: [
                'capture.har',
                'elementos.json',
                'relatorios parciais',
                'comandos cURL',
                'coleções Postman',
                'screenshots',
                'vídeos'
            ]
        };
        
        await fs.writeFile(
            'meep-ultimate/RELATORIO-FINAL.json',
            JSON.stringify(relatorioFinal, null, 2)
        );
        
        console.log('=' .repeat(80));
        console.log('🎯 CAPTURA ULTIMATE COMPLETA!');
        console.log(`✅ Total de requisições: ${relatorioFinal.estatisticas.totalRequests}`);
        console.log(`✅ APIs capturadas: ${relatorioFinal.estatisticas.totalAPIs}`);
        console.log(`✅ Tokens encontrados: ${relatorioFinal.estatisticas.tokens}`);
        console.log(`✅ WebSockets: ${relatorioFinal.estatisticas.websockets}`);
        console.log(`✅ Screenshots: ${relatorioFinal.estatisticas.screenshots}`);
        console.log(`✅ Comandos cURL: ${relatorioFinal.estatisticas.curlCommands}`);
        console.log('\n📁 Todos os dados em: meep-ultimate/');
        console.log('=' .repeat(80));
        
        if (this.browser) {
            await this.browser.close();
        }
    }
}

// Executar missão
async function executar() {
    const missao = new MEEPUltimateCapture();
    
    try {
        await missao.iniciar();
    } catch (error) {
        console.error('❌ Erro:', error);
    } finally {
        await missao.finalizar();
    }
}

console.log('🔥 INICIANDO MEEP ULTIMATE CAPTURE\n');
executar().catch(console.error);