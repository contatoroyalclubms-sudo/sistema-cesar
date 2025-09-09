# 🔧 Sistema Modular de Cadastros - MeepFood

## 📋 Visão Geral

Este sistema permite a criação rápida e padronizada de módulos de cadastro para o portal MeepFood, seguindo uma arquitetura modular que garante consistência visual, funcionalidade completa e manutenibilidade.

## 🏗️ Arquitetura

### Componentes Base
- **CadastroModule.vue** - Container principal com breadcrumb, loading, error handling
- **CadastroList.vue** - Listagem genérica com filtros, paginação, ações CRUD
- **FormModal.vue** - Formulário modal genérico com validação
- **ConfirmDialog.vue** - Modal de confirmação para exclusões
- **ImportModal.vue** - Modal para importação de dados
- **HelpModal.vue** - Modal de ajuda contextual

### Store Pattern
- **createCrudModule()** - Factory para módulos CRUD genéricos
- State management padronizado com Vuex
- Actions, mutations e getters reutilizáveis
- Integração automática com notificações

### API Services
- **ApiService** - Classe genérica para operações CRUD
- Interceptors para autenticação e contexto de estabelecimento
- Suporte para file uploads, export/import
- Error handling padronizado

### Configuração Modular
- **moduleConfig.js** - Define estrutura e comportamento de cada módulo
- Configuração declarativa de colunas, campos, filtros
- Validações customizáveis por campo
- Sistema de permissões integrado

## 🚀 Como Usar

### 1. Instalação das Dependências

```bash
# Instalar dependências do CLI
npm install readline fs path

# Dar permissão de execução (Linux/Mac)
chmod +x generate-module.js
```

### 2. Geração de Módulos

#### Modo Interativo (Recomendado)
```bash
node generate-module.js --interactive
```

#### Usando Exemplos Pré-definidos
```bash
# Listar exemplos disponíveis
node generate-module.js --list-examples

# Gerar módulo de fornecedores
node generate-module.js fornecedores

# Gerar módulo de categorias
node generate-module.js categorias
```

#### Usando Arquivo de Configuração
```bash
node generate-module.js --config=meu-modulo.json
```

### 3. Validação do Projeto
```bash
# Validar estrutura do projeto
node generate-module.js --validate
```

## 📝 Estrutura de Configuração

### Exemplo Completo - Fornecedores

```javascript
{
  "name": "fornecedores",
  "title": "Fornecedores", 
  "itemName": "Fornecedor",
  "apiEndpoint": "fornecedores",
  "description": "Cadastro de fornecedores da empresa",
  "allowBulkActions": true,
  "showExportImport": true,
  "generateBackend": true,
  
  "columns": [
    { "key": "razao_social", "label": "RAZÃO SOCIAL", "type": "text" },
    { "key": "nome_fantasia", "label": "NOME FANTASIA", "type": "text" },
    { "key": "cnpj", "label": "CNPJ", "type": "text" },
    { "key": "telefone", "label": "TELEFONE", "type": "text" },
    { "key": "email", "label": "E-MAIL", "type": "text" },
    { "key": "status", "label": "STATUS", "type": "status" }
  ],
  
  "formFields": [
    {
      "key": "razao_social",
      "label": "Razão Social",
      "type": "text",
      "required": true,
      "placeholder": "Razão social da empresa",
      "maxLength": 200
    },
    {
      "key": "cnpj",
      "label": "CNPJ",
      "type": "text",
      "required": true,
      "placeholder": "00.000.000/0000-00",
      "maxLength": 18,
      "validate": "value => /^\\d{2}\\.\\d{3}\\.\\d{3}\\/\\d{4}-\\d{2}$/.test(value) || 'CNPJ inválido'"
    },
    {
      "key": "ativo",
      "label": "Status",
      "type": "checkbox",
      "checkboxText": "Fornecedor ativo",
      "defaultValue": true
    }
  ],
  
  "filters": [
    { "key": "razao_social", "type": "text", "placeholder": "Razão Social" },
    { "key": "cnpj", "type": "text", "placeholder": "CNPJ" }
  ]
}
```

### Propriedades da Configuração

#### Informações Básicas
- **name** (string) - Nome único do módulo (lowercase, sem espaços)
- **title** (string) - Título exibido na interface
- **itemName** (string) - Nome singular do item (ex: "Cliente", "Produto")
- **apiEndpoint** (string) - Endpoint da API (ex: "clientes")
- **description** (string) - Descrição do módulo

#### Configurações de UI
- **allowBulkActions** (boolean) - Habilita ações em lote
- **showExportImport** (boolean) - Mostra opções de importação/exportação
- **createButtonText** (string) - Texto do botão de criar (opcional)
- **emptyMessage** (string) - Mensagem quando não há dados (opcional)

#### Geração de Código
- **generateBackend** (boolean) - Gera modelos Python/SQLAlchemy
- **customComponent** (boolean) - Cria componente Vue específico
- **customComponents** (object) - Componentes adicionais personalizados

### Tipos de Campos Suportados

#### Campos de Input
```javascript
// Texto simples
{ "key": "nome", "label": "Nome", "type": "text", "required": true }

// Email com validação
{ "key": "email", "label": "E-mail", "type": "email" }

// Número com min/max
{ "key": "idade", "label": "Idade", "type": "number", "min": 0, "max": 120 }

// Moeda
{ "key": "preco", "label": "Preço", "type": "currency" }

// Data
{ "key": "nascimento", "label": "Data de Nascimento", "type": "date" }

// Textarea
{ "key": "observacoes", "label": "Observações", "type": "textarea", "rows": 3 }
```

#### Campos de Seleção
```javascript
// Select dropdown
{
  "key": "categoria",
  "label": "Categoria", 
  "type": "select",
  "options": [
    { "value": "a", "label": "Categoria A" },
    { "value": "b", "label": "Categoria B" }
  ]
}

// Radio buttons
{
  "key": "tipo",
  "label": "Tipo",
  "type": "radio", 
  "options": [
    { "value": "fisica", "label": "Pessoa Física" },
    { "value": "juridica", "label": "Pessoa Jurídica" }
  ]
}

// Checkbox
{ "key": "ativo", "label": "Ativo", "type": "checkbox", "checkboxText": "Cliente ativo" }
```

#### Upload de Arquivos
```javascript
{
  "key": "foto",
  "label": "Foto",
  "type": "file",
  "accept": "image/*",
  "multiple": false
}
```

### Validações Customizadas

```javascript
{
  "key": "cpf",
  "label": "CPF",
  "type": "text",
  "validate": "value => /^\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}$/.test(value) || 'CPF inválido'"
}
```

### Tipos de Colunas da Tabela

```javascript
// Texto simples
{ "key": "nome", "label": "NOME", "type": "text" }

// Status com cores
{ "key": "status", "label": "STATUS", "type": "status" }

// Moeda formatada
{ "key": "valor", "label": "VALOR", "type": "currency" }

// Data formatada
{ "key": "criado_em", "label": "CRIADO EM", "type": "date" }

// Link/botão
{ "key": "site", "label": "SITE", "type": "link" }

// Cor
{ "key": "cor", "label": "COR", "type": "color" }
```

## 🔧 Funcionalidades Incluídas

### Para Todos os Módulos
- ✅ **CRUD Completo** - Criar, listar, editar, excluir
- ✅ **Filtros de Busca** - Configuráveis por campo
- ✅ **Paginação** - Automática com controles
- ✅ **Validação** - Client-side e server-side
- ✅ **Responsividade** - Interface mobile-friendly
- ✅ **Permissões** - Sistema integrado de controle de acesso
- ✅ **Notificações** - Feedback automático de ações
- ✅ **Loading States** - Indicadores visuais de carregamento
- ✅ **Error Handling** - Tratamento padronizado de erros

### Opcionais (Configuráveis)
- 🔄 **Ações em Lote** - Excluir múltiplos registros
- 📤 **Exportação** - Download de dados em Excel
- 📥 **Importação** - Upload de planilhas
- 📜 **Histórico** - Log de alterações
- 🆘 **Ajuda Contextual** - Modais explicativos
- 🔍 **Busca Avançada** - Filtros complexos

## 🛡️ Sistema de Validação

O sistema inclui validação automática para garantir compatibilidade:

### Validações Executadas
1. **Estrutura Básica** - Campos obrigatórios presentes
2. **Conflitos de Nome** - Evita duplicação de módulos
3. **Dependências** - Verifica arquivos necessários
4. **Rotas** - Valida configuração do router
5. **API Endpoints** - Previne conflitos de URL
6. **Permissões** - Verifica padrões de nomenclatura
7. **Campos** - Valida tipos e configurações

### Exemplo de Uso
```bash
# Validar antes de gerar
node generate-module.js --validate

# Gerar com validação automática
node generate-module.js --interactive
```

## 📂 Estrutura de Arquivos Gerados

Para o módulo `fornecedores`, são criados:

```
frontend/
├── src/
│   ├── config/modules/
│   │   └── fornecedoresConfig.js      # Configuração do módulo
│   └── views/cadastro/
│       └── Fornecedores.vue           # Componente específico (se customComponent: true)
│
backend/                                # Se generateBackend: true
├── app/
│   ├── models/
│   │   └── fornecedores.py            # Modelo SQLAlchemy
│   └── schemas/
│       └── fornecedores.py            # Schemas Pydantic
│
docs/
├── modules/
│   └── fornecedores.md                # Documentação automática
└── compatibility-reports/
    └── fornecedores-compatibility.json # Relatório de validação
```

### Atualizações Automáticas

O gerador atualiza automaticamente:
- `frontend/src/config/moduleConfig.js` - Adiciona configuração
- `frontend/src/services/api.js` - Registra API service
- `frontend/src/store/index.js` - Adiciona store module
- `frontend/src/router/index.js` - Configura rota

## 🎨 Personalização

### Temas de Cores
O sistema usa as cores padrão do MeepFood:
- **Primária:** #6B46C1 (roxo)
- **Secundária:** #1E40AF (azul escuro)
- **Sucesso:** #059669 (verde)
- **Erro:** #DC2626 (vermelho)

### Estilos Customizados
```css
/* Personalizar cores de status */
.status.ativo { background: #D1FAE5; color: #065F46; }
.status.inativo { background: #FEE2E2; color: #991B1B; }

/* Personalizar tabela */
.data-table .table-header { background: #9CA3AF; }
.data-table .table-row:hover { background: #F9FAFB; }
```

## 🔒 Sistema de Permissões

### Padrão de Nomenclatura
- `{modulo}.view` - Visualizar listagem
- `{modulo}.create` - Criar novos registros
- `{modulo}.edit` - Editar registros existentes
- `{modulo}.delete` - Excluir registros
- `{modulo}.history` - Visualizar histórico (opcional)

### Exemplo para Fornecedores
```javascript
const permissions = [
  'fornecedores.view',
  'fornecedores.create', 
  'fornecedores.edit',
  'fornecedores.delete',
  'fornecedores.history'
]
```

### Verificação no Frontend
```javascript
// Automática nos componentes
const canCreate = computed(() => permissions.value.create)
const canEdit = computed(() => permissions.value.edit)
const canDelete = computed(() => permissions.value.delete)
```

## 🧪 Testes

### Validação Automática
```bash
# Testar configuração antes de gerar
const validator = new CompatibilityValidator('./projeto')
const result = await validator.validateModule(config)

if (!result.valid) {
  console.log('Erros:', result.errors)
  console.log('Avisos:', result.warnings)
}
```

### Testes de Integração
```bash
# Testar integração do módulo
const testResult = await validator.testModuleIntegration(config)
console.log(`Testes: ${testResult.passed}/${testResult.total} passaram`)
```

## 🚀 Deploy

### Desenvolvimento
1. Gere o módulo desejado
2. Reinicie o servidor de desenvolvimento
3. Acesse `/cadastro/{nome-do-modulo}` no navegador

### Produção
1. Configure as permissões no backend
2. Execute migrations se necessário
3. Build e deploy do frontend
4. Teste todas as funcionalidades

## 🆘 Solução de Problemas

### Erro: "Módulo já existe"
```bash
# Remover módulo existente primeiro
rm frontend/src/config/modules/{modulo}Config.js
# Limpar referências manuais nos arquivos de configuração
```

### Erro: "Arquivo necessário não encontrado"
```bash
# Validar estrutura do projeto
node generate-module.js --validate

# Verificar se está na raiz do projeto
ls frontend/src/components/cadastro/
```

### Erro: "Permissões não funcionando"
1. Verificar se usuário tem permissões no backend
2. Confirmar formato: `{modulo}.{acao}`
3. Verificar se store auth está carregado

## 📚 Exemplos Práticos

### 1. Módulo Simples - Categorias
```bash
node generate-module.js categorias
```

### 2. Módulo Complexo - Fornecedores  
```bash
node generate-module.js fornecedores
```

### 3. Módulo Customizado - Modo Interativo
```bash
node generate-module.js --interactive
```

### 4. Módulo a partir de Arquivo
```bash
# Criar arquivo config.json com a configuração
node generate-module.js --config=config.json
```

## 🔄 Atualizações e Manutenção

### Adicionando Campos a Módulo Existente
1. Editar arquivo `{modulo}Config.js`
2. Adicionar campo em `formFields[]` e `columns[]`
3. Atualizar backend se necessário
4. Testar em desenvolvimento

### Atualizando Componentes Base
Os componentes base são compartilhados por todos os módulos. Alterações devem ser testadas em múltiplos módulos para garantir compatibilidade.

### Versionamento
- Manter backup das configurações em `docs/modules/`
- Documentar mudanças significativas
- Testar compatibilidade antes de atualizações

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação completa
2. Execute `node generate-module.js --help`
3. Verifique os logs de erro detalhados
4. Consulte exemplos na pasta `docs/modules/`

**Desenvolvido para o ecossistema MeepFood** 🍽️

---

*Última atualização: ${new Date().toISOString()}*
