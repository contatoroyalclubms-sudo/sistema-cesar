const axios = require('axios');

async function testarAPI() {
  console.log('🧪 TESTE DIRETO DA API');
  console.log('=======================\n');
  
  const API_URL = 'http://localhost:8003';
  
  try {
    // 1. Testar health check
    console.log('1️⃣ Testando health check...');
    try {
      const health = await axios.get(`${API_URL}/api/health`);
      console.log('   ✅ API está rodando:', health.data);
    } catch (e) {
      console.log('   ❌ Health check falhou:', e.message);
    }
    
    // 2. Fazer login
    console.log('\n2️⃣ Fazendo login...');
    let token = null;
    try {
      const login = await axios.post(`${API_URL}/api/auth/login`, {
        cpf: '00000000000',
        senha: '0000'
      });
      token = login.data.access_token || login.data.token;
      console.log('   ✅ Login bem sucedido');
      console.log('   Token:', token ? token.substring(0, 20) + '...' : 'Não recebido');
    } catch (e) {
      console.log('   ❌ Login falhou:', e.response?.data || e.message);
    }
    
    // Configurar headers com token
    const config = token ? {
      headers: { Authorization: `Bearer ${token}` }
    } : {};
    
    // 3. Listar eventos
    console.log('\n3️⃣ Listando eventos...');
    try {
      const eventos = await axios.get(`${API_URL}/api/eventos/`, config);
      console.log('   ✅ Eventos listados:', eventos.data.length || 0, 'eventos');
      if (eventos.data.length > 0) {
        console.log('   Primeiro evento:', eventos.data[0].nome);
      }
    } catch (e) {
      console.log('   ❌ Listar eventos falhou:', e.response?.status, e.response?.data || e.message);
    }
    
    // 4. Criar novo evento
    console.log('\n4️⃣ Criando novo evento...');
    
    const agora = new Date();
    const novoEvento = {
      nome: 'Evento Teste API',
      descricao: 'Teste direto via API',
      local: 'Centro de Convenções',
      endereco: 'Rua Teste, 123',
      // Datas com intervalos válidos
      data_inicio_vendas: new Date(agora.getTime() + 30 * 60 * 1000).toISOString(),
      data_fim_vendas: new Date(agora.getTime() + 80 * 60 * 1000).toISOString(),
      data_inicio_evento: new Date(agora.getTime() + 90 * 60 * 1000).toISOString(),
      data_fim_evento: new Date(agora.getTime() + 270 * 60 * 1000).toISOString(),
      // Manter compatibilidade
      data_evento: new Date(agora.getTime() + 90 * 60 * 1000).toISOString(),
      capacidade_maxima: 500,
      limite_idade: 18
    };
    
    console.log('   Dados do evento:');
    console.log('   - Nome:', novoEvento.nome);
    console.log('   - Local:', novoEvento.local);
    console.log('   - Início vendas:', new Date(novoEvento.data_inicio_vendas).toLocaleString());
    console.log('   - Fim vendas:', new Date(novoEvento.data_fim_vendas).toLocaleString());
    console.log('   - Início evento:', new Date(novoEvento.data_inicio_evento).toLocaleString());
    console.log('   - Fim evento:', new Date(novoEvento.data_fim_evento).toLocaleString());
    
    try {
      const response = await axios.post(`${API_URL}/api/eventos/`, novoEvento, config);
      console.log('\n   ✅ EVENTO CRIADO COM SUCESSO!');
      console.log('   ID do evento:', response.data.id);
      console.log('   Nome:', response.data.nome);
    } catch (e) {
      console.log('\n   ❌ ERRO AO CRIAR EVENTO!');
      console.log('   Status:', e.response?.status);
      console.log('   Erro:', e.response?.data?.detail || e.response?.data || e.message);
      
      if (e.response?.data?.detail) {
        console.log('\n   📝 Detalhes do erro:');
        if (typeof e.response.data.detail === 'string') {
          console.log('   ', e.response.data.detail);
        } else if (Array.isArray(e.response.data.detail)) {
          e.response.data.detail.forEach(err => {
            console.log('   -', err.msg || err.message || err);
          });
        }
      }
    }
    
    // 5. Verificar endpoints disponíveis
    console.log('\n5️⃣ Verificando endpoints disponíveis...');
    try {
      const docs = await axios.get(`${API_URL}/docs`);
      console.log('   ✅ Documentação da API disponível em:', `${API_URL}/docs`);
    } catch (e) {
      console.log('   ❌ Documentação não disponível');
    }
    
  } catch (error) {
    console.error('\n❌ Erro geral:', error.message);
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('📊 RESUMO DO TESTE');
  console.log('='.repeat(50));
  console.log('\nPROBLEMAS IDENTIFICADOS:');
  console.log('1. Backend auth_server.py tem funcionalidades limitadas');
  console.log('2. Endpoint /api/eventos pode não estar implementado');
  console.log('3. Validação de datas pode estar muito restritiva');
  console.log('\nSOLUÇÕES NECESSÁRIAS:');
  console.log('1. Implementar endpoint completo de eventos no auth_server.py');
  console.log('2. Ou usar o main.py completo (corrigindo os imports)');
  console.log('3. Ajustar validação de datas para ser mais flexível');
}

testarAPI();