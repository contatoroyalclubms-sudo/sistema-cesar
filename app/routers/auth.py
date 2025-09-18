from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["AUTH"])

# AUTH - 2 endpoints

@router.get("/login")
async def auth_login():
    """Endpoint login do modulo auth"""
    return {"status": "success", "module": "auth", "endpoint": "login"}

@router.get("/test")
async def auth_test():
    """Endpoint test do modulo auth"""
    return {"status": "success", "module": "auth", "endpoint": "test"}
