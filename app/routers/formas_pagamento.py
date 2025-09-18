from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/formas-pagamento", tags=["FORMAS-PAGAMENTO"])

# FORMAS-PAGAMENTO - 7 endpoints

@router.get("/listar")
async def formas_pagamento_listar():
    """Endpoint listar do modulo formas-pagamento"""
    return {"status": "success", "module": "formas-pagamento", "endpoint": "listar"}

@router.get("/criar")
async def formas_pagamento_criar():
    """Endpoint criar do modulo formas-pagamento"""
    return {"status": "success", "module": "formas-pagamento", "endpoint": "criar"}

@router.get("/obter")
async def formas_pagamento_obter():
    """Endpoint obter do modulo formas-pagamento"""
    return {"status": "success", "module": "formas-pagamento", "endpoint": "obter"}

@router.get("/atualizar")
async def formas_pagamento_atualizar():
    """Endpoint atualizar do modulo formas-pagamento"""
    return {"status": "success", "module": "formas-pagamento", "endpoint": "atualizar"}

@router.get("/excluir")
async def formas_pagamento_excluir():
    """Endpoint excluir do modulo formas-pagamento"""
    return {"status": "success", "module": "formas-pagamento", "endpoint": "excluir"}

@router.get("/toggle")
async def formas_pagamento_toggle():
    """Endpoint toggle do modulo formas-pagamento"""
    return {"status": "success", "module": "formas-pagamento", "endpoint": "toggle"}

@router.get("/tipos")
async def formas_pagamento_tipos():
    """Endpoint tipos do modulo formas-pagamento"""
    return {"status": "success", "module": "formas-pagamento", "endpoint": "tipos"}
