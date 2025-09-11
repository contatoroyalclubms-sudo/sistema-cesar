// Configuração do módulo de clientes
export const clientesConfig = {
  "name": "clientes",
  "title": "Clientes",
  "itemName": "Cliente",
  "apiEndpoint": "meep/clientes",
  "description": "Gestão completa de clientes do sistema",
  "allowBulkActions": true,
  "showExportImport": true,
  "generateBackend": false,
  "columns": [
    {
      "key": "nome_completo",
      "label": "NOME COMPLETO",
      "type": "text",
      "sortable": true
    },
    {
      "key": "cpf",
      "label": "CPF",
      "type": "cpf",
      "sortable": true
    },
    {
      "key": "email",
      "label": "EMAIL",
      "type": "email",
      "sortable": true
    },
    {
      "key": "telefone",
      "label": "TELEFONE",
      "type": "phone",
      "sortable": true
    },
    {
      "key": "data_nascimento",
      "label": "DATA NASCIMENTO",
      "type": "date",
      "sortable": true
    },
    {
      "key": "status",
      "label": "STATUS",
      "type": "status",
      "sortable": true
    }
  ],
  "formFields": [
    {
      "key": "nome_completo",
      "label": "Nome Completo",
      "type": "text",
      "required": true,
      "placeholder": "Digite o nome completo",
      "validation": {
        "minLength": 3,
        "maxLength": 100,
        "pattern": "^[A-Za-zÀ-ÿ\\s]+$",
        "message": "Nome deve conter apenas letras e espaços"
      }
    },
    {
      "key": "cpf",
      "label": "CPF",
      "type": "cpf",
      "required": true,
      "placeholder": "000.000.000-00",
      "validation": {
        "cpf": true,
        "message": "CPF inválido"
      }
    },
    {
      "key": "email",
      "label": "Email",
      "type": "email",
      "required": true,
      "placeholder": "exemplo@email.com",
      "validation": {
        "email": true,
        "message": "Email inválido"
      }
    },
    {
      "key": "telefone",
      "label": "Telefone",
      "type": "phone",
      "required": true,
      "placeholder": "(11) 99999-9999",
      "validation": {
        "phone": true,
        "message": "Telefone inválido"
      }
    },
    {
      "key": "nome_social",
      "label": "Nome Social",
      "type": "text",
      "required": false,
      "placeholder": "Nome social (opcional)",
      "validation": {
        "maxLength": 100
      }
    },
    {
      "key": "data_nascimento",
      "label": "Data de Nascimento",
      "type": "date",
      "required": false,
      "validation": {
        "maxDate": "today",
        "message": "Data deve ser anterior a hoje"
      }
    },
    {
      "key": "nome_mae",
      "label": "Nome da Mãe",
      "type": "text",
      "required": false,
      "placeholder": "Nome da mãe (opcional)",
      "validation": {
        "maxLength": 100
      }
    },
    {
      "key": "status",
      "label": "Status",
      "type": "select",
      "required": true,
      "defaultValue": "ativo",
      "options": [
        {
          "value": "ativo",
          "label": "Ativo"
        },
        {
          "value": "inativo",
          "label": "Inativo"
        },
        {
          "value": "suspenso",
          "label": "Suspenso"
        }
      ]
    }
  ],
  "filters": [
    {
      "key": "nome_completo",
      "label": "Nome",
      "type": "text",
      "placeholder": "Filtrar por nome"
    },
    {
      "key": "cpf",
      "label": "CPF",
      "type": "text",
      "placeholder": "Filtrar por CPF"
    },
    {
      "key": "email",
      "label": "Email",
      "type": "text",
      "placeholder": "Filtrar por email"
    },
    {
      "key": "status",
      "label": "Status",
      "type": "select",
      "options": [
        {
          "value": "",
          "label": "Todos"
        },
        {
          "value": "ativo",
          "label": "Ativo"
        },
        {
          "value": "inativo",
          "label": "Inativo"
        },
        {
          "value": "suspenso",
          "label": "Suspenso"
        }
      ]
    }
  ],
  "searchConfig": {
    "searchableFields": [
      "nome_completo",
      "cpf",
      "email",
      "telefone"
    ],
    "placeholder": "Buscar clientes..."
  },
  "actions": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "export": true,
    "import": true
  },
  "permissions": {
    "roles": [
      "admin",
      "promoter"
    ],
    "create": [
      "admin",
      "promoter"
    ],
    "update": [
      "admin",
      "promoter"
    ],
    "delete": [
      "admin"
    ],
    "export": [
      "admin",
      "promoter"
    ],
    "import": [
      "admin"
    ]
  },
  "ui": {
    "itemsPerPage": 25,
    "showPagination": true,
    "showSearch": true,
    "showFilters": true,
    "showBulkActions": true,
    "sortBy": "nome_completo",
    "sortOrder": "asc"
  }
};
