const { test, expect, chromium } = require('@playwright/test');
const path = require('path');

/**
 * TESTE COMPLETO DO SISTEMA DE LOGIN
 * ==================================
 * 
 * INFORMACOES DO SISTEMA:
 * - Frontend: http://localhost:5177
 * - Backend: http://localhost:8000 (auth_server.py)  
 * - Credenciais teste: Admin CPF "00000000000", Senha "0000"
 * 
 * TAREFAS:
 * 1. Navegue para http://localhost:5177
 * 2. Teste o login com as credenciais: CPF "00000000000", senha "0000" 
 * 3. Capture screenshots do processo
 * 4. Documente erros encontrados
 * 5. Teste navegação pós-login se o login funcionar
 * 6. Valide se o Dashboard BI (Phase 5) está acessível em /app/bi/dashboard
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
        // TAREFA 1: Navegar para o frontend
        console.log('📍 ETAPA 1: Navegando para http://localhost:5177');
        await page.goto('http://localhost:5177', { waitUntil: 'networkidle' });
        
        // Screenshot inicial
        await page.screenshot({ 
            path: './screenshot_01_inicial.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot inicial capturado: screenshot_01_inicial.png');

        // Aguardar carregamento da página
        await page.waitForTimeout(2000);

        // TAREFA 2: Localizar campos de login
        console.log('\n📍 ETAPA 2: Localizando campos de login');
        
        // Procurar por diferentes seletores possíveis para os campos de login
        const possibleCpfSelectors = [
            'input[name="cpf"]',
            'input[placeholder*="CPF"]',
            '#cpf',
            'input[type="text"]',
            '.cpf-input'
        ];

        const possiblePasswordSelectors = [
            'input[name="senha"]',
            'input[name="password"]',
            'input[placeholder*="senha"]',
            'input[placeholder*="Senha"]',
            '#senha',
            '#password',
            'input[type="password"]'
        ];

        let cpfField = null;
        let passwordField = null;
        
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
            console.log('❌ ERRO: Campos de login não encontrados!');
            console.log('📋 Elementos disponíveis na página:');
            
            // Listar inputs disponíveis
            const inputs = await page.$$eval('input', elements => 
                elements.map(el => ({
                    type: el.type,
                    name: el.name,
                    placeholder: el.placeholder,
                    id: el.id,
                    className: el.className
                }))
            );
            console.table(inputs);

            throw new Error('Campos de login não encontrados');
        }

        // TAREFA 3: Preencher credenciais
        console.log('\n📍 ETAPA 3: Preenchendo credenciais');
        console.log('   CPF: 00000000000');
        console.log('   Senha: 0000');

        // Limpar e preencher CPF
        await page.click(cpfField);
        await page.fill(cpfField, '00000000000');

        // Limpar e preencher senha
        await page.click(passwordField);
        await page.fill(passwordField, '0000');

        // Screenshot com campos preenchidos
        await page.screenshot({ 
            path: './screenshot_02_preenchido.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot com campos preenchidos: screenshot_02_preenchido.png');

        // TAREFA 4: Localizar e clicar no botão de login
        console.log('\n📍 ETAPA 4: Tentando fazer login');
        
        const possibleLoginButtons = [
            'button[type="submit"]',
            'button:has-text("Login")',
            'button:has-text("Entrar")',
            'button:has-text("Acessar")',
            '.login-button',
            '.btn-login'
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

        if (!loginButton) {
            // Listar todos os botões disponíveis
            console.log('📋 Botões disponíveis na página:');
            const buttons = await page.$$eval('button', elements => 
                elements.map(el => ({
                    type: el.type,
                    textContent: el.textContent.trim(),
                    className: el.className,
                    id: el.id
                }))
            );
            console.table(buttons);
            
            // Tentar Enter no campo de senha
            console.log('⚠️ Tentando pressionar Enter no campo senha...');
            await page.press(passwordField, 'Enter');
        } else {
            await page.click(loginButton);
        }

        // Aguardar resposta do login
        console.log('⏳ Aguardando resposta do login...');
        await page.waitForTimeout(3000);

        // TAREFA 5: Verificar se o login foi bem-sucedido
        console.log('\n📍 ETAPA 5: Verificando resultado do login');
        
        // Capturar screenshot após tentativa de login
        await page.screenshot({ 
            path: './screenshot_03_pos_login.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot pós-login: screenshot_03_pos_login.png');

        // Verificar se foi redirecionado ou se há mensagem de erro
        const currentUrl = page.url();
        console.log(`📍 URL atual: ${currentUrl}`);

        // Procurar por indicadores de sucesso de login
        const successIndicators = [
            'Dashboard', 'Painel', 'Bem-vindo', 'Welcome', 
            'Logout', 'Sair', 'Perfil', 'Configurações'
        ];

        let loginSuccess = false;
        for (const indicator of successIndicators) {
            try {
                await page.waitForSelector(`:has-text("${indicator}")`, { timeout: 2000 });
                console.log(`✅ Indicador de sucesso encontrado: ${indicator}`);
                loginSuccess = true;
                break;
            } catch (e) {
                // Continue verificando
            }
        }

        // Verificar se há mensagens de erro
        const errorIndicators = [
            'erro', 'error', 'inválido', 'incorrect', 'failed'
        ];

        for (const errorText of errorIndicators) {
            try {
                await page.waitForSelector(`:has-text("${errorText}")`, { timeout: 1000 });
                console.log(`❌ Mensagem de erro encontrada: ${errorText}`);
                break;
            } catch (e) {
                // Continue verificando
            }
        }

        if (loginSuccess || currentUrl !== 'http://localhost:5177/') {
            console.log('\n🎉 LOGIN BEM-SUCEDIDO!');
            
            // TAREFA 6: Testar navegação pós-login
            console.log('\n📍 ETAPA 6: Testando navegação pós-login');
            
            // Aguardar estabilização da página
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
                    await page.goto(`http://localhost:5177${route}`);
                    await page.waitForTimeout(2000);
                    
                    const routeUrl = page.url();
                    console.log(`      URL resultante: ${routeUrl}`);
                    
                    // Screenshot de cada rota testada
                    await page.screenshot({ 
                        path: `./screenshot_route_${route.replace(/\//g, '')}.png`, 
                        fullPage: true 
                    });
                    
                } catch (e) {
                    console.log(`      ❌ Erro ao acessar ${route}: ${e.message}`);
                }
            }

            // TAREFA 7: Validar Dashboard BI especificamente
            console.log('\n📍 ETAPA 7: Validando Dashboard BI (Phase 5)');
            try {
                await page.goto('http://localhost:5177/app/bi/dashboard');
                await page.waitForTimeout(3000);
                
                const biUrl = page.url();
                console.log(`📍 URL Dashboard BI: ${biUrl}`);
                
                // Procurar por elementos específicos do BI
                const biElements = ['chart', 'graph', 'analytics', 'metric', 'kpi'];
                let biFound = false;
                
                for (const element of biElements) {
                    try {
                        await page.waitForSelector(`[class*="${element}"], [id*="${element}"]`, { timeout: 2000 });
                        console.log(`✅ Elemento BI encontrado: ${element}`);
                        biFound = true;
                        break;
                    } catch (e) {
                        // Continue procurando
                    }
                }

                if (biFound) {
                    console.log('🎯 Dashboard BI (Phase 5) está ACESSÍVEL e FUNCIONAL!');
                } else {
                    console.log('⚠️ Dashboard BI acessível, mas elementos específicos não encontrados');
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
            console.log('   Possíveis causas:');
            console.log('   - Credenciais incorretas');
            console.log('   - Backend não está respondendo');
            console.log('   - Proxy não configurado corretamente');
            console.log('   - Campos de login não identificados corretamente');
        }

        // Screenshot final
        await page.screenshot({ 
            path: './screenshot_04_final.png', 
            fullPage: true 
        });
        console.log('✅ Screenshot final: screenshot_04_final.png');

    } catch (error) {
        console.log('\n❌ ERRO DURANTE O TESTE:', error.message);
        
        // Screenshot de erro
        await page.screenshot({ 
            path: './screenshot_error.png', 
            fullPage: true 
        });
        console.log('📸 Screenshot de erro salvo: screenshot_error.png');

        // Informações de debug
        console.log('\n🔍 INFORMAÇÕES DE DEBUG:');
        console.log(`URL atual: ${page.url()}`);
        
        try {
            const pageTitle = await page.title();
            console.log(`Título da página: ${pageTitle}`);
        } catch (e) {
            console.log('Não foi possível obter título da página');
        }

        // Verificar se os serviços estão rodando
        console.log('\n🔍 VERIFICAÇÃO DOS SERVIÇOS:');
        try {
            const response = await page.request.get('http://localhost:5177');
            console.log(`Frontend (5177): ${response.status()}`);
        } catch (e) {
            console.log('Frontend (5177): ❌ Não acessível');
        }

        try {
            const response = await page.request.get('http://localhost:8000/api/health');
            console.log(`Backend API (8000): ${response.status()}`);
        } catch (e) {
            console.log('Backend API (8000): ❌ Não acessível');
        }
    }

    await context.close();
    await browser.close();

    console.log('\n===============================================');
    console.log('>>>        TESTE CONCLUÍDO               <<<');
    console.log('===============================================\n');
    
    console.log('📁 Arquivos gerados:');
    console.log('   - screenshot_01_inicial.png');
    console.log('   - screenshot_02_preenchido.png');  
    console.log('   - screenshot_03_pos_login.png');
    console.log('   - screenshot_04_final.png');
    console.log('   - screenshot_04_dashboard_bi.png (se acessível)');
    console.log('   - Videos em ./test-results/videos/');
    console.log('\n');
}

// Executar o teste
runCompleteLoginTest().catch(console.error);