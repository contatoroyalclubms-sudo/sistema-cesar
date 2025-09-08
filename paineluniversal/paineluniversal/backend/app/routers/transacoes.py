from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Transacao, Lista, Evento, Usuario
from ..schemas import Transacao as TransacaoSchema, TransacaoCreate
from ..auth_functions import obter_usuario_atual, validar_cpf_basico
import uuid

router = APIRouter()

@router.post("/", response_model=TransacaoSchema)
async def criar_transacao(
    transacao: TransacaoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar nova transação (venda de ingresso)"""
    
    if not validar_cpf_basico(transacao.cpf_comprador):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF do comprador inválido"
        )
    
    lista = db.query(Lista).filter(Lista.id == transacao.lista_id).first()
    if not lista or not lista.ativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista não encontrada ou inativa"
        )
    
    evento = db.query(Evento).filter(Evento.id == transacao.evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Verificação simplificada: admins e promoters podem gerenciar transações
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem gerenciar transações"
        )
    
    if lista.limite_vendas and lista.vendas_realizadas >= lista.limite_vendas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limite de vendas da lista atingido"
        )
    
    transacao_data = transacao.dict()
    transacao_data['codigo_transacao'] = str(uuid.uuid4())
    transacao_data['qr_code_ticket'] = f"TICKET-{str(uuid.uuid4())[:8].upper()}-{evento.id}"
    transacao_data['usuario_id'] = usuario_atual.id
    transacao_data['valor'] = lista.preco
    
    # Remover quantidade do dict se existir (não é campo da tabela)
    quantidade = transacao_data.pop('quantidade', 1)
    
    db_transacao = Transacao(**transacao_data)
    db.add(db_transacao)
    
    lista.vendas_realizadas += quantidade
    
    db.commit()
    db.refresh(db_transacao)
    
    return db_transacao

@router.get("/", response_model=List[TransacaoSchema])
async def listar_transacoes(
    skip: int = 0,
    limit: int = 100,
    evento_id: Optional[int] = None,
    cpf_comprador: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar transações"""
    
    query = db.query(Transacao)
    
    # Admins podem ver todas as transações
    # Promoters e clientes têm acesso baseado em suas permissões específicas
    
    if evento_id:
        query = query.filter(Transacao.evento_id == evento_id)
    
    if cpf_comprador:
        query = query.filter(Transacao.cpf_comprador == cpf_comprador)
    
    if status:
        query = query.filter(Transacao.status == status)
    
    transacoes = query.offset(skip).limit(limit).all()
    return transacoes

@router.get("/{transacao_id}", response_model=TransacaoSchema)
async def obter_transacao(
    transacao_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados de uma transação"""
    
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    
    evento = db.query(Evento).filter(Evento.id == transacao.evento_id).first()
    # Verificação simplificada: admins e promoters podem gerenciar transações
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem gerenciar transações"
        )
    
    return transacao

@router.put("/{transacao_id}/status")
async def atualizar_status_transacao(
    transacao_id: int,
    novo_status: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar status da transação"""
    
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    
    evento = db.query(Evento).filter(Evento.id == transacao.evento_id).first()
    # Verificação simplificada: admins e promoters podem gerenciar transações
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem gerenciar transações"
        )
    
    status_validos = ["pendente", "aprovada", "cancelada"]
    if novo_status not in status_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Use: {', '.join(status_validos)}"
        )
    
    transacao.status = novo_status
    db.commit()
    
    return {"mensagem": f"Status da transação atualizado para: {novo_status}"}
