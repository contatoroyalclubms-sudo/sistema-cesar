import { test, expect } from '@playwright/test';

// Testes gerados automaticamente por engenharia reversa
// Sistema de Eventos - 2025-09-11T06:18:17.794Z

const config = {
    baseUrl: 'http://localhost:5173',
    backendUrl: 'http://localhost:8000',
    testCredentials: {
        cpf: '00000000000',
        senha: 'admin123'
    }
};

test.describe('Sistema de Eventos - Testes Automatizados', () => {
    let token;
    
    test.beforeAll(async ({ request }) => {
        // Fazer login e obter token
        const response = await request.post(`${config.backendUrl}/api/auth/login`, {
            data: config.testCredentials
        });
        const data = await response.json();
        token = data.token;
    });

    test.describe('Outros', () => {
        test('GET /api/cors-test', async ({ request }) => {
            const response = await request.get(`${config.backendUrl}/api/cors-test`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            expect(response.status()).toBeLessThan(400);
        });

        test('GET /api/cors-test', async ({ request }) => {
            const response = await request.get(`${config.backendUrl}/api/cors-test`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            expect(response.status()).toBeLessThan(400);
        });

    });
});
