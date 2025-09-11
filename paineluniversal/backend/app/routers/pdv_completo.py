"""
Router para PDV Completo - Sistema de Ponto de Venda avançado
Vendas, formas de pagamento, descontos, impressão de recibos
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import asyncio

from ..database import get_db
from ..auth import get_current_user, get_websocket_user
from ..models import (
    Usuario, Venda, ItemVenda, Produto, Cliente, Evento,
    Caixa, FechamentoCaixa, Desconto, FormaPagamento,
    ConfiguracaoPDV, CartaoCashless, TransacaoCashless
)
from ..schemas_meep_complete import (
    VendaCreate, VendaResponse, ItemVendaBase
)

router = APIRouter(
    prefix="/api/pdv",
    tags=["PDV - Ponto de Venda"]
)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, caixa_id: int):
        await websocket.accept()
        if caixa_id not in self.active_connections:
            self.active_connections[caixa_id] = []
        self.active_connections[caixa_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, caixa_id: int):
        if caixa_id in self.active_connections:
            self.active_connections[caixa_id].remove(websocket)
    
    async def broadcast_to_caixa(self, message: dict, caixa_id: int):
        if caixa_id in self.active_connections:
            for connection in self.active_connections[caixa_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

@router.post("/venda/create", response_model=VendaResponse)
async def criar_venda(
    venda: VendaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova venda no PDV
    Replica funcionalidade: Sistema PDV > Nova Venda
    """
    
    # Gerar número da venda
    ultima_venda = db.query(Venda).order_by(desc(Venda.id)).first()
    numero_venda = f"V{str(ultima_venda.id + 1).zfill(6)}" if ultima_venda else "V000001"
    
    # Calcular total
    valor_total = Decimal(0)
    for item in venda.itens:
        valor_total += item.quantidade * item.preco_unitario
    
    # Aplicar desconto
    if venda.desconto:
        valor_total -= venda.desconto
    
    # Criar venda
    nova_venda = Venda(
        numero_venda=numero_venda,
        evento_id=venda.evento_id,
        vendedor_id=venda.vendedor_id,
        cliente_cpf=venda.cliente_cpf,
        tipo_pagamento=venda.tipo_pagamento,
        valor_total=valor_total,
        desconto=venda.desconto or Decimal(0),
        observacoes=venda.observacoes,
        status="CONCLUIDA"
    )
    
    db.add(nova_venda)
    db.flush()
    
    # Adicionar itens
    for item in venda.itens:
        novo_item = ItemVenda(
            venda_id=nova_venda.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            valor_total=item.quantidade * item.preco_unitario
        )
        db.add(novo_item)
        
        # Atualizar estoque
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if produto:
            produto.estoque_atual -= item.quantidade
    
    # Se pagamento cashless, debitar do saldo
    if venda.tipo_pagamento == "CASHLESS" and venda.cliente_cpf:
        cliente = db.query(Cliente).filter(Cliente.cpf == venda.cliente_cpf).first()
        if cliente:
            if cliente.saldo_cashless >= valor_total:
                cliente.saldo_cashless -= valor_total
                
                # Registrar transação
                transacao = TransacaoCashless(
                    cliente_id=cliente.id,
                    tipo="DEBITO",
                    valor=valor_total,
                    descricao=f"Compra PDV - {numero_venda}",
                    saldo_anterior=cliente.saldo_cashless + valor_total,
                    saldo_posterior=cliente.saldo_cashless
                )
                db.add(transacao)
            else:
                raise HTTPException(status_code=400, detail="Saldo cashless insuficiente")
    
    # Adicionar pontos de fidelidade
    if venda.cliente_cpf:
        cliente = db.query(Cliente).filter(Cliente.cpf == venda.cliente_cpf).first()
        if cliente:
            pontos_ganhos = int(valor_total * 10)  # 10 pontos por real
            cliente.pontos_fidelidade += pontos_ganhos
    
    db.commit()
    db.refresh(nova_venda)
    
    # Broadcast venda para WebSocket
    await manager.broadcast_to_caixa(
        {"tipo": "nova_venda", "venda": {"id": nova_venda.id, "valor": float(valor_total)}},
        venda.vendedor_id
    )
    
    return nova_venda

@router.get("/caixa/abrir")
async def abrir_caixa(
    valor_inicial: Decimal = Query(..., description="Valor inicial do caixa"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Abrir caixa do PDV
    Replica funcionalidade: Sistema PDV > Abrir Caixa
    """
    
    # Verificar se já existe caixa aberto
    caixa_aberto = db.query(Caixa).filter(
        and_(
            Caixa.usuario_id == current_user.id,
            Caixa.status == "ABERTO"
        )
    ).first()
    
    if caixa_aberto:
        raise HTTPException(status_code=400, detail="Já existe um caixa aberto")
    
    # Criar novo caixa
    novo_caixa = Caixa(
        usuario_id=current_user.id,
        valor_inicial=valor_inicial,
        valor_atual=valor_inicial,
        status="ABERTO",
        aberto_em=datetime.now()
    )
    
    db.add(novo_caixa)
    db.commit()
    db.refresh(novo_caixa)
    
    return {
        "id": novo_caixa.id,
        "status": "ABERTO",
        "valor_inicial": float(novo_caixa.valor_inicial),
        "aberto_em": novo_caixa.aberto_em.isoformat()
    }

@router.post("/caixa/fechar")
async def fechar_caixa(
    caixa_id: int,
    valor_final: Decimal,
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fechar caixa do PDV com fechamento detalhado
    Replica funcionalidade: Sistema PDV > Fechamento de Caixa
    """
    
    caixa = db.query(Caixa).filter(
        and_(
            Caixa.id == caixa_id,
            Caixa.usuario_id == current_user.id,
            Caixa.status == "ABERTO"
        )
    ).first()
    
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrado")
    
    # Calcular vendas do período
    vendas = db.query(Venda).filter(
        and_(
            Venda.vendedor_id == current_user.id,
            Venda.criado_em >= caixa.aberto_em
        )
    ).all()
    
    # Totais por forma de pagamento
    totais_pagamento = {}
    for venda in vendas:
        if venda.tipo_pagamento not in totais_pagamento:
            totais_pagamento[venda.tipo_pagamento] = Decimal(0)
        totais_pagamento[venda.tipo_pagamento] += venda.valor_total
    
    # Criar fechamento
    fechamento = FechamentoCaixa(
        caixa_id=caixa.id,
        valor_inicial=caixa.valor_inicial,
        valor_final=valor_final,
        valor_esperado=caixa.valor_inicial + sum(totais_pagamento.values()),
        diferenca=valor_final - (caixa.valor_inicial + sum(totais_pagamento.values())),
        total_vendas=len(vendas),
        vendas_dinheiro=totais_pagamento.get("DINHEIRO", Decimal(0)),
        vendas_cartao=totais_pagamento.get("CARTAO_CREDITO", Decimal(0)) + 
                      totais_pagamento.get("CARTAO_DEBITO", Decimal(0)),
        vendas_pix=totais_pagamento.get("PIX", Decimal(0)),
        vendas_cashless=totais_pagamento.get("CASHLESS", Decimal(0)),
        observacoes=observacoes
    )
    
    db.add(fechamento)
    
    # Fechar caixa
    caixa.status = "FECHADO"
    caixa.fechado_em = datetime.now()
    caixa.valor_final = valor_final
    
    db.commit()
    
    return {
        "id": fechamento.id,
        "valor_inicial": float(fechamento.valor_inicial),
        "valor_final": float(fechamento.valor_final),
        "valor_esperado": float(fechamento.valor_esperado),
        "diferenca": float(fechamento.diferenca),
        "total_vendas": fechamento.total_vendas,
        "totais_pagamento": {
            "dinheiro": float(fechamento.vendas_dinheiro),
            "cartao": float(fechamento.vendas_cartao),
            "pix": float(fechamento.vendas_pix),
            "cashless": float(fechamento.vendas_cashless)
        }
    }

@router.get("/produtos/search")
async def buscar_produtos(
    q: str = Query(..., description="Termo de busca"),
    categoria_id: Optional[int] = None,
    disponivel_pdv: bool = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar produtos para PDV com busca rápida
    Replica funcionalidade: Sistema PDV > Busca de Produtos
    """
    
    query = db.query(Produto)
    
    # Busca por nome ou código
    if q:
        query = query.filter(
            or_(
                Produto.nome.ilike(f"%{q}%"),
                Produto.codigo == q
            )
        )
    
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    
    if disponivel_pdv:
        query = query.filter(Produto.disponivel_pdv == True)
    
    if current_user.empresa_id:
        query = query.filter(Produto.empresa_id == current_user.empresa_id)
    
    produtos = query.limit(20).all()
    
    return [
        {
            "id": p.id,
            "codigo": p.codigo,
            "nome": p.nome,
            "preco": float(p.preco),
            "estoque_atual": float(p.estoque_atual),
            "imagem_url": p.imagem_url
        }
        for p in produtos
    ]

@router.post("/desconto/aplicar")
async def aplicar_desconto(
    venda_id: int,
    tipo_desconto: str = "PERCENTUAL",  # PERCENTUAL, VALOR_FIXO
    valor: Decimal = Query(...),
    motivo: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aplicar desconto em venda
    Replica funcionalidade: Sistema PDV > Descontos
    """
    
    venda = db.query(Venda).filter(Venda.id == venda_id).first()
    
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    if venda.status != "PENDENTE":
        raise HTTPException(status_code=400, detail="Venda já foi finalizada")
    
    # Calcular desconto
    if tipo_desconto == "PERCENTUAL":
        valor_desconto = venda.valor_total * (valor / 100)
    else:
        valor_desconto = valor
    
    # Verificar permissão para desconto
    limite_desconto = Decimal(50)  # 50% ou R$ 50
    if valor_desconto > limite_desconto:
        # Requer aprovação de supervisor
        raise HTTPException(status_code=403, detail="Desconto requer aprovação")
    
    # Aplicar desconto
    venda.desconto = valor_desconto
    venda.valor_total -= valor_desconto
    
    # Registrar desconto
    registro_desconto = Desconto(
        venda_id=venda_id,
        tipo=tipo_desconto,
        valor=valor,
        valor_desconto=valor_desconto,
        motivo=motivo,
        autorizado_por=current_user.id
    )
    
    db.add(registro_desconto)
    db.commit()
    
    return {
        "venda_id": venda_id,
        "valor_original": float(venda.valor_total + valor_desconto),
        "desconto": float(valor_desconto),
        "valor_final": float(venda.valor_total)
    }

@router.get("/relatorio/vendas")
async def relatorio_vendas(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    vendedor_id: Optional[int] = None,
    tipo_pagamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Relatório de vendas do PDV
    Replica funcionalidade: Sistema PDV > Relatórios
    """
    
    query = db.query(Venda).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    )
    
    if vendedor_id:
        query = query.filter(Venda.vendedor_id == vendedor_id)
    
    if tipo_pagamento:
        query = query.filter(Venda.tipo_pagamento == tipo_pagamento)
    
    vendas = query.all()
    
    # Estatísticas
    total_vendas = len(vendas)
    valor_total = sum(v.valor_total for v in vendas)
    ticket_medio = valor_total / total_vendas if total_vendas > 0 else Decimal(0)
    
    # Vendas por dia
    vendas_por_dia = {}
    for venda in vendas:
        dia = venda.criado_em.date()
        if dia not in vendas_por_dia:
            vendas_por_dia[dia] = {"quantidade": 0, "valor": Decimal(0)}
        vendas_por_dia[dia]["quantidade"] += 1
        vendas_por_dia[dia]["valor"] += venda.valor_total
    
    # Produtos mais vendidos
    produtos_vendidos = db.query(
        Produto.nome,
        func.sum(ItemVenda.quantidade).label("quantidade"),
        func.sum(ItemVenda.valor_total).label("valor")
    ).join(
        ItemVenda,
        ItemVenda.produto_id == Produto.id
    ).join(
        Venda,
        Venda.id == ItemVenda.venda_id
    ).filter(
        Venda.id.in_([v.id for v in vendas])
    ).group_by(
        Produto.id, Produto.nome
    ).order_by(
        desc("quantidade")
    ).limit(10).all()
    
    return {
        "periodo": {
            "inicio": data_inicio.isoformat(),
            "fim": data_fim.isoformat()
        },
        "resumo": {
            "total_vendas": total_vendas,
            "valor_total": float(valor_total),
            "ticket_medio": float(ticket_medio)
        },
        "vendas_por_dia": [
            {
                "data": dia.isoformat(),
                "quantidade": dados["quantidade"],
                "valor": float(dados["valor"])
            }
            for dia, dados in sorted(vendas_por_dia.items())
        ],
        "produtos_mais_vendidos": [
            {
                "produto": p.nome,
                "quantidade": float(p.quantidade),
                "valor": float(p.valor)
            }
            for p in produtos_vendidos
        ]
    }

@router.websocket("/ws/{caixa_id}")
async def websocket_pdv(
    websocket: WebSocket,
    caixa_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket para atualizações em tempo real do PDV
    """
    
    await manager.connect(websocket, caixa_id)
    
    try:
        while True:
            # Receber mensagens do cliente
            data = await websocket.receive_json()
            
            # Processar diferentes tipos de mensagem
            if data["tipo"] == "ping":
                await websocket.send_json({"tipo": "pong"})
            
            elif data["tipo"] == "atualizar_estoque":
                # Broadcast atualização de estoque
                await manager.broadcast_to_caixa(
                    {
                        "tipo": "estoque_atualizado",
                        "produto_id": data["produto_id"],
                        "novo_estoque": data["novo_estoque"]
                    },
                    caixa_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, caixa_id)

@router.post("/configuracao/salvar")
async def salvar_configuracao_pdv(
    permitir_venda_sem_estoque: bool = False,
    obrigar_cliente: bool = False,
    impressora_padrao: Optional[str] = None,
    taxa_servico_percentual: Optional[Decimal] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Salvar configurações do PDV
    """
    
    config = db.query(ConfiguracaoPDV).filter(
        ConfiguracaoPDV.empresa_id == current_user.empresa_id
    ).first()
    
    if not config:
        config = ConfiguracaoPDV(empresa_id=current_user.empresa_id)
        db.add(config)
    
    config.permitir_venda_sem_estoque = permitir_venda_sem_estoque
    config.obrigar_cliente = obrigar_cliente
    config.impressora_padrao = impressora_padrao
    config.taxa_servico_percentual = taxa_servico_percentual
    
    db.commit()
    
    return {"message": "Configurações salvas com sucesso"}
