#!/usr/bin/env node

/**
 * Script para diagnosticar problemas de conectividade com o backend
 */

const https = require('https');
const http = require('http');

// URLs para testar
const backendUrls = [
  'https://backend-painel-universal-production.up.railway.app',
  'https://paineluniversal-backend-production.up.railway.app',
  'https://backend-painel-unive-production.up.railway.app',
  'https://painel-universal-backend-production.up.railway.app'
];

const endpoints = ['/healthz', '/api/auth/test', '/docs', '/'];

function testUrl(fullUrl) {
  return new Promise((resolve) => {
    console.log(`🧪 Testando: ${fullUrl}`);
    
    const url = new URL(fullUrl);
    const client = url.protocol === 'https:' ? https : http;
    
    const req = client.request({
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: 'GET',
      timeout: 10000
    }, (res) => {
      console.log(`✅ ${fullUrl} - Status: ${res.statusCode}`);
      resolve({ url: fullUrl, status: res.statusCode, success: true });
    });
    
    req.on('error', (error) => {
      console.log(`❌ ${fullUrl} - Erro: ${error.message}`);
      resolve({ url: fullUrl, status: 'ERROR', success: false, error: error.message });
    });
    
    req.on('timeout', () => {
      console.log(`⏰ ${fullUrl} - Timeout`);
      resolve({ url: fullUrl, status: 'TIMEOUT', success: false, error: 'Timeout' });
      req.destroy();
    });
    
    req.end();
  });
}

async function diagnoseConnectivity() {
  console.log('🔍 DIAGNÓSTICO DE CONECTIVIDADE BACKEND\n');
  
  const results = [];
  
  for (const baseUrl of backendUrls) {
    console.log(`\n📡 Testando base URL: ${baseUrl}`);
    
    for (const endpoint of endpoints) {
      const fullUrl = baseUrl + endpoint;
      const result = await testUrl(fullUrl);
      results.push(result);
      
      // Se encontrou um endpoint funcionando, testar mais endpoints nesta URL
      if (result.success) {
        console.log(`🎯 URL FUNCIONANDO ENCONTRADA: ${baseUrl}`);
        
        // Testar outros endpoints importantes
        const extraEndpoints = ['/api/cors-test', '/api/usuarios/', '/api/eventos/'];
        for (const extra of extraEndpoints) {
          const extraResult = await testUrl(baseUrl + extra);
          results.push(extraResult);
        }
        break;
      }
    }
  }
  
  console.log('\n📊 RESUMO DOS RESULTADOS:');
  const working = results.filter(r => r.success);
  const failing = results.filter(r => !r.success);
  
  console.log(`✅ URLs funcionando: ${working.length}`);
  console.log(`❌ URLs com erro: ${failing.length}`);
  
  if (working.length > 0) {
    console.log('\n🎯 URLs FUNCIONANDO:');
    working.forEach(r => console.log(`   ${r.url} (${r.status})`));
  }
  
  if (failing.length > 0) {
    console.log('\n💥 URLs COM PROBLEMA:');
    failing.forEach(r => console.log(`   ${r.url} (${r.status})`));
  }
  
  // Recomendação
  if (working.length > 0) {
    const baseUrl = working[0].url.split('/')[0] + '//' + working[0].url.split('/')[2];
    console.log(`\n🔧 RECOMENDAÇÃO: Usar a URL base: ${baseUrl}`);
    
    // Gerar código para atualizar frontend
    console.log('\n📝 CÓDIGO PARA CORRIGIR FRONTEND:');
    console.log(`// Em frontend/src/services/api.ts, linha ~40:`);
    console.log(`return '${baseUrl}';`);
    
  } else {
    console.log('\n🚨 PROBLEMA CRÍTICO: Nenhuma URL do backend está funcionando!');
    console.log('   - Verifique se o serviço está rodando no Railway');
    console.log('   - Verifique as configurações de deploy');
    console.log('   - Verifique os logs do Railway');
  }
}

// Executar diagnóstico
diagnoseConnectivity().catch(console.error);
