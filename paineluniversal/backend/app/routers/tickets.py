"""
Router para gerenciamento de tickets e ingressos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
import json
import qrcode
import io
import base64
import secrets
from enum import Enum

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    TipoTicket, TipoTicketCreate, TipoTicketUpdate,
    Ticket, TicketCreate, TicketUpdate,
    LoteTicket, LoteTicketCreate, LoteTicketUpdate,
    TransferenciaTicket, TransferenciaTicketCreate
)

router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"]
)

class StatusTicket(str, Enum):
    DISPONIVEL = "disponivel"
    RESERVADO = "reservado"
    VENDIDO = "vendido"
    USADO = "usado"
    CANCELADO = "cancelado"
    TRANSFERIDO = "transferido"

class TipoPagamento(str, Enum):
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    PIX = "pix"
    BOLETO = "boleto"
    DINHEIRO = "dinheiro"
    CORTESIA = "cortesia"

def gerar_codigo_ticket() -> str:
    """Gera código único para ticket"""
    return f"TKT{datetime.now().strftime('%Y%m%d')}{secrets.token_hex(4).upper()}"

def gerar_qr_code_ticket(ticket_id: int, codigo: str) -> str:
    """Gera QR code para ticket"""
    url = f"https://app.eventos.com/ticket/{ticket_id}/{codigo}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def calcular_preco_com_taxas(valor_base: float, incluir_taxas: bool = True) -> Dict[str, float]:
    """Calcula preço final com taxas"""
    taxa_servico = valor_base * 0.10  # 10% taxa de serviço
    taxa_pagamento = valor_base * 0.03  # 3% taxa de pagamento
    
    if incluir_taxas:
        valor_final = valor_base + taxa_servico + taxa_pagamento
    else:
        valor_final = valor_base
    
    return {
        "valor_base": round(valor_base, 2),
        "taxa_servico": round(taxa_servico, 2),
        "taxa_pagamento": round(taxa_pagamento, 2),
        "valor_final": round(valor_final, 2)
    }

@router.get("/tipos/", response_model=List[TipoTicket])
def listar_tipos_ticket(
    evento_id: Optional[int] = None,
    disponivel: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista tipos de tickets disponíveis"""
    query = db.query(models.TipoTicket)
    
    if evento_id:
        query = query.filter(models.TipoTicket.evento_id == evento_id)
    
    if disponivel is not None:
        if disponivel:
            query = query.filter(
                models.TipoTicket.quantidade_disponivel > 0,
                models.TipoTicket.ativo == True
            )
        else:
            query = query.filter(
                or_(
                    models.TipoTicket.quantidade_disponivel == 0,
                    models.TipoTicket.ativo == False
                )
            )
    
    tipos = query.order_by(models.TipoTicket.ordem).all()
    
    # Adicionar informações de lotes ativos
    for tipo in tipos:
        lote_ativo = db.query(models.LoteTicket).filter(
            models.LoteTicket.tipo_ticket_id == tipo.id,
            models.LoteTicket.ativo == True,
            models.LoteTicket.data_inicio <= datetime.now(),
            or_(
                models.LoteTicket.data_fim.is_(None),
                models.LoteTicket.data_fim >= datetime.now()
            )
        ).first()
        
        if lote_ativo:
            tipo.preco_atual = lote_ativo.preco
            tipo.lote_atual = lote_ativo.nome
        else:
            tipo.preco_atual = tipo.preco_base
            tipo.lote_atual = None
    
    return tipos

@router.get("/tipos/{tipo_id}", response_model=TipoTicket)
def obter_tipo_ticket(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém um tipo de ticket específico"""
    tipo = db.query(models.TipoTicket).filter(
        models.TipoTicket.id == tipo_id
    ).first()
    
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ticket não encontrado")
    
    return tipo

@router.post("/tipos/", response_model=TipoTicket)
def criar_tipo_ticket(
    tipo: TipoTicketCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo tipo de ticket"""
    # Verificar se evento existe
    evento = db.query(models.Evento).filter(
        models.Evento.id == tipo.evento_id
    ).first()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Converter benefícios para JSON
    beneficios = json.dumps(tipo.beneficios) if tipo.beneficios else None
    restricoes = json.dumps(tipo.restricoes) if tipo.restricoes else None
    
    db_tipo = models.TipoTicket(
        **tipo.model_dump(exclude={'beneficios', 'restricoes'}),
        beneficios=beneficios,
        restricoes=restricoes,
        quantidade_disponivel=tipo.quantidade_total
    )
    
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    
    return db_tipo

@router.put("/tipos/{tipo_id}", response_model=TipoTicket)
def atualizar_tipo_ticket(
    tipo_id: int,
    tipo_update: TipoTicketUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um tipo de ticket"""
    tipo = db.query(models.TipoTicket).filter(
        models.TipoTicket.id == tipo_id
    ).first()
    
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ticket não encontrado")
    
    update_data = tipo_update.model_dump(exclude_unset=True)
    
    if 'beneficios' in update_data and update_data['beneficios']:
        update_data['beneficios'] = json.dumps(update_data['beneficios'])
    
    if 'restricoes' in update_data and update_data['restricoes']:
        update_data['restricoes'] = json.dumps(update_data['restricoes'])
    
    for key, value in update_data.items():
        setattr(tipo, key, value)
    
    db.commit()
    db.refresh(tipo)
    
    return tipo

# ====== LOTES DE TICKETS ======

@router.get("/lotes/", response_model=List[LoteTicket])
def listar_lotes_ticket(
    tipo_ticket_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista lotes de tickets"""
    query = db.query(models.LoteTicket)
    
    if tipo_ticket_id:
        query = query.filter(models.LoteTicket.tipo_ticket_id == tipo_ticket_id)
    
    if ativo is not None:
        query = query.filter(models.LoteTicket.ativo == ativo)
    
    lotes = query.order_by(models.LoteTicket.ordem).all()
    
    # Adicionar estatísticas
    for lote in lotes:
        lote.vendidos = db.query(models.Ticket).filter(
            models.Ticket.lote_id == lote.id,
            models.Ticket.status.in_(["vendido", "usado"])
        ).count()
        
        lote.disponivel = lote.quantidade - lote.vendidos
    
    return lotes

@router.post("/lotes/", response_model=LoteTicket)
def criar_lote_ticket(
    lote: LoteTicketCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo lote de tickets"""
    # Verificar tipo de ticket
    tipo = db.query(models.TipoTicket).filter(
        models.TipoTicket.id == lote.tipo_ticket_id
    ).first()
    
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ticket não encontrado")
    
    db_lote = models.LoteTicket(**lote.model_dump())
    
    db.add(db_lote)
    db.commit()
    db.refresh(db_lote)
    
    return db_lote

@router.put("/lotes/{lote_id}", response_model=LoteTicket)
def atualizar_lote_ticket(
    lote_id: int,
    lote_update: LoteTicketUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um lote de tickets"""
    lote = db.query(models.LoteTicket).filter(
        models.LoteTicket.id == lote_id
    ).first()
    
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    
    update_data = lote_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(lote, key, value)
    
    db.commit()
    db.refresh(lote)
    
    return lote

# ====== TICKETS INDIVIDUAIS ======

@router.get("/", response_model=List[Ticket])
def listar_tickets(
    skip: int = 0,
    limit: int = 100,
    evento_id: Optional[int] = None,
    tipo_ticket_id: Optional[int] = None,
    status: Optional[str] = None,
    cliente_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista tickets"""
    query = db.query(models.Ticket)
    
    if evento_id:
        query = query.join(models.TipoTicket).filter(
            models.TipoTicket.evento_id == evento_id
        )
    
    if tipo_ticket_id:
        query = query.filter(models.Ticket.tipo_ticket_id == tipo_ticket_id)
    
    if status:
        query = query.filter(models.Ticket.status == status)
    
    if cliente_id:
        query = query.filter(models.Ticket.cliente_id == cliente_id)
    
    tickets = query.order_by(
        models.Ticket.data_compra.desc()
    ).offset(skip).limit(limit).all()
    
    return tickets

@router.get("/{ticket_id}", response_model=Ticket)
def obter_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém um ticket específico"""
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    return ticket

@router.post("/comprar", response_model=List[Ticket])
def comprar_tickets(
    compra: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Realiza compra de tickets"""
    # Verificar tipo de ticket
    tipo = db.query(models.TipoTicket).filter(
        models.TipoTicket.id == compra.tipo_ticket_id,
        models.TipoTicket.ativo == True
    ).first()
    
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ticket não encontrado ou indisponível")
    
    # Verificar disponibilidade
    if tipo.quantidade_disponivel < compra.quantidade:
        raise HTTPException(
            status_code=400,
            detail=f"Apenas {tipo.quantidade_disponivel} tickets disponíveis"
        )
    
    # Verificar lote ativo
    lote = db.query(models.LoteTicket).filter(
        models.LoteTicket.tipo_ticket_id == tipo.id,
        models.LoteTicket.ativo == True,
        models.LoteTicket.data_inicio <= datetime.now(),
        or_(
            models.LoteTicket.data_fim.is_(None),
            models.LoteTicket.data_fim >= datetime.now()
        )
    ).first()
    
    if not lote:
        # Usar preço base se não houver lote ativo
        preco_unitario = tipo.preco_base
        lote_id = None
    else:
        preco_unitario = lote.preco
        lote_id = lote.id
    
    # Calcular valores
    precos = calcular_preco_com_taxas(preco_unitario * compra.quantidade)
    
    # Criar tickets
    tickets_criados = []
    for i in range(compra.quantidade):
        codigo = gerar_codigo_ticket()
        qr_code = gerar_qr_code_ticket(0, codigo)  # ID será atualizado depois
        
        ticket = models.Ticket(
            tipo_ticket_id=compra.tipo_ticket_id,
            lote_id=lote_id,
            cliente_id=compra.cliente_id or current_user.id,
            codigo=codigo,
            qr_code=qr_code,
            status="reservado",
            valor_pago=preco_unitario,
            nome_titular=compra.nome_titular,
            cpf_titular=compra.cpf_titular,
            email_titular=compra.email_titular,
            telefone_titular=compra.telefone_titular
        )
        
        db.add(ticket)
        tickets_criados.append(ticket)
    
    # Atualizar disponibilidade
    tipo.quantidade_disponivel -= compra.quantidade
    tipo.quantidade_vendida = (tipo.quantidade_vendida or 0) + compra.quantidade
    
    if lote:
        lote.quantidade_vendida = (lote.quantidade_vendida or 0) + compra.quantidade
    
    db.commit()
    
    # Atualizar QR codes com IDs corretos
    for ticket in tickets_criados:
        ticket.qr_code = gerar_qr_code_ticket(ticket.id, ticket.codigo)
    
    db.commit()
    
    # Enviar confirmação em background
    background_tasks.add_task(
        enviar_confirmacao_compra,
        tickets_criados,
        compra.email_titular
    )
    
    return tickets_criados

async def enviar_confirmacao_compra(tickets: List[models.Ticket], email: str):
    """Envia email de confirmação de compra"""
    # Implementação de envio de email
    # ... código de envio ...
    pass

@router.post("/{ticket_id}/validar")
def validar_ticket(
    ticket_id: int,
    codigo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Valida um ticket para entrada"""
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Verificar código se fornecido
    if codigo and ticket.codigo != codigo:
        raise HTTPException(status_code=400, detail="Código de ticket inválido")
    
    # Verificar status
    if ticket.status == "usado":
        return {
            "valido": False,
            "mensagem": "Ticket já foi utilizado",
            "data_uso": ticket.data_uso.isoformat() if ticket.data_uso else None
        }
    
    if ticket.status != "vendido":
        return {
            "valido": False,
            "mensagem": f"Ticket com status {ticket.status} não pode ser validado"
        }
    
    # Validar ticket
    ticket.status = "usado"
    ticket.data_uso = datetime.now()
    ticket.usado_por_id = current_user.id
    
    db.commit()
    
    return {
        "valido": True,
        "mensagem": "Ticket validado com sucesso",
        "ticket": {
            "codigo": ticket.codigo,
            "tipo": ticket.tipo_ticket.nome if ticket.tipo_ticket else None,
            "titular": ticket.nome_titular
        }
    }

@router.post("/{ticket_id}/cancelar")
def cancelar_ticket(
    ticket_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cancela um ticket"""
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if ticket.status in ["usado", "cancelado"]:
        raise HTTPException(
            status_code=400,
            detail=f"Ticket com status {ticket.status} não pode ser cancelado"
        )
    
    # Cancelar ticket
    ticket.status = "cancelado"
    ticket.data_cancelamento = datetime.now()
    ticket.motivo_cancelamento = motivo
    
    # Devolver ao estoque
    tipo = ticket.tipo_ticket
    if tipo:
        tipo.quantidade_disponivel += 1
        tipo.quantidade_vendida = max(0, (tipo.quantidade_vendida or 0) - 1)
    
    if ticket.lote:
        ticket.lote.quantidade_vendida = max(0, (ticket.lote.quantidade_vendida or 0) - 1)
    
    db.commit()
    
    return {"message": "Ticket cancelado com sucesso"}

# ====== TRANSFERÊNCIAS ======

@router.post("/transferir", response_model=TransferenciaTicket)
def transferir_ticket(
    transferencia: TransferenciaTicketCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Transfere um ticket para outro cliente"""
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == transferencia.ticket_id,
        models.Ticket.cliente_id == current_user.id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket não encontrado ou você não é o proprietário"
        )
    
    if ticket.status not in ["vendido", "reservado"]:
        raise HTTPException(
            status_code=400,
            detail=f"Ticket com status {ticket.status} não pode ser transferido"
        )
    
    # Verificar se novo cliente existe
    novo_cliente = db.query(models.ClienteEvento).filter(
        models.ClienteEvento.id == transferencia.novo_cliente_id
    ).first()
    
    if not novo_cliente:
        raise HTTPException(status_code=404, detail="Novo cliente não encontrado")
    
    # Criar registro de transferência
    db_transferencia = models.TransferenciaTicket(
        ticket_id=transferencia.ticket_id,
        cliente_anterior_id=ticket.cliente_id,
        cliente_novo_id=transferencia.novo_cliente_id,
        motivo=transferencia.motivo
    )
    
    # Atualizar ticket
    ticket.cliente_id = transferencia.novo_cliente_id
    ticket.status = "transferido"
    
    # Atualizar dados do titular se fornecidos
    if transferencia.nome_titular:
        ticket.nome_titular = transferencia.nome_titular
    if transferencia.cpf_titular:
        ticket.cpf_titular = transferencia.cpf_titular
    if transferencia.email_titular:
        ticket.email_titular = transferencia.email_titular
    if transferencia.telefone_titular:
        ticket.telefone_titular = transferencia.telefone_titular
    
    # Gerar novo QR code
    ticket.qr_code = gerar_qr_code_ticket(ticket.id, ticket.codigo)
    
    db.add(db_transferencia)
    db.commit()
    db.refresh(db_transferencia)
    
    return db_transferencia

@router.get("/relatorios/vendas")
def relatorio_vendas_tickets(
    evento_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera relatório de vendas de tickets"""
    query = db.query(models.Ticket).filter(
        models.Ticket.status.in_(["vendido", "usado"])
    )
    
    if evento_id:
        query = query.join(models.TipoTicket).filter(
            models.TipoTicket.evento_id == evento_id
        )
    
    if data_inicio:
        query = query.filter(models.Ticket.data_compra >= data_inicio)
    
    if data_fim:
        query = query.filter(models.Ticket.data_compra <= data_fim)
    
    tickets = query.all()
    
    # Calcular estatísticas
    total_vendidos = len(tickets)
    receita_total = sum(t.valor_pago for t in tickets)
    
    # Vendas por tipo
    vendas_por_tipo = {}
    for ticket in tickets:
        tipo_nome = ticket.tipo_ticket.nome if ticket.tipo_ticket else "Desconhecido"
        if tipo_nome not in vendas_por_tipo:
            vendas_por_tipo[tipo_nome] = {
                "quantidade": 0,
                "receita": 0
            }
        vendas_por_tipo[tipo_nome]["quantidade"] += 1
        vendas_por_tipo[tipo_nome]["receita"] += ticket.valor_pago
    
    # Vendas por dia
    vendas_por_dia = {}
    for ticket in tickets:
        data = ticket.data_compra.date() if ticket.data_compra else None
        if data:
            if data not in vendas_por_dia:
                vendas_por_dia[data] = {
                    "quantidade": 0,
                    "receita": 0
                }
            vendas_por_dia[data]["quantidade"] += 1
            vendas_por_dia[data]["receita"] += ticket.valor_pago
    
    return {
        "periodo": {
            "inicio": data_inicio.isoformat() if data_inicio else None,
            "fim": data_fim.isoformat() if data_fim else None
        },
        "resumo": {
            "total_vendidos": total_vendidos,
            "receita_total": round(receita_total, 2),
            "ticket_medio": round(receita_total / total_vendidos, 2) if total_vendidos > 0 else 0
        },
        "por_tipo": vendas_por_tipo,
        "por_dia": [
            {
                "data": str(data),
                "quantidade": valores["quantidade"],
                "receita": round(valores["receita"], 2)
            }
            for data, valores in sorted(vendas_por_dia.items())
        ]
    }