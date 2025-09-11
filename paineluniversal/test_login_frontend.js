// Script para testar login automaticamente
async function testLogin() {
    console.log('🚀 Iniciando teste de login automático...');
    
    // Navegar para a página de login
    if (!window.location.pathname.includes('/login')) {
        console.log('📍 Navegando para /login...');
        window.location.href = '/login';
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    console.log('📋 Preenchendo formulário de login...');
    
    // Aguardar elementos carregarem
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Preencher CPF
    const cpfInput = document.querySelector('input[placeholder="000.000.000-00"]');
    if (cpfInput) {
        cpfInput.value = '066.012.061-54';
        cpfInput.dispatchEvent(new Event('change', { bubbles: true }));
        console.log('✅ CPF preenchido');
    } else {
        console.error('❌ Campo CPF não encontrado');
        return;
    }
    
    // Preencher senha
    const senhaInput = document.querySelector('input[placeholder="Digite sua senha"]');
    if (senhaInput) {
        senhaInput.value = '101112';
        senhaInput.dispatchEvent(new Event('change', { bubbles: true }));
        console.log('✅ Senha preenchida');
    } else {
        console.error('❌ Campo senha não encontrado');
        return;
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Clicar no botão de login
    const loginButton = document.querySelector('button[type="submit"]');
    if (loginButton) {
        console.log('🔐 Clicando no botão de login...');
        
        // Monitorar mudanças na URL
        const originalUrl = window.location.href;
        let urlChanged = false;
        
        const urlChecker = setInterval(() => {
            if (window.location.href !== originalUrl) {
                urlChanged = true;
                console.log(`🔄 URL mudou de ${originalUrl} para ${window.location.href}`);
                clearInterval(urlChecker);
            }
        }, 100);
        
        // Monitorar storage
        const originalToken = localStorage.getItem('token');
        const originalUsuario = localStorage.getItem('usuario');
        
        const storageChecker = setInterval(() => {
            const newToken = localStorage.getItem('token');
            const newUsuario = localStorage.getItem('usuario');
            
            if (newToken !== originalToken) {
                console.log('🔑 Token alterado:', newToken ? 'Token definido' : 'Token removido');
            }
            
            if (newUsuario !== originalUsuario) {
                console.log('👤 Usuário alterado:', newUsuario ? JSON.parse(newUsuario) : 'Usuário removido');
            }
        }, 100);
        
        loginButton.click();
        
        // Aguardar resultado
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        clearInterval(urlChecker);
        clearInterval(storageChecker);
        
        // Verificar resultado
        const finalToken = localStorage.getItem('token');
        const finalUsuario = localStorage.getItem('usuario');
        const finalUrl = window.location.href;
        
        console.log('📊 Resultado do teste:');
        console.log('  - URL final:', finalUrl);
        console.log('  - Token presente:', !!finalToken);
        console.log('  - Usuário presente:', !!finalUsuario);
        
        if (finalUsuario) {
            try {
                const userData = JSON.parse(finalUsuario);
                console.log('  - Dados do usuário:', userData);
            } catch (e) {
                console.log('  - Erro ao parsear usuário:', e);
            }
        }
        
        // Verificar se ainda está na página de login
        if (finalUrl.includes('/login')) {
            console.log('❌ PROBLEMA: Ainda está na página de login!');
            
            // Verificar se há erros no console
            console.log('🔍 Verificando se há erros...');
            
            // Tentar verificar o estado do AuthContext
            if (window.React && window.React.useContext) {
                console.log('🔍 Tentando acessar contexto de autenticação...');
            }
        } else if (finalUrl.includes('/app')) {
            console.log('✅ SUCESSO: Redirecionado para área autenticada!');
        } else {
            console.log('⚠️ RESULTADO INESPERADO: URL final não é nem login nem app');
        }
        
    } else {
        console.error('❌ Botão de login não encontrado');
    }
}

// Executar teste
testLogin().catch(console.error);
