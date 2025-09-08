/**
 * Configuração do Módulo de Comandas
 * 
 * Este arquivo define a configuração completa para o módulo de cadastro de comandas,
 * incluindo campos do formulário, validações, filtros e permissões.
 */

export const comandasConfig = {
  name: 'comandas',
  title: 'Comandas',
  itemName: 'Comanda',
  apiEndpoint: 'comandas',
  description: 'Gestão completa de comandas do sistema',
  
  allowBulkActions: true,
  showExportImport: true,
  generateBackend: false, // Assumindo que já existe endpoint de comandas
  
  columns: [
    { key: 'numero', label: 'NÚMERO', type: 'text', sortable: true },
    { key: 'cardapio_digital', label: 'CARDÁPIO DIGITAL', type: 'boolean', sortable: true },
    { key: 'status', label: 'STATUS', type: 'status', sortable: true },
    { key: 'ativo', label: 'ATIVO', type: 'status', sortable: true },
    { key: 'created_at', label: 'CRIADO EM', type: 'datetime', sortable: true }
  ],
  
  formFields: [
    {
      key: 'numero',
      label: 'Número da Comanda',
      type: 'text',
      required: true,
      placeholder: 'Digite o número da comanda (ex: 001, 002, 003)',
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
      ],
      description: 'Define se a comanda terá acesso ao cardápio digital'
    },
    {
      key: 'qr_code',
      label: 'QR Code',
      type: 'text',
      required: false,
      placeholder: 'QR Code será gerado automaticamente',
      disabled: true,
      description: 'QR Code gerado automaticamente para acesso ao cardápio'
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
    },
    {
      key: 'observacoes',
      label: 'Observações',
      type: 'textarea',
      required: false,
      placeholder: 'Observações adicionais sobre a comanda',
      validation: {
        maxLength: 500,
        message: 'Observações não podem exceder 500 caracteres'
      }
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
    searchableFields: ['numero', 'observacoes'],
    placeholder: 'Buscar comandas...'
  },
  
  actions: {
    create: true,
    read: true,
    update: true,
    delete: true,
    export: true,
    import: true,
    customActions: [
      {
        key: 'generate_qr',
        label: 'Gerar QR Code',
        icon: 'qr-code',
        color: 'primary'
      },
      {
        key: 'print_qr',
        label: 'Imprimir QR',
        icon: 'printer',
        color: 'secondary'
      }
    ]
  },
  
  validation: {
    uniqueFields: ['numero'],
    
    // Validação customizada para comandas
    customValidation: async (field, value, apiService) => {
      if (field === 'numero' && value) {
        const result = await apiService.validateUnique('numero', value);
        if (!result.valid) {
          return 'Número de comanda já existe'
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
    sortBy: 'numero',
    sortOrder: 'asc',
    
    // Configurações específicas para comandas
    customColumns: {
      cardapio_digital: {
        render: (value) => value ? '🔗 Habilitado' : '❌ Desabilitado'
      },
      numero: {
        render: (value) => `#${value.toString().padStart(3, '0')}`
      }
    }
  },

  // Configurações específicas para comandas
  features: {
    autoGenerateQR: true,
    printSupport: true,
    bulkQRGeneration: true
  }
}

// Removido export default para usar named export
