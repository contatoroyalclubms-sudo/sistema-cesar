"""
Router para Financeiro Completo - Sistema financeiro avançado
Contas a pagar, contas a receber, fluxo de caixa, conciliação
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Usuario, Venda, ContaPagar, ContaReceber, CentroCusto,
    FluxoCaixa, ConciliacaoBancaria, MovimentoFinanceiro,
    PlanejamentoOrcamentario, MetaFinanceira, Empresa
)
from ..schemas_meep_complete import DashboardFinanceiro

router = APIRouter(
    prefix="/api/financeiro",
    tags=["Financeiro"]
)

@router.get("/dashboard", response_model=DashboardFinanceiro)
async def dashboard_financeiro(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard financeiro completo
    Replica funcionalidade: Sistema Financeiro > Dashboard
    """
    
    # Período padrão: mês atual
    if not mes:
        mes = date.today().month
    if not ano:
        ano = date.today().year
    
    data_inicio = date(ano, mes, 1)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_fim = date(ano, mes, ultimo_dia)
    
    # Receitas (vendas)
    receita_total = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or Decimal(0)
    
    # Receitas por forma de pagamento
    receitas_pagamento = db.query(
        Venda.tipo_pagamento,
        func.sum(Venda.valor_total).label("total")
    ).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).group_by(Venda.tipo_pagamento).all()
    
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
    
    # Contas a pagar em aberto
    contas_pagar_abertas = db.query(func.count(ContaPagar.id)).filter(
        ContaPagar.status == "PENDENTE"
    ).scalar() or 0
    
    # Contas a receber em aberto
    contas_receber_abertas = db.query(func.count(ContaReceber.id)).filter(
        ContaReceber.status == "PENDENTE"
    ).scalar() or 0
    
    # Valor em aberto (contas a pagar)
    valor_comandas_abertas = db.query(func.sum(ContaPagar.valor)).filter(
        ContaPagar.status == "PENDENTE"
    ).scalar() or Decimal(0)
    
    return DashboardFinanceiro(
        receita_total=receita_total,
        receita_dinheiro=receita_dinheiro,
        receita_cartao=receita_cartao,
        receita_pix=receita_pix,
        receita_cashless=receita_cashless,
        comandas_abertas=contas_pagar_abertas,
        comandas_fechadas=contas_receber_abertas,
        valor_comandas_abertas=valor_comandas_abertas
    )

@router.post("/contas-pagar/create")
async def criar_conta_pagar(
    fornecedor: str,
    descricao: str,
    valor: Decimal,
    data_vencimento: date,
    centro_custo_id: Optional[int] = None,
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar conta a pagar
    Replica funcionalidade: Sistema Financeiro > Contas a Pagar
    """
    
    nova_conta = ContaPagar(
        fornecedor=fornecedor,
        descricao=descricao,
        valor=valor,
        data_vencimento=data_vencimento,
        centro_custo_id=centro_custo_id,
        observacoes=observacoes,
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        status="PENDENTE"
    )
    
    db.add(nova_conta)
    db.commit()
    db.refresh(nova_conta)
    
    return nova_conta

@router.get("/contas-pagar")
async def listar_contas_pagar(
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    fornecedor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar contas a pagar com filtros
    """
    
    query = db.query(ContaPagar)
    
    if current_user.empresa_id:
        query = query.filter(ContaPagar.empresa_id == current_user.empresa_id)
    
    if status:
        query = query.filter(ContaPagar.status == status)
    
    if data_inicio:
        query = query.filter(ContaPagar.data_vencimento >= data_inicio)
    
    if data_fim:
        query = query.filter(ContaPagar.data_vencimento <= data_fim)
    
    if fornecedor:
        query = query.filter(ContaPagar.fornecedor.ilike(f"%{fornecedor}%"))
    
    contas = query.order_by(ContaPagar.data_vencimento).all()
    
    # Calcular totais
    total_pendente = sum(c.valor for c in contas if c.status == "PENDENTE")
    total_pago = sum(c.valor for c in contas if c.status == "PAGO")
    
    return {
        "contas": [
            {
                "id": c.id,
                "fornecedor": c.fornecedor,
                "descricao": c.descricao,
                "valor": float(c.valor),
                "data_vencimento": c.data_vencimento.isoformat(),
                "status": c.status,
                "dias_vencimento": (date.today() - c.data_vencimento).days if c.status == "PENDENTE" else None
            }
            for c in contas
        ],
        "resumo": {
            "total_contas": len(contas),
            "total_pendente": float(total_pendente),
            "total_pago": float(total_pago)
        }
    }

@router.put("/contas-pagar/{conta_id}/pagar")
async def pagar_conta(
    conta_id: int,
    data_pagamento: date,
    valor_pago: Decimal,
    forma_pagamento: str,
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Realizar pagamento de conta
    """
    
    conta = db.query(ContaPagar).filter(ContaPagar.id == conta_id).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    if conta.status != "PENDENTE":
        raise HTTPException(status_code=400, detail="Conta já foi paga")
    
    # Atualizar conta
    conta.status = "PAGO"
    conta.data_pagamento = data_pagamento
    conta.valor_pago = valor_pago
    conta.forma_pagamento = forma_pagamento
    
    if observacoes:
        conta.observacoes = (conta.observacoes or "") + f"\nPagamento: {observacoes}"
    
    # Registrar movimento financeiro
    movimento = MovimentoFinanceiro(
        tipo="SAIDA",
        valor=valor_pago,
        descricao=f"Pagamento - {conta.fornecedor}: {conta.descricao}",
        forma_pagamento=forma_pagamento,
        conta_pagar_id=conta.id,
        centro_custo_id=conta.centro_custo_id,
        usuario_id=current_user.id
    )
    db.add(movimento)
    
    db.commit()
    
    return {
        "conta_id": conta_id,
        "status": "PAGO",
        "valor_pago": float(valor_pago),
        "data_pagamento": data_pagamento.isoformat()
    }

@router.get("/fluxo-caixa")
async def fluxo_caixa(
    data_inicio: date,
    data_fim: date,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Relatório de fluxo de caixa
    Replica funcionalidade: Sistema Financeiro > Fluxo de Caixa
    """
    
    # Entradas (vendas)
    entradas = db.query(
        func.date(Venda.criado_em).label("data"),
        func.sum(Venda.valor_total).label("valor")
    ).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).group_by(
        func.date(Venda.criado_em)
    ).all()
    
    # Saídas (contas pagas)
    saidas = db.query(
        ContaPagar.data_pagamento.label("data"),
        func.sum(ContaPagar.valor_pago).label("valor")
    ).filter(
        and_(
            ContaPagar.data_pagamento >= data_inicio,
            ContaPagar.data_pagamento <= data_fim,
            ContaPagar.status == "PAGO"
        )
    ).group_by(
        ContaPagar.data_pagamento
    ).all()
    
    # Organizar por data
    fluxo_diario = {}
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        fluxo_diario[data_atual] = {
            "data": data_atual.isoformat(),
            "entradas": Decimal(0),
            "saidas": Decimal(0),
            "saldo_dia": Decimal(0)
        }
        data_atual += timedelta(days=1)
    
    # Adicionar entradas
    for entrada in entradas:
        if entrada.data in fluxo_diario:
            fluxo_diario[entrada.data]["entradas"] = entrada.valor
    
    # Adicionar saídas
    for saida in saidas:
        if saida.data in fluxo_diario:
            fluxo_diario[saida.data]["saidas"] = saida.valor
    
    # Calcular saldo diário e acumulado
    saldo_acumulado = Decimal(0)
    fluxo_final = []
    
    for data_key in sorted(fluxo_diario.keys()):
        dia = fluxo_diario[data_key]
        saldo_dia = dia["entradas"] - dia["saidas"]
        saldo_acumulado += saldo_dia
        
        fluxo_final.append({
            "data": dia["data"],
            "entradas": float(dia["entradas"]),
            "saidas": float(dia["saidas"]),
            "saldo_dia": float(saldo_dia),
            "saldo_acumulado": float(saldo_acumulado)
        })
    
    # Resumo
    total_entradas = sum(float(d["entradas"]) for d in fluxo_final)
    total_saidas = sum(float(d["saidas"]) for d in fluxo_final)
    
    return {
        "periodo": {
            "inicio": data_inicio.isoformat(),
            "fim": data_fim.isoformat()
        },
        "resumo": {
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "saldo_periodo": total_entradas - total_saidas,
            "saldo_final": float(saldo_acumulado)
        },
        "fluxo_diario": fluxo_final
    }

@router.post("/centro-custo/create")
async def criar_centro_custo(
    nome: str,
    descricao: Optional[str] = None,
    orcamento_mensal: Optional[Decimal] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar centro de custo
    Replica funcionalidade: Sistema Financeiro > Centros de Custo
    """
    
    novo_centro = CentroCusto(
        nome=nome,
        descricao=descricao,
        orcamento_mensal=orcamento_mensal,
        empresa_id=current_user.empresa_id,
        ativo=True
    )
    
    db.add(novo_centro)
    db.commit()
    db.refresh(novo_centro)
    
    return novo_centro

@router.get("/centro-custo/analise")
async def analise_centro_custo(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2020),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Análise de gastos por centro de custo
    """
    
    data_inicio = date(ano, mes, 1)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_fim = date(ano, mes, ultimo_dia)
    
    # Gastos por centro de custo
    gastos_centro = db.query(
        CentroCusto.nome,
        CentroCusto.orcamento_mensal,
        func.sum(ContaPagar.valor_pago).label("gasto_realizado")
    ).outerjoin(
        ContaPagar,
        and_(
            ContaPagar.centro_custo_id == CentroCusto.id,
            ContaPagar.data_pagamento >= data_inicio,
            ContaPagar.data_pagamento <= data_fim,
            ContaPagar.status == "PAGO"
        )
    ).filter(
        CentroCusto.empresa_id == current_user.empresa_id if current_user.empresa_id else True
    ).group_by(
        CentroCusto.id, CentroCusto.nome, CentroCusto.orcamento_mensal
    ).all()
    
    resultado = []
    total_orcado = Decimal(0)
    total_realizado = Decimal(0)
    
    for centro in gastos_centro:
        gasto_realizado = centro.gasto_realizado or Decimal(0)
        orcamento = centro.orcamento_mensal or Decimal(0)
        
        if orcamento > 0:
            percentual_usado = (gasto_realizado / orcamento) * 100
            status = (
                "Crítico" if percentual_usado > 90 else
                "Atenção" if percentual_usado > 70 else
                "Normal"
            )
        else:
            percentual_usado = 0
            status = "Sem orçamento"
        
        resultado.append({
            "centro_custo": centro.nome,
            "orcamento_mensal": float(orcamento),
            "gasto_realizado": float(gasto_realizado),
            "saldo_disponivel": float(orcamento - gasto_realizado),
            "percentual_usado": float(percentual_usado),
            "status": status
        })
        
        total_orcado += orcamento
        total_realizado += gasto_realizado
    
    return {
        "periodo": f"{mes:02d}/{ano}",
        "resumo": {
            "total_orcado": float(total_orcado),
            "total_realizado": float(total_realizado),
            "saldo_total": float(total_orcado - total_realizado),
            "percentual_geral": float((total_realizado / total_orcado) * 100) if total_orcado > 0 else 0
        },
        "centros_custo": resultado
    }

@router.get("/dre")
async def demonstrativo_resultado(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2020),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Demonstrativo de Resultado do Exercício (DRE)
    Replica funcionalidade: Sistema Financeiro > DRE
    """
    
    data_inicio = date(ano, mes, 1)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_fim = date(ano, mes, ultimo_dia)
    
    # Receita Bruta (Vendas)
    receita_bruta = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or Decimal(0)
    
    # Deduções (descontos)
    deducoes = db.query(func.sum(Venda.desconto)).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or Decimal(0)
    
    # Receita Líquida
    receita_liquida = receita_bruta - deducoes
    
    # Custos por categoria
    custos_categoria = db.query(
        CentroCusto.nome,
        func.sum(ContaPagar.valor_pago).label("valor")
    ).join(
        ContaPagar,
        ContaPagar.centro_custo_id == CentroCusto.id
    ).filter(
        and_(
            ContaPagar.data_pagamento >= data_inicio,
            ContaPagar.data_pagamento <= data_fim,
            ContaPagar.status == "PAGO"
        )
    ).group_by(
        CentroCusto.id, CentroCusto.nome
    ).all()
    
    # Separar custos e despesas
    custo_vendas = Decimal(0)
    despesas_operacionais = Decimal(0)
    despesas_administrativas = Decimal(0)
    
    custos_detalhados = []
    
    for custo in custos_categoria:
        valor = custo.valor or Decimal(0)
        custos_detalhados.append({
            "categoria": custo.nome,
            "valor": float(valor)
        })
        
        # Classificar por tipo (simplificado)
        if "venda" in custo.nome.lower() or "produto" in custo.nome.lower():
            custo_vendas += valor
        elif "admin" in custo.nome.lower() or "escritorio" in custo.nome.lower():
            despesas_administrativas += valor
        else:
            despesas_operacionais += valor
    
    # Cálculos do DRE
    lucro_bruto = receita_liquida - custo_vendas
    lucro_operacional = lucro_bruto - despesas_operacionais
    lucro_liquido = lucro_operacional - despesas_administrativas
    
    # Margens
    margem_bruta = (lucro_bruto / receita_liquida * 100) if receita_liquida > 0 else 0
    margem_operacional = (lucro_operacional / receita_liquida * 100) if receita_liquida > 0 else 0
    margem_liquida = (lucro_liquido / receita_liquida * 100) if receita_liquida > 0 else 0
    
    return {
        "periodo": f"{mes:02d}/{ano}",
        "dre": {
            "receita_bruta": float(receita_bruta),
            "deducoes": float(deducoes),
            "receita_liquida": float(receita_liquida),
            "custo_vendas": float(custo_vendas),
            "lucro_bruto": float(lucro_bruto),
            "despesas_operacionais": float(despesas_operacionais),
            "lucro_operacional": float(lucro_operacional),
            "despesas_administrativas": float(despesas_administrativas),
            "lucro_liquido": float(lucro_liquido)
        },
        "margens": {
            "margem_bruta": float(margem_bruta),
            "margem_operacional": float(margem_operacional),
            "margem_liquida": float(margem_liquida)
        },
        "custos_detalhados": custos_detalhados
    }

@router.post("/metas/create")
async def criar_meta_financeira(
    tipo: str = Query(..., description="RECEITA, CUSTO, LUCRO"),
    valor: Decimal = Query(...),
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2020),
    descricao: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar meta financeira
    Replica funcionalidade: Sistema Financeiro > Metas
    """
    
    # Verificar se já existe meta para o período
    meta_existente = db.query(MetaFinanceira).filter(
        and_(
            MetaFinanceira.tipo == tipo,
            MetaFinanceira.mes == mes,
            MetaFinanceira.ano == ano,
            MetaFinanceira.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if meta_existente:
        raise HTTPException(status_code=400, detail="Meta já existe para este período")
    
    nova_meta = MetaFinanceira(
        tipo=tipo,
        valor=valor,
        mes=mes,
        ano=ano,
        descricao=descricao,
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id
    )
    
    db.add(nova_meta)
    db.commit()
    db.refresh(nova_meta)
    
    return nova_meta

@router.get("/metas/acompanhamento")
async def acompanhamento_metas(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2020),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acompanhamento de metas financeiras
    """
    
    # Buscar metas do período
    metas = db.query(MetaFinanceira).filter(
        and_(
            MetaFinanceira.mes == mes,
            MetaFinanceira.ano == ano,
            MetaFinanceira.empresa_id == current_user.empresa_id if current_user.empresa_id else True
        )
    ).all()
    
    data_inicio = date(ano, mes, 1)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_fim = date(ano, mes, ultimo_dia)
    
    # Dados reais do período
    receita_real = db.query(func.sum(Venda.valor_total)).filter(
        and_(
            func.date(Venda.criado_em) >= data_inicio,
            func.date(Venda.criado_em) <= data_fim,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or Decimal(0)
    
    custo_real = db.query(func.sum(ContaPagar.valor_pago)).filter(
        and_(
            ContaPagar.data_pagamento >= data_inicio,
            ContaPagar.data_pagamento <= data_fim,
            ContaPagar.status == "PAGO"
        )
    ).scalar() or Decimal(0)
    
    lucro_real = receita_real - custo_real
    
    # Valores reais por tipo
    valores_reais = {
        "RECEITA": receita_real,
        "CUSTO": custo_real,
        "LUCRO": lucro_real
    }
    
    # Comparar com metas
    resultado = []
    
    for meta in metas:
        valor_real = valores_reais.get(meta.tipo, Decimal(0))
        percentual_atingido = (valor_real / meta.valor * 100) if meta.valor > 0 else 0
        
        status = (
            "Superou" if percentual_atingido > 100 else
            "Atingiu" if percentual_atingido >= 95 else
            "Próximo" if percentual_atingido >= 80 else
            "Distante"
        )
        
        resultado.append({
            "tipo": meta.tipo,
            "meta": float(meta.valor),
            "realizado": float(valor_real),
            "diferenca": float(valor_real - meta.valor),
            "percentual_atingido": float(percentual_atingido),
            "status": status,
            "descricao": meta.descricao
        })
    
    return {
        "periodo": f"{mes:02d}/{ano}",
        "metas": resultado,
        "resumo": {
            "total_metas": len(metas),
            "metas_atingidas": len([r for r in resultado if r["percentual_atingido"] >= 95]),
            "performance_geral": sum(r["percentual_atingido"] for r in resultado) / len(resultado) if resultado else 0
        }
    }
