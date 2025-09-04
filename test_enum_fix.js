#!/usr/bin/env node

/**
 * Script para testar se a correção do enum está funcionando
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
    if (data) {
      console.log(`📤 Dados:`, data);
    }
    
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

async function testEnumFix() {
  console.log('🔍 TESTE DA CORREÇÃO DO ENUM\n');
  
  // Teste com ADMIN em uppercase (correto)
  console.log('1️⃣ Testando com ADMIN (uppercase - correto)...');
  const testAdminUpper = {
    cpf: '98765432100',
    nome: 'Admin Teste Upper',
    email: 'admin.upper@teste.com',
    senha: 'teste123',
    tipo: 'ADMIN'
  };
  
  const resultAdminUpper = await makeRequest(`${BACKEND_URL}/api/auth/register`, 'POST', testAdminUpper);
  
  // Teste com admin em lowercase (deve falhar)
  console.log('\n2️⃣ Testando com admin (lowercase - deve falhar)...');
  const testAdminLower = {
    cpf: '11111111111',
    nome: 'Admin Teste Lower',
    email: 'admin.lower@teste.com',
    senha: 'teste123',
    tipo: 'admin'
  };
  
  const resultAdminLower = await makeRequest(`${BACKEND_URL}/api/auth/register`, 'POST', testAdminLower);
  
  // Teste com PROMOTER (correto)
  console.log('\n3️⃣ Testando com PROMOTER (uppercase - correto)...');
  const testPromoter = {
    cpf: '22222222222',
    nome: 'Promoter Teste',
    email: 'promoter@teste.com',
    senha: 'teste123',
    tipo: 'PROMOTER'
  };
  
  const resultPromoter = await makeRequest(`${BACKEND_URL}/api/auth/register`, 'POST', testPromoter);
  
  // Resumo
  console.log('\n📊 RESUMO DOS TESTES:');
  console.log(`ADMIN (uppercase): ${resultAdminUpper.success ? '✅ SUCESSO' : '❌ FALHOU'} (${resultAdminUpper.status})`);
  console.log(`admin (lowercase): ${resultAdminLower.success ? '✅ SUCESSO (inesperado!)' : '❌ FALHOU (esperado)'} (${resultAdminLower.status})`);
  console.log(`PROMOTER (uppercase): ${resultPromoter.success ? '✅ SUCESSO' : '❌ FALHOU'} (${resultPromoter.status})`);
  
  if (resultAdminUpper.success && !resultAdminLower.success && resultPromoter.success) {
    console.log('\n🎉 CORREÇÃO FUNCIONANDO! Frontend deve enviar valores em UPPERCASE.');
  } else {
    console.log('\n⚠️ Verificar se ainda há problemas com a validação do enum.');
  }
}

// Executar teste
testEnumFix().catch(console.error);
