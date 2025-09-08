/**
 * Gerador Automático de Módulos de Cadastro
 * Cria toda a estrutura necessária para um novo módulo seguindo os padrões estabelecidos
 */

import fs from 'fs'
import path from 'path'

// Templates para geração automática
const templates = {
  // Template para configuração de módulo
  moduleConfig: (config) => `
// Configuração do módulo ${config.name}
export const ${config.name}Config = {
  name: '${config.name}',
  title: '${config.title.toUpperCase()}',
  itemName: '${config.itemName}',
  storeName: '${config.name}',
  apiEndpoint: '${config.apiEndpoint}',
  createButtonText: '${config.createButtonText || `Novo ${config.itemName}`}',
  emptyMessage: '${config.emptyMessage || `NÃO HÁ ${config.title.toUpperCase()} CADASTRADOS`}',
  allowBulkActions: ${config.allowBulkActions || false},
  showExportImport: ${config.showExportImport || false},
  
  columns: [
    ${config.columns.map(col => `{ key: '${col.key}', label: '${col.label}', type: '${col.type}' }`).join(',\n    ')}
  ],
  
  formFields: [
    { key: 'id', type: 'hidden' },
    ${config.formFields.map(field => `{
      key: '${field.key}',
      label: '${field.label}',
      type: '${field.type}',
      required: ${field.required || false},
      placeholder: '${field.placeholder || ''}',
      ${field.maxLength ? `maxLength: ${field.maxLength},` : ''}
      ${field.min !== undefined ? `min: ${field.min},` : ''}
      ${field.max !== undefined ? `max: ${field.max},` : ''}
      ${field.options ? `options: ${JSON.stringify(field.options)},` : ''}
      ${field.validate ? `validate: ${field.validate.toString()},` : ''}
    }`).join(',\n    ')}
  ],
  
  ${config.filters ? `filters: [
    ${config.filters.map(filter => `{ key: '${filter.key}', type: '${filter.type}', placeholder: '${filter.placeholder}' }`).join(',\n    ')}
  ],` : ''}
  
  ${config.toggleFilters ? `toggleFilters: [
    ${config.toggleFilters.map(toggle => `{ key: '${toggle.key}', label: '${toggle.label}' }`).join(',\n    ')}
  ]` : ''}
}
`,

  // Template para componente Vue específico (se necessário customização)
  vueComponent: (config) => `
<template>
  <CadastroModule
    :module-config="${config.name}Config"
    :permissions="permissions"
  />
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import CadastroModule from '@/components/cadastro/CadastroModule.vue'
import { ${config.name}Config } from '@/config/modules/${config.name}Config.js'

export default {
  name: '${config.name.charAt(0).toUpperCase() + config.name.slice(1)}View',
  components: {
    CadastroModule
  },
  setup() {
    const store = useStore()
    
    const permissions = computed(() => {
      const user = store.state.auth.user
      
      if (!user) {
        return { create: false, edit: false, delete: false, view: false }
      }

      // Admin tem todas as permissões
      if (user.role === 'admin' || user.is_super_admin) {
        return { create: true, edit: true, delete: true, view: true, viewHistory: true }
      }

      // Verificar permissões específicas
      const userPermissions = user.permissions || []
      return {
        view: userPermissions.includes('${config.name}.view'),
        create: userPermissions.includes('${config.name}.create'),
        edit: userPermissions.includes('${config.name}.edit'),
        delete: userPermissions.includes('${config.name}.delete'),
        viewHistory: userPermissions.includes('${config.name}.history')
      }
    })
    
    return {
      ${config.name}Config,
      permissions
    }
  }
}
</script>
`,

  // Template para rota
  routeConfig: (config) => `
{
  path: '${config.routePath}',
  name: '${config.name.charAt(0).toUpperCase() + config.name.slice(1)}',
  component: ${config.customComponent ? `${config.name.charAt(0).toUpperCase() + config.name.slice(1)}View` : 'CadastroModule'},
  meta: { 
    title: '${config.title}',
    moduleName: '${config.name}',
    permissions: ['${config.name}.view'],
    breadcrumb: [
      { text: 'Cadastro', to: '/cadastro' },
      { text: '${config.title}' }
    ]
  }
},`,

  // Template para store module registration
  storeRegistration: (config) => `
${config.name}: createCrudModule(apiServices.${config.name}Api, '${config.itemName}'),`,

  // Template para API service
  apiService: (config) => `
export const ${config.name}Api = new ApiService('${config.apiEndpoint}')`,

  // Template para backend model (Python)
  backendModel: (config) => `
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ${config.itemName}(Base):
    __tablename__ = '${config.tableName || config.name}'
    
    id = Column(Integer, primary_key=True, index=True)
    ${config.formFields.filter(f => f.type !== 'hidden').map(field => {
      const sqlType = getSqlType(field.type)
      const nullable = !field.required
      return `${field.key} = Column(${sqlType}, nullable=${nullable})`
    }).join('\n    ')}
    
    # Campos de auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com estabelecimento (se aplicável)
    establishment_id = Column(Integer, ForeignKey('establishments.id'), nullable=False)
    
    def __repr__(self):
        return f"<${config.itemName}(id={self.id})>"
`,

  // Template para schema Pydantic
  backendSchema: (config) => `
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class ${config.itemName}Base(BaseModel):
    ${config.formFields.filter(f => f.type !== 'hidden').map(field => {
      const pythonType = getPythonType(field.type)
      const optional = !field.required ? 'Optional[' : ''
      const close = !field.required ? ']' : ''
      const defaultValue = field.defaultValue ? ` = ${JSON.stringify(field.defaultValue)}` : (!field.required ? ' = None' : '')
      return `${field.key}: ${optional}${pythonType}${close}${defaultValue}`
    }).join('\n    ')}

class ${config.itemName}Create(${config.itemName}Base):
    pass

class ${config.itemName}Update(${config.itemName}Base):
    pass

class ${config.itemName}(${config.itemName}Base):
    id: int
    created_at: datetime
    updated_at: datetime
    establishment_id: int
    
    class Config:
        from_attributes = True
`
}

// Funções auxiliares para conversão de tipos
function getSqlType(fieldType) {
  const typeMap = {
    'text': 'String(255)',
    'email': 'String(255)',
    'number': 'Integer',
    'currency': 'Numeric(10, 2)',
    'date': 'Date',
    'datetime': 'DateTime',
    'textarea': 'Text',
    'checkbox': 'Boolean',
    'select': 'String(100)',
    'file': 'String(500)'
  }
  return typeMap[fieldType] || 'String(255)'
}

function getPythonType(fieldType) {
  const typeMap = {
    'text': 'str',
    'email': 'str',
    'number': 'int',
    'currency': 'float',
    'date': 'date',
    'datetime': 'datetime',
    'textarea': 'str',
    'checkbox': 'bool',
    'select': 'str',
    'file': 'str'
  }
  return typeMap[fieldType] || 'str'
}

/**
 * Classe principal do gerador de módulos
 */
export class ModuleGenerator {
  constructor(projectPath) {
    this.projectPath = projectPath
    this.frontendPath = path.join(projectPath, 'frontend')
    this.backendPath = path.join(projectPath, 'backend')
  }

  /**
   * Gera um módulo completo com base na configuração
   * @param {Object} config - Configuração do módulo
   */
  async generateModule(config) {
    console.log(`🚀 Gerando módulo: ${config.name}`)
    
    try {
      // 1. Validar configuração
      this.validateConfig(config)
      
      // 2. Criar estrutura de diretórios
      await this.createDirectories(config)
      
      // 3. Gerar arquivos frontend
      await this.generateFrontendFiles(config)
      
      // 4. Gerar arquivos backend (se solicitado)
      if (config.generateBackend) {
        await this.generateBackendFiles(config)
      }
      
      // 5. Atualizar arquivos de configuração
      await this.updateConfigFiles(config)
      
      // 6. Gerar documentação
      await this.generateDocumentation(config)
      
      console.log(`✅ Módulo ${config.name} gerado com sucesso!`)
      
      return {
        success: true,
        message: `Módulo ${config.name} criado com sucesso`,
        files: this.getGeneratedFiles(config)
      }
      
    } catch (error) {
      console.error(`❌ Erro ao gerar módulo ${config.name}:`, error)
      throw error
    }
  }

  /**
   * Valida a configuração do módulo
   */
  validateConfig(config) {
    const required = ['name', 'title', 'itemName', 'columns', 'formFields']
    const missing = required.filter(field => !config[field])
    
    if (missing.length > 0) {
      throw new Error(`Campos obrigatórios faltando: ${missing.join(', ')}`)
    }

    // Validar formato do nome (apenas letras minúsculas)
    if (!/^[a-z][a-zA-Z0-9]*$/.test(config.name)) {
      throw new Error('Nome do módulo deve começar com letra minúscula e conter apenas letras e números')
    }

    // Validar colunas obrigatórias
    if (!config.columns.length) {
      throw new Error('Módulo deve ter pelo menos uma coluna')
    }

    // Validar campos do formulário
    if (!config.formFields.length) {
      throw new Error('Módulo deve ter pelo menos um campo de formulário')
    }
  }

  /**
   * Cria estrutura de diretórios
   */
  async createDirectories(config) {
    const dirs = [
      path.join(this.frontendPath, 'src', 'config', 'modules'),
      path.join(this.frontendPath, 'src', 'views', 'cadastro'),
      path.join(this.frontendPath, 'src', 'components', 'cadastro', config.name)
    ]

    if (config.generateBackend) {
      dirs.push(
        path.join(this.backendPath, 'app', 'models'),
        path.join(this.backendPath, 'app', 'schemas'),
        path.join(this.backendPath, 'app', 'routers')
      )
    }

    for (const dir of dirs) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
      }
    }
  }

  /**
   * Gera arquivos do frontend
   */
  async generateFrontendFiles(config) {
    // 1. Configuração do módulo
    const configPath = path.join(this.frontendPath, 'src', 'config', 'modules', `${config.name}Config.js`)
    fs.writeFileSync(configPath, templates.moduleConfig(config))

    // 2. Componente Vue (se customização necessária)
    if (config.customComponent) {
      const componentPath = path.join(this.frontendPath, 'src', 'views', 'cadastro', `${config.name.charAt(0).toUpperCase() + config.name.slice(1)}.vue`)
      fs.writeFileSync(componentPath, templates.vueComponent(config))
    }

    // 3. Componentes específicos (se houver)
    if (config.customComponents) {
      for (const [componentName, template] of Object.entries(config.customComponents)) {
        const componentPath = path.join(this.frontendPath, 'src', 'components', 'cadastro', config.name, `${componentName}.vue`)
        fs.writeFileSync(componentPath, template)
      }
    }
  }

  /**
   * Gera arquivos do backend
   */
  async generateBackendFiles(config) {
    // 1. Model SQLAlchemy
    const modelPath = path.join(this.backendPath, 'app', 'models', `${config.name}.py`)
    fs.writeFileSync(modelPath, templates.backendModel(config))

    // 2. Schema Pydantic
    const schemaPath = path.join(this.backendPath, 'app', 'schemas', `${config.name}.py`)
    fs.writeFileSync(schemaPath, templates.backendSchema(config))

    // 3. Router (CRUD endpoints)
    // const routerPath = path.join(this.backendPath, 'app', 'routers', `${config.name}.py`)
    // fs.writeFileSync(routerPath, templates.backendRouter(config))
  }

  /**
   * Atualiza arquivos de configuração existentes
   */
  async updateConfigFiles(config) {
    // 1. Atualizar moduleConfig.js principal
    const moduleConfigPath = path.join(this.frontendPath, 'src', 'config', 'moduleConfig.js')
    if (fs.existsSync(moduleConfigPath)) {
      let content = fs.readFileSync(moduleConfigPath, 'utf8')
      
      // Adicionar import
      const importLine = `import { ${config.name}Config } from './modules/${config.name}Config.js'`
      if (!content.includes(importLine)) {
        content = content.replace(
          /\/\/ Module configurations export/,
          `${importLine}\n\n// Module configurations export`
        )
      }
      
      // Adicionar ao moduleConfigs
      const configLine = `  ${config.name}: ${config.name}Config,`
      if (!content.includes(configLine)) {
        content = content.replace(
          /export const moduleConfigs = {/,
          `export const moduleConfigs = {\n${configLine}`
        )
      }
      
      fs.writeFileSync(moduleConfigPath, content)
    }

    // 2. Atualizar API services
    const apiPath = path.join(this.frontendPath, 'src', 'services', 'api.js')
    if (fs.existsSync(apiPath)) {
      let content = fs.readFileSync(apiPath, 'utf8')
      
      // Adicionar API service
      const apiLine = templates.apiService(config)
      if (!content.includes(`${config.name}Api`)) {
        content = content.replace(
          /export const linksPagamentoApi/,
          `export const linksPagamentoApi${apiLine.replace('export const', '\nexport const')}`
        )
      }
      
      fs.writeFileSync(apiPath, content)
    }

    // 3. Atualizar store
    const storePath = path.join(this.frontendPath, 'src', 'store', 'index.js')
    if (fs.existsSync(storePath)) {
      let content = fs.readFileSync(storePath, 'utf8')
      
      // Adicionar módulo ao store
      const storeModule = templates.storeRegistration(config)
      if (!content.includes(`${config.name}:`)) {
        content = content.replace(
          /linksPagamento: createCrudModule\(apiServices\.linksPagamentoApi, 'Link de Pagamento'\)/,
          `linksPagamento: createCrudModule(apiServices.linksPagamentoApi, 'Link de Pagamento'),\n    ${storeModule.trim()}`
        )
      }
      
      fs.writeFileSync(storePath, content)
    }

    // 4. Atualizar router
    const routerPath = path.join(this.frontendPath, 'src', 'router', 'index.js')
    if (fs.existsSync(routerPath)) {
      let content = fs.readFileSync(routerPath, 'utf8')
      
      // Adicionar rota
      const routeConfig = templates.routeConfig({
        ...config,
        routePath: `/cadastro/${config.name}`
      })
      
      if (!content.includes(`path: '/cadastro/${config.name}'`)) {
        content = content.replace(
          /path: 'links-pagamento'/,
          `path: 'links-pagamento'${routeConfig.replace(/^{/, '\n          },\n          {')}`.replace(/,$/, '')
        )
      }
      
      fs.writeFileSync(routerPath, content)
    }
  }

  /**
   * Gera documentação do módulo
   */
  async generateDocumentation(config) {
    const docContent = `
# Módulo ${config.title}

## Descrição
${config.description || `Módulo para gerenciamento de ${config.title.toLowerCase()}`}

## Funcionalidades
- ✅ Listagem com filtros e paginação
- ✅ Criação de novos registros
- ✅ Edição de registros existentes
- ✅ Exclusão de registros
${config.allowBulkActions ? '- ✅ Ações em lote' : ''}
${config.showExportImport ? '- ✅ Importação/Exportação' : ''}

## Campos
${config.formFields.map(field => `- **${field.label}** (${field.type})${field.required ? ' *obrigatório*' : ''}`).join('\n')}

## Permissões
- \`${config.name}.view\` - Visualizar listagem
- \`${config.name}.create\` - Criar novos registros
- \`${config.name}.edit\` - Editar registros
- \`${config.name}.delete\` - Excluir registros
- \`${config.name}.history\` - Visualizar histórico

## API Endpoints
- \`GET /api/${config.apiEndpoint}\` - Listar registros
- \`POST /api/${config.apiEndpoint}\` - Criar registro
- \`PUT /api/${config.apiEndpoint}/{id}\` - Atualizar registro
- \`DELETE /api/${config.apiEndpoint}/{id}\` - Excluir registro

## Arquivos Gerados
${this.getGeneratedFiles(config).map(file => `- \`${file}\``).join('\n')}

---
*Gerado automaticamente pelo ModuleGenerator em ${new Date().toISOString()}*
`

    const docPath = path.join(this.projectPath, 'docs', 'modules', `${config.name}.md`)
    fs.mkdirSync(path.dirname(docPath), { recursive: true })
    fs.writeFileSync(docPath, docContent)
  }

  /**
   * Retorna lista de arquivos que serão gerados
   */
  getGeneratedFiles(config) {
    const files = [
      `frontend/src/config/modules/${config.name}Config.js`,
      `docs/modules/${config.name}.md`
    ]

    if (config.customComponent) {
      files.push(`frontend/src/views/cadastro/${config.name.charAt(0).toUpperCase() + config.name.slice(1)}.vue`)
    }

    if (config.generateBackend) {
      files.push(
        `backend/app/models/${config.name}.py`,
        `backend/app/schemas/${config.name}.py`
      )
    }

    return files
  }
}

// Exemplos de configurações de módulos
export const moduleExamples = {
  fornecedores: {
    name: 'fornecedores',
    title: 'Fornecedores',
    itemName: 'Fornecedor',
    apiEndpoint: 'fornecedores',
    description: 'Cadastro de fornecedores da empresa',
    allowBulkActions: true,
    showExportImport: true,
    
    columns: [
      { key: 'razao_social', label: 'RAZÃO SOCIAL', type: 'text' },
      { key: 'nome_fantasia', label: 'NOME FANTASIA', type: 'text' },
      { key: 'cnpj', label: 'CNPJ', type: 'text' },
      { key: 'telefone', label: 'TELEFONE', type: 'text' },
      { key: 'email', label: 'E-MAIL', type: 'text' },
      { key: 'status', label: 'STATUS', type: 'status' }
    ],
    
    formFields: [
      {
        key: 'razao_social',
        label: 'Razão Social',
        type: 'text',
        required: true,
        placeholder: 'Razão social da empresa',
        maxLength: 200
      },
      {
        key: 'nome_fantasia',
        label: 'Nome Fantasia',
        type: 'text',
        required: false,
        placeholder: 'Nome fantasia da empresa',
        maxLength: 200
      },
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
        }
      },
      {
        key: 'telefone',
        label: 'Telefone',
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
        placeholder: 'contato@empresa.com'
      },
      {
        key: 'endereco',
        label: 'Endereço',
        type: 'textarea',
        required: false,
        placeholder: 'Endereço completo',
        rows: 3
      },
      {
        key: 'observacoes',
        label: 'Observações',
        type: 'textarea',
        required: false,
        placeholder: 'Observações sobre o fornecedor',
        rows: 3
      },
      {
        key: 'ativo',
        label: 'Status',
        type: 'checkbox',
        checkboxText: 'Fornecedor ativo',
        defaultValue: true
      }
    ],
    
    filters: [
      { key: 'razao_social', type: 'text', placeholder: 'Razão Social' },
      { key: 'cnpj', type: 'text', placeholder: 'CNPJ' },
      { key: 'email', type: 'text', placeholder: 'E-mail' }
    ],
    
    generateBackend: true
  },

  categorias: {
    name: 'categorias',
    title: 'Categorias',
    itemName: 'Categoria',
    apiEndpoint: 'categorias',
    description: 'Categorias para classificação de produtos e serviços',
    allowBulkActions: true,
    
    columns: [
      { key: 'nome', label: 'NOME', type: 'text' },
      { key: 'descricao', label: 'DESCRIÇÃO', type: 'text' },
      { key: 'cor', label: 'COR', type: 'color' },
      { key: 'ativo', label: 'STATUS', type: 'status' }
    ],
    
    formFields: [
      {
        key: 'nome',
        label: 'Nome',
        type: 'text',
        required: true,
        placeholder: 'Nome da categoria',
        maxLength: 100
      },
      {
        key: 'descricao',
        label: 'Descrição',
        type: 'textarea',
        required: false,
        placeholder: 'Descrição detalhada da categoria',
        rows: 3
      },
      {
        key: 'cor',
        label: 'Cor',
        type: 'color',
        required: false,
        defaultValue: '#6B46C1'
      },
      {
        key: 'ativo',
        label: 'Status',
        type: 'checkbox',
        checkboxText: 'Categoria ativa',
        defaultValue: true
      }
    ],
    
    filters: [
      { key: 'nome', type: 'text', placeholder: 'Nome da categoria' }
    ],
    
    generateBackend: true
  }
}

export default ModuleGenerator
