const { chromium } = require('playwright');

async function automacaoNavegadorCompleta() {
    console.log('🚀 AUTOMAÇÃO NAVEGADOR NORMAL - MISSÃO COMPLETA');
    console.log('=' * 60);

    let browser;
    let page;

    try {
        console.log('🌐 Abrindo navegador normal (visível)...');
        browser = await chromium.launch({
            headless: false,
            slowMo: 1000,
            args: ['--start-maximized', '--disable-web-security']
        });

        page = await browser.newPage();
        await page.setViewportSize({ width: 1920, height: 1080 });

        console.log('📍 Navegando para GitHub...');
        await page.goto('https://github.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
        
        await page.screenshot({ path: 'github-01-homepage.png' });
        console.log('📸 Screenshot salvo: github-01-homepage.png');

        console.log('🔍 Aguardando página carregar completamente...');
        await page.waitForTimeout(3000);

        console.log('🔍 Procurando botão Sign in...');
        
        // Estratégia mais robusta para encontrar Sign in
        try {
            // Tentar múltiplos seletores
            const signInButton = await page.locator('text=Sign in').first();
            if (await signInButton.isVisible()) {
                console.log('✅ Encontrado botão "Sign in" por texto');
                await signInButton.click();
            } else {
                // Tentar por href
                await page.click('a[href="/login"]');
                console.log('✅ Clicou em Sign in via href');
            }
        } catch (error) {
            console.log('⚠️ Botão não encontrado automaticamente, navegando direto para login...');
            await page.goto('https://github.com/login', { waitUntil: 'domcontentloaded' });
        }

        console.log('⏳ Aguardando página de login...');
        await page.waitForTimeout(3000);
        await page.screenshot({ path: 'github-02-login-page.png' });
        console.log('📸 Screenshot: github-02-login-page.png');

        console.log('📧 Campos de login detectados. Continuando automação...');
        
        // Verificar se existem campos de login
        const loginField = await page.locator('#login_field').first();
        const passwordField = await page.locator('#password').first();
        
        if (await loginField.isVisible() && await passwordField.isVisible()) {
            console.log('✅ Página de login carregada corretamente!');
            
            console.log('ℹ️ NOTA: Para completar o login, use as credenciais:');
            console.log('   📧 Email: contato.royalclubms@gmail.com');
            console.log('   🔐 Senha: 352162Cl');
            
            // Preencher campos automaticamente
            await loginField.fill('contato.royalclubms@gmail.com');
            await passwordField.fill('352162Cl');
            
            console.log('✅ Campos preenchidos automaticamente!');
            console.log('🔘 Clique em "Sign in" no navegador para continuar...');
            
            // Aguardar login manual ou automático
            await page.waitForTimeout(5000);
            
            // Tentar fazer login automaticamente
            try {
                await page.click('input[type="submit"]');
                console.log('🔐 Login enviado automaticamente!');
            } catch (e) {
                console.log('⚠️ Login manual necessário - clique no botão Sign in');
            }
        }

        console.log('⏳ Aguardando processamento... (30 segundos)');
        await page.waitForTimeout(30000);

        console.log('📁 Navegando para repositório sistema-cesar...');
        await page.goto('https://github.com/contatoroyalclubms-sudo/sistema-cesar', {
            waitUntil: 'domcontentloaded',
            timeout: 30000
        });

        await page.screenshot({ path: 'github-03-repository.png' });
        console.log('📸 Screenshot: github-03-repository.png');

        console.log('🎉 NAVEGADOR ABERTO E CONFIGURADO!');
        console.log('📋 STATUS:');
        console.log('   ✅ Navegador normal aberto');
        console.log('   ✅ GitHub acessado');
        console.log('   ✅ Página de login preparada');
        console.log('   ✅ Repositório acessível');
        
        console.log('⏳ Navegador permanecerá aberto para configuração manual...');
        console.log('🔧 Próximo passo: Configurar Git local');

        // Manter aberto indefinidamente
        console.log('🌐 Navegador mantido aberto para interação...');

    } catch (error) {
        console.error('❌ Erro:', error.message);
        if (page) {
            await page.screenshot({ path: 'erro-automacao.png' });
            console.log('📸 Screenshot do erro salvo');
        }
    }
    // NÃO fechar o browser - mantê-lo aberto
}

// Executar
automacaoNavegadorCompleta().catch(console.error);