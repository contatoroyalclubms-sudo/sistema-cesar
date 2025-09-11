"""
Router para gerenciamento de caixa de eventos
Implementação baseada no sistema MEEP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from ..database import get_db
from ..models import (
    Evento, Usuario, Transacao, Checkin, 
    Produto, ItemVenda, CaixaEvento, MovimentacaoCaixa
)
from ..schemas import (
    CaixaEventoCreate, CaixaEventoUpdate, CaixaEventoResponse,
    MovimentacaoCaixaCreate, MovimentacaoCaixaResponse,
    VendaCreate, VendaResponse, EstatisticasCaixa
)
from ..auth import get_current_user

router = APIRouter(prefix="/eventos/{evento_id}/caixa", tags=["Evento Caixa"])

@router.post("/abrir", response_model=CaixaEventoResponse)
def abrir_caixa(
    evento_id: int,
    caixa_data: CaixaEventoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Abrir caixa para um evento"""
    
    # Verificar se evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verificar se já existe caixa aberto
    caixa_aberto = db.query(CaixaEvento).filter(
        and_(
            CaixaEvento.evento_id == evento_id,
            CaixaEvento.status == "aberto"
        )
    ).first()
    
    if caixa_aberto:
        raise HTTPException(status_code=400, detail="Já existe um caixa aberto para este evento")
    
    # Criar novo caixa
    novo_caixa = CaixaEvento(
        evento_id=evento_id,
        usuario_abertura_id=current_user.id,
        valor_inicial=caixa_data.valor_inicial,
        data_abertura=datetime.now(),
        status="aberto"
    )
    
    db.add(novo_caixa)
    db.commit()
    db.refresh(novo_caixa)
    
    return novo_caixa

@router.post("/fechar", response_model=CaixaEventoResponse)
def fechar_caixa(
    evento_id: int,
    valor_final: float,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Fechar caixa do evento"""
    
    # Buscar caixa aberto
    caixa = db.query(CaixaEvento).filter(
        and_(
            CaixaEvento.evento_id == evento_id,
            CaixaEvento.status == "aberto"
        )
    ).first()
    
    if not caixa:
        raise HTTPException(status_code=404, detail="Não há caixa aberto para este evento")
    
    # Calcular totais
    vendas_total = db.query(func.sum(Transacao.valor_total)).filter(
        and_(
            Transacao.evento_id == evento_id,
            Transacao.data_transacao >= caixa.data_abertura,
            Transacao.status == "confirmada"
        )
    ).scalar() or 0
    
    # Atualizar caixa
    caixa.data_fechamento = datetime.now()
    caixa.usuario_fechamento_id = current_user.id
    caixa.valor_final = valor_final
    caixa.valor_vendas = vendas_total
    caixa.diferenca = valor_final - (caixa.valor_inicial + vendas_total)
    caixa.observacoes = observacoes
    caixa.status = "fechado"
    
    db.commit()
    db.refresh(caixa)
    
    return caixa

@router.post("/sangria", response_model=MovimentacaoCaixaResponse)
def registrar_sangria(
    evento_id: int,
    movimentacao: MovimentacaoCaixaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registrar sangria (retirada) do caixa"""
    
    # Verificar caixa aberto
    caixa = db.query(CaixaEvento).filter(
        and_(
            CaixaEvento.evento_id == evento_id,
            CaixaEvento.status == "aberto"
        )
    ).first()
    
    if not caixa:
        raise HTTPException(status_code=404, detail="Não há caixa aberto para este evento")
    
    # Criar movimentação
    nova_movimentacao = MovimentacaoCaixa(
        caixa_id=caixa.id,
        tipo="sangria",
        valor=movimentacao.valor,
        motivo=movimentacao.motivo,
        usuario_id=current_user.id,
        data_movimentacao=datetime.now()
    )
    
    db.add(nova_movimentacao)
    db.commit()
    db.refresh(nova_movimentacao)
    
    return nova_movimentacao

@router.post("/suprimento", response_model=MovimentacaoCaixaResponse)
def registrar_suprimento(
    evento_id: int,
    movimentacao: MovimentacaoCaixaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registrar suprimento (entrada) no caixa"""
    
    # Verificar caixa aberto
    caixa = db.query(CaixaEvento).filter(
        and_(
            CaixaEvento.evento_id == evento_id,
            CaixaEvento.status == "aberto"
        )
    ).first()
    
    if not caixa:
        raise HTTPException(status_code=404, detail="Não há caixa aberto para este evento")
    
    # Criar movimentação
    nova_movimentacao = MovimentacaoCaixa(
        caixa_id=caixa.id,
        tipo="suprimento",
        valor=movimentacao.valor,
        motivo=movimentacao.motivo,
        usuario_id=current_user.id,
        data_movimentacao=datetime.now()
    )
    
    db.add(nova_movimentacao)
    db.commit()
    db.refresh(nova_movimentacao)
    
    return nova_movimentacao

@router.get("/estatisticas", response_model=EstatisticasCaixa)
def obter_estatisticas_caixa(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter estatísticas do caixa do evento"""
    
    # Buscar caixa atual
    caixa = db.query(CaixaEvento).filter(
        CaixaEvento.evento_id == evento_id
    ).order_by(CaixaEvento.data_abertura.desc()).first()
    
    if not caixa:
        return EstatisticasCaixa(
            faturamento=0,
            ticket_medio=0,
            ticket_medio_consumo=0,
            ticket_medio_total=0,
            entradas_vendidas=0,
            checkins_realizados=0,
            vendas_dinheiro=0,
            vendas_cartao=0,
            vendas_pix=0,
            total_sangrias=0,
            total_suprimentos=0,
            saldo_atual=0
        )
    
    # Calcular estatísticas
    inicio = caixa.data_abertura
    fim = caixa.data_fechamento or datetime.now()
    
    # Total de vendas
    vendas = db.query(Transacao).filter(
        and_(
            Transacao.evento_id == evento_id,
            Transacao.data_transacao >= inicio,
            Transacao.data_transacao <= fim,
            Transacao.status == "confirmada"
        )
    ).all()
    
    faturamento = sum(v.valor_total for v in vendas)
    num_vendas = len(vendas)
    ticket_medio = faturamento / num_vendas if num_vendas > 0 else 0
    
    # Vendas por forma de pagamento
    vendas_dinheiro = sum(v.valor_total for v in vendas if v.forma_pagamento == "dinheiro")
    vendas_cartao = sum(v.valor_total for v in vendas if v.forma_pagamento == "cartao")
    vendas_pix = sum(v.valor_total for v in vendas if v.forma_pagamento == "pix")
    
    # Entradas vendidas
    entradas_vendidas = db.query(func.count(ItemVenda.id)).join(Transacao).filter(
        and_(
            Transacao.evento_id == evento_id,
            Transacao.data_transacao >= inicio,
            Transacao.data_transacao <= fim,
            ItemVenda.tipo_item == "entrada"
        )
    ).scalar() or 0
    
    # Check-ins realizados
    checkins_realizados = db.query(func.count(Checkin.id)).filter(
        and_(
            Checkin.evento_id == evento_id,
            Checkin.data_checkin >= inicio,
            Checkin.data_checkin <= fim
        )
    ).scalar() or 0
    
    # Movimentações
    movimentacoes = db.query(MovimentacaoCaixa).filter(
        MovimentacaoCaixa.caixa_id == caixa.id
    ).all()
    
    total_sangrias = sum(m.valor for m in movimentacoes if m.tipo == "sangria")
    total_suprimentos = sum(m.valor for m in movimentacoes if m.tipo == "suprimento")
    
    # Saldo atual
    saldo_atual = caixa.valor_inicial + faturamento + total_suprimentos - total_sangrias
    
    return EstatisticasCaixa(
        faturamento=faturamento,
        ticket_medio=ticket_medio,
        ticket_medio_consumo=0,  # Implementar cálculo específico se necessário
        ticket_medio_total=ticket_medio,
        entradas_vendidas=entradas_vendidas,
        checkins_realizados=checkins_realizados,
        vendas_dinheiro=vendas_dinheiro,
        vendas_cartao=vendas_cartao,
        vendas_pix=vendas_pix,
        total_sangrias=total_sangrias,
        total_suprimentos=total_suprimentos,
        saldo_atual=saldo_atual
    )

@router.post("/vendas", response_model=VendaResponse)
def registrar_venda(
    evento_id: int,
    venda_data: VendaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registrar nova venda no caixa"""
    
    # Verificar caixa aberto
    caixa = db.query(CaixaEvento).filter(
        and_(
            CaixaEvento.evento_id == evento_id,
            CaixaEvento.status == "aberto"
        )
    ).first()
    
    if not caixa:
        raise HTTPException(status_code=404, detail="Não há caixa aberto para este evento")
    
    # Criar transação
    nova_transacao = Transacao(
        evento_id=evento_id,
        usuario_id=current_user.id,
        cpf_cliente=venda_data.cpf_cliente,
        nome_cliente=venda_data.nome_cliente,
        tipo_transacao="venda",
        forma_pagamento=venda_data.forma_pagamento,
        valor_total=venda_data.total,
        status="confirmada",
        data_transacao=datetime.now()
    )
    
    db.add(nova_transacao)
    db.flush()
    
    # Adicionar itens da venda
    for item in venda_data.itens:
        novo_item = ItemVenda(
            transacao_id=nova_transacao.id,
            tipo_item=item.tipo,
            nome_item=item.nome,
            quantidade=item.quantidade,
            valor_unitario=item.preco,
            desconto=item.desconto or 0,
            valor_total=item.preco * item.quantidade * (1 - (item.desconto or 0) / 100)
        )
        db.add(novo_item)
    
    db.commit()
    db.refresh(nova_transacao)
    
    return VendaResponse(
        id=nova_transacao.id,
        evento_id=evento_id,
        cpf_cliente=nova_transacao.cpf_cliente,
        nome_cliente=nova_transacao.nome_cliente,
        forma_pagamento=nova_transacao.forma_pagamento,
        valor_total=nova_transacao.valor_total,
        status=nova_transacao.status,
        data_transacao=nova_transacao.data_transacao,
        vendedor=current_user.nome
    )

@router.get("/movimentacoes", response_model=List[MovimentacaoCaixaResponse])
def listar_movimentacoes(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas as movimentações do caixa atual"""
    
    # Buscar caixa atual
    caixa = db.query(CaixaEvento).filter(
        CaixaEvento.evento_id == evento_id
    ).order_by(CaixaEvento.data_abertura.desc()).first()
    
    if not caixa:
        return []
    
    movimentacoes = db.query(MovimentacaoCaixa).filter(
        MovimentacaoCaixa.caixa_id == caixa.id
    ).order_by(MovimentacaoCaixa.data_movimentacao.desc()).all()
    
    return movimentacoes

@router.get("/relatorio-fechamento")
def gerar_relatorio_fechamento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Gerar relatório de fechamento de caixa"""
    
    # Buscar último caixa
    caixa = db.query(CaixaEvento).filter(
        CaixaEvento.evento_id == evento_id
    ).order_by(CaixaEvento.data_abertura.desc()).first()
    
    if not caixa:
        raise HTTPException(status_code=404, detail="Nenhum caixa encontrado para este evento")
    
    # Buscar todas as transações
    transacoes = db.query(Transacao).filter(
        and_(
            Transacao.evento_id == evento_id,
            Transacao.data_transacao >= caixa.data_abertura,
            Transacao.data_transacao <= (caixa.data_fechamento or datetime.now())
        )
    ).all()
    
    # Buscar movimentações
    movimentacoes = db.query(MovimentacaoCaixa).filter(
        MovimentacaoCaixa.caixa_id == caixa.id
    ).all()
    
    # Calcular resumo
    vendas_por_tipo = {}
    vendas_por_pagamento = {
        "dinheiro": 0,
        "cartao": 0,
        "pix": 0
    }
    
    for transacao in transacoes:
        vendas_por_pagamento[transacao.forma_pagamento] += transacao.valor_total
        
        # Agrupar por tipo de item
        itens = db.query(ItemVenda).filter(
            ItemVenda.transacao_id == transacao.id
        ).all()
        
        for item in itens:
            if item.tipo_item not in vendas_por_tipo:
                vendas_por_tipo[item.tipo_item] = {
                    "quantidade": 0,
                    "valor_total": 0
                }
            vendas_por_tipo[item.tipo_item]["quantidade"] += item.quantidade
            vendas_por_tipo[item.tipo_item]["valor_total"] += item.valor_total
    
    # Montar relatório
    relatorio = {
        "evento_id": evento_id,
        "caixa": {
            "id": caixa.id,
            "data_abertura": caixa.data_abertura,
            "data_fechamento": caixa.data_fechamento,
            "valor_inicial": caixa.valor_inicial,
            "valor_final": caixa.valor_final,
            "valor_vendas": caixa.valor_vendas,
            "diferenca": caixa.diferenca,
            "status": caixa.status
        },
        "vendas": {
            "total_transacoes": len(transacoes),
            "valor_total": sum(t.valor_total for t in transacoes),
            "por_tipo": vendas_por_tipo,
            "por_pagamento": vendas_por_pagamento
        },
        "movimentacoes": {
            "sangrias": sum(m.valor for m in movimentacoes if m.tipo == "sangria"),
            "suprimentos": sum(m.valor for m in movimentacoes if m.tipo == "suprimento"),
            "detalhes": [
                {
                    "tipo": m.tipo,
                    "valor": m.valor,
                    "motivo": m.motivo,
                    "data": m.data_movimentacao
                }
                for m in movimentacoes
            ]
        },
        "resumo": {
            "saldo_inicial": caixa.valor_inicial,
            "entradas": sum(t.valor_total for t in transacoes) + sum(m.valor for m in movimentacoes if m.tipo == "suprimento"),
            "saidas": sum(m.valor for m in movimentacoes if m.tipo == "sangria"),
            "saldo_esperado": caixa.valor_inicial + sum(t.valor_total for t in transacoes) + sum(m.valor for m in movimentacoes if m.tipo == "suprimento") - sum(m.valor for m in movimentacoes if m.tipo == "sangria"),
            "saldo_informado": caixa.valor_final if caixa.valor_final else 0,
            "diferenca": caixa.diferenca if caixa.diferenca else 0
        }
    }
    
    return relatorio