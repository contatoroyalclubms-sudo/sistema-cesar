# 🚀 URLS DE TESTE - INTEGRAÇÃO MEEP

## 🌐 FRONTEND (React + Vite)

### Aplicação Principal
- **URL Base**: http://localhost:5174
- **Login**: http://localhost:5174/login
  - CPF: `00000000000`
  - Senha: `0000`

### Módulos MEEP
- **Dashboard MEEP**: http://localhost:5174/meep/dashboard
- **Analytics MEEP**: http://localhost:5174/meep/analytics
- **Validação CPF**: http://localhost:5174/meep/validacao-cpf
- **Equipamentos**: http://localhost:5174/meep/equipamentos

---

## 🔧 BACKEND (FastAPI)

### Servidor de Autenticação (Porta 8003)
- **Base**: http://localhost:8003
- **Docs**: http://localhost:8003/docs
- **Health**: http://localhost:8003/api/health
- **Login**: POST http://localhost:8003/api/auth/login

### Servidor MEEP Test (Porta 8004)
- **Base**: http://localhost:8004
- **Docs**: http://localhost:8004/docs
- **Status**: http://localhost:8004/api/meep/status

### Endpoints MEEP
```bash
# Status do Serviço
GET http://localhost:8004/api/meep/status

# Criar Integração
POST http://localhost:8004/api/meep/integrate?evento_id=1&meep_event_id=test123&api_key=key123

# Obter Integração
GET http://localhost:8004/api/meep/integration/1

# Criar Analytics
POST http://localhost:8004/api/meep/analytics/1?total_requests=100&unique_visitors=50

# Obter Analytics
GET http://localhost:8004/api/meep/analytics/1
```

---

## 🧪 TESTES RÁPIDOS

### 1. Testar Frontend
```bash
# Abrir no navegador
start http://localhost:5174
```

### 2. Testar Backend Auth
```bash
# Login
curl -X POST http://localhost:8003/api/auth/login -H "Content-Type: application/json" -d "{\"cpf\":\"00000000000\",\"senha\":\"0000\"}"
```

### 3. Testar MEEP API
```bash
# Status
curl http://localhost:8004/api/meep/status

# Criar integração
curl -X POST "http://localhost:8004/api/meep/integrate?evento_id=1&meep_event_id=meep123&api_key=key123"

# Ver analytics
curl http://localhost:8004/api/meep/analytics/1
```

---

## 📊 SERVIÇOS EM EXECUÇÃO

| Serviço | Porta | Status | Descrição |
|---------|-------|--------|-----------|
| Frontend React | 5174 | ✅ Rodando | Interface principal |
| Auth Server | 8003 | ✅ Rodando | Autenticação |
| MEEP Test Server | 8004 | ✅ Rodando | API MEEP |
| Main Backend | 8000 | ⚠️ Com erros | Backend principal |

---

## 🔍 SCRIPTS DE CAPTURA

Todos os scripts estão rodando em background:
- `meep-ultimate-capture.js` - Captura principal
- `meep-reverse-engineering.js` - Análise reversa
- `missao-completa-mcp.js` - Automação completa

---

## 📝 COMANDOS ÚTEIS

### Verificar Logs
```bash
# Ver logs do frontend
# (Terminal com ID: 64072c)

# Ver logs do auth server
# (Terminal com ID: 609d14)

# Ver logs do MEEP server
# (Terminal com ID: 602fd6)
```

### Abrir Todas as URLs
```bash
# Frontend
start http://localhost:5174/login
start http://localhost:5174/meep/dashboard

# Backend Docs
start http://localhost:8003/docs
start http://localhost:8004/docs
```

---

## ✅ CHECKLIST DE TESTE

- [ ] Login no sistema (http://localhost:5174)
- [ ] Acessar Dashboard MEEP
- [ ] Testar criação de integração
- [ ] Visualizar analytics
- [ ] Testar captura de dados
- [ ] Verificar WebSocket funcionando
- [ ] Testar validação de CPF

---

## 🎯 ACESSO DIRETO

### Para testar agora:
1. **Frontend MEEP**: http://localhost:5174/meep/dashboard
2. **API Docs**: http://localhost:8004/docs
3. **Login**: CPF `00000000000` / Senha `0000`

---

**TUDO PRONTO PARA TESTES!** 🚀