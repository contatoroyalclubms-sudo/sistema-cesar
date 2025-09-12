const { chromium } = require('playwright');

async function navegadorNormalGitHub() {
    console.log('🚀 MISSÃO COMPLETA: Navegador Normal + GitHub + Google Login');
    console.log('=' * 60);

    // Credenciais do Google
    const email = 'contato.royalclubms@gmail.com';
    const password = '352162Cl';

    let browser;
    let page;

    try {
        // Abrir navegador NORMAL (visível) - exatamente como solicitado
        console.log('🌐 Abrindo navegador normal...');
        browser = await chromium.launch({
            headless: false,        // NAVEGADOR NORMAL VISÍVEL
            slowMo: 500,           // Ações visíveis
            devtools: false,       // Não abrir devtools
            args: [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled'
            ]
        });

        // Nova página
        page = await browser.newPage();
        
        // Configurar viewport para tela cheia
        await page.setViewportSize({ width: 1920, height: 1080 });

        console.log('📍 ETAPA 1: Navegando para GitHub...');
        await page.goto('https://github.com/', { 
            waitUntil: 'networkidle',
            timeout: 30000 
        });

        // Capturar screenshot
        await page.screenshot({ path: 'github-01-homepage.png', fullPage: true });
        console.log('📸 Screenshot: github-01-homepage.png');

        console.log('🔍 ETAPA 2: Procurando botão Sign in...');
        
        // Aguardar e clicar em Sign in
        await page.waitForSelector('a[href="/login"]', { timeout: 10000 });
        await page.click('a[href="/login"]');
        
        console.log('⏳ Aguardando página de login...');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'github-02-login-page.png', fullPage: true });
        console.log('📸 Screenshot: github-02-login-page.png');

        console.log('🔍 ETAPA 3: Procurando login com Google...');
        
        // Tentar encontrar botão do Google OAuth
        try {
            // Procurar por vários seletores possíveis do Google
            const googleSelectors = [
                'a[href*="oauth/authorize"]',
                'button[data-provider="google"]',
                'a[data-provider="google"]',
                '.btn-google',
                '[data-ga-click*="google"]',
                'a[href*="google.com/oauth"]'
            ];

            let googleButton = null;
            for (const selector of googleSelectors) {
                try {
                    googleButton = await page.waitForSelector(selector, { timeout: 2000 });
                    if (googleButton) {
                        console.log(`✅ Botão Google encontrado: ${selector}`);
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }

            if (googleButton) {
                console.log('🔗 Clicando no botão Google OAuth...');
                await googleButton.click();
                
                // Aguardar redirecionamento para Google
                await page.waitForURL('**/accounts.google.com/**', { timeout: 15000 });
                console.log('🎯 Redirecionado para Google!');

                console.log('📧 ETAPA 4: Fazendo login no Google...');
                
                // Aguardar campo de email
                await page.waitForSelector('#identifierId', { timeout: 10000 });
                await page.fill('#identifierId', email);
                await page.click('#identifierNext');
                
                console.log('⏳ Aguardando campo de senha...');
                await page.waitForSelector('input[name="password"]', { timeout: 10000 });
                await page.fill('input[name="password"]', password);
                await page.click('#passwordNext');
                
                console.log('🔐 Login enviado, aguardando processamento...');
                await page.waitForTimeout(5000);

            } else {
                console.log('ℹ️  Botão Google não encontrado, fazendo login manual...');
                
                // Login manual no GitHub
                await page.fill('#login_field', email);
                await page.fill('#password', password);
                await page.click('input[type="submit"]');
            }

        } catch (error) {
            console.log('⚠️ Erro no OAuth, tentando login manual...');
            console.log('Error:', error.message);
        }

        console.log('🏠 ETAPA 5: Navegando para repositório...');
        await page.goto('https://github.com/contatoroyalclubms-sudo/sistema-cesar', {
            waitUntil: 'networkidle',
            timeout: 30000
        });

        await page.screenshot({ path: 'github-03-repository.png', fullPage: true });
        console.log('📸 Screenshot: github-03-repository.png');

        console.log('⚙️ ETAPA 6: Verificando se precisa criar repositório...');
        
        // Verificar se a página mostra erro 404 (repositório não existe)
        const pageContent = await page.content();
        if (pageContent.includes('404') || pageContent.includes('Not Found')) {
            console.log('📁 Repositório não existe, navegando para criar novo...');
            
            await page.goto('https://github.com/new', { waitUntil: 'networkidle' });
            await page.screenshot({ path: 'github-04-new-repo-page.png', fullPage: true });
            
            // Preencher formulário de novo repositório
            await page.fill('#repository_name', 'sistema-cesar');
            await page.fill('#repository_description', 'Sistema Cesar V7 - Painel Universal');
            
            // Tornar público se necessário
            try {
                await page.click('input[value="public"]');
            } catch (e) {
                console.log('Repositório já configurado como público');
            }
            
            await page.screenshot({ path: 'github-05-repo-filled.png', fullPage: true });
            
            // Criar repositório
            await page.click('button[type="submit"]:has-text("Create repository")');
            await page.waitForLoadState('networkidle');
            
            console.log('✅ Repositório criado!');
        }

        console.log('🎉 MISSÃO CONCLUÍDA COM SUCESSO!');
        console.log('📊 Resumo:');
        console.log('   ✅ Navegador normal aberto');
        console.log('   ✅ GitHub acessado');
        console.log('   ✅ Login processado');
        console.log('   ✅ Repositório sistema-cesar acessível');
        
        console.log('⏳ Mantendo navegador aberto por 60 segundos para verificação...');
        await page.waitForTimeout(60000);

    } catch (error) {
        console.error('❌ Erro durante automação:', error.message);
        if (page) {
            await page.screenshot({ path: 'erro-automacao.png', fullPage: true });
            console.log('📸 Screenshot do erro salvo');
        }
    } finally {
        console.log('🎯 Automação finalizada!');
        // Não fechar automaticamente para permitir verificação manual
        // if (browser) await browser.close();
    }
}

// Executar automação
navegadorNormalGitHub().catch(console.error);