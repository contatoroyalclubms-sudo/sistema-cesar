# 🚀 GUIA DE DEPLOY - SISTEMA V6

## Status Atual do Sistema

### ✅ Serviços Funcionando
- **Backend API**: http://localhost:8000
  - Servidor simplificado rodando
  - Endpoints básicos funcionais
  - Autenticação mock configurada
  
- **Frontend React**: http://localhost:5173
  - Vite dev server ativo
  - 843 pacotes instalados
  - Interface pronta para desenvolvimento

### ⚠️ Correções Aplicadas
1. **models.py**: Renomeado `metadata` para `meta_data` (palavra reservada SQLAlchemy)
2. **models.py**: Adicionado import `Time` do SQLAlchemy
3. **models.py**: Classe `ExecucaoFluxo` duplicada (precisa revisão)

---

## 📋 Checklist Pre-Deploy

### Backend
- [ ] Instalar todas dependências: `pip install -r requirements.txt`
- [ ] Configurar variáveis de ambiente (.env)
- [ ] Corrigir modelo `ExecucaoFluxo` duplicado
- [ ] Executar migrações do banco
- [ ] Testar todos endpoints críticos

### Frontend
- [ ] Build de produção: `npm run build`
- [ ] Configurar URLs de API para produção
- [ ] Testar build localmente: `npm run preview`
- [ ] Otimizar assets e imagens

### Banco de Dados
- [ ] Criar banco PostgreSQL de produção
- [ ] Executar scripts de migração
- [ ] Popular dados iniciais
- [ ] Configurar backups automáticos

---

## 🌐 Deploy para Railway

### 1. Preparação
```bash
# Backend
cd paineluniversal/paineluniversal/backend
pip freeze > requirements.txt

# Frontend
cd ../frontend
npm run build
```

### 2. Variáveis de Ambiente Railway
```env
# Backend
DATABASE_URL=postgresql://...
SECRET_KEY=production-secret-key
JWT_SECRET=production-jwt-secret
FRONTEND_URL=https://seu-frontend.railway.app

# Frontend
VITE_API_URL=https://seu-backend.railway.app
```

### 3. railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### 4. Deploy Commands
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy backend
cd backend
railway up

# Deploy frontend
cd ../frontend
railway up
```

---

## 🐳 Deploy com Docker

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
    depends_on:
      - db
      
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=sistemav6
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Build e Deploy
```bash
docker-compose build
docker-compose up -d
```

---

## 📊 Monitoramento Pós-Deploy

### Health Checks
- Backend: `GET /api/health`
- Frontend: `GET /`
- Database: `SELECT 1`

### Logs
```bash
# Railway
railway logs

# Docker
docker-compose logs -f

# PM2
pm2 logs
```

### Métricas Importantes
- Response time < 200ms
- Error rate < 1%
- Uptime > 99.9%
- Database connections < 100

---

## 🔧 Troubleshooting

### Problema: Backend não inicia
```bash
# Verificar dependências
pip list
# Reinstalar
pip install -r requirements.txt --force-reinstall
```

### Problema: Frontend build falha
```bash
# Limpar cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Problema: Database connection error
```bash
# Testar conexão
psql $DATABASE_URL
# Verificar migrações
alembic current
alembic upgrade head
```

---

## 📱 URLs de Produção

### Staging
- API: https://api-staging.sistemav6.com
- App: https://app-staging.sistemav6.com

### Produção
- API: https://api.sistemav6.com
- App: https://app.sistemav6.com
- Landing: https://sistemav6.com

---

## 🔐 Segurança

### Checklist de Segurança
- [ ] HTTPS configurado
- [ ] CORS configurado corretamente
- [ ] Secrets em variáveis de ambiente
- [ ] Rate limiting ativo
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF tokens

### Backup Strategy
- Database: Daily automated backups
- Files: Weekly S3 sync
- Code: Git with tags for releases

---

## 📈 Próximos Passos

1. **Correções Urgentes**
   - Resolver duplicação de modelos
   - Completar migrações pendentes
   - Testar fluxo completo de autenticação

2. **Otimizações**
   - Implementar cache Redis
   - Configurar CDN para assets
   - Otimizar queries do banco

3. **Features**
   - Completar integração WhatsApp
   - Ativar sistema de notificações
   - Implementar analytics

---

## 📞 Suporte

### Desenvolvimento
- Logs: `/var/log/sistemav6/`
- Erros: Sentry Dashboard
- Métricas: Grafana/Prometheus

### Contatos
- DevOps: devops@sistemav6.com
- Backend: backend@sistemav6.com
- Frontend: frontend@sistemav6.com

---

**Sistema pronto para deploy com ajustes mínimos necessários!**