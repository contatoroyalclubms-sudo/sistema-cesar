import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * MISSÃO COMPLETA: MCP + HAR + cURL + Automação
 * Integração total dos sistemas
 */
class MissaoCompletaMCP {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.harData = [];
        this.curlCommands = [];
        this.sessionData = {
            cookies: [],
            localStorage: {},
            sessionStorage: {},
            headers: {}
        };
    }

    async iniciar() {
        console.log('🚀 MISSÃO COMPLETA MCP INICIANDO...\n');
        console.log('=' .repeat(60));
        
        // Configurar navegador com HAR recording
        this.browser = await chromium.launch({
            headless: false,
            args: [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        });

        // Criar contexto com gravação HAR
        this.context = await this.browser.newContext({
            recordHar: { 
                path: 'captures/missao-completa.har',
                mode: 'full',
                content: 'attach'
            },
            recordVideo: {
                dir: 'videos/',
                size: { width: 1920, height: 1080 }
            }
        });

        this.page = await this.context.newPage();
        
        // Interceptar todas as requisições
        await this.configurarInterceptadores();
        
        return this;
    }

    async configurarInterceptadores() {
        console.log('🔧 Configurando interceptadores...\n');
        
        // Interceptar requisições
        this.page.on('request', request => {
            const url = request.url();
            const method = request.method();
            const headers = request.headers();
            
            // Converter para cURL
            const curl = this.gerarCurl(method, url, headers, request.postData());
            this.curlCommands.push(curl);
            
            console.log(`📤 ${method} ${url.substring(0, 50)}...`);
        });

        // Interceptar respostas
        this.page.on('response', response => {
            const status = response.status();
            const url = response.url();
            
            if (status >= 400) {
                console.log(`❌ Erro ${status}: ${url}`);
            }
        });

        // Capturar console do browser
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('🔴 Console Error:', msg.text());
            }
        });

        // WebSocket monitoring
        this.page.on('websocket', ws => {
            console.log('🔌 WebSocket conectado:', ws.url());
            
            ws.on('framereceived', ({ payload }) => {
                console.log('📥 WS Recebido:', payload.substring(0, 100));
            });
            
            ws.on('framesent', ({ payload }) => {
                console.log('📤 WS Enviado:', payload.substring(0, 100));
            });
        });
    }

    gerarCurl(method, url, headers, postData) {
        let curl = `curl -X ${method} '${url}'`;
        
        // Adicionar headers
        for (const [key, value] of Object.entries(headers)) {
            if (!key.startsWith(':')) {  // Ignorar pseudo-headers HTTP/2
                curl += ` \\\n  -H '${key}: ${value}'`;
            }
        }
        
        // Adicionar body se existir
        if (postData) {
            curl += ` \\\n  --data '${postData}'`;
        }
        
        return curl;
    }

    async executarMissaoGitHub() {
        console.log('\n🐙 MISSÃO GITHUB COM CAPTURA COMPLETA\n');
        console.log('-' .repeat(60));
        
        try {
            // 1. Navegar para GitHub
            console.log('📍 Navegando para GitHub...');
            await this.page.goto('https://github.com', { 
                waitUntil: 'networkidle',
                timeout: 30000 
            });
            
            // Capturar estado inicial
            await this.capturarEstado('github-home');
            
            // 2. Clicar em Sign in
            console.log('🔐 Indo para login...');
            await this.page.click('a[href="/login"]');
            await this.page.waitForLoadState('networkidle');
            
            // Capturar página de login
            await this.capturarEstado('github-login');
            
            // 3. Preencher formulário
            console.log('📝 Preenchendo formulário...');
            await this.page.fill('#login_field', 'contato.royalclubms@gmail.com');
            await this.page.fill('#password', '352162Cl');
            
            // Screenshot antes do login
            await this.page.screenshot({ 
                path: 'captures/github-login-filled.png',
                fullPage: true 
            });
            
            // 4. Fazer login
            console.log('🚀 Fazendo login...');
            await this.page.click('input[type="submit"]');
            
            // Aguardar navegação
            try {
                await this.page.waitForURL('https://github.com/', { timeout: 10000 });
                console.log('✅ Login bem-sucedido!');
                await this.capturarEstado('github-logged');
            } catch (e) {
                console.log('⚠️ Aguardando verificação 2FA ou captcha...');
                await this.page.waitForTimeout(30000);
            }
            
            // 5. Navegar para repositório
            console.log('📁 Navegando para repositório...');
            await this.page.goto('https://github.com/contatoroyalclubms-sudo/sistema-cesar', {
                waitUntil: 'networkidle'
            });
            
            await this.capturarEstado('github-repo');
            
        } catch (error) {
            console.error('❌ Erro na missão:', error.message);
            await this.page.screenshot({ path: 'captures/erro.png' });
        }
    }

    async capturarEstado(nome) {
        console.log(`📸 Capturando estado: ${nome}`);
        
        // Screenshot
        await this.page.screenshot({ 
            path: `captures/${nome}.png`,
            fullPage: false 
        });
        
        // Capturar cookies
        const cookies = await this.context.cookies();
        
        // Capturar localStorage e sessionStorage
        const storage = await this.page.evaluate(() => ({
            localStorage: { ...localStorage },
            sessionStorage: { ...sessionStorage }
        }));
        
        // Salvar estado
        this.sessionData = {
            timestamp: new Date().toISOString(),
            nome,
            url: this.page.url(),
            cookies,
            ...storage
        };
        
        // Salvar em arquivo
        await fs.writeFile(
            `captures/${nome}-state.json`,
            JSON.stringify(this.sessionData, null, 2)
        );
    }

    async executarMissaoAPI() {
        console.log('\n🌐 MISSÃO API TESTING COM HAR\n');
        console.log('-' .repeat(60));
        
        const apis = [
            'https://api.github.com/user',
            'https://api.github.com/repos',
            'https://jsonplaceholder.typicode.com/posts',
            'https://httpbin.org/headers'
        ];
        
        for (const api of apis) {
            console.log(`\n📡 Testando: ${api}`);
            
            try {
                const response = await this.page.request.get(api);
                const status = response.status();
                const data = await response.json().catch(() => null);
                
                console.log(`  Status: ${status}`);
                console.log(`  Dados: ${data ? 'JSON válido' : 'Sem dados'}`);
                
                // Gerar cURL para esta API
                const curl = this.gerarCurl('GET', api, response.headers(), null);
                console.log(`  cURL: ${curl.substring(0, 100)}...`);
                
            } catch (error) {
                console.log(`  ❌ Erro: ${error.message}`);
            }
        }
    }

    async executarMissaoWebScraping() {
        console.log('\n🕷️ MISSÃO WEB SCRAPING\n');
        console.log('-' .repeat(60));
        
        // Navegar para site de exemplo
        await this.page.goto('https://news.ycombinator.com', {
            waitUntil: 'networkidle'
        });
        
        // Extrair dados
        const noticias = await this.page.evaluate(() => {
            const items = Array.from(document.querySelectorAll('.athing'));
            return items.slice(0, 10).map(item => {
                const titleEl = item.querySelector('.titleline > a');
                const scoreEl = item.nextElementSibling?.querySelector('.score');
                return {
                    titulo: titleEl?.textContent,
                    url: titleEl?.href,
                    pontos: scoreEl?.textContent
                };
            });
        });
        
        console.log(`📰 Extraídas ${noticias.length} notícias:`);
        noticias.forEach((n, i) => {
            console.log(`  ${i + 1}. ${n.titulo?.substring(0, 50)}...`);
        });
        
        // Salvar dados
        await fs.writeFile(
            'captures/noticias.json',
            JSON.stringify(noticias, null, 2)
        );
    }

    async gerarRelatorio() {
        console.log('\n📊 GERANDO RELATÓRIO FINAL\n');
        console.log('=' .repeat(60));
        
        // Fechar contexto para salvar HAR
        await this.context.close();
        
        // Ler arquivo HAR
        const harContent = await fs.readFile('captures/missao-completa.har', 'utf-8');
        const har = JSON.parse(harContent);
        
        const relatorio = {
            timestamp: new Date().toISOString(),
            estatisticas: {
                total_requisicoes: har.log.entries.length,
                total_curl_commands: this.curlCommands.length,
                paginas_visitadas: har.log.pages?.length || 0,
                tempo_total: har.log.pages?.[0]?.pageTimings?.onLoad || 0
            },
            requisicoes_por_tipo: this.analisarRequisicoes(har.log.entries),
            curl_samples: this.curlCommands.slice(0, 5),
            cookies_capturados: this.sessionData.cookies?.length || 0,
            arquivos_gerados: await this.listarArquivos()
        };
        
        // Salvar relatório
        await fs.writeFile(
            'captures/relatorio-final.json',
            JSON.stringify(relatorio, null, 2)
        );
        
        // Exibir resumo
        console.log('📈 RESUMO DA MISSÃO:');
        console.log(`  ✅ Requisições capturadas: ${relatorio.estatisticas.total_requisicoes}`);
        console.log(`  ✅ Comandos cURL gerados: ${relatorio.estatisticas.total_curl_commands}`);
        console.log(`  ✅ Páginas visitadas: ${relatorio.estatisticas.paginas_visitadas}`);
        console.log(`  ✅ Cookies capturados: ${relatorio.cookies_capturados}`);
        console.log(`  ✅ Arquivos gerados: ${relatorio.arquivos_gerados.length}`);
        
        // Salvar comandos cURL
        const curlScript = this.curlCommands.join('\n\n');
        await fs.writeFile('captures/comandos.sh', curlScript);
        console.log('\n📝 Comandos cURL salvos em: captures/comandos.sh');
        
        return relatorio;
    }

    analisarRequisicoes(entries) {
        const tipos = {};
        entries.forEach(entry => {
            const tipo = entry.response.content.mimeType?.split('/')[0] || 'unknown';
            tipos[tipo] = (tipos[tipo] || 0) + 1;
        });
        return tipos;
    }

    async listarArquivos() {
        try {
            const files = await fs.readdir('captures');
            return files;
        } catch {
            return [];
        }
    }

    async finalizar() {
        if (this.browser) {
            await this.browser.close();
        }
        console.log('\n🎉 MISSÃO COMPLETA!');
    }
}

// Executar missão completa
async function executar() {
    const missao = new MissaoCompletaMCP();
    
    try {
        // Criar diretórios
        await fs.mkdir('captures', { recursive: true });
        await fs.mkdir('videos', { recursive: true });
        
        // Iniciar missão
        await missao.iniciar();
        
        // Executar todas as missões
        await missao.executarMissaoGitHub();
        await missao.executarMissaoAPI();
        await missao.executarMissaoWebScraping();
        
        // Gerar relatório
        await missao.gerarRelatorio();
        
    } catch (error) {
        console.error('❌ Erro fatal:', error);
    } finally {
        await missao.finalizar();
    }
}

// Executar
console.log('🎯 MISSÃO COMPLETA MCP + HAR + cURL\n');
executar().catch(console.error);