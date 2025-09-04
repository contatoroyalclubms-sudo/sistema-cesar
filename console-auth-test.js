/* 
SCRIPT PARA TESTAR AUTENTICAÇÃO NO CONSOLE DO NAVEGADOR

Copie e cole este código no console do navegador para verificar o estado da autenticação:
*/

console.log('🔍 === TESTE DE AUTENTICAÇÃO ===');

// 1. Verificar localStorage
const token = localStorage.getItem('token');
const userData = localStorage.getItem('user');

console.log('📱 LocalStorage:');
console.log('- Token:', token ? `✅ Existe (${token.length} chars)` : '❌ Não encontrado');
console.log('- User Data:', userData ? '✅ Existe' : '❌ Não encontrado');

// 2. Tentar parsear dados do usuário
if (userData) {
  try {
    const user = JSON.parse(userData);
    console.log('👤 Dados do usuário:', user);
  } catch (e) {
    console.error('❌ Erro ao parsear userData:', e);
  }
}

// 3. Testar endpoint de eventos
if (token) {
  console.log('🌐 Testando endpoint de eventos...');
  
  fetch('https://backend-painel-universal-production.up.railway.app/api/eventos/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log(`📡 Status da resposta: ${response.status}`);
    if (response.status === 401) {
      console.log('❌ Token inválido ou expirado');
    } else if (response.status === 200) {
      console.log('✅ Autenticação funcionando!');
    }
    return response.text();
  })
  .then(data => {
    console.log('📄 Resposta:', data.substring(0, 200));
  })
  .catch(error => {
    console.error('💥 Erro na requisição:', error);
  });
} else {
  console.log('🔐 Fazendo login de teste...');
  
  // Tentar login padrão
  fetch('https://backend-painel-universal-production.up.railway.app/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      cpf: '00000000000',
      senha: 'admin123'
    })
  })
  .then(response => {
    console.log(`🔑 Status do login: ${response.status}`);
    return response.json();
  })
  .then(data => {
    console.log('📋 Resposta do login:', data);
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }
      console.log('✅ Login realizado! Recarregue a página.');
    } else {
      console.log('❌ Login falhou:', data.detail || 'Erro desconhecido');
    }
  })
  .catch(error => {
    console.error('💥 Erro no login:', error);
  });
}

console.log('🔍 === FIM DO TESTE ===');
