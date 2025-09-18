from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/n8n", tags=["N8N"])

# N8N - 4 endpoints

@router.get("/webhook")
async def n8n_webhook():
    """Endpoint webhook do modulo n8n"""
    return {"status": "success", "module": "n8n", "endpoint": "webhook"}

@router.get("/trigger")
async def n8n_trigger():
    """Endpoint trigger do modulo n8n"""
    return {"status": "success", "module": "n8n", "endpoint": "trigger"}

@router.get("/meta-ads")
async def n8n_meta_ads():
    """Endpoint meta-ads do modulo n8n"""
    return {"status": "success", "module": "n8n", "endpoint": "meta-ads"}

@router.get("/crm")
async def n8n_crm():
    """Endpoint crm do modulo n8n"""
    return {"status": "success", "module": "n8n", "endpoint": "crm"}
