#!/usr/bin/env node

/**
 * CLI para geração automática de módulos de cadastro
 * Uso: node generate-module.js [nome-do-modulo] [--interactive] [--config=arquivo.json]
 */

import { ModuleGenerator, moduleExamples } from './frontend/src/utils/moduleGenerator.js'
import fs from 'fs'
import path from 'path'
import readline from 'readline'

// Configuração do CLI
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
})

class ModuleCLI {
  constructor() {
    this.projectPath = process.cwd()
    this.generator = new ModuleGenerator(this.projectPath)
  }

  /**
   * Executa o CLI principal
   */
  async run() {
    console.log('🔧 Gerador de Módulos de Cadastro - MeepFood\n')
    
    const args = process.argv.slice(2)
    
    if (args.includes('--help') || args.includes('-h')) {
      this.showHelp()
      return
    }

    if (args.includes('--list-examples')) {
      this.listExamples()
      return
    }

    if (args.includes('--validate')) {
      await this.validateProject()
      return
    }

    // Modo interativo
    if (args.includes('--interactive') || args.length === 0) {
      await this.interactiveMode()
      return
    }

    // Gerar a partir de arquivo de configuração
    const configFlag = args.find(arg => arg.startsWith('--config='))
    if (configFlag) {
      const configFile = configFlag.split('=')[1]
      await this.generateFromConfig(configFile)
      return
    }

    // Gerar usando exemplo
    const moduleName = args[0]
    if (moduleExamples[moduleName]) {
      await this.generateFromExample(moduleName)
      return
    }

    console.log('❌ Módulo não encontrado. Use --list-examples para ver exemplos disponíveis.')
  }

  /**
   * Modo interativo para criação de módulos
   */
  async interactiveMode() {
    console.log('📝 Modo Interativo - Criação de Módulo\n')

    try {
      const config = {}

      // Informações básicas
      config.name = await this.ask('Nome do módulo (ex: fornecedores): ')
      config.title = await this.ask('Título (ex: Fornecedores): ')
      config.itemName = await this.ask('Nome do item singular (ex: Fornecedor): ')
      config.description = await this.ask('Descrição (opcional): ')
      
      // Configurações
      config.allowBulkActions = await this.askBoolean('Permitir ações em lote? (s/N): ', false)
      config.showExportImport = await this.askBoolean('Mostrar importação/exportação? (s/N): ', false)
      config.generateBackend = await this.askBoolean('Gerar arquivos backend? (s/N): ', false)
      config.customComponent = await this.askBoolean('Criar componente Vue customizado? (s/N): ', false)

      // API endpoint
      config.apiEndpoint = config.name

      // Colunas da tabela
      console.log('\n📋 Configuração das Colunas da Tabela:')
      config.columns = await this.configureColumns()

      // Campos do formulário
      console.log('\n📝 Configuração dos Campos do Formulário:')
      config.formFields = await this.configureFormFields()

      // Filtros
      if (await this.askBoolean('\nConfigurar filtros de busca? (s/N): ', false)) {
        config.filters = await this.configureFilters()
      }

      // Gerar módulo
      console.log('\n🚀 Gerando módulo...')
      const result = await this.generator.generateModule(config)
      
      console.log('\n✅ Módulo gerado com sucesso!')
      console.log('\n📁 Arquivos criados:')
      result.files.forEach(file => console.log(`  - ${file}`))

      console.log('\n📖 Próximos passos:')
      console.log('1. Reinicie o servidor de desenvolvimento')
      console.log('2. Acesse o menu Cadastro para ver o novo módulo')
      console.log('3. Configure as permissões no backend se necessário')

    } catch (error) {
      console.error('❌ Erro:', error.message)
    } finally {
      rl.close()
    }
  }

  /**
   * Configura colunas da tabela interativamente
   */
  async configureColumns() {
    const columns = []
    let continuar = true

    while (continuar) {
      console.log(`\nColuna ${columns.length + 1}:`)
      
      const column = {}
      column.key = await this.ask('  Chave do campo: ')
      column.label = await this.ask('  Label da coluna: ')
      column.type = await this.askSelect('  Tipo:', [
        'text', 'status', 'currency', 'date', 'link', 'color'
      ])

      columns.push(column)
      continuar = await this.askBoolean('Adicionar outra coluna? (s/N): ', false)
    }

    return columns
  }

  /**
   * Configura campos do formulário interativamente
   */
  async configureFormFields() {
    const fields = []
    let continuar = true

    while (continuar) {
      console.log(`\nCampo ${fields.length + 1}:`)
      
      const field = {}
      field.key = await this.ask('  Chave do campo: ')
      field.label = await this.ask('  Label: ')
      field.type = await this.askSelect('  Tipo:', [
        'text', 'email', 'number', 'currency', 'date', 'textarea', 
        'select', 'checkbox', 'radio', 'file'
      ])
      
      field.required = await this.askBoolean('  Obrigatório? (s/N): ', false)
      field.placeholder = await this.ask('  Placeholder (opcional): ')
      
      if (field.type === 'text' || field.type === 'textarea') {
        const maxLength = await this.ask('  Tamanho máximo (opcional): ')
        if (maxLength) field.maxLength = parseInt(maxLength)
      }

      if (field.type === 'number') {
        const min = await this.ask('  Valor mínimo (opcional): ')
        if (min) field.min = parseInt(min)
        
        const max = await this.ask('  Valor máximo (opcional): ')
        if (max) field.max = parseInt(max)
      }

      if (field.type === 'select' || field.type === 'radio') {
        console.log('  Opções (digite uma por linha, linha vazia para terminar):')
        field.options = await this.configureOptions()
      }

      fields.push(field)
      continuar = await this.askBoolean('Adicionar outro campo? (s/N): ', false)
    }

    return fields
  }

  /**
   * Configura opções para select/radio
   */
  async configureOptions() {
    const options = []
    let option

    while ((option = await this.ask('    Opção (value=label): ')) !== '') {
      const [value, label] = option.split('=')
      if (value && label) {
        options.push({ value: value.trim(), label: label.trim() })
      } else {
        options.push({ value: option.trim(), label: option.trim() })
      }
    }

    return options
  }

  /**
   * Configura filtros de busca
   */
  async configureFilters() {
    const filters = []
    let continuar = true

    while (continuar) {
      console.log(`\nFiltro ${filters.length + 1}:`)
      
      const filter = {}
      filter.key = await this.ask('  Campo: ')
      filter.type = await this.askSelect('  Tipo:', ['text', 'select', 'date'])
      filter.placeholder = await this.ask('  Placeholder: ')

      filters.push(filter)
      continuar = await this.askBoolean('Adicionar outro filtro? (s/N): ', false)
    }

    return filters
  }

  /**
   * Gera módulo a partir de arquivo de configuração
   */
  async generateFromConfig(configFile) {
    try {
      if (!fs.existsSync(configFile)) {
        console.log(`❌ Arquivo de configuração não encontrado: ${configFile}`)
        return
      }

      const config = JSON.parse(fs.readFileSync(configFile, 'utf8'))
      console.log(`🚀 Gerando módulo a partir de: ${configFile}`)
      
      const result = await this.generator.generateModule(config)
      
      console.log('✅ Módulo gerado com sucesso!')
      console.log('\n📁 Arquivos criados:')
      result.files.forEach(file => console.log(`  - ${file}`))

    } catch (error) {
      console.error('❌ Erro:', error.message)
    }
  }

  /**
   * Gera módulo usando exemplo pré-definido
   */
  async generateFromExample(moduleName) {
    try {
      console.log(`🚀 Gerando módulo: ${moduleName}`)
      
      const config = moduleExamples[moduleName]
      const result = await this.generator.generateModule(config)
      
      console.log('✅ Módulo gerado com sucesso!')
      console.log('\n📁 Arquivos criados:')
      result.files.forEach(file => console.log(`  - ${file}`))

    } catch (error) {
      console.error('❌ Erro:', error.message)
    }
  }

  /**
   * Valida estrutura do projeto
   */
  async validateProject() {
    console.log('🔍 Validando estrutura do projeto...\n')

    const checks = [
      {
        name: 'Frontend directory',
        path: 'frontend/src',
        required: true
      },
      {
        name: 'Module config file',
        path: 'frontend/src/config/moduleConfig.js',
        required: true
      },
      {
        name: 'API services',
        path: 'frontend/src/services/api.js',
        required: true
      },
      {
        name: 'Store index',
        path: 'frontend/src/store/index.js',
        required: true
      },
      {
        name: 'Router config',
        path: 'frontend/src/router/index.js',
        required: true
      },
      {
        name: 'Backend directory',
        path: 'backend/app',
        required: false
      }
    ]

    let valid = true

    for (const check of checks) {
      const exists = fs.existsSync(path.join(this.projectPath, check.path))
      const status = exists ? '✅' : (check.required ? '❌' : '⚠️')
      const message = exists ? 'OK' : (check.required ? 'MISSING (required)' : 'MISSING (optional)')
      
      console.log(`${status} ${check.name}: ${message}`)
      
      if (check.required && !exists) {
        valid = false
      }
    }

    console.log(`\n${valid ? '✅' : '❌'} Projeto ${valid ? 'válido' : 'inválido'} para geração de módulos`)
  }

  /**
   * Lista exemplos disponíveis
   */
  listExamples() {
    console.log('📋 Exemplos de módulos disponíveis:\n')
    
    Object.entries(moduleExamples).forEach(([name, config]) => {
      console.log(`🔹 ${name}`)
      console.log(`   Título: ${config.title}`)
      console.log(`   Descrição: ${config.description}`)
      console.log(`   Campos: ${config.formFields.length}`)
      console.log(`   Uso: node generate-module.js ${name}\n`)
    })
  }

  /**
   * Mostra ajuda
   */
  showHelp() {
    console.log(`
🔧 Gerador de Módulos de Cadastro

USO:
  node generate-module.js [opcoes]

OPÇÕES:
  --interactive              Modo interativo para criar módulo personalizado
  --config=arquivo.json      Gerar a partir de arquivo de configuração
  --list-examples           Listar exemplos disponíveis
  --validate                Validar estrutura do projeto
  --help, -h                Mostrar esta ajuda

EXEMPLOS:
  node generate-module.js --interactive
  node generate-module.js fornecedores
  node generate-module.js --config=meu-modulo.json
  node generate-module.js --list-examples

ESTRUTURA DO ARQUIVO DE CONFIGURAÇÃO:
{
  "name": "fornecedores",
  "title": "Fornecedores", 
  "itemName": "Fornecedor",
  "description": "Cadastro de fornecedores",
  "allowBulkActions": true,
  "showExportImport": true,
  "generateBackend": true,
  "columns": [...],
  "formFields": [...],
  "filters": [...]
}
`)
  }

  // Utilitários para input
  async ask(question) {
    return new Promise(resolve => {
      rl.question(question, resolve)
    })
  }

  async askBoolean(question, defaultValue = false) {
    const answer = await this.ask(question)
    if (answer.toLowerCase() === 's' || answer.toLowerCase() === 'y') return true
    if (answer.toLowerCase() === 'n') return false
    return defaultValue
  }

  async askSelect(question, options) {
    console.log(question)
    options.forEach((option, index) => {
      console.log(`  ${index + 1}. ${option}`)
    })
    
    let selected
    while (true) {
      const answer = await this.ask('Escolha (número): ')
      const index = parseInt(answer) - 1
      
      if (index >= 0 && index < options.length) {
        selected = options[index]
        break
      }
      
      console.log('Opção inválida. Tente novamente.')
    }
    
    return selected
  }
}

// Executar CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cli = new ModuleCLI()
  cli.run().catch(console.error)
}

export default ModuleCLI
