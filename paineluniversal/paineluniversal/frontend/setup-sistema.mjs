import { setupInicial } from '../src/services/api.js';

async function executarSetup() {
  console.log('🚀 Executando setup inicial do sistema...\n');

  try {
    const resultado = await setupInicial();
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
}

executarSetup();
