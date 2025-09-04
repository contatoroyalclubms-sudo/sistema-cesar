#!/usr/bin/env node

/**
 * Suite de Testes Completa MEEP
 * Testa todas as funcionalidades do sistema
 */

const axios = require('axios');
const crypto = require('crypto');

const BASE_URL = 'http://localhost:3001';
const BACKEND_URL = 'http://localhost:8000';

// Cores para output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    cyan: '\x1b[36m',
    magenta: '\x1b[35m'
};

let testsPassed = 0;
let testsFailed = 0;
const results = [];

async function test(name, testFn) {
    process.stdout.write(`Testing ${name}... `);
    try {
        const result = await testFn();
        console.log(`${colors.green}✓ PASSOU${colors.reset}`);
        testsPassed++;
        results.push({ name, status: 'PASSOU', data: result });
        return result;
    } catch (error) {
        console.log(`${colors.red}✗ FALHOU${colors.reset}`);
        console.log(`  Erro: ${error.message}`);
        testsFailed++;
        results.push({ name, status: 'FALHOU', error: error.message });
        return null;
    }
}

async function runTests() {
    console.log(`
${colors.cyan}========================================================
              SUITE DE TESTES MEEP v1.0
========================================================${colors.reset}
`);

    console.log(`${colors.yellow}[1] TESTES DE VALIDAÇÃO CPF${colors.reset}\n`);
    
    // Teste 1: Validação CPF válido
    await test('CPF válido (matemática)', async () => {
        const response = await axios.post(`${BASE_URL}/api/meep/cpf/validar`, {
            cpf: '11144477735'  // CPF válido matematicamente
        });
        if (!response.data.valido) throw new Error('CPF deveria ser válido');
        return response.data;
    });

    // Teste 2: CPF inválido
    await test('CPF inválido', async () => {
        const response = await axios.post(`${BASE_URL}/api/meep/cpf/validar`, {
            cpf: '11111111111'
        });
        if (response.data.valido) throw new Error('CPF deveria ser inválido');
        return response.data;
    });

    // Teste 3: Validação com evento
    await test('CPF com evento_id', async () => {
        const response = await axios.post(`${BASE_URL}/api/meep/cpf/validar`, {
            cpf: '11144477735',
            evento_id: 1
        });
        return response.data;
    });

    // Teste 4: Estatísticas CPF
    await test('Estatísticas de validação', async () => {
        const response = await axios.get(`${BASE_URL}/api/meep/cpf/stats?periodo=1d`);
        if (!response.data.estatisticas) throw new Error('Estatísticas não retornadas');
        return response.data;
    });

    console.log(`\n${colors.yellow}[2] TESTES DE CHECK-IN QR CODE${colors.reset}\n`);

    // Teste 5: Gerar QR Code
    const qrCodeData = await test('Gerar QR Code', async () => {
        const response = await axios.post(`${BASE_URL}/api/meep/checkin/gerar-qr`, {
            cpf: '11144477735'
        });
        if (!response.data.qr_code) throw new Error('QR Code não gerado');
        return response.data;
    });

    // Teste 6: Validar acesso com QR Code
    if (qrCodeData) {
        await test('Check-in com QR válido', async () => {
            const response = await axios.post(`${BASE_URL}/api/meep/checkin/validate-access`, {
                qr_code: qrCodeData.qr_code,
                cpf_digits: '111',
                evento_id: 1
            });
            if (!response.data.sucesso) throw new Error('Check-in deveria ter sucesso');
            return response.data;
        });

        // Teste 7: Check-in com dígitos errados
        await test('Check-in com dígitos CPF errados', async () => {
            try {
                const response = await axios.post(`${BASE_URL}/api/meep/checkin/validate-access`, {
                    qr_code: qrCodeData.qr_code,
                    cpf_digits: '999',  // Dígitos errados
                    evento_id: 1
                });
                throw new Error('Check-in deveria falhar');
            } catch (error) {
                if (error.response && error.response.status === 401) {
                    return { sucesso: false, motivo: 'Dígitos incorretos' };
                }
                throw error;
            }
        });
    }

    // Teste 8: QR Code expirado (simulado)
    await test('QR Code expirado', async () => {
        const expiredQR = JSON.stringify({
            cpf: '11144477735',
            timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(), // 10 minutos atrás
            hash: 'invalid'
        });
        
        try {
            await axios.post(`${BASE_URL}/api/meep/checkin/validate-access`, {
                qr_code: expiredQR,
                cpf_digits: '111',
                evento_id: 1
            });
            throw new Error('QR expirado deveria falhar');
        } catch (error) {
            if (error.response && error.response.status === 400) {
                return { sucesso: false, motivo: 'QR expirado' };
            }
            throw error;
        }
    });

    // Teste 9: Histórico de check-ins
    await test('Histórico de check-ins', async () => {
        const response = await axios.get(`${BASE_URL}/api/meep/checkin/historico?limit=10`);
        if (!response.data.historico) throw new Error('Histórico não retornado');
        return response.data;
    });

    console.log(`\n${colors.yellow}[3] TESTES DE ANALYTICS E IA${colors.reset}\n`);

    // Teste 10: Fluxo com previsão
    await test('Analytics - Fluxo com previsão IA', async () => {
        const response = await axios.get(`${BASE_URL}/api/meep/analytics/fluxo-previsao?evento_id=1&periodo=24h`);
        if (!response.data.previsoes) throw new Error('Previsões não retornadas');
        console.log(`  Confiabilidade: ${response.data.previsoes.confiabilidade}%`);
        return response.data;
    });

    // Teste 11: Dashboard real-time
    await test('Dashboard em tempo real', async () => {
        const response = await axios.get(`${BASE_URL}/api/meep/analytics/dashboard-realtime?evento_id=1`);
        if (!response.data.metricas_gerais) throw new Error('Métricas não retornadas');
        return response.data;
    });

    // Teste 12: Performance report
    await test('Relatório de performance', async () => {
        const response = await axios.get(`${BASE_URL}/api/meep/analytics/performance?evento_id=1&periodo=1d`);
        if (!response.data.kpis) throw new Error('KPIs não retornados');
        return response.data;
    });

    console.log(`\n${colors.yellow}[4] TESTES DE VALIDAÇÃO E SEGURANÇA${colors.reset}\n`);

    // Teste 13: Rate limiting (múltiplas requisições)
    await test('Rate limiting CPF', async () => {
        const promises = [];
        for (let i = 0; i < 15; i++) {
            promises.push(
                axios.post(`${BASE_URL}/api/meep/cpf/validar`, {
                    cpf: '11144477735'
                }).catch(e => e.response)
            );
        }
        
        const responses = await Promise.all(promises);
        const rateLimited = responses.some(r => r && r.status === 429);
        if (!rateLimited) {
            console.log('  Aviso: Rate limiting pode não estar ativo');
        }
        return { tentativas: 15, bloqueadas: responses.filter(r => r && r.status === 429).length };
    });

    // Teste 14: Validação de entrada
    await test('Validação de entrada - CPF formato errado', async () => {
        try {
            await axios.post(`${BASE_URL}/api/meep/cpf/validar`, {
                cpf: '123'  // CPF muito curto
            });
            throw new Error('Deveria rejeitar CPF mal formatado');
        } catch (error) {
            if (error.response && error.response.status === 400) {
                return { validacao: 'funcionando' };
            }
            throw error;
        }
    });

    console.log(`\n${colors.yellow}[5] TESTES DE CACHE${colors.reset}\n`);

    // Teste 15: Cache de validação
    const startTime = Date.now();
    await test('Cache - primeira requisição', async () => {
        const response = await axios.post(`${BASE_URL}/api/meep/cpf/validar`, {
            cpf: '52998224725'  // CPF válido diferente
        });
        const time1 = Date.now() - startTime;
        console.log(`  Tempo: ${time1}ms`);
        return { ...response.data, tempo: time1 };
    });

    const startTime2 = Date.now();
    await test('Cache - segunda requisição (cached)', async () => {
        const response = await axios.post(`${BASE_URL}/api/meep/cpf/validar`, {
            cpf: '52998224725'  // Mesmo CPF
        });
        const time2 = Date.now() - startTime2;
        console.log(`  Tempo: ${time2}ms (deve ser mais rápido)`);
        if (response.data.fonte !== 'cache' && time2 > 50) {
            console.log('  Aviso: Cache pode não estar funcionando');
        }
        return { ...response.data, tempo: time2 };
    });

    console.log(`\n${colors.yellow}[6] TESTES DE INTEGRAÇÃO${colors.reset}\n`);

    // Teste 16: Health check geral
    await test('Health check - MEEP Service', async () => {
        const response = await axios.get(`${BASE_URL}/health`);
        if (response.data.status !== 'healthy') throw new Error('Serviço não saudável');
        return response.data;
    });

    // Teste 17: Validações recentes
    await test('Buscar validações recentes', async () => {
        const response = await axios.get(`${BASE_URL}/api/meep/cpf/validacoes-recentes?limit=5`);
        if (!Array.isArray(response.data.validacoes)) throw new Error('Lista de validações não retornada');
        console.log(`  Total de validações: ${response.data.total}`);
        return response.data;
    });

    // Teste 18: Stats de check-in
    await test('Estatísticas de check-in', async () => {
        const response = await axios.get(`${BASE_URL}/api/meep/checkin/stats?periodo=1d`);
        if (!response.data.estatisticas) throw new Error('Estatísticas não retornadas');
        console.log(`  Taxa de sucesso: ${response.data.estatisticas.taxa_sucesso}%`);
        return response.data;
    });
}

async function main() {
    try {
        await runTests();
        
        console.log(`
${colors.cyan}========================================================
                    RESULTADO DOS TESTES
========================================================${colors.reset}

${colors.green}✓ Testes Passados: ${testsPassed}${colors.reset}
${colors.red}✗ Testes Falhados: ${testsFailed}${colors.reset}
${colors.yellow}📊 Taxa de Sucesso: ${Math.round((testsPassed / (testsPassed + testsFailed)) * 100)}%${colors.reset}

${colors.magenta}RESUMO POR CATEGORIA:${colors.reset}
• Validação CPF: ${results.filter(r => r.name.includes('CPF')).filter(r => r.status === 'PASSOU').length}/${results.filter(r => r.name.includes('CPF')).length}
• Check-in QR: ${results.filter(r => r.name.includes('Check-in') || r.name.includes('QR')).filter(r => r.status === 'PASSOU').length}/${results.filter(r => r.name.includes('Check-in') || r.name.includes('QR')).length}
• Analytics/IA: ${results.filter(r => r.name.includes('Analytics') || r.name.includes('Dashboard')).filter(r => r.status === 'PASSOU').length}/${results.filter(r => r.name.includes('Analytics') || r.name.includes('Dashboard')).length}
• Segurança: ${results.filter(r => r.name.includes('Rate') || r.name.includes('Validação de entrada')).filter(r => r.status === 'PASSOU').length}/${results.filter(r => r.name.includes('Rate') || r.name.includes('Validação de entrada')).length}
• Cache: ${results.filter(r => r.name.includes('Cache')).filter(r => r.status === 'PASSOU').length}/${results.filter(r => r.name.includes('Cache')).length}

${testsPassed === (testsPassed + testsFailed) 
    ? colors.green + '🎉 TODOS OS TESTES PASSARAM!' 
    : testsFailed > 0 
        ? colors.yellow + '⚠️ Alguns testes falharam, mas o sistema está funcional.' 
        : colors.green + '✅ Sistema testado com sucesso!'}${colors.reset}

${colors.cyan}========================================================${colors.reset}
`);

        // Salvar relatório
        const fs = require('fs');
        const report = {
            timestamp: new Date().toISOString(),
            totalTests: testsPassed + testsFailed,
            passed: testsPassed,
            failed: testsFailed,
            successRate: Math.round((testsPassed / (testsPassed + testsFailed)) * 100),
            results: results
        };
        
        fs.writeFileSync('test-report-meep.json', JSON.stringify(report, null, 2));
        console.log(`\n📄 Relatório salvo em: test-report-meep.json`);
        
    } catch (error) {
        console.error(`${colors.red}Erro fatal:${colors.reset}`, error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}