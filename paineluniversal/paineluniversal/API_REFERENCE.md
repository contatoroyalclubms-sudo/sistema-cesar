# 📘 API REFERENCE - SISTEMA REFATORADO v2.0

## 🔐 Autenticação

Todas as rotas protegidas requerem token JWT no header:
```
Authorization: Bearer <token>
```

---

## 🧑 USUÁRIOS

### POST /api/usuarios
Criar novo usuário

**Request Body:**
```json
{
  "nome": "string",          // Obrigatório, min: 3 caracteres
  "email": "string",          // Obrigatório, formato email válido
  "cpf": "string",            // Obrigatório, CPF válido (com ou sem formatação)
  "telefone": "string",       // Opcional, formato: (00) 00000-0000
  "senha": "string",          // Obrigatório, min: 6 caracteres
  "role": "ADMIN|PROMOTER|CLIENTE", // Obrigatório, default: CLIENTE
  "empresa_id": "number"      // Opcional
}
```

**Validações:**
- CPF deve ser válido (dígitos verificadores corretos)
- Email deve ser único no sistema
- CPF deve ser único no sistema
- Telefone deve ter 11 dígitos (se fornecido)

**Response 201:**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@example.com",
  "cpf": "123.456.789-09",
  "telefone": "(11) 98765-4321",
  "role": "CLIENTE",
  "ativo": true,
  "created_at": "2025-01-05T10:00:00Z",
  "updated_at": "2025-01-05T10:00:00Z"
}
```

**Erros Possíveis:**
- 400: Dados inválidos
- 409: CPF ou email já cadastrado
- 422: Erro de validação (CPF inválido, email mal formatado, etc.)

### GET /api/usuarios/{id}
Buscar usuário por ID

**Response 200:**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@example.com",
  "cpf": "123.456.789-09",
  "telefone": "(11) 98765-4321",
  "role": "CLIENTE",
  "ativo": true,
  "eventos": [],
  "checkins": [],
  "created_at": "2025-01-05T10:00:00Z",
  "updated_at": "2025-01-05T10:00:00Z"
}
```

**Erros:**
- 404: Usuário não encontrado

### PUT /api/usuarios/{id}
Atualizar usuário

**Request Body:** (campos opcionais)
```json
{
  "nome": "string",
  "email": "string",
  "telefone": "string",
  "ativo": "boolean"
}
```

**Validações:**
- Não é permitido alterar CPF
- Email deve ser único (se alterado)
- Apenas ADMIN pode alterar role

**Response 200:** Usuário atualizado

**Erros:**
- 400: Dados inválidos
- 403: Sem permissão
- 404: Usuário não encontrado
- 409: Email já em uso

---

## 📅 EVENTOS

### POST /api/eventos
Criar novo evento

**Request Body:**
```json
{
  "nome": "string",           // Obrigatório, min: 3 caracteres
  "descricao": "string",      // Opcional
  "data": "2025-01-10",       // Obrigatório, formato: YYYY-MM-DD
  "horario": "20:00",         // Obrigatório, formato: HH:MM
  "local": "string",          // Obrigatório
  "endereco": "string",       // Opcional
  "cidade": "string",         // Opcional
  "estado": "string",         // Opcional, 2 caracteres
  "cep": "00000-000",         // Opcional, formato CEP
  "capacidade_maxima": 500,   // Opcional, default: null
  "idade_minima": 18,         // Opcional, default: 18
  "status": "ATIVO|INATIVO|CANCELADO|FINALIZADO", // Default: ATIVO
  "tipo_evento": "BALADA|SHOW|FESTIVAL|CORPORATIVO|OUTRO", // Default: OUTRO
  "banner_url": "string",     // Opcional, URL válida
  "organizador_id": 1         // Obrigatório, ID do usuário organizador
}
```

**Validações:**
- Data deve ser futura
- CEP deve ter formato válido (se fornecido)
- Estado deve ter 2 caracteres (se fornecido)
- Capacidade máxima deve ser > 0 (se fornecida)
- Idade mínima deve estar entre 0 e 120

**Response 201:**
```json
{
  "id": 1,
  "nome": "Festa de Ano Novo",
  "data": "2025-01-10",
  "horario": "20:00",
  "local": "Casa de Shows XYZ",
  "status": "ATIVO",
  "tipo_evento": "BALADA",
  "capacidade_maxima": 500,
  "idade_minima": 18,
  "total_checkins": 0,
  "created_at": "2025-01-05T10:00:00Z",
  "updated_at": "2025-01-05T10:00:00Z"
}
```

**Erros:**
- 400: Dados inválidos
- 401: Não autorizado
- 422: Erro de validação

### GET /api/eventos
Listar eventos

**Query Params:**
- `status`: ATIVO|INATIVO|CANCELADO|FINALIZADO
- `tipo_evento`: BALADA|SHOW|FESTIVAL|CORPORATIVO|OUTRO
- `data_inicio`: YYYY-MM-DD
- `data_fim`: YYYY-MM-DD
- `cidade`: string
- `organizador_id`: number
- `page`: number (default: 1)
- `limit`: number (default: 20, max: 100)

**Response 200:**
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "pages": 3,
  "limit": 20
}
```

### PUT /api/eventos/{id}
Atualizar evento

**Validações:**
- Apenas organizador ou ADMIN pode editar
- Não pode alterar evento FINALIZADO
- Não pode alterar data para passado

**Response 200:** Evento atualizado

**Erros:**
- 403: Sem permissão
- 404: Evento não encontrado
- 409: Conflito (evento já finalizado)

---

## ✅ CHECK-IN

### POST /api/checkin
Realizar check-in

**Request Body:**
```json
{
  "evento_id": 1,            // Obrigatório
  "usuario_id": 1,           // Obrigatório
  "lista_id": 1,             // Opcional
  "tipo_ingresso": "VIP|NORMAL|PROMOTER", // Obrigatório
  "observacoes": "string"    // Opcional
}
```

**Validações:**
- Evento deve estar ATIVO
- Usuário não pode ter check-in duplicado no mesmo evento
- Idade do usuário deve atender idade mínima do evento

**Response 201:**
```json
{
  "id": 1,
  "evento_id": 1,
  "usuario_id": 1,
  "tipo_ingresso": "VIP",
  "status": "CONFIRMADO",
  "horario_checkin": "2025-01-05T20:30:00Z",
  "created_at": "2025-01-05T20:30:00Z"
}
```

**Erros:**
- 400: Check-in já realizado
- 403: Idade insuficiente
- 404: Evento ou usuário não encontrado
- 409: Check-in duplicado

### GET /api/checkin/evento/{evento_id}
Listar check-ins do evento

**Query Params:**
- `status`: PENDENTE|CONFIRMADO|CANCELADO
- `tipo_ingresso`: VIP|NORMAL|PROMOTER
- `search`: string (busca por nome ou CPF)

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "usuario": {
        "id": 1,
        "nome": "João Silva",
        "cpf": "123.456.789-09"
      },
      "tipo_ingresso": "VIP",
      "status": "CONFIRMADO",
      "horario_checkin": "2025-01-05T20:30:00Z"
    }
  ],
  "total": 150,
  "confirmados": 145,
  "pendentes": 5
}
```

---

## 💰 PDV (Ponto de Venda)

### POST /api/pdv/venda
Registrar venda

**Request Body:**
```json
{
  "evento_id": 1,             // Obrigatório
  "cliente_id": 1,            // Obrigatório
  "vendedor_id": 1,           // Obrigatório
  "itens": [                  // Obrigatório, min: 1 item
    {
      "produto_id": 1,
      "quantidade": 2,
      "preco_unitario": 15.00,
      "desconto": 0
    }
  ],
  "forma_pagamento": "DINHEIRO|CARTAO|PIX|FIADO", // Obrigatório
  "observacoes": "string"     // Opcional
}
```

**Validações:**
- Quantidade deve ser > 0
- Preço unitário deve ser >= 0
- Desconto deve ser entre 0 e 100%
- Produto deve ter estoque suficiente

**Response 201:**
```json
{
  "id": 1,
  "codigo": "VND-2025-0001",
  "evento_id": 1,
  "cliente_id": 1,
  "vendedor_id": 1,
  "total": 30.00,
  "forma_pagamento": "PIX",
  "status": "CONCLUIDA",
  "itens": [...],
  "created_at": "2025-01-05T21:00:00Z"
}
```

**Erros:**
- 400: Dados inválidos
- 404: Produto, cliente ou evento não encontrado
- 409: Estoque insuficiente

### POST /api/pdv/cancelar/{venda_id}
Cancelar venda

**Request Body:**
```json
{
  "motivo": "string"          // Obrigatório
}
```

**Validações:**
- Apenas vendedor original ou ADMIN pode cancelar
- Venda deve estar no status CONCLUIDA
- Estoque é devolvido automaticamente

**Response 200:**
```json
{
  "id": 1,
  "status": "CANCELADA",
  "motivo_cancelamento": "Cliente desistiu",
  "cancelada_em": "2025-01-05T21:30:00Z",
  "cancelada_por": 1
}
```

---

## 📦 ESTOQUE

### POST /api/estoque/produto
Criar produto

**Request Body:**
```json
{
  "nome": "string",           // Obrigatório
  "descricao": "string",      // Opcional
  "codigo_barras": "string",  // Opcional, único
  "categoria": "BEBIDA|COMIDA|OUTROS", // Obrigatório
  "preco_venda": 10.00,       // Obrigatório, >= 0
  "preco_custo": 5.00,        // Opcional, >= 0
  "unidade": "UN|CX|PCT|L|ML", // Default: UN
  "estoque_minimo": 10,       // Default: 0
  "ativo": true               // Default: true
}
```

**Response 201:** Produto criado

### POST /api/estoque/movimento
Registrar movimento de estoque

**Request Body:**
```json
{
  "produto_id": 1,            // Obrigatório
  "tipo": "ENTRADA|SAIDA|AJUSTE", // Obrigatório
  "quantidade": 100,          // Obrigatório, > 0
  "motivo": "string",         // Obrigatório
  "evento_id": 1,             // Opcional
  "responsavel_id": 1         // Obrigatório
}
```

**Validações:**
- SAIDA: deve ter estoque suficiente
- Quantidade deve ser positiva
- Produto deve estar ativo

**Response 201:** Movimento registrado

---

## 🎮 GAMIFICAÇÃO

### GET /api/ranking/promoters
Ranking de promoters

**Query Params:**
- `evento_id`: number (opcional, para ranking específico do evento)
- `periodo`: DIA|SEMANA|MES|TOTAL (default: TOTAL)
- `limit`: number (default: 10, max: 100)

**Response 200:**
```json
{
  "ranking": [
    {
      "posicao": 1,
      "promoter": {
        "id": 1,
        "nome": "Maria Silva",
        "foto_url": "https://..."
      },
      "pontos": 1500,
      "vendas": 45,
      "checkins": 150,
      "badges": ["top_seller", "early_bird"]
    }
  ],
  "periodo": "TOTAL",
  "atualizado_em": "2025-01-05T22:00:00Z"
}
```

### POST /api/badges/atribuir
Atribuir badge

**Request Body:**
```json
{
  "usuario_id": 1,            // Obrigatório
  "badge": "TOP_SELLER|EARLY_BIRD|FIDELIDADE", // Obrigatório
  "evento_id": 1              // Opcional
}
```

**Response 201:** Badge atribuída

---

## 🔄 IMPORT/EXPORT

### POST /api/import/usuarios
Importar usuários em lote

**Request Body (multipart/form-data):**
- `file`: CSV ou XLSX com colunas: nome, email, cpf, telefone, role

**Validações:**
- Todos os CPFs são validados
- Emails duplicados são rejeitados
- Máximo 1000 registros por importação

**Response 200:**
```json
{
  "total": 100,
  "importados": 95,
  "erros": 5,
  "detalhes_erros": [
    {
      "linha": 10,
      "erro": "CPF inválido",
      "dados": {"cpf": "111.111.111-11"}
    }
  ]
}
```

### GET /api/export/evento/{evento_id}/checkins
Exportar check-ins do evento

**Query Params:**
- `formato`: CSV|XLSX|PDF (default: CSV)

**Response 200:** File download

---

## 🔔 WEBHOOKS E NOTIFICAÇÕES

### WebSocket /api/pdv/ws/{evento_id}
WebSocket para atualizações em tempo real do PDV

**Mensagens enviadas pelo servidor:**
```json
{
  "tipo": "nova_venda|venda_cancelada|estoque_baixo",
  "dados": {
    "venda_id": 1,
    "total": 50.00,
    "vendedor": "João"
  },
  "timestamp": "2025-01-05T22:00:00Z"
}
```

### WebSocket /api/checkin/ws/{evento_id}
WebSocket para atualizações de check-in

**Mensagens:**
```json
{
  "tipo": "novo_checkin|checkin_cancelado",
  "dados": {
    "usuario": "Maria Silva",
    "tipo_ingresso": "VIP",
    "horario": "2025-01-05T20:30:00Z"
  }
}
```

---

## 🚨 CÓDIGOS DE ERRO

### Estrutura de Erro Padrão
```json
{
  "error": "Mensagem de erro legível",
  "code": "ERROR_CODE",
  "details": {
    "field": "campo_com_erro",
    "value": "valor_invalido"
  },
  "timestamp": "2025-01-05T10:00:00Z"
}
```

### Códigos de Erro Comuns

| Código | HTTP Status | Descrição |
|--------|------------|-----------|
| VALIDATION_ERROR | 422 | Erro de validação de dados |
| REQUIRED_FIELD | 422 | Campo obrigatório não fornecido |
| INVALID_FORMAT | 422 | Formato de dados inválido |
| UNAUTHORIZED | 401 | Não autenticado |
| TOKEN_EXPIRED | 401 | Token JWT expirado |
| FORBIDDEN | 403 | Sem permissão para ação |
| NOT_FOUND | 404 | Recurso não encontrado |
| DUPLICATE_ENTRY | 409 | Registro duplicado |
| CONFLICT | 409 | Conflito de estado |
| BUSINESS_ERROR | 400 | Erro de regra de negócio |
| RATE_LIMIT_EXCEEDED | 429 | Limite de requisições excedido |
| INTERNAL_SERVER_ERROR | 500 | Erro interno do servidor |

---

## 🔒 RATE LIMITING

- **Limite padrão**: 100 requisições por minuto por IP
- **Endpoints de autenticação**: 5 tentativas por minuto
- **Import/Export**: 10 operações por hora
- **WebSockets**: 1000 mensagens por minuto

Header de resposta quando limite excedido:
```
Retry-After: 60
```

---

## 📝 NOTAS IMPORTANTES

1. **CPF/CNPJ**: Sempre enviar com ou sem formatação - o sistema formata automaticamente
2. **Datas**: Sempre no formato ISO 8601 (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SSZ)
3. **Valores monetários**: Sempre com 2 casas decimais
4. **Enums**: Sempre em UPPERCASE
5. **Paginação**: Máximo de 100 itens por página
6. **Ordenação**: Adicionar `?sort=campo&order=asc|desc`
7. **Busca**: Usar `?search=termo` onde disponível

---

## 🛠️ DESENVOLVIMENTO

### Ambiente de Testes
- Base URL: `http://localhost:8000/api`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Headers Obrigatórios
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
```

### Exemplo de Requisição Completa
```bash
curl -X POST http://localhost:8000/api/eventos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1..." \
  -d '{
    "nome": "Evento Teste",
    "data": "2025-02-01",
    "horario": "20:00",
    "local": "Casa de Shows",
    "status": "ATIVO",
    "organizador_id": 1
  }'
```

---

**Versão da API**: 2.0.0
**Última Atualização**: 05/01/2025