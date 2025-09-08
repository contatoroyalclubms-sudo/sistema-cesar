// Configuração do módulo de formas de pagamento
export const formasPagamentoConfig = {
  "name": "formas-pagamento",
  "title": "Formas de Pagamento",
  "itemName": "Forma de Pagamento",
  "apiEndpoint": "formas-pagamento",
  "description": "Gestão completa das formas de pagamento aceitas no sistema",
  "allowBulkActions": true,
  "showExportImport": false,
  "generateBackend": false,
  
  "columns": [
    {
      "key": "nome",
      "label": "NOME",
      "type": "text",
      "sortable": true,
      "width": "250px"
    },
    {
      "key": "codigo",
      "label": "CÓDIGO",
      "type": "text",
      "sortable": true,
      "width": "120px"
    },
    {
      "key": "tipo",
      "label": "TIPO",
      "type": "badge",
      "sortable": true,
      "width": "150px",
      "badgeColors": {
        "DINHEIRO": "green",
        "PIX": "blue", 
        "CARTAO_CREDITO": "purple",
        "CARTAO_DEBITO": "indigo",
        "TRANSFERENCIA": "cyan",
        "BOLETO": "yellow",
        "VOUCHER": "pink",
        "CREDITO_LOJA": "orange"
      }
    },
    {
      "key": "taxa_percentual",
      "label": "TAXA (%)",
      "type": "currency",
      "sortable": true,
      "width": "100px",
      "format": "percentage"
    },
    {
      "key": "taxa_fixa",
      "label": "TAXA FIXA",
      "type": "currency", 
      "sortable": true,
      "width": "120px"
    },
    {
      "key": "status",
      "label": "STATUS",
      "type": "badge",
      "sortable": true,
      "width": "120px",
      "badgeColors": {
        "ATIVO": "green",
        "INATIVO": "red", 
        "MANUTENCAO": "yellow"
      }
    },
    {
      "key": "ativo",
      "label": "ATIVO",
      "type": "boolean",
      "sortable": true,
      "width": "80px"
    },
    {
      "key": "criado_em",
      "label": "CRIADO EM",
      "type": "datetime",
      "sortable": true,
      "width": "180px"
    }
  ],
  
  "fields": [
    {
      "key": "nome",
      "label": "Nome da Forma de Pagamento",
      "type": "text",
      "required": true,
      "placeholder": "Ex: Cartão de Crédito Visa",
      "maxLength": 100,
      "validation": {
        "minLength": 2,
        "message": "Nome deve ter pelo menos 2 caracteres"
      }
    },
    {
      "key": "codigo",
      "label": "Código Identificador",
      "type": "text",
      "required": true,
      "placeholder": "Ex: VISA_CREDITO",
      "maxLength": 50,
      "style": "uppercase",
      "validation": {
        "pattern": "^[A-Z0-9_]+$",
        "message": "Código deve conter apenas letras maiúsculas, números e underscore"
      }
    },
    {
      "key": "tipo",
      "label": "Tipo",
      "type": "select",
      "required": true,
      "options": [
        { "value": "DINHEIRO", "label": "Dinheiro" },
        { "value": "PIX", "label": "PIX" },
        { "value": "CARTAO_CREDITO", "label": "Cartão de Crédito" },
        { "value": "CARTAO_DEBITO", "label": "Cartão de Débito" },
        { "value": "TRANSFERENCIA", "label": "Transferência Bancária" },
        { "value": "BOLETO", "label": "Boleto Bancário" },
        { "value": "VOUCHER", "label": "Voucher" },
        { "value": "CREDITO_LOJA", "label": "Crédito da Loja" }
      ]
    },
    {
      "key": "status",
      "label": "Status",
      "type": "select",
      "required": true,
      "defaultValue": "ATIVO",
      "options": [
        { "value": "ATIVO", "label": "Ativo" },
        { "value": "INATIVO", "label": "Inativo" },
        { "value": "MANUTENCAO", "label": "Em Manutenção" }
      ]
    },
    {
      "key": "descricao",
      "label": "Descrição",
      "type": "textarea",
      "placeholder": "Descrição detalhada da forma de pagamento...",
      "rows": 3,
      "maxLength": 500
    },
    {
      "key": "taxa_percentual",
      "label": "Taxa Percentual (%)",
      "type": "number",
      "placeholder": "Ex: 2.50 para 2.5%",
      "min": 0,
      "max": 100,
      "step": 0.01,
      "defaultValue": 0
    },
    {
      "key": "taxa_fixa",
      "label": "Taxa Fixa (R$)",
      "type": "currency",
      "placeholder": "Ex: 1.50",
      "min": 0,
      "step": 0.01,
      "defaultValue": 0
    },
    {
      "key": "limite_minimo",
      "label": "Valor Mínimo (R$)",
      "type": "currency",
      "placeholder": "Ex: 5.00",
      "min": 0,
      "step": 0.01,
      "defaultValue": 0
    },
    {
      "key": "limite_maximo",
      "label": "Valor Máximo (R$)",
      "type": "currency",
      "placeholder": "Ex: 1000.00 (deixe em branco para ilimitado)",
      "min": 0,
      "step": 0.01
    },
    {
      "key": "ativo",
      "label": "Forma de Pagamento Ativa",
      "type": "checkbox",
      "checkboxText": "Esta forma de pagamento está disponível para uso",
      "defaultValue": true
    }
  ],
  
  "filters": [
    { 
      "key": "search", 
      "type": "text", 
      "placeholder": "Buscar por nome, código ou descrição...",
      "icon": "search"
    },
    { 
      "key": "tipo", 
      "type": "select", 
      "placeholder": "Filtrar por tipo",
      "options": [
        { "value": "", "label": "Todos os tipos" },
        { "value": "DINHEIRO", "label": "Dinheiro" },
        { "value": "PIX", "label": "PIX" },
        { "value": "CARTAO_CREDITO", "label": "Cartão de Crédito" },
        { "value": "CARTAO_DEBITO", "label": "Cartão de Débito" },
        { "value": "TRANSFERENCIA", "label": "Transferência" },
        { "value": "BOLETO", "label": "Boleto" },
        { "value": "VOUCHER", "label": "Voucher" },
        { "value": "CREDITO_LOJA", "label": "Crédito da Loja" }
      ]
    },
    { 
      "key": "status", 
      "type": "select", 
      "placeholder": "Filtrar por status",
      "options": [
        { "value": "", "label": "Todos os status" },
        { "value": "ATIVO", "label": "Ativo" },
        { "value": "INATIVO", "label": "Inativo" },
        { "value": "MANUTENCAO", "label": "Em Manutenção" }
      ]
    },
    { 
      "key": "ativo", 
      "type": "select", 
      "placeholder": "Filtrar por disponibilidade",
      "options": [
        { "value": "", "label": "Todos" },
        { "value": "true", "label": "Disponíveis" },
        { "value": "false", "label": "Indisponíveis" }
      ]
    }
  ],
  
  "pagination": {
    "defaultPage": 1,
    "defaultLimit": 25,
    "pageSizeOptions": [10, 25, 50, 100]
  },
  
  "permissions": {
    "view": ["admin", "promoter"],
    "create": ["admin", "promoter"],
    "edit": ["admin", "promoter"],
    "delete": ["admin"]
  },
  
  "layout": {
    "showHeader": true,
    "showFilters": true,
    "showPagination": true,
    "sortBy": "nome",
    "sortOrder": "asc"
  }
};
