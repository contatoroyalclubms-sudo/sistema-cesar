from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])
security = HTTPBearer()

# Schemas
class EmpresaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200, description="Nome da empresa")
    cnpj: Optional[str] = Field(None, pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', description="CNPJ no formato XX.XXX.XXX/XXXX-XX")
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="Email da empresa")
    telefone: Optional[str] = Field(None, description="Telefone da empresa")
    endereco: Optional[str] = Field(None, description="Endereço da empresa")

class EmpresaCreate(EmpresaBase):
    nome: str = Field(..., examples=["Empresa Exemplo Ltda"])
    cnpj: str = Field(..., examples=["12.345.678/0001-90"])
    email: Optional[str] = Field(None, examples=["contato@empresa.com"])

class EmpresaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None

class EmpresaResponse(EmpresaBase):
    id: str = Field(..., description="ID único da empresa")
    status: str = Field(default="ativo", description="Status da empresa")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")

class EmpresaStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r'^(ativo|inativo|suspenso)$', description="Novo status")
    motivo: Optional[str] = Field(None, description="Motivo da alteração")

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    meta: Optional[dict] = None

class PaginatedResponse(BaseModel):
    status: str = "success"
    message: str
    data: dict
    meta: dict

# Simulação de dados (em produção, usar banco de dados)
fake_empresas_db = {}

# Dependency para autenticação
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validação JWT simplificada (implementar validação completa em produção)
    return {"email": "admin@nip.com", "id": "admin-123"}

# ENDPOINTS REST NORMALIZADOS

@router.get("", response_model=PaginatedResponse, status_code=200)
async def listar_empresas(
    page: int = Query(1, ge=1, description="Número da página"),
    pageSize: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Buscar por nome ou CNPJ"),
    sort: Optional[str] = Query("created_at", description="Campo de ordenação"),
    order: Optional[str] = Query("desc", pattern=r'^(asc|desc)$', description="Direção da ordenação"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por status"),
    current_user = Depends(get_current_user)
):
    """
    Listar empresas com paginação e filtros
    
    - **page**: Número da página (padrão: 1)
    - **pageSize**: Itens por página (padrão: 20, máximo: 100)
    - **search**: Buscar por nome ou CNPJ
    - **sort**: Campo de ordenação (padrão: created_at)
    - **order**: asc ou desc (padrão: desc)
    - **status**: Filtrar por status (ativo, inativo, suspenso)
    """
    # Simulação de dados paginados
    total_items = len(fake_empresas_db)
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize
    
    empresas = list(fake_empresas_db.values())[start_idx:end_idx]
    
    return PaginatedResponse(
        status="success",
        message=f"Lista de empresas (página {page})",
        data={
            "empresas": empresas,
            "filters_applied": {
                "search": search,
                "status": status_filter,
                "sort": f"{sort} {order}"
            }
        },
        meta={
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": total_items,
                "totalPages": (total_items + pageSize - 1) // pageSize,
                "hasNext": end_idx < total_items,
                "hasPrev": page > 1
            },
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid4())
        }
    )

@router.post("", response_model=APIResponse, status_code=201)
async def criar_empresa(
    empresa: EmpresaCreate,
    response: Response,
    current_user = Depends(get_current_user)
):
    """
    Criar nova empresa
    
    Retorna 201 Created com header Location.
    """
    # Validar CNPJ único
    for existing_empresa in fake_empresas_db.values():
        if existing_empresa.get("cnpj") == empresa.cnpj:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="CNPJ já cadastrado"
            )
    
    # Criar nova empresa
    empresa_id = str(uuid4())
    nova_empresa = {
        "id": empresa_id,
        "nome": empresa.nome,
        "cnpj": empresa.cnpj,
        "email": empresa.email,
        "telefone": empresa.telefone,
        "status": "ativo",
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "created_by": current_user["email"]
    }
    
    fake_empresas_db[empresa_id] = nova_empresa
    
    # Header Location obrigatório para 201
    response.headers["Location"] = f"/api/empresas/{empresa_id}"
    
    return APIResponse(
        status="success",
        message="Empresa criada com sucesso",
        data=nova_empresa,
        meta={
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid4())
        }
    )

@router.get("/{empresa_id}", response_model=APIResponse, status_code=200)
async def obter_empresa(
    empresa_id: str = Path(..., description="ID da empresa"),
    current_user = Depends(get_current_user)
):
    """
    Obter empresa específica por ID
    """
    if empresa_id not in fake_empresas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    empresa = fake_empresas_db[empresa_id]
    
    return APIResponse(
        status="success",
        message="Empresa encontrada",
        data=empresa,
        meta={
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid4())
        }
    )

@router.put("/{empresa_id}", response_model=APIResponse, status_code=200)
async def atualizar_empresa(
    empresa_update: EmpresaUpdate,
    empresa_id: str = Path(..., description="ID da empresa"),
    current_user = Depends(get_current_user)
):
    """
    Atualizar empresa completamente
    """
    if empresa_id not in fake_empresas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    empresa = fake_empresas_db[empresa_id]
    
    # Atualizar campos fornecidos
    update_data = empresa_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        empresa[field] = value
    
    empresa["updated_at"] = datetime.now().isoformat()
    empresa["updated_by"] = current_user["email"]
    
    fake_empresas_db[empresa_id] = empresa
    
    return APIResponse(
        status="success",
        message="Empresa atualizada com sucesso",
        data=empresa,
        meta={
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid4())
        }
    )

@router.delete("/{empresa_id}", status_code=204)
async def remover_empresa(
    empresa_id: str = Path(..., description="ID da empresa"),
    current_user = Depends(get_current_user)
):
    """
    Remover empresa (exclusão lógica)
    
    Retorna 204 No Content (sem body de resposta).
    """
    if empresa_id not in fake_empresas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Em produção, fazer exclusão lógica (status = 'removido')
    del fake_empresas_db[empresa_id]
    
    # 204 não retorna body
    return None

@router.patch("/{empresa_id}/status", response_model=APIResponse, status_code=200)
async def alterar_status_empresa(
    status_update: EmpresaStatusUpdate,
    empresa_id: str = Path(..., description="ID da empresa"),
    current_user = Depends(get_current_user)
):
    """
    Alterar status da empresa (ativar/desativar/suspender)
    """
    if empresa_id not in fake_empresas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    empresa = fake_empresas_db[empresa_id]
    status_anterior = empresa["status"]
    
    empresa["status"] = status_update.status
    empresa["updated_at"] = datetime.now().isoformat()
    empresa["status_changed_by"] = current_user["email"]
    
    if status_update.motivo:
        empresa["status_change_reason"] = status_update.motivo
    
    fake_empresas_db[empresa_id] = empresa
    
    return APIResponse(
        status="success",
        message=f"Status alterado de '{status_anterior}' para '{status_update.status}'",
        data={
            "empresa_id": empresa_id,
            "status_anterior": status_anterior,
            "status_novo": status_update.status,
            "motivo": status_update.motivo
        },
        meta={
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid4())
        }
    )

# =============================================================================
# ROTAS LEGADAS (DEPRECATED) - Compatibilidade
# =============================================================================

@router.get("/criar", deprecated=True, status_code=301)
async def empresas_criar_deprecated():
    """
    [DEPRECATED] Endpoint legacy para criar empresa
    
    ⚠️ DEPRECATED: Use POST /api/empresas
    """
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="Endpoint movido permanentemente",
        headers={"Location": "/api/empresas"}
    )

@router.get("/listar", deprecated=True, status_code=301)
async def empresas_listar_deprecated():
    """
    [DEPRECATED] Endpoint legacy para listar empresas
    
    ⚠️ DEPRECATED: Use GET /api/empresas
    """
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="Endpoint movido permanentemente",
        headers={"Location": "/api/empresas"}
    )

@router.get("/obter", deprecated=True, status_code=301)
async def empresas_obter_deprecated():
    """
    [DEPRECATED] Endpoint legacy para obter empresa
    
    ⚠️ DEPRECATED: Use GET /api/empresas/{id}
    """
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="Endpoint movido permanentemente",
        headers={"Location": "/api/empresas/{id}"}
    )

@router.get("/atualizar", deprecated=True, status_code=301)
async def empresas_atualizar_deprecated():
    """
    [DEPRECATED] Endpoint legacy para atualizar empresa
    
    ⚠️ DEPRECATED: Use PUT /api/empresas/{id}
    """
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="Endpoint movido permanentemente",
        headers={"Location": "/api/empresas/{id}"}
    )

@router.get("/ativar", deprecated=True, status_code=301)
async def empresas_ativar_deprecated():
    """
    [DEPRECATED] Endpoint legacy para ativar empresa
    
    ⚠️ DEPRECATED: Use PATCH /api/empresas/{id}/status
    """
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="Endpoint movido permanentemente",
        headers={"Location": "/api/empresas/{id}/status"}
    )

@router.get("/desativar", deprecated=True, status_code=301)
async def empresas_desativar_deprecated():
    """
    [DEPRECATED] Endpoint legacy para desativar empresa
    
    ⚠️ DEPRECATED: Use PATCH /api/empresas/{id}/status
    """
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="Endpoint movido permanentemente",
        headers={"Location": "/api/empresas/{id}/status"}
    )
