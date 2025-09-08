/**
 * Exemplo de Configuração Completa de Módulo - Fornecedores
 * Este arquivo demonstra como criar um módulo completo do zero
 */

export const exemploFornecedores = {
  name: 'fornecedores',
  title: 'Fornecedores',
  itemName: 'Fornecedor', 
  apiEndpoint: 'fornecedores',
  description: 'Módulo para gestão completa de fornecedores da empresa, incluindo dados cadastrais, contatos e documentação.',
  
  // Configurações de UI
  allowBulkActions: true,
  showExportImport: true,
  generateBackend: true,
  customComponent: false,
  
  // Mensagens customizadas
  createButtonText: 'Cadastrar Fornecedor',
  emptyMessage: 'NENHUM FORNECEDOR CADASTRADO',
  
  // Colunas da tabela de listagem
  columns: [
    { 
      key: 'razao_social', 
      label: 'RAZÃO SOCIAL', 
      type: 'text',
      sortable: true 
    },
    { 
      key: 'nome_fantasia', 
      label: 'NOME FANTASIA', 
      type: 'text' 
    },
    { 
      key: 'cnpj', 
      label: 'CNPJ', 
      type: 'text' 
    },
    { 
      key: 'telefone', 
      label: 'TELEFONE', 
      type: 'text' 
    },
    { 
      key: 'email', 
      label: 'E-MAIL', 
      type: 'text' 
    },
    { 
      key: 'cidade', 
      label: 'CIDADE', 
      type: 'text' 
    },
    { 
      key: 'status', 
      label: 'STATUS', 
      type: 'status' 
    }
  ],
  
  // Campos do formulário
  formFields: [
    // Dados básicos
    {
      key: 'razao_social',
      label: 'Razão Social',
      type: 'text',
      required: true,
      placeholder: 'Razão social da empresa',
      maxLength: 200,
      helpText: 'Nome oficial da empresa conforme registro na Receita Federal'
    },
    {
      key: 'nome_fantasia', 
      label: 'Nome Fantasia',
      type: 'text',
      required: false,
      placeholder: 'Nome fantasia da empresa',
      maxLength: 200,
      helpText: 'Nome comercial pelo qual a empresa é conhecida'
    },
    
    // Documentação
    {
      key: 'cnpj',
      label: 'CNPJ',
      type: 'text',
      required: true,
      placeholder: '00.000.000/0000-00',
      maxLength: 18,
      validate: (value) => {
        if (value && !/^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(value)) {
          return 'CNPJ deve estar no formato 00.000.000/0000-00'
        }
      },
      helpText: 'CNPJ da empresa (obrigatório)'
    },
    {
      key: 'inscricao_estadual',
      label: 'Inscrição Estadual',
      type: 'text',
      required: false,
      placeholder: '000.000.000.000',
      maxLength: 20
    },
    
    // Contato
    {
      key: 'telefone',
      label: 'Telefone',
      type: 'text',
      required: false,
      placeholder: '(00) 00000-0000',
      maxLength: 15,
      validate: (value) => {
        if (value && !/^\(\d{2}\)\s\d{4,5}-\d{4}$/.test(value)) {
          return 'Telefone deve estar no formato (00) 00000-0000'
        }
      }
    },
    {
      key: 'celular',
      label: 'Celular',
      type: 'text',
      required: false,
      placeholder: '(00) 00000-0000',
      maxLength: 15
    },
    {
      key: 'email',
      label: 'E-mail',
      type: 'email',
      required: false,
      placeholder: 'contato@empresa.com',
      helpText: 'E-mail principal para contato'
    },
    {
      key: 'site',
      label: 'Website',
      type: 'text',
      required: false,
      placeholder: 'https://www.empresa.com.br'
    },
    
    // Endereço
    {
      key: 'cep',
      label: 'CEP',
      type: 'text',
      required: false,
      placeholder: '00000-000',
      maxLength: 9,
      validate: (value) => {
        if (value && !/^\d{5}-\d{3}$/.test(value)) {
          return 'CEP deve estar no formato 00000-000'
        }
      }
    },
    {
      key: 'endereco',
      label: 'Endereço',
      type: 'text',
      required: false,
      placeholder: 'Rua, número, complemento',
      maxLength: 200
    },
    {
      key: 'bairro',
      label: 'Bairro',
      type: 'text',
      required: false,
      maxLength: 100
    },
    {
      key: 'cidade',
      label: 'Cidade',
      type: 'text',
      required: false,
      maxLength: 100
    },
    {
      key: 'estado',
      label: 'Estado',
      type: 'select',
      required: false,
      placeholder: 'Selecione o estado',
      options: [
        { value: 'AC', label: 'Acre' },
        { value: 'AL', label: 'Alagoas' },
        { value: 'AP', label: 'Amapá' },
        { value: 'AM', label: 'Amazonas' },
        { value: 'BA', label: 'Bahia' },
        { value: 'CE', label: 'Ceará' },
        { value: 'DF', label: 'Distrito Federal' },
        { value: 'ES', label: 'Espírito Santo' },
        { value: 'GO', label: 'Goiás' },
        { value: 'MA', label: 'Maranhão' },
        { value: 'MT', label: 'Mato Grosso' },
        { value: 'MS', label: 'Mato Grosso do Sul' },
        { value: 'MG', label: 'Minas Gerais' },
        { value: 'PA', label: 'Pará' },
        { value: 'PB', label: 'Paraíba' },
        { value: 'PR', label: 'Paraná' },
        { value: 'PE', label: 'Pernambuco' },
        { value: 'PI', label: 'Piauí' },
        { value: 'RJ', label: 'Rio de Janeiro' },
        { value: 'RN', label: 'Rio Grande do Norte' },
        { value: 'RS', label: 'Rio Grande do Sul' },
        { value: 'RO', label: 'Rondônia' },
        { value: 'RR', label: 'Roraima' },
        { value: 'SC', label: 'Santa Catarina' },
        { value: 'SP', label: 'São Paulo' },
        { value: 'SE', label: 'Sergipe' },
        { value: 'TO', label: 'Tocantins' }
      ]
    },
    
    // Dados comerciais
    {
      key: 'categoria_fornecedor',
      label: 'Categoria',
      type: 'select',
      required: false,
      placeholder: 'Selecione a categoria',
      options: [
        { value: 'produtos', label: 'Produtos' },
        { value: 'servicos', label: 'Serviços' },
        { value: 'equipamentos', label: 'Equipamentos' },
        { value: 'materiais', label: 'Materiais' },
        { value: 'outros', label: 'Outros' }
      ]
    },
    {
      key: 'prazo_pagamento',
      label: 'Prazo de Pagamento (dias)',
      type: 'number',
      required: false,
      min: 0,
      max: 365,
      defaultValue: 30,
      helpText: 'Prazo padrão para pagamento em dias'
    },
    {
      key: 'limite_credito',
      label: 'Limite de Crédito',
      type: 'currency',
      required: false,
      helpText: 'Limite de crédito aprovado para este fornecedor'
    },
    
    // Documentos/anexos
    {
      key: 'logo',
      label: 'Logo da Empresa',
      type: 'file',
      required: false,
      accept: 'image/*',
      multiple: false,
      helpText: 'Logo ou imagem representativa da empresa'
    },
    {
      key: 'documentos',
      label: 'Documentos',
      type: 'file',
      required: false,
      accept: '.pdf,.doc,.docx,.jpg,.png',
      multiple: true,
      helpText: 'Contratos, certidões e outros documentos relevantes'
    },
    
    // Observações
    {
      key: 'observacoes',
      label: 'Observações',
      type: 'textarea',
      required: false,
      placeholder: 'Informações adicionais sobre o fornecedor...',
      rows: 4,
      maxLength: 1000,
      helpText: 'Informações complementares, observações especiais, etc.'
    },
    
    // Status
    {
      key: 'ativo',
      label: 'Status',
      type: 'checkbox',
      checkboxText: 'Fornecedor ativo',
      defaultValue: true,
      helpText: 'Indica se o fornecedor está ativo para novas operações'
    }
  ],
  
  // Filtros de busca
  filters: [
    { 
      key: 'razao_social', 
      type: 'text', 
      placeholder: 'Buscar por razão social...' 
    },
    { 
      key: 'nome_fantasia', 
      type: 'text', 
      placeholder: 'Buscar por nome fantasia...' 
    },
    { 
      key: 'cnpj', 
      type: 'text', 
      placeholder: 'Buscar por CNPJ...' 
    },
    { 
      key: 'email', 
      type: 'text', 
      placeholder: 'Buscar por e-mail...' 
    },
    { 
      key: 'cidade', 
      type: 'text', 
      placeholder: 'Buscar por cidade...' 
    },
    {
      key: 'categoria_fornecedor',
      type: 'select',
      placeholder: 'Filtrar por categoria',
      options: [
        { value: 'produtos', label: 'Produtos' },
        { value: 'servicos', label: 'Serviços' },
        { value: 'equipamentos', label: 'Equipamentos' },
        { value: 'materiais', label: 'Materiais' },
        { value: 'outros', label: 'Outros' }
      ]
    }
  ],
  
  // Filtros toggle (checkboxes)
  toggleFilters: [
    { key: 'apenas_ativos', label: 'Apenas fornecedores ativos' },
    { key: 'com_limite_credito', label: 'Com limite de crédito definido' },
    { key: 'vencimento_proximo', label: 'Com vencimentos próximos' }
  ],
  
  // Função para transformar dados antes do envio
  transformSubmitData: (data) => {
    // Remover formatação do CNPJ para salvar no banco
    if (data.cnpj) {
      data.cnpj = data.cnpj.replace(/[^\d]/g, '')
    }
    
    // Remover formatação do CEP
    if (data.cep) {
      data.cep = data.cep.replace(/[^\d]/g, '')
    }
    
    // Converter telefones para formato limpo
    if (data.telefone) {
      data.telefone = data.telefone.replace(/[^\d]/g, '')
    }
    
    if (data.celular) {
      data.celular = data.celular.replace(/[^\d]/g, '')
    }
    
    return data
  },
  
  // Validações customizadas adicionais
  customValidations: {
    // Validar se CNPJ já existe
    cnpj: async (value) => {
      if (value) {
        const response = await fetch(`/api/fornecedores/validate-cnpj?cnpj=${value}`)
        const result = await response.json()
        
        if (!result.valid) {
          return 'CNPJ já cadastrado no sistema'
        }
      }
    },
    
    // Validar se email já existe
    email: async (value) => {
      if (value) {
        const response = await fetch(`/api/fornecedores/validate-email?email=${value}`)
        const result = await response.json()
        
        if (!result.valid) {
          return 'E-mail já cadastrado no sistema'
        }
      }
    }
  }
}

/**
 * Exemplo de Configuração Completa - Clientes
 */
export const exemploClientes = {
  name: 'clientes',
  title: 'Clientes',
  itemName: 'Cliente',
  apiEndpoint: 'meep/clientes',
  description: 'Gestão completa de clientes do sistema',
  
  allowBulkActions: true,
  showExportImport: true,
  generateBackend: false, // Já existe no backend meep.py
  
  columns: [
    { key: 'nome_completo', label: 'NOME COMPLETO', type: 'text', sortable: true },
    { key: 'cpf', label: 'CPF', type: 'cpf', sortable: true },
    { key: 'email', label: 'EMAIL', type: 'email', sortable: true },
    { key: 'telefone', label: 'TELEFONE', type: 'phone', sortable: true },
    { key: 'data_nascimento', label: 'DATA NASCIMENTO', type: 'date', sortable: true },
    { key: 'status', label: 'STATUS', type: 'status', sortable: true }
  ],
  
  formFields: [
    {
      key: 'nome_completo',
      label: 'Nome Completo',
      type: 'text',
      required: true,
      placeholder: 'Digite o nome completo',
      validation: {
        minLength: 3,
        maxLength: 100,
        pattern: '^[A-Za-zÀ-ÿ\\s]+$',
        message: 'Nome deve conter apenas letras e espaços'
      }
    },
    {
      key: 'cpf',
      label: 'CPF',
      type: 'cpf',
      required: true,
      placeholder: '000.000.000-00',
      validation: {
        cpf: true,
        message: 'CPF inválido'
      }
    },
    {
      key: 'email',
      label: 'Email',
      type: 'email',
      required: true,
      placeholder: 'exemplo@email.com',
      validation: {
        email: true,
        message: 'Email inválido'
      }
    },
    {
      key: 'telefone',
      label: 'Telefone',
      type: 'phone',
      required: true,
      placeholder: '(11) 99999-9999',
      validation: {
        phone: true,
        message: 'Telefone inválido'
      }
    },
    {
      key: 'nome_social',
      label: 'Nome Social',
      type: 'text',
      required: false,
      placeholder: 'Nome social (opcional)',
      validation: {
        maxLength: 100
      }
    },
    {
      key: 'data_nascimento',
      label: 'Data de Nascimento',
      type: 'date',
      required: false,
      validation: {
        maxDate: 'today',
        message: 'Data deve ser anterior a hoje'
      }
    },
    {
      key: 'nome_mae',
      label: 'Nome da Mãe',
      type: 'text',
      required: false,
      placeholder: 'Nome da mãe (opcional)',
      validation: {
        maxLength: 100
      }
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      required: true,
      defaultValue: 'ativo',
      options: [
        { value: 'ativo', label: 'Ativo' },
        { value: 'inativo', label: 'Inativo' },
        { value: 'suspenso', label: 'Suspenso' }
      ]
    }
  ],
  
  filters: [
    {
      key: 'nome_completo',
      label: 'Nome',
      type: 'text',
      placeholder: 'Filtrar por nome'
    },
    {
      key: 'cpf',
      label: 'CPF',
      type: 'text',
      placeholder: 'Filtrar por CPF'
    },
    {
      key: 'email',
      label: 'Email',
      type: 'text',
      placeholder: 'Filtrar por email'
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: '', label: 'Todos' },
        { value: 'ativo', label: 'Ativo' },
        { value: 'inativo', label: 'Inativo' },
        { value: 'suspenso', label: 'Suspenso' }
      ]
    }
  ],
  
  searchConfig: {
    searchableFields: ['nome_completo', 'cpf', 'email', 'telefone'],
    placeholder: 'Buscar clientes...'
  },
  
  actions: {
    create: true,
    read: true,
    update: true,
    delete: true,
    export: true,
    import: true
  },
  
  validation: {
    uniqueFields: ['cpf', 'email'],
    
    // Validação customizada para CPF único
    customValidation: async (field, value, apiService) => {
      if (field === 'cpf' && value) {
        const cpfFormatted = value.replace(/[^0-9]/g, '');
        const result = await apiService.validateUnique('cpf', cpfFormatted);
        if (!result.valid) {
          return 'CPF já cadastrado no sistema'
        }
      }
      if (field === 'email' && value) {
        const result = await apiService.validateUnique('email', value);
        if (!result.valid) {
          return 'Email já cadastrado no sistema'
        }
      }
    }
  },
  
  permissions: {
    roles: ['admin', 'promoter'],
    create: ['admin', 'promoter'],
    update: ['admin', 'promoter'],
    delete: ['admin'],
    export: ['admin', 'promoter'],
    import: ['admin']
  },
  
  ui: {
    itemsPerPage: 25,
    showPagination: true,
    showSearch: true,
    showFilters: true,
    showBulkActions: true,
    sortBy: 'nome_completo',
    sortOrder: 'asc'
  }
}

/**
 * Exemplo de Configuração Completa - Operadores
 */
export const exemploOperadores = {
  name: 'operadores',
  title: 'Operadores',
  itemName: 'Operador',
  apiEndpoint: 'usuarios', // Usar endpoint de usuários com tipo operador
  description: 'Gestão completa de operadores do sistema',
  
  allowBulkActions: true,
  showExportImport: true,
  generateBackend: false, // Já existe no backend usuarios.py
  
  columns: [
    { key: 'nome', label: 'NOME', type: 'text', sortable: true },
    { key: 'cpf', label: 'CPF', type: 'cpf', sortable: true },
    { key: 'email', label: 'EMAIL', type: 'email', sortable: true },
    { key: 'telefone', label: 'TELEFONE', type: 'phone', sortable: true },
    { key: 'comissao', label: 'COMISSÃO (%)', type: 'percentage', sortable: true },
    { key: 'ativo', label: 'STATUS', type: 'status', sortable: true }
  ],
  
  formFields: [
    {
      key: 'nome',
      label: 'Nome Completo',
      type: 'text',
      required: true,
      placeholder: 'Digite o nome completo do operador',
      validation: {
        minLength: 3,
        maxLength: 100,
        pattern: '^[A-Za-zÀ-ÿ\\s]+$',
        message: 'Nome deve conter apenas letras e espaços'
      }
    },
    {
      key: 'cpf',
      label: 'CPF',
      type: 'cpf',
      required: true,
      placeholder: '000.000.000-00',
      validation: {
        cpf: true,
        message: 'CPF inválido'
      }
    },
    {
      key: 'email',
      label: 'Email',
      type: 'email',
      required: true,
      placeholder: 'exemplo@email.com',
      validation: {
        email: true,
        message: 'Email inválido'
      }
    },
    {
      key: 'telefone',
      label: 'Telefone',
      type: 'phone',
      required: true,
      placeholder: '(11) 99999-9999',
      validation: {
        phone: true,
        message: 'Telefone inválido'
      }
    },
    {
      key: 'senha',
      label: 'Senha',
      type: 'password',
      required: true,
      placeholder: 'Digite uma senha segura',
      validation: {
        minLength: 6,
        message: 'Senha deve ter pelo menos 6 caracteres'
      }
    },
    {
      key: 'comissao',
      label: 'Comissão (%)',
      type: 'number',
      required: false,
      placeholder: '0.00',
      defaultValue: '0.00',
      validation: {
        min: 0,
        max: 100,
        step: 0.01,
        message: 'Comissão deve estar entre 0% e 100%'
      }
    },
    {
      key: 'tipo',
      label: 'Tipo de Usuário',
      type: 'hidden',
      defaultValue: 'promoter',
      required: true
    },
    {
      key: 'ativo',
      label: 'Status',
      type: 'select',
      required: true,
      defaultValue: true,
      options: [
        { value: true, label: 'Ativo' },
        { value: false, label: 'Inativo' }
      ]
    }
  ],
  
  filters: [
    {
      key: 'nome',
      label: 'Nome',
      type: 'text',
      placeholder: 'Filtrar por nome'
    },
    {
      key: 'cpf',
      label: 'CPF',
      type: 'text',
      placeholder: 'Filtrar por CPF'
    },
    {
      key: 'email',
      label: 'Email',
      type: 'text',
      placeholder: 'Filtrar por email'
    },
    {
      key: 'ativo',
      label: 'Status',
      type: 'select',
      options: [
        { value: '', label: 'Todos' },
        { value: 'true', label: 'Ativo' },
        { value: 'false', label: 'Inativo' }
      ]
    }
  ],
  
  searchConfig: {
    searchableFields: ['nome', 'cpf', 'email', 'telefone'],
    placeholder: 'Buscar operadores...'
  },
  
  actions: {
    create: true,
    read: true,
    update: true,
    delete: true,
    export: true,
    import: true
  },
  
  validation: {
    uniqueFields: ['cpf', 'email'],
    
    // Validação customizada para operadores
    customValidation: async (field, value, apiService) => {
      if (field === 'cpf' && value) {
        const cpfFormatted = value.replace(/[^0-9]/g, '');
        const result = await apiService.validateUnique('cpf', cpfFormatted);
        if (!result.valid) {
          return 'CPF já cadastrado no sistema'
        }
      }
      if (field === 'email' && value) {
        const result = await apiService.validateUnique('email', value);
        if (!result.valid) {
          return 'Email já cadastrado no sistema'
        }
      }
    }
  },
  
  permissions: {
    roles: ['admin'],
    create: ['admin'],
    update: ['admin'],
    delete: ['admin'],
    export: ['admin'],
    import: ['admin']
  },
  
  ui: {
    itemsPerPage: 25,
    showPagination: true,
    showSearch: true,
    showFilters: true,
    showBulkActions: true,
    sortBy: 'nome',
    sortOrder: 'asc'
  }
}

/**
 * Exemplo de Configuração Completa - Comandas
 */
export const exemploComandas = {
  name: 'comandas',
  title: 'Comandas',
  itemName: 'Comanda',
  apiEndpoint: 'comandas',
  description: 'Gestão completa de comandas do sistema',
  
  allowBulkActions: true,
  showExportImport: true,
  generateBackend: false,
  
  columns: [
    { key: 'numero', label: 'NÚMERO', type: 'text', sortable: true },
    { key: 'cardapio_digital', label: 'CARDÁPIO DIGITAL', type: 'boolean', sortable: true },
    { key: 'status', label: 'STATUS', type: 'status', sortable: true },
    { key: 'ativo', label: 'ATIVO', type: 'status', sortable: true }
  ],
  
  formFields: [
    {
      key: 'numero',
      label: 'Número da Comanda',
      type: 'text',
      required: true,
      placeholder: 'Digite o número da comanda',
      validation: {
        minLength: 1,
        maxLength: 10,
        pattern: '^[0-9A-Za-z]+$',
        message: 'Número deve conter apenas letras e números'
      }
    },
    {
      key: 'cardapio_digital',
      label: 'Cardápio Digital',
      type: 'select',
      required: true,
      defaultValue: true,
      options: [
        { value: true, label: 'Habilitado' },
        { value: false, label: 'Desabilitado' }
      ]
    },
    {
      key: 'ativo',
      label: 'Status',
      type: 'select',
      required: true,
      defaultValue: true,
      options: [
        { value: true, label: 'Ativo' },
        { value: false, label: 'Inativo' }
      ]
    }
  ],
  
  filters: [
    {
      key: 'numero',
      label: 'Número',
      type: 'text',
      placeholder: 'Filtrar por número'
    },
    {
      key: 'cardapio_digital',
      label: 'Cardápio Digital',
      type: 'select',
      options: [
        { value: '', label: 'Todos' },
        { value: 'true', label: 'Habilitado' },
        { value: 'false', label: 'Desabilitado' }
      ]
    }
  ],
  
  actions: {
    create: true,
    read: true,
    update: true,
    delete: true,
    export: true,
    import: true
  },
  
  validation: {
    uniqueFields: ['numero']
  },
  
  permissions: {
    roles: ['admin', 'promoter'],
    create: ['admin', 'promoter'],
    update: ['admin', 'promoter'],
    delete: ['admin']
  }
}

/**
 * Exemplo de Configuração Simples - Categorias
 */
export const exemploCategorias = {
  name: 'categorias',
  title: 'Categorias',
  itemName: 'Categoria',
  apiEndpoint: 'categorias', 
  description: 'Categorias para classificação de produtos e serviços',
  
  allowBulkActions: true,
  showExportImport: false,
  generateBackend: true,
  
  columns: [
    { key: 'nome', label: 'NOME', type: 'text' },
    { key: 'descricao', label: 'DESCRIÇÃO', type: 'text' },
    { key: 'cor', label: 'COR', type: 'color' },
    { key: 'total_produtos', label: 'PRODUTOS', type: 'number' },
    { key: 'ativo', label: 'STATUS', type: 'status' }
  ],
  
  formFields: [
    {
      key: 'nome',
      label: 'Nome da Categoria',
      type: 'text',
      required: true,
      placeholder: 'Ex: Bebidas, Lanches, Sobremesas...',
      maxLength: 100,
      helpText: 'Nome único para identificar a categoria'
    },
    {
      key: 'descricao',
      label: 'Descrição',
      type: 'textarea',
      required: false,
      placeholder: 'Descrição detalhada da categoria...',
      rows: 3,
      maxLength: 500,
      helpText: 'Descrição opcional para esclarecer o uso da categoria'
    },
    {
      key: 'cor',
      label: 'Cor da Categoria',
      type: 'color',
      required: false,
      defaultValue: '#6B46C1',
      helpText: 'Cor para identificação visual da categoria'
    },
    {
      key: 'icone',
      label: 'Ícone',
      type: 'select',
      required: false,
      placeholder: 'Selecione um ícone',
      options: [
        { value: 'food', label: '🍽️ Comida' },
        { value: 'drink', label: '🥤 Bebida' },
        { value: 'dessert', label: '🍰 Sobremesa' },
        { value: 'snack', label: '🍿 Lanche' },
        { value: 'pizza', label: '🍕 Pizza' },
        { value: 'burger', label: '🍔 Hambúrguer' },
        { value: 'coffee', label: '☕ Café' },
        { value: 'ice-cream', label: '🍦 Sorvete' }
      ]
    },
    {
      key: 'ordenacao',
      label: 'Ordem de Exibição',
      type: 'number',
      required: false,
      min: 1,
      max: 999,
      defaultValue: 1,
      helpText: 'Número para controlar a ordem de exibição (menor número aparece primeiro)'
    },
    {
      key: 'ativo',
      label: 'Status',
      type: 'checkbox',
      checkboxText: 'Categoria ativa',
      defaultValue: true,
      helpText: 'Categorias inativas não aparecem para seleção'
    }
  ],
  
  filters: [
    { key: 'nome', type: 'text', placeholder: 'Buscar por nome...' },
    { key: 'descricao', type: 'text', placeholder: 'Buscar na descrição...' }
  ],
  
  toggleFilters: [
    { key: 'apenas_ativas', label: 'Apenas categorias ativas' },
    { key: 'com_produtos', label: 'Com produtos cadastrados' }
  ]
}

/**
 * Exemplo de Configuração Minimalista - Tags
 */
export const exemploTags = {
  name: 'tags',
  title: 'Tags',
  itemName: 'Tag',
  apiEndpoint: 'tags',
  description: 'Tags para marcação e organização',
  
  allowBulkActions: true,
  showExportImport: false,
  
  columns: [
    { key: 'nome', label: 'NOME', type: 'text' },
    { key: 'cor', label: 'COR', type: 'color' },
    { key: 'uso_count', label: 'USOS', type: 'number' }
  ],
  
  formFields: [
    {
      key: 'nome',
      label: 'Nome da Tag',
      type: 'text',
      required: true,
      placeholder: 'Ex: Promocional, Sazonal, Popular...',
      maxLength: 50
    },
    {
      key: 'cor',
      label: 'Cor',
      type: 'color',
      required: false,
      defaultValue: '#6B46C1'
    }
  ],
  
  filters: [
    { key: 'nome', type: 'text', placeholder: 'Buscar tags...' }
  ]
}

// Exportar todos os exemplos
export const exemplosCadastros = {
  fornecedores: exemploFornecedores,
  categorias: exemploCategorias,
  tags: exemploTags
}

export default exemplosCadastros
