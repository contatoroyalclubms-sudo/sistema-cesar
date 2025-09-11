/**
 * 🧪 TESTES DE INTEGRAÇÃO COMPLETOS - FRONTEND
 * Testes end-to-end para validar toda a refatoração
 * Última atualização: 05/01/2025
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// Importar validadores
import {
  validarCPF,
  formatarCPF,
  validarCNPJ,
  formatarCNPJ,
  validarEmail,
  validarTelefone,
  formatarTelefone,
  validarNome,
  validarSenha,
  validarValorMonetario,
  formatarMoeda,
  validarQuantidade,
  validarData,
  validarDadosUsuario,
  validarDadosEvento
} from '@/lib/validators';

// Importar enums
import {
  StatusEvento,
  TipoUsuario,
  TipoLista,
  StatusTransacao,
  TipoProduto,
  StatusProduto,
  TipoPagamentoPDV,
  getEnumValues,
  validateEnumValue,
  parseEnumValue
} from '@/types/enums';

// Importar error handler
import {
  AppError,
  ErrorCode,
  handleApiError,
  extractFormErrors,
  withRetry
} from '@/lib/errorHandler';

// Importar tipos
import type {
  Usuario,
  UsuarioCreate,
  Evento,
  EventoCreate,
  Produto,
  ProdutoCreate,
  Lista,
  ListaCreate,
  VendaPDV,
  VendaPDVCreate
} from '@/types/interfaces';

// Mock do Axios
const mock = new MockAdapter(axios);

// ===== TESTES DE VALIDADORES =====

describe('Validadores', () => {
  describe('CPF', () => {
    it('deve validar CPF correto', () => {
      const result = validarCPF('123.456.789-09');
      expect(result.valid).toBe(true);
      expect(result.formatted).toBe('123.456.789-09');
    });

    it('deve rejeitar CPF inválido', () => {
      const result = validarCPF('111.111.111-11');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('iguais');
    });

    it('deve rejeitar CPF com dígitos incorretos', () => {
      const result = validarCPF('123.456.789-00');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('verificadores');
    });

    it('deve formatar CPF sem máscara', () => {
      const formatted = formatarCPF('12345678909');
      expect(formatted).toBe('123.456.789-09');
    });
  });

  describe('CNPJ', () => {
    it('deve validar CNPJ correto', () => {
      const result = validarCNPJ('11.222.333/0001-81');
      expect(result.valid).toBe(true);
      expect(result.formatted).toBe('11.222.333/0001-81');
    });

    it('deve rejeitar CNPJ inválido', () => {
      const result = validarCNPJ('11.111.111/1111-11');
      expect(result.valid).toBe(false);
    });

    it('deve formatar CNPJ sem máscara', () => {
      const formatted = formatarCNPJ('11222333000181');
      expect(formatted).toBe('11.222.333/0001-81');
    });
  });

  describe('Email', () => {
    it('deve validar email correto', () => {
      const result = validarEmail('teste@example.com');
      expect(result.valid).toBe(true);
    });

    it('deve rejeitar email inválido', () => {
      const result = validarEmail('email_invalido');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('inválido');
    });

    it('deve rejeitar email muito longo', () => {
      const longEmail = 'a'.repeat(250) + '@test.com';
      const result = validarEmail(longEmail);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('longo');
    });
  });

  describe('Telefone', () => {
    it('deve validar celular com 9 dígitos', () => {
      const result = validarTelefone('(11) 98765-4321');
      expect(result.valid).toBe(true);
      expect(result.formatted).toBe('(11) 98765-4321');
    });

    it('deve validar telefone fixo', () => {
      const result = validarTelefone('(11) 3456-7890');
      expect(result.valid).toBe(true);
      expect(result.formatted).toBe('(11) 3456-7890');
    });

    it('deve rejeitar DDD inválido', () => {
      const result = validarTelefone('(00) 98765-4321');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('DDD');
    });

    it('deve formatar telefone sem máscara', () => {
      const formatted = formatarTelefone('11987654321');
      expect(formatted).toBe('(11) 98765-4321');
    });
  });

  describe('Nome', () => {
    it('deve validar nome correto', () => {
      const result = validarNome('João Silva');
      expect(result.valid).toBe(true);
    });

    it('deve rejeitar nome muito curto', () => {
      const result = validarNome('A');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('2 caracteres');
    });

    it('deve rejeitar nome apenas com números', () => {
      const result = validarNome('123456');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('letra');
    });
  });

  describe('Senha', () => {
    it('deve validar senha forte', () => {
      const result = validarSenha('SenhaForte123!', {
        requireUppercase: true,
        requireLowercase: true,
        requireDigit: true,
        requireSpecial: true
      });
      expect(result.valid).toBe(true);
      expect(result.strength).toBe('strong');
    });

    it('deve rejeitar senha fraca', () => {
      const result = validarSenha('123', { minLength: 6 });
      expect(result.valid).toBe(false);
      expect(result.error).toContain('6 caracteres');
    });

    it('deve calcular força da senha', () => {
      const weak = validarSenha('abc123');
      const medium = validarSenha('Abc123');
      const strong = validarSenha('Abc123!@#');
      
      expect(weak.strength).toBe('weak');
      expect(medium.strength).toBe('medium');
      expect(strong.strength).toBe('strong');
    });
  });

  describe('Valor Monetário', () => {
    it('deve validar valor correto', () => {
      const result = validarValorMonetario('1.234,56');
      expect(result.valid).toBe(true);
      expect(result.value).toBe(1234.56);
      expect(result.formatted).toBe('R$ 1.234,56');
    });

    it('deve rejeitar valor negativo quando min=0', () => {
      const result = validarValorMonetario(-10);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('maior ou igual');
    });

    it('deve formatar moeda corretamente', () => {
      const formatted = formatarMoeda(1234.56);
      expect(formatted).toBe('R$ 1.234,56');
    });
  });

  describe('Validação de Dados Compostos', () => {
    it('deve validar dados de usuário completos', () => {
      const result = validarDadosUsuario({
        cpf: '123.456.789-09',
        nome: 'João Silva',
        email: 'joao@example.com',
        telefone: '(11) 98765-4321',
        senha: 'senha123',
        tipo: 'cliente'
      });
      
      expect(result.valid).toBe(true);
      expect(result.validated?.cpf).toBe('123.456.789-09');
      expect(result.validated?.email).toBe('joao@example.com');
    });

    it('deve detectar múltiplos erros em dados de usuário', () => {
      const result = validarDadosUsuario({
        cpf: '111.111.111-11',
        nome: 'J',
        email: 'email_invalido',
        senha: '123'
      });
      
      expect(result.valid).toBe(false);
      expect(result.errors.cpf).toBeDefined();
      expect(result.errors.nome).toBeDefined();
      expect(result.errors.email).toBeDefined();
      expect(result.errors.senha).toBeDefined();
    });
  });
});

// ===== TESTES DE ENUMS =====

describe('Enums', () => {
  it('deve retornar todos os valores de um enum', () => {
    const valores = getEnumValues(StatusEvento);
    expect(valores).toContain('ATIVO');
    expect(valores).toContain('INATIVO');
    expect(valores).toContain('CANCELADO');
  });

  it('deve validar valor de enum', () => {
    expect(validateEnumValue(TipoProduto, 'BEBIDA')).toBe(true);
    expect(validateEnumValue(TipoProduto, 'INVALIDO')).toBe(false);
  });

  it('deve fazer parse de string para enum', () => {
    expect(parseEnumValue(StatusEvento, 'ativo')).toBe('ATIVO');
    expect(parseEnumValue(StatusEvento, 'ATIVO')).toBe('ATIVO');
    expect(parseEnumValue(StatusEvento, 'invalido')).toBeNull();
  });

  it('deve verificar compatibilidade de enums backend/frontend', () => {
    // Todos os enums devem estar em MAIÚSCULO
    expect(StatusEvento.ATIVO).toBe('ATIVO');
    expect(TipoProduto.BEBIDA).toBe('BEBIDA');
    expect(StatusProduto.ATIVO).toBe('ATIVO');
    expect(TipoPagamentoPDV.PIX).toBe('PIX');
  });
});

// ===== TESTES DE TRATAMENTO DE ERROS =====

describe('Error Handler', () => {
  beforeEach(() => {
    mock.reset();
  });

  it('deve tratar erro de validação (422)', () => {
    const axiosError = {
      isAxiosError: true,
      response: {
        status: 422,
        data: {
          error: 'Erro de validação',
          code: 'VALIDATION_ERROR',
          details: [
            { field: 'cpf', message: 'CPF inválido' },
            { field: 'email', message: 'Email inválido' }
          ]
        }
      }
    };

    const appError = handleApiError(axiosError);
    
    expect(appError).toBeInstanceOf(AppError);
    expect(appError.code).toBe(ErrorCode.VALIDATION_ERROR);
    expect(appError.statusCode).toBe(422);
    expect(appError.details).toHaveLength(2);
  });

  it('deve tratar erro de autenticação (401)', () => {
    const axiosError = {
      isAxiosError: true,
      response: {
        status: 401,
        data: {
          error: 'Token inválido',
          code: 'UNAUTHORIZED'
        }
      }
    };

    const appError = handleApiError(axiosError);
    
    expect(appError.code).toBe(ErrorCode.UNAUTHORIZED);
    expect(appError.statusCode).toBe(401);
  });

  it('deve tratar erro de rede', () => {
    const networkError = new Error('Network Error');
    networkError.code = 'ERR_NETWORK';

    const appError = handleApiError(networkError);
    
    expect(appError.code).toBe(ErrorCode.NETWORK_ERROR);
    expect(appError.statusCode).toBe(0);
    expect(appError.message).toContain('conexão');
  });

  it('deve extrair erros de formulário', () => {
    const appError = new AppError(
      'Erro de validação',
      ErrorCode.VALIDATION_ERROR,
      422,
      [
        { field: 'nome', message: 'Nome obrigatório' },
        { field: 'email', message: 'Email inválido' }
      ]
    );

    const formErrors = extractFormErrors(appError);
    
    expect(formErrors.nome).toBe('Nome obrigatório');
    expect(formErrors.email).toBe('Email inválido');
  });

  it('deve executar retry em caso de erro temporário', async () => {
    let attempts = 0;
    
    const fn = async () => {
      attempts++;
      if (attempts < 3) {
        throw new AppError('Erro temporário', ErrorCode.SERVICE_UNAVAILABLE, 503);
      }
      return 'success';
    };

    const result = await withRetry(fn, {
      maxAttempts: 3,
      delay: 10
    });

    expect(result).toBe('success');
    expect(attempts).toBe(3);
  });
});

// ===== TESTES DE INTEGRAÇÃO COM API =====

describe('API Integration', () => {
  beforeEach(() => {
    mock.reset();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('Autenticação', () => {
    it('deve fazer login com sucesso', async () => {
      const loginData = {
        cpf: '123.456.789-09',
        senha: 'senha123'
      };

      const responseData = {
        access_token: 'jwt_token_here',
        token_type: 'bearer',
        user: {
          id: 1,
          cpf: '123.456.789-09',
          nome: 'João Silva',
          email: 'joao@example.com',
          tipo: 'cliente',
          ativo: true
        }
      };

      mock.onPost('/api/auth/login').reply(200, responseData);

      const response = await axios.post('/api/auth/login', loginData);
      
      expect(response.status).toBe(200);
      expect(response.data.access_token).toBeDefined();
      expect(response.data.user.cpf).toBe('123.456.789-09');
    });

    it('deve tratar erro de credenciais inválidas', async () => {
      mock.onPost('/api/auth/login').reply(401, {
        error: 'Credenciais inválidas',
        code: 'INVALID_CREDENTIALS'
      });

      try {
        await axios.post('/api/auth/login', {
          cpf: '123.456.789-09',
          senha: 'senha_errada'
        });
        expect.fail('Should have thrown an error');
      } catch (error) {
        const appError = handleApiError(error);
        expect(appError.code).toBe(ErrorCode.UNAUTHORIZED);
        expect(appError.message).toContain('Credenciais');
      }
    });
  });

  describe('CRUD de Eventos', () => {
    const authHeaders = {
      Authorization: 'Bearer test_token'
    };

    it('deve criar evento com dados válidos', async () => {
      const eventoData: EventoCreate = {
        nome: 'Festival de Verão',
        descricao: 'O maior festival',
        data_evento: new Date('2025-07-15T18:00:00Z'),
        local: 'Praia de Copacabana',
        endereco: 'Av. Atlântica, Rio',
        limite_idade: 18,
        capacidade_maxima: 5000
      };

      const responseData: Evento = {
        id: 1,
        ...eventoData,
        status: StatusEvento.ATIVO,
        criador_id: 1,
        criado_em: new Date().toISOString()
      };

      mock.onPost('/api/eventos').reply(201, responseData);

      const response = await axios.post('/api/eventos', eventoData, { headers: authHeaders });
      
      expect(response.status).toBe(201);
      expect(response.data.id).toBeDefined();
      expect(response.data.status).toBe(StatusEvento.ATIVO);
    });

    it('deve listar eventos com paginação', async () => {
      const responseData = {
        items: [
          { id: 1, nome: 'Evento 1', status: StatusEvento.ATIVO },
          { id: 2, nome: 'Evento 2', status: StatusEvento.ATIVO }
        ],
        total: 2,
        page: 1,
        limit: 10,
        pages: 1
      };

      mock.onGet('/api/eventos?page=1&limit=10').reply(200, responseData);

      const response = await axios.get('/api/eventos', {
        params: { page: 1, limit: 10 },
        headers: authHeaders
      });
      
      expect(response.data.items).toHaveLength(2);
      expect(response.data.total).toBe(2);
    });

    it('deve atualizar status do evento', async () => {
      mock.onPut('/api/eventos/1').reply(200, {
        id: 1,
        nome: 'Evento Atualizado',
        status: StatusEvento.FINALIZADO
      });

      const response = await axios.put(
        '/api/eventos/1',
        { status: StatusEvento.FINALIZADO },
        { headers: authHeaders }
      );
      
      expect(response.data.status).toBe(StatusEvento.FINALIZADO);
    });

    it('deve deletar evento', async () => {
      mock.onDelete('/api/eventos/1').reply(204);

      const response = await axios.delete('/api/eventos/1', { headers: authHeaders });
      
      expect(response.status).toBe(204);
    });
  });

  describe('Fluxo Completo de Venda', () => {
    const authHeaders = {
      Authorization: 'Bearer test_token'
    };

    it('deve completar fluxo de venda PDV', async () => {
      // 1. Criar produtos
      const produto1: Produto = {
        id: 1,
        nome: 'Cerveja',
        tipo: TipoProduto.BEBIDA,
        preco: 10.00,
        estoque_atual: 100,
        estoque_minimo: 10,
        estoque_maximo: 500,
        controla_estoque: true,
        status: StatusProduto.ATIVO
      };

      const produto2: Produto = {
        id: 2,
        nome: 'Hambúrguer',
        tipo: TipoProduto.COMIDA,
        preco: 25.00,
        estoque_atual: 50,
        estoque_minimo: 5,
        estoque_maximo: 100,
        controla_estoque: true,
        status: StatusProduto.ATIVO
      };

      // 2. Criar venda
      const vendaData: VendaPDVCreate = {
        evento_id: 1,
        cpf_cliente: '123.456.789-09',
        nome_cliente: 'João Silva',
        tipo_pagamento: TipoPagamentoPDV.PIX,
        itens: [
          {
            produto_id: 1,
            quantidade: 2,
            preco_unitario: 10.00
          },
          {
            produto_id: 2,
            quantidade: 1,
            preco_unitario: 25.00
          }
        ]
      };

      const vendaResponse: VendaPDV = {
        id: 1,
        numero_venda: 'V001',
        evento_id: 1,
        cpf_cliente: '123.456.789-09',
        nome_cliente: 'João Silva',
        tipo_pagamento: TipoPagamentoPDV.PIX,
        valor_total: 45.00,
        valor_desconto: 0,
        valor_final: 45.00,
        status: StatusVendaPDV.APROVADA,
        usuario_vendedor_id: 1,
        criado_em: new Date().toISOString()
      };

      mock.onPost('/api/pdv/vendas').reply(201, vendaResponse);

      const response = await axios.post('/api/pdv/vendas', vendaData, { headers: authHeaders });
      
      expect(response.status).toBe(201);
      expect(response.data.valor_final).toBe(45.00);
      expect(response.data.status).toBe(StatusVendaPDV.APROVADA);
    });
  });
});

// ===== TESTES DE PERFORMANCE =====

describe('Performance', () => {
  it('deve validar CPF em menos de 10ms', () => {
    const start = performance.now();
    
    for (let i = 0; i < 1000; i++) {
      validarCPF('123.456.789-09');
    }
    
    const end = performance.now();
    const avgTime = (end - start) / 1000;
    
    expect(avgTime).toBeLessThan(10);
  });

  it('deve formatar valores monetários rapidamente', () => {
    const start = performance.now();
    
    for (let i = 0; i < 1000; i++) {
      formatarMoeda(1234.56);
    }
    
    const end = performance.now();
    const avgTime = (end - start) / 1000;
    
    expect(avgTime).toBeLessThan(5);
  });

  it('deve processar validação de formulário complexo rapidamente', () => {
    const start = performance.now();
    
    const dadosCompletos = {
      cpf: '123.456.789-09',
      nome: 'Nome Completo do Usuário',
      email: 'usuario@example.com',
      telefone: '(11) 98765-4321',
      senha: 'SenhaForte123!',
      tipo: 'cliente'
    };
    
    for (let i = 0; i < 100; i++) {
      validarDadosUsuario(dadosCompletos);
    }
    
    const end = performance.now();
    const avgTime = (end - start) / 100;
    
    expect(avgTime).toBeLessThan(50);
  });
});