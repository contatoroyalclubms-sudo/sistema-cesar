import axios from 'axios';

const API_BASE = 'https://backend-painel-universal-production.up.railway.app';

async function setupSimples() {
  console.log('🔧 Setup simples do banco de dados...\n');

  try {
    // 1. Testar conexão
    console.log('1️⃣ Testando backend...');
    const health = await axios.get(`${API_BASE}/healthz`);
    console.log(`✅ Backend funcionando: ${health.data.environment}\n`);

    // 2. Tentar criar empresa usando a API existente
    console.log('2️⃣ Criando empresa...');
    try {
      const empresaResponse = await axios.post(`${API_BASE}/api/empresas/`, {
        nome: "Painel Universal - Demo",
        cnpj: "00000000000100",
        email: "contato@demo.com",
        telefone: "(11) 99999-9999",
        endereco: "São Paulo, SP"
      });
      console.log(`✅ Empresa criada: ${empresaResponse.data.nome}`);
    } catch (error) {
      if (error.response?.status === 400) {
        console.log('ℹ️ Empresa já existe ou erro de validação');
      } else {
        console.log(`⚠️ Erro: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
      }
    }

    // 3. Tentar criar usuário admin usando a API existente
    console.log('\n3️⃣ Criando admin...');
    try {
      const adminResponse = await axios.post(`${API_BASE}/api/usuarios/`, {
        cpf: "00000000000",
        nome: "Admin Sistema",
        email: "admin@demo.com",
        telefone: "(11) 99999-0000",
        senha: "0000",
        tipo: "admin",
        empresa_id: 1
      });
      console.log(`✅ Admin criado: ${adminResponse.data.nome}`);
    } catch (error) {
      console.log(`⚠️ Erro admin: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
    }

    // 4. Testar login
    console.log('\n4️⃣ Testando login...');
    try {
      const loginResponse = await axios.post(`${API_BASE}/api/auth/login`, {
        cpf: "00000000000",
        senha: "0000"
      });
      
      if (loginResponse.data.access_token) {
        console.log(`✅ Login OK! Usuário: ${loginResponse.data.usuario.nome}`);
      }
    } catch (error) {
      if (error.response?.status === 202) {
        console.log(`📱 Precisa de código 2FA (isso é normal)`);
      } else {
        console.log(`❌ Login falhou: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
      }
    }

    console.log('\n🎯 CREDENCIAIS PARA USO:');
    console.log('CPF: 00000000000');
    console.log('Senha: 0000');
    console.log('\n🌐 Frontend: https://frontend-painel-universal-production.up.railway.app/login');

  } catch (error) {
    console.error(`❌ Erro geral: ${error.message}`);
  }
}

setupSimples();
