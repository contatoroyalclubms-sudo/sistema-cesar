"""
Router para Sistema Cashless Avançado
Implementa todas as funcionalidades de comandas, recargas e movimentações
Baseado na análise da engenharia reversa do sistema MEEP
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import qrcode
import io
import base64
from decimal import Decimal

from ..database import get_db
from ..models_cashless import (
    CartaoCashless, RecargaCashless, MovimentacaoCashless, 
    ConfiguracaoCashlessEvento, TerminalPagamentoCashless,
    ComandaDigital, PedidoComandaDigital,
    StatusRecarga, TipoMovimentacao, StatusComandaDigital
)
from ..models import Usuario, Evento, Empresa
from ..schemas_cashless import (
    RecargaCashlessCreate, RecargaCashlessUpdate, RecargaCashlessResponse,
    MovimentacaoCashlessCreate, MovimentacaoCashlessResponse,
    ConfiguracaoCashlessCreate, ConfiguracaoCashlessUpdate, ConfiguracaoCashlessResponse,
    TerminalPagamentoCreate, TerminalPagamentoUpdate, TerminalPagamentoResponse,
    ComandaDigitalCreate, ComandaDigitalUpdate, ComandaDigitalResponse,
    PedidoComandaDigitalCreate, PedidoComandaDigitalUpdate, PedidoComandaDigitalResponse,
    DashboardCashlessResponse, FiltroRelatorioAvancado, RelatorioAvancadoResponse
)
from ..utils.security import get_current_user
from ..utils.cashless import CashlessService

router = APIRouter(prefix="/api/v1/cashless", tags=["Cashless Avançado"])

# ================================================================================
# ENDPOINTS PARA RECARGAS
# ================================================================================

@router.post("/recargas", response_model=RecargaCashlessResponse)
async def criar_recarga(
    recarga: RecargaCashlessCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova recarga para cartão cashless"""
    
    # Verificar se o cartão existe e está ativo
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == recarga.cartao_id).first()
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    
    if cartao.status != "ativo":
        raise HTTPException(status_code=400, detail="Cartão não está ativo")
    
    # Verificar configurações do evento
    config = db.query(ConfiguracaoCashlessEvento).filter(
        ConfiguracaoCashlessEvento.evento_id == cartao.evento_id
    ).first()
    
    if config:
        if recarga.valor_recarga < config.valor_minimo_recarga:
            raise HTTPException(
                status_code=400, 
                detail=f"Valor mínimo para recarga: R$ {config.valor_minimo_recarga}"
            )
        if recarga.valor_recarga > config.valor_maximo_recarga:
            raise HTTPException(
                status_code=400, 
                detail=f"Valor máximo para recarga: R$ {config.valor_maximo_recarga}"
            )
    
    # Calcular bonus se habilitado
    valor_bonus = Decimal('0')
    if config and config.bonus_habilitado and recarga.valor_recarga >= config.bonus_valor_minimo:
        valor_bonus = recarga.valor_recarga * (config.bonus_percentual / 100)
    
    # Criar recarga
    numero_recarga = f"REC{datetime.now().strftime('%Y%m%d%H%M%S')}{cartao.id:04d}"
    
    nova_recarga = RecargaCashless(
        numero_recarga=numero_recarga,
        cartao_id=recarga.cartao_id,
        valor_recarga=recarga.valor_recarga,
        valor_bonus=valor_bonus,
        valor_total=recarga.valor_recarga + valor_bonus,
        forma_pagamento=recarga.forma_pagamento,
        cpf_cliente=recarga.cpf_cliente,
        nome_cliente=recarga.nome_cliente,
        cpf_operador=recarga.cpf_operador,
        nome_operador=recarga.nome_operador,
        terminal_id=recarga.terminal_id,
        observacoes=recarga.observacoes,
        evento_id=cartao.evento_id,
        empresa_id=cartao.empresa_id
    )
    
    db.add(nova_recarga)
    db.commit()
    db.refresh(nova_recarga)
    
    # Processar recarga em background se necessário
    if recarga.forma_pagamento in ["PIX", "CARTAO"]:
        background_tasks.add_task(processar_recarga_gateway, nova_recarga.id, db)
    else:
        # Para dinheiro, aprovar automaticamente
        background_tasks.add_task(aprovar_recarga, nova_recarga.id, current_user.id, db)
    
    return nova_recarga

@router.put("/recargas/{recarga_id}", response_model=RecargaCashlessResponse)
async def atualizar_recarga(
    recarga_id: int,
    recarga_update: RecargaCashlessUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar status de recarga"""
    
    recarga = db.query(RecargaCashless).filter(RecargaCashless.id == recarga_id).first()
    if not recarga:
        raise HTTPException(status_code=404, detail="Recarga não encontrada")
    
    # Atualizar campos
    if recarga_update.status:
        recarga.status = recarga_update.status
        
        # Se aprovando, criar movimentação
        if recarga_update.status == StatusRecarga.APROVADA and recarga.status != StatusRecarga.APROVADA:
            await processar_aprovacao_recarga(recarga, current_user.id, db)
    
    if recarga_update.observacoes is not None:
        recarga.observacoes = recarga_update.observacoes
    
    if recarga_update.aprovado_por:
        recarga.aprovado_por = recarga_update.aprovado_por
        recarga.aprovado_em = datetime.now()
    
    db.commit()
    db.refresh(recarga)
    
    return recarga

@router.get("/recargas", response_model=List[RecargaCashlessResponse])
async def listar_recargas(
    evento_id: Optional[int] = Query(None),
    cartao_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    limite: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar recargas com filtros"""
    
    query = db.query(RecargaCashless)
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(RecargaCashless.evento_id == evento_id)
    if cartao_id:
        query = query.filter(RecargaCashless.cartao_id == cartao_id)
    if status:
        query = query.filter(RecargaCashless.status == status)
    if data_inicio:
        query = query.filter(RecargaCashless.criado_em >= data_inicio)
    if data_fim:
        data_fim_datetime = datetime.combine(data_fim, datetime.max.time())
        query = query.filter(RecargaCashless.criado_em <= data_fim_datetime)
    
    # Ordenar por mais recente
    query = query.order_by(desc(RecargaCashless.criado_em))
    
    # Aplicar paginação
    recargas = query.offset(offset).limit(limite).all()
    
    return recargas

# ================================================================================
# ENDPOINTS PARA MOVIMENTAÇÕES
# ================================================================================

@router.post("/movimentacoes", response_model=MovimentacaoCashlessResponse)
async def criar_movimentacao(
    movimentacao: MovimentacaoCashlessCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova movimentação financeira"""
    
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == movimentacao.cartao_id).first()
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    
    # Calcular saldos
    saldo_anterior = cartao.saldo_atual
    
    if movimentacao.tipo_movimentacao in [TipoMovimentacao.CREDITO, TipoMovimentacao.BONUS]:
        saldo_posterior = saldo_anterior + movimentacao.valor
    elif movimentacao.tipo_movimentacao == TipoMovimentacao.DEBITO:
        # Verificar se há saldo suficiente
        config = db.query(ConfiguracaoCashlessEvento).filter(
            ConfiguracaoCashlessEvento.evento_id == cartao.evento_id
        ).first()
        
        if not config or not config.permite_saldo_negativo:
            if saldo_anterior < movimentacao.valor:
                raise HTTPException(status_code=400, detail="Saldo insuficiente")
        
        saldo_posterior = saldo_anterior - movimentacao.valor
    else:
        saldo_posterior = saldo_anterior  # Para estornos e outros tipos
    
    # Gerar número da movimentação
    numero_movimento = f"MOV{datetime.now().strftime('%Y%m%d%H%M%S')}{cartao.id:04d}"
    
    # Criar movimentação
    nova_movimentacao = MovimentacaoCashless(
        numero_movimento=numero_movimento,
        cartao_id=movimentacao.cartao_id,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        valor=movimentacao.valor,
        saldo_anterior=saldo_anterior,
        saldo_posterior=saldo_posterior,
        descricao=movimentacao.descricao,
        referencia_id=movimentacao.referencia_id,
        referencia_tipo=movimentacao.referencia_tipo,
        referencia_numero=movimentacao.referencia_numero,
        terminal_id=movimentacao.terminal_id,
        cpf_operador=movimentacao.cpf_operador,
        nome_operador=movimentacao.nome_operador,
        evento_id=cartao.evento_id,
        empresa_id=cartao.empresa_id
    )
    
    # Atualizar saldo do cartão
    cartao.saldo_atual = saldo_posterior
    cartao.ultima_utilizacao = datetime.now()
    
    db.add(nova_movimentacao)
    db.commit()
    db.refresh(nova_movimentacao)
    
    return nova_movimentacao

@router.get("/movimentacoes", response_model=List[MovimentacaoCashlessResponse])
async def listar_movimentacoes(
    cartao_id: Optional[int] = Query(None),
    tipo_movimentacao: Optional[str] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    limite: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Listar movimentações com filtros"""
    
    query = db.query(MovimentacaoCashless)
    
    if cartao_id:
        query = query.filter(MovimentacaoCashless.cartao_id == cartao_id)
    if tipo_movimentacao:
        query = query.filter(MovimentacaoCashless.tipo_movimentacao == tipo_movimentacao)
    if data_inicio:
        query = query.filter(MovimentacaoCashless.criado_em >= data_inicio)
    if data_fim:
        data_fim_datetime = datetime.combine(data_fim, datetime.max.time())
        query = query.filter(MovimentacaoCashless.criado_em <= data_fim_datetime)
    
    query = query.order_by(desc(MovimentacaoCashless.criado_em))
    movimentacoes = query.offset(offset).limit(limite).all()
    
    return movimentacoes

# ================================================================================
# ENDPOINTS PARA COMANDAS DIGITAIS
# ================================================================================

@router.post("/comandas", response_model=ComandaDigitalResponse)
async def criar_comanda_digital(
    comanda: ComandaDigitalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova comanda digital com QR Code"""
    
    # Gerar UUID para a comanda
    comanda_uuid = str(uuid.uuid4())
    qr_code = f"COMANDA_{comanda_uuid}"
    url_acesso = f"https://app.paineluniversal.com/comanda/{comanda_uuid}"
    
    # Criar comanda
    nova_comanda = ComandaDigital(
        numero_comanda=comanda.numero_comanda,
        qr_code=qr_code,
        url_acesso=url_acesso,
        cartao_id=comanda.cartao_id,
        mesa_id=comanda.mesa_id,
        cliente_cpf=comanda.cliente_cpf,
        cliente_nome=comanda.cliente_nome,
        cliente_telefone=comanda.cliente_telefone,
        limite_credito=comanda.limite_credito,
        evento_id=comanda.evento_id,
        empresa_id=comanda.empresa_id
    )
    
    db.add(nova_comanda)
    db.commit()
    db.refresh(nova_comanda)
    
    return nova_comanda

@router.get("/comandas/{comanda_uuid}")
async def obter_comanda_por_uuid(
    comanda_uuid: str,
    db: Session = Depends(get_db)
):
    """Obter comanda digital pelo UUID do QR Code"""
    
    qr_code = f"COMANDA_{comanda_uuid}"
    comanda = db.query(ComandaDigital).filter(ComandaDigital.qr_code == qr_code).first()
    
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    
    # Retornar dados da comanda com cardápio
    return {
        "comanda": comanda,
        "cardapio": await obter_cardapio_evento(comanda.evento_id, db),
        "mesa": comanda.mesa,
        "pedidos": comanda.pedidos
    }

@router.post("/comandas/{comanda_id}/pedidos", response_model=PedidoComandaDigitalResponse)
async def criar_pedido_comanda(
    comanda_id: int,
    pedido: PedidoComandaDigitalCreate,
    db: Session = Depends(get_db)
):
    """Criar novo pedido na comanda digital"""
    
    comanda = db.query(ComandaDigital).filter(ComandaDigital.id == comanda_id).first()
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    
    if comanda.status != StatusComandaDigital.ATIVA:
        raise HTTPException(status_code=400, detail="Comanda não está ativa")
    
    # Calcular valores
    valor_produtos = sum(item.quantidade * item.preco_unitario for item in pedido.produtos)
    valor_total = valor_produtos  # Adicionar taxa de serviço se configurado
    
    # Gerar número do pedido
    numero_pedido = f"PED{datetime.now().strftime('%Y%m%d%H%M%S')}{comanda_id:04d}"
    
    # Criar pedido
    novo_pedido = PedidoComandaDigital(
        numero_pedido=numero_pedido,
        comanda_id=comanda_id,
        produtos=[item.dict() for item in pedido.produtos],
        valor_produtos=valor_produtos,
        valor_total=valor_total,
        observacoes_cliente=pedido.observacoes_cliente,
        evento_id=comanda.evento_id,
        empresa_id=comanda.empresa_id
    )
    
    # Atualizar valores da comanda
    comanda.valor_total += valor_total
    comanda.valor_pendente += valor_total
    
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    
    return novo_pedido

# ================================================================================
# ENDPOINTS PARA DASHBOARD E RELATÓRIOS
# ================================================================================

@router.get("/dashboard", response_model=DashboardCashlessResponse)
async def obter_dashboard_cashless(
    evento_id: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter dados do dashboard cashless"""
    
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    # Construir filtros base
    filtros_base = []
    if evento_id:
        filtros_base.append(RecargaCashless.evento_id == evento_id)
    
    filtros_base.extend([
        RecargaCashless.criado_em >= data_inicio,
        RecargaCashless.criado_em <= datetime.combine(data_fim, datetime.max.time())
    ])
    
    # Dados de recargas
    recargas_query = db.query(RecargaCashless).filter(and_(*filtros_base))
    
    total_recargas = recargas_query.count()
    recargas_aprovadas = recargas_query.filter(RecargaCashless.status == StatusRecarga.APROVADA).count()
    recargas_pendentes = recargas_query.filter(RecargaCashless.status == StatusRecarga.PENDENTE).count()
    recargas_canceladas = recargas_query.filter(RecargaCashless.status == StatusRecarga.CANCELADA).count()
    
    valores_recargas = recargas_query.filter(RecargaCashless.status == StatusRecarga.APROVADA).with_entities(
        func.sum(RecargaCashless.valor_recarga).label('total_recargas'),
        func.sum(RecargaCashless.valor_bonus).label('total_bonus')
    ).first()
    
    valor_total_recargas = valores_recargas.total_recargas or Decimal('0')
    valor_total_bonus = valores_recargas.total_bonus or Decimal('0')
    ticket_medio = valor_total_recargas / recargas_aprovadas if recargas_aprovadas > 0 else Decimal('0')
    
    # Dados de movimentações
    filtros_mov = filtros_base.copy()
    if evento_id:
        filtros_mov = [MovimentacaoCashless.evento_id == evento_id]
    
    movimentacoes_query = db.query(MovimentacaoCashless).filter(and_(*filtros_mov))
    
    total_movimentacoes = movimentacoes_query.count()
    
    creditos = movimentacoes_query.filter(
        MovimentacaoCashless.tipo_movimentacao.in_([TipoMovimentacao.CREDITO, TipoMovimentacao.BONUS])
    ).with_entities(func.sum(MovimentacaoCashless.valor)).scalar() or Decimal('0')
    
    debitos = movimentacoes_query.filter(
        MovimentacaoCashless.tipo_movimentacao == TipoMovimentacao.DEBITO
    ).with_entities(func.sum(MovimentacaoCashless.valor)).scalar() or Decimal('0')
    
    # Dados de cartões
    filtros_cartao = []
    if evento_id:
        filtros_cartao.append(CartaoCashless.evento_id == evento_id)
    
    cartoes_ativos = db.query(CartaoCashless).filter(
        and_(CartaoCashless.status == "ativo", *filtros_cartao)
    ).count()
    
    cartoes_bloqueados = db.query(CartaoCashless).filter(
        and_(CartaoCashless.status == "bloqueado", *filtros_cartao)
    ).count()
    
    # Saldo atual do sistema
    saldo_atual_sistema = db.query(func.sum(CartaoCashless.saldo_atual)).filter(
        and_(*filtros_cartao)
    ).scalar() or Decimal('0')
    
    # Outros dados
    eventos_ativos = db.query(Evento).filter(Evento.ativo == True).count()
    terminais_online = db.query(TerminalPagamentoCashless).filter(
        TerminalPagamentoCashless.online == True
    ).count()
    comandas_abertas = db.query(ComandaDigital).filter(
        ComandaDigital.status == StatusComandaDigital.ATIVA
    ).count()
    
    return {
        "periodo_inicio": data_inicio,
        "periodo_fim": data_fim,
        "recargas": {
            "total_recargas": total_recargas,
            "valor_total_recargas": valor_total_recargas,
            "valor_total_bonus": valor_total_bonus,
            "recargas_aprovadas": recargas_aprovadas,
            "recargas_pendentes": recargas_pendentes,
            "recargas_canceladas": recargas_canceladas,
            "ticket_medio": ticket_medio
        },
        "movimentacoes": {
            "total_movimentacoes": total_movimentacoes,
            "valor_total_creditos": creditos,
            "valor_total_debitos": debitos,
            "saldo_atual_sistema": saldo_atual_sistema,
            "cartoes_ativos": cartoes_ativos,
            "cartoes_bloqueados": cartoes_bloqueados
        },
        "eventos_ativos": eventos_ativos,
        "terminais_online": terminais_online,
        "comandas_abertas": comandas_abertas
    }

# ================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================

async def processar_recarga_gateway(recarga_id: int, db: Session):
    """Processar recarga via gateway de pagamento"""
    # Implementar integração com gateway
    pass

async def aprovar_recarga(recarga_id: int, aprovador_id: int, db: Session):
    """Aprovar recarga e criar movimentação"""
    recarga = db.query(RecargaCashless).filter(RecargaCashless.id == recarga_id).first()
    if recarga and recarga.status == StatusRecarga.PENDENTE:
        await processar_aprovacao_recarga(recarga, aprovador_id, db)

async def processar_aprovacao_recarga(recarga: RecargaCashless, aprovador_id: int, db: Session):
    """Processar aprovação da recarga e criar movimentação"""
    # Atualizar status da recarga
    recarga.status = StatusRecarga.APROVADA
    recarga.aprovado_por = aprovador_id
    recarga.aprovado_em = datetime.now()
    
    # Criar movimentação de crédito
    movimentacao = MovimentacaoCashless(
        numero_movimento=f"MOV{datetime.now().strftime('%Y%m%d%H%M%S')}{recarga.cartao_id:04d}",
        cartao_id=recarga.cartao_id,
        tipo_movimentacao=TipoMovimentacao.CREDITO,
        valor=recarga.valor_total,
        saldo_anterior=recarga.cartao.saldo_atual,
        saldo_posterior=recarga.cartao.saldo_atual + recarga.valor_total,
        descricao=f"Recarga aprovada - {recarga.numero_recarga}",
        referencia_id=recarga.id,
        referencia_tipo="recarga",
        referencia_numero=recarga.numero_recarga,
        evento_id=recarga.evento_id,
        empresa_id=recarga.empresa_id
    )
    
    # Atualizar saldo do cartão
    recarga.cartao.saldo_atual += recarga.valor_total
    
    db.add(movimentacao)
    db.commit()

async def obter_cardapio_evento(evento_id: int, db: Session):
    """Obter cardápio digital do evento"""
    # Implementar busca do cardápio digital
    return []
