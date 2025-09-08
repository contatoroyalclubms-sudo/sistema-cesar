# Prompt para Refatoração Completa e Alinhamento do Sistema

## Objetivo Principal
Analise todo o projeto (banco de dados, backend e frontend) e execute uma refatoração completa para garantir 100% de alinhamento entre todos os componentes, eliminando erros de salvamento de dados e inconsistências.

## Fase 1: Análise Completa do Sistema

### 1.1 Mapeamento do Banco de Dados
- Analise TODOS os arquivos de schema/migrations do banco de dados
- Liste TODAS as tabelas existentes com seus campos, tipos, constraints e relacionamentos
- Identifique chaves primárias, chaves estrangeiras e índices
- Documente TODOS os campos obrigatórios, opcionais e suas validações
- Mapeie relacionamentos entre tabelas (1:1, 1:N, N:N)

### 1.2 Auditoria do Backend
- Examine TODOS os modelos/entities do backend
- Verifique TODAS as APIs/endpoints existentes
- Analise TODOS os DTOs, requests e responses
- Identifique TODAS as validações implementadas
- Mapeie TODOS os serviços e suas operações de CRUD
- Verifique tratamento de erros e exceções

### 1.3 Auditoria do Frontend
- Analise TODOS os formulários e componentes de entrada de dados
- Examine TODAS as interfaces/types TypeScript
- Verifique TODAS as chamadas de API
- Identifique TODOS os estados e validações do frontend
- Mapeie TODAS as telas que interagem com dados

## Fase 2: Identificação de Inconsistências

### 2.1 Análise de Discrepâncias
- Compare campos do banco vs modelos do backend
- Compare DTOs do backend vs interfaces do frontend  
- Identifique campos ausentes em qualquer camada
- Detecte tipos de dados incompatíveis
- Localize validações inconsistentes ou ausentes
- Identifique relacionamentos mal mapeados

### 2.2 Relatório de Problemas
- Documente TODAS as inconsistências encontradas
- Priorize os problemas por severidade e impacto
- Identifique dependências entre correções
- Sugira estratégia de correção

## Fase 3: Refatoração Sistemática

### 3.1 Padronização do Banco de Dados
- Corrija/padronize nomes de tabelas e campos
- Ajuste tipos de dados se necessário
- Adicione constraints ausentes
- Otimize índices
- Garanta integridade referencial

### 3.2 Refatoração do Backend
- Atualize TODOS os modelos para refletir exatamente o schema do banco
- Padronize TODOS os DTOs com validações apropriadas
- Implemente TODAS as validações necessárias
- Corrija TODOS os endpoints para usar os DTOs corretos
- Adicione tratamento robusto de erros
- Implemente logging adequado

### 3.3 Refatoração do Frontend  
- Atualize TODAS as interfaces TypeScript
- Corrija TODOS os formulários para incluir todos os campos necessários
- Implemente validações no frontend que espelhem o backend
- Atualize TODAS as chamadas de API
- Adicione tratamento de erros adequado
- Implemente feedback visual para o usuário

## Fase 4: Implementação de Boas Práticas

### 4.1 Validações Robustas
- Implemente validação em todas as camadas (frontend, backend, banco)
- Use bibliotecas de validação consistentes
- Garanta mensagens de erro claras e padronizadas
- Implemente sanitização de dados

### 4.2 Tratamento de Erros
- Implemente tratamento de erros consistente em todas as camadas
- Crie sistema de logging estruturado
- Implemente retry policies onde apropriado
- Garanta rollback em operações que falharem

### 4.3 Documentação Automática
- Gere documentação da API automaticamente
- Documente schemas do banco de dados
- Crie comentários claros no código
- Mantenha README atualizado

## Fase 5: Testes e Validação

### 5.1 Testes Automatizados
- Implemente testes unitários para todos os modelos e serviços
- Crie testes de integração para APIs
- Adicione testes end-to-end para fluxos críticos
- Implemente testes de validação de dados

### 5.2 Validação Manual
- Teste TODOS os formulários e operações CRUD
- Verifique se TODOS os campos são salvos corretamente
- Confirme que validações estão funcionando
- Teste cenários de erro

## Fase 6: Otimização e Performance

### 6.1 Otimização de Queries
- Otimize consultas ao banco de dados
- Adicione índices onde necessário
- Implemente pagination onde apropriado
- Use eager/lazy loading adequadamente

### 6.2 Performance do Frontend
- Otimize renderização de formulários complexos
- Implemente loading states
- Adicione debounce em validações
- Otimize bundle size

## Deliverables Esperados

1. **Relatório de Análise**: Documento completo com todas as inconsistências encontradas
2. **Código Refatorado**: Todo o código atualizado e alinhado
3. **Scripts de Migração**: Scripts SQL para atualizar banco se necessário
4. **Documentação**: Documentação completa do sistema refatorado
5. **Testes**: Suite completa de testes automatizados
6. **Guia de Deploy**: Instruções para aplicar as mudanças em produção

## Critérios de Sucesso

- ✅ Zero erros ao salvar dados em qualquer formulário
- ✅ 100% de alinhamento entre banco, backend e frontend
- ✅ Validações consistentes em todas as camadas
- ✅ Tratamento robusto de erros
- ✅ Código limpo e bem documentado
- ✅ Testes automatizados com boa cobertura
- ✅ Performance otimizada

## Instruções de Execução

1. Execute esta análise de forma incremental, documentando cada descoberta
2. Não faça alterações até completar a análise completa
3. Priorize correções que podem quebrar funcionalidades existentes
4. Mantenha backup de todos os arquivos antes das alterações
5. Execute testes após cada grupo de alterações
6. Documente TODAS as mudanças realizadas

**IMPORTANTE**: Esta refatoração deve ser executada com extremo cuidado. Faça backup completo antes de iniciar e execute em ambiente de desenvolvimento primeiro.