# 🚀 CONFIGURAÇÃO COMPLETA - PAINEL UNIVERSAL V6

## ✅ STATUS DO SISTEMA

### SERVIÇOS ATIVOS:
- ✅ **Backend Auth Server**: Porta 8003
- ✅ **Frontend Vite**: Porta 5174/5175
- ✅ **Local Auth Server**: Porta 8000
- ✅ **CORS**: Configurado para todas as portas

---

## 📂 ESTRUTURA DE ARQUIVOS CRIADOS

```
paineluniversal/
├── START_SYSTEM.bat           # Script para iniciar o sistema
├── TEST_SYSTEM.py             # Script de teste completo
├── INSTRUCOES_PARA_REINICIAR.md  # Instruções detalhadas
├── backend/
│   ├── auth_server.py         # Servidor de autenticação principal
│   ├── local_auth_server.py   # Servidor mock para desenvolvimento
│   └── .env                   # Variáveis de ambiente
└── frontend/
    ├── .env                   # Variáveis do frontend
    └── vite.config.ts         # Configuração do Vite com proxy

```

---

## 🔧 ARQUIVOS DE CONFIGURAÇÃO

### 1. Backend `.env`
```env
DATABASE_URL=sqlite:///./paineluniversal.db
SECRET_KEY=desenvolvimento-secret-key-2025
JWT_SECRET=jwt-secret-desenvolvimento-2025
HOST=0.0.0.0
PORT=8003
FRONTEND_URL=http://localhost:5174
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175
```

### 2. Frontend `.env`
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_USE_LOCAL_AUTH=true
VITE_SKIP_GOOGLE_AUTH=true
```

### 3. Vite Config
```typescript
server: {
  port: 5173,
  strictPort: false,
  proxy: {
    '/api': {
      target: 'http://localhost:8003',
      changeOrigin: true,
      secure: false,
      ws: true,
    },
  },
}
```

---

## 🚀 COMO INICIAR O SISTEMA

### Opção 1: Script Automático
```bash
# Simplesmente execute:
START_SYSTEM.bat
```

### Opção 2: Manual (2 terminais)

**Terminal 1 - Backend:**
```bash
cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\backend
python auth_server.py
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal\paineluniversal\frontend
npm run dev
```

---

## 🔑 CREDENCIAIS DE ACESSO

### Sistema Principal (auth_server.py)
| CPF | Senha | Tipo |
|-----|-------|------|
| **00000000000** | **0000** | Admin |

### Sistema Mock (local_auth_server.py)
| CPF | Senha | Tipo |
|-----|-------|------|
| **00000000000** | **admin123** | Admin |
| **11111111111** | **promoter123** | Promoter |
| **22222222222** | **cliente123** | Cliente |

---

## 🌐 URLs DO SISTEMA

- **Frontend**: http://localhost:5174 (ou 5175)
- **Backend API**: http://localhost:8003
- **Documentação API**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/api/health

---

## 🔍 ENDPOINTS DISPONÍVEIS

### Autenticação
- `POST /api/auth/login` - Login com CPF e senha
- `POST /api/auth/register` - Registro de novo usuário
- `GET /api/auth/verify-token` - Verificar token
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/me` - Dados do usuário atual

### MEEP Integration
- `GET/POST /api/meep/sync/auto/status` - Status da sincronização
- `POST /api/meep/sync/auto/force` - Forçar sincronização

### Recursos Protegidos
- `GET /api/eventos` - Listar eventos
- `GET /api/usuarios` - Listar usuários (admin only)

---

## 🛠️ SOLUÇÃO DE PROBLEMAS

### Problema: "Porta já em uso"
```bash
# Windows - Matar processos
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### Problema: "Cannot connect to backend"
1. Verifique se o backend está rodando na porta 8003
2. Confirme no terminal: "Uvicorn running on http://0.0.0.0:8003"

### Problema: "Invalid credentials"
- Use exatamente: CPF `00000000000` e senha `0000`
- Não adicione pontos ou traços no CPF

### Problema: "CORS error"
- Backend já está configurado com CORS permissivo
- Verifique se o frontend está usando o proxy correto

---

## 📊 TESTE DO SISTEMA

### Testar manualmente:
```bash
# Teste de health check
curl http://localhost:8003/api/health

# Teste de login
curl -X POST http://localhost:8003/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"cpf\":\"00000000000\",\"senha\":\"0000\"}"
```

### Teste automatizado:
```bash
cd C:\Users\User\OneDrive\Desktop\sistema-v6-novo\paineluniversal
python TEST_SYSTEM.py
```

---

## 📝 CHECKLIST DE VERIFICAÇÃO

- [ ] Backend rodando na porta 8003
- [ ] Frontend rodando na porta 5174 ou 5175
- [ ] Login funcionando com CPF 00000000000
- [ ] Sem erros de CORS no console
- [ ] WebSocket conectado (sem erros no console)
- [ ] Token salvo no localStorage após login
- [ ] Redirecionamento para dashboard após login

---

## 🔄 ATUALIZAÇÃO E MANUTENÇÃO

### Para atualizar dependências:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Para limpar cache:
```bash
# Frontend
rm -rf node_modules/.vite
npm run dev
```

---

## 📌 NOTAS IMPORTANTES

1. **NÃO usar Google OAuth** - Sistema usa apenas CPF
2. **Portas padrão**: Backend 8003, Frontend 5174
3. **CORS está totalmente aberto** para desenvolvimento
4. **Tokens JWT** expiram em 24 horas
5. **SQLite** para desenvolvimento, PostgreSQL para produção

---

## ✨ RECURSOS ADICIONAIS

- Script de inicialização: `START_SYSTEM.bat`
- Script de teste: `TEST_SYSTEM.py`
- Servidor mock: `local_auth_server.py`
- Instruções detalhadas: `INSTRUCOES_PARA_REINICIAR.md`

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Sistema básico funcionando
2. ✅ Autenticação configurada
3. ✅ CORS resolvido
4. ⬜ Implementar mais endpoints
5. ⬜ Adicionar testes automatizados
6. ⬜ Configurar CI/CD
7. ⬜ Deploy em produção

---

**Última atualização:** 11/09/2025
**Versão:** 1.0.0
**Status:** ✅ FUNCIONANDO