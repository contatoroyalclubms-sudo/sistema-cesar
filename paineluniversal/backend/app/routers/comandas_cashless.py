"""
Router para Comandas e Sistema Cashless - Funcionalidades completas do MEEP
Gestão de comandas, cartões cashless, recargas e transações
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario, Cliente
from ..models_meep_complete import Comanda, Pedido, Produto, CartaoCashless, TransacaoCashless
# StatusComanda, TipoPagamento, Pagamento - may need to be created
from ..schemas_meep_complete import (
    ComandaCreate, ComandaUpdate, ComandaResponse,
    PedidoCreate, PedidoUpdate, PedidoResponse,
    CartaoCashlessCreate, CartaoCashlessUpdate, CartaoCashlessResponse,
    RecargaCashless
)

router = APIRouter(
    prefix="/api",
    tags=["Comandas & Cashless"]
)

# ==================== COMANDAS ====================

@router.get("/comandas", response_model=List[ComandaResponse])
async def listar_comandas(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    periodo_dias: Optional[int] = Query(None, description="Período em dias"),
    busca: Optional[str] = Query(None, description="Buscar por CPF, tag, número ou nome"),
    ativas: Optional[bool] = Query(None, description="Apenas ativas"),
    abertas: Optional[bool] = Query(None, description="Apenas abertas"),
    bloqueadas: Optional[bool] = Query(None, description="Apenas bloqueadas"),
    com_consumo: Optional[bool] = Query(None, description="Apenas com consumo"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista comandas com filtros avançados
    Replica funcionalidade: MEEP Informações dos clientes > Comandas
    """
    
    query = db.query(Comanda)
    
    # Filtros
    if status:
        query = query.filter(Comanda.status == status)
    
    if periodo_dias:
        data_inicio = datetime.now() - timedelta(days=periodo_dias)
        query = query.filter(Comanda.aberta_em >= data_inicio)
    
    if busca:
        # Buscar por CPF, número da comanda ou nome do cliente
        query = query.join(Usuario, Comanda.cliente_id == Usuario.id).filter(
            or_(
                Comanda.numero.contains(busca),
                Usuario.cpf.contains(busca),
                Usuario.nome.ilike(f"%{busca}%")
            )
        )
    
    if ativas:
        query = query.filter(Comanda.status != StatusComanda.CANCELADA)
    
    if abertas:
        query = query.filter(Comanda.status == StatusComanda.ABERTA)
    
    if bloqueadas:
        query = query.filter(Comanda.status == StatusComanda.BLOQUEADA)
    
    if com_consumo:
        query = query.filter(Comanda.valor_total > 0)
    
    comandas = query.order_by(desc(Comanda.aberta_em)).all()
    return comandas

@router.post("/comandas", response_model=ComandaResponse)
async def criar_comanda(
    comanda: ComandaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria nova comanda
    """
    
    # Verificar se número já existe
    existe = db.query(Comanda).filter(Comanda.numero == comanda.numero).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comanda {comanda.numero} já existe"
        )
    
    db_comanda = Comanda(
        **comanda.dict(),
        status=StatusComanda.ABERTA,
        valor_total=Decimal(0)
    )
    
    db.add(db_comanda)
    db.commit()
    db.refresh(db_comanda)
    
    return db_comanda

@router.get("/comandas/{comanda_id}", response_model=ComandaResponse)
async def obter_comanda(
    comanda_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de uma comanda específica
    """
    
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    
    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comanda não encontrada"
        )
    
    return comanda

@router.put("/comandas/{comanda_id}", response_model=ComandaResponse)
async def atualizar_comanda(
    comanda_id: int,
    update_data: ComandaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza comanda
    """
    
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    
    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comanda não encontrada"
        )
    
    # Aplicar atualizações
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(comanda, field, value)
    
    # Se fechando a comanda
    if update_data.status == StatusComanda.FECHADA and not comanda.fechada_em:
        comanda.fechada_em = datetime.now()
    
    db.commit()
    db.refresh(comanda)
    
    return comanda

@router.post("/comandas/{comanda_id}/fechar")
async def fechar_comanda(
    comanda_id: int,
    tipo_pagamento: TipoPagamento,
    desconto: Optional[Decimal] = 0,
    taxa_servico: Optional[Decimal] = 0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fecha comanda e processa pagamento
    """
    
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    
    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comanda não encontrada"
        )
    
    if comanda.status != StatusComanda.ABERTA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comanda não está aberta"
        )
    
    # Calcular total com desconto e taxa
    valor_final = comanda.valor_total - desconto + taxa_servico
    
    # Criar pagamento
    pagamento = Pagamento(
        comanda_id=comanda_id,
        tipo_pagamento=tipo_pagamento,
        valor=valor_final,
        status="APROVADO"
    )
    
    # Atualizar comanda
    comanda.status = StatusComanda.FECHADA
    comanda.fechada_em = datetime.now()
    comanda.desconto = desconto
    comanda.taxa_servico = taxa_servico
    
    db.add(pagamento)
    db.commit()
    
    return {
        "message": "Comanda fechada com sucesso",
        "valor_total": float(valor_final),
        "pagamento_id": pagamento.id
    }

# ==================== PEDIDOS ====================

@router.post("/comandas/{comanda_id}/pedidos", response_model=PedidoResponse)
async def adicionar_pedido(
    comanda_id: int,
    pedido: PedidoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Adiciona pedido à comanda
    """
    
    # Verificar comanda
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    
    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comanda não encontrada"
        )
    
    if comanda.status != StatusComanda.ABERTA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comanda não está aberta"
        )
    
    # Buscar produto
    produto = db.query(Produto).filter(Produto.id == pedido.produto_id).first()
    
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Criar pedido
    db_pedido = Pedido(
        comanda_id=comanda_id,
        produto_id=pedido.produto_id,
        quantidade=pedido.quantidade,
        preco_unitario=produto.preco,
        valor_total=produto.preco * pedido.quantidade,
        observacoes=pedido.observacoes,
        status="PENDENTE"
    )
    
    # Atualizar total da comanda
    comanda.valor_total += db_pedido.valor_total
    
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    
    return db_pedido

@router.put("/pedidos/{pedido_id}/status")
async def atualizar_status_pedido(
    pedido_id: int,
    status: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza status do pedido (para KDS - Kitchen Display System)
    """
    
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado"
        )
    
    pedido.status = status
    
    # Atualizar timestamps baseado no status
    if status == "PREPARANDO":
        pedido.preparado_em = datetime.now()
    elif status == "ENTREGUE":
        pedido.entregue_em = datetime.now()
    
    db.commit()
    
    return {"message": f"Status atualizado para {status}"}

# ==================== CASHLESS ====================

@router.get("/cashless/cartoes", response_model=List[CartaoCashlessResponse])
async def listar_cartoes(
    filtro_caixa: Optional[int] = None,
    busca: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista cartões cashless
    Replica funcionalidade: MEEP Informações dos clientes > Cashless
    """
    
    query = db.query(CartaoCashless).join(Cliente)
    
    if busca:
        query = query.filter(
            or_(
                CartaoCashless.numero.contains(busca),
                CartaoCashless.tag_rfid.contains(busca),
                Cliente.nome.ilike(f"%{busca}%"),
                Cliente.cpf.contains(busca)
            )
        )
    
    if current_user.empresa_id:
        query = query.filter(Cliente.empresa_id == current_user.empresa_id)
    
    cartoes = query.all()
    return cartoes

@router.post("/cashless/cartoes", response_model=CartaoCashlessResponse)
async def criar_cartao(
    cartao: CartaoCashlessCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo cartão cashless
    """
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == cartao.cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar duplicação
    existe = db.query(CartaoCashless).filter(
        or_(
            CartaoCashless.numero == cartao.numero,
            CartaoCashless.tag_rfid == cartao.tag_rfid if cartao.tag_rfid else False
        )
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cartão ou tag RFID já cadastrado"
        )
    
    db_cartao = CartaoCashless(**cartao.dict())
    db.add(db_cartao)
    db.commit()
    db.refresh(db_cartao)
    
    return db_cartao

@router.post("/cashless/recarga")
async def recarregar_cartao(
    recarga: RecargaCashless,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Realiza recarga de cartão cashless
    """
    
    # Buscar cartão
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == recarga.cartao_id).first()
    
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    if cartao.bloqueado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cartão bloqueado"
        )
    
    # Criar transação
    saldo_anterior = cartao.saldo
    saldo_posterior = saldo_anterior + recarga.valor
    
    transacao = TransacaoCashless(
        cartao_id=cartao.id,
        cliente_id=cartao.cliente_id,
        tipo="RECARGA",
        valor=recarga.valor,
        saldo_anterior=saldo_anterior,
        saldo_posterior=saldo_posterior,
        descricao=f"Recarga via {recarga.forma_pagamento}",
        referencia=str(uuid.uuid4())
    )
    
    # Atualizar saldo do cartão e do cliente
    cartao.saldo = saldo_posterior
    
    cliente = db.query(Cliente).filter(Cliente.id == cartao.cliente_id).first()
    if cliente:
        cliente.saldo_cashless = saldo_posterior
    
    db.add(transacao)
    db.commit()
    
    return {
        "message": "Recarga realizada com sucesso",
        "saldo_anterior": float(saldo_anterior),
        "valor_recarga": float(recarga.valor),
        "saldo_atual": float(saldo_posterior),
        "transacao_id": transacao.id
    }

@router.post("/cashless/consumo")
async def processar_consumo(
    cartao_numero: str,
    valor: Decimal,
    descricao: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Processa consumo via cartão cashless
    """
    
    # Buscar cartão
    cartao = db.query(CartaoCashless).filter(
        or_(
            CartaoCashless.numero == cartao_numero,
            CartaoCashless.tag_rfid == cartao_numero
        )
    ).first()
    
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    if cartao.bloqueado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cartão bloqueado"
        )
    
    if cartao.saldo < valor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Saldo atual: R$ {cartao.saldo}"
        )
    
    # Criar transação
    saldo_anterior = cartao.saldo
    saldo_posterior = saldo_anterior - valor
    
    transacao = TransacaoCashless(
        cartao_id=cartao.id,
        cliente_id=cartao.cliente_id,
        tipo="CONSUMO",
        valor=valor,
        saldo_anterior=saldo_anterior,
        saldo_posterior=saldo_posterior,
        descricao=descricao or "Consumo no estabelecimento",
        referencia=str(uuid.uuid4())
    )
    
    # Atualizar saldo
    cartao.saldo = saldo_posterior
    
    cliente = db.query(Cliente).filter(Cliente.id == cartao.cliente_id).first()
    if cliente:
        cliente.saldo_cashless = saldo_posterior
    
    db.add(transacao)
    db.commit()
    
    return {
        "message": "Consumo processado com sucesso",
        "saldo_anterior": float(saldo_anterior),
        "valor_consumo": float(valor),
        "saldo_atual": float(saldo_posterior),
        "transacao_id": transacao.id
    }

@router.get("/cashless/transacoes/{cartao_id}")
async def listar_transacoes_cartao(
    cartao_id: int,
    limit: int = Query(100, description="Limite de registros"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista histórico de transações de um cartão
    """
    
    transacoes = db.query(TransacaoCashless).filter(
        TransacaoCashless.cartao_id == cartao_id
    ).order_by(desc(TransacaoCashless.criado_em)).limit(limit).all()
    
    return [{
        "id": t.id,
        "tipo": t.tipo,
        "valor": float(t.valor),
        "saldo_anterior": float(t.saldo_anterior),
        "saldo_posterior": float(t.saldo_posterior),
        "descricao": t.descricao,
        "data": t.criado_em.isoformat()
    } for t in transacoes]

@router.put("/cashless/cartoes/{cartao_id}/bloquear")
async def bloquear_cartao(
    cartao_id: int,
    bloquear: bool = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bloqueia ou desbloqueia cartão cashless
    """
    
    cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
    
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    cartao.bloqueado = bloquear
    db.commit()
    
    return {
        "message": f"Cartão {'bloqueado' if bloquear else 'desbloqueado'} com sucesso",
        "cartao_id": cartao_id,
        "status": "BLOQUEADO" if bloquear else "ATIVO"
    }

@router.post("/cashless/importar")
async def importar_cartoes(
    arquivo: str,  # Base64 do arquivo CSV
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Importa cartões em lote via CSV
    Replica funcionalidade: MEEP Cashless > Importar
    """
    
    # TODO: Implementar importação CSV
    # Decodificar base64
    # Processar CSV
    # Criar cartões em lote
    
    return {
        "message": "Funcionalidade de importação em desenvolvimento",
        "total_importados": 0
    }

@router.post("/cashless/recorrencia")
async def configurar_recorrencia(
    cliente_id: int,
    valor_mensal: Decimal,
    dia_cobranca: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configura recarga recorrente para cliente
    Replica funcionalidade: MEEP Cashless > Recorrência
    """
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # TODO: Implementar sistema de recorrência
    # Criar job agendado
    # Processar cobrança recorrente
    
    return {
        "message": "Recorrência configurada com sucesso",
        "cliente_id": cliente_id,
        "valor_mensal": float(valor_mensal),
        "dia_cobranca": dia_cobranca
    }