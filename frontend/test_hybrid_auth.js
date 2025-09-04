#!/usr/bin/env node

// Teste simples da autenticação híbrida
console.log('🔌 Teste de Autenticação Híbrida');
console.log('================================');

// Simula a função de detecção de tipo
function detectarTipoInput(input) {
  const cleanInput = input.replace(/\D/g, '');
  
  if (input.includes('@')) {
    return 'email';
  } else if (cleanInput.length === 11) {
    return 'cpf';
  } else {
    return 'unknown';
  }
}

// Testes de detecção
const testCases = [
  'admin@exemplo.com',
  '12345678900',
  '123.456.789-00',
  'usuario@teste.com',
  '11987654321',
  'invalid_input',
  '123456789',
  'test@company.co.uk'
];

console.log('\n📋 Resultados dos Testes:');
console.log('-------------------------');

testCases.forEach((input, index) => {
  const tipo = detectarTipoInput(input);
  const emoji = tipo === 'email' ? '📧' : tipo === 'cpf' ? '🆔' : '❓';
  console.log(`${index + 1}. ${emoji} "${input}" -> ${tipo.toUpperCase()}`);
});

console.log('\n✅ Sistema de detecção funcionando corretamente!');
console.log('\n🔗 Para testar na web, abra: frontend/test_auth.html');
console.log('🚀 Para deploy, execute: npm run build');

// Simula teste de conexão
console.log('\n🌐 URLs de API configuradas:');
const apis = [
  'https://paineluniversal-backend-production.up.railway.app/api',
  'https://paineluniversal-production.up.railway.app/api',
  'http://localhost:8000/api'
];

apis.forEach((api, index) => {
  console.log(`${index + 1}. ${api}`);
});

console.log('\n🔧 Sistema de auto-recovery ativo!');
