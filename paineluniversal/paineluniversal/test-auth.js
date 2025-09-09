// Script para testar autenticação
console.log('🔍 Verificando autenticação...');

// Verificar token
const token = localStorage.getItem('token');
console.log('Token:', token);

// Verificar dados do usuário
const userData = localStorage.getItem('user');
console.log('User data:', userData);

// Testar endpoint de eventos diretamente
fetch('https://backend-painel-universal-production.up.railway.app/api/eventos/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}).then(response => {
  console.log('Status da resposta:', response.status);
  return response.text();
}).then(data => {
  console.log('Resposta do servidor:', data);
}).catch(error => {
  console.error('Erro na requisição:', error);
});

// Se não há token, vamos fazer login de teste
if (!token) {
  console.log('🔐 Fazendo login de teste...');
  
  fetch('https://backend-painel-universal-production.up.railway.app/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      cpf: '00000000000',
      senha: 'admin123'
    })
  }).then(response => {
    console.log('Status do login:', response.status);
    return response.json();
  }).then(data => {
    console.log('Resposta do login:', data);
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
      console.log('✅ Token salvo!');
    }
  }).catch(error => {
    console.error('Erro no login:', error);
  });
}
