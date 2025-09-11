const { chromium } = require('playwright');

async function setupGitHubForDeploy() {
    console.log('🚀 Iniciando automação do GitHub para configuração de deploy...');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 1000 // Tornar as ações mais visíveis
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    
    try {
        console.log('📱 Navegando para GitHub...');
        await page.goto('https://github.com/', { waitUntil: 'networkidle' });
        
        // Tirar screenshot inicial
        await page.screenshot({ path: 'github-01-homepage.png' });
        console.log('📸 Screenshot salvo: github-01-homepage.png');
        
        // Procurar botão de login
        console.log('🔍 Procurando botão de login...');
        
        const loginSelectors = [
            'a[href="/login"]',
            'text=Sign in',
            '[data-testid="signin-link"]',
            '.Header-link[href="/login"]'
        ];
        
        let loginButton = null;
        for (const selector of loginSelectors) {
            try {
                loginButton = await page.locator(selector).first();
                if (await loginButton.isVisible()) {
                    console.log(`✅ Botão de login encontrado: ${selector}`);
                    break;
                }
            } catch (e) {
                console.log(`❌ Seletor não encontrado: ${selector}`);
            }
        }
        
        if (loginButton && await loginButton.isVisible()) {
            console.log('🖱️ Clicando no botão de login...');
            await loginButton.click();
            await page.waitForLoadState('networkidle');
            await page.screenshot({ path: 'github-02-login-page.png' });
            console.log('📸 Screenshot salvo: github-02-login-page.png');
            
            // Procurar opção de login com Google
            console.log('🔍 Procurando opção de login com Google...');
            
            const googleLoginSelectors = [
                'text=Continue with Google',
                'text=Sign in with Google',
                '[aria-label="Sign in with Google"]',
                '.oauth-login-google',
                '.btn-google'
            ];
            
            let googleLoginButton = null;
            for (const selector of googleLoginSelectors) {
                try {
                    googleLoginButton = await page.locator(selector).first();
                    if (await googleLoginButton.isVisible()) {
                        console.log(`✅ Botão Google encontrado: ${selector}`);
                        break;
                    }
                } catch (e) {
                    console.log(`❌ Seletor Google não encontrado: ${selector}`);
                }
            }
            
            if (googleLoginButton && await googleLoginButton.isVisible()) {
                console.log('🖱️ Clicando no login com Google...');
                await googleLoginButton.click();
                await page.waitForLoadState('networkidle');
                await page.screenshot({ path: 'github-03-google-login.png' });
                console.log('📸 Screenshot salvo: github-03-google-login.png');
                
                console.log('⏳ Aguardando login manual do usuário...');
                console.log('👤 Por favor, complete o login com Google manualmente.');
                console.log('🔗 O navegador permanecerá aberto para você fazer o login.');
                
                // Aguardar até que o usuário seja redirecionado de volta para o GitHub
                await page.waitForURL('https://github.com/**', { timeout: 300000 }); // 5 minutos
                
                console.log('✅ Login detectado! Continuando automação...');
                await page.screenshot({ path: 'github-04-logged-in.png' });
                
            } else {
                console.log('❌ Botão de login com Google não encontrado.');
                console.log('📋 Campos disponíveis na página:');
                
                // Listar todos os elementos visíveis
                const visibleElements = await page.locator('a, button, input').all();
                for (let i = 0; i < Math.min(visibleElements.length, 10); i++) {
                    const text = await visibleElements[i].textContent();
                    const tag = await visibleElements[i].evaluate(el => el.tagName);
                    const id = await visibleElements[i].getAttribute('id');
                    const className = await visibleElements[i].getAttribute('class');
                    console.log(`   ${tag}: "${text}" id="${id}" class="${className}"`);
                }
            }
            
        } else {
            console.log('❌ Botão de login não encontrado. Verificando a página atual...');
            const title = await page.title();
            const url = page.url();
            console.log(`📄 Título: ${title}`);
            console.log(`🔗 URL: ${url}`);
        }
        
        // Manter o navegador aberto para interação manual
        console.log('🖥️ Navegador mantido aberto para configuração manual...');
        console.log('📝 Próximos passos a serem realizados manualmente:');
        console.log('   1. Complete o login se necessário');
        console.log('   2. Acesse Settings > Developer settings > Personal access tokens');
        console.log('   3. Configure um novo token para deploy');
        console.log('   4. Configure as chaves SSH se necessário');
        
        // Aguardar entrada do usuário para fechar
        await page.waitForTimeout(600000); // 10 minutos
        
    } catch (error) {
        console.error('❌ Erro durante automação:', error);
        await page.screenshot({ path: 'github-error.png' });
    } finally {
        await browser.close();
        console.log('✅ Automação concluída!');
    }
}

// Executar automação
setupGitHubForDeploy().catch(console.error);