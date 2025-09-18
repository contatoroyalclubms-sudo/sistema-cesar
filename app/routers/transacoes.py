from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/transacoes", tags=["TRANSACOES"])

# TRANSACOES - 4 endpoints

@router.get("/criar")
async def transacoes_criar():
    """Endpoint criar do modulo transacoes"""
    return {"status": "success", "module": "transacoes", "endpoint": "criar"}

@router.get("/listar")
async def transacoes_listar():
    """Endpoint listar do modulo transacoes"""
    return {"status": "success", "module": "transacoes", "endpoint": "listar"}

@router.get("/obter")
async def transacoes_obter():
    """Endpoint obter do modulo transacoes"""
    return {"status": "success", "module": "transacoes", "endpoint": "obter"}

@router.get("/status")
async def transacoes_status():
    """Endpoint status do modulo transacoes"""
    return {"status": "success", "module": "transacoes", "endpoint": "status"}
