import axios from 'axios';

const API_BASE = 'https://backend-painel-universal-production.up.railway.app';

async function executarSetup() {
  console.log('🚀 Executando setup inicial do sistema...\n');

  try {
    const response = await axios.post(`${API_BASE}/setup-inicial`);
    const resultado = response.data;
    
    console.log('✅ Setup realizado com sucesso!');
    console.log('📊 Resultado:', JSON.stringify(resultado, null, 2));
    
    console.log('\n🎯 CREDENCIAIS CRIADAS:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    if (resultado.usuarios_criados) {
      resultado.usuarios_criados.forEach((usuario, index) => {
        console.log(`👤 ${usuario.tipo.toUpperCase()}:`);
        console.log(`   CPF: ${usuario.cpf}`);
        console.log(`   Nome: ${usuario.nome}`);
        console.log(`   Senha: ${usuario.senha}`);
        if (index < resultado.usuarios_criados.length - 1) console.log('');
      });
    }
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('\n🌐 LINKS DO SISTEMA:');
    console.log('Frontend: https://frontend-painel-universal-production.up.railway.app/login');
    console.log('Backend API: https://backend-painel-universal-production.up.railway.app/docs');
    
  } catch (error) {
    if (error.response?.data?.message?.includes('já foi inicializado')) {
      console.log('ℹ️ Sistema já foi inicializado anteriormente');
      
      console.log('\n🎯 CREDENCIAIS PADRÃO:');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('👤 ADMIN:');
      console.log('   CPF: 000.000.000-00');
      console.log('   Senha: 0000');
      console.log('');
      console.log('👤 PROMOTER:');
      console.log('   CPF: 111.111.111-11');
      console.log('   Senha: promoter123');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    } else {
      console.error('❌ Erro no setup:', error.response?.data || error.message);
    }
  }

  console.log('\n📝 FUNCIONALIDADES DISPONÍVEIS:');
  console.log('• ✅ Login/Logout com autenticação JWT');
  console.log('• ✅ Cadastro de novos usuários na página de login');
  console.log('• ✅ Módulo completo de gerenciamento de usuários (/usuarios)');
  console.log('• ✅ Dashboard com estatísticas em tempo real');
  console.log('• ✅ Gestão de eventos e listas');
  console.log('• ✅ Sistema de check-in inteligente');
  console.log('• ✅ PDV para vendas');
  console.log('• ✅ Sistema financeiro');
  console.log('• ✅ Gamificação e ranking');
  console.log('• ✅ Todas as rotas corrigidas para produção');
}

executarSetup();
