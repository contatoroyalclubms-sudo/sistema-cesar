from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/cupons", tags=["CUPONS"])

# CUPONS - 4 endpoints

@router.get("/criar")
async def cupons_criar():
    """Endpoint criar do modulo cupons"""
    return {"status": "success", "module": "cupons", "endpoint": "criar"}

@router.get("/validar")
async def cupons_validar():
    """Endpoint validar do modulo cupons"""
    return {"status": "success", "module": "cupons", "endpoint": "validar"}

@router.get("/usar")
async def cupons_usar():
    """Endpoint usar do modulo cupons"""
    return {"status": "success", "module": "cupons", "endpoint": "usar"}

@router.get("/listar")
async def cupons_listar():
    """Endpoint listar do modulo cupons"""
    return {"status": "success", "module": "cupons", "endpoint": "listar"}
