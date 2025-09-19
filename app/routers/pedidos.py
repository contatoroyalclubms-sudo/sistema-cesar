from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/pedidos", tags=["PEDIDOS"])

# PEDIDOS - gestão de pedidos e comandas

@router.get("/")
async def listar_pedidos():
    """Lista todos os pedidos"""
    return {"status": "success", "module": "pedidos", "endpoint": "listar"}

@router.get("/{pedido_id}")
async def obter_pedido(pedido_id: int):
    """Obtém detalhes de um pedido específico"""
    return {"status": "success", "pedido_id": pedido_id}

@router.post("/")
async def criar_pedido():
    """Cria novo pedido"""
    return {"status": "success", "message": "Pedido criado"}

@router.put("/{pedido_id}")
async def atualizar_pedido(pedido_id: int):
    """Atualiza pedido existente"""
    return {"status": "success", "pedido_id": pedido_id}

@router.delete("/{pedido_id}")
async def cancelar_pedido(pedido_id: int):
    """Cancela um pedido"""
    return {"status": "success", "pedido_id": pedido_id}

@router.post("/{pedido_id}/itens")
async def adicionar_item_pedido(pedido_id: int):
    """Adiciona item ao pedido"""
    return {"status": "success", "pedido_id": pedido_id}

@router.delete("/{pedido_id}/itens/{item_id}")
async def remover_item_pedido(pedido_id: int, item_id: int):
    """Remove item do pedido"""
    return {"status": "success", "pedido_id": pedido_id, "item_id": item_id}

@router.post("/{pedido_id}/fechar")
async def fechar_pedido(pedido_id: int):
    """Fecha pedido e envia para pagamento"""
    return {"status": "success", "pedido_id": pedido_id}

@router.get("/mesa/{mesa_id}")
async def obter_pedidos_mesa(mesa_id: int):
    """Obtém pedidos de uma mesa"""
    return {"status": "success", "mesa_id": mesa_id}

@router.get("/comanda/{comanda_id}")
async def obter_pedidos_comanda(comanda_id: str):
    """Obtém pedidos de uma comanda"""
    return {"status": "success", "comanda_id": comanda_id}

@router.post("/delivery")
async def criar_pedido_delivery():
    """Cria pedido para delivery"""
    return {"status": "success", "message": "Pedido delivery criado"}

@router.get("/cozinha")
async def listar_pedidos_cozinha():
    """Lista pedidos para preparação na cozinha"""
    return {"status": "success", "endpoint": "cozinha"}

@router.put("/{pedido_id}/status")
async def atualizar_status_pedido(pedido_id: int):
    """Atualiza status do pedido (preparando, pronto, entregue)"""
    return {"status": "success", "pedido_id": pedido_id}