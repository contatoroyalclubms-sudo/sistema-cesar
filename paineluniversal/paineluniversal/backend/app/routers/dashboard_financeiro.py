"""
Router para Dashboard Financeiro Expandido
Implementa análises avançadas financeiras e operacionais
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from ..database import get_db
from ..models import VendaPDV, ItemVendaPDV, Produto, Usuario, Categoria
from ..models_cashless import CartaoCashless
from ..utils.security import get_current_user

router = APIRouter(prefix="/api/v1/dashboard-financeiro", tags=["Dashboard Financeiro"])

@router.get("/resumo")
async def obter_resumo_dashboard(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    evento_id: Optional[int] = Query(None),
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter resumo executivo do dashboard financeiro"""
    
    # Definir período padrão se não fornecido
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    # Query base para vendas
    query_base = db.query(VendaPDV).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros opcionais
    if evento_id:
        query_base = query_base.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        query_base = query_base.filter(VendaPDV.empresa_id == empresa_id)
    
    # Calcular métricas usando agregações SQL
    vendas_stats = db.query(
        func.count(VendaPDV.id).label('quantidade_vendas'),
        func.sum(VendaPDV.valor_total).label('vendas_totais'),
        func.avg(VendaPDV.valor_total).label('ticket_medio')
    ).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    )
    
    if evento_id:
        vendas_stats = vendas_stats.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        vendas_stats = vendas_stats.filter(VendaPDV.empresa_id == empresa_id)
    
    stats = vendas_stats.first()
    
    # Produtos únicos vendidos
    produtos_vendidos = db.query(func.count(func.distinct(ItemVendaPDV.produto_id))).join(
        VendaPDV
    ).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    )
    
    if evento_id:
        produtos_vendidos = produtos_vendidos.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        produtos_vendidos = produtos_vendidos.filter(VendaPDV.empresa_id == empresa_id)
    
    produtos_count = produtos_vendidos.scalar() or 0
    
    # Calcular crescimento comparado com período anterior
    periodo_anterior_inicio = data_inicio - (data_fim - data_inicio)
    periodo_anterior_fim = data_inicio - timedelta(days=1)
    
    vendas_anteriores = db.query(func.sum(VendaPDV.valor_total)).filter(
        VendaPDV.data_venda >= periodo_anterior_inicio,
        VendaPDV.data_venda <= periodo_anterior_fim,
        VendaPDV.status == "finalizada"
    )
    
    if evento_id:
        vendas_anteriores = vendas_anteriores.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        vendas_anteriores = vendas_anteriores.filter(VendaPDV.empresa_id == empresa_id)
    
    valor_anterior = vendas_anteriores.scalar() or Decimal('0')
    
    # Calcular percentual de crescimento
    crescimento_percentual = 0.0
    if valor_anterior and stats.vendas_totais:
        crescimento_percentual = float(((stats.vendas_totais - valor_anterior) / valor_anterior) * 100)
    
    return {
        "periodo": {
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat()
        },
        "kpis": {
            "vendas_totais": float(stats.vendas_totais or 0),
            "ticket_medio": float(stats.ticket_medio or 0),
            "quantidade_vendas": stats.quantidade_vendas or 0,
            "produtos_vendidos": produtos_count,
            "crescimento_percentual": crescimento_percentual
        },
        "comparacao_periodo_anterior": {
            "vendas_anteriores": float(valor_anterior),
            "crescimento": crescimento_percentual
        }
    }

@router.get("/vendas-periodo")
async def obter_vendas_por_periodo(
    granularidade: str = Query("dia", regex="^(dia|semana|mes)$"),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    evento_id: Optional[int] = Query(None),
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter vendas agrupadas por período"""
    
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    # Definir agrupamento baseado na granularidade
    if granularidade == "dia":
        date_trunc = func.date(VendaPDV.data_venda)
        periodo_format = func.date_format(VendaPDV.data_venda, '%Y-%m-%d')
    elif granularidade == "semana":
        date_trunc = func.yearweek(VendaPDV.data_venda)
        periodo_format = func.concat('Semana ', func.week(VendaPDV.data_venda), '/', func.year(VendaPDV.data_venda))
    else:  # mes
        date_trunc = func.date_format(VendaPDV.data_venda, '%Y-%m')
        periodo_format = func.date_format(VendaPDV.data_venda, '%Y-%m')
    
    # Query para vendas por período
    query = db.query(
        periodo_format.label('periodo'),
        func.sum(VendaPDV.valor_total).label('vendas_brutas'),
        func.sum(VendaPDV.valor_liquido).label('vendas_liquidas'),
        func.count(VendaPDV.id).label('quantidade_vendas'),
        func.avg(VendaPDV.valor_total).label('ticket_medio')
    ).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        query = query.filter(VendaPDV.empresa_id == empresa_id)
    
    vendas_periodo = query.group_by(date_trunc).order_by(date_trunc).all()
    
    resultado = []
    for i, venda in enumerate(vendas_periodo):
        crescimento = None
        if i > 0:
            anterior = float(vendas_periodo[i-1].vendas_brutas or 0)
            atual = float(venda.vendas_brutas or 0)
            if anterior > 0:
                crescimento = ((atual - anterior) / anterior) * 100
        
        resultado.append({
            "periodo": venda.periodo,
            "vendas_brutas": float(venda.vendas_brutas or 0),
            "vendas_liquidas": float(venda.vendas_liquidas or venda.vendas_brutas or 0),
            "quantidade_vendas": venda.quantidade_vendas or 0,
            "ticket_medio": float(venda.ticket_medio or 0),
            "crescimento": crescimento
        })
    
    return resultado

@router.get("/produtos-performance")
async def obter_produtos_performance(
    limite: int = Query(default=20, le=100),
    ordenar_por: str = Query("valor_total", regex="^(valor_total|quantidade|ticket_medio)$"),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    evento_id: Optional[int] = Query(None),
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter performance dos produtos"""
    
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    # Query para performance de produtos
    query = db.query(
        Produto.id.label('produto_id'),
        Produto.nome.label('nome'),
        Categoria.nome.label('categoria'),
        func.sum(ItemVendaPDV.quantidade).label('quantidade_vendida'),
        func.sum(ItemVendaPDV.valor_total).label('valor_total'),
        func.avg(ItemVendaPDV.valor_unitario).label('ticket_medio'),
        func.avg(((ItemVendaPDV.valor_unitario - func.coalesce(Produto.custo, 0)) / ItemVendaPDV.valor_unitario) * 100).label('margem_percentual')
    ).join(ItemVendaPDV).join(VendaPDV).outerjoin(Categoria, Produto.categoria_id == Categoria.id).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        query = query.filter(VendaPDV.empresa_id == empresa_id)
    
    # Ordenação
    if ordenar_por == "quantidade":
        query = query.order_by(desc('quantidade_vendida'))
    elif ordenar_por == "ticket_medio":
        query = query.order_by(desc('ticket_medio'))
    else:  # valor_total
        query = query.order_by(desc('valor_total'))
    
    produtos = query.group_by(Produto.id, Produto.nome, Categoria.nome).limit(limite).all()
    
    resultado = []
    for i, produto in enumerate(produtos, 1):
        resultado.append({
            "produto_id": produto.produto_id,
            "nome": produto.nome,
            "categoria": produto.categoria,
            "quantidade_vendida": produto.quantidade_vendida or 0,
            "valor_total": float(produto.valor_total or 0),
            "ticket_medio": float(produto.ticket_medio or 0),
            "margem_percentual": float(produto.margem_percentual or 0),
            "ranking": i
        })
    
    return resultado

@router.get("/formas-pagamento")
async def obter_analise_formas_pagamento(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    evento_id: Optional[int] = Query(None),
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter análise das formas de pagamento"""
    
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    # Query para formas de pagamento
    query = db.query(
        VendaPDV.tipo_pagamento.label('forma_pagamento'),
        func.sum(VendaPDV.valor_total).label('valor_total'),
        func.count(VendaPDV.id).label('quantidade_transacoes'),
        func.avg(VendaPDV.valor_total).label('ticket_medio')
    ).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        query = query.filter(VendaPDV.empresa_id == empresa_id)
    
    formas = query.group_by(VendaPDV.tipo_pagamento).all()
    
    # Calcular total geral para percentuais
    total_geral = sum(float(fp.valor_total or 0) for fp in formas)
    
    resultado = []
    for fp in formas:
        valor = float(fp.valor_total or 0)
        percentual = (valor / total_geral * 100) if total_geral > 0 else 0.0
        
        resultado.append({
            "forma_pagamento": fp.forma_pagamento or "Não informado",
            "valor_total": valor,
            "quantidade_transacoes": fp.quantidade_transacoes or 0,
            "percentual_total": percentual,
            "ticket_medio": float(fp.ticket_medio or 0)
        })
    
    return sorted(resultado, key=lambda x: x["valor_total"], reverse=True)

@router.get("/metricas-tempo-real")
async def obter_metricas_tempo_real(
    evento_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter métricas em tempo real (últimas 24 horas)"""
    
    agora = datetime.now()
    inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Vendas do dia atual
    query_hoje = db.query(
        func.count(VendaPDV.id).label('total_vendas'),
        func.sum(VendaPDV.valor_total).label('valor_total'),
        func.avg(VendaPDV.valor_total).label('ticket_medio')
    ).filter(
        VendaPDV.data_venda >= inicio_dia.date(),
        VendaPDV.status == "finalizada"
    )
    
    if evento_id:
        query_hoje = query_hoje.filter(VendaPDV.evento_id == evento_id)
    
    vendas_hoje = query_hoje.first()
    
    # Vendas por hora (últimas 24 horas)
    vendas_por_hora = db.query(
        func.hour(VendaPDV.criado_em).label('hora'),
        func.count(VendaPDV.id).label('vendas'),
        func.sum(VendaPDV.valor_total).label('valor')
    ).filter(
        VendaPDV.criado_em >= agora - timedelta(hours=24),
        VendaPDV.status == "finalizada"
    )
    
    if evento_id:
        vendas_por_hora = vendas_por_hora.filter(VendaPDV.evento_id == evento_id)
    
    vendas_hora = vendas_por_hora.group_by(func.hour(VendaPDV.criado_em)).all()
    
    # Cartões cashless ativos
    cartoes_ativos = 0
    saldo_total_sistema = 0.0
    
    if evento_id:
        cartoes_stats = db.query(
            func.count(CartaoCashless.id).label('ativos'),
            func.sum(CartaoCashless.saldo_atual).label('saldo_total')
        ).filter(
            CartaoCashless.evento_id == evento_id,
            CartaoCashless.status == "ativo"
        ).first()
        
        cartoes_ativos = cartoes_stats.ativos or 0
        saldo_total_sistema = float(cartoes_stats.saldo_total or 0)
    
    return {
        "vendas_hoje": {
            "total_vendas": vendas_hoje.total_vendas or 0,
            "valor_total": float(vendas_hoje.valor_total or 0),
            "ticket_medio": float(vendas_hoje.ticket_medio or 0)
        },
        "vendas_por_hora": [
            {
                "hora": f"{vh.hora:02d}:00",
                "vendas": vh.vendas or 0,
                "valor": float(vh.valor or 0)
            }
            for vh in vendas_hora
        ],
        "sistema_cashless": {
            "cartoes_ativos": cartoes_ativos,
            "saldo_total_sistema": saldo_total_sistema
        },
        "ultima_atualizacao": agora.isoformat()
    }
