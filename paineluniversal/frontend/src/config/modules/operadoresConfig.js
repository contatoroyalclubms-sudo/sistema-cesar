/**
 * Configuração do Módulo de Operadores
 * 
 * Este arquivo define a configuração completa para o módulo de cadastro de operadores,
 * incluindo campos do formulário, validações, filtros e permissões.
 */

export const operadoresConfig = {
  name: 'operadores',
  title: 'Operadores',
  itemName: 'Operador',
  apiEndpoint: 'usuarios', // Usar endpoint de usuários com filtro tipo=promoter
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
  },

  // Configurações específicas para operadores
  filters: {
    // Filtro automático para mostrar apenas usuários do tipo promoter
    defaultFilters: {
      tipo: 'promoter'
    }
  }
}
