# 🔄 GUIA DE MIGRAÇÃO - SISTEMA REFATORADO

## ⚠️ IMPORTANTE: FAZER BACKUP ANTES DE MIGRAR

```bash
# Backup completo
cp -r . ../backup_sistema_$(date +%Y%m%d)

# Backup do banco de dados
cp backend/eventos.db backend/eventos.db.backup_$(date +%Y%m%d)
```

---

## 📋 CHECKLIST DE MIGRAÇÃO

### PRÉ-MIGRAÇÃO
- [ ] Backup completo do sistema
- [ ] Backup do banco de dados
- [ ] Notificar usuários sobre manutenção
- [ ] Parar todos os serviços

### MIGRAÇÃO
- [ ] Aplicar mudanças no banco de dados
- [ ] Atualizar código backend
- [ ] Atualizar código frontend
- [ ] Rodar testes de integração
- [ ] Verificar logs de erro

### PÓS-MIGRAÇÃO
- [ ] Testar funcionalidades críticas
- [ ] Monitorar logs por 24h
- [ ] Coletar feedback dos usuários
- [ ] Documentar problemas encontrados

---

## 🚀 PASSO A PASSO DA MIGRAÇÃO

### PASSO 1: Preparar Ambiente
```bash
# Parar todos os serviços
pkill -f uvicorn
pkill -f "npm run dev"

# Criar branch de migração
git checkout -b migracao-v2
```

### PASSO 2: Migrar Banco de Dados
```bash
cd backend

# 1. Fazer backup
cp eventos.db eventos.db.pre_migration

# 2. Aplicar migração de enums (CRÍTICO!)
python migrations/standardize_enums_migration.py

# 3. Verificar migração
python -c "
from app.database import get_db
from sqlalchemy import text
db = next(get_db())
result = db.execute(text('SELECT DISTINCT status FROM eventos'))
print('Status encontrados:', [r[0] for r in result])
"

# Resultado esperado: ['ATIVO', 'INATIVO', 'CANCELADO', 'FINALIZADO']
```

### PASSO 3: Atualizar Backend
```bash
cd backend

# 1. Atualizar dependências
poetry install

# 2. Copiar novos arquivos
# - app/enums.py
# - app/validators.py
# - app/schemas_completo.py
# - app/error_handlers.py

# 3. Atualizar main.py para usar novos handlers
# Adicionar no main.py:
from app.error_handlers import register_error_handlers
register_error_handlers(app)

# 4. Testar backend
poetry run pytest tests/test_integration_complete.py -v

# 5. Iniciar servidor de teste
poetry run uvicorn app.main:app --reload --port 8000
```

### PASSO 4: Atualizar Frontend
```bash
cd frontend

# 1. Instalar dependências
npm install

# 2. Copiar novos arquivos
# - src/types/enums.ts
# - src/types/interfaces.ts  
# - src/lib/validators.ts
# - src/lib/errorHandler.ts

# 3. Atualizar imports nos componentes
# Trocar enums antigos pelos novos:
# import { StatusEvento } from '@/types/enums';

# 4. Build de teste
npm run build

# 5. Testar frontend
npm run dev
```

### PASSO 5: Validar Sistema Completo
```bash
# 1. Teste de criação de usuário
curl -X POST http://localhost:8000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste Migration",
    "email": "teste@migration.com",
    "cpf": "123.456.789-09",
    "senha": "senha123",
    "role": "CLIENTE"
  }'

# 2. Teste de criação de evento
curl -X POST http://localhost:8000/api/eventos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nome": "Evento Teste",
    "data": "2025-01-10",
    "local": "Local Teste",
    "status": "ATIVO"
  }'

# 3. Verificar logs
tail -f backend/logs/app.log
```

---

## 🔧 MUDANÇAS NO CÓDIGO EXISTENTE

### 1. ENUMS - Atualizar de lowercase para UPPERCASE

#### ❌ ANTES:
```python
# Backend
status = "ativo"
tipo_lista = "vip"

# Frontend
status: 'ativo'
tipoLista: 'vip'
```

#### ✅ DEPOIS:
```python
# Backend
from app.enums import StatusEvento, TipoLista
status = StatusEvento.ATIVO
tipo_lista = TipoLista.VIP

# Frontend
import { StatusEvento, TipoLista } from '@/types/enums';
status: StatusEvento.ATIVO
tipoLista: TipoLista.VIP
```

### 2. VALIDAÇÕES - Usar validadores centralizados

#### ❌ ANTES:
```python
# Validação manual
if len(cpf) != 11:
    raise ValueError("CPF inválido")
```

#### ✅ DEPOIS:
```python
from app.validators import validar_cpf, formatar_cpf

cpf_formatado = formatar_cpf(cpf_input)
validar_cpf(cpf_formatado)  # Lança exceção se inválido
```

### 3. TRATAMENTO DE ERROS - Usar classes customizadas

#### ❌ ANTES:
```python
raise HTTPException(status_code=404, detail="Not found")
```

#### ✅ DEPOIS:
```python
from app.error_handlers import NotFoundError

raise NotFoundError("Evento", evento_id)
```

### 4. SCHEMAS - Usar schemas completos

#### ❌ ANTES:
```python
# Schemas parciais em vários arquivos
from app.schemas import UserBase
```

#### ✅ DEPOIS:
```python
from app.schemas_completo import UsuarioCreate, UsuarioResponse

@router.post("/", response_model=UsuarioResponse)
def create_user(user: UsuarioCreate):
    # ...
```

---

## 🐛 PROBLEMAS COMUNS E SOLUÇÕES

### PROBLEMA 1: "Enum value 'ativo' is not valid"
**Causa**: Banco ainda tem valores em lowercase
**Solução**:
```bash
cd backend
python migrations/standardize_enums_migration.py
```

### PROBLEMA 2: "CPF validation failed"
**Causa**: CPF sem formatação ou inválido
**Solução**:
```python
from app.validators import formatar_cpf
cpf = formatar_cpf("12345678909")  # Adiciona formatação
```

### PROBLEMA 3: "Cannot import enums"
**Causa**: Arquivo de enums não copiado
**Solução**:
```bash
# Backend
cp caminho/para/enums.py backend/app/enums.py

# Frontend  
cp caminho/para/enums.ts frontend/src/types/enums.ts
```

### PROBLEMA 4: "CORS errors"
**Causa**: Middleware não configurado
**Solução**: Verificar `backend/app/main.py`:
```python
from app.middleware import UltimateCORSMiddleware
app.add_middleware(UltimateCORSMiddleware)
```

---

## 📊 TESTES DE VALIDAÇÃO PÓS-MIGRAÇÃO

### Teste 1: Validação de CPF
```python
# backend/test_migration.py
from app.validators import validar_cpf

# Deve passar
assert validar_cpf("123.456.789-09", raise_error=False) is not None

# Deve falhar
assert validar_cpf("111.111.111-11", raise_error=False) is None
```

### Teste 2: Enums
```python
from app.enums import StatusEvento
from app.database import get_db
from sqlalchemy import text

db = next(get_db())
result = db.execute(text("SELECT DISTINCT status FROM eventos"))
statuses = [r[0] for r in result]

# Todos devem ser UPPERCASE
assert all(s == s.upper() for s in statuses)
```

### Teste 3: Tratamento de Erros
```bash
# Deve retornar erro formatado
curl http://localhost:8000/api/usuarios/99999

# Resposta esperada:
{
  "error": "Usuario não encontrado (ID: 99999)",
  "code": "NOT_FOUND",
  "timestamp": "2025-01-05T..."
}
```

---

## 🔄 ROLLBACK (EM CASO DE PROBLEMAS)

### Reverter Banco de Dados:
```bash
cd backend

# Reverter enums para lowercase
python migrations/standardize_enums_migration.py --rollback

# Ou restaurar backup
cp eventos.db.backup eventos.db
```

### Reverter Código:
```bash
# Voltar para branch anterior
git checkout main
git branch -D migracao-v2

# Reiniciar serviços
./start_services.sh
```

---

## 📈 MONITORAMENTO PÓS-MIGRAÇÃO

### 1. Logs a Monitorar:
```bash
# Backend logs
tail -f backend/logs/app.log | grep ERROR

# Frontend console
# Abrir DevTools no navegador e monitorar Console

# Database queries
tail -f backend/logs/sql.log
```

### 2. Métricas a Acompanhar:
- Taxa de erro HTTP 4xx e 5xx
- Tempo de resposta das APIs
- Erros de validação por endpoint
- Falhas de autenticação

### 3. Alertas a Configurar:
```python
# Exemplo de alerta para muitos erros
if error_count > 100:
    send_alert("Alto volume de erros pós-migração")
```

---

## ✅ CRITÉRIOS DE SUCESSO

A migração é considerada **BEM-SUCEDIDA** quando:

1. ✅ Todos os testes passam (`pytest` e `npm test`)
2. ✅ Nenhum erro 500 nas últimas 2 horas
3. ✅ Taxa de erro < 1% das requisições
4. ✅ Todas as funcionalidades críticas operacionais:
   - Login/Logout
   - Criar/Editar eventos
   - Check-in de participantes
   - PDV funcionando
   - Relatórios gerando

---

## 📞 SUPORTE

Em caso de problemas durante a migração:

1. **Verificar documentação**: `DOCUMENTACAO_REFATORACAO.md`
2. **Consultar logs**: `backend/logs/migration.log`
3. **Rollback imediato** se sistema crítico afetado
4. **Documentar problema** para correção futura

---

## 🎉 CONCLUSÃO

Após completar todos os passos:

1. **Comemorar** a migração bem-sucedida! 🎊
2. **Monitorar** sistema por 48h
3. **Coletar feedback** dos usuários
4. **Documentar melhorias** para próxima versão

**Versão do Sistema**: 2.0.0
**Data da Migração**: ___/___/2025
**Responsável**: ________________

---

*Boa sorte com a migração! O sistema está muito mais robusto agora.* 💪