console.log('🔍 TESTE FINAL DO REGISTRO - CONFIGURAÇÃO CORRETA');

const axios = require('axios');

async function testFinalRegistro() {
    console.log('\n🧪 Testando registro com configuração lowercase (correta)...\n');
    
    try {
        const userData = {
            cpf: '33333333333',
            nome: 'Teste Final Admin',
            email: 'final.admin@teste.com',
            senha: 'teste123',
            tipo: 'admin'  // lowercase conforme backend espera
        };
        
        console.log('📤 Dados enviados:', userData);
        
        const response = await axios.post(
            'https://backend-painel-universal-production.up.railway.app/api/auth/register',
            userData,
            {
                timeout: 30000,
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );
        
        console.log('✅ Status:', response.status);
        console.log('📄 Resposta:', response.data);
        console.log('\n🎉 REGISTRO FUNCIONANDO CORRETAMENTE!');
        
    } catch (error) {
        console.log('❌ Erro:', error.message);
        
        if (error.response) {
            console.log('📊 Status HTTP:', error.response.status);
            console.log('📄 Detalhes:', error.response.data);
        }
        
        if (error.code === 'ECONNABORTED') {
            console.log('⏰ Timeout - possível problema de conectividade');
        }
    }
}

testFinalRegistro().catch(console.error);
