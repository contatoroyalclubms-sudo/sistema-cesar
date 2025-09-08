"""
Router para gerenciamento do programa de fidelidade
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from decimal import Decimal

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    ProgramaFidelidade, ProgramaFidelidadeCreate, ProgramaFidelidadeUpdate,
    NivelFidelidade, NivelFidelidadeCreate,
    ParticipanteFidelidade, ParticipanteFidelidadeCreate,
    MovimentacaoPontos, MovimentacaoPontosCreate
)

router = APIRouter(
    prefix="/api/fidelidade",
    tags=["fidelidade"]
)

# ====== PROGRAMAS DE FIDELIDADE ======

@router.get("/programas", response_model=List[ProgramaFidelidade])
def listar_programas(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os programas de fidelidade"""
    query = db.query(models.ProgramaFidelidade)
    
    if ativo is not None:
        query = query.filter(models.ProgramaFidelidade.ativo == ativo)
    
    programas = query.offset(skip).limit(limit).all()
    
    # Adicionar contagem de participantes
    for programa in programas:
        programa.total_participantes = db.query(models.ParticipanteFidelidade).filter(
            models.ParticipanteFidelidade.programa_id == programa.id
        ).count()
    
    return programas

@router.get("/programas/{programa_id}", response_model=ProgramaFidelidade)
def obter_programa(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém um programa específico"""
    programa = db.query(models.ProgramaFidelidade).filter(
        models.ProgramaFidelidade.id == programa_id
    ).first()
    
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    programa.total_participantes = db.query(models.ParticipanteFidelidade).filter(
        models.ParticipanteFidelidade.programa_id == programa.id
    ).count()
    
    return programa

@router.post("/programas", response_model=ProgramaFidelidade)
def criar_programa(
    programa: ProgramaFidelidadeCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo programa de fidelidade"""
    db_programa = models.ProgramaFidelidade(**programa.model_dump())
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    
    # Criar níveis padrão se for programa de níveis
    if programa.tipo_programa == 'niveis':
        niveis_padrao = [
            {"nome": "Bronze", "pontos_minimos": 0, "pontos_maximos": 999, "cor": "#CD7F32", "ordem": 1},
            {"nome": "Prata", "pontos_minimos": 1000, "pontos_maximos": 4999, "cor": "#C0C0C0", "ordem": 2},
            {"nome": "Ouro", "pontos_minimos": 5000, "pontos_maximos": None, "cor": "#FFD700", "ordem": 3}
        ]
        
        for nivel_data in niveis_padrao:
            nivel = models.NivelFidelidade(
                programa_id=db_programa.id,
                **nivel_data
            )
            db.add(nivel)
        
        db.commit()
    
    db_programa.total_participantes = 0
    return db_programa

@router.put("/programas/{programa_id}", response_model=ProgramaFidelidade)
def atualizar_programa(
    programa_id: int,
    programa_update: ProgramaFidelidadeUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um programa existente"""
    programa = db.query(models.ProgramaFidelidade).filter(
        models.ProgramaFidelidade.id == programa_id
    ).first()
    
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    update_data = programa_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(programa, key, value)
    
    db.commit()
    db.refresh(programa)
    
    programa.total_participantes = db.query(models.ParticipanteFidelidade).filter(
        models.ParticipanteFidelidade.programa_id == programa.id
    ).count()
    
    return programa

# ====== NÍVEIS DE FIDELIDADE ======

@router.get("/programas/{programa_id}/niveis", response_model=List[NivelFidelidade])
def listar_niveis(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os níveis de um programa"""
    niveis = db.query(models.NivelFidelidade).filter(
        models.NivelFidelidade.programa_id == programa_id
    ).order_by(models.NivelFidelidade.ordem).all()
    
    return niveis

@router.post("/programas/{programa_id}/niveis", response_model=NivelFidelidade)
def criar_nivel(
    programa_id: int,
    nivel: NivelFidelidadeCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo nível de fidelidade"""
    # Verificar se o programa existe
    programa = db.query(models.ProgramaFidelidade).filter(
        models.ProgramaFidelidade.id == programa_id
    ).first()
    
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    # Converter benefícios para JSON string se necessário
    beneficios = None
    if nivel.beneficios:
        import json
        beneficios = json.dumps(nivel.beneficios)
    
    db_nivel = models.NivelFidelidade(
        programa_id=programa_id,
        **nivel.model_dump(exclude={'beneficios', 'programa_id'}),
        beneficios=beneficios
    )
    
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    
    return db_nivel

@router.put("/niveis/{nivel_id}", response_model=NivelFidelidade)
def atualizar_nivel(
    nivel_id: int,
    nivel_update: dict,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um nível existente"""
    nivel = db.query(models.NivelFidelidade).filter(
        models.NivelFidelidade.id == nivel_id
    ).first()
    
    if not nivel:
        raise HTTPException(status_code=404, detail="Nível não encontrado")
    
    # Converter benefícios para JSON string se necessário
    if 'beneficios' in nivel_update and nivel_update['beneficios']:
        import json
        nivel_update['beneficios'] = json.dumps(nivel_update['beneficios'])
    
    for key, value in nivel_update.items():
        setattr(nivel, key, value)
    
    db.commit()
    db.refresh(nivel)
    
    return nivel

# ====== PARTICIPANTES ======

@router.post("/participar", response_model=ParticipanteFidelidade)
def aderir_programa(
    participacao: ParticipanteFidelidadeCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Adiciona um cliente ao programa de fidelidade"""
    # Verificar se o programa existe e está ativo
    programa = db.query(models.ProgramaFidelidade).filter(
        models.ProgramaFidelidade.id == participacao.programa_id,
        models.ProgramaFidelidade.ativo == True
    ).first()
    
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado ou inativo")
    
    # Verificar se o cliente existe
    cliente = db.query(models.ClienteEvento).filter(
        models.ClienteEvento.id == participacao.cliente_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar se já é participante
    participante_existente = db.query(models.ParticipanteFidelidade).filter(
        models.ParticipanteFidelidade.programa_id == participacao.programa_id,
        models.ParticipanteFidelidade.cliente_id == participacao.cliente_id
    ).first()
    
    if participante_existente:
        raise HTTPException(status_code=400, detail="Cliente já é participante deste programa")
    
    # Se for programa de níveis, definir nível inicial
    nivel_inicial_id = None
    if programa.tipo_programa == 'niveis':
        nivel_inicial = db.query(models.NivelFidelidade).filter(
            models.NivelFidelidade.programa_id == programa.id,
            models.NivelFidelidade.pontos_minimos == 0
        ).first()
        
        if nivel_inicial:
            nivel_inicial_id = nivel_inicial.id
    
    db_participante = models.ParticipanteFidelidade(
        **participacao.model_dump(),
        nivel_atual_id=nivel_inicial_id
    )
    
    db.add(db_participante)
    db.commit()
    db.refresh(db_participante)
    
    # Adicionar informação do nível
    if nivel_inicial_id:
        db_participante.nivel_atual = db.query(models.NivelFidelidade).filter(
            models.NivelFidelidade.id == nivel_inicial_id
        ).first()
    
    return db_participante

@router.get("/participante/{cliente_id}", response_model=List[ParticipanteFidelidade])
def obter_participacoes_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém todas as participações em programas de um cliente"""
    participacoes = db.query(models.ParticipanteFidelidade).filter(
        models.ParticipanteFidelidade.cliente_id == cliente_id
    ).all()
    
    # Adicionar informações do nível
    for participacao in participacoes:
        if participacao.nivel_atual_id:
            participacao.nivel_atual = db.query(models.NivelFidelidade).filter(
                models.NivelFidelidade.id == participacao.nivel_atual_id
            ).first()
    
    return participacoes

# ====== MOVIMENTAÇÃO DE PONTOS ======

@router.post("/pontos/adicionar", response_model=MovimentacaoPontos)
def adicionar_pontos(
    movimentacao: MovimentacaoPontosCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Adiciona pontos a um participante"""
    # Verificar se o participante existe
    participante = db.query(models.ParticipanteFidelidade).filter(
        models.ParticipanteFidelidade.id == movimentacao.participante_id
    ).first()
    
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    
    # Validar tipo de movimentação
    if movimentacao.tipo not in ['credito', 'debito', 'expiracao']:
        raise HTTPException(status_code=400, detail="Tipo de movimentação inválido")
    
    # Para débito, verificar saldo disponível
    if movimentacao.tipo == 'debito' and participante.pontos_disponiveis < movimentacao.pontos:
        raise HTTPException(status_code=400, detail="Pontos insuficientes")
    
    # Criar movimentação
    db_movimentacao = models.MovimentacaoPontos(**movimentacao.model_dump())
    db.add(db_movimentacao)
    
    # Atualizar pontos do participante
    if movimentacao.tipo == 'credito':
        participante.pontos_totais += movimentacao.pontos
        participante.pontos_disponiveis += movimentacao.pontos
    elif movimentacao.tipo == 'debito':
        participante.pontos_disponiveis -= movimentacao.pontos
    elif movimentacao.tipo == 'expiracao':
        participante.pontos_disponiveis -= movimentacao.pontos
    
    participante.data_ultima_movimentacao = datetime.now()
    
    # Verificar mudança de nível (se aplicável)
    programa = db.query(models.ProgramaFidelidade).filter(
        models.ProgramaFidelidade.id == participante.programa_id
    ).first()
    
    if programa and programa.tipo_programa == 'niveis':
        novo_nivel = db.query(models.NivelFidelidade).filter(
            models.NivelFidelidade.programa_id == programa.id,
            models.NivelFidelidade.pontos_minimos <= participante.pontos_totais,
            or_(
                models.NivelFidelidade.pontos_maximos.is_(None),
                models.NivelFidelidade.pontos_maximos >= participante.pontos_totais
            )
        ).order_by(models.NivelFidelidade.pontos_minimos.desc()).first()
        
        if novo_nivel and novo_nivel.id != participante.nivel_atual_id:
            participante.nivel_atual_id = novo_nivel.id
    
    db.commit()
    db.refresh(db_movimentacao)
    
    return db_movimentacao

@router.get("/pontos/historico/{participante_id}", response_model=List[MovimentacaoPontos])
def obter_historico_pontos(
    participante_id: int,
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém o histórico de movimentações de pontos"""
    query = db.query(models.MovimentacaoPontos).filter(
        models.MovimentacaoPontos.participante_id == participante_id
    )
    
    if tipo:
        query = query.filter(models.MovimentacaoPontos.tipo == tipo)
    
    movimentacoes = query.order_by(
        models.MovimentacaoPontos.data_movimentacao.desc()
    ).offset(skip).limit(limit).all()
    
    return movimentacoes

@router.get("/estatisticas/{programa_id}")
def obter_estatisticas_programa(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém estatísticas do programa de fidelidade"""
    programa = db.query(models.ProgramaFidelidade).filter(
        models.ProgramaFidelidade.id == programa_id
    ).first()
    
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    # Estatísticas gerais
    total_participantes = db.query(models.ParticipanteFidelidade).filter(
        models.ParticipanteFidelidade.programa_id == programa_id
    ).count()
    
    # Total de pontos distribuídos
    pontos_distribuidos = db.query(
        func.sum(models.MovimentacaoPontos.pontos)
    ).join(
        models.ParticipanteFidelidade
    ).filter(
        models.ParticipanteFidelidade.programa_id == programa_id,
        models.MovimentacaoPontos.tipo == 'credito'
    ).scalar() or 0
    
    # Total de pontos resgatados
    pontos_resgatados = db.query(
        func.sum(models.MovimentacaoPontos.pontos)
    ).join(
        models.ParticipanteFidelidade
    ).filter(
        models.ParticipanteFidelidade.programa_id == programa_id,
        models.MovimentacaoPontos.tipo == 'debito'
    ).scalar() or 0
    
    # Distribuição por nível (se aplicável)
    distribuicao_niveis = {}
    if programa.tipo_programa == 'niveis':
        niveis = db.query(models.NivelFidelidade).filter(
            models.NivelFidelidade.programa_id == programa_id
        ).all()
        
        for nivel in niveis:
            count = db.query(models.ParticipanteFidelidade).filter(
                models.ParticipanteFidelidade.programa_id == programa_id,
                models.ParticipanteFidelidade.nivel_atual_id == nivel.id
            ).count()
            distribuicao_niveis[nivel.nome] = count
    
    # Participantes mais ativos (top 10)
    top_participantes = db.query(
        models.ParticipanteFidelidade,
        models.ClienteEvento.nome_completo
    ).join(
        models.ClienteEvento
    ).filter(
        models.ParticipanteFidelidade.programa_id == programa_id
    ).order_by(
        models.ParticipanteFidelidade.pontos_totais.desc()
    ).limit(10).all()
    
    return {
        "programa": {
            "id": programa.id,
            "nome": programa.nome,
            "tipo": programa.tipo_programa,
            "ativo": programa.ativo
        },
        "estatisticas": {
            "total_participantes": total_participantes,
            "pontos_distribuidos": pontos_distribuidos,
            "pontos_resgatados": pontos_resgatados,
            "pontos_em_circulacao": pontos_distribuidos - pontos_resgatados,
            "distribuicao_niveis": distribuicao_niveis,
            "top_participantes": [
                {
                    "nome": nome,
                    "pontos_totais": part.pontos_totais,
                    "pontos_disponiveis": part.pontos_disponiveis
                }
                for part, nome in top_participantes
            ]
        }
    }