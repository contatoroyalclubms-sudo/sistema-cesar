"""
Router para Eventos - Nível MEEP
Sistema completo de gestão de eventos com todas as funcionalidades do MEEP
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pydantic import BaseModel, Field
import csv
import io
import json
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from ..database import get_db, Base
from ..models import Evento, Usuario, PromoterEvento, Transacao, Checkin, Lista, StatusTransacao
from ..schemas import (
    Evento as EventoSchema, 
    EventoCreate, 
    EventoDetalhado, 
    EventoFiltros,
    PromoterEventoCreate,
    PromoterEventoResponse
)
from ..auth_functions import obter_usuario_atual, verificar_permissao_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/eventos", tags=["Eventos MEEP Level"])

# Modelos MEEP para Eventos
class LoteEvento(Base):
    __tablename__ = "lotes_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    nome = Column(String(255), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)
    descricao = Column(Text)
    vendas_inicio = Column(DateTime)
    vendas_fim = Column(DateTime)
    vendidos = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    
    evento = relationship("Evento", back_populates="lotes")

class ConfiguracaoEvento(Base):
    __tablename__ = "configuracoes_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    confirmacao_email = Column(Boolean, default=True)
    confirmacao_sms = Column(Boolean, default=False)
    compartilhamento_social = Column(Boolean, default=True)
    desconto_promocional = Column(Boolean, default=False)
    codigo_desconto = Column(String(50))
    percentual_desconto = Column(Float, default=0)
    limite_ingressos_pessoa = Column(Integer, default=10)
    venda_no_local = Column(Boolean, default=False)
    meia_entrada = Column(Boolean, default=True)
    taxa_servico = Column(Float, default=5.0)
    
    evento = relationship("Evento", back_populates="configuracao")

class AnalyticsEvento(Base):
    __tablename__ = "analytics_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    visualizacoes = Column(Integer, default=0)
    compartilhamentos = Column(Integer, default=0)
    conversao_vendas = Column(Float, default=0)
    receita_total = Column(Float, default=0)
    tickets_vendidos = Column(Integer, default=0)
    data_atualizacao = Column(DateTime, default=datetime.utcnow)
    
    evento = relationship("Evento", back_populates="analytics")

# Schemas MEEP para Eventos  
class LoteEventoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    quantidade: int = Field(..., gt=0)
    preco: float = Field(..., ge=0)
    descricao: Optional[str] = None
    vendas_inicio: Optional[datetime] = None
    vendas_fim: Optional[datetime] = None

class LoteEventoResponse(BaseModel):
    id: int
    nome: str
    quantidade: int
    preco: float
    descricao: Optional[str]
    vendas_inicio: Optional[datetime]
    vendas_fim: Optional[datetime]
    vendidos: int
    ativo: bool
    
    class Config:
        from_attributes = True

class ConfiguracaoEventoCreate(BaseModel):
    confirmacao_email: bool = True
    confirmacao_sms: bool = False
    compartilhamento_social: bool = True
    desconto_promocional: bool = False
    codigo_desconto: Optional[str] = None
    percentual_desconto: float = 0
    limite_ingressos_pessoa: int = 10
    venda_no_local: bool = False
    meia_entrada: bool = True
    taxa_servico: float = 5.0

class EventoMEEPCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    local: Optional[str] = None
    endereco: Optional[str] = None
    categoria: str = "Geral"
    tipo: str = "presencial"
    capacidade_maxima: Optional[int] = None
    preco_base: float = 0
    imagem_url: Optional[str] = None
    publicado: bool = False
    lotes: List[LoteEventoCreate] = []
    configuracao: Optional[ConfiguracaoEventoCreate] = None

class EventoMEEPResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    data_inicio: datetime
    data_fim: Optional[datetime]
    local: Optional[str]
    endereco: Optional[str]
    categoria: str
    tipo: str
    capacidade_maxima: Optional[int]
    preco_base: float
    imagem_url: Optional[str]
    publicado: bool
    created_at: datetime
    lotes: List[LoteEventoResponse] = []
    configuracao: Optional[Dict[str, Any]] = None
    analytics: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Endpoints MEEP Level para Eventos

@router.post("/meep", response_model=EventoMEEPResponse)
async def criar_evento_meep(
    evento: EventoMEEPCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo evento com funcionalidades MEEP completas"""
    try:
        # Criar evento principal
        db_evento = Evento(
            nome=evento.nome,
            descricao=evento.descricao,
            data_evento=evento.data_inicio,
            local=evento.local,
            endereco=evento.endereco,
            categoria=evento.categoria,
            capacidade_maxima=evento.capacidade_maxima,
            preco=evento.preco_base,
            imagem_url=evento.imagem_url,
            publicado=evento.publicado,
            criado_por=usuario_atual.id,
            created_at=datetime.utcnow()
        )
        
        db.add(db_evento)
        db.flush()  # Para obter o ID
        
        # Criar lotes se fornecidos
        lotes_criados = []
        for lote_data in evento.lotes:
            lote = LoteEvento(
                evento_id=db_evento.id,
                nome=lote_data.nome,
                quantidade=lote_data.quantidade,
                preco=lote_data.preco,
                descricao=lote_data.descricao,
                vendas_inicio=lote_data.vendas_inicio,
                vendas_fim=lote_data.vendas_fim
            )
            db.add(lote)
            lotes_criados.append(lote)
        
        # Criar configurações se fornecidas
        if evento.configuracao:
            config = ConfiguracaoEvento(
                evento_id=db_evento.id,
                **evento.configuracao.dict()
            )
            db.add(config)
        
        # Criar analytics iniciais
        analytics = AnalyticsEvento(
            evento_id=db_evento.id,
            visualizacoes=0,
            compartilhamentos=0,
            conversao_vendas=0,
            receita_total=0,
            tickets_vendidos=0
        )
        db.add(analytics)
        
        db.commit()
        db.refresh(db_evento)
        
        return EventoMEEPResponse(
            id=db_evento.id,
            nome=db_evento.nome,
            descricao=db_evento.descricao,
            data_inicio=db_evento.data_evento,
            data_fim=evento.data_fim,
            local=db_evento.local,
            endereco=db_evento.endereco,
            categoria=db_evento.categoria,
            tipo=evento.tipo,
            capacidade_maxima=db_evento.capacidade_maxima,
            preco_base=float(db_evento.preco),
            imagem_url=db_evento.imagem_url,
            publicado=db_evento.publicado,
            created_at=db_evento.created_at,
            lotes=[],
            configuracao={},
            analytics={}
        )
        
    except Exception as e:
        logger.error(f"Erro ao criar evento MEEP: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar evento: {str(e)}"
        )

@router.get("/meep", response_model=List[EventoMEEPResponse])
async def listar_eventos_meep(
    skip: int = 0,
    limit: int = 100,
    categoria: Optional[str] = None,
    publicado: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listar eventos com funcionalidades MEEP"""
    query = db.query(Evento)
    
    if categoria:
        query = query.filter(Evento.categoria == categoria)
    if publicado is not None:
        query = query.filter(Evento.publicado == publicado)
    
    eventos = query.offset(skip).limit(limit).all()
    
    eventos_response = []
    for evento in eventos:
        # Buscar lotes
        lotes = db.query(LoteEvento).filter(LoteEvento.evento_id == evento.id).all()
        
        # Buscar configuração
        config = db.query(ConfiguracaoEvento).filter(ConfiguracaoEvento.evento_id == evento.id).first()
        
        # Buscar analytics
        analytics = db.query(AnalyticsEvento).filter(AnalyticsEvento.evento_id == evento.id).first()
        
        evento_response = EventoMEEPResponse(
            id=evento.id,
            nome=evento.nome,
            descricao=evento.descricao,
            data_inicio=evento.data_evento,
            data_fim=None,
            local=evento.local,
            endereco=evento.endereco,
            categoria=evento.categoria,
            tipo="presencial",
            capacidade_maxima=evento.capacidade_maxima,
            preco_base=float(evento.preco) if evento.preco else 0,
            imagem_url=evento.imagem_url,
            publicado=evento.publicado,
            created_at=evento.created_at,
            lotes=[LoteEventoResponse.from_orm(lote) for lote in lotes],
            configuracao=config.__dict__ if config else {},
            analytics=analytics.__dict__ if analytics else {}
        )
        eventos_response.append(evento_response)
    
    return eventos_response

@router.get("/meep/{evento_id}", response_model=EventoMEEPResponse)
async def obter_evento_meep(
    evento_id: int,
    db: Session = Depends(get_db)
):
    """Obter evento específico com funcionalidades MEEP"""
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Buscar dados relacionados
    lotes = db.query(LoteEvento).filter(LoteEvento.evento_id == evento.id).all()
    config = db.query(ConfiguracaoEvento).filter(ConfiguracaoEvento.evento_id == evento.id).first()
    analytics = db.query(AnalyticsEvento).filter(AnalyticsEvento.evento_id == evento.id).first()
    
    # Incrementar visualizações
    if analytics:
        analytics.visualizacoes += 1
        analytics.data_atualizacao = datetime.utcnow()
        db.commit()
    
    return EventoMEEPResponse(
        id=evento.id,
        nome=evento.nome,
        descricao=evento.descricao,
        data_inicio=evento.data_evento,
        data_fim=None,
        local=evento.local,
        endereco=evento.endereco,
        categoria=evento.categoria,
        tipo="presencial",
        capacidade_maxima=evento.capacidade_maxima,
        preco_base=float(evento.preco) if evento.preco else 0,
        imagem_url=evento.imagem_url,
        publicado=evento.publicado,
        created_at=evento.created_at,
        lotes=[LoteEventoResponse.from_orm(lote) for lote in lotes],
        configuracao=config.__dict__ if config else {},
        analytics=analytics.__dict__ if analytics else {}
    )

@router.post("/meep/{evento_id}/lotes", response_model=LoteEventoResponse)
async def criar_lote_evento(
    evento_id: int,
    lote: LoteEventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo lote para evento"""
    # Verificar se evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Criar lote
    db_lote = LoteEvento(
        evento_id=evento_id,
        **lote.dict()
    )
    
    db.add(db_lote)
    db.commit()
    db.refresh(db_lote)
    
    return LoteEventoResponse.from_orm(db_lote)

@router.put("/meep/{evento_id}/configuracoes")
async def atualizar_configuracoes_evento(
    evento_id: int,
    config: ConfiguracaoEventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar configurações do evento"""
    # Verificar se evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Buscar configuração existente
    db_config = db.query(ConfiguracaoEvento).filter(ConfiguracaoEvento.evento_id == evento_id).first()
    
    if db_config:
        # Atualizar existente
        for field, value in config.dict().items():
            setattr(db_config, field, value)
    else:
        # Criar nova
        db_config = ConfiguracaoEvento(
            evento_id=evento_id,
            **config.dict()
        )
        db.add(db_config)
    
    db.commit()
    return {"message": "Configurações atualizadas com sucesso"}

@router.get("/meep/{evento_id}/analytics")
async def obter_analytics_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter analytics detalhadas do evento"""
    # Verificar se evento existe
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Buscar analytics
    analytics = db.query(AnalyticsEvento).filter(AnalyticsEvento.evento_id == evento_id).first()
    
    # Calcular métricas adicionais
    total_vendas = db.query(func.sum(Transacao.valor)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == StatusTransacao.CONFIRMADA
    ).scalar() or 0
    
    tickets_vendidos = db.query(func.count(Transacao.id)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == StatusTransacao.CONFIRMADA
    ).scalar() or 0
    
    # Atualizar analytics
    if analytics:
        analytics.receita_total = float(total_vendas)
        analytics.tickets_vendidos = tickets_vendidos
        analytics.data_atualizacao = datetime.utcnow()
        db.commit()
    
    return {
        "evento_id": evento_id,
        "visualizacoes": analytics.visualizacoes if analytics else 0,
        "compartilhamentos": analytics.compartilhamentos if analytics else 0,
        "receita_total": float(total_vendas),
        "tickets_vendidos": tickets_vendidos,
        "conversao_vendas": (tickets_vendidos / analytics.visualizacoes * 100) if analytics and analytics.visualizacoes > 0 else 0,
        "data_atualizacao": analytics.data_atualizacao if analytics else datetime.utcnow()
    }

@router.post("/meep/{evento_id}/compartilhar")
async def compartilhar_evento(
    evento_id: int,
    platform: str,
    db: Session = Depends(get_db)
):
    """Registrar compartilhamento do evento"""
    # Atualizar analytics
    analytics = db.query(AnalyticsEvento).filter(AnalyticsEvento.evento_id == evento_id).first()
    
    if analytics:
        analytics.compartilhamentos += 1
        analytics.data_atualizacao = datetime.utcnow()
        db.commit()
    
    return {"message": f"Compartilhamento registrado para {platform}"}

@router.post("/meep/upload-imagem")
async def upload_imagem_evento(
    file: UploadFile = File(...),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Upload de imagem para evento"""
    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )
    
    # Simular upload (implementar storage real depois)
    filename = f"evento_{datetime.utcnow().timestamp()}_{file.filename}"
    
    return {
        "url": f"/uploads/eventos/{filename}",
        "filename": filename,
        "message": "Imagem enviada com sucesso"
    }

@router.get("/meep/categorias")
async def listar_categorias():
    """Listar categorias disponíveis para eventos"""
    return {
        "categorias": [
            "Música",
            "Teatro",
            "Esportes", 
            "Tecnologia",
            "Gastronomia",
            "Arte",
            "Educação",
            "Negócios",
            "Saúde",
            "Turismo",
            "Religioso",
            "Geral"
        ]
    }

@router.get("/meep/dashboard")
async def dashboard_eventos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Dashboard completo de eventos estilo MEEP"""
    # Eventos do usuário
    eventos_usuario = db.query(Evento).filter(Evento.criado_por == usuario_atual.id).all()
    
    # Métricas gerais
    total_eventos = len(eventos_usuario)
    eventos_ativos = len([e for e in eventos_usuario if e.publicado])
    
    total_vendas = db.query(func.sum(Transacao.valor)).join(Evento).filter(
        Evento.criado_por == usuario_atual.id,
        Transacao.status == StatusTransacao.CONFIRMADA
    ).scalar() or 0
    
    total_tickets = db.query(func.count(Transacao.id)).join(Evento).filter(
        Evento.criado_por == usuario_atual.id,
        Transacao.status == StatusTransacao.CONFIRMADA
    ).scalar() or 0
    
    # Analytics agregadas
    total_visualizacoes = db.query(func.sum(AnalyticsEvento.visualizacoes)).join(Evento).filter(
        Evento.criado_por == usuario_atual.id
    ).scalar() or 0
    
    return {
        "metricas": {
            "total_eventos": total_eventos,
            "eventos_ativos": eventos_ativos,
            "receita_total": float(total_vendas),
            "tickets_vendidos": total_tickets,
            "total_visualizacoes": total_visualizacoes
        },
        "eventos_recentes": [
            {
                "id": e.id,
                "nome": e.nome,
                "data_evento": e.data_evento,
                "publicado": e.publicado,
                "local": e.local
            } for e in eventos_usuario[-5:]
        ],
        "vendas_por_mes": [],  # Implementar agregação por mês
        "categorias_populares": []  # Implementar análise de categorias
    }

@router.post("/test", response_model=EventoSchema)
async def criar_evento_teste(
    evento: EventoCreate,
    db: Session = Depends(get_db)
):
    """TESTE: Criar novo evento SEM autenticação para debug"""
    
    print("=" * 50)
    print("TESTE CRIANDO EVENTO - SEM AUTENTICACAO")
    print(f"Dados recebidos: {evento.dict()}")
    print(f"Nome: {evento.nome}")
    print(f"Data do evento: {evento.data_evento} (tipo: {type(evento.data_evento)})")
    print(f"Local: {evento.local}")
    print(f"Endereco: {evento.endereco}")
    print(f"Limite idade: {evento.limite_idade}")
    print(f"Capacidade: {evento.capacidade_maxima}")
    # print(f"Empresa ID: {evento.empresa_id}") # empresa_id removed from model
    print("=" * 50)
    
    # Para teste, criar um usuário fake
    from ..models import Usuario
    usuario_teste = db.query(Usuario).filter(Usuario.tipo_usuario== "admin").first()
    if not usuario_teste:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nenhum usuário admin encontrado para teste"
        )
    
    # Se não foi especificada uma empresa, usar a primeira empresa disponível ou criar uma padrão
    empresa_id = None  # EventoCreate não tem empresa_id no schema
    if not empresa_id:
        from ..models import Empresa
        primeira_empresa = db.query(Empresa).filter(Empresa.ativa == True).first()
        if not primeira_empresa:
            # Criar empresa padrão se não existir nenhuma
            empresa_padrao = Empresa(
                nome="Empresa Padrão",
                cnpj="00000000000100",
                email="contato@paineluniversal.com",
                telefone="(11) 99999-9999",
                ativa=True
            )
            db.add(empresa_padrao)
            db.commit()
            db.refresh(empresa_padrao)
            empresa_id = empresa_padrao.id
        else:
            empresa_id = primeira_empresa.id
    
    try:
        evento_data = evento.dict()
        evento_data['criador_id'] = usuario_teste.id
        evento_data['empresa_id'] = empresa_id
        
        print(f"Dados finais do evento: {evento_data}")
        
        db_evento = Evento(**evento_data)
        db.add(db_evento)
        db.commit()
        db.refresh(db_evento)
        
        print(f"TESTE: Evento criado com sucesso: ID {db_evento.id}")
        
        return db_evento
        
    except Exception as e:
        print(f"TESTE ERRO ao criar evento no banco: {e}")
        print(f"TESTE Tipo do erro: {type(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao criar evento: {str(e)}"
        )

@router.post("/", response_model=EventoSchema)
async def criar_evento(
    evento: EventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo evento"""
    
    print("=" * 50)
    print("CRIANDO EVENTO - DEBUG DETALHADO")
    print(f"Dados recebidos: {evento.dict()}")
    print(f"Nome: {evento.nome}")
    print(f"Data do evento: {evento.data_evento} (tipo: {type(evento.data_evento)})")
    print(f"Local: {evento.local}")
    print(f"Endereco: {evento.endereco}")
    print(f"Limite idade: {evento.limite_idade}")
    print(f"Capacidade: {evento.capacidade_maxima}")
    print(f"Usuario: {usuario_atual.nome} ({usuario_atual.tipo}) - ID: {usuario_atual.id}")
    print("=" * 50)
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem criar eventos"
        )
    
    # Validação de data mais robusta com timezone awareness
    try:
        from datetime import timezone
        
        # Garantir que ambas as datas tenham timezone para comparação
        agora = datetime.now(timezone.utc)
        data_evento = evento.data_evento
        
        # Se a data do evento não tem timezone, assumir UTC
        if data_evento.tzinfo is None:
            data_evento = data_evento.replace(tzinfo=timezone.utc)
        
        print(f"VALIDAÇÃO DATA:")
        print(f"  Agora (UTC): {agora}")
        print(f"  Evento: {data_evento}")
        print(f"  É futura: {data_evento > agora}")
        
        if data_evento <= agora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data do evento deve ser futura. Evento: {data_evento}, Agora: {agora}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"ERRO ao validar data: {e}")
        print(f"Tipo da data do evento: {type(evento.data_evento)}")
        print(f"Valor da data do evento: {evento.data_evento}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data do evento inválida: {str(e)}"
        )
    
    # Se não foi especificada uma empresa, usar a primeira empresa disponível ou criar uma padrão
    empresa_id = None  # EventoCreate não tem empresa_id no schema
    if not empresa_id:
        from ..models import Empresa
        primeira_empresa = db.query(Empresa).filter(Empresa.ativa == True).first()
        if not primeira_empresa:
            # Criar empresa padrão se não existir nenhuma
            empresa_padrao = Empresa(
                nome="Empresa Padrão",
                cnpj="00000000000100",
                email="contato@paineluniversal.com",
                telefone="(11) 99999-9999",
                ativa=True
            )
            db.add(empresa_padrao)
            db.commit()
            db.refresh(empresa_padrao)
            empresa_id = empresa_padrao.id
        else:
            empresa_id = primeira_empresa.id
    
    try:
        evento_data = evento.dict()
        evento_data['criador_id'] = usuario_atual.id
        evento_data['empresa_id'] = empresa_id
        
        print(f"Dados finais do evento: {evento_data}")
        
        db_evento = Evento(**evento_data)
        db.add(db_evento)
        db.commit()
        db.refresh(db_evento)
        
        print(f"Evento criado com sucesso: ID {db_evento.id}")
        
        return db_evento
        
    except Exception as e:
        print(f"ERRO ao criar evento no banco: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao criar evento: {str(e)}"
        )

@router.get("/", response_model=List[EventoSchema])
async def listar_eventos(
    skip: int = 0,
    limit: int = 100,
    empresa_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar eventos"""
    
    query = db.query(Evento)
    
    # Role-based filtering removed - promoters and admins have access to all data
    if empresa_id:
        query = query.filter(Evento.empresa_id == empresa_id)
    
    if status:
        query = query.filter(Evento.status == status)
    
    eventos = query.offset(skip).limit(limit).all()
    return eventos

@router.get("/buscar", response_model=List[EventoSchema])
async def buscar_eventos(
    nome: Optional[str] = None,
    status: Optional[str] = None,
    empresa_id: Optional[int] = None,
    local: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Busca avançada de eventos com filtros"""
    
    query = db.query(Evento)
    
    # Role-based filtering removed - promoters and admins have access to all data
    if empresa_id:
        query = query.filter(Evento.empresa_id == empresa_id)
    
    if nome:
        query = query.filter(Evento.nome.ilike(f"%{nome}%"))
    
    if status:
        status_lower = status.lower()
        query = query.filter(Evento.status == status_lower)
    
    if local:
        query = query.filter(Evento.local.ilike(f"%{local}%"))
    
    eventos = query.offset(skip).limit(limit).all()
    return eventos

@router.get("/{evento_id}", response_model=EventoSchema)
async def obter_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados de um evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    return evento

@router.put("/{evento_id}", response_model=EventoSchema)
async def atualizar_evento(
    evento_id: int,
    evento_update: EventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar dados do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    if evento_update.data_evento <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data do evento deve ser futura"
        )
    
    for field, value in evento_update.dict(exclude={'empresa_id'}).items():
        setattr(evento, field, value)
    
    db.commit()
    db.refresh(evento)
    
    return evento

@router.delete("/{evento_id}")
async def cancelar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Cancelar evento (apenas admins)"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    evento.status = "cancelado"
    db.commit()
    
    return {"mensagem": "Evento cancelado com sucesso"}

@router.get("/detalhado/{evento_id}", response_model=EventoDetalhado)
async def obter_evento_detalhado(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter evento com dados financeiros e promoters"""
    
    evento = db.query(Evento).options(
        joinedload(Evento.promoters).joinedload(PromoterEvento.promoter)
    ).filter(Evento.id == evento_id).first()
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    total_vendas = db.query(func.count(Transacao.id)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == StatusTransacao.APROVADA
    ).scalar() or 0
    
    receita_total = db.query(func.sum(Transacao.valor)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == StatusTransacao.APROVADA
    ).scalar() or Decimal('0.00')
    
    total_checkins = db.query(func.count(Checkin.id)).filter(
        Checkin.evento_id == evento_id
    ).scalar() or 0
    
    promoters_vinculados = []
    for promoter_evento in evento.promoters:
        if promoter_evento.ativo:
            promoters_vinculados.append({
                "id": promoter_evento.id,
                "promoter_id": promoter_evento.promoter_id,
                "nome": promoter_evento.promoter.nome,
                "meta_vendas": promoter_evento.meta_vendas,
                "vendas_realizadas": promoter_evento.vendas_realizadas,
                "comissao_percentual": float(promoter_evento.comissao_percentual or 0)
            })
    
    if receita_total == 0:
        status_financeiro = "sem_vendas"
    elif receita_total < 1000:
        status_financeiro = "baixo"
    elif receita_total < 5000:
        status_financeiro = "medio"
    else:
        status_financeiro = "alto"
    
    evento_dict = {
        "id": evento.id,
        "nome": evento.nome,
        "descricao": evento.descricao,
        "data_evento": evento.data_evento,
        "local": evento.local,
        "endereco": evento.endereco,
        "limite_idade": evento.limite_idade,
        "capacidade_maxima": evento.capacidade_maxima,
        "status": evento.status,
        "empresa_id": getattr(evento, 'empresa_id', None),
        "criador_id": evento.criador_id,
        "criado_em": evento.criado_em,
        "atualizado_em": evento.atualizado_em,
        "total_vendas": total_vendas,
        "receita_total": receita_total,
        "total_checkins": total_checkins,
        "promoters_vinculados": promoters_vinculados,
        "status_financeiro": status_financeiro
    }
    
    return EventoDetalhado(**evento_dict)


@router.post("/{evento_id}/promoters", response_model=PromoterEventoResponse)
async def vincular_promoter(
    evento_id: int,
    promoter_data: PromoterEventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Vincular promoter ao evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    promoter = db.query(Usuario).filter(
        Usuario.id == promoter_data.promoter_id,
        Usuario.tipo_usuario== "promoter"
    ).first()
    if not promoter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoter não encontrado"
        )
    
    existing = db.query(PromoterEvento).filter(
        PromoterEvento.evento_id == evento_id,
        PromoterEvento.promoter_id == promoter_data.promoter_id,
        PromoterEvento.ativo == True
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promoter já vinculado ao evento"
        )
    
    promoter_evento = PromoterEvento(
        evento_id=evento_id,
        promoter_id=promoter_data.promoter_id,
        meta_vendas=promoter_data.meta_vendas,
        comissao_percentual=promoter_data.comissao_percentual,
        ativo=True
    )
    
    db.add(promoter_evento)
    db.commit()
    db.refresh(promoter_evento)
    
    return PromoterEventoResponse(
        id=promoter_evento.id,
        promoter_id=promoter_evento.promoter_id,
        evento_id=promoter_evento.evento_id,
        meta_vendas=promoter_evento.meta_vendas,
        vendas_realizadas=promoter_evento.vendas_realizadas,
        comissao_percentual=promoter_evento.comissao_percentual,
        ativo=promoter_evento.ativo,
        promoter_nome=promoter.nome
    )

@router.delete("/{evento_id}/promoters/{promoter_id}")
async def desvincular_promoter(
    evento_id: int,
    promoter_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Desvincular promoter do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    promoter_evento = db.query(PromoterEvento).filter(
        PromoterEvento.evento_id == evento_id,
        PromoterEvento.promoter_id == promoter_id,
        PromoterEvento.ativo == True
    ).first()
    
    if not promoter_evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vinculação não encontrada"
        )
    
    promoter_evento.ativo = False
    db.commit()
    
    return {"mensagem": "Promoter desvinculado com sucesso"}

@router.get("/{evento_id}/financeiro")
async def obter_status_financeiro(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter status financeiro detalhado do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    vendas_por_lista = db.query(
        Lista.nome,
        Lista.tipo,
        Lista.preco,
        func.count(Transacao.id).label('vendas'),
        func.sum(Transacao.valor).label('receita')
    ).join(
        Transacao, Transacao.lista_id == Lista.id
    ).filter(
        Lista.evento_id == evento_id,
        Transacao.status == StatusTransacao.APROVADA
    ).group_by(Lista.id, Lista.nome, Lista.tipo, Lista.preco).all()
    
    vendas_por_promoter = db.query(
        Usuario.nome,
        func.count(Transacao.id).label('vendas'),
        func.sum(Transacao.valor).label('receita')
    ).join(
        Lista, Lista.promoter_id == Usuario.id
    ).join(
        Transacao, Transacao.lista_id == Lista.id
    ).filter(
        Lista.evento_id == evento_id,
        Transacao.status == StatusTransacao.APROVADA
    ).group_by(Usuario.id, Usuario.nome).all()
    
    total_receita = sum(row.receita or 0 for row in vendas_por_lista)
    total_vendas = sum(row.vendas for row in vendas_por_lista)
    
    return {
        "evento_id": evento_id,
        "total_receita": float(total_receita),
        "total_vendas": total_vendas,
        "vendas_por_lista": [
            {
                "nome": row.nome,
                "tipo": row.tipo,
                "preco": float(row.preco),
                "vendas": row.vendas,
                "receita": float(row.receita or 0)
            }
            for row in vendas_por_lista
        ],
        "vendas_por_promoter": [
            {
                "nome": row.nome,
                "vendas": row.vendas,
                "receita": float(row.receita or 0)
            }
            for row in vendas_por_promoter
        ]
    }

@router.get("/{evento_id}/export/csv")
async def exportar_evento_csv(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Exportar dados do evento em CSV"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    transacoes = db.query(Transacao).join(Lista).filter(
        Lista.evento_id == evento_id
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID Transação', 'CPF Comprador', 'Nome Comprador', 'Email', 'Telefone',
        'Lista', 'Valor', 'Status', 'Data Compra', 'Promoter'
    ])
    
    for transacao in transacoes:
        lista = transacao.lista
        promoter_nome = lista.promoter.nome if lista.promoter else "N/A"
        
        writer.writerow([
            transacao.id,
            transacao.cpf_comprador,
            transacao.nome_comprador,
            transacao.email_comprador,
            transacao.telefone_comprador,
            lista.nome,
            float(transacao.valor),
            transacao.status.value,
            transacao.criado_em.strftime('%d/%m/%Y %H:%M'),
            promoter_nome
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=evento_{evento_id}_vendas.csv"}
    )

@router.get("/{evento_id}/export/pdf")
async def exportar_evento_pdf(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Exportar dados do evento em PDF"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem acessar este recurso"
        )
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Relatório do Evento: {evento.nome}")
    
    p.setFont("Helvetica", 12)
    y_position = height - 100
    
    info_evento = [
        f"Data: {evento.data_evento.strftime('%d/%m/%Y %H:%M')}",
        f"Local: {evento.local}",
        f"Endereço: {evento.endereco or 'N/A'}",
        f"Limite de Idade: {evento.limite_idade}+",
        f"Capacidade: {evento.capacidade_maxima}",
        f"Status: {evento.status.value}"
    ]
    
    for info in info_evento:
        p.drawString(50, y_position, info)
        y_position -= 20
    
    total_vendas = db.query(func.count(Transacao.id)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == StatusTransacao.APROVADA
    ).scalar() or 0
    
    receita_total = db.query(func.sum(Transacao.valor)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == StatusTransacao.APROVADA
    ).scalar() or Decimal('0.00')
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Resumo Financeiro")
    
    y_position -= 30
    p.setFont("Helvetica", 12)
    p.drawString(50, y_position, f"Total de Vendas: {total_vendas}")
    y_position -= 20
    p.drawString(50, y_position, f"Receita Total: R$ {float(receita_total):.2f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=evento_{evento_id}_relatorio.pdf"}
    )
# Forced reload
