# 🖨️ Manual de Configuração - Sistema de Impressoras Térmicas

## 📋 Índice
1. [Introdução](#introdução)
2. [Acesso ao Sistema](#acesso-ao-sistema)
3. [Tipos de Impressoras Suportadas](#tipos-de-impressoras-suportadas)
4. [Interfaces de Conexão](#interfaces-de-conexão)
5. [Configuração Passo a Passo](#configuração-passo-a-passo)
6. [Configurações por Tipo de Interface](#configurações-por-tipo-de-interface)
7. [Templates de Impressão](#templates-de-impressão)
8. [Testes e Resolução de Problemas](#testes-e-resolução-de-problemas)
9. [Exemplos Práticos](#exemplos-práticos)
10. [FAQ - Perguntas Frequentes](#faq---perguntas-frequentes)

---

## 🎯 Introdução

O Sistema de Impressoras Térmicas permite a integração completa de impressoras ESC/POS com o ERP Sistema Universal. Este manual irá guiá-lo através de todo o processo de configuração, desde a conexão física até a personalização de templates de impressão.

### ✨ Funcionalidades Principais:
- ✅ Suporte a múltiplos tipos de impressoras (Térmicas 58mm/80mm, Matriciais, Jato de Tinta)
- ✅ Conexões via USB, Ethernet, Wi-Fi, Bluetooth, Paralela e Serial
- ✅ Roteamento automático por estações (COZINHA, BAR, CAIXA)
- ✅ Sistema de filas com prioridades
- ✅ Templates ESC/POS customizáveis
- ✅ Monitoramento em tempo real
- ✅ Retry automático em caso de falhas
- ✅ Auditoria completa de impressões

---

## 🌐 Acesso ao Sistema

### 1. **URLs do Sistema**
- **Frontend (Interface Web)**: http://localhost:5173
- **Backend (API)**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs

### 2. **Login no Sistema**
```
Usuário Admin Padrão:
CPF: 00000000000
Senha: admin123

Usuário Promoter:
CPF: 11111111111
Senha: promoter123
```

### 3. **Acesso ao Módulo de Impressoras**
1. Faça login no sistema
2. Navegue até **"Impressoras"** no menu principal
3. Você verá o dashboard com status geral das impressoras

---

## 🖨️ Tipos de Impressoras Suportadas

### **TERMICA_58MM**
- **Uso**: Recibos compactos, comanda de mesa
- **Largura**: 58mm (aproximadamente 32 caracteres por linha)
- **Ideal para**: Caixas compactos, PDVs móveis

### **TERMICA_80MM**
- **Uso**: Recibos padrão, cupons fiscais
- **Largura**: 80mm (aproximadamente 48 caracteres por linha)
- **Ideal para**: Caixas principais, recibos detalhados

### **MATRICIAL**
- **Uso**: Impressão em formulários carbonados
- **Largura**: Variável (80-132 colunas)
- **Ideal para**: Notas fiscais, documentos oficiais

### **JATO_TINTA**
- **Uso**: Impressões coloridas, etiquetas
- **Largura**: Variável
- **Ideal para**: Etiquetas de produtos, relatórios coloridos

---

## 🔌 Interfaces de Conexão

### **USB**
- **Vantagens**: Configuração simples, conexão direta
- **Desvantagens**: Limitado a um computador
- **Formato do Endereço**: `COM3` ou `/dev/usb/lp0`

### **ETHERNET**
- **Vantagens**: Rede compartilhada, múltiplos computadores
- **Desvantagens**: Requer configuração de rede
- **Formato do Endereço**: `192.168.1.100`
- **Porta Padrão**: `9100`

### **WIFI**
- **Vantagens**: Sem fios, flexibilidade de posicionamento
- **Desvantagens**: Dependente da qualidade do Wi-Fi
- **Formato do Endereço**: `192.168.1.101`
- **Porta Padrão**: `9100`

### **BLUETOOTH**
- **Vantagens**: Sem fios, ideal para dispositivos móveis
- **Desvantagens**: Alcance limitado (10m)
- **Formato do Endereço**: `00:11:22:33:44:55` (MAC Address)

### **PARALELA**
- **Vantagens**: Conexão tradicional, estável
- **Desvantagens**: Interface obsoleta
- **Formato do Endereço**: `LPT1`

### **SERIAL**
- **Vantagens**: Comunicação confiável
- **Desvantagens**: Velocidade limitada
- **Formato do Endereço**: `COM1`

---

## ⚙️ Configuração Passo a Passo

### **Passo 1: Acessar o Gerenciador de Impressoras**
1. Abra o navegador e acesse: http://localhost:5173
2. Faça login no sistema
3. Clique em **"Impressoras"** no menu

### **Passo 2: Adicionar Nova Impressora**
1. Clique no botão **"Nova Impressora"**
2. Preencha o formulário com as informações:

#### **Informações Básicas**
- **Nome da Impressora**: Nome descritivo (ex: "Impressora Caixa Principal")
- **Tipo**: Selecione o tipo de impressora
- **Interface**: Escolha o tipo de conexão
- **Endereço**: IP, COM, ou identificador da impressora
- **Porta**: Para conexões de rede (padrão: 9100)

#### **Configurações Operacionais**
- **Estação/Setor**: COZINHA, BAR, CAIXA, ou customizado
- **Local Físico**: Descrição da localização
- **Densidade**: 1-15 (padrão: 8)
- **Velocidade**: 1-200% (padrão: 100%)
- **Corte Automático**: Ativo/Inativo

### **Passo 3: Testar a Impressora**
1. Após salvar, clique no ícone de **"Teste"** na impressora
2. Verifique se a impressão de teste foi realizada
3. Se houver erro, verifique as configurações de conexão

### **Passo 4: Monitorar Status**
- **Verde (Online)**: Impressora funcionando normalmente
- **Vermelho (Offline)**: Impressora desconectada
- **Amarelo (Erro)**: Problema de papel ou conexão

---

## 🔧 Configurações por Tipo de Interface

### **Configuração USB**

#### **Windows:**
1. Conecte a impressora via USB
2. Instale os drivers do fabricante
3. Anote a porta COM atribuída (ex: COM3)
4. No sistema:
   - **Endereço**: `COM3`
   - **Porta**: Deixar em branco

#### **Linux:**
1. Conecte a impressora via USB
2. Verifique o dispositivo: `lsusb`
3. Anote o dispositivo (ex: `/dev/usb/lp0`)
4. No sistema:
   - **Endereço**: `/dev/usb/lp0`
   - **Porta**: Deixar em branco

### **Configuração Ethernet/Wi-Fi**

#### **1. Configurar IP da Impressora:**
- Imprima a página de configuração da impressora
- Acesse o painel web da impressora (geralmente http://ip-da-impressora)
- Configure IP fixo na mesma rede do servidor

#### **2. Exemplo de Configuração:**
```
IP da Impressora: 192.168.1.100
Máscara de Rede: 255.255.255.0
Gateway: 192.168.1.1
```

#### **3. No Sistema:**
- **Endereço**: `192.168.1.100`
- **Porta**: `9100`

#### **4. Teste de Conectividade:**
```bash
# Windows
telnet 192.168.1.100 9100

# Linux
nc -zv 192.168.1.100 9100
```

### **Configuração Bluetooth**

#### **1. Parear a Impressora:**
1. Ative o Bluetooth no computador
2. Coloque a impressora em modo de pareamento
3. Conecte através das configurações de Bluetooth
4. Anote o endereço MAC (ex: 00:11:22:33:44:55)

#### **2. No Sistema:**
- **Endereço**: `00:11:22:33:44:55`
- **Porta**: Deixar em branco

---

## 📄 Templates de Impressão

### **Tipos de Templates Disponíveis:**

#### **RECIBO_CAIXA**
- Recibos de vendas no PDV
- Informações: produtos, valores, forma de pagamento
- Estação recomendada: CAIXA

#### **PEDIDO_COZINHA**
- Pedidos para preparo na cozinha
- Informações: itens, quantidade, observações
- Estação recomendada: COZINHA

#### **PEDIDO_BAR**
- Pedidos de bebidas
- Informações: bebidas, quantidade, mesa
- Estação recomendada: BAR

#### **COMANDA_RECARGA**
- Recarga de comandas
- Informações: valor, saldo anterior, novo saldo

#### **COMANDA_FECHAMENTO**
- Fechamento de comandas
- Informações: consumo total, forma de pagamento

### **Variáveis Disponíveis nos Templates:**

```
{nome_empresa}      - Nome da empresa
{endereco_empresa}  - Endereço da empresa
{cnpj_empresa}      - CNPJ da empresa
{numero_venda}      - Número da venda
{data_venda}        - Data da venda
{nome_operador}     - Nome do operador
{itens_lista}       - Lista de itens
{subtotal}          - Subtotal
{desconto}          - Desconto aplicado
{total}             - Valor total
{forma_pagamento}   - Forma de pagamento
{mensagem_rodape}   - Mensagem do rodapé
{mesa_comanda}      - Número da mesa/comanda
{observacoes}       - Observações do pedido
```

### **Exemplo de Template Personalizado:**

```
{nome_empresa}
{endereco_empresa}
CNPJ: {cnpj_empresa}
Tel: (11) 99999-9999
--------------------------------
*** PEDIDO COZINHA ***

Mesa: {mesa_comanda}
Pedido: #{numero_pedido}
Data: {data_hora}
Operador: {operador}

================================
{itens_cozinha}
================================

Observações:
{observacoes}

*** PREPARAR AGORA ***
--------------------------------
Sistema Universal - v1.0
```

---

## 🔍 Testes e Resolução de Problemas

### **Teste Básico de Impressão**
1. No gerenciador de impressoras, clique no ícone **"Teste"**
2. Deve imprimir uma página com:
   - Nome da impressora
   - Data/hora do teste
   - Nome do operador
   - Informações técnicas

### **Problemas Comuns e Soluções**

#### **❌ Impressora Offline**
**Possíveis Causas:**
- Cabo desconectado
- Impressora desligada
- IP incorreto
- Driver não instalado

**Soluções:**
1. Verificar conexões físicas
2. Verificar se a impressora está ligada
3. Testar conectividade de rede: `ping 192.168.1.100`
4. Reinstalar drivers da impressora

#### **❌ Erro de Papel**
**Possíveis Causas:**
- Papel acabou
- Papel mal posicionado
- Sensor de papel sujo

**Soluções:**
1. Recolocar papel corretamente
2. Limpar sensores com álcool isopropílico
3. Verificar se o papel está na direção correta

#### **❌ Impressão Cortada**
**Possíveis Causas:**
- Template muito largo para a impressora
- Configuração de largura incorreta

**Soluções:**
1. Ajustar template para largura da impressora
2. Verificar configurações de margem
3. Usar quebras de linha adequadas

#### **❌ Caracteres Estranhos**
**Possíveis Causas:**
- Encoding incorreto
- Driver incompatível
- Velocidade de comunicação inadequada

**Soluções:**
1. Verificar encoding UTF-8
2. Atualizar drivers da impressora
3. Reduzir velocidade de impressão

---

## 📚 Exemplos Práticos

### **Exemplo 1: Impressora de Caixa (Ethernet)**

```json
{
  "nome": "Impressora Caixa Principal",
  "tipo": "TERMICA_80MM",
  "interface": "ETHERNET",
  "endereco": "192.168.1.100",
  "porta": 9100,
  "estacao": "CAIXA",
  "local_fisico": "Balcão Principal - Caixa 1",
  "densidade": 8,
  "velocidade": 100,
  "corte_automatico": true,
  "evento_id": 1
}
```

### **Exemplo 2: Impressora de Cozinha (USB)**

```json
{
  "nome": "Impressora Cozinha",
  "tipo": "TERMICA_80MM",
  "interface": "USB",
  "endereco": "COM3",
  "estacao": "COZINHA",
  "local_fisico": "Cozinha - Pass Through",
  "densidade": 10,
  "velocidade": 80,
  "corte_automatico": true,
  "evento_id": 1
}
```

### **Exemplo 3: Impressora de Bar (Wi-Fi)**

```json
{
  "nome": "Impressora Bar Móvel",
  "tipo": "TERMICA_58MM",
  "interface": "WIFI",
  "endereco": "192.168.1.101",
  "porta": 9100,
  "estacao": "BAR",
  "local_fisico": "Bar - Estação Móvel",
  "densidade": 8,
  "velocidade": 100,
  "corte_automatico": true,
  "evento_id": 1
}
```

### **Exemplo 4: Impressora Matricial (Paralela)**

```json
{
  "nome": "Impressora Fiscal Matricial",
  "tipo": "MATRICIAL",
  "interface": "PARALELA",
  "endereco": "LPT1",
  "estacao": "FISCAL",
  "local_fisico": "Escritório - Mesa Fiscal",
  "densidade": 5,
  "velocidade": 50,
  "corte_automatico": false,
  "evento_id": 1
}
```

---

## ❓ FAQ - Perguntas Frequentes

### **1. Quantas impressoras posso conectar?**
Não há limite técnico. O sistema suporta múltiplas impressoras simultâneas.

### **2. Posso usar impressoras de marcas diferentes?**
Sim, desde que sejam compatíveis com ESC/POS (padrão da maioria das impressoras térmicas).

### **3. Como funciona o roteamento automático?**
O sistema direciona automaticamente:
- RECIBO_CAIXA → impressoras com estação "CAIXA"
- PEDIDO_COZINHA → impressoras com estação "COZINHA"
- PEDIDO_BAR → impressoras com estação "BAR"

### **4. Posso personalizar os templates?**
Sim, através do gerenciador de templates você pode criar templates customizados com variáveis específicas.

### **5. O que acontece se uma impressora falhar?**
O sistema possui retry automático (3 tentativas por padrão) e registra todas as falhas no log para auditoria.

### **6. Como monitorar o status das impressoras?**
O dashboard principal mostra em tempo real:
- Impressoras online/offline
- Jobs na fila
- Jobs sendo processados
- Histórico de erros

### **7. Posso imprimir em múltiplas impressoras simultaneamente?**
Sim, especialmente útil para pedidos que vão para cozinha E bar simultaneamente.

### **8. Como configurar prioridades de impressão?**
As prioridades são definidas automaticamente:
- Prioridade 1: Urgente (testes, cancelamentos)
- Prioridade 3: Normal (recibos, pedidos)
- Prioridade 5: Baixa (relatórios)

### **9. Posso agendar impressões?**
Sim, o sistema permite agendar jobs para impressão em horários específicos.

### **10. Como fazer backup das configurações?**
As configurações ficam no banco de dados. Faça backup regular do arquivo `eventos.db`.

---

## 🎯 Próximos Passos

1. **Configure sua primeira impressora** seguindo o passo a passo
2. **Teste a impressão** com o botão de teste
3. **Personalize os templates** conforme sua necessidade
4. **Configure todas as estações** (CAIXA, COZINHA, BAR)
5. **Monitore o dashboard** para acompanhar o funcionamento

---

## 📞 Suporte

Para dúvidas adicionais ou problemas não cobertos neste manual:

- **Documentação da API**: http://localhost:8000/docs
- **Logs do Sistema**: Disponíveis no terminal do backend
- **Status da Aplicação**: http://localhost:8000/api/health

---

**Sistema Universal - Módulo de Impressoras Térmicas v1.0**  
*Desenvolvido para máxima compatibilidade e facilidade de uso*

🎉 **Parabéns! Você está pronto para usar o sistema de impressoras térmicas!**
