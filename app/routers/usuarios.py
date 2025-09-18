from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/usuarios", tags=["USUARIOS"])

# USUARIOS - 5 endpoints

@router.get("/criar")
async def usuarios_criar():
    """Endpoint criar do modulo usuarios"""
    return {"status": "success", "module": "usuarios", "endpoint": "criar"}

@router.get("/listar")
async def usuarios_listar():
    """Endpoint listar do modulo usuarios"""
    return {"status": "success", "module": "usuarios", "endpoint": "listar"}

@router.get("/obter")
async def usuarios_obter():
    """Endpoint obter do modulo usuarios"""
    return {"status": "success", "module": "usuarios", "endpoint": "obter"}

@router.get("/atualizar")
async def usuarios_atualizar():
    """Endpoint atualizar do modulo usuarios"""
    return {"status": "success", "module": "usuarios", "endpoint": "atualizar"}

@router.get("/desativar")
async def usuarios_desativar():
    """Endpoint desativar do modulo usuarios"""
    return {"status": "success", "module": "usuarios", "endpoint": "desativar"}
