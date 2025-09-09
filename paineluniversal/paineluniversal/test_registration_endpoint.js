#!/usr/bin/env node

/**
 * Script para testar especificamente o endpoint de registro que está falhando
 */

const https = require('https');

const BACKEND_URL = 'https://backend-painel-universal-production.up.railway.app';

function makeRequest(url, method = 'GET', data = null) {
  return new Promise((resolve) => {
    const urlObj = new URL(url);
    
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'NodeJS-Test-Script',
        'Origin': 'https://frontend-painel-universal-production.up.railway.app'
      },
      timeout: 15000
    };

    if (data && method !== 'GET') {
      const jsonData = JSON.stringify(data);
      options.headers['Content-Length'] = Buffer.byteLength(jsonData);
    }

    console.log(`🧪 ${method} ${url}`);
    
    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          console.log(`✅ Status: ${res.statusCode}`);
          console.log(`📄 Resposta:`, parsed);
          resolve({ 
            status: res.statusCode, 
            success: res.statusCode < 400, 
            data: parsed,
            headers: res.headers 
          });
        } catch (e) {
          console.log(`✅ Status: ${res.statusCode}`);
          console.log(`📄 Resposta (raw):`, responseData.slice(0, 200));
          resolve({ 
            status: res.statusCode, 
            success: res.statusCode < 400, 
            data: responseData,
            headers: res.headers 
          });
        }
      });
    });
    
    req.on('error', (error) => {
      console.log(`❌ Erro: ${error.message}`);
      resolve({ 
        status: 'ERROR', 
        success: false, 
        error: error.message 
      });
    });
    
    req.on('timeout', () => {
      console.log(`⏰ Timeout`);
      resolve({ 
        status: 'TIMEOUT', 
        success: false, 
        error: 'Timeout' 
      });
      req.destroy();
    });
    
    if (data && method !== 'GET') {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

async function testRegistrationFlow() {
  console.log('🔍 TESTE ESPECÍFICO DO FLUXO DE REGISTRO\n');
  
  // 1. Testar healthcheck
  console.log('1️⃣ Testando healthcheck...');
  const health = await makeRequest(`${BACKEND_URL}/healthz`);
  
  if (!health.success) {
    console.log('❌ Backend não está funcionando básico!');
    return;
  }
  
  // 2. Testar CORS
  console.log('\n2️⃣ Testando CORS...');
  const cors = await makeRequest(`${BACKEND_URL}/api/cors-test`);
  
  // 3. Testar endpoint de registro com dados mínimos
  console.log('\n3️⃣ Testando endpoint de registro...');
  const testUser = {
    cpf: '12345678901',
    nome: 'Teste Usuario',
    email: 'teste@teste.com',
    senha: 'teste123',
    tipo: 'cliente'
  };
  
  const registration = await makeRequest(`${BACKEND_URL}/api/auth/register`, 'POST', testUser);
  
  // 4. Testar se endpoint existe (mesmo que retorne erro)
  console.log('\n4️⃣ Testando se endpoint existe (OPTIONS)...');
  const options = await makeRequest(`${BACKEND_URL}/api/auth/register`, 'OPTIONS');
  
  // 5. Testar login endpoint
  console.log('\n5️⃣ Testando endpoint de login...');
  const loginTest = {
    cpf: '12345678901',
    senha: 'teste123'
  };
  
  const login = await makeRequest(`${BACKEND_URL}/api/auth/login`, 'POST', loginTest);
  
  // Resumo
  console.log('\n📊 RESUMO DOS TESTES:');
  console.log(`Healthcheck: ${health.success ? '✅' : '❌'} (${health.status})`);
  console.log(`CORS Test: ${cors.success ? '✅' : '❌'} (${cors.status})`);
  console.log(`Registration: ${registration.success ? '✅' : '❌'} (${registration.status})`);
  console.log(`Options: ${options.success ? '✅' : '❌'} (${options.status})`);
  console.log(`Login: ${login.success ? '✅' : '❌'} (${login.status})`);
  
  // Análise específica do erro de registro
  if (!registration.success) {
    console.log('\n🔍 ANÁLISE DO ERRO DE REGISTRO:');
    if (registration.status === 500) {
      console.log('💥 ERRO 500: Erro interno do servidor');
      console.log('   Possíveis causas:');
      console.log('   - Problema de conexão com banco de dados');
      console.log('   - Erro na validação dos dados');
      console.log('   - Problema no processo de hash da senha');
      console.log('   - Erro no modelo de usuário');
      
      if (registration.data && registration.data.detail) {
        console.log(`   Detalhes: ${registration.data.detail}`);
      }
    } else if (registration.status === 422) {
      console.log('📝 ERRO 422: Dados inválidos');
      console.log('   O endpoint existe mas os dados não passaram na validação');
    } else if (registration.status === 404) {
      console.log('🔍 ERRO 404: Endpoint não encontrado');
      console.log('   O endpoint /api/auth/register não existe');
    }
  }
}

// Executar teste
testRegistrationFlow().catch(console.error);
