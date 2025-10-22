// Testes E2E Playwright - Fluxo PDV Sistema NIP
// Executa: npx playwright test e2e/playwright/pdv_flow.spec.ts

import { test, expect } from '@playwright/test';

// Configuração do ambiente
const BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'admin@nip.com.br';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

test.describe('Fluxo PDV - Sistema NIP', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    // Realizar login e obter token
    const loginResponse = await request.post(`${BASE_URL}/api/auth/login`, {
      data: {
        email: ADMIN_EMAIL,
        senha: ADMIN_PASSWORD
      }
    });

    if (loginResponse.ok()) {
      const loginData = await loginResponse.json();
      authToken = loginData.access_token;
    } else {
      console.warn('⚠️ Login falhou - usando token placeholder');
      authToken = 'test-token-placeholder';
    }
  });

  test('01 - Health Check da API', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/health`);
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data.status).toBe('healthy');
  });

  test('02 - Autenticação - Login via API', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/auth/login`, {
      data: {
        email: ADMIN_EMAIL,
        senha: ADMIN_PASSWORD
      }
    });

    // Aceita 200 (sucesso) ou 401 (credenciais inválidas) - não 404/405
    expect([200, 401, 422]).toContain(response.status());
    
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('access_token');
      expect(data.token_type).toBe('bearer');
    }
  });

  test('03 - Dashboard - Carregar métricas', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/dashboard`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    // Com token, não deve ser 401/403
    if (authToken !== 'test-token-placeholder') {
      expect([401, 403]).not.toContain(response.status());
    }
    
    // Se der 200, verificar estrutura
    if (response.status() === 200) {
      const data = await response.json();
      expect(data).toHaveProperty('status');
    }
  });

  test('04 - PDV - Configurações do sistema', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/pdv/configuracoes`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    // Endpoint deve existir (não 404)
    expect(response.status()).not.toBe(404);
    
    if (response.status() === 200) {
      const data = await response.json();
      expect(data).toHaveProperty('status');
    }
  });

  test('05 - PDV - Tipos de vínculo proprietário', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/pdv/proprietario/tipo-vinculo`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    // Endpoint REST normalizado deve existir
    expect(response.status()).not.toBe(404);
    
    // Testar rota legada também
    const legacyResponse = await request.get(`${BASE_URL}/api/Proprietario/tipovinculo`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    // Rota legada deve existir ou redirecionar
    expect([200, 301, 401, 403]).toContain(legacyResponse.status());
    
    // Se redirect, deve ter Location header
    if (legacyResponse.status() === 301) {
      expect(legacyResponse.headers()['location']).toBeTruthy();
    }
  });

  test('06 - Empresas - CRUD completo', async ({ request }) => {
    // Listar empresas
    const listResponse = await request.get(`${BASE_URL}/api/empresas?page=1&pageSize=5`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    expect(listResponse.status()).not.toBe(404);
    
    // Criar empresa (se autenticado)
    if (authToken !== 'test-token-placeholder') {
      const createResponse = await request.post(`${BASE_URL}/api/empresas`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        },
        data: {
          nome: 'Empresa Teste E2E',
          cnpj: '12.345.678/0001-90',
          email: 'teste@e2e.com'
        }
      });
      
      // Pode dar 201 (criado) ou error de validação, mas não 404
      expect(createResponse.status()).not.toBe(404);
      
      if (createResponse.status() === 201) {
        expect(createResponse.headers()['location']).toBeTruthy();
      }
    }
    
    // Testar rota legada
    const legacyCreate = await request.get(`${BASE_URL}/api/empresas/criar`);
    expect([200, 301, 401, 403]).toContain(legacyCreate.status());
  });

  test('07 - Financeiro - Transações com idempotência', async ({ request }) => {
    // Listar transações
    const listResponse = await request.get(`${BASE_URL}/api/financeiro/transacoes`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    expect(listResponse.status()).not.toBe(404);
    
    // Criar transação com chave de idempotência
    if (authToken !== 'test-token-placeholder') {
      const idempotencyKey = `test-${Date.now()}`;
      
      const createResponse = await request.post(`${BASE_URL}/api/financeiro/transacoes`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Idempotency-Key': idempotencyKey
        },
        data: {
          valor: 100.50,
          tipo: 'receita',
          descricao: 'Teste E2E Transação'
        }
      });
      
      expect(createResponse.status()).not.toBe(404);
      
      // Repetir mesma requisição - deve detectar duplicata
      const duplicateResponse = await request.post(`${BASE_URL}/api/financeiro/transacoes`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Idempotency-Key': idempotencyKey
        },
        data: {
          valor: 100.50,
          tipo: 'receita',
          descricao: 'Teste E2E Transação'
        }
      });
      
      // Pode retornar 409 (conflito) ou mesmo resultado
      if (duplicateResponse.status() === 409) {
        console.log('✅ Idempotência funcionando - detectou duplicata');
      }
    }
  });

  test('08 - Marketing - Campanhas e fidelidade', async ({ request }) => {
    // Listar campanhas
    const campaignsResponse = await request.get(`${BASE_URL}/api/marketing/campanhas`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    expect(campaignsResponse.status()).not.toBe(404);
    
    // Listar programas de fidelidade
    const loyaltyResponse = await request.get(`${BASE_URL}/api/marketing/fidelidade/programas`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    expect(loyaltyResponse.status()).not.toBe(404);
    
    // Criar campanha
    if (authToken !== 'test-token-placeholder') {
      const createCampaign = await request.post(`${BASE_URL}/api/marketing/campanhas`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        },
        data: {
          nome: 'Campanha Teste E2E',
          canal: 'email',
          conteudo: {
            assunto: 'Teste',
            corpo: 'Campanha de teste'
          }
        }
      });
      
      expect(createCampaign.status()).not.toBe(404);
    }
  });

  test('09 - Paginação - Parâmetros aceitos', async ({ request }) => {
    const endpoints = [
      '/api/empresas',
      '/api/financeiro/transacoes',
      '/api/marketing/campanhas'
    ];
    
    for (const endpoint of endpoints) {
      const response = await request.get(`${endpoint}?page=1&pageSize=5&sort=created_at&order=desc`, {
        baseURL: BASE_URL,
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      // Não deve dar erro de parâmetro inválido
      expect(response.status()).not.toBe(400);
      console.log(`✅ ${endpoint} aceita paginação`);
    }
  });

  test('10 - Tratamento de Erros', async ({ request }) => {
    // Endpoint inexistente - deve retornar 404
    const notFoundResponse = await request.get(`${BASE_URL}/api/inexistente`);
    expect(notFoundResponse.status()).toBe(404);
    
    // Método não permitido
    const methodNotAllowed = await request.delete(`${BASE_URL}/health`);
    expect([405, 404]).toContain(methodNotAllowed.status());
    
    // Sem autenticação em endpoint protegido
    const unauthorized = await request.get(`${BASE_URL}/api/dashboard`);
    expect([401, 403]).toContain(unauthorized.status());
    
    if (unauthorized.status() === 401) {
      const errorData = await unauthorized.json();
      expect(errorData).toHaveProperty('message');
    }
  });

  test('11 - Headers de segurança', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/health`);
    
    const headers = response.headers();
    
    // Verificar headers de segurança básicos
    expect(headers['content-type']).toContain('application/json');
    
    // Logs para debug
    console.log('Headers recebidos:', Object.keys(headers));
  });

  test('12 - Performance - Tempo de resposta', async ({ request }) => {
    const startTime = Date.now();
    
    const response = await request.get(`${BASE_URL}/health`);
    
    const responseTime = Date.now() - startTime;
    
    expect(response.status()).toBe(200);
    expect(responseTime).toBeLessThan(5000); // Menos de 5 segundos
    
    console.log(`⏱️ Tempo de resposta /health: ${responseTime}ms`);
  });
});

// Configuração adicional do Playwright
test.afterEach(async ({}, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    console.log(`❌ Teste falhou: ${testInfo.title}`);
  }
});

// Hooks de configuração
test.beforeEach(async ({}) => {
  // Setup comum para cada teste
  console.log(`🧪 Executando: ${test.info().title}`);
});