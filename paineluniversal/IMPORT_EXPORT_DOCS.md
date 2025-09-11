# 📦 Módulo de Import/Export - Documentação Completa

## 🎯 Visão Geral

O módulo de Import/Export é uma extensão avançada do sistema de estoque que permite importar e exportar produtos em lote, com validação robusta, mapeamento de campos flexível e relatórios inteligentes específicos para o setor de entretenimento noturno.

## 🚀 Funcionalidades Principais

### 📥 Importação de Produtos

#### Formatos Suportados
- **CSV** - Valores separados por vírgula (padrão universal)
- **Excel** - Planilhas .xlsx e .xls 
- **JSON** - Formato estruturado para APIs
- **Limite**: 10MB por arquivo

#### Campos Disponíveis para Importação

| Campo | Tipo | Obrigatório | Descrição | Exemplos |
|-------|------|-------------|-----------|----------|
| `codigo` | String | ✅ | Código/SKU único | PROD001, BEB-001 |
| `nome` | String | ✅ | Nome do produto | Cerveja Lata 350ml |
| `categoria` | String | ✅ | Categoria | Bebidas, Comidas, Fichas |
| `preco_venda` | Number | ✅ | Preço de venda | 10.50 |
| `codigo_barras` | String | ❌ | EAN/Código barras | 1234567890123 |
| `marca` | String | ❌ | Marca do produto | Brahma, Skol |
| `fornecedor` | String | ❌ | Fornecedor | Distribuidora ABC |
| `preco_custo` | Number | ❌ | Preço de custo | 7.50 |
| `margem_lucro` | Number | ❌ | % de margem | 40.0 |
| `estoque_atual` | Integer | ❌ | Quantidade em estoque | 100 |
| `estoque_minimo` | Integer | ❌ | Alerta estoque baixo | 10 |
| `estoque_maximo` | Integer | ❌ | Limite máximo | 1000 |
| `unidade_medida` | String | ❌ | UN, LT, KG, etc | UN |
| `volume` | Number | ❌ | Volume (ml, L) | 350 |
| `teor_alcoolico` | Number | ❌ | % álcool | 4.5 |
| `temperatura_ideal` | String | ❌ | Conservação | Gelado, Ambiente |
| `validade_dias` | Integer | ❌ | Dias até vencer | 180 |
| `ncm` | String | ❌ | Código NCM (8 dígitos) | 22030000 |
| `icms` | Number | ❌ | % ICMS | 18.0 |
| `ipi` | Number | ❌ | % IPI | 5.0 |
| `destaque` | Boolean | ❌ | Produto em destaque | true/false |
| `promocional` | Boolean | ❌ | Em promoção | true/false |
| `observacoes` | String | ❌ | Observações gerais | Texto livre |

#### Processo de Importação

```mermaid
graph TD
    A[Upload Arquivo] --> B[Análise Estrutura]
    B --> C[Mapeamento de Campos]
    C --> D[Validação de Dados]
    D --> E{Erros Críticos?}
    E -->|Sim| F[Corrigir Erros]
    E -->|Não| G[Executar Importação]
    F --> D
    G --> H[Relatório Final]
```

#### Validações Aplicadas

1. **Campos Obrigatórios**
   - Código, Nome, Categoria, Preço de Venda

2. **Formato de Dados**
   - Números válidos para preços
   - CPF/CNPJ quando aplicável
   - Códigos de barras (8-14 dígitos)

3. **Regras de Negócio**
   - Códigos únicos no sistema
   - Preços positivos
   - Margem de lucro entre 0-100%
   - NCM com 8 dígitos

4. **Integridade Referencial**
   - Categorias existentes
   - Fornecedores válidos

### 📤 Exportação de Produtos

#### Tipos de Exportação

| Tipo | Descrição | Campos Incluídos |
|------|-----------|------------------|
| **Estoque Completo** | Todos os produtos com informações detalhadas | Todos os campos |
| **Estoque Baixo** | Produtos com estoque abaixo do mínimo | Código, Nome, Estoque Atual, Mínimo |
| **Lista de Preços** | Para fornecedores e parcerias | Código, Nome, Preços, Margem |
| **Fiscal** | Para contabilidade | Código, Nome, NCM, ICMS, IPI |
| **Inventário** | Para contagem física | Código, Nome, Estoque Sistema |
| **Personalizado** | Campos selecionados pelo usuário | Campos customizáveis |

#### Formatos de Exportação

| Formato | Uso Recomendado | Características |
|---------|-----------------|-----------------|
| **CSV** | Análise de dados, importação em outros sistemas | Universal, compacto |
| **Excel** | Planilhas, análises complexas | Formatação, múltiplas abas |
| **JSON** | Integrações, APIs | Estruturado, programático |
| **PDF** | Relatórios impressos | Apresentação, documentação |

#### Filtros Avançados

- **Por Categoria**: Bebidas, Comidas, etc.
- **Por Fornecedor**: Filtrar por fornecedor específico
- **Status Estoque**: Normal, Baixo, Zerado, Excesso
- **Faixa de Preços**: Mínimo e máximo
- **Período**: Data de criação/atualização
- **Status**: Apenas ativos, com estoque, etc.

## 🔧 APIs Disponíveis

### Endpoints de Importação

```http
# Obter opções de importação
GET /api/estoque/import/options

# Upload de arquivo
POST /api/estoque/upload
Content-Type: multipart/form-data

# Validar dados
POST /api/estoque/validate/{operacao_id}
Content-Type: application/json

# Executar importação
POST /api/estoque/import/{operacao_id}
Content-Type: application/json

# Status da importação
GET /api/estoque/import/{operacao_id}/status
```

### Endpoints de Exportação

```http
# Formatos disponíveis
GET /api/estoque/export/formats

# Preview da exportação
POST /api/estoque/export/preview
Content-Type: application/json

# Executar exportação
POST /api/estoque/export
Content-Type: application/json
```

### Endpoints de Templates

```http
# Listar templates
GET /api/estoque/templates

# Criar template
POST /api/estoque/templates
Content-Type: application/json

# Download template
GET /api/estoque/templates/{format}/download
```

### Endpoints de Monitoramento

```http
# Estatísticas do dashboard
GET /api/estoque/dashboard/stats

# Jobs de import/export
GET /api/estoque/jobs?limit=20&status_filter=CONCLUIDA

# Cancelar job
DELETE /api/estoque/jobs/{job_id}
```

### Endpoints de Relatórios

```http
# Relatório de giro de estoque
GET /api/estoque/reports/giro?periodo=30

# Análise ABC
GET /api/estoque/reports/abc

# Relatório de perdas
GET /api/estoque/reports/perdas?periodo=30
```

## 📊 Dashboard e Monitoramento

### Métricas Principais

- **Importações Hoje**: Número de importações realizadas
- **Produtos Atualizados**: Produtos modificados recentemente
- **Erros Último Import**: Erros na última importação
- **Tempo Médio**: Tempo médio de processamento

### Operações Recentes

Visualização em tempo real de:
- Tipo da operação (Importação/Exportação)
- Status atual (Pendente, Processando, Concluída, Erro)
- Progresso em tempo real
- Número de registros processados
- Estatísticas de sucesso/erro

### Ações Rápidas

- **Importar CSV**: Template mais comum
- **Exportar Excel**: Formato de análise
- **Templates**: Download de modelos
- **Relatórios**: Acesso rápido a relatórios

## 🏗️ Arquitetura Técnica

### Backend (Python/FastAPI)

```
backend/
├── app/
│   ├── models.py                          # Modelos SQLAlchemy
│   ├── schemas_import_export.py           # Schemas Pydantic
│   ├── routers/
│   │   └── import_export.py              # Endpoints da API
│   └── services/
│       └── import_export_service.py      # Lógica de negócio
```

### Frontend (React/TypeScript)

```
frontend/src/components/estoque/
├── EstoqueModule.tsx                      # Módulo principal com tabs
├── ImportModal.tsx                        # Modal de importação
├── ExportModal.tsx                        # Modal de exportação
├── ImportExportDashboard.tsx             # Dashboard de monitoramento
└── index.ts                              # Exports dos componentes
```

### Banco de Dados

#### Tabelas Principais

```sql
-- Produtos com campos estendidos
ALTER TABLE produtos ADD (
  marca VARCHAR(100),
  fornecedor VARCHAR(200),
  preco_custo DECIMAL(10, 2),
  margem_lucro DECIMAL(5, 2),
  -- ... outros campos
);

-- Operações de import/export
CREATE TABLE operacoes_import_export (
  id SERIAL PRIMARY KEY,
  tipo_operacao VARCHAR(20),
  nome_arquivo VARCHAR(255),
  status VARCHAR(20),
  -- ... outros campos
);

-- Validações de importação
CREATE TABLE validacoes_importacao (
  id SERIAL PRIMARY KEY,
  operacao_id INTEGER REFERENCES operacoes_import_export(id),
  linha_arquivo INTEGER,
  status VARCHAR(20),
  mensagem TEXT,
  -- ... outros campos
);

-- Templates de importação
CREATE TABLE templates_importacao (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100),
  formato VARCHAR(10),
  mapeamento_padrao TEXT,
  -- ... outros campos
);
```

## 🚀 Instalação e Setup

### 1. Executar Migração do Banco

```bash
cd backend
python create_import_export_tables.py
```

### 2. Instalar Dependências Python

```bash
cd backend
poetry install
# Ou
pip install pandas openpyxl reportlab
```

### 3. Instalar Dependências Frontend

```bash
cd frontend
npm install
# Dependências já incluídas no package.json
```

### 4. Configurar Variáveis de Ambiente

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/db
# Ou para desenvolvimento
DATABASE_URL=sqlite:///./app.db
```

## 📝 Exemplos de Uso

### Template CSV Básico

```csv
codigo,nome,categoria,preco_venda,estoque_atual
BEB001,Cerveja Lata 350ml,Bebidas,5.50,100
BEB002,Água 500ml,Bebidas,3.00,200
COM001,Hambúrguer Tradicional,Comidas,25.00,50
FIC001,Ficha Consumação,Fichas,10.00,1000
```

### Template CSV Completo

```csv
codigo,nome,categoria,preco_venda,codigo_barras,marca,fornecedor,preco_custo,margem_lucro,estoque_atual,estoque_minimo,unidade_medida,volume,teor_alcoolico,temperatura_ideal,ncm,icms,destaque,promocional
BEB001,Cerveja Brahma Lata 350ml,Bebidas,5.50,1234567890123,Brahma,Distribuidora ABC,3.50,57.14,100,20,UN,350,4.5,Gelado,22030000,18.0,true,false
BEB002,Água Crystal 500ml,Bebidas,3.00,9876543210987,Crystal,Distribuidora XYZ,1.80,66.67,200,50,UN,500,0,Ambiente,22011000,0,false,false
```

### Exemplo JSON

```json
[
  {
    "codigo": "BEB001",
    "nome": "Cerveja Brahma Lata 350ml",
    "categoria": "Bebidas",
    "preco_venda": 5.50,
    "codigo_barras": "1234567890123",
    "marca": "Brahma",
    "fornecedor": "Distribuidora ABC",
    "preco_custo": 3.50,
    "margem_lucro": 57.14,
    "estoque_atual": 100,
    "estoque_minimo": 20,
    "unidade_medida": "UN",
    "volume": 350,
    "teor_alcoolico": 4.5,
    "temperatura_ideal": "Gelado",
    "ncm": "22030000",
    "icms": 18.0,
    "destaque": true,
    "promocional": false
  }
]
```

## 🧪 Testes

### Executar Testes

```bash
cd backend
python test_import_export.py

# Com pytest
python -m pytest test_import_export.py -v

# Com cobertura
python -m pytest test_import_export.py --cov=app.services.import_export_service --cov-report=html -v
```

### Cenários de Teste Cobertos

- ✅ Análise de arquivos CSV, Excel, JSON
- ✅ Validação de campos obrigatórios
- ✅ Mapeamento automático de campos
- ✅ Detecção de formatos de arquivo
- ✅ Estimativa de tamanho de arquivos
- ✅ Conversão de produtos para diferentes formatos
- ✅ APIs de import/export
- ✅ Download de templates

## 📈 Relatórios Específicos do Setor

### 1. Relatório de Giro de Estoque

Analisa a rotatividade dos produtos baseado nas vendas dos últimos 30/60/90 dias.

**Fórmula**: `Giro = Vendas no Período / Estoque Médio`

**Uso**: Identificar produtos de alta e baixa rotatividade para otimizar compras.

### 2. Análise ABC de Produtos

Classifica produtos por faturamento acumulado:
- **Classe A**: 80% do faturamento (produtos críticos)
- **Classe B**: 15% do faturamento (produtos importantes)  
- **Classe C**: 5% do faturamento (produtos complementares)

**Uso**: Priorizar atenção nos produtos mais lucrativos.

### 3. Relatório de Perdas

Acompanha perdas por:
- Validade vencida
- Quebra/danos
- Furto/roubo
- Outras causas

**Uso**: Reduzir desperdícios e melhorar controles.

## 🔒 Segurança e Validações

### Validações de Segurança

- **Tamanho máximo**: 10MB por arquivo
- **Formatos permitidos**: Apenas CSV, Excel, JSON
- **Sanitização**: Limpeza de dados maliciosos
- **Autenticação**: Apenas usuários autenticados
- **Autorização**: Permissões baseadas em roles

### Controle de Acesso

- **inventory:read**: Visualizar dados de estoque
- **inventory:write**: Criar/editar produtos e movimentações
- **inventory:admin**: Gerenciar configurações e templates

## 🚀 Performance e Otimização

### Processamento em Lote

- **Chunk Size**: 100 registros por lote
- **Processamento Assíncrono**: Não bloqueia interface
- **Progress Tracking**: Acompanhamento em tempo real
- **Error Recovery**: Rollback automático em falhas

### Índices de Banco de Dados

```sql
-- Índices para performance
CREATE INDEX idx_produtos_marca ON produtos(marca);
CREATE INDEX idx_produtos_fornecedor ON produtos(fornecedor);
CREATE INDEX idx_operacoes_status ON operacoes_import_export(status);
CREATE INDEX idx_operacoes_criado_em ON operacoes_import_export(criado_em);
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro "Formato não suportado"**
   - Verificar extensão do arquivo (.csv, .xlsx, .json)
   - Confirmar que arquivo não está corrompido

2. **Erro "Campo obrigatório"**
   - Verificar mapeamento de campos
   - Confirmar que campos obrigatórios estão preenchidos

3. **Erro "Código duplicado"**
   - Códigos devem ser únicos no sistema
   - Verificar se produto já existe

4. **Timeout na importação**
   - Reduzir tamanho do arquivo
   - Dividir importação em múltiplos arquivos

### Logs e Debug

```bash
# Verificar logs do servidor
tail -f backend/server.log

# Debug modo desenvolvimento
cd backend
uvicorn app.main:app --reload --log-level debug
```

## 📞 Suporte

Para dúvidas ou problemas:

1. Consultar esta documentação
2. Verificar logs de erro no dashboard
3. Testar com templates de exemplo
4. Verificar permissões do usuário

---

## 🎊 Conclusão

O módulo de Import/Export transforma o controle de estoque básico em uma solução profissional e completa, específica para o setor de entretenimento noturno. Com validações robustas, relatórios inteligentes e interface intuitiva, permite gestão eficiente de inventário em qualquer escala de operação.

**Benefícios Principais:**
- ⚡ **Agilidade**: Importação de milhares de produtos em minutos
- 🎯 **Precisão**: Validações impedem erros de dados
- 📊 **Inteligência**: Relatórios específicos do setor
- 🔄 **Integração**: APIs para sistemas externos
- 👥 **Usabilidade**: Interface intuitiva para qualquer usuário