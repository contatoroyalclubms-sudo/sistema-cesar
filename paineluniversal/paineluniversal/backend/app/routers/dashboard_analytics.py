"""
Router para Dashboard e Analytics - Funcionalidades completas do MEEP
Dashboard Geral, Dashboard de Clientes, Métricas e KPIs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario, Cliente, Checkin, Evento
from ..models_meep_complete import Venda, Produto, ItemVenda, Comanda, Pedido, TransacaoCashless
from ..schemas_meep_complete import DashboardStats, DashboardFinanceiro

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard & Analytics"]
)

@router.get("/general", response_model=DashboardStats)
async def get_dashboard_geral(
    periodo_dias: int = Query(30, description="Período em dias para análise"),
    caixa_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard Geral com métricas financeiras e operacionais
    Replica funcionalidade: MEEP Dashboard > Geral
    """
    
    # Calcular datas
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=periodo_dias)
    data_hoje = date.today()
    inicio_mes = date(data_hoje.year, data_hoje.month, 1)
    
    # Filtros base
    filtros_vendas = [
        Venda.criado_em >= data_inicio,
        Venda.status == "CONCLUIDA"
    ]
    
    if caixa_id:
        filtros_vendas.append(Venda.vendedor_id == caixa_id)
    
    if current_user.empresa_id:
        filtros_vendas.append(Venda.evento_id.in_(
            db.query(Evento.id).filter(Evento.empresa_id == current_user.empresa_id)
        ))
    
    # Vendas hoje
    vendas_hoje = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) == data_hoje,
            *filtros_vendas
        )
    ).scalar() or Decimal(0)
    
    # Vendas mês
    vendas_mes = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            Venda.criado_em >= inicio_mes,
            *filtros_vendas
        )
    ).scalar() or Decimal(0)
    
    # Clientes novos no mês
    clientes_novos_mes = db.query(func.count(Cliente.id)).filter(
        and_(
            Cliente.criado_em >= inicio_mes,
            Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
        )
    ).scalar() or 0
    
    # Produtos mais vendidos
    produtos_vendidos = db.query(
        Produto.nome,
        Produto.id,
        func.sum(ItemVenda.quantidade).label("quantidade_total"),
        func.sum(ItemVenda.valor_total).label("valor_total")
    ).join(
        ItemVenda, ItemVenda.produto_id == Produto.id
    ).join(
        Venda, Venda.id == ItemVenda.venda_id
    ).filter(
        *filtros_vendas
    ).group_by(
        Produto.id, Produto.nome
    ).order_by(
        desc("quantidade_total")
    ).limit(10).all()
    
    produtos_mais_vendidos = [
        {
            "id": p.id,
            "nome": p.nome,
            "quantidade": float(p.quantidade_total),
            "valor_total": float(p.valor_total)
        }
        for p in produtos_vendidos
    ]
    
    # Horários de pico
    vendas_por_hora = db.query(
        func.extract('hour', Venda.criado_em).label("hora"),
        func.count(Venda.id).label("quantidade"),
        func.sum(Venda.valor_total).label("valor")
    ).filter(
        *filtros_vendas
    ).group_by(
        "hora"
    ).order_by(
        desc("quantidade")
    ).all()
    
    horarios_pico = [
        {
            "hora": int(h.hora),
            "quantidade": h.quantidade,
            "valor": float(h.valor)
        }
        for h in vendas_por_hora
    ]
    
    # Taxa de ocupação (comandas abertas vs capacidade)
    comandas_abertas = db.query(func.count(Comanda.id)).filter(
        Comanda.status == "ABERTA"
    ).scalar() or 0
    
    capacidade_total = 100  # Configurável por empresa
    taxa_ocupacao = (comandas_abertas / capacidade_total * 100) if capacidade_total > 0 else 0
    
    # Ticket médio
    total_vendas = db.query(func.count(Venda.id)).filter(*filtros_vendas).scalar() or 1
    valor_total = db.query(func.sum(Venda.valor_total)).filter(*filtros_vendas).scalar() or Decimal(0)
    ticket_medio = valor_total / total_vendas if total_vendas > 0 else Decimal(0)
    
    return DashboardStats(
        vendas_hoje=vendas_hoje,
        vendas_mes=vendas_mes,
        clientes_novos_mes=clientes_novos_mes,
        produtos_mais_vendidos=produtos_mais_vendidos,
        horarios_pico=horarios_pico,
        taxa_ocupacao=taxa_ocupacao,
        ticket_medio=ticket_medio
    )

@router.get("/customer", response_model=Dict[str, Any])
async def get_dashboard_clientes(
    periodo_dias: int = Query(30, description="Período em dias para análise"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard Analytics de Clientes
    Replica funcionalidade: MEEP Dashboard > Clientes
    """
    
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=periodo_dias)
    
    # Total de clientes
    total_clientes = db.query(func.count(Cliente.id)).filter(
        Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
    ).scalar() or 0
    
    # Novos clientes no período
    novos_clientes = db.query(func.count(Cliente.id)).filter(
        and_(
            Cliente.criado_em >= data_inicio,
            Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
        )
    ).scalar() or 0
    
    # Clientes por categoria
    clientes_categoria = db.query(
        func.coalesce(Cliente.categoria_id, 0).label("categoria"),
        func.count(Cliente.id).label("quantidade")
    ).filter(
        Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
    ).group_by("categoria").all()
    
    # Clientes ativos (com compras no período)
    clientes_ativos = db.query(func.count(func.distinct(Venda.cliente_cpf))).filter(
        Venda.criado_em >= data_inicio
    ).scalar() or 0
    
    # Taxa de retenção
    taxa_retencao = (clientes_ativos / total_clientes * 100) if total_clientes > 0 else 0
    
    # Análise de fidelidade
    fidelidade_stats = db.query(
        Cliente.nivel_fidelidade,
        func.count(Cliente.id).label("quantidade")
    ).filter(
        Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
    ).group_by(Cliente.nivel_fidelidade).all()
    
    # Top clientes por gasto
    top_clientes = db.query(
        Cliente.nome,
        Cliente.cpf,
        func.sum(Venda.valor_total).label("total_gasto")
    ).join(
        Venda, Venda.cliente_cpf == Cliente.cpf
    ).filter(
        and_(
            Venda.criado_em >= data_inicio,
            Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
        )
    ).group_by(
        Cliente.id, Cliente.nome, Cliente.cpf
    ).order_by(
        desc("total_gasto")
    ).limit(10).all()
    
    return {
        "total_clientes": total_clientes,
        "novos_clientes": novos_clientes,
        "clientes_ativos": clientes_ativos,
        "taxa_retencao": taxa_retencao,
        "clientes_por_categoria": [
            {"categoria_id": c.categoria, "quantidade": c.quantidade}
            for c in clientes_categoria
        ],
        "fidelidade_distribuicao": [
            {"nivel": f.nivel_fidelidade, "quantidade": f.quantidade}
            for f in fidelidade_stats
        ],
        "top_clientes": [
            {
                "nome": t.nome,
                "cpf": t.cpf,
                "total_gasto": float(t.total_gasto)
            }
            for t in top_clientes
        ]
    }

@router.get("/financial", response_model=DashboardFinanceiro)
async def get_dashboard_financeiro(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard Financeiro com análise de formas de pagamento
    Replica funcionalidade: MEEP Dashboard financeiro
    """
    
    if not data_inicio:
        data_inicio = date.today()
    if not data_fim:
        data_fim = date.today()
    
    # Filtros base
    filtros = [
        func.date(Venda.criado_em) >= data_inicio,
        func.date(Venda.criado_em) <= data_fim,
        Venda.status == "CONCLUIDA"
    ]
    
    # Receita total
    receita_total = db.query(func.sum(Venda.valor_total)).filter(*filtros).scalar() or Decimal(0)
    
    # Receita por forma de pagamento
    receitas_pagamento = db.query(
        Venda.tipo_pagamento,
        func.sum(Venda.valor_total).label("total")
    ).filter(*filtros).group_by(Venda.tipo_pagamento).all()
    
    receita_dinheiro = Decimal(0)
    receita_cartao = Decimal(0)
    receita_pix = Decimal(0)
    receita_cashless = Decimal(0)
    
    for r in receitas_pagamento:
        if r.tipo_pagamento == "DINHEIRO":
            receita_dinheiro = r.total
        elif r.tipo_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"]:
            receita_cartao += r.total
        elif r.tipo_pagamento == "PIX":
            receita_pix = r.total
        elif r.tipo_pagamento == "CASHLESS":
            receita_cashless = r.total
    
    # Comandas
    comandas_abertas = db.query(func.count(Comanda.id)).filter(
        Comanda.status == "ABERTA"
    ).scalar() or 0
    
    comandas_fechadas = db.query(func.count(Comanda.id)).filter(
        and_(
            Comanda.status == "FECHADA",
            func.date(Comanda.fechada_em) >= data_inicio,
            func.date(Comanda.fechada_em) <= data_fim
        )
    ).scalar() or 0
    
    valor_comandas_abertas = db.query(func.sum(Comanda.valor_total)).filter(
        Comanda.status == "ABERTA"
    ).scalar() or Decimal(0)
    
    return DashboardFinanceiro(
        receita_total=receita_total,
        receita_dinheiro=receita_dinheiro,
        receita_cartao=receita_cartao,
        receita_pix=receita_pix,
        receita_cashless=receita_cashless,
        comandas_abertas=comandas_abertas,
        comandas_fechadas=comandas_fechadas,
        valor_comandas_abertas=valor_comandas_abertas
    )

@router.get("/realtime-stats")
async def get_realtime_stats(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Estatísticas em tempo real para atualização do dashboard
    """
    
    agora = datetime.now()
    hoje = date.today()
    ultima_hora = agora - timedelta(hours=1)
    
    # Vendas última hora
    vendas_ultima_hora = db.query(func.count(Venda.id)).filter(
        Venda.criado_em >= ultima_hora
    ).scalar() or 0
    
    # Check-ins última hora
    checkins_ultima_hora = db.query(func.count(Checkin.id)).filter(
        Checkin.horario_entrada >= ultima_hora
    ).scalar() or 0
    
    # Comandas abertas agora
    comandas_abertas_agora = db.query(func.count(Comanda.id)).filter(
        Comanda.status == "ABERTA"
    ).scalar() or 0
    
    # Pedidos pendentes
    pedidos_pendentes = db.query(func.count(Pedido.id)).filter(
        Pedido.status == "PENDENTE"
    ).scalar() or 0
    
    # Transações cashless hoje
    transacoes_cashless_hoje = db.query(func.count(TransacaoCashless.id)).filter(
        func.date(TransacaoCashless.criado_em) == hoje
    ).scalar() or 0
    
    return {
        "timestamp": agora.isoformat(),
        "vendas_ultima_hora": vendas_ultima_hora,
        "checkins_ultima_hora": checkins_ultima_hora,
        "comandas_abertas": comandas_abertas_agora,
        "pedidos_pendentes": pedidos_pendentes,
        "transacoes_cashless_hoje": transacoes_cashless_hoje
    }

@router.get("/kpis")
async def get_kpis(
    periodo: str = Query("mes", description="dia, semana, mes, ano"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    KPIs principais do negócio
    """
    
    # Determinar período
    hoje = date.today()
    if periodo == "dia":
        data_inicio = hoje
    elif periodo == "semana":
        data_inicio = hoje - timedelta(days=7)
    elif periodo == "mes":
        data_inicio = hoje - timedelta(days=30)
    else:  # ano
        data_inicio = hoje - timedelta(days=365)
    
    # Calcular KPIs
    filtros = [
        func.date(Venda.criado_em) >= data_inicio,
        Venda.status == "CONCLUIDA"
    ]
    
    # Faturamento
    faturamento = db.query(func.sum(Venda.valor_total)).filter(*filtros).scalar() or Decimal(0)
    
    # Quantidade de vendas
    qtd_vendas = db.query(func.count(Venda.id)).filter(*filtros).scalar() or 0
    
    # Ticket médio
    ticket_medio = faturamento / qtd_vendas if qtd_vendas > 0 else Decimal(0)
    
    # Taxa de conversão (checkins que viraram vendas)
    total_checkins = db.query(func.count(Checkin.id)).filter(
        func.date(Checkin.horario_entrada) >= data_inicio
    ).scalar() or 0
    
    clientes_compraram = db.query(func.count(func.distinct(Venda.cliente_cpf))).filter(
        *filtros
    ).scalar() or 0
    
    taxa_conversao = (clientes_compraram / total_checkins * 100) if total_checkins > 0 else 0
    
    # Crescimento
    if periodo == "dia":
        data_inicio_anterior = hoje - timedelta(days=1)
        data_fim_anterior = hoje - timedelta(days=1)
    elif periodo == "semana":
        data_inicio_anterior = hoje - timedelta(days=14)
        data_fim_anterior = hoje - timedelta(days=7)
    elif periodo == "mes":
        data_inicio_anterior = hoje - timedelta(days=60)
        data_fim_anterior = hoje - timedelta(days=30)
    else:
        data_inicio_anterior = hoje - timedelta(days=730)
        data_fim_anterior = hoje - timedelta(days=365)
    
    faturamento_anterior = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio_anterior,
            func.date(Venda.criado_em) < data_fim_anterior,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or Decimal(1)
    
    crescimento = ((faturamento - faturamento_anterior) / faturamento_anterior * 100) if faturamento_anterior > 0 else 0
    
    return {
        "periodo": periodo,
        "faturamento": float(faturamento),
        "quantidade_vendas": qtd_vendas,
        "ticket_medio": float(ticket_medio),
        "taxa_conversao": taxa_conversao,
        "crescimento_percentual": float(crescimento),
        "total_checkins": total_checkins,
        "clientes_compraram": clientes_compraram
    }