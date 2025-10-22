from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api", tags=["PDV"])

# Constante para evitar duplicação de string
DISABLE_ERROR_DESC = "Desabilitar tratamento de erro"

# PDV - Original endpoints + Meep-compatible endpoints

@router.get("/pdv/produtos")
async def pdv_produtos():
    """Endpoint produtos do modulo pdv"""
    return {"status": "success", "module": "pdv", "endpoint": "produtos"}

@router.get("/pdv/comandas")
async def pdv_comandas():
    """Endpoint comandas do modulo pdv"""
    return {"status": "success", "module": "pdv", "endpoint": "comandas"}

@router.get("/pdv/vendas")
async def pdv_vendas():
    """Endpoint vendas do modulo pdv"""
    return {"status": "success", "module": "pdv", "endpoint": "vendas"}

@router.get("/pdv/caixa")
async def pdv_caixa():
    """Endpoint caixa do modulo pdv"""
    return {"status": "success", "module": "pdv", "endpoint": "caixa"}

@router.get("/pdv/dashboard")
async def pdv_dashboard():
    """Endpoint dashboard do modulo pdv"""
    return {"status": "success", "module": "pdv", "endpoint": "dashboard"}

@router.get("/pdv/relatorios")
async def pdv_relatorios():
    """Endpoint relatorios do modulo pdv"""
    return {"status": "success", "module": "pdv", "endpoint": "relatorios"}

# Meep-compatible PDV endpoints discovered during analysis

@router.get("/Proprietario/tipovinculo")
async def buscar_tipo_vinculo(
    local_cliente_id: str = Query(..., description="ID do local/cliente", alias="LocalClienteId"),
    disable_error: bool = Query(False, description=DISABLE_ERROR_DESC, alias="disableError")
):
    """
    Buscar tipo de vínculo dos equipamentos PDV
    Endpoint descoberto: /api/Proprietario/tipovinculo?LocalClienteId={local_id}
    """
    return {
        "tipoVinculo": "Local",
        "opcoes": ["Local", "Franquia", "Rede"],
        "localClienteId": local_cliente_id,
        "permiteMudanca": True
    }

@router.get("/Sessao/PossuiSessaoAberta/{local_id}")
async def possui_sessao_aberta(
    local_id: str,
    disable_error: bool = Query(False, description=DISABLE_ERROR_DESC, alias="disableError")
):
    """
    Verificar se existe sessão PDV aberta
    Endpoint descoberto: /api/Sessao/PossuiSessaoAberta/{local_id}
    """
    return {
        "possuiSessaoAberta": False,
        "localId": local_id,
        "sessaoAtual": None,
        "ultimaSessao": {
            "dataAbertura": "2025-01-15T08:00:00Z",
            "dataFechamento": "2025-01-15T18:00:00Z",
            "operador": "admin"
        }
    }

@router.get("/comandaseletronicas/")
async def buscar_comandas_eletronicas(
    local_cliente_id: str = Query(..., description="ID do local/cliente", alias="localClienteId"),
    disable_error: bool = Query(False, description=DISABLE_ERROR_DESC, alias="disableError")
):
    """
    Buscar comandas eletrônicas do PDV
    Endpoint descoberto: /api/comandaseletronicas/?localClienteId={local_id}
    """
    return {
        "comandas": [],
        "total": 0,
        "localClienteId": local_cliente_id,
        "configuracao": {
            "habilitado": True,
            "tipoComanda": "eletronica"
        }
    }

@router.get("/Proprietario/BuscarOperadoresDoLocal/{local_id}")
async def buscar_operadores_do_local(
    local_id: str,
    disable_error: bool = Query(False, description=DISABLE_ERROR_DESC, alias="disableError")
):
    """
    Buscar operadores/colaboradores do local para PDV
    Endpoint descoberto: /api/Proprietario/BuscarOperadoresDoLocal/{local_id}
    """
    return {
        "operadores": [
            {
                "id": "op001",
                "nome": "Operador Principal",
                "email": "operador@local.com",
                "ativo": True,
                "permissoesPDV": ["venda", "cancelamento", "desconto"]
            }
        ],
        "localId": local_id,
        "total": 1
    }

@router.get("/Contrato/Buscar/Equipamentos/{local_id}")
async def buscar_equipamentos_contrato(
    local_id: str,
    disable_error: bool = Query(False, description=DISABLE_ERROR_DESC, alias="disableError")
):
    """
    Buscar equipamentos do contrato PDV
    Endpoint descoberto: /api/Contrato/Buscar/Equipamentos/{local_id}
    """
    return {
        "equipamentos": [
            {
                "id": "eq001",
                "tipo": "PDV",
                "modelo": "Terminal Meep Pro",
                "status": "ativo",
                "ultimaConexao": "2025-01-15T14:30:00Z"
            }
        ],
        "localId": local_id,
        "contratoAtivo": True
    }
