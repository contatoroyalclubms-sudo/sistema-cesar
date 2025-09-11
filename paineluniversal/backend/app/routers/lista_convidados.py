from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import secrets
from ..database import get_db
from ..models import ListaConvidados, ConvidadoLista, Evento, Usuario
from ..auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/eventos/{evento_id}/listas", tags=["Lista de Convidados"])

# Schemas
class ListaConvidadosCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: str = "geral"  # geral, promoter, aniversariante, vip
    promoter_responsavel_id: Optional[int] = None
    promoter_responsavel_nome: Optional[str] = None
    quantidade_maxima: int = 100
    data_fechamento: Optional[datetime] = None
    preco_entrada: Optional[float] = 0.0
    desconto_percentual: Optional[float] = 0.0
    exibir_no_app: bool = True
    ativo: bool = True

class ConvidadoCreate(BaseModel):
    nome: str
    cpf: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    tipo_ingresso: str = "free"  # free, vip, pagante

class ListaConvidadosResponse(BaseModel):
    id: int
    evento_id: int
    nome: str
    descricao: Optional[str]
    tipo: str
    promoter_responsavel_id: Optional[int]
    promoter_responsavel_nome: Optional[str]
    quantidade_maxima: int
    quantidade_atual: int
    link_gerado: str
    codigo_acesso: str
    data_fechamento: Optional[datetime]
    preco_entrada: Optional[float]
    desconto_percentual: Optional[float]
    exibir_no_app: bool
    ativo: bool
    vendas: int
    checkins: int
    data_criacao: datetime

@router.get("/", response_model=List[ListaConvidadosResponse])
def listar_listas_convidados(
    evento_id: int,
    tipo: Optional[str] = None,
    promoter_id: Optional[int] = None,
    ativo: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas as listas de convidados de um evento"""
    # Verificar se o evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    query = db.query(ListaConvidados).filter(ListaConvidados.evento_id == evento_id)
    
    if tipo:
        query = query.filter(ListaConvidados.tipo == tipo)
    if promoter_id:
        query = query.filter(ListaConvidados.promoter_responsavel_id == promoter_id)
    if ativo is not None:
        query = query.filter(ListaConvidados.ativo == ativo)
    
    listas = query.all()
    
    # Adicionar contagens
    response = []
    for lista in listas:
        quantidade_atual = db.query(func.count(ConvidadoLista.id)).filter(
            ConvidadoLista.lista_id == lista.id
        ).scalar() or 0
        
        vendas = db.query(func.count(ConvidadoLista.id)).filter(
            ConvidadoLista.lista_id == lista.id,
            ConvidadoLista.pagamento_confirmado == True
        ).scalar() or 0
        
        checkins = db.query(func.count(ConvidadoLista.id)).filter(
            ConvidadoLista.lista_id == lista.id,
            ConvidadoLista.checkin_realizado == True
        ).scalar() or 0
        
        response.append({
            **lista.__dict__,
            "quantidade_atual": quantidade_atual,
            "vendas": vendas,
            "checkins": checkins
        })
    
    return response

@router.post("/", response_model=ListaConvidadosResponse)
def criar_lista_convidados(
    evento_id: int,
    lista_data: ListaConvidadosCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar uma nova lista de convidados"""
    # Verificar se o evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Gerar código único para a lista
    codigo_acesso = secrets.token_urlsafe(8)
    
    # Criar link único
    base_url = "https://sistema.meep.com.br"  # TODO: Pegar do env
    link_gerado = f"{base_url}/convite/{evento_id}/{codigo_acesso}"
    
    # Criar a lista
    nova_lista = ListaConvidados(
        evento_id=evento_id,
        nome=lista_data.nome,
        descricao=lista_data.descricao,
        tipo=lista_data.tipo,
        promoter_responsavel_id=lista_data.promoter_responsavel_id,
        promoter_responsavel_nome=lista_data.promoter_responsavel_nome,
        quantidade_maxima=lista_data.quantidade_maxima,
        data_fechamento=lista_data.data_fechamento,
        preco_entrada=lista_data.preco_entrada,
        desconto_percentual=lista_data.desconto_percentual,
        link_gerado=link_gerado,
        codigo_acesso=codigo_acesso,
        exibir_no_app=lista_data.exibir_no_app,
        ativo=lista_data.ativo,
        criado_por_id=current_user.id,
        data_criacao=datetime.now()
    )
    
    db.add(nova_lista)
    db.commit()
    db.refresh(nova_lista)
    
    # Retornar com contagens zeradas
    return {
        **nova_lista.__dict__,
        "quantidade_atual": 0,
        "vendas": 0,
        "checkins": 0
    }

@router.get("/{lista_id}", response_model=ListaConvidadosResponse)
def obter_lista_convidados(
    evento_id: int,
    lista_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter detalhes de uma lista específica"""
    lista = db.query(ListaConvidados).filter(
        ListaConvidados.id == lista_id,
        ListaConvidados.evento_id == evento_id
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Adicionar contagens
    quantidade_atual = db.query(func.count(ConvidadoLista.id)).filter(
        ConvidadoLista.lista_id == lista.id
    ).scalar() or 0
    
    vendas = db.query(func.count(ConvidadoLista.id)).filter(
        ConvidadoLista.lista_id == lista.id,
        ConvidadoLista.pagamento_confirmado == True
    ).scalar() or 0
    
    checkins = db.query(func.count(ConvidadoLista.id)).filter(
        ConvidadoLista.lista_id == lista.id,
        ConvidadoLista.checkin_realizado == True
    ).scalar() or 0
    
    return {
        **lista.__dict__,
        "quantidade_atual": quantidade_atual,
        "vendas": vendas,
        "checkins": checkins
    }

@router.put("/{lista_id}")
def atualizar_lista_convidados(
    evento_id: int,
    lista_id: int,
    lista_data: ListaConvidadosCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar uma lista de convidados"""
    lista = db.query(ListaConvidados).filter(
        ListaConvidados.id == lista_id,
        ListaConvidados.evento_id == evento_id
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Atualizar campos
    for field, value in lista_data.dict(exclude_unset=True).items():
        setattr(lista, field, value)
    
    lista.data_atualizacao = datetime.now()
    db.commit()
    
    return {"message": "Lista atualizada com sucesso"}

@router.delete("/{lista_id}")
def excluir_lista_convidados(
    evento_id: int,
    lista_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Excluir uma lista de convidados"""
    lista = db.query(ListaConvidados).filter(
        ListaConvidados.id == lista_id,
        ListaConvidados.evento_id == evento_id
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Verificar se há convidados na lista
    convidados_count = db.query(func.count(ConvidadoLista.id)).filter(
        ConvidadoLista.lista_id == lista_id
    ).scalar()
    
    if convidados_count > 0:
        # Soft delete - apenas desativar
        lista.ativo = False
        db.commit()
        return {"message": "Lista desativada (possui convidados)"}
    else:
        # Hard delete - remover completamente
        db.delete(lista)
        db.commit()
        return {"message": "Lista excluída com sucesso"}

# === ENDPOINTS PARA CONVIDADOS NA LISTA ===

@router.get("/{lista_id}/convidados")
def listar_convidados_lista(
    evento_id: int,
    lista_id: int,
    checkin_realizado: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todos os convidados de uma lista"""
    # Verificar se a lista existe
    lista = db.query(ListaConvidados).filter(
        ListaConvidados.id == lista_id,
        ListaConvidados.evento_id == evento_id
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    query = db.query(ConvidadoLista).filter(ConvidadoLista.lista_id == lista_id)
    
    if checkin_realizado is not None:
        query = query.filter(ConvidadoLista.checkin_realizado == checkin_realizado)
    
    convidados = query.all()
    return convidados

@router.post("/{lista_id}/convidados")
def adicionar_convidado_lista(
    evento_id: int,
    lista_id: int,
    convidado_data: ConvidadoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Adicionar um convidado à lista"""
    # Verificar se a lista existe
    lista = db.query(ListaConvidados).filter(
        ListaConvidados.id == lista_id,
        ListaConvidados.evento_id == evento_id
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Verificar limite da lista
    quantidade_atual = db.query(func.count(ConvidadoLista.id)).filter(
        ConvidadoLista.lista_id == lista_id
    ).scalar() or 0
    
    if quantidade_atual >= lista.quantidade_maxima:
        raise HTTPException(status_code=400, detail="Lista atingiu o limite máximo")
    
    # Verificar se o CPF já está na lista
    convidado_existente = db.query(ConvidadoLista).filter(
        ConvidadoLista.lista_id == lista_id,
        ConvidadoLista.cpf == convidado_data.cpf
    ).first()
    
    if convidado_existente:
        raise HTTPException(status_code=400, detail="CPF já está nesta lista")
    
    # Criar o convidado
    novo_convidado = ConvidadoLista(
        lista_id=lista_id,
        nome=convidado_data.nome,
        cpf=convidado_data.cpf,
        telefone=convidado_data.telefone,
        email=convidado_data.email,
        tipo_ingresso=convidado_data.tipo_ingresso,
        data_adicao=datetime.now(),
        adicionado_por_id=current_user.id
    )
    
    db.add(novo_convidado)
    db.commit()
    
    return {"message": "Convidado adicionado com sucesso", "id": novo_convidado.id}

@router.delete("/{lista_id}/convidados/{convidado_id}")
def remover_convidado_lista(
    evento_id: int,
    lista_id: int,
    convidado_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remover um convidado da lista"""
    convidado = db.query(ConvidadoLista).filter(
        ConvidadoLista.id == convidado_id,
        ConvidadoLista.lista_id == lista_id
    ).first()
    
    if not convidado:
        raise HTTPException(status_code=404, detail="Convidado não encontrado")
    
    if convidado.checkin_realizado:
        raise HTTPException(status_code=400, detail="Não é possível remover convidado com check-in realizado")
    
    db.delete(convidado)
    db.commit()
    
    return {"message": "Convidado removido com sucesso"}

# === ENDPOINT PÚBLICO PARA CONVITE ===

@router.get("/convite/{codigo_acesso}")
def obter_dados_convite(
    evento_id: int,
    codigo_acesso: str,
    db: Session = Depends(get_db)
):
    """Endpoint público para obter dados do convite via link"""
    lista = db.query(ListaConvidados).filter(
        ListaConvidados.evento_id == evento_id,
        ListaConvidados.codigo_acesso == codigo_acesso,
        ListaConvidados.ativo == True
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Convite inválido ou expirado")
    
    # Verificar data de fechamento
    if lista.data_fechamento and datetime.now() > lista.data_fechamento:
        raise HTTPException(status_code=400, detail="Lista fechada")
    
    # Verificar limite
    quantidade_atual = db.query(func.count(ConvidadoLista.id)).filter(
        ConvidadoLista.lista_id == lista.id
    ).scalar() or 0
    
    if quantidade_atual >= lista.quantidade_maxima:
        raise HTTPException(status_code=400, detail="Lista cheia")
    
    # Obter dados do evento
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    
    return {
        "evento": {
            "id": evento.id,
            "nome": evento.nome,
            "data": evento.data_inicio_evento,
            "local": evento.local,
            "descricao": evento.descricao
        },
        "lista": {
            "id": lista.id,
            "nome": lista.nome,
            "descricao": lista.descricao,
            "tipo": lista.tipo,
            "preco_entrada": lista.preco_entrada,
            "desconto_percentual": lista.desconto_percentual,
            "vagas_disponiveis": lista.quantidade_maxima - quantidade_atual
        }
    }

@router.post("/convite/{codigo_acesso}/confirmar")
def confirmar_presenca_convite(
    evento_id: int,
    codigo_acesso: str,
    convidado_data: ConvidadoCreate,
    db: Session = Depends(get_db)
):
    """Endpoint público para confirmar presença via link de convite"""
    # Verificar lista
    lista = db.query(ListaConvidados).filter(
        ListaConvidados.evento_id == evento_id,
        ListaConvidados.codigo_acesso == codigo_acesso,
        ListaConvidados.ativo == True
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Convite inválido")
    
    # Verificações de limite e data
    if lista.data_fechamento and datetime.now() > lista.data_fechamento:
        raise HTTPException(status_code=400, detail="Lista já foi fechada")
    
    quantidade_atual = db.query(func.count(ConvidadoLista.id)).filter(
        ConvidadoLista.lista_id == lista.id
    ).scalar() or 0
    
    if quantidade_atual >= lista.quantidade_maxima:
        raise HTTPException(status_code=400, detail="Lista cheia")
    
    # Verificar CPF duplicado
    convidado_existente = db.query(ConvidadoLista).filter(
        ConvidadoLista.lista_id == lista.id,
        ConvidadoLista.cpf == convidado_data.cpf
    ).first()
    
    if convidado_existente:
        raise HTTPException(status_code=400, detail="Você já está nesta lista")
    
    # Adicionar convidado
    novo_convidado = ConvidadoLista(
        lista_id=lista.id,
        nome=convidado_data.nome,
        cpf=convidado_data.cpf,
        telefone=convidado_data.telefone,
        email=convidado_data.email,
        tipo_ingresso=convidado_data.tipo_ingresso or lista.tipo,
        data_adicao=datetime.now()
    )
    
    db.add(novo_convidado)
    db.commit()
    
    return {
        "message": "Presença confirmada com sucesso!",
        "codigo_confirmacao": f"CONF-{novo_convidado.id:06d}",
        "detalhes": {
            "evento": db.query(Evento).filter(Evento.id == evento_id).first().nome,
            "lista": lista.nome,
            "tipo_ingresso": novo_convidado.tipo_ingresso
        }
    }