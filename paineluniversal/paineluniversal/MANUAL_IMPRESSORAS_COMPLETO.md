# 📖 MANUAL COMPLETO DE USO DAS IMPRESSORAS
## Sistema Universal de Eventos

**Versão:** 1.0  
**Data:** 05/09/2025  
**Autor:** Sistema Universal de Eventos  

---

## 📋 ÍNDICE

1. [Visão Geral do Sistema](#visão-geral)
2. [Tipos de Impressoras Suportadas](#tipos-suportadas)
3. [Configuração Inicial](#configuração-inicial)
4. [Interface Web - Como Usar](#interface-web)
5. [Configurações Avançadas](#configurações-avançadas)
6. [Sistema de Roteamento Inteligente](#roteamento-inteligente)
7. [Templates de Impressão](#templates)
8. [Monitoramento e Logs](#monitoramento)
9. [Solução de Problemas](#troubleshooting)
10. [API para Desenvolvedores](#api)

---

## 🎯 VISÃO GERAL DO SISTEMA {#visão-geral}

O Sistema Universal de Eventos possui um **sistema completo de gerenciamento de impressoras** que permite:

✅ **Gerenciar múltiplas impressoras térmicas**  
✅ **Roteamento automático de impressões**  
✅ **Templates personalizáveis**  
✅ **Monitoramento em tempo real**  
✅ **Fila de impressão com retry automático**  
✅ **Logs detalhados de auditoria**  

### **Componentes do Sistema:**

- **Backend:** FastAPI + Python (API REST)
- **Frontend:** React + TypeScript (Interface Web)
- **Banco:** PostgreSQL (Armazenamento)
- **Protocolos:** ESC/POS, TCP/IP, USB

---

## 🖨️ TIPOS DE IMPRESSORAS SUPORTADAS {#tipos-suportadas}

### **1. Impressoras Térmicas (Recomendado)**

| Tipo | Largura do Papel | Uso Recomendado |
|------|------------------|-----------------|
| **TERMICA_58MM** | 58mm | Comandas, tickets pequenos |
| **TERMICA_80MM** | 80mm | Cupons fiscais, recibos |

### **2. Outras Impressoras**

| Tipo | Descrição | Uso |
|------|-----------|-----|
| **MATRICIAL** | Impressoras de agulha | Formulários contínuos |
| **JATO_TINTA** | Impressoras inkjet | Documentos coloridos |

### **3. Interfaces de Conexão**

| Interface | Descrição | Configuração |
|-----------|-----------|--------------|
| **ETHERNET** | Rede TCP/IP | IP + Porta (9100) |
| **WIFI** | Rede sem fio | IP + Porta |
| **USB** | Conexão direta | Porta USB |
| **BLUETOOTH** | Conexão BT | MAC Address |
| **SERIAL** | Porta serial | COM1, COM2, etc. |
| **PARALELA** | Porta paralela | LPT1, LPT2, etc. |

### **4. Marcas Homologadas**

**✅ Testadas e Compatíveis:**
- Bematech MP-4200 TH
- Elgin i9/i7
- Daruma DR-800
- Epson TM-T20/TM-T88
- Star TSP100
- Sweda SI-250/SI-300

---

## ⚙️ CONFIGURAÇÃO INICIAL {#configuração-inicial}

### **Passo 1: Acessar o Sistema**

1. Faça login no sistema como **Administrador**
2. Navegue para: **Menu → Cadastros → Impressoras**
3. Ou acesse diretamente: `http://localhost:5173/app/impressoras`

### **Passo 2: Detectar Impressoras Automáticamente**

```javascript
// O sistema pode detectar impressoras na rede automaticamente
1. Clique em "Detectar Impressoras"
2. O sistema escaneará IPs 192.168.1.1 até 192.168.1.255
3. Testará portas: 9100, 515, 631, 9101, 9102
4. Listará impressoras encontradas
```

### **Passo 3: Configuração Manual**

**Para Impressora de Rede (Ethernet/WiFi):**
```
Nome: "Cozinha Principal"
Tipo: TERMICA_80MM
Interface: ETHERNET
Endereço: 192.168.1.100
Porta: 9100
Estação: COZINHA
Local Físico: "Andar 1 - Cozinha"
```

**Para Impressora USB:**
```
Nome: "Caixa Principal" 
Tipo: TERMICA_80MM
Interface: USB
Endereço: \\localhost\ImpressoraPDV
Estação: CAIXA
Local Físico: "Balcão Principal"
```

---

## 💻 INTERFACE WEB - COMO USAR {#interface-web}

### **Tela Principal - Abas Disponíveis**

#### **1️⃣ Aba "Impressoras"**
- **Lista todas as impressoras cadastradas**
- **Status em tempo real** (Online/Offline/Erro)
- **Ações disponíveis:**
  - ✏️ Editar configurações
  - 🧪 Testar impressão
  - 🗑️ Excluir impressora
  - 🔄 Atualizar status

#### **2️⃣ Aba "Roteamento Inteligente"**
- **Regras automáticas de impressão**
- **Configuração por:**
  - Local de origem
  - Categoria de produto
  - Horário de funcionamento
  - Prioridade

#### **3️⃣ Aba "Equipamentos"**
- **Gestão de dispositivos PDV**
- **Tipos:** POS, Tablet, Totem, Terminal
- **Vinculação com impressoras**

#### **4️⃣ Aba "Operadores"**
- **Usuários do sistema PDV**
- **Controle de comissões**
- **Permissões específicas**

### **Como Adicionar Nova Impressora**

```typescript
1. Clique no botão "➕ Adicionar Impressora"
2. Preencha o formulário:
   
   📝 DADOS BÁSICOS:
   - Nome: Nome identificador (obrigatório)
   - Tipo: Selecione o tipo de impressora
   - Interface: Como está conectada
   - Endereço: IP ou caminho da impressora
   
   ⚙️ CONFIGURAÇÕES TÉCNICAS:
   - Largura: 58mm ou 80mm
   - Colunas: Quantidade de caracteres por linha
   - Densidade: Intensidade da impressão (1-15)
   - Velocidade: Velocidade de impressão (1-10)
   
   📍 LOCALIZAÇÃO:
   - Estação: COZINHA, BAR, CAIXA, etc.
   - Local Físico: Descrição da localização
   - Evento: Vincular ao evento atual
   
   🔧 OPÇÕES AVANÇADAS:
   - Corte Automático: Sim/Não
   - Impressora Backup: Selecionar outra impressora
   - Ativa: Habilitar/Desabilitar

3. Clique em "💾 Salvar"
4. Teste a impressora clicando em "🧪 Testar"
```

### **Testando uma Impressora**

```javascript
// Tipos de teste disponíveis:
1. 🟢 TESTE SIMPLES
   - Imprime página básica com texto
   - Verifica conectividade
   
2. 🔵 TESTE COMPLETO
   - Testa todas as funcionalidades
   - Formatação, alinhamento, corte
   - QR Code e código de barras
   
3. ✂️ TESTE DE GUILHOTINA
   - Testa apenas o corte do papel
   - Útil para verificar guilhotina
   
4. 📱 TESTE QR CODE
   - Imprime QR Code de teste
   - Verifica qualidade de impressão
```

---

## 🔧 CONFIGURAÇÕES AVANÇADAS {#configurações-avançadas}

### **Parâmetros Técnicos**

#### **Densidade (1-15)**
```
1-5:   Impressão clara (papel normal)
6-10:  Impressão média (recomendado)
11-15: Impressão escura (papel de baixa qualidade)
```

#### **Velocidade (1-10)**
```
1-3:   Lenta (melhor qualidade)
4-7:   Média (balanceado)
8-10:  Rápida (menor qualidade)
```

#### **Perfis ESC/POS**
```
EPSON:    Compatível com Epson, Bematech
STAR:     Compatível com Star Micronics
BEMATECH: Otimizado para Bematech
```

### **Configurações JSON Avançadas**

```json
{
  "corte_automatico": true,
  "beep": false,
  "gaveta_dinheiro": true,
  "qr_code_size": 6,
  "barcode_height": 50,
  "margem_superior": 3,
  "margem_inferior": 5,
  "espaco_entre_linhas": 1.2,
  "timeout_conexao": 5,
  "timeout_impressao": 30,
  "retry_maximo": 3
}
```

---

## 🧠 SISTEMA DE ROTEAMENTO INTELIGENTE {#roteamento-inteligente}

### **O que é o Roteamento Inteligente?**

Sistema que **automaticamente decide qual impressora usar** baseado em regras configuráveis.

### **Tipos de Regras**

#### **1. Por Local de Origem**
```
Regra: "Pedidos da Mesa 1-10"
Condição: Mesa entre 1 e 10
Impressora: Cozinha Andar 1
Prioridade: 1 (Alta)
```

#### **2. Por Categoria de Produto**
```
Regra: "Bebidas Alcoólicas"
Condição: Categoria = "BEBIDAS" E Teor > 0%
Impressora: Bar Principal
Prioridade: 2 (Média)
```

#### **3. Por Horário**
```
Regra: "Delivery Noturno"
Condição: Hora entre 22:00 e 06:00
Impressora: Cozinha Delivery
Dias: Segunda a Domingo
```

### **Como Configurar Regras**

```typescript
1. Acesse aba "Roteamento Inteligente"
2. Clique "➕ Nova Regra"
3. Configure:

   📋 DADOS DA REGRA:
   - Nome: "Bebidas para Bar"
   - Descrição: "Todas as bebidas vão para impressora do bar"
   - Ativa: ✅ Sim
   - Prioridade: 1 (menor número = maior prioridade)
   
   🎯 CONDIÇÕES:
   - Local Origem: Qualquer mesa
   - Categoria: BEBIDAS
   - Subcategoria: Todas
   - Horário: 24h
   - Dias: Todos
   
   🖨️ DESTINO:
   - Impressora: Bar Principal
   - Impressora Backup: Bar Secundário
   - Múltiplas Vias: 1
   
4. Salvar e testar
```

### **Ordem de Prioridade**

```
1️⃣ Regras com prioridade 1 (mais alta)
2️⃣ Regras com prioridade 2
3️⃣ Regras com prioridade 3
...
🔧 Impressora padrão da estação
📋 Primeira impressora ativa encontrada
```

---

## 📄 TEMPLATES DE IMPRESSÃO {#templates}

### **O que são Templates?**

**Modelos pré-definidos** que formatam automaticamente os documentos impressos.

### **Tipos de Templates Disponíveis**

| Tipo | Uso | Exemplo |
|------|-----|---------|
| **RECIBO_CAIXA** | Cupons de venda | Comprovante PDV |
| **PEDIDO_COZINHA** | Comandas cozinha | Pedido #001 |
| **PEDIDO_BAR** | Comandas bar | Drinks Mesa 5 |
| **COMANDA_RECHARGE** | Recarga comanda | +R$ 50,00 |
| **RELATORIO** | Relatórios | Fechamento caixa |

### **Estrutura de um Template**

```handlebars
{{!-- CABEÇALHO --}}
=====================================
        {{empresa.nome}}
=====================================
CNPJ: {{empresa.cnpj}}
{{empresa.endereco}}

{{!-- CORPO DO DOCUMENTO --}}
PEDIDO: #{{pedido.numero}}
DATA: {{pedido.data}}
MESA: {{pedido.mesa}}
CLIENTE: {{pedido.cliente}}

-------------------------------------
{{#each itens}}
{{nome}}
{{quantidade}}x {{preco}} = {{total}}
{{/each}}
-------------------------------------

{{!-- RODAPÉ --}}
TOTAL: R$ {{pedido.total}}
=====================================
Obrigado pela preferência!

{{!-- COMANDOS ESC/POS --}}
{{{escpos.corte_total}}}
```

### **Variáveis Disponíveis**

#### **Empresa/Evento**
- `{{empresa.nome}}`
- `{{empresa.cnpj}}`
- `{{empresa.endereco}}`
- `{{evento.nome}}`
- `{{evento.data}}`

#### **Pedido/Venda**
- `{{pedido.numero}}`
- `{{pedido.data}}`
- `{{pedido.hora}}`
- `{{pedido.mesa}}`
- `{{pedido.cliente}}`
- `{{pedido.total}}`
- `{{pedido.desconto}}`

#### **Itens**
```handlebars
{{#each itens}}
  {{nome}}          - Nome do produto
  {{quantidade}}    - Quantidade
  {{preco}}         - Preço unitário
  {{total}}         - Total do item
  {{observacoes}}   - Observações
{{/each}}
```

#### **Comandos ESC/POS**
- `{{{escpos.negrito_on}}}`
- `{{{escpos.negrito_off}}}`
- `{{{escpos.centralizar}}}`
- `{{{escpos.alinhar_esquerda}}}`
- `{{{escpos.corte_total}}}`
- `{{{escpos.qr_code}}}`

### **Criando um Template Personalizado**

```typescript
1. Vá para: Templates de Impressão
2. Clique "➕ Novo Template"
3. Configure:

   📝 DADOS BÁSICOS:
   - Nome: "Comanda Cozinha Personalizada"
   - Tipo: PEDIDO_COZINHA
   - Evento: Selecionar evento
   - Padrão: Sim/Não
   
   🎨 TEMPLATE CONTENT:
   [Editor de texto com sintaxe Handlebars]
   
   ⚙️ COMANDOS ESC/POS:
   ```json
   {
     "densidade": 8,
     "corte": true,
     "beep": false,
     "gaveta": false
   }
   ```
   
   📐 LAYOUT:
   - Largura: 42 colunas
   - Fonte: normal
   - Ativo: ✅

4. Clique "💾 Salvar"
5. Teste com dados reais
```

---

## 📊 MONITORAMENTO E LOGS {#monitoramento}

### **Dashboard de Status**

```
📊 VISÃO GERAL
┌─────────────────────────────────────┐
│ 🖨️  Total de Impressoras: 5        │
│ 🟢 Online: 4                       │
│ 🔴 Offline: 1                      │
│ ⚠️  Com Erro: 0                     │
│ 📄 Jobs Pendentes: 3               │
│ 🔄 Processando: 1                  │
└─────────────────────────────────────┘
```

### **Status Individual**

| Impressora | Status | Último Heartbeat | Jobs Hoje |
|------------|--------|------------------|-----------|
| Cozinha 01 | 🟢 Online | 10:35:22 | 127 |
| Bar Principal | 🟢 Online | 10:35:15 | 89 |
| Caixa 01 | 🔴 Offline | 09:12:45 | 45 |

### **Sistema de Logs**

#### **Tipos de Log:**
- ✅ **SUCESSO:** Impressão concluída
- ⚠️ **AVISO:** Tentativa de retry
- ❌ **ERRO:** Falha na impressão
- 🔧 **SISTEMA:** Mudanças de configuração

#### **Detalhes Registrados:**
```json
{
  "timestamp": "2025-09-05T10:35:22Z",
  "impressora_id": "cozinha-01",
  "job_id": "job-12345",
  "tipo": "PEDIDO_COZINHA",
  "status": "SUCESSO",
  "usuario": "operador@teste.com",
  "ip_cliente": "192.168.1.50",
  "tempo_processamento": 1.2,
  "tentativas": 1,
  "dados": {
    "pedido_numero": 123,
    "mesa": 5,
    "total_itens": 3
  }
}
```

### **Alertas Automáticos**

#### **🔴 Alertas Críticos:**
- Impressora offline por mais de 5 minutos
- Fila com mais de 20 jobs pendentes
- Taxa de erro acima de 10%

#### **⚠️ Alertas de Atenção:**
- Impressora com retry frequente
- Papel acabando (se suportado)
- Jobs em processamento há mais de 5 minutos

---

## 🛠️ SOLUÇÃO DE PROBLEMAS {#troubleshooting}

### **Problemas Comuns**

#### **1. Impressora Não Conecta**

**❌ Problema:** Status sempre "Offline"

**✅ Soluções:**
```bash
1. Verificar cabo de rede/USB
2. Testar conectividade:
   ping 192.168.1.100
   telnet 192.168.1.100 9100

3. Verificar configurações:
   - IP correto
   - Porta correta (9100 é padrão)
   - Firewall liberado

4. Testar no navegador:
   http://192.168.1.100
```

#### **2. Impressora Corta Texto**

**❌ Problema:** Texto aparece cortado

**✅ Soluções:**
```
1. Verificar largura configurada:
   - 58mm = 32 colunas
   - 80mm = 42-48 colunas

2. Ajustar no template:
   - Reduzir tamanho da fonte
   - Quebrar linhas longas
   - Usar abreviações

3. Verificar papel:
   - Papel correto instalado
   - Posição adequada
```

#### **3. Impressão Muito Clara**

**❌ Problema:** Texto quase invisível

**✅ Soluções:**
```
1. Aumentar densidade: 8-12
2. Reduzir velocidade: 3-6
3. Verificar papel térmico
4. Limpar cabeça de impressão
```

#### **4. Jobs Ficam na Fila**

**❌ Problema:** Impressões não saem

**✅ Soluções:**
```
1. Verificar status da impressora
2. Limpar fila manualmente
3. Reiniciar serviço de impressão
4. Verificar logs de erro
```

### **Diagnóstico Avançado**

#### **Teste de Conectividade via API**

```bash
# Testar impressora específica
curl -X POST "http://localhost:8000/api/impressoras/{id}/teste" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "COMPLETO",
    "mensagem": "Teste de conectividade"
  }'
```

#### **Verificar Logs Detalhados**

```bash
# Ver logs recentes
curl "http://localhost:8000/api/impressoras/logs?limit=50" \
  -H "Authorization: Bearer {token}"

# Filtrar por impressora
curl "http://localhost:8000/api/impressoras/logs?impressora_id={id}" \
  -H "Authorization: Bearer {token}"
```

### **Códigos de Erro Comuns**

| Código | Significado | Solução |
|--------|-------------|---------|
| **CONN_TIMEOUT** | Timeout de conexão | Verificar IP/porta |
| **PRINT_TIMEOUT** | Timeout de impressão | Verificar papel/dados |
| **INVALID_DATA** | Dados inválidos | Verificar template |
| **PRINTER_ERROR** | Erro da impressora | Verificar status físico |

---

## 🔌 API PARA DESENVOLVEDORES {#api}

### **Endpoints Principais**

#### **Listar Impressoras**
```http
GET /api/impressoras/
Authorization: Bearer {token}

Response:
[
  {
    "id": "cozinha-01",
    "nome": "Cozinha Principal",
    "tipo": "TERMICA_80MM",
    "status": "ONLINE",
    "ip": "192.168.1.100",
    "porta": 9100
  }
]
```

#### **Criar Impressora**
```http
POST /api/impressoras/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nome": "Nova Impressora",
  "tipo": "TERMICA_80MM",
  "interface": "ETHERNET",
  "endereco": "192.168.1.101",
  "porta": 9100,
  "estacao": "BAR",
  "ativo": true
}
```

#### **Testar Impressora**
```http
POST /api/impressoras/{id}/teste
Authorization: Bearer {token}
Content-Type: application/json

{
  "tipo": "SIMPLES",
  "mensagem": "Teste personalizado"
}
```

#### **Enviar Job de Impressão**
```http
POST /api/impressoras/fila/
Authorization: Bearer {token}
Content-Type: application/json

{
  "impressora_id": "cozinha-01",
  "tipo": "PEDIDO_COZINHA",
  "template_id": 1,
  "dados": {
    "pedido_numero": 123,
    "mesa": 5,
    "itens": [
      {
        "nome": "Hambúrguer",
        "quantidade": 2,
        "observacoes": "Sem cebola"
      }
    ]
  }
}
```

### **Webhooks (Futuro)**

```http
POST /webhook/impressora/status
Content-Type: application/json

{
  "impressora_id": "cozinha-01",
  "status_anterior": "ONLINE",
  "status_atual": "OFFLINE",
  "timestamp": "2025-09-05T10:35:22Z"
}
```

---

## 📞 SUPORTE E CONTATO

### **🆘 Em Caso de Problemas**

1. **Verifique este manual primeiro**
2. **Consulte os logs do sistema**
3. **Teste conectividade básica**
4. **Entre em contato com suporte técnico**

### **📋 Informações para Suporte**

Ao entrar em contato, tenha em mãos:
- **Modelo da impressora**
- **Tipo de conexão (IP/USB)**
- **Mensagem de erro exata**
- **Logs recentes do sistema**
- **Print do status atual**

---

## 📚 RESUMO QUICK START

### **⚡ Para Começar Rapidamente:**

```
1. 🌐 Acesse: /app/impressoras
2. 🔍 Clique: "Detectar Impressoras" 
3. ⚙️ Configure: Nome + IP + Tipo
4. 💾 Salve e teste
5. 🧠 Configure roteamento (opcional)
6. 📄 Personalize templates (opcional)
7. ✅ Está pronto para usar!
```

### **🎯 Configuração Mínima Recomendada:**

```
- 1 Impressora para COZINHA (80mm)
- 1 Impressora para CAIXA (80mm)  
- 1 Impressora para BAR (58mm)
- Templates padrão ativados
- Roteamento por categoria básico
```

---

**📅 Última atualização:** 05/09/2025  
**👨‍💻 Desenvolvido por:** Sistema Universal de Eventos  
**📧 Suporte:** suporte@sistemauniversal.com  
**🌐 Documentação completa:** [Link para docs online]
