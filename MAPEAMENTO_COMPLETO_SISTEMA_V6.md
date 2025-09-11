# MAPEAMENTO COMPLETO - Sistema Painel Universal V6

**Data de Análise:** 2025-09-10  
**Versão do Sistema:** v6.0  
**Status:** Sistema em desenvolvimento ativo com múltiplos processos rodando

## 📊 RESUMO EXECUTIVO

O Sistema Painel Universal V6 é uma aplicação completa de gestão de eventos com arquitetura moderna baseada em FastAPI (backend) e React/Vite (frontend). O sistema possui **162 componentes frontend**, **74 routers backend**, **95+ modelos de dados** e múltiplos serviços rodando simultaneamente.

## 🏗️ ARQUITETURA DO SISTEMA

### Stack Tecnológica
- **Backend:** Python 3.13, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React 18.3, TypeScript, Vite 6.0, TailwindCSS
- **Database:** PostgreSQL (porta 5432)
- **Autenticação:** JWT, Sistema de permissões baseado em roles
- **PWA:** Service Workers, Web App Manifest

### Estrutura de Portas e Serviços
```
PORTA 5173/5174/5175 - Frontend Vite (Development)
PORTA 8000 - Backend FastAPI (Main Server)
PORTA 8001 - Backend FastAPI (Secondary Instance)  
PORTA 8002 - Backend Simple Server
PORTA 5432 - PostgreSQL Database
```

## 📁 ESTRUTURA DE DIRETÓRIOS

### Diretório Raiz
```
C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\
├── paineluniversal/              # Sistema principal
│   ├── backend/                  # API Backend
│   ├── frontend/                 # Interface React
│   ├── mobile-app/               # App React Native
│   ├── landing-unique/           # Landing page
│   ├── meep-service/            # Serviços MEEP
│   ├── pdv-mobile-limpo/        # PDV Mobile
│   ├── monitoring/              # Sistema de monitoramento
│   ├── nginx/                   # Configurações Nginx
│   └── docs/                    # Documentação
├── e2e/                         # Testes End-to-End
├── tests/                       # Testes gerais
└── WORKSPACE/                   # Área de trabalho
```

### Backend Structure (paineluniversal/backend/)
```
app/
├── routers/                     # 74 arquivos de rotas da API
├── models.py                    # 95+ modelos de dados (2.921 linhas)
├── main.py                      # Servidor principal FastAPI
├── database.py                  # Configuração do banco
├── auth.py                      # Sistema de autenticação
├── middleware.py                # Middlewares customizados
├── migrations/                  # Migrações automáticas
├── services/                    # Lógica de negócio
├── schemas/                     # Schemas Pydantic
├── inventory/                   # Módulo de inventário
└── utils/                       # Utilitários
```

### Frontend Structure (paineluniversal/frontend/)
```
src/
├── components/                  # 162 componentes React (.tsx/.jsx)
│   ├── auth/                    # Autenticação
│   ├── dashboard/               # Painéis de controle
│   ├── events/                  # Gestão de eventos
│   ├── financial/               # Módulo financeiro
│   ├── inventory/               # Controle de estoque
│   ├── cashless/                # Sistema cashless
│   ├── kds/                     # Kitchen Display System
│   ├── bi/                      # Business Intelligence
│   ├── mobile/                  # Componentes mobile
│   ├── pdv/                     # Ponto de venda
│   └── ui/                      # Componentes UI base
├── pages/                       # Páginas da aplicação
├── services/                    # Serviços API
├── hooks/                       # Custom React hooks
├── contexts/                    # React contexts
├── stores/                      # Gerenciamento de estado
├── types/                       # Definições TypeScript
└── utils/                       # Funções utilitárias
```

## 🗃️ MODELOS DE DADOS (Database Schema)

### Modelos Core (95+ Classes)
1. **Gestão Básica**
   - `Empresa` - Dados da empresa
   - `Usuario` - Sistema de usuários
   - `Evento` - Gestão de eventos
   - `Lista` - Listas de convidados

2. **Sistema Comercial**
   - `Produto` - Catálogo de produtos
   - `Comanda` - Sistema de comandas
   - `VendaPDV` - Vendas PDV
   - `ItemVendaPDV` - Itens das vendas
   - `PagamentoPDV` - Pagamentos

3. **Controle Financeiro**
   - `MovimentacaoFinanceira` - Movimentações
   - `CaixaPDV` - Controle de caixa
   - `CaixaEvento` - Caixa por evento
   - `FormaPagamento` - Formas de pagamento

4. **Sistema Cashless**
   - `RecargaComanda` - Recargas
   - `TransacaoComanda` - Transações
   - `SaldoComanda` - Saldos

5. **Estoque e Inventário**
   - `MovimentoEstoque` - Movimentações
   - `ProdutoEstoque` - Produtos em estoque
   - `LocalEstoque` - Localizações
   - `ContagemEstoque` - Inventários

6. **Sistema de Impressão**
   - `Impressora` - Cadastro de impressoras
   - `PrintTemplate` - Templates de impressão
   - `PrintJob` - Jobs de impressão
   - `PrintJobLog` - Logs de impressão

7. **CRM e Marketing**
   - `LeadCRM` - Leads de vendas
   - `CampanhaCRM` - Campanhas de marketing
   - `AtividadeCRM` - Atividades de CRM
   - `FluxoAutomacao` - Automações

8. **Business Intelligence**
   - `DashboardBI` - Painéis BI
   - `WidgetBI` - Widgets de dados
   - `AnalyticsMEEP` - Analytics MEEP
   - `PrevisaoIA` - Previsões IA

9. **Sistema de Permissões**
   - `Cargo` - Cargos/Roles
   - `Permissao` - Permissões específicas
   - `Colaborador` - Funcionários
   - `PermissaoCargo` - Relação permissão-cargo

10. **KDS (Kitchen Display System)**
    - `FilaKDS` - Filas de pedidos
    - `FluxoKDS` - Fluxos de trabalho
    - `NotificacaoKDS` - Notificações
    - `AlertaKDS` - Alertas do sistema

## 🌐 ENDPOINTS DA API

### Routers Ativos (74 arquivos)
1. **auth_no_redis.py** - Autenticação sem Redis
2. **dashboard.py** - Dashboard principal
3. **eventos.py** - Gestão de eventos
4. **produtos.py** - Catálogo de produtos
5. **pdv.py** - Sistema PDV
6. **financeiro.py** - Controle financeiro
7. **estoque.py** - Gestão de estoque
8. **impressoras.py** - Sistema de impressão
9. **kds.py** - Kitchen Display System
10. **cashless.py** - Sistema cashless
11. **business_intelligence.py** - BI e Analytics
12. **automacao.py** - Automações
13. **integracoes.py** - Integrações externas
14. **relatorios.py** - Relatórios gerais
15. **usuarios.py** - Gestão de usuários

### Status dos Routers
- **✅ Funcionando:** auth_no_redis, dashboard, eventos, produtos, usuarios
- **⚠️ Desabilitados:** meep, cashless_avancado, cardapios_digitais (conflitos)
- **🔧 Em Desenvolvimento:** estoque_controle, multi_cardapio, kds_avancado

## 💾 CONFIGURAÇÕES DE AMBIENTE

### Variáveis Críticas
```bash
DATABASE_URL - URL do PostgreSQL
RAILWAY_ENVIRONMENT - Ambiente Railway (prod/dev)
CORS_ORIGINS - Origens permitidas para CORS
SECRET_KEY - Chave secreta JWT
DEBUG_MODE - Modo debug (true/false)
```

### CORS Configuration
```python
allow_origins = [
  'http://localhost:3000',
  'http://localhost:5173', 
  'http://localhost:5174',
  'http://127.0.0.1:5173',
  'http://127.0.0.1:5174'
]
```

## 🔄 PROCESSOS EM EXECUÇÃO

### Servidores Ativos
1. **Frontend Vite Dev Server** - Porta 5173/5174
2. **Backend FastAPI** - Porta 8000 (Uvicorn)
3. **Backend FastAPI Secondary** - Porta 8001 (Uvicorn)
4. **Simple Server** - Porta 8002 (Multiple instances)
5. **PostgreSQL Database** - Porta 5432
6. **Build Process** - npm run build (ativo)

### Status dos Serviços
- **🟢 Ativo:** Frontend, Backend principal, Database
- **🟡 Múltiplas Instâncias:** Simple servers (múltiplos processos)
- **🔵 Build:** Frontend build em progresso

## 🧩 MÓDULOS E FUNCIONALIDADES

### Módulos Frontend (162 componentes)
1. **Dashboard** - Painéis principais
2. **Autenticação** - Login/logout, proteção de rotas
3. **Eventos** - Criação e gestão de eventos
4. **PDV** - Ponto de venda completo
5. **Estoque** - Controle de inventário
6. **Financeiro** - Gestão financeira
7. **Cashless** - Sistema cashless
8. **KDS** - Kitchen Display System
9. **BI** - Business Intelligence
10. **Mobile** - Componentes mobile-first
11. **Impressoras** - Gestão de impressão
12. **CRM** - Customer Relationship Management
13. **Automação** - Fluxos automatizados
14. **Relatórios** - Relatórios e exports

### Status dos Módulos
- **✅ Funcionando:** Dashboard, Auth, Eventos, Produtos, Usuários
- **🔧 Desenvolvimento:** Estoque, Financeiro, KDS, BI
- **⚠️ Conflitos:** MEEP, Cashless Avançado, Multi-cardápio
- **📱 Mobile:** PDV Mobile, App React Native

## 📊 DEPENDÊNCIAS E TECNOLOGIAS

### Backend Dependencies
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI
- **PostgreSQL** - Banco de dados
- **JWT** - Autenticação baseada em tokens
- **Alembic** - Migrações de banco

### Frontend Dependencies
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1", 
  "vite": "^6.0.1",
  "typescript": "~5.6.2",
  "@mui/material": "^7.3.2",
  "@radix-ui/*": "Multiple UI components",
  "axios": "^1.11.0",
  "react-router-dom": "^7.7.1",
  "recharts": "^2.15.4"
}
```

## 🔐 SISTEMA DE AUTENTICAÇÃO

### Fluxo de Autenticação
1. **Login:** CPF + Senha → JWT Token
2. **Validação:** Middleware verifica token em cada request
3. **Permissões:** Sistema baseado em roles (admin, promoter, operador)
4. **Sessões:** Controle de sessões ativas
5. **Segurança:** Hash bcrypt para senhas

### Tipos de Usuário
- **Admin:** Acesso completo ao sistema
- **Promoter:** Gestão de eventos e vendas
- **Operador:** Operações básicas (PDV, check-in)
- **Cliente:** Acesso limitado (mobile app)

## 🚀 DEPLOY E INFRAESTRUTURA

### Railway Configuration
- **Auto-deploy:** Integrado com Git
- **Migrações:** Executadas automaticamente no deploy
- **Ambiente:** Variáveis configuradas no Railway
- **Scaling:** Auto-scaling habilitado
- **Monitoring:** Logs centralizados

### Ambientes
- **Desenvolvimento:** Local (múltiplas portas)
- **Produção:** Railway (URLs .up.railway.app)
- **Testes:** E2E com Playwright

## 📈 MÉTRICAS DO SISTEMA

### Tamanho do Código
- **Backend:** 2.921 linhas (models.py) + 74 routers
- **Frontend:** 162 componentes React/TypeScript
- **Total de Arquivos:** 500+ arquivos Python/TypeScript/JavaScript
- **Database Schema:** 95+ tabelas/modelos

### Performance
- **Startup Time:** ~5-10 segundos
- **API Response:** <200ms (média)
- **Frontend Build:** ~30-60 segundos
- **Database Queries:** Otimizadas com SQLAlchemy

## 🔍 PONTOS DE ATENÇÃO

### Problemas Identificados
1. **Múltiplos Servidores:** Várias instâncias rodando simultaneamente
2. **Routers Desabilitados:** Alguns módulos comentados por conflitos
3. **Migrações:** Sistema de migração automática pode ser instável
4. **CORS:** Configuração permissiva em desenvolvimento
5. **Dependencies:** Algumas dependências podem estar conflitando

### Recomendações
1. **Limpeza:** Remover processos desnecessários
2. **Consolidação:** Unificar instâncias do servidor
3. **Testes:** Implementar testes unitários e integração
4. **Documentação:** Expandir documentação da API
5. **Monitoramento:** Implementar APM (Application Performance Monitoring)

## 📋 PRÓXIMOS PASSOS

### Desenvolvimento
1. **Resolver Conflitos:** Módulos desabilitados (MEEP, Cashless avançado)
2. **Testes E2E:** Expandir cobertura de testes
3. **Mobile App:** Finalizar aplicativo React Native
4. **Performance:** Otimizar queries e componentes
5. **Segurança:** Audit de segurança completo

### Produção
1. **CI/CD:** Pipeline automatizado
2. **Backup:** Estratégia de backup automático
3. **Scaling:** Preparar para alta demanda
4. **Monitoring:** Alertas e métricas em tempo real
5. **Documentation:** Manual do usuário final

---

**Gerado em:** 2025-09-10  
**Última Atualização:** Sistema em desenvolvimento ativo  
**Versão do Documento:** 1.0

*Este documento será atualizado conforme o desenvolvimento do sistema progride.*