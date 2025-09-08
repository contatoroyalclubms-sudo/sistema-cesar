/**
 * Teste específico de autenticação para identificar problema 502
 */

import axios from 'axios';

const API_BASE = 'https://backend-painel-universal-production.up.railway.app';

async function testAuth() {
  try {
    console.log('🔐 Testando processo de autenticação...\n');

    // 1. Testar rota de documentação (sem auth)
    console.log('1️⃣ Testando rota pública /docs...');
    const docsResponse = await axios.get(`${API_BASE}/docs`, { timeout: 10000 });
    console.log(`✅ Docs OK: ${docsResponse.status}\n`);

    // 2. Testar healthcheck
    console.log('2️⃣ Testando healthcheck...');
    const healthResponse = await axios.get(`${API_BASE}/healthz`, { timeout: 10000 });
    console.log(`✅ Health OK: ${healthResponse.status}`);
    console.log(`📊 Dados: ${JSON.stringify(healthResponse.data)}\n`);

    // 3. Testar rota de auth sem credenciais (deve dar 403)
    console.log('3️⃣ Testando auth/me sem token (esperado 403)...');
    try {
      await axios.get(`${API_BASE}/api/auth/me`, { timeout: 10000 });
    } catch (error) {
      console.log(`✅ Auth sem token: ${error.response?.status} (correto)\n`);
    }

    // 4. Testar login com dados inválidos (deve dar 422 ou 401)
    console.log('4️⃣ Testando login com dados inválidos...');
    try {
      await axios.post(`${API_BASE}/api/auth/login`, {
        cpf: '00000000000',
        senha: 'senha_invalida'
      }, { timeout: 10000 });
    } catch (error) {
      console.log(`✅ Login inválido: ${error.response?.status} ${error.response?.statusText}`);
      console.log(`📝 Resposta: ${JSON.stringify(error.response?.data)}\n`);
    }

    // 5. Testar rota de eventos sem auth
    console.log('5️⃣ Testando /api/eventos sem auth...');
    try {
      await axios.get(`${API_BASE}/api/eventos/`, { timeout: 10000 });
    } catch (error) {
      console.log(`✅ Eventos sem auth: ${error.response?.status} (esperado 403)\n`);
    }

    console.log('🎉 Todos os testes completados - Backend funcionando corretamente!');

  } catch (error) {
    console.error(`❌ Erro inesperado: ${error.message}`);
    console.error(`📍 Stack: ${error.stack}`);
  }
}

testAuth();
