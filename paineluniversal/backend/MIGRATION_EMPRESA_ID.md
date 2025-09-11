# Migração: Remoção da Dependência de Empresa na Criação de Usuários

## Problema Resolvido
- **Erro Original**: `null value in column "empresa_id" violates not-null constraint`
- **Causa**: Campo `empresa_id` era obrigatório na criação de usuários
- **Regra de Negócio**: Empresa deve ser vinculada ao usuário posteriormente no sistema

## Alterações Realizadas

### 1. Modelo de Dados (`app/models.py`)
```python
# ANTES: empresa_id obrigatório
empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

# DEPOIS: empresa_id opcional  
empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
```

### 2. Endpoint de Criação (`app/routers/usuarios.py`)
```python
# ANTES: Lógica de empresa padrão forçada
if not usuario.empresa_id:
    empresa_padrao = db.query(Empresa).filter(Empresa.ativa == True).first()
    usuario.empresa_id = empresa_padrao.id

# DEPOIS: Validação opcional
if usuario.empresa_id:
    empresa = db.query(Empresa).filter(Empresa.id == usuario.empresa_id).first()
    if not empresa:
        raise HTTPException(404, "Empresa não encontrada")
```

### 3. Função de Permissões (`app/auth.py`)
Nova função para verificar permissões considerando usuários sem empresa:
```python
def verificar_permissao_empresa(usuario_atual: Usuario, empresa_id: Optional[int]) -> bool:
    """
    Regras:
    - Admins têm acesso a todas as empresas
    - Usuários sem empresa (empresa_id=None) só acessam recursos sem empresa específica
    - Usuários com empresa só acessam recursos da sua empresa
    """
```

## Migração PostgreSQL

### Para Produção
Execute o script SQL no PostgreSQL de produção:

```sql
-- Verificar estrutura atual
SELECT column_name, is_nullable, data_type
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'empresa_id';

-- Remover constraint NOT NULL
ALTER TABLE usuarios ALTER COLUMN empresa_id DROP NOT NULL;

-- Verificar alteração
SELECT column_name, is_nullable, data_type
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'empresa_id';
```

### Aplicação Automática
```bash
# No servidor de produção
cd backend
python apply_postgresql_migration.py
```

## Comportamento Atual

### ✅ Funcionalidades que Funcionam
- ✅ Criar usuário **sem empresa** (`empresa_id: null`)
- ✅ Criar usuário **com empresa válida** (`empresa_id: 1`) 
- ✅ Validação de empresa fornecida
- ✅ Permissões baseadas na empresa do usuário
- ✅ Frontend permite empresa opcional

### 📋 Fluxo de Uso
1. **Registro inicial**: Usuário criado sem empresa
2. **Onboarding**: Posteriormente vinculado à empresa no sistema  
3. **Permissões**: Baseadas na empresa vinculada (ou admin global)

## Arquivos Criados/Modificados

### Criados
- `backend/postgresql_migration.sql` - Script SQL para PostgreSQL
- `backend/apply_postgresql_migration.py` - Aplicação automática da migração
- `backend/MIGRATION_EMPRESA_ID.md` - Esta documentação

### Modificados  
- `backend/app/routers/usuarios.py` - Endpoint de criação
- `backend/app/auth.py` - Nova função de permissões
- `frontend/src/components/usuarios/CadastroUsuarioModal.tsx` - Já suportava empresa opcional

## Teste de Validação

```python
# Teste realizado com sucesso
usuario_data = UsuarioCreate(
    cpf='00000000191',
    nome='Usuario Sem Empresa', 
    email='semempresa@teste.com',
    senha='senha123',
    tipo=TipoUsuario.CLIENTE,
    empresa_id=None  # ✅ Permitido
)

# Resultado: Usuario criado com empresa_id: None
```

## Próximos Passos

1. **Validar em produção**: Aplicar migração no PostgreSQL de produção
2. **Implementar onboarding**: Sistema para vincular empresa posteriormente
3. **Ajustar permissões**: Revisar endpoints que usam `usuario_atual.empresa_id`
4. **Documentar processo**: Como vincular empresa ao usuário no sistema

---
**Status**: ✅ Implementado e testado  
**Ambiente**: Desenvolvimento (SQLite) - Pronto para produção (PostgreSQL)