"""
Router para Dashboard Financeiro Expandido
Implementa análises avançadas financeiras e operacionais
Baseado na análise da engenharia reversa do sistema MEEP
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, extract, case
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar

from ..database import get_db
from ..models import (
    VendaPDV, ItemVendaPDV, Produto, Usuario, Evento, Empresa,
    FormaPagamento, Categoria, TipoPagamentoPDV
)
from ..models_cashless import (
    CartaoCashless, RecargaCashless, MovimentacaoCashless,
    ConfiguracaoCashlessEvento
)
from ..utils.security import get_current_user

router = APIRouter(prefix="/api/v1/dashboard-financeiro", tags=["Dashboard Financeiro"])

# ================================================================================
# SCHEMAS PARA DASHBOARD FINANCEIRO
# ================================================================================

from pydantic import BaseModel, Field

class KPIResumo(BaseModel):
    vendas_totais: float
    ticket_medio: float
    quantidade_vendas: int
    produtos_vendidos: int
    crescimento_percentual: Optional[float] = None

class VendaPeriodo(BaseModel):
    periodo: str
    vendas_brutas: float
    vendas_liquidas: float
    quantidade_vendas: int
    ticket_medio: float
    crescimento: Optional[float] = None

class ProdutoPerformance(BaseModel):
    produto_id: int
    nome: str
    categoria: Optional[str]
    quantidade_vendida: int
    valor_total: float
    ticket_medio: float
    margem_percentual: Optional[float]
    ranking: int

class PDVPerformance(BaseModel):
    pdv_id: Optional[int]
    nome_operador: str
    vendas_totais: float
    quantidade_vendas: int
    ticket_medio: float
    ranking: int

class FormaPagamentoAnalise(BaseModel):
    forma_pagamento: str
    valor_total: float
    quantidade_transacoes: int
    percentual_total: float
    ticket_medio: float

class ClienteAnalise(BaseModel):
    total_clientes: int
    clientes_novos: int
    clientes_recorrentes: int
    taxa_retencao: float
    ticket_medio_novo: float
    ticket_medio_recorrente: float

# ================================================================================
# ENDPOINTS PRINCIPAIS
# ================================================================================

@router.get("/resumo", response_model=Dict[str, Any])
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
    
    # Construir query base
    query_base = db.query(VendaPDV).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if evento_id:
        query_base = query_base.filter(VendaPDV.evento_id == evento_id)
    if empresa_id:
        query_base = query_base.filter(VendaPDV.empresa_id == empresa_id)
    
    # Calcular KPIs principais
    vendas = query_base.all()
    
    vendas_totais = sum(float(v.valor_total or 0) for v in vendas)
    quantidade_vendas = len(vendas)
    ticket_medio = vendas_totais / quantidade_vendas if quantidade_vendas > 0 else 0
    
    # Produtos únicos vendidos
    produtos_vendidos = db.query(func.count(func.distinct(ItemVendaPDV.produto_id))).join(
        VendaPDV
    ).filter(
        VendaPDV.data_venda >= data_inicio,
        VendaPDV.data_venda <= data_fim,
        VendaPDV.status == "finalizada"
    ).scalar() or 0
    
    # Calcular crescimento comparado com período anterior
    periodo_anterior_inicio = data_inicio - (data_fim - data_inicio)
    periodo_anterior_fim = data_inicio - timedelta(days=1)
    
    vendas_periodo_anterior = db.query(func.sum(VendaPDV.valor_total)).filter(
        VendaPDV.data_venda >= periodo_anterior_inicio,
        VendaPDV.data_venda <= periodo_anterior_fim,
        VendaPDV.status == "finalizada"
    ).scalar() or 0
    
    crescimento_percentual = 0.0
    if vendas_periodo_anterior > 0:
        crescimento_percentual = ((vendas_totais - float(vendas_periodo_anterior)) / float(vendas_periodo_anterior)) * 100
    
    return {
        "periodo": {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        },
        "kpis": {
            "vendas_totais": vendas_totais,
            "ticket_medio": ticket_medio,
            "quantidade_vendas": quantidade_vendas,
            "produtos_vendidos": produtos_vendidos,
            "crescimento_percentual": crescimento_percentual
        },
        "comparacao_periodo_anterior": {
            "vendas_anteriores": float(vendas_periodo_anterior) if vendas_periodo_anterior else 0,
            "crescimento": crescimento_percentual
        }
    }

@router.get("/vendas-periodo", response_model=List[VendaPeriodo])
async def obter_vendas_por_periodo(
    granularidade: str = Query("dia", regex="^(dia|semana|mes)$"),
    filtros: FiltrosDashboard = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter vendas agrupadas por período"""
    
    if not filtros.data_inicio:
        filtros.data_inicio = date.today() - timedelta(days=30)
    if not filtros.data_fim:
        filtros.data_fim = date.today()
    
    # Definir agrupamento baseado na granularidade
    if granularidade == "dia":
        date_trunc = func.date(VendaPDV.data_venda)
        periodo_format = func.date_format(VendaPDV.data_venda, '%Y-%m-%d')
    elif granularidade == "semana":
        date_trunc = func.yearweek(VendaPDV.data_venda)
        periodo_format = func.concat(
            func.year(VendaPDV.data_venda), 
            ' - Semana ', 
            func.week(VendaPDV.data_venda)
        )
    else:  # mes
        date_trunc = func.date_format(VendaPDV.data_venda, '%Y-%m')
        periodo_format = func.date_format(VendaPDV.data_venda, '%Y-%m')
    
    # Query para vendas por período
    vendas_periodo = db.query(
        periodo_format.label('periodo'),
        func.sum(VendaPDV.valor_total).label('vendas_brutas'),
        func.sum(VendaPDV.valor_liquido).label('vendas_liquidas'),
        func.count(VendaPDV.id).label('quantidade_vendas'),
        func.avg(VendaPDV.valor_total).label('ticket_medio')
    ).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if filtros.evento_id:
        vendas_periodo = vendas_periodo.filter(VendaPDV.evento_id == filtros.evento_id)
    if filtros.empresa_id:
        vendas_periodo = vendas_periodo.filter(VendaPDV.empresa_id == filtros.empresa_id)
    
    vendas_periodo = vendas_periodo.group_by(date_trunc).order_by(date_trunc).all()
    
    resultado = []
    for i, venda in enumerate(vendas_periodo):
        crescimento = None
        if i > 0:
            anterior = vendas_periodo[i-1].vendas_brutas
            if anterior > 0:
                crescimento = ((venda.vendas_brutas - anterior) / anterior) * 100
        
        resultado.append(VendaPeriodo(
            periodo=venda.periodo,
            vendas_brutas=venda.vendas_brutas,
            vendas_liquidas=venda.vendas_liquidas or venda.vendas_brutas,
            quantidade_vendas=venda.quantidade_vendas,
            ticket_medio=venda.ticket_medio,
            crescimento=crescimento
        ))
    
    return resultado

@router.get("/produtos-performance", response_model=List[ProdutoPerformance])
async def obter_produtos_performance(
    limite: int = Query(default=20, le=100),
    ordenar_por: str = Query("valor_total", regex="^(valor_total|quantidade|ticket_medio)$"),
    filtros: FiltrosDashboard = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter performance dos produtos"""
    
    if not filtros.data_inicio:
        filtros.data_inicio = date.today() - timedelta(days=30)
    if not filtros.data_fim:
        filtros.data_fim = date.today()
    
    # Query para performance de produtos
    produtos_performance = db.query(
        Produto.id.label('produto_id'),
        Produto.nome.label('nome'),
        Categoria.nome.label('categoria'),
        func.sum(ItemVendaPDV.quantidade).label('quantidade_vendida'),
        func.sum(ItemVendaPDV.valor_total).label('valor_total'),
        func.avg(ItemVendaPDV.valor_unitario).label('ticket_medio'),
        func.avg(((ItemVendaPDV.valor_unitario - Produto.custo) / ItemVendaPDV.valor_unitario) * 100).label('margem_percentual')
    ).join(ItemVendaPDV).join(VendaPDV).outerjoin(Categoria).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if filtros.evento_id:
        produtos_performance = produtos_performance.filter(VendaPDV.evento_id == filtros.evento_id)
    if filtros.empresa_id:
        produtos_performance = produtos_performance.filter(VendaPDV.empresa_id == filtros.empresa_id)
    
    # Ordenação
    if ordenar_por == "quantidade":
        produtos_performance = produtos_performance.order_by(desc('quantidade_vendida'))
    elif ordenar_por == "ticket_medio":
        produtos_performance = produtos_performance.order_by(desc('ticket_medio'))
    else:  # valor_total
        produtos_performance = produtos_performance.order_by(desc('valor_total'))
    
    produtos_performance = produtos_performance.group_by(
        Produto.id, Produto.nome, Categoria.nome
    ).limit(limite).all()
    
    resultado = []
    for i, produto in enumerate(produtos_performance, 1):
        resultado.append(ProdutoPerformance(
            produto_id=produto.produto_id,
            nome=produto.nome,
            categoria=produto.categoria,
            quantidade_vendida=produto.quantidade_vendida,
            valor_total=produto.valor_total,
            ticket_medio=produto.ticket_medio,
            margem_percentual=produto.margem_percentual,
            ranking=i
        ))
    
    return resultado

@router.get("/formas-pagamento", response_model=List[FormaPagamentoAnalise])
async def obter_analise_formas_pagamento(
    filtros: FiltrosDashboard = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter análise das formas de pagamento"""
    
    if not filtros.data_inicio:
        filtros.data_inicio = date.today() - timedelta(days=30)
    if not filtros.data_fim:
        filtros.data_fim = date.today()
    
    # Query para formas de pagamento
    formas_pagamento = db.query(
        VendaPDV.tipo_pagamento.label('forma_pagamento'),
        func.sum(VendaPDV.valor_total).label('valor_total'),
        func.count(VendaPDV.id).label('quantidade_transacoes'),
        func.avg(VendaPDV.valor_total).label('ticket_medio')
    ).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if filtros.evento_id:
        formas_pagamento = formas_pagamento.filter(VendaPDV.evento_id == filtros.evento_id)
    if filtros.empresa_id:
        formas_pagamento = formas_pagamento.filter(VendaPDV.empresa_id == filtros.empresa_id)
    
    formas_pagamento = formas_pagamento.group_by(VendaPDV.tipo_pagamento).all()
    
    # Calcular total geral para percentuais
    total_geral = sum(fp.valor_total for fp in formas_pagamento)
    
    resultado = []
    for fp in formas_pagamento:
        percentual = (fp.valor_total / total_geral * 100) if total_geral > 0 else 0
        
        resultado.append(FormaPagamentoAnalise(
            forma_pagamento=fp.forma_pagamento or "Não informado",
            valor_total=fp.valor_total,
            quantidade_transacoes=fp.quantidade_transacoes,
            percentual_total=percentual,
            ticket_medio=fp.ticket_medio
        ))
    
    return sorted(resultado, key=lambda x: x.valor_total, reverse=True)

@router.get("/pdvs-performance", response_model=List[PDVPerformance])
async def obter_performance_pdvs(
    limite: int = Query(default=20, le=100),
    filtros: FiltrosDashboard = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter performance dos PDVs/Operadores"""
    
    if not filtros.data_inicio:
        filtros.data_inicio = date.today() - timedelta(days=30)
    if not filtros.data_fim:
        filtros.data_fim = date.today()
    
    # Query para performance de PDVs
    pdvs_performance = db.query(
        VendaPDV.pdv_id.label('pdv_id'),
        VendaPDV.operador_nome.label('nome_operador'),
        func.sum(VendaPDV.valor_total).label('vendas_totais'),
        func.count(VendaPDV.id).label('quantidade_vendas'),
        func.avg(VendaPDV.valor_total).label('ticket_medio')
    ).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada"
    )
    
    # Aplicar filtros
    if filtros.evento_id:
        pdvs_performance = pdvs_performance.filter(VendaPDV.evento_id == filtros.evento_id)
    if filtros.empresa_id:
        pdvs_performance = pdvs_performance.filter(VendaPDV.empresa_id == filtros.empresa_id)
    if filtros.pdv_ids:
        pdvs_performance = pdvs_performance.filter(VendaPDV.pdv_id.in_(filtros.pdv_ids))
    
    pdvs_performance = pdvs_performance.group_by(
        VendaPDV.pdv_id, VendaPDV.operador_nome
    ).order_by(desc('vendas_totais')).limit(limite).all()
    
    resultado = []
    for i, pdv in enumerate(pdvs_performance, 1):
        resultado.append(PDVPerformance(
            pdv_id=pdv.pdv_id,
            nome_operador=pdv.nome_operador or "Operador não informado",
            vendas_totais=pdv.vendas_totais,
            quantidade_vendas=pdv.quantidade_vendas,
            ticket_medio=pdv.ticket_medio,
            ranking=i
        ))
    
    return resultado

@router.get("/clientes-analise", response_model=ClienteAnalise)
async def obter_analise_clientes(
    filtros: FiltrosDashboard = Depends(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter análise de comportamento de clientes"""
    
    if not filtros.data_inicio:
        filtros.data_inicio = date.today() - timedelta(days=30)
    if not filtros.data_fim:
        filtros.data_fim = date.today()
    
    # Clientes únicos no período
    clientes_periodo = db.query(func.count(func.distinct(VendaPDV.cliente_cpf))).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada",
        VendaPDV.cliente_cpf.isnot(None)
    )
    
    if filtros.evento_id:
        clientes_periodo = clientes_periodo.filter(VendaPDV.evento_id == filtros.evento_id)
    
    total_clientes = clientes_periodo.scalar() or 0
    
    # Clientes novos (primeira compra no período)
    periodo_anterior = filtros.data_inicio - timedelta(days=365)
    
    clientes_anteriores = db.query(func.distinct(VendaPDV.cliente_cpf)).filter(
        VendaPDV.data_venda >= periodo_anterior,
        VendaPDV.data_venda < filtros.data_inicio,
        VendaPDV.status == "finalizada",
        VendaPDV.cliente_cpf.isnot(None)
    ).subquery()
    
    clientes_novos = db.query(func.count(func.distinct(VendaPDV.cliente_cpf))).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada",
        VendaPDV.cliente_cpf.isnot(None),
        ~VendaPDV.cliente_cpf.in_(db.query(clientes_anteriores.c.cliente_cpf))
    ).scalar() or 0
    
    clientes_recorrentes = total_clientes - clientes_novos
    taxa_retencao = (clientes_recorrentes / total_clientes * 100) if total_clientes > 0 else 0
    
    # Ticket médio por tipo de cliente
    ticket_novos = db.query(func.avg(VendaPDV.valor_total)).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada",
        VendaPDV.cliente_cpf.isnot(None),
        ~VendaPDV.cliente_cpf.in_(db.query(clientes_anteriores.c.cliente_cpf))
    ).scalar() or 0
    
    ticket_recorrentes = db.query(func.avg(VendaPDV.valor_total)).filter(
        VendaPDV.data_venda >= filtros.data_inicio,
        VendaPDV.data_venda <= filtros.data_fim,
        VendaPDV.status == "finalizada",
        VendaPDV.cliente_cpf.isnot(None),
        VendaPDV.cliente_cpf.in_(db.query(clientes_anteriores.c.cliente_cpf))
    ).scalar() or 0
    
    return ClienteAnalise(
        total_clientes=total_clientes,
        clientes_novos=clientes_novos,
        clientes_recorrentes=clientes_recorrentes,
        taxa_retencao=taxa_retencao,
        ticket_medio_novo=ticket_novos,
        ticket_medio_recorrente=ticket_recorrentes
    )

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
    query_hoje = db.query(VendaPDV).filter(
        VendaPDV.data_venda >= inicio_dia.date(),
        VendaPDV.status == "finalizada"
    )
    
    if evento_id:
        query_hoje = query_hoje.filter(VendaPDV.evento_id == evento_id)
    
    vendas_hoje = query_hoje.all()
    
    # Vendas por hora
    vendas_por_hora = {}
    for venda in vendas_hoje:
        hora = venda.criado_em.hour if venda.criado_em else 0
        if hora not in vendas_por_hora:
            vendas_por_hora[hora] = {"vendas": 0, "valor": Decimal('0')}
        vendas_por_hora[hora]["vendas"] += 1
        vendas_por_hora[hora]["valor"] += venda.valor_total
    
    # Cartões cashless ativos
    cartoes_ativos = 0
    if evento_id:
        cartoes_ativos = db.query(CartaoCashless).filter(
            CartaoCashless.evento_id == evento_id,
            CartaoCashless.status == "ativo"
        ).count()
    
    return {
        "vendas_hoje": {
            "total_vendas": len(vendas_hoje),
            "valor_total": sum(v.valor_total for v in vendas_hoje),
            "ticket_medio": sum(v.valor_total for v in vendas_hoje) / len(vendas_hoje) if vendas_hoje else 0
        },
        "vendas_por_hora": [
            {
                "hora": f"{hora:02d}:00",
                "vendas": dados["vendas"],
                "valor": float(dados["valor"])
            }
            for hora, dados in sorted(vendas_por_hora.items())
        ],
        "sistema_cashless": {
            "cartoes_ativos": cartoes_ativos,
            "saldo_total_sistema": db.query(func.sum(CartaoCashless.saldo_atual)).filter(
                CartaoCashless.evento_id == evento_id if evento_id else True
            ).scalar() or 0
        },
        "ultima_atualizacao": agora
    }
