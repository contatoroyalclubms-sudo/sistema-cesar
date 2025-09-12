#!/usr/bin/env node
// Teste completo do sistema

const axios = require('axios');

async function testarSistema() {
    console.log('🧪 Testando Sistema Completo...\n');
    
    const testes = [
        { nome: 'Backend Health', url: 'http://localhost:8000/api/health' },
        { nome: 'Frontend', url: 'http://localhost:5173' },
        { nome: 'MEEP Service', url: 'http://localhost:3333/health' },
        { nome: 'Login Endpoint', url: 'http://localhost:8000/api/auth/login', method: 'POST' }
    ];
    
    for (const teste of testes) {
        try {
            const response = await axios({
                method: teste.method || 'GET',
                url: teste.url,
                timeout: 5000
            });
            console.log(`✅ ${teste.nome}: OK (Status ${response.status})`);
        } catch (error) {
            console.log(`❌ ${teste.nome}: FALHOU (${error.message})`);
        }
    }
}

testarSistema();
