/**
 * Script para gerar módulo de clientes usando o sistema modular
 */

// Configuração do módulo clientes baseada no exemploClientes
const clientesConfig = {
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

// Gerar os arquivos do módulo
import fs from 'fs'
import path from 'path'

const frontendPath = './frontend/src'

// Criar diretórios necessários
const createDirectories = () => {
  const dirs = [
    `${frontendPath}/components/clientes`,
    `${frontendPath}/services`,
    `${frontendPath}/store/modules`,
    `${frontendPath}/config/modules`
  ]
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true })
      console.log(`✅ Diretório criado: ${dir}`)
    }
  })
}

// Template para o componente principal
const createMainComponent = () => {
  const content = `import React from 'react';
import CadastroModule from '../common/CadastroModule';
import { clientesConfig } from '../../config/modules/clientesConfig';

export default function ClientesModule() {
  return (
    <CadastroModule 
      config={clientesConfig}
      title="Gestão de Clientes"
      description="Gerenciar clientes do sistema"
    />
  );
}
`

  fs.writeFileSync(`${frontendPath}/components/clientes/ClientesModule.tsx`, content)
  console.log('✅ Componente principal criado: ClientesModule.tsx')
}

// Template para configuração do módulo
const createModuleConfig = () => {
  const content = `// Configuração do módulo de clientes
export const clientesConfig = ${JSON.stringify(clientesConfig, null, 2)};
`

  fs.writeFileSync(`${frontendPath}/config/modules/clientesConfig.js`, content)
  console.log('✅ Configuração criada: clientesConfig.js')
}

// Template para o serviço API
const createApiService = () => {
  const content = `import apiClient from '../apiClient';

class ClientesService {
  async getAll(params = {}) {
    const response = await apiClient.get('/meep/clientes', { params });
    return response.data;
  }

  async getById(id) {
    const response = await apiClient.get(\`/meep/clientes/\${id}\`);
    return response.data;
  }

  async create(cliente) {
    const response = await apiClient.post('/meep/clientes', cliente);
    return response.data;
  }

  async update(id, cliente) {
    const response = await apiClient.put(\`/meep/clientes/\${id}\`, cliente);
    return response.data;
  }

  async delete(id) {
    const response = await apiClient.delete(\`/meep/clientes/\${id}\`);
    return response.data;
  }

  async validateUnique(field, value) {
    try {
      const response = await apiClient.get(\`/meep/clientes/validate/\${field}/\${value}\`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 409) {
        return { valid: false };
      }
      throw error;
    }
  }
}

export default new ClientesService();
`

  fs.writeFileSync(`${frontendPath}/services/clientesService.js`, content)
  console.log('✅ Serviço API criado: clientesService.js')
}

// Executar geração
console.log('🚀 Gerando módulo de clientes...')
createDirectories()
createMainComponent()
createModuleConfig()
createApiService()
console.log('✅ Módulo de clientes gerado com sucesso!')
console.log('\n📝 Próximos passos:')
console.log('1. Adicionar rota no App.tsx')
console.log('2. Adicionar link na navegação (Layout.tsx)')
console.log('3. Importar o módulo onde necessário')
