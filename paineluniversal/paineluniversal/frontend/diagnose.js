#!/usr/bin/env node

/**
 * Script de diagnóstico para testar conectividade entre frontend e backend
 */

import axios from 'axios';

const BACKEND_URLS = [
  'https://backend-painel-universal-production.up.railway.app/healthz',
  'https://backend-painel-universal-production.up.railway.app/api/eventos/',
  'https://backend-painel-universal-production.up.railway.app/api/empresas/',
  'https://backend-painel-universal-production.up.railway.app/api/dashboard/resumo',
  'https://backend-painel-universal-production.up.railway.app/docs'
];

async function testUrl(url) {
  try {
    console.log(`🧪 Testando: ${url}`);
    const response = await axios.get(url, { timeout: 10000 });
    console.log(`✅ Sucesso: ${response.status} - ${JSON.stringify(response.data)}`);
    return true;
  } catch (error) {
    console.log(`❌ Erro: ${error.code || error.response?.status} - ${error.message}`);
    return false;
  }
}

async function diagnose() {
  console.log('🔍 Iniciando diagnóstico de conectividade...\n');
  
  for (const url of BACKEND_URLS) {
    await testUrl(url);
    console.log('');
  }
  
  console.log('🏁 Diagnóstico concluído!');
}

diagnose().catch(console.error);
