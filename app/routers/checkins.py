from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/checkins", tags=["CHECKINS"])

# CHECKINS - 5 endpoints

@router.get("/realizar")
async def checkins_realizar():
    """Endpoint realizar do modulo checkins"""
    return {"status": "success", "module": "checkins", "endpoint": "realizar"}

@router.get("/evento")
async def checkins_evento():
    """Endpoint evento do modulo checkins"""
    return {"status": "success", "module": "checkins", "endpoint": "evento"}

@router.get("/cpf")
async def checkins_cpf():
    """Endpoint cpf do modulo checkins"""
    return {"status": "success", "module": "checkins", "endpoint": "cpf"}

@router.get("/qr")
async def checkins_qr():
    """Endpoint qr do modulo checkins"""
    return {"status": "success", "module": "checkins", "endpoint": "qr"}

@router.get("/dashboard")
async def checkins_dashboard():
    """Endpoint dashboard do modulo checkins"""
    return {"status": "success", "module": "checkins", "endpoint": "dashboard"}
