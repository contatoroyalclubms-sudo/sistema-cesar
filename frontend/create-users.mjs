/**
 * Script para criar usuários via API do backend em produção
 */

import axios from 'axios';

const API_BASE = 'https://backend-painel-universal-production.up.railway.app';

async function createInitialData() {
  try {
    console.log('🚀 Realizando setup inicial via API...\n');

    // 1. Testar se o backend está funcionando
    console.log('1️⃣ Testando conexão com backend...');
    const healthResponse = await axios.get(`${API_BASE}/healthz`);
    console.log(`✅ Backend OK: ${JSON.stringify(healthResponse.data)}\n`);

    // 2. Executar setup inicial
    console.log('2️⃣ Executando setup inicial...');
    try {
      const setupResponse = await axios.post(`${API_BASE}/setup-inicial`);
      console.log(`✅ Setup realizado com sucesso!`);
      console.log(`📊 Resposta: ${JSON.stringify(setupResponse.data, null, 2)}`);
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('já foi inicializado')) {
        console.log('ℹ️ Sistema já foi inicializado anteriormente');
      } else {
        console.log(`❌ Erro no setup: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
        return;
      }
    }

    // 3. Testar login do admin
    console.log('\n3️⃣ Testando login do admin...');
    try {
      const loginResponse = await axios.post(`${API_BASE}/api/auth/login`, {
        cpf: "00000000000",
        senha: "0000"
      });
      
      if (loginResponse.data.access_token) {
        console.log(`✅ Login funcionando! Token recebido.`);
        console.log(`👤 Usuário: ${loginResponse.data.usuario.nome}`);
        console.log(`🏷️ Tipo: ${loginResponse.data.usuario.tipo}`);
      }
    } catch (error) {
      if (error.response?.status === 202) {
        const codigo = error.response.data.detail.match(/Use: (\d+)/)?.[1];
        console.log(`📱 Código de verificação necessário: ${codigo}`);
        
        // Testar com código
        try {
          const loginComCodigoResponse = await axios.post(`${API_BASE}/api/auth/login`, {
            cpf: "00000000000",
            senha: "0000",
            codigo_verificacao: codigo
          });
          console.log(`✅ Login com código funcionando!`);
          console.log(`👤 Usuário: ${loginComCodigoResponse.data.usuario.nome}`);
        } catch (codeError) {
          console.log(`❌ Erro no login com código: ${codeError.response?.data?.detail || codeError.message}`);
        }
      } else {
        console.log(`❌ Erro no login: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
      }
    }

    console.log('\n🎉 Setup concluído!');
    console.log('\n📋 Credenciais para login no frontend:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('👤 ADMIN:');
    console.log('   CPF: 000.000.000-00 (ou 00000000000)');
    console.log('   Senha: 0000');
    console.log();
    console.log('👤 PROMOTER:');
    console.log('   CPF: 111.111.111-11 (ou 11111111111)');
    console.log('   Senha: promoter123');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('\n🌐 URL do Frontend: https://frontend-painel-universal-production.up.railway.app/login');

  } catch (error) {
    console.error(`❌ Erro geral: ${error.message}`);
  }
}

createInitialData();
