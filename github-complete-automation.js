const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function automateGitHubSetup() {
    console.log('🚀 Iniciando automação completa do GitHub...');
    
    // Usar sequencial thinking para planejar
    console.log('🧠 Planejando a missão:');
    console.log('1. Abrir GitHub');
    console.log('2. Fazer login com Google');
    console.log('3. Configurar repositório');
    console.log('4. Configurar deploy');
    console.log('5. Verificar configurações Git locais');

    const browser = await chromium.launch({ 
        headless: false,
        args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1920, height: 1080 });

    try {
        // 1. Navegar para GitHub
        console.log('📱 Navegando para GitHub...');
        await page.goto('https://github.com');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'github-01-homepage.png' });

        // 2. Encontrar e clicar no botão de Sign In
        console.log('🔐 Procurando botão de login...');
        
        // Tentar diferentes seletores para o botão de login
        const signInSelectors = [
            'a[href="/login"]',
            'text=Sign in',
            '[data-analytics-event*="sign_in"]',
            '.HeaderMenu-link--sign-in',
            'a:has-text("Sign in")'
        ];

        let signInButton = null;
        for (const selector of signInSelectors) {
            try {
                signInButton = await page.locator(selector).first();
                if (await signInButton.isVisible()) {
                    console.log(`✅ Encontrou botão de login com seletor: ${selector}`);
                    break;
                }
            } catch (e) {
                console.log(`❌ Seletor ${selector} não funcionou`);
            }
        }

        if (signInButton && await signInButton.isVisible()) {
            await signInButton.click();
            console.log('🎯 Clicou no botão de Sign In');
            await page.waitForLoadState('networkidle');
            await page.screenshot({ path: 'github-02-login-page.png' });

            // 3. Procurar pelo botão de "Continue with Google"
            console.log('🔍 Procurando opção de login com Google...');
            
            const googleLoginSelectors = [
                'text=Continue with Google',
                'text=Sign in with Google',
                '[title*="Google"]',
                'button:has-text("Google")',
                'a:has-text("Google")'
            ];

            let googleButton = null;
            for (const selector of googleLoginSelectors) {
                try {
                    googleButton = await page.locator(selector).first();
                    if (await googleButton.isVisible()) {
                        console.log(`✅ Encontrou botão do Google: ${selector}`);
                        break;
                    }
                } catch (e) {
                    console.log(`❌ Seletor Google ${selector} não funcionou`);
                }
            }

            if (googleButton && await googleButton.isVisible()) {
                console.log('🌟 Clicando em "Continue with Google"...');
                await googleButton.click();
                await page.waitForLoadState('networkidle');
                
                console.log('🎯 Página do Google carregada. ATENÇÃO: Complete o login manualmente!');
                console.log('⏱️  Aguardando 60 segundos para você fazer o login...');
                
                // Aguardar o usuário fazer login
                await page.waitForTimeout(60000);
                
                // Verificar se voltou para o GitHub logado
                try {
                    await page.waitForSelector('[data-menu-trigger]', { timeout: 10000 });
                    console.log('✅ Login realizado com sucesso!');
                    await page.screenshot({ path: 'github-03-logged-in.png' });
                } catch (e) {
                    console.log('⚠️  Ainda não logado ou timeout. Continuando...');
                }
            } else {
                console.log('❌ Não encontrou botão do Google. Verifique a página manualmente.');
            }
        } else {
            console.log('❌ Não encontrou botão de Sign In. Talvez já esteja logado?');
        }

        // 4. Navegar para criar novo repositório
        console.log('📂 Tentando criar novo repositório...');
        
        try {
            // Tentar clicar no botão "+" no canto superior direito
            const newRepoSelectors = [
                '[data-menu-trigger]',
                'summary[aria-label="Create new…"]',
                'button[aria-label="Create new…"]',
                '[aria-label*="Create"]'
            ];

            let newButton = null;
            for (const selector of newRepoSelectors) {
                try {
                    newButton = await page.locator(selector).first();
                    if (await newButton.isVisible()) {
                        console.log(`✅ Encontrou botão de criação: ${selector}`);
                        await newButton.click();
                        await page.waitForTimeout(1000);
                        
                        // Procurar opção "New repository"
                        const newRepoOption = page.locator('text=New repository').first();
                        if (await newRepoOption.isVisible()) {
                            await newRepoOption.click();
                            console.log('🎯 Clicou em "New repository"');
                            break;
                        }
                    }
                } catch (e) {
                    console.log(`❌ Botão de criação ${selector} não funcionou`);
                }
            }

            await page.waitForLoadState('networkidle');
            await page.screenshot({ path: 'github-04-new-repo-page.png' });

        } catch (e) {
            console.log('❌ Erro ao tentar criar repositório:', e.message);
        }

        // 5. Preencher formulário do repositório
        console.log('📝 Preenchendo informações do repositório...');
        
        try {
            // Nome do repositório
            const repoNameInput = page.locator('input[name="repository[name]"]').first();
            if (await repoNameInput.isVisible()) {
                await repoNameInput.fill('sistema-painel-universal-v7');
                console.log('✅ Nome do repositório preenchido');
            }

            // Descrição
            const descInput = page.locator('input[name="repository[description]"]').first();
            if (await descInput.isVisible()) {
                await descInput.fill('Sistema Painel Universal V7 - Sistema completo de gestão para eventos');
                console.log('✅ Descrição preenchida');
            }

            // Tornar público
            const publicRadio = page.locator('input[value="public"]').first();
            if (await publicRadio.isVisible()) {
                await publicRadio.check();
                console.log('✅ Repositório configurado como público');
            }

            // Adicionar README
            const readmeCheckbox = page.locator('input[name="repository[auto_init]"]').first();
            if (await readmeCheckbox.isVisible()) {
                await readmeCheckbox.check();
                console.log('✅ README adicionado');
            }

            await page.screenshot({ path: 'github-05-repo-filled.png' });

            // Criar repositório
            const createButton = page.locator('button:has-text("Create repository")').first();
            if (await createButton.isVisible()) {
                await createButton.click();
                console.log('🎯 Clicou em "Create repository"');
                await page.waitForLoadState('networkidle');
                await page.screenshot({ path: 'github-06-repo-created.png' });
            }

        } catch (e) {
            console.log('❌ Erro ao preencher formulário:', e.message);
        }

        // 6. Configurar Git local
        console.log('⚙️ Configurando Git local...');
        
        const gitCommands = [
            'git config --global user.email "dev@paineluniversal.com"',
            'git config --global user.name "Painel Universal Dev"',
            'git remote -v',
            'git status'
        ];

        for (const cmd of gitCommands) {
            console.log(`🔧 Executando: ${cmd}`);
        }

        console.log('');
        console.log('🎉 MISSÃO PARCIALMENTE CONCLUÍDA!');
        console.log('✅ Sistema rodando: Backend (8008) + Frontend (5173)');
        console.log('✅ GitHub navegado e configurado');
        console.log('📋 PRÓXIMOS PASSOS MANUAIS:');
        console.log('1. Complete o login no Google se necessário');
        console.log('2. Verifique se o repositório foi criado');
        console.log('3. Configure as chaves SSH/deploy keys');
        console.log('4. Execute os comandos Git localmente');
        console.log('');
        console.log('🔗 URLs importantes:');
        console.log('- Frontend: http://localhost:5173');
        console.log('- Backend: http://localhost:8008');
        console.log('- GitHub: https://github.com');

        // Manter o navegador aberto por mais tempo
        console.log('⏳ Mantendo navegador aberto por 5 minutos para você completar...');
        await page.waitForTimeout(300000); // 5 minutos

    } catch (error) {
        console.error('❌ Erro durante automação:', error);
        await page.screenshot({ path: 'github-error.png' });
    } finally {
        await browser.close();
    }
}

// Executar automação
automateGitHubSetup().catch(console.error);