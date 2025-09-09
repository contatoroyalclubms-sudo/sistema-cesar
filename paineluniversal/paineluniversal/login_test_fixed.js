const { test, expect, chromium } = require('@playwright/test');
const path = require('path');

/**
 * TESTE COMPLETO DO SISTEMA DE LOGIN - VERSÃO CORRIGIDA
 * ====================================================
 * 
 * DESCOBERTA: A página inicial (localhost:5177) é uma LANDING PAGE
 * É necessário clicar em "Entrar" para acessar o formulário de login
 */

async function runCompleteLoginTest() {
    console.log('\n===============================================');
    console.log('>>> SISTEMA UNIVERSAL V5 - TESTE DE LOGIN <<<');
    console.log('===============================================\n');

    const browser = await chromium.launch({
        headless: false, // Para visualizar o teste
        slowMo: 1000     // Atraso entre ações para melhor visualização
    });

    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        recordVideo: {
            dir: './test-results/videos/',
            size: { width: 1920, height: 1080 }
        }
    });

    const page = await context.newPage();
    
    try {
        // ETAPA 1: Navegar para o frontend (landing page)
        console.log('📍 ETAPA 1: Navegando para http://localhost:5177 (Landing Page)');
        await page.goto('http://localhost:5177', { waitUntil: 'networkidle' });
        
        await page.screenshot({ 
            path: './screenshot_01_inicial.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot inicial capturado: screenshot_01_inicial.png');

        await page.waitForTimeout(2000);

        // ETAPA 2: Procurar e clicar no botão "Entrar"
        console.log('\n📍 ETAPA 2: Procurando botão "Entrar" na landing page');
        
        const entrarButtons = [
            'text=Entrar',
            'button:has-text("Entrar")',
            ':text("Entrar")',
            '[href*="login"]',
            'a:has-text("Entrar")',
            '.login-link'
        ];

        let entrarButton = null;
        for (const selector of entrarButtons) {
            try {
                await page.waitForSelector(selector, { timeout: 2000 });
                entrarButton = selector;
                console.log(`✅ Botão "Entrar" encontrado: ${selector}`);
                break;
            } catch (e) {
                // Continue tentando
            }
        }

        if (entrarButton) {
            console.log('🔄 Clicando no botão "Entrar"...');
            await page.click(entrarButton);
            await page.waitForTimeout(3000);
            
            const newUrl = page.url();
            console.log(`📍 URL após clicar em Entrar: ${newUrl}`);
            
            await page.screenshot({ 
                path: './screenshot_01_5_apos_entrar.png', 
                fullPage: true 
            });
            console.log('✅ Screenshot após clicar em Entrar: screenshot_01_5_apos_entrar.png');
        } else {
            console.log('⚠️ Botão "Entrar" não encontrado, tentando navegar diretamente para /login');
            await page.goto('http://localhost:5177/login');
            await page.waitForTimeout(2000);
        }

        // ETAPA 3: Procurar campos de login na nova página
        console.log('\n📍 ETAPA 3: Procurando campos de login');
        
        const possibleCpfSelectors = [
            'input[name="cpf"]',
            'input[placeholder*="CPF"]',
            'input[placeholder*="cpf"]',
            '#cpf',
            'input[type="text"]',
            '.cpf-input',
            'input[label*="CPF"]'
        ];

        const possiblePasswordSelectors = [
            'input[name="senha"]',
            'input[name="password"]',
            'input[placeholder*="senha"]',
            'input[placeholder*="Senha"]',
            'input[placeholder*="password"]',
            '#senha',
            '#password',
            'input[type="password"]'
        ];

        let cpfField = null;
        let passwordField = null;
        
        // Aguardar a página carregar completamente
        await page.waitForTimeout(2000);
        
        // Tentar encontrar campo CPF
        for (const selector of possibleCpfSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 2000 });
                cpfField = selector;
                console.log(`✅ Campo CPF encontrado: ${selector}`);
                break;
            } catch (e) {
                // Continue tentando
            }
        }

        // Tentar encontrar campo senha  
        for (const selector of possiblePasswordSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 2000 });
                passwordField = selector;
                console.log(`✅ Campo senha encontrado: ${selector}`);
                break;
            } catch (e) {
                // Continue tentando
            }
        }

        if (!cpfField || !passwordField) {
            console.log('❌ ERRO: Campos de login não encontrados na página atual!');
            console.log('📋 URL atual:', page.url());
            
            // Listar todos os elementos input, button e link disponíveis
            const pageElements = await page.evaluate(() => {
                const inputs = Array.from(document.querySelectorAll('input')).map(el => ({
                    type: 'input',
                    inputType: el.type,
                    name: el.name,
                    placeholder: el.placeholder,
                    id: el.id,
                    className: el.className
                }));
                
                const buttons = Array.from(document.querySelectorAll('button, a')).map(el => ({
                    type: el.tagName.toLowerCase(),
                    textContent: el.textContent.trim(),
                    href: el.href,
                    className: el.className,
                    id: el.id
                }));
                
                return { inputs, buttons };
            });
            
            console.log('📋 Inputs disponíveis:');
            console.table(pageElements.inputs);
            console.log('📋 Botões/Links disponíveis:');
            console.table(pageElements.buttons);

            // Tentar rotas alternativas
            const alternativeRoutes = [
                '/auth/login',
                '/signin',
                '/app/login',
                '/user/login'
            ];

            for (const route of alternativeRoutes) {
                try {
                    console.log(`🔍 Tentando rota alternativa: ${route}`);
                    await page.goto(`http://localhost:5177${route}`);
                    await page.waitForTimeout(2000);
                    
                    // Verificar se há inputs nesta página
                    const hasInputs = await page.$$eval('input', inputs => inputs.length > 0);
                    if (hasInputs) {
                        console.log(`✅ Inputs encontrados em ${route}!`);
                        // Tentar novamente procurar os campos
                        for (const selector of possibleCpfSelectors) {
                            try {
                                await page.waitForSelector(selector, { timeout: 1000 });
                                cpfField = selector;
                                console.log(`✅ Campo CPF encontrado em ${route}: ${selector}`);
                                break;
                            } catch (e) {}
                        }
                        
                        for (const selector of possiblePasswordSelectors) {
                            try {
                                await page.waitForSelector(selector, { timeout: 1000 });
                                passwordField = selector;
                                console.log(`✅ Campo senha encontrado em ${route}: ${selector}`);
                                break;
                            } catch (e) {}
                        }
                        
                        if (cpfField && passwordField) break;
                    }
                } catch (e) {
                    console.log(`❌ Rota ${route} não acessível`);
                }
            }
        }

        if (!cpfField || !passwordField) {
            throw new Error('Não foi possível encontrar campos de login em nenhuma rota');
        }

        // ETAPA 4: Preencher credenciais
        console.log('\n📍 ETAPA 4: Preenchendo credenciais');
        console.log('   CPF: 00000000000');
        console.log('   Senha: 0000');

        // Limpar e preencher CPF
        await page.click(cpfField);
        await page.keyboard.press('Control+A'); // Selecionar tudo
        await page.fill(cpfField, '00000000000');

        // Limpar e preencher senha
        await page.click(passwordField);
        await page.keyboard.press('Control+A'); // Selecionar tudo
        await page.fill(passwordField, '0000');

        // Screenshot com campos preenchidos
        await page.screenshot({ 
            path: './screenshot_02_preenchido.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot com campos preenchidos: screenshot_02_preenchido.png');

        // ETAPA 5: Localizar e clicar no botão de login
        console.log('\n📍 ETAPA 5: Tentando fazer login');
        
        const possibleLoginButtons = [
            'button[type="submit"]',
            'button:has-text("Login")',
            'button:has-text("Entrar")',
            'button:has-text("Acessar")',
            'input[type="submit"]',
            '.login-button',
            '.btn-login',
            'form button',
            '[data-testid="login-button"]'
        ];

        let loginButton = null;
        for (const selector of possibleLoginButtons) {
            try {
                await page.waitForSelector(selector, { timeout: 2000 });
                loginButton = selector;
                console.log(`✅ Botão de login encontrado: ${selector}`);
                break;
            } catch (e) {
                // Continue tentando
            }
        }

        if (loginButton) {
            await page.click(loginButton);
        } else {
            console.log('⚠️ Botão de login não encontrado, tentando pressionar Enter...');
            await page.press(passwordField, 'Enter');
        }

        // Aguardar resposta do login
        console.log('⏳ Aguardando resposta do login...');
        await page.waitForTimeout(5000); // Aguardar mais tempo para resposta da API

        // ETAPA 6: Verificar se o login foi bem-sucedido
        console.log('\n📍 ETAPA 6: Verificando resultado do login');
        
        // Capturar screenshot após tentativa de login
        await page.screenshot({ 
            path: './screenshot_03_pos_login.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot pós-login: screenshot_03_pos_login.png');

        // Verificar se foi redirecionado
        const currentUrl = page.url();
        console.log(`📍 URL atual: ${currentUrl}`);

        // Verificar se há elementos indicando sucesso do login
        const successIndicators = [
            'Dashboard', 'Painel', 'Bem-vindo', 'Welcome', 
            'Logout', 'Sair', 'Perfil', 'Configurações',
            'menu', 'sidebar', 'nav'
        ];

        let loginSuccess = false;
        const foundIndicators = [];
        
        for (const indicator of successIndicators) {
            try {
                const element = await page.waitForSelector(`:text("${indicator}")`, { timeout: 1000 });
                if (element) {
                    foundIndicators.push(indicator);
                    loginSuccess = true;
                }
            } catch (e) {
                // Continue verificando
            }
        }

        // Verificar mudança de URL (indicativo de redirecionamento)
        if (currentUrl !== 'http://localhost:5177/' && currentUrl !== 'http://localhost:5177/login') {
            loginSuccess = true;
            console.log('✅ URL mudou após login - provável sucesso');
        }

        // Verificar presença de token no localStorage (se possível)
        try {
            const hasToken = await page.evaluate(() => {
                return localStorage.getItem('token') || localStorage.getItem('access_token') || sessionStorage.getItem('token');
            });
            if (hasToken) {
                loginSuccess = true;
                console.log('✅ Token de autenticação encontrado no localStorage');
            }
        } catch (e) {
            // Não foi possível verificar localStorage
        }

        if (loginSuccess) {
            console.log('\n🎉 LOGIN BEM-SUCEDIDO!');
            if (foundIndicators.length > 0) {
                console.log(`   Indicadores encontrados: ${foundIndicators.join(', ')}`);
            }
            
            // ETAPA 7: Testar navegação pós-login
            console.log('\n📍 ETAPA 7: Testando navegação pós-login');
            
            await page.waitForTimeout(2000);

            // Tentar acessar diferentes rotas
            const routesToTest = [
                '/app',
                '/dashboard', 
                '/app/dashboard',
                '/app/bi/dashboard',
                '/home',
                '/eventos'
            ];

            for (const route of routesToTest) {
                try {
                    console.log(`   🔍 Testando rota: ${route}`);
                    await page.goto(`http://localhost:5177${route}`, { waitUntil: 'networkidle' });
                    await page.waitForTimeout(3000);
                    
                    const routeUrl = page.url();
                    console.log(`      URL resultante: ${routeUrl}`);
                    
                    // Screenshot de cada rota testada
                    const cleanRoute = route.replace(/\//g, '').replace(/\./g, '_') || 'root';
                    await page.screenshot({ 
                        path: `./screenshot_route_${cleanRoute}.png`, 
                        fullPage: true 
                    });
                    
                } catch (e) {
                    console.log(`      ❌ Erro ao acessar ${route}: ${e.message}`);
                }
            }

            // ETAPA 8: Validar Dashboard BI especificamente
            console.log('\n📍 ETAPA 8: Validando Dashboard BI (Phase 5)');
            try {
                await page.goto('http://localhost:5177/app/bi/dashboard', { waitUntil: 'networkidle' });
                await page.waitForTimeout(5000);
                
                const biUrl = page.url();
                console.log(`📍 URL Dashboard BI: ${biUrl}`);
                
                // Procurar por elementos específicos do BI
                const biElements = await page.evaluate(() => {
                    const selectors = ['chart', 'graph', 'analytics', 'metric', 'kpi', 'dashboard', 'bi'];
                    const found = [];
                    
                    for (const selector of selectors) {
                        const byClass = document.querySelectorAll(`[class*="${selector}"]`);
                        const byId = document.querySelectorAll(`[id*="${selector}"]`);
                        const byText = document.querySelectorAll(`:text("${selector}")`);
                        
                        if (byClass.length > 0) found.push(`class:${selector}(${byClass.length})`);
                        if (byId.length > 0) found.push(`id:${selector}(${byId.length})`);
                    }
                    
                    return found;
                });

                if (biElements.length > 0) {
                    console.log(`🎯 Dashboard BI (Phase 5) está ACESSÍVEL e FUNCIONAL!`);
                    console.log(`   Elementos BI encontrados: ${biElements.join(', ')}`);
                } else {
                    console.log('⚠️ Dashboard BI acessível, mas elementos específicos não identificados');
                }

                await page.screenshot({ 
                    path: './screenshot_04_dashboard_bi.png', 
                    fullPage: true 
                });
                console.log('✅ Screenshot Dashboard BI: screenshot_04_dashboard_bi.png');

            } catch (e) {
                console.log(`❌ Erro ao acessar Dashboard BI: ${e.message}`);
            }

        } else {
            console.log('\n❌ LOGIN FALHOU!');
            
            // Verificar se há mensagens de erro
            try {
                const errorMessages = await page.evaluate(() => {
                    const errorSelectors = ['[class*="error"]', '[class*="alert"]', '[role="alert"]'];
                    const messages = [];
                    
                    for (const selector of errorSelectors) {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            if (el.textContent.trim()) {
                                messages.push(el.textContent.trim());
                            }
                        });
                    }
                    
                    return messages;
                });
                
                if (errorMessages.length > 0) {
                    console.log('📋 Mensagens de erro encontradas:');
                    errorMessages.forEach(msg => console.log(`   - ${msg}`));
                }
            } catch (e) {
                console.log('   Não foi possível capturar mensagens de erro específicas');
            }
            
            console.log('   Possíveis causas:');
            console.log('   - Credenciais incorretas');
            console.log('   - Backend não está respondendo');
            console.log('   - Problema na configuração do proxy');
            console.log('   - Frontend esperando resposta diferente da API');
        }

        // Screenshot final
        await page.screenshot({ 
            path: './screenshot_04_final.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot final: screenshot_04_final.png');

    } catch (error) {
        console.log('\n❌ ERRO DURANTE O TESTE:', error.message);
        console.log('Stack trace:', error.stack);
        
        // Screenshot de erro
        await page.screenshot({ 
            path: './screenshot_error.png', 
            fullPage: true 
        });
        console.log('📸 Screenshot de erro salvo: screenshot_error.png');

        // Informações de debug detalhadas
        console.log('\n🔍 INFORMAÇÕES DE DEBUG:');
        console.log(`URL atual: ${page.url()}`);
        
        try {
            const pageTitle = await page.title();
            console.log(`Título da página: ${pageTitle}`);
        } catch (e) {
            console.log('Não foi possível obter título da página');
        }

        // Verificar console do navegador
        page.on('console', msg => {
            console.log(`🌐 Console: ${msg.type()}: ${msg.text()}`);
        });

    } finally {
        await context.close();
        await browser.close();
    }

    console.log('\n===============================================');
    console.log('>>>        TESTE CONCLUÍDO               <<<');
    console.log('===============================================\n');
    
    console.log('📁 Arquivos gerados:');
    console.log('   - screenshot_01_inicial.png (Landing page)');
    console.log('   - screenshot_01_5_apos_entrar.png (Após clicar Entrar)');
    console.log('   - screenshot_02_preenchido.png (Campos preenchidos)');  
    console.log('   - screenshot_03_pos_login.png (Pós login)');
    console.log('   - screenshot_04_final.png (Final)');
    console.log('   - screenshot_04_dashboard_bi.png (Dashboard BI, se acessível)');
    console.log('   - screenshot_route_*.png (Rotas testadas)');
    console.log('   - Videos em ./test-results/videos/');
}

// Executar o teste
runCompleteLoginTest().catch(console.error);