/**
 * Sistema de Validação de Compatibilidade para Módulos
 * Garante que novos módulos não quebrem funcionalidades existentes
 */

import fs from 'fs'
import path from 'path'

export class CompatibilityValidator {
  constructor(projectPath) {
    this.projectPath = projectPath
    this.errors = []
    this.warnings = []
  }

  /**
   * Valida se um novo módulo é compatível com o sistema existente
   */
  async validateModule(config) {
    console.log(`🔍 Validando compatibilidade do módulo: ${config.name}`)
    
    this.errors = []
    this.warnings = []

    // 1. Validar estrutura básica
    this.validateBasicStructure(config)
    
    // 2. Validar conflitos de nomes
    this.validateNameConflicts(config)
    
    // 3. Validar dependências
    this.validateDependencies(config)
    
    // 4. Validar rotas
    this.validateRoutes(config)
    
    // 5. Validar API endpoints
    this.validateApiEndpoints(config)
    
    // 6. Validar permissões
    this.validatePermissions(config)
    
    // 7. Validar campos obrigatórios
    this.validateRequiredFields(config)

    return {
      valid: this.errors.length === 0,
      errors: this.errors,
      warnings: this.warnings
    }
  }

  /**
   * Valida estrutura básica do módulo
   */
  validateBasicStructure(config) {
    const required = ['name', 'title', 'itemName', 'columns', 'formFields']
    
    for (const field of required) {
      if (!config[field]) {
        this.errors.push(`Campo obrigatório ausente: ${field}`)
      }
    }

    // Validar nome do módulo
    if (config.name && !/^[a-z][a-zA-Z0-9]*$/.test(config.name)) {
      this.errors.push('Nome do módulo deve começar com letra minúscula e conter apenas letras e números')
    }

    // Validar colunas
    if (config.columns && config.columns.length === 0) {
      this.errors.push('Módulo deve ter pelo menos uma coluna')
    }

    // Validar campos do formulário
    if (config.formFields && config.formFields.length === 0) {
      this.errors.push('Módulo deve ter pelo menos um campo de formulário')
    }
  }

  /**
   * Valida conflitos de nomes com módulos existentes
   */
  validateNameConflicts(config) {
    // Verificar se módulo já existe
    const moduleConfigPath = path.join(this.projectPath, 'frontend/src/config/moduleConfig.js')
    if (fs.existsSync(moduleConfigPath)) {
      const content = fs.readFileSync(moduleConfigPath, 'utf8')
      
      if (content.includes(`${config.name}:`)) {
        this.errors.push(`Módulo '${config.name}' já existe no sistema`)
      }
    }

    // Verificar conflitos com rotas existentes
    const routerPath = path.join(this.projectPath, 'frontend/src/router/index.js')
    if (fs.existsSync(routerPath)) {
      const content = fs.readFileSync(routerPath, 'utf8')
      
      if (content.includes(`path: '/cadastro/${config.name}'`) || 
          content.includes(`name: '${config.name.charAt(0).toUpperCase() + config.name.slice(1)}'`)) {
        this.errors.push(`Rota para módulo '${config.name}' já existe`)
      }
    }

    // Verificar conflitos com store
    const storePath = path.join(this.projectPath, 'frontend/src/store/index.js')
    if (fs.existsSync(storePath)) {
      const content = fs.readFileSync(storePath, 'utf8')
      
      if (content.includes(`${config.name}:`)) {
        this.errors.push(`Store module '${config.name}' já existe`)
      }
    }

    // Verificar conflitos com API services
    const apiPath = path.join(this.projectPath, 'frontend/src/services/api.js')
    if (fs.existsSync(apiPath)) {
      const content = fs.readFileSync(apiPath, 'utf8')
      
      if (content.includes(`${config.name}Api`)) {
        this.errors.push(`API service '${config.name}Api' já existe`)
      }
    }
  }

  /**
   * Valida dependências necessárias
   */
  validateDependencies(config) {
    const requiredFiles = [
      'frontend/src/components/cadastro/CadastroModule.vue',
      'frontend/src/components/cadastro/CadastroList.vue', 
      'frontend/src/components/cadastro/FormModal.vue',
      'frontend/src/config/moduleConfig.js',
      'frontend/src/services/api.js',
      'frontend/src/store/index.js',
      'frontend/src/router/index.js'
    ]

    for (const file of requiredFiles) {
      const filePath = path.join(this.projectPath, file)
      if (!fs.existsSync(filePath)) {
        this.errors.push(`Arquivo necessário não encontrado: ${file}`)
      }
    }

    // Validar estrutura dos componentes base
    this.validateBaseComponents()
  }

  /**
   * Valida componentes base necessários
   */
  validateBaseComponents() {
    const moduleComponentPath = path.join(this.projectPath, 'frontend/src/components/cadastro/CadastroModule.vue')
    if (fs.existsSync(moduleComponentPath)) {
      const content = fs.readFileSync(moduleComponentPath, 'utf8')
      
      // Verificar props essenciais
      if (!content.includes('moduleConfig') || !content.includes('permissions')) {
        this.errors.push('CadastroModule.vue não possui props necessárias (moduleConfig, permissions)')
      }
    }

    const listComponentPath = path.join(this.projectPath, 'frontend/src/components/cadastro/CadastroList.vue')
    if (fs.existsSync(listComponentPath)) {
      const content = fs.readFileSync(listComponentPath, 'utf8')
      
      // Verificar emits essenciais
      if (!content.includes('FormModal')) {
        this.warnings.push('CadastroList.vue pode estar faltando integração com FormModal')
      }
    }
  }

  /**
   * Valida configuração de rotas
   */
  validateRoutes(config) {
    // Verificar se rota pai /cadastro existe
    const routerPath = path.join(this.projectPath, 'frontend/src/router/index.js')
    if (fs.existsSync(routerPath)) {
      const content = fs.readFileSync(routerPath, 'utf8')
      
      if (!content.includes("path: '/cadastro'")) {
        this.errors.push('Rota pai /cadastro não encontrada no router')
      }

      // Verificar se possui meta.requiresAuth
      if (!content.includes('requiresAuth: true')) {
        this.warnings.push('Sistema de autenticação pode não estar configurado corretamente')
      }
    }
  }

  /**
   * Valida endpoints da API
   */
  validateApiEndpoints(config) {
    if (config.apiEndpoint) {
      // Verificar se endpoint não conflita com outros
      const commonEndpoints = [
        'auth', 'users', 'establishments', 'dashboard', 
        'clientes', 'operadores', 'promocoes', 'planos',
        'comandas', 'impressoras', 'formas-pagamento', 'lojas', 'links-pagamento'
      ]

      if (commonEndpoints.includes(config.apiEndpoint)) {
        this.errors.push(`Endpoint '${config.apiEndpoint}' conflita com endpoint existente`)
      }

      // Verificar formato do endpoint
      if (!/^[a-z][a-z0-9-]*$/.test(config.apiEndpoint)) {
        this.errors.push('Endpoint deve conter apenas letras minúsculas, números e hífens')
      }
    }
  }

  /**
   * Valida sistema de permissões
   */
  validatePermissions(config) {
    const requiredPermissions = ['view', 'create', 'edit', 'delete']
    
    // Verificar padrão de nomenclatura das permissões
    for (const permission of requiredPermissions) {
      const permissionName = `${config.name}.${permission}`
      
      // Validar formato
      if (!/^[a-z][a-zA-Z0-9]*\.[a-z]+$/.test(permissionName)) {
        this.warnings.push(`Permissão '${permissionName}' não segue padrão recomendado`)
      }
    }

    // Verificar se sistema de auth está configurado
    const authStorePath = path.join(this.projectPath, 'frontend/src/store/index.js')
    if (fs.existsSync(authStorePath)) {
      const content = fs.readFileSync(authStorePath, 'utf8')
      
      if (!content.includes('auth:') || !content.includes('permissions')) {
        this.warnings.push('Sistema de autenticação/permissões pode não estar configurado')
      }
    }
  }

  /**
   * Valida campos obrigatórios do formulário
   */
  validateRequiredFields(config) {
    if (config.formFields) {
      // Verificar se tem pelo menos um campo além do ID
      const visibleFields = config.formFields.filter(field => field.type !== 'hidden')
      if (visibleFields.length === 0) {
        this.errors.push('Formulário deve ter pelo menos um campo visível')
      }

      // Validar tipos de campo
      const validTypes = [
        'text', 'email', 'number', 'currency', 'date', 'datetime',
        'textarea', 'select', 'checkbox', 'radio', 'file', 'hidden'
      ]

      config.formFields.forEach((field, index) => {
        if (!validTypes.includes(field.type)) {
          this.errors.push(`Campo ${index + 1}: tipo '${field.type}' não é válido`)
        }

        if (!field.key) {
          this.errors.push(`Campo ${index + 1}: chave (key) é obrigatória`)
        }

        if (!field.label && field.type !== 'hidden') {
          this.warnings.push(`Campo '${field.key}': label não definido`)
        }

        // Validar campos do tipo select
        if (field.type === 'select' && (!field.options || field.options.length === 0)) {
          this.errors.push(`Campo '${field.key}': tipo select deve ter opções definidas`)
        }

        // Validar validações customizadas
        if (field.validate && typeof field.validate !== 'function') {
          this.errors.push(`Campo '${field.key}': validate deve ser uma função`)
        }
      })
    }

    // Validar colunas da tabela
    if (config.columns) {
      config.columns.forEach((column, index) => {
        if (!column.key) {
          this.errors.push(`Coluna ${index + 1}: chave (key) é obrigatória`)
        }

        if (!column.label) {
          this.errors.push(`Coluna ${index + 1}: label é obrigatório`)
        }

        if (!column.type) {
          this.warnings.push(`Coluna '${column.key}': tipo não definido, usando 'text' como padrão`)
        }
      })
    }
  }

  /**
   * Testa integração básica do módulo
   */
  async testModuleIntegration(config) {
    console.log(`🧪 Testando integração do módulo: ${config.name}`)
    
    const tests = []

    // Teste 1: Configuração pode ser importada
    tests.push({
      name: 'Importação de configuração',
      test: () => {
        try {
          // Simular importação da configuração
          const configString = JSON.stringify(config)
          JSON.parse(configString)
          return { success: true }
        } catch (error) {
          return { success: false, error: error.message }
        }
      }
    })

    // Teste 2: Store module pode ser criado
    tests.push({
      name: 'Criação de store module',
      test: () => {
        try {
          // Validar se a configuração pode ser usada para criar um store module
          const requiredProps = ['name', 'itemName']
          for (const prop of requiredProps) {
            if (!config[prop]) {
              throw new Error(`Propriedade ${prop} necessária para store module`)
            }
          }
          return { success: true }
        } catch (error) {
          return { success: false, error: error.message }
        }
      }
    })

    // Teste 3: Formulário pode ser renderizado
    tests.push({
      name: 'Renderização de formulário',
      test: () => {
        try {
          if (!config.formFields || config.formFields.length === 0) {
            throw new Error('FormFields necessários para renderização')
          }

          // Verificar se todos os campos têm propriedades mínimas
          for (const field of config.formFields) {
            if (!field.key || !field.type) {
              throw new Error(`Campo inválido: ${JSON.stringify(field)}`)
            }
          }

          return { success: true }
        } catch (error) {
          return { success: false, error: error.message }
        }
      }
    })

    // Executar testes
    const results = tests.map(test => ({
      ...test,
      result: test.test()
    }))

    // Resumo dos testes
    const passed = results.filter(r => r.result.success).length
    const failed = results.filter(r => !r.result.success)

    console.log(`📊 Resultados dos testes: ${passed}/${results.length} passaram`)

    if (failed.length > 0) {
      console.log('\n❌ Testes que falharam:')
      failed.forEach(test => {
        console.log(`  - ${test.name}: ${test.result.error}`)
      })
    }

    return {
      passed,
      total: results.length,
      failed: failed.map(t => ({ name: t.name, error: t.result.error })),
      success: failed.length === 0
    }
  }

  /**
   * Gera relatório de compatibilidade
   */
  generateReport(config, validationResult, testResult = null) {
    const report = {
      module: config.name,
      timestamp: new Date().toISOString(),
      validation: validationResult,
      tests: testResult,
      recommendations: this.generateRecommendations(config, validationResult)
    }

    // Salvar relatório
    const reportPath = path.join(this.projectPath, 'docs', 'compatibility-reports', `${config.name}-compatibility.json`)
    fs.mkdirSync(path.dirname(reportPath), { recursive: true })
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))

    return report
  }

  /**
   * Gera recomendações baseadas na validação
   */
  generateRecommendations(config, validationResult) {
    const recommendations = []

    if (validationResult.errors.length > 0) {
      recommendations.push({
        type: 'error',
        message: 'Corrija os erros antes de gerar o módulo',
        actions: validationResult.errors
      })
    }

    if (validationResult.warnings.length > 0) {
      recommendations.push({
        type: 'warning', 
        message: 'Considere revisar os avisos para melhor compatibilidade',
        actions: validationResult.warnings
      })
    }

    // Recomendações específicas
    if (!config.allowBulkActions) {
      recommendations.push({
        type: 'suggestion',
        message: 'Considere habilitar ações em lote para melhor usabilidade',
        action: 'Definir allowBulkActions: true na configuração'
      })
    }

    if (!config.filters || config.filters.length === 0) {
      recommendations.push({
        type: 'suggestion',
        message: 'Adicione filtros para melhorar a experiência de busca',
        action: 'Definir array filters[] na configuração'
      })
    }

    if (!config.description) {
      recommendations.push({
        type: 'suggestion',
        message: 'Adicione uma descrição para melhor documentação',
        action: 'Definir propriedade description na configuração'
      })
    }

    return recommendations
  }
}

export default CompatibilityValidator
