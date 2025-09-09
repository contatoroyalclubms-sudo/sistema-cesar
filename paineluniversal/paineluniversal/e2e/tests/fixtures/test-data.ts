/**
 * 🧪 DADOS DE TESTE
 * Dados mockados e factories para testes
 */

import { faker } from '@faker-js/faker/locale/pt_BR';

// ===== USUÁRIOS DE TESTE =====

export const testUsers = {
  admin: {
    cpf: '123.456.789-09',
    senha: 'Admin@123',
    nome: 'Admin Teste',
    email: 'admin@teste.com',
    role: 'ADMIN'
  },
  promoter: {
    cpf: '987.654.321-00',
    senha: 'Promoter@123',
    nome: 'Promoter Teste',
    email: 'promoter@teste.com',
    role: 'PROMOTER'
  },
  cliente: {
    cpf: '111.222.333-44',
    senha: 'Cliente@123',
    nome: 'Cliente Teste',
    email: 'cliente@teste.com',
    role: 'CLIENTE'
  }
};

// ===== FACTORIES =====

export class TestDataFactory {
  /**
   * Gera CPF válido aleatório
   */
  static generateCPF(): string {
    const randomDigits = () => Math.floor(Math.random() * 9);
    const cpf = Array.from({ length: 9 }, randomDigits);
    
    // Calcular primeiro dígito verificador
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += cpf[i] * (10 - i);
    }
    let digit1 = 11 - (sum % 11);
    digit1 = digit1 >= 10 ? 0 : digit1;
    cpf.push(digit1);
    
    // Calcular segundo dígito verificador
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += cpf[i] * (11 - i);
    }
    let digit2 = 11 - (sum % 11);
    digit2 = digit2 >= 10 ? 0 : digit2;
    cpf.push(digit2);
    
    // Formatar
    const cpfString = cpf.join('');
    return `${cpfString.slice(0, 3)}.${cpfString.slice(3, 6)}.${cpfString.slice(6, 9)}-${cpfString.slice(9)}`;
  }
  
  /**
   * Gera dados de usuário aleatório
   */
  static generateUser() {
    return {
      nome: faker.person.fullName(),
      email: faker.internet.email(),
      cpf: this.generateCPF(),
      telefone: faker.phone.number('(##) #####-####'),
      senha: faker.internet.password({ length: 10, memorable: false }),
      role: faker.helpers.arrayElement(['CLIENTE', 'PROMOTER', 'ADMIN'])
    };
  }
  
  /**
   * Gera dados de evento aleatório
   */
  static generateEvento() {
    const futureDate = faker.date.future();
    
    return {
      nome: faker.company.name() + ' - ' + faker.music.genre(),
      descricao: faker.lorem.paragraph(),
      data: futureDate.toISOString().split('T')[0],
      horario: faker.date.future().toTimeString().slice(0, 5),
      local: faker.company.name(),
      endereco: faker.location.streetAddress(),
      cidade: faker.location.city(),
      estado: faker.location.state({ abbreviated: true }),
      cep: faker.location.zipCode('#####-###'),
      capacidade_maxima: faker.number.int({ min: 50, max: 1000 }),
      idade_minima: faker.helpers.arrayElement([16, 18, 21]),
      status: 'ATIVO',
      tipo_evento: faker.helpers.arrayElement(['BALADA', 'SHOW', 'FESTIVAL', 'CORPORATIVO', 'OUTRO']),
      banner_url: faker.image.url()
    };
  }
  
  /**
   * Gera dados de produto aleatório
   */
  static generateProduto() {
    return {
      nome: faker.commerce.productName(),
      descricao: faker.commerce.productDescription(),
      categoria: faker.helpers.arrayElement(['BEBIDA', 'COMIDA', 'OUTROS']),
      preco_venda: parseFloat(faker.commerce.price({ min: 5, max: 100 })),
      preco_custo: parseFloat(faker.commerce.price({ min: 2, max: 50 })),
      codigo_barras: faker.string.numeric(13),
      unidade: faker.helpers.arrayElement(['UN', 'CX', 'PCT', 'L', 'ML']),
      estoque_minimo: faker.number.int({ min: 10, max: 100 }),
      ativo: true
    };
  }
  
  /**
   * Gera dados de venda aleatória
   */
  static generateVenda(eventoId: number, clienteId: number, vendedorId: number) {
    const numItens = faker.number.int({ min: 1, max: 5 });
    const itens = [];
    
    for (let i = 0; i < numItens; i++) {
      itens.push({
        produto_id: faker.number.int({ min: 1, max: 10 }),
        quantidade: faker.number.int({ min: 1, max: 3 }),
        preco_unitario: parseFloat(faker.commerce.price({ min: 5, max: 50 })),
        desconto: faker.number.int({ min: 0, max: 10 })
      });
    }
    
    return {
      evento_id: eventoId,
      cliente_id: clienteId,
      vendedor_id: vendedorId,
      itens,
      forma_pagamento: faker.helpers.arrayElement(['DINHEIRO', 'CARTAO', 'PIX', 'FIADO']),
      observacoes: faker.lorem.sentence()
    };
  }
  
  /**
   * Gera dados de check-in aleatório
   */
  static generateCheckin(eventoId: number, usuarioId: number) {
    return {
      evento_id: eventoId,
      usuario_id: usuarioId,
      tipo_ingresso: faker.helpers.arrayElement(['VIP', 'NORMAL', 'PROMOTER']),
      observacoes: faker.lorem.sentence()
    };
  }
}

// ===== DADOS DE TESTE ESTÁTICOS =====

export const staticTestData = {
  // Evento padrão para testes
  defaultEvento: {
    nome: 'Evento de Teste E2E',
    descricao: 'Evento criado automaticamente para testes E2E',
    data: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 dias no futuro
    horario: '20:00',
    local: 'Local de Teste',
    endereco: 'Rua de Teste, 123',
    cidade: 'São Paulo',
    estado: 'SP',
    cep: '01234-567',
    capacidade_maxima: 500,
    idade_minima: 18,
    status: 'ATIVO',
    tipo_evento: 'BALADA'
  },
  
  // Produtos padrão para PDV
  defaultProdutos: [
    {
      nome: 'Água Mineral',
      categoria: 'BEBIDA',
      preco_venda: 5.00,
      codigo_barras: '7891234567890'
    },
    {
      nome: 'Cerveja Lata',
      categoria: 'BEBIDA',
      preco_venda: 8.00,
      codigo_barras: '7891234567891'
    },
    {
      nome: 'Hambúrguer',
      categoria: 'COMIDA',
      preco_venda: 25.00,
      codigo_barras: '7891234567892'
    }
  ],
  
  // Listas de check-in
  listas: {
    vip: {
      nome: 'Lista VIP',
      tipo: 'VIP',
      limite: 50
    },
    normal: {
      nome: 'Lista Normal',
      tipo: 'NORMAL',
      limite: 200
    },
    promoter: {
      nome: 'Lista Promoter',
      tipo: 'PROMOTER',
      limite: 100
    }
  }
};

// ===== HELPERS =====

export class TestHelpers {
  /**
   * Aguarda elemento estar visível
   */
  static async waitForElement(page: any, selector: string, timeout = 5000) {
    await page.waitForSelector(selector, { state: 'visible', timeout });
  }
  
  /**
   * Aguarda navegação completa
   */
  static async waitForNavigation(page: any) {
    await page.waitForLoadState('networkidle');
  }
  
  /**
   * Gera timestamp único
   */
  static generateTimestamp(): string {
    return new Date().getTime().toString();
  }
  
  /**
   * Formata moeda brasileira
   */
  static formatCurrency(value: number): string {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  }
  
  /**
   * Extrai números de string
   */
  static extractNumbers(str: string): number {
    const numbers = str.match(/\d+/g);
    return numbers ? parseInt(numbers.join('')) : 0;
  }
}