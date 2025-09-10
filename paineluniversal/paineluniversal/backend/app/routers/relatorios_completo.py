"""
Router para Relatórios Completos - Sistema de BI e Analytics
Relatórios financeiros, operacionais, de clientes e eventos
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import pandas as pd
import io
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Usuario, Venda, ItemVenda, Produto, Cliente, Evento,
    Checkin, Comanda, Pedido, TransacaoCashless, MovimentacaoEstoque,
    Empresa, Colaborador, Caixa, FechamentoCaixa
)
from ..schemas_meep_complete import (
    FiltroRelatorio, RelatorioResponse
)

router = APIRouter(
    prefix="/api/relatorios",
    tags=["Relatórios e BI"]
)

@router.post("/vendas", response_model=RelatorioResponse)
async def relatorio_vendas(
    filtros: FiltroRelatorio,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Relatório completo de vendas
    Replica funcionalidade: Sistema Relatórios > Vendas
    """
    
    # Query base
    query = db.query(Venda).filter(
        and_(
            func.date(Venda.criado_em) >= filtros.data_inicio,
            func.date(Venda.criado_em) <= filtros.data_fim,
            Venda.status == "CONCLUIDA"
        )
    )
    
    # Aplicar filtros
    if filtros.empresa_id:
        query = query.join(Evento).filter(Evento.empresa_id == filtros.empresa_id)
    
    if filtros.evento_id:
        query = query.filter(Venda.evento_id == filtros.evento_id)
    
    if filtros.caixa_id:
        query = query.filter(Venda.vendedor_id == filtros.caixa_id)
    
    if filtros.tipo_pagamento:
        query = query.filter(Venda.tipo_pagamento == filtros.tipo_pagamento)
    
    vendas = query.all()
    
    # Calcular estatísticas
    total_vendas = len(vendas)
    valor_total = sum(v.valor_total for v in vendas)
    ticket_medio = valor_total / total_vendas if total_vendas > 0 else Decimal(0)
    
    # Produtos vendidos
    produtos_vendidos = db.query(
        Produto.nome,
        func.sum(ItemVenda.quantidade).label("quantidade"),
        func.sum(ItemVenda.valor_total).label("valor")
    ).join(
        ItemVenda,
        ItemVenda.produto_id == Produto.id
    ).filter(
        ItemVenda.venda_id.in_([v.id for v in vendas])
    ).group_by(
        Produto.id, Produto.nome
    ).order_by(
        desc("valor")
    ).all()
    
    # Formas de pagamento
    formas_pagamento = {}
    for venda in vendas:
        if venda.tipo_pagamento not in formas_pagamento:
            formas_pagamento[venda.tipo_pagamento] = Decimal(0)
        formas_pagamento[venda.tipo_pagamento] += venda.valor_total
    
    # Vendas por dia
    vendas_por_dia = {}
    for venda in vendas:
        dia = venda.criado_em.date()
        if dia not in vendas_por_dia:
            vendas_por_dia[dia] = {"quantidade": 0, "valor": Decimal(0)}
        vendas_por_dia[dia]["quantidade"] += 1
        vendas_por_dia[dia]["valor"] += venda.valor_total
    
    # Vendas por hora
    vendas_por_hora = {}
    for venda in vendas:
        hora = venda.criado_em.hour
        if hora not in vendas_por_hora:
            vendas_por_hora[hora] = {"quantidade": 0, "valor": Decimal(0)}
        vendas_por_hora[hora]["quantidade"] += 1
        vendas_por_hora[hora]["valor"] += venda.valor_total
    
    return RelatorioResponse(
        total_vendas=total_vendas,
        valor_total=valor_total,
        ticket_medio=ticket_medio,
        produtos_vendidos=[
            {
                "produto": p.nome,
                "quantidade": float(p.quantidade),
                "valor": float(p.valor)
            }
            for p in produtos_vendidos
        ],
        formas_pagamento={
            k: float(v) for k, v in formas_pagamento.items()
        },
        vendas_por_dia=[
            {
                "data": dia.isoformat(),
                "quantidade": dados["quantidade"],
                "valor": float(dados["valor"])
            }
            for dia, dados in sorted(vendas_por_dia.items())
        ],
        vendas_por_hora=[
            {
                "hora": f"{hora:02d}:00",
                "quantidade": dados["quantidade"],
                "valor": float(dados["valor"])
            }
            for hora, dados in sorted(vendas_por_hora.items())
        ]
    )

@router.get("/financeiro/consolidado")
async def relatorio_financeiro_consolidado(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2020),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Relatório financeiro consolidado mensal
    Replica funcionalidade: Sistema Relatórios > Financeiro
    """
    
    # Período do mês
    data_inicio = date(ano, mes, 1)
    if mes == 12:
        data_fim = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
    
    # Receitas
    receitas = db.query(
        func.sum(Venda.valor_total).label("total")
    ).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or Decimal(0)
    
    # Receitas por categoria
    receitas_categoria = db.query(
        Categoria.nome,
        func.sum(ItemVenda.valor_total).label("valor")
    ).join(
        Produto,
        Produto.categoria_id == Categoria.id
    ).join(
        ItemVenda,
        ItemVenda.produto_id == Produto.id
    ).join(
        Venda,
        Venda.id == ItemVenda.venda_id
    ).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).group_by(
        Categoria.id, Categoria.nome
    ).all()
    
    # Custos (baseado no preço de custo dos produtos)
    custos = db.query(
        func.sum(ItemVenda.quantidade * Produto.preco_custo).label("total")
    ).join(
        Produto,
        Produto.id == ItemVenda.produto_id
    ).join(
        Venda,
        Venda.id == ItemVenda.venda_id
    ).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA",
            Produto.preco_custo.isnot(None)
        )
    ).scalar() or Decimal(0)
    
    # Lucro bruto
    lucro_bruto = receitas - custos
    margem_lucro = (lucro_bruto / receitas * 100) if receitas > 0 else 0
    
    # Fluxo de caixa diário
    fluxo_diario = db.query(
        func.date(Venda.criado_em).label("data"),
        func.sum(Venda.valor_total).label("entrada")
    ).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).group_by(
        func.date(Venda.criado_em)
    ).all()
    
    # Fechamentos de caixa
    fechamentos = db.query(FechamentoCaixa).join(
        Caixa,
        Caixa.id == FechamentoCaixa.caixa_id
    ).filter(
        and_(
            func.date(Caixa.fechado_em) >= data_inicio,
            func.date(Caixa.fechado_em) <= data_fim
        )
    ).all()
    
    total_diferencas = sum(f.diferenca for f in fechamentos)
    
    return {
        "periodo": {
            "mes": mes,
            "ano": ano,
            "inicio": data_inicio.isoformat(),
            "fim": data_fim.isoformat()
        },
        "resumo": {
            "receita_total": float(receitas),
            "custo_total": float(custos),
            "lucro_bruto": float(lucro_bruto),
            "margem_lucro": float(margem_lucro)
        },
        "receitas_por_categoria": [
            {
                "categoria": r.nome,
                "valor": float(r.valor)
            }
            for r in receitas_categoria
        ],
        "fluxo_caixa_diario": [
            {
                "data": f.data.isoformat(),
                "entrada": float(f.entrada)
            }
            for f in fluxo_diario
        ],
        "diferencas_caixa": {
            "total_fechamentos": len(fechamentos),
            "diferenca_total": float(total_diferencas)
        }
    }

@router.get("/clientes/analise")
async def relatorio_analise_clientes(
    periodo_dias: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Análise completa de clientes
    Replica funcionalidade: Sistema Relatórios > Clientes
    """
    
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Top clientes por valor
    top_clientes_valor = db.query(
        Cliente.nome,
        Cliente.cpf,
        func.count(Venda.id).label("total_compras"),
        func.sum(Venda.valor_total).label("valor_total"),
        func.avg(Venda.valor_total).label("ticket_medio")
    ).join(
        Venda,
        Venda.cliente_cpf == Cliente.cpf
    ).filter(
        and_(
            Venda.criado_em >= data_inicio,
            Venda.status == "CONCLUIDA"
        )
    ).group_by(
        Cliente.id, Cliente.nome, Cliente.cpf
    ).order_by(
        desc("valor_total")
    ).limit(20).all()
    
    # Segmentação RFM (Recency, Frequency, Monetary)
    clientes_rfm = db.query(
        Cliente.id,
        Cliente.nome,
        func.max(Venda.criado_em).label("ultima_compra"),
        func.count(Venda.id).label("frequencia"),
        func.sum(Venda.valor_total).label("valor_total")
    ).join(
        Venda,
        Venda.cliente_cpf == Cliente.cpf
    ).filter(
        Venda.status == "CONCLUIDA"
    ).group_by(
        Cliente.id, Cliente.nome
    ).all()
    
    # Classificar clientes
    segmentos = {
        "champions": [],
        "loyal_customers": [],
        "potential_loyalists": [],
        "at_risk": [],
        "cant_lose": [],
        "lost": []
    }
    
    for cliente in clientes_rfm:
        dias_sem_compra = (datetime.now() - cliente.ultima_compra).days
        
        if dias_sem_compra <= 30 and cliente.frequencia >= 5 and cliente.valor_total >= 1000:
            segmentos["champions"].append(cliente.nome)
        elif dias_sem_compra <= 60 and cliente.frequencia >= 3:
            segmentos["loyal_customers"].append(cliente.nome)
        elif dias_sem_compra <= 90 and cliente.frequencia >= 1:
            segmentos["potential_loyalists"].append(cliente.nome)
        elif dias_sem_compra <= 180 and cliente.valor_total >= 500:
            segmentos["at_risk"].append(cliente.nome)
        elif dias_sem_compra <= 365 and cliente.valor_total >= 1000:
            segmentos["cant_lose"].append(cliente.nome)
        else:
            segmentos["lost"].append(cliente.nome)
    
    # Taxa de retenção
    total_clientes = db.query(func.count(Cliente.id)).scalar()
    clientes_ativos = db.query(
        func.count(func.distinct(Venda.cliente_cpf))
    ).filter(
        Venda.criado_em >= data_inicio
    ).scalar()
    
    taxa_retencao = (clientes_ativos / total_clientes * 100) if total_clientes > 0 else 0
    
    # Lifetime Value médio
    ltv_medio = db.query(
        func.avg(
            db.query(
                func.sum(Venda.valor_total)
            ).filter(
                Venda.cliente_cpf == Cliente.cpf
            ).scalar_subquery()
        )
    ).scalar() or 0
    
    return {
        "periodo_dias": periodo_dias,
        "metricas": {
            "total_clientes": total_clientes,
            "clientes_ativos": clientes_ativos,
            "taxa_retencao": float(taxa_retencao),
            "ltv_medio": float(ltv_medio)
        },
        "top_clientes": [
            {
                "nome": c.nome,
                "cpf": c.cpf,
                "total_compras": c.total_compras,
                "valor_total": float(c.valor_total),
                "ticket_medio": float(c.ticket_medio)
            }
            for c in top_clientes_valor
        ],
        "segmentacao_rfm": {
            "champions": len(segmentos["champions"]),
            "loyal_customers": len(segmentos["loyal_customers"]),
            "potential_loyalists": len(segmentos["potential_loyalists"]),
            "at_risk": len(segmentos["at_risk"]),
            "cant_lose": len(segmentos["cant_lose"]),
            "lost": len(segmentos["lost"])
        }
    }

@router.get("/eventos/performance")
async def relatorio_performance_eventos(
    evento_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Relatório de performance de eventos
    Replica funcionalidade: Sistema Relatórios > Eventos
    """
    
    query = db.query(Evento)
    
    if evento_id:
        query = query.filter(Evento.id == evento_id)
    
    if current_user.empresa_id:
        query = query.filter(Evento.empresa_id == current_user.empresa_id)
    
    eventos = query.all()
    
    resultado = []
    
    for evento in eventos:
        # Check-ins
        total_checkins = db.query(func.count(Checkin.id)).filter(
            Checkin.evento_id == evento.id
        ).scalar()
        
        # Vendas
        vendas_evento = db.query(
            func.count(Venda.id).label("quantidade"),
            func.sum(Venda.valor_total).label("valor")
        ).filter(
            and_(
                Venda.evento_id == evento.id,
                Venda.status == "CONCLUIDA"
            )
        ).first()
        
        # Taxa de conversão
        taxa_conversao = (
            vendas_evento.quantidade / total_checkins * 100
        ) if total_checkins > 0 else 0
        
        # Produtos mais vendidos no evento
        produtos_evento = db.query(
            Produto.nome,
            func.sum(ItemVenda.quantidade).label("quantidade")
        ).join(
            ItemVenda,
            ItemVenda.produto_id == Produto.id
        ).join(
            Venda,
            Venda.id == ItemVenda.venda_id
        ).filter(
            Venda.evento_id == evento.id
        ).group_by(
            Produto.id, Produto.nome
        ).order_by(
            desc("quantidade")
        ).limit(5).all()
        
        # Horário de pico
        checkins_por_hora = db.query(
            extract('hour', Checkin.horario_entrada).label("hora"),
            func.count(Checkin.id).label("quantidade")
        ).filter(
            Checkin.evento_id == evento.id
        ).group_by(
            "hora"
        ).order_by(
            desc("quantidade")
        ).first()
        
        resultado.append({
            "evento": {
                "id": evento.id,
                "nome": evento.nome,
                "data_inicio": evento.data_inicio.isoformat(),
                "data_fim": evento.data_fim.isoformat(),
                "capacidade_maxima": evento.capacidade_maxima
            },
            "metricas": {
                "total_checkins": total_checkins,
                "total_vendas": vendas_evento.quantidade if vendas_evento else 0,
                "valor_total": float(vendas_evento.valor) if vendas_evento and vendas_evento.valor else 0,
                "taxa_conversao": float(taxa_conversao),
                "ocupacao": (total_checkins / evento.capacidade_maxima * 100) if evento.capacidade_maxima else 0
            },
            "produtos_mais_vendidos": [
                {"produto": p.nome, "quantidade": float(p.quantidade)}
                for p in produtos_evento
            ],
            "horario_pico": {
                "hora": int(checkins_por_hora.hora) if checkins_por_hora else 0,
                "quantidade": checkins_por_hora.quantidade if checkins_por_hora else 0
            }
        })
    
    return resultado

@router.post("/export/excel")
async def exportar_relatorio_excel(
    tipo_relatorio: str = Query(..., description="vendas, financeiro, clientes, eventos"),
    filtros: FiltroRelatorio = Body(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exportar relatório para Excel
    Replica funcionalidade: Sistema Relatórios > Exportar
    """
    
    # Criar workbook
    wb = Workbook()
    ws = wb.active
    
    # Estilo do cabeçalho
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    if tipo_relatorio == "vendas":
        ws.title = "Relatório de Vendas"
        
        # Cabeçalhos
        headers = ["Data", "Número", "Cliente", "Vendedor", "Forma Pagamento", "Valor Total"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Dados
        vendas = db.query(Venda).filter(
            and_(
                func.date(Venda.criado_em) >= filtros.data_inicio,
                func.date(Venda.criado_em) <= filtros.data_fim,
                Venda.status == "CONCLUIDA"
            )
        ).all()
        
        for row, venda in enumerate(vendas, 2):
            ws.cell(row=row, column=1, value=venda.criado_em.strftime("%d/%m/%Y %H:%M"))
            ws.cell(row=row, column=2, value=venda.numero_venda)
            ws.cell(row=row, column=3, value=venda.cliente_cpf or "Não informado")
            
            vendedor = db.query(Usuario).filter(Usuario.id == venda.vendedor_id).first()
            ws.cell(row=row, column=4, value=vendedor.nome if vendedor else "")
            
            ws.cell(row=row, column=5, value=venda.tipo_pagamento)
            ws.cell(row=row, column=6, value=float(venda.valor_total))
        
        # Ajustar largura das colunas
        for col in range(1, 7):
            ws.column_dimensions[get_column_letter(col)].width = 15
    
    # Salvar em memória
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Retornar arquivo
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_{tipo_relatorio}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )

@router.get("/dashboard/bi")
async def dashboard_bi(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard de Business Intelligence com KPIs avançados
    Replica funcionalidade: Sistema BI Dashboard
    """
    
    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    inicio_ano = date(hoje.year, 1, 1)
    
    # KPIs principais
    vendas_hoje = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) == hoje,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or 0
    
    vendas_mes = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) >= inicio_mes,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or 0
    
    vendas_ano = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) >= inicio_ano,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or 0
    
    # Crescimento MoM (Month over Month)
    mes_anterior = inicio_mes - timedelta(days=1)
    inicio_mes_anterior = date(mes_anterior.year, mes_anterior.month, 1)
    
    vendas_mes_anterior = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) >= inicio_mes_anterior,
            func.date(Venda.criado_em) < inicio_mes,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or 1
    
    crescimento_mom = ((vendas_mes - vendas_mes_anterior) / vendas_mes_anterior * 100) if vendas_mes_anterior > 0 else 0
    
    # Previsão (simples média móvel)
    vendas_ultimos_30_dias = db.query(
        func.date(Venda.criado_em).label("data"),
        func.sum(Venda.valor_total).label("valor")
    ).filter(
        and_(
            Venda.criado_em >= datetime.now() - timedelta(days=30),
            Venda.status == "CONCLUIDA"
        )
    ).group_by(
        func.date(Venda.criado_em)
    ).all()
    
    media_diaria = sum(v.valor for v in vendas_ultimos_30_dias) / 30 if vendas_ultimos_30_dias else 0
    previsao_mes = media_diaria * 30
    
    return {
        "kpis": {
            "vendas_hoje": float(vendas_hoje),
            "vendas_mes": float(vendas_mes),
            "vendas_ano": float(vendas_ano),
            "crescimento_mom": float(crescimento_mom),
            "previsao_mes": float(previsao_mes)
        },
        "tendencias": {
            "media_diaria": float(media_diaria),
            "dias_ate_fim_mes": (date(hoje.year, hoje.month + 1 if hoje.month < 12 else 1, 1) - hoje).days
        }
    }
