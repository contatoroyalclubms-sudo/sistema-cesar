from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
import json
import asyncio
import httpx
from enum import Enum

from ..database import get_db
from ..models_comunicacao import (
    CanalComunicacao, TemplateMensagem, ContatoComunicacao, CampanhaComunicacao,
    Mensagem, EventoNotificacao, FilaEnvio, MetricaComunicacao,
    TipoCanal, StatusCanal, TipoTemplate, StatusMensagem, TipoCampanha, 
    StatusCampanha, TipoEvento, PrioridadeMensagem,
    CONFIGURACOES_CANAIS_PADRAO, TEMPLATES_SISTEMA_PADRAO
)
from ..auth import get_current_user

router = APIRouter()

# === SCHEMAS DE REQUEST/RESPONSE ===

class CreateCanalRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: TipoCanal
    descricao: Optional[str] = None
    configuracoes: Dict[str, Any] = {}
    limite_diario: int = Field(default=1000, ge=1)
    limite_mensal: int = Field(default=30000, ge=1)
    tempo_throttle: int = Field(default=1, ge=0)

class UpdateCanalRequest(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None
    limite_diario: Optional[int] = Field(None, ge=1)
    limite_mensal: Optional[int] = Field(None, ge=1)
    tempo_throttle: Optional[int] = Field(None, ge=0)
    ativo: Optional[bool] = None

class CreateTemplateRequest(BaseModel):
    canal_id: int
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: TipoTemplate
    assunto: Optional[str] = Field(None, max_length=200)
    conteudo: str = Field(..., min_length=1)
    conteudo_html: Optional[str] = None
    variaveis: List[str] = []
    configuracoes: Dict[str, Any] = {}

class CreateContatoRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, regex=r'^\+?[1-9]\d{1,14}$')
    whatsapp: Optional[str] = Field(None, regex=r'^\+?[1-9]\d{1,14}$')
    cliente_id: Optional[int] = None
    dados_extras: Dict[str, Any] = {}
    aceita_marketing: bool = True
    aceita_promocional: bool = True
    aceita_whatsapp: bool = True
    aceita_email: bool = True
    aceita_sms: bool = False
    tags: List[str] = []

class CreateCampanhaRequest(BaseModel):
    template_id: int
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    tipo: TipoCampanha = TipoCampanha.IMEDIATA
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    filtros_segmentacao: Dict[str, Any] = {}
    variante_a_template_id: Optional[int] = None
    variante_b_template_id: Optional[int] = None
    percentual_variante_a: float = Field(default=50.0, ge=0, le=100)

class EnvioMensagemRequest(BaseModel):
    canal_id: int
    template_id: Optional[int] = None
    contato_id: Optional[int] = None
    destinatario: str = Field(..., min_length=1)
    nome_destinatario: Optional[str] = None
    assunto: Optional[str] = None
    conteudo: str = Field(..., min_length=1)
    conteudo_html: Optional[str] = None
    prioridade: PrioridadeMensagem = PrioridadeMensagem.NORMAL
    variaveis: Dict[str, Any] = {}
    agendado_para: Optional[datetime] = None

class CreateEventoRequest(BaseModel):
    template_id: int
    nome: str = Field(..., min_length=1, max_length=100)
    tipo_evento: TipoEvento
    descricao: Optional[str] = None
    condicoes: Dict[str, Any] = {}
    delay_minutos: int = Field(default=0, ge=0)
    filtros: Dict[str, Any] = {}

class DashboardComunicacao(BaseModel):
    total_canais: int
    canais_ativos: int
    total_templates: int
    total_contatos: int
    total_campanhas: int
    campanhas_ativas: int
    mensagens_hoje: int
    mensagens_mes: int
    taxa_entrega_media: float
    taxa_abertura_media: float
    canais_por_tipo: Dict[str, int]
    mensagens_por_canal: Dict[str, int]
    atividade_recente: List[Dict[str, Any]]

# === UTILITÁRIOS ===

def processar_variaveis_template(conteudo: str, variaveis: Dict[str, Any]) -> str:
    """Processa variáveis no template usando formato {variavel}"""
    try:
        return conteudo.format(**variaveis)
    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Variável {e} não encontrada no dicionário de variáveis"
        )

async def validar_configuracao_canal(tipo: TipoCanal, configuracoes: Dict[str, Any]) -> bool:
    """Valida configurações específicas do canal"""
    config_padrao = CONFIGURACOES_CANAIS_PADRAO.get(tipo, {})
    
    if tipo == TipoCanal.WHATSAPP:
        required_fields = ["access_token", "phone_number_id"]
        return all(configuracoes.get(field) for field in required_fields)
    elif tipo == TipoCanal.EMAIL:
        return configuracoes.get("api_key") or (
            configuracoes.get("smtp_host") and configuracoes.get("smtp_username")
        )
    elif tipo == TipoCanal.SMS:
        return configuracoes.get("api_key") and configuracoes.get("account_sid")
    
    return True

# === ENDPOINTS DE CANAIS ===

@router.post("/canais", response_model=Dict[str, Any])
async def criar_canal(
    request: CreateCanalRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo canal de comunicação"""
    
    # Validar configurações
    if not await validar_configuracao_canal(request.tipo, request.configuracoes):
        raise HTTPException(
            status_code=400,
            detail="Configurações do canal inválidas ou incompletas"
        )
    
    # Verificar se já existe canal do mesmo tipo
    canal_existente = db.query(CanalComunicacao).filter(
        and_(
            CanalComunicacao.empresa_id == current_user.empresa_id,
            CanalComunicacao.tipo == request.tipo
        )
    ).first()
    
    if canal_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe um canal do tipo {request.tipo.value} para esta empresa"
        )
    
    # Mesclar com configurações padrão
    config_final = CONFIGURACOES_CANAIS_PADRAO.get(request.tipo, {}).copy()
    config_final.update(request.configuracoes)
    
    canal = CanalComunicacao(
        empresa_id=current_user.empresa_id,
        nome=request.nome,
        tipo=request.tipo,
        descricao=request.descricao,
        configuracoes=config_final,
        limite_diario=request.limite_diario,
        limite_mensal=request.limite_mensal,
        tempo_throttle=request.tempo_throttle,
        status=StatusCanal.CONFIGURANDO
    )
    
    db.add(canal)
    db.commit()
    db.refresh(canal)
    
    return {
        "id": canal.id,
        "message": "Canal criado com sucesso",
        "canal": {
            "id": canal.id,
            "nome": canal.nome,
            "tipo": canal.tipo.value,
            "status": canal.status.value
        }
    }

@router.get("/canais", response_model=List[Dict[str, Any]])
async def listar_canais(
    ativo: Optional[bool] = None,
    tipo: Optional[TipoCanal] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar canais de comunicação"""
    
    query = db.query(CanalComunicacao).filter(
        CanalComunicacao.empresa_id == current_user.empresa_id
    )
    
    if ativo is not None:
        query = query.filter(CanalComunicacao.ativo == ativo)
    
    if tipo is not None:
        query = query.filter(CanalComunicacao.tipo == tipo)
    
    canais = query.order_by(CanalComunicacao.criado_em.desc()).all()
    
    return [
        {
            "id": canal.id,
            "nome": canal.nome,
            "tipo": canal.tipo.value,
            "descricao": canal.descricao,
            "status": canal.status.value,
            "ativo": canal.ativo,
            "limite_diario": canal.limite_diario,
            "limite_mensal": canal.limite_mensal,
            "total_enviados": canal.total_enviados,
            "total_entregues": canal.total_entregues,
            "total_erros": canal.total_erros,
            "taxa_entrega": round((canal.total_entregues / max(canal.total_enviados, 1)) * 100, 2),
            "ultimo_teste": canal.ultimo_teste.isoformat() if canal.ultimo_teste else None,
            "criado_em": canal.criado_em.isoformat()
        }
        for canal in canais
    ]

@router.get("/canais/{canal_id}", response_model=Dict[str, Any])
async def obter_canal(
    canal_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes do canal"""
    
    canal = db.query(CanalComunicacao).filter(
        and_(
            CanalComunicacao.id == canal_id,
            CanalComunicacao.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not canal:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Remover dados sensíveis das configurações
    configuracoes_safe = canal.configuracoes.copy()
    campos_sensíveis = ["api_key", "access_token", "smtp_password", "api_secret"]
    for campo in campos_sensíveis:
        if campo in configuracoes_safe:
            configuracoes_safe[campo] = "*" * 8
    
    return {
        "id": canal.id,
        "nome": canal.nome,
        "tipo": canal.tipo.value,
        "descricao": canal.descricao,
        "status": canal.status.value,
        "configuracoes": configuracoes_safe,
        "ativo": canal.ativo,
        "limite_diario": canal.limite_diario,
        "limite_mensal": canal.limite_mensal,
        "tempo_throttle": canal.tempo_throttle,
        "total_enviados": canal.total_enviados,
        "total_entregues": canal.total_entregues,
        "total_erros": canal.total_erros,
        "ultimo_teste": canal.ultimo_teste.isoformat() if canal.ultimo_teste else None,
        "ultimo_erro": canal.ultimo_erro,
        "criado_em": canal.criado_em.isoformat(),
        "atualizado_em": canal.atualizado_em.isoformat()
    }

@router.put("/canais/{canal_id}", response_model=Dict[str, Any])
async def atualizar_canal(
    canal_id: int,
    request: UpdateCanalRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar canal de comunicação"""
    
    canal = db.query(CanalComunicacao).filter(
        and_(
            CanalComunicacao.id == canal_id,
            CanalComunicacao.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not canal:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Atualizar campos
    if request.nome is not None:
        canal.nome = request.nome
    if request.descricao is not None:
        canal.descricao = request.descricao
    if request.configuracoes is not None:
        # Validar novas configurações
        config_final = canal.configuracoes.copy()
        config_final.update(request.configuracoes)
        if not await validar_configuracao_canal(canal.tipo, config_final):
            raise HTTPException(
                status_code=400,
                detail="Configurações inválidas"
            )
        canal.configuracoes = config_final
    if request.limite_diario is not None:
        canal.limite_diario = request.limite_diario
    if request.limite_mensal is not None:
        canal.limite_mensal = request.limite_mensal
    if request.tempo_throttle is not None:
        canal.tempo_throttle = request.tempo_throttle
    if request.ativo is not None:
        canal.ativo = request.ativo
    
    db.commit()
    db.refresh(canal)
    
    return {"message": "Canal atualizado com sucesso"}

@router.post("/canais/{canal_id}/testar", response_model=Dict[str, Any])
async def testar_canal(
    canal_id: int,
    destinatario_teste: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Testar configuração do canal"""
    
    canal = db.query(CanalComunicacao).filter(
        and_(
            CanalComunicacao.id == canal_id,
            CanalComunicacao.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not canal:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    try:
        sucesso = await _enviar_mensagem_teste(canal, destinatario_teste)
        
        canal.ultimo_teste = datetime.now()
        if sucesso:
            canal.status = StatusCanal.ATIVO
            canal.ultimo_erro = None
        else:
            canal.status = StatusCanal.ERRO
            canal.ultimo_erro = "Teste de envio falhou"
        
        db.commit()
        
        return {
            "sucesso": sucesso,
            "message": "Teste realizado com sucesso" if sucesso else "Teste falhou",
            "timestamp": canal.ultimo_teste.isoformat()
        }
        
    except Exception as e:
        canal.ultimo_erro = str(e)
        canal.status = StatusCanal.ERRO
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro no teste: {str(e)}"
        )

# === ENDPOINTS DE TEMPLATES ===

@router.post("/templates", response_model=Dict[str, Any])
async def criar_template(
    request: CreateTemplateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar template de mensagem"""
    
    # Verificar se canal existe
    canal = db.query(CanalComunicacao).filter(
        and_(
            CanalComunicacao.id == request.canal_id,
            CanalComunicacao.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not canal:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    template = TemplateMensagem(
        empresa_id=current_user.empresa_id,
        canal_id=request.canal_id,
        nome=request.nome,
        tipo=request.tipo,
        assunto=request.assunto,
        conteudo=request.conteudo,
        conteudo_html=request.conteudo_html,
        variaveis=request.variaveis,
        configuracoes=request.configuracoes
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {
        "id": template.id,
        "message": "Template criado com sucesso",
        "template": {
            "id": template.id,
            "nome": template.nome,
            "tipo": template.tipo.value,
            "canal": canal.nome
        }
    }

@router.get("/templates", response_model=List[Dict[str, Any]])
async def listar_templates(
    canal_id: Optional[int] = None,
    tipo: Optional[TipoTemplate] = None,
    ativo: Optional[bool] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar templates de mensagem"""
    
    query = db.query(TemplateMensagem).filter(
        TemplateMensagem.empresa_id == current_user.empresa_id
    )
    
    if canal_id is not None:
        query = query.filter(TemplateMensagem.canal_id == canal_id)
    if tipo is not None:
        query = query.filter(TemplateMensagem.tipo == tipo)
    if ativo is not None:
        query = query.filter(TemplateMensagem.ativo == ativo)
    
    templates = query.order_by(TemplateMensagem.criado_em.desc()).all()
    
    return [
        {
            "id": template.id,
            "nome": template.nome,
            "tipo": template.tipo.value,
            "canal_nome": template.canal.nome,
            "canal_tipo": template.canal.tipo.value,
            "assunto": template.assunto,
            "variaveis": template.variaveis,
            "total_usado": template.total_usado,
            "taxa_entrega": template.taxa_entrega,
            "taxa_abertura": template.taxa_abertura,
            "ativo": template.ativo,
            "criado_em": template.criado_em.isoformat()
        }
        for template in templates
    ]

# === ENDPOINTS DE CONTATOS ===

@router.post("/contatos", response_model=Dict[str, Any])
async def criar_contato(
    request: CreateContatoRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar contato para comunicação"""
    
    contato = ContatoComunicacao(
        empresa_id=current_user.empresa_id,
        cliente_id=request.cliente_id,
        nome=request.nome,
        email=request.email,
        telefone=request.telefone,
        whatsapp=request.whatsapp,
        dados_extras=request.dados_extras,
        aceita_marketing=request.aceita_marketing,
        aceita_promocional=request.aceita_promocional,
        aceita_whatsapp=request.aceita_whatsapp,
        aceita_email=request.aceita_email,
        aceita_sms=request.aceita_sms,
        tags=request.tags
    )
    
    db.add(contato)
    db.commit()
    db.refresh(contato)
    
    return {
        "id": contato.id,
        "message": "Contato criado com sucesso"
    }

@router.get("/contatos", response_model=List[Dict[str, Any]])
async def listar_contatos(
    ativo: Optional[bool] = None,
    aceita_marketing: Optional[bool] = None,
    tag: Optional[str] = None,
    busca: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar contatos"""
    
    query = db.query(ContatoComunicacao).filter(
        ContatoComunicacao.empresa_id == current_user.empresa_id
    )
    
    if ativo is not None:
        query = query.filter(ContatoComunicacao.ativo == ativo)
    if aceita_marketing is not None:
        query = query.filter(ContatoComunicacao.aceita_marketing == aceita_marketing)
    if tag:
        query = query.filter(ContatoComunicacao.tags.contains([tag]))
    if busca:
        query = query.filter(
            or_(
                ContatoComunicacao.nome.ilike(f"%{busca}%"),
                ContatoComunicacao.email.ilike(f"%{busca}%"),
                ContatoComunicacao.telefone.ilike(f"%{busca}%")
            )
        )
    
    contatos = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": contato.id,
            "nome": contato.nome,
            "email": contato.email,
            "telefone": contato.telefone,
            "whatsapp": contato.whatsapp,
            "tags": contato.tags,
            "aceita_marketing": contato.aceita_marketing,
            "total_mensagens_recebidas": contato.total_mensagens_recebidas,
            "ultima_interacao": contato.ultima_interacao.isoformat() if contato.ultima_interacao else None,
            "ativo": contato.ativo,
            "criado_em": contato.criado_em.isoformat()
        }
        for contato in contatos
    ]

# === ENDPOINTS DE CAMPANHAS ===

@router.post("/campanhas", response_model=Dict[str, Any])
async def criar_campanha(
    request: CreateCampanhaRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar campanha de comunicação"""
    
    # Verificar template
    template = db.query(TemplateMensagem).filter(
        and_(
            TemplateMensagem.id == request.template_id,
            TemplateMensagem.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    campanha = CampanhaComunicacao(
        empresa_id=current_user.empresa_id,
        template_id=request.template_id,
        nome=request.nome,
        descricao=request.descricao,
        tipo=request.tipo,
        data_inicio=request.data_inicio,
        data_fim=request.data_fim,
        filtros_segmentacao=request.filtros_segmentacao,
        variante_a_template_id=request.variante_a_template_id,
        variante_b_template_id=request.variante_b_template_id,
        percentual_variante_a=request.percentual_variante_a
    )
    
    db.add(campanha)
    db.commit()
    db.refresh(campanha)
    
    # Calcular contatos alvo
    contatos_alvo = _calcular_contatos_campanha(db, current_user.empresa_id, request.filtros_segmentacao)
    campanha.total_contatos_alvo = contatos_alvo
    db.commit()
    
    return {
        "id": campanha.id,
        "message": "Campanha criada com sucesso",
        "contatos_alvo": contatos_alvo
    }

@router.post("/campanhas/{campanha_id}/executar", response_model=Dict[str, Any])
async def executar_campanha(
    campanha_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executar campanha de comunicação"""
    
    campanha = db.query(CampanhaComunicacao).filter(
        and_(
            CampanhaComunicacao.id == campanha_id,
            CampanhaComunicacao.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    if campanha.status != StatusCampanha.RASCUNHO:
        raise HTTPException(
            status_code=400, 
            detail="Campanha já foi executada ou está em andamento"
        )
    
    # Atualizar status
    campanha.status = StatusCampanha.ATIVA
    campanha.iniciada_em = datetime.now()
    db.commit()
    
    # Executar em background
    background_tasks.add_task(_processar_campanha, campanha_id, current_user.empresa_id)
    
    return {
        "message": "Campanha iniciada com sucesso",
        "status": "processando"
    }

# === ENDPOINTS DE MENSAGENS ===

@router.post("/mensagens/enviar", response_model=Dict[str, Any])
async def enviar_mensagem(
    request: EnvioMensagemRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar mensagem individual"""
    
    # Verificar canal
    canal = db.query(CanalComunicacao).filter(
        and_(
            CanalComunicacao.id == request.canal_id,
            CanalComunicacao.empresa_id == current_user.empresa_id,
            CanalComunicacao.ativo == True
        )
    ).first()
    
    if not canal:
        raise HTTPException(status_code=404, detail="Canal não encontrado ou inativo")
    
    # Processar conteúdo com variáveis
    conteudo_final = processar_variaveis_template(request.conteudo, request.variaveis)
    conteudo_html_final = None
    if request.conteudo_html:
        conteudo_html_final = processar_variaveis_template(request.conteudo_html, request.variaveis)
    
    # Criar mensagem
    mensagem = Mensagem(
        empresa_id=current_user.empresa_id,
        canal_id=request.canal_id,
        template_id=request.template_id,
        contato_id=request.contato_id,
        assunto=request.assunto,
        conteudo=conteudo_final,
        conteudo_html=conteudo_html_final,
        destinatario=request.destinatario,
        nome_destinatario=request.nome_destinatario,
        prioridade=request.prioridade
    )
    
    db.add(mensagem)
    db.commit()
    db.refresh(mensagem)
    
    # Adicionar à fila
    agendamento = request.agendado_para or datetime.now()
    fila = FilaEnvio(
        empresa_id=current_user.empresa_id,
        mensagem_id=mensagem.id,
        prioridade=request.prioridade,
        agendado_para=agendamento
    )
    
    db.add(fila)
    db.commit()
    
    # Se for envio imediato, processar
    if agendamento <= datetime.now():
        background_tasks.add_task(_processar_fila_envio, fila.id)
    
    return {
        "id": mensagem.id,
        "message": "Mensagem adicionada à fila de envio",
        "agendado_para": agendamento.isoformat()
    }

@router.get("/mensagens", response_model=List[Dict[str, Any]])
async def listar_mensagens(
    canal_id: Optional[int] = None,
    status: Optional[StatusMensagem] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar mensagens"""
    
    query = db.query(Mensagem).filter(
        Mensagem.empresa_id == current_user.empresa_id
    )
    
    if canal_id is not None:
        query = query.filter(Mensagem.canal_id == canal_id)
    if status is not None:
        query = query.filter(Mensagem.status == status)
    if data_inicio:
        query = query.filter(Mensagem.criado_em >= data_inicio)
    if data_fim:
        query = query.filter(Mensagem.criado_em <= data_fim)
    
    mensagens = query.order_by(desc(Mensagem.criado_em)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": mensagem.id,
            "canal_nome": mensagem.canal.nome,
            "destinatario": mensagem.destinatario,
            "assunto": mensagem.assunto,
            "status": mensagem.status.value,
            "prioridade": mensagem.prioridade.value,
            "tentativas": mensagem.tentativas,
            "enviada_em": mensagem.enviada_em.isoformat() if mensagem.enviada_em else None,
            "entregue_em": mensagem.entregue_em.isoformat() if mensagem.entregue_em else None,
            "criado_em": mensagem.criado_em.isoformat()
        }
        for mensagem in mensagens
    ]

# === DASHBOARD E MÉTRICAS ===

@router.get("/dashboard", response_model=DashboardComunicacao)
async def obter_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dashboard de comunicação"""
    
    empresa_id = current_user.empresa_id
    hoje = datetime.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Estatísticas básicas
    total_canais = db.query(CanalComunicacao).filter(CanalComunicacao.empresa_id == empresa_id).count()
    canais_ativos = db.query(CanalComunicacao).filter(
        and_(CanalComunicacao.empresa_id == empresa_id, CanalComunicacao.ativo == True)
    ).count()
    
    total_templates = db.query(TemplateMensagem).filter(TemplateMensagem.empresa_id == empresa_id).count()
    total_contatos = db.query(ContatoComunicacao).filter(ContatoComunicacao.empresa_id == empresa_id).count()
    total_campanhas = db.query(CampanhaComunicacao).filter(CampanhaComunicacao.empresa_id == empresa_id).count()
    campanhas_ativas = db.query(CampanhaComunicacao).filter(
        and_(
            CampanhaComunicacao.empresa_id == empresa_id,
            CampanhaComunicacao.status == StatusCampanha.ATIVA
        )
    ).count()
    
    # Mensagens
    mensagens_hoje = db.query(Mensagem).filter(
        and_(
            Mensagem.empresa_id == empresa_id,
            func.date(Mensagem.criado_em) == hoje
        )
    ).count()
    
    mensagens_mes = db.query(Mensagem).filter(
        and_(
            Mensagem.empresa_id == empresa_id,
            func.date(Mensagem.criado_em) >= inicio_mes
        )
    ).count()
    
    # Taxas médias
    metricas = db.query(
        func.avg(MetricaComunicacao.taxa_entrega).label('taxa_entrega'),
        func.avg(MetricaComunicacao.taxa_abertura).label('taxa_abertura')
    ).filter(MetricaComunicacao.empresa_id == empresa_id).first()
    
    taxa_entrega_media = float(metricas.taxa_entrega or 0)
    taxa_abertura_media = float(metricas.taxa_abertura or 0)
    
    # Distribuições
    canais_por_tipo = {}
    for canal in db.query(CanalComunicacao).filter(CanalComunicacao.empresa_id == empresa_id).all():
        tipo = canal.tipo.value
        canais_por_tipo[tipo] = canais_por_tipo.get(tipo, 0) + 1
    
    mensagens_por_canal = {}
    for resultado in db.query(
        CanalComunicacao.nome,
        func.count(Mensagem.id).label('total')
    ).join(Mensagem).filter(
        Mensagem.empresa_id == empresa_id
    ).group_by(CanalComunicacao.nome).all():
        mensagens_por_canal[resultado.nome] = resultado.total
    
    # Atividade recente
    mensagens_recentes = db.query(Mensagem).filter(
        Mensagem.empresa_id == empresa_id
    ).order_by(desc(Mensagem.criado_em)).limit(10).all()
    
    atividade_recente = [
        {
            "tipo": "mensagem",
            "descricao": f"Mensagem enviada para {msg.destinatario}",
            "canal": msg.canal.nome,
            "status": msg.status.value,
            "timestamp": msg.criado_em.isoformat()
        }
        for msg in mensagens_recentes
    ]
    
    return DashboardComunicacao(
        total_canais=total_canais,
        canais_ativos=canais_ativos,
        total_templates=total_templates,
        total_contatos=total_contatos,
        total_campanhas=total_campanhas,
        campanhas_ativas=campanhas_ativas,
        mensagens_hoje=mensagens_hoje,
        mensagens_mes=mensagens_mes,
        taxa_entrega_media=taxa_entrega_media,
        taxa_abertura_media=taxa_abertura_media,
        canais_por_tipo=canais_por_tipo,
        mensagens_por_canal=mensagens_por_canal,
        atividade_recente=atividade_recente
    )

# === FUNÇÕES AUXILIARES ===

async def _enviar_mensagem_teste(canal: CanalComunicacao, destinatario: str) -> bool:
    """Enviar mensagem de teste para validar canal"""
    try:
        if canal.tipo == TipoCanal.WHATSAPP:
            return await _enviar_whatsapp_teste(canal, destinatario)
        elif canal.tipo == TipoCanal.EMAIL:
            return await _enviar_email_teste(canal, destinatario)
        elif canal.tipo == TipoCanal.SMS:
            return await _enviar_sms_teste(canal, destinatario)
        return True
    except Exception:
        return False

async def _enviar_whatsapp_teste(canal: CanalComunicacao, destinatario: str) -> bool:
    """Enviar teste WhatsApp"""
    config = canal.configuracoes
    url = f"{config['api_url']}/{config['phone_number_id']}/messages"
    
    headers = {
        "Authorization": f"Bearer {config['access_token']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "text",
        "text": {
            "body": "🧪 Teste de configuração do canal WhatsApp. Canal funcionando corretamente!"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.status_code == 200

async def _enviar_email_teste(canal: CanalComunicacao, destinatario: str) -> bool:
    """Enviar teste Email"""
    # Implementação depende do provedor (SendGrid, SES, SMTP)
    return True  # Placeholder

async def _enviar_sms_teste(canal: CanalComunicacao, destinatario: str) -> bool:
    """Enviar teste SMS"""
    # Implementação depende do provedor (Twilio, SNS)
    return True  # Placeholder

def _calcular_contatos_campanha(db: Session, empresa_id: int, filtros: Dict[str, Any]) -> int:
    """Calcular número de contatos para campanha com base nos filtros"""
    query = db.query(ContatoComunicacao).filter(
        and_(
            ContatoComunicacao.empresa_id == empresa_id,
            ContatoComunicacao.ativo == True
        )
    )
    
    # Aplicar filtros de segmentação
    if filtros.get("aceita_marketing"):
        query = query.filter(ContatoComunicacao.aceita_marketing == True)
    
    if filtros.get("tags"):
        for tag in filtros["tags"]:
            query = query.filter(ContatoComunicacao.tags.contains([tag]))
    
    return query.count()

async def _processar_campanha(campanha_id: int, empresa_id: int):
    """Processar campanha em background"""
    # Esta função seria implementada para processar campanhas
    # de forma assíncrona, criando mensagens para todos os contatos
    pass

async def _processar_fila_envio(fila_id: int):
    """Processar item da fila de envio"""
    # Esta função seria implementada para processar
    # a fila de envio de mensagens
    pass

# === EVENTOS AUTOMÁTICOS ===

@router.post("/eventos", response_model=Dict[str, Any])
async def criar_evento_automatico(
    request: CreateEventoRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar evento automático de notificação"""
    
    evento = EventoNotificacao(
        empresa_id=current_user.empresa_id,
        template_id=request.template_id,
        nome=request.nome,
        tipo_evento=request.tipo_evento,
        descricao=request.descricao,
        condicoes=request.condicoes,
        delay_minutos=request.delay_minutos,
        filtros=request.filtros
    )
    
    db.add(evento)
    db.commit()
    db.refresh(evento)
    
    return {
        "id": evento.id,
        "message": "Evento automático criado com sucesso"
    }

@router.get("/eventos", response_model=List[Dict[str, Any]])
async def listar_eventos_automaticos(
    ativo: Optional[bool] = None,
    tipo_evento: Optional[TipoEvento] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar eventos automáticos"""
    
    query = db.query(EventoNotificacao).filter(
        EventoNotificacao.empresa_id == current_user.empresa_id
    )
    
    if ativo is not None:
        query = query.filter(EventoNotificacao.ativo == ativo)
    if tipo_evento is not None:
        query = query.filter(EventoNotificacao.tipo_evento == tipo_evento)
    
    eventos = query.order_by(EventoNotificacao.criado_em.desc()).all()
    
    return [
        {
            "id": evento.id,
            "nome": evento.nome,
            "tipo_evento": evento.tipo_evento.value,
            "template_nome": evento.template.nome,
            "delay_minutos": evento.delay_minutos,
            "total_disparos": evento.total_disparos,
            "total_sucessos": evento.total_sucessos,
            "ativo": evento.ativo,
            "criado_em": evento.criado_em.isoformat()
        }
        for evento in eventos
    ]

# Trigger para executar eventos automáticos
async def trigger_evento_automatico(tipo_evento: TipoEvento, dados_evento: Dict[str, Any], empresa_id: int):
    """Função para ser chamada quando eventos automáticos devem ser disparados"""
    # Esta função seria chamada por outros módulos do sistema
    # quando eventos relevantes ocorrem (novo pedido, pagamento, etc.)
    pass
