"""
Schemas Pydantic para funcionalidades avançadas do sistema
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

# ================== SCHEMAS PARA WORKSPACE ==================

class WorkspaceBase(BaseModel):
    nome: str
    slug: str
    logo_url: Optional[str] = None
    plano: str = "free"

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    nome: Optional[str] = None
    logo_url: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None
    plano: Optional[str] = None

class WorkspaceResponse(WorkspaceBase):
    id: int
    limite_usuarios: int
    limite_eventos: int
    limite_vendas_mes: int
    features_habilitadas: List[str]
    ativo: bool
    trial_ate: Optional[datetime]
    criado_em: datetime
    
    class Config:
        from_attributes = True

class UsuarioWorkspaceBase(BaseModel):
    usuario_id: int
    workspace_id: int
    papel: str = "membro"
    permissoes: List[str] = []

class UsuarioWorkspaceResponse(UsuarioWorkspaceBase):
    id: int
    workspace_padrao: bool
    ultimo_acesso: Optional[datetime]
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA EVENTOS RECORRENTES ==================

class EventoRecorrenciaBase(BaseModel):
    tipo_recorrencia: str  # diario, semanal, mensal, anual
    intervalo: int = 1
    dias_semana: Optional[List[int]] = None
    dia_mes: Optional[int] = None
    data_fim: Optional[date] = None
    max_ocorrencias: Optional[int] = None
    excecoes: List[str] = []

class EventoRecorrenciaCreate(EventoRecorrenciaBase):
    evento_pai_id: int

class EventoRecorrenciaUpdate(BaseModel):
    ativo: Optional[bool] = None
    data_fim: Optional[date] = None
    excecoes: Optional[List[str]] = None

class EventoRecorrenciaResponse(EventoRecorrenciaBase):
    id: int
    evento_pai_id: int
    ocorrencias_criadas: int
    ativo: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA FILAS VIRTUAIS ==================

class FilaVirtualBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    capacidade_maxima: Optional[int] = None
    tempo_estimado_atendimento: Optional[int] = None
    prioridade_habilitada: bool = False

class FilaVirtualCreate(FilaVirtualBase):
    evento_id: int

class FilaVirtualUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    capacidade_maxima: Optional[int] = None
    tempo_estimado_atendimento: Optional[int] = None
    ativa: Optional[bool] = None

class FilaVirtualResponse(FilaVirtualBase):
    id: int
    evento_id: int
    posicao_atual: int
    total_atendidos: int
    ativa: bool
    qr_code_acesso: Optional[str]
    criado_em: datetime
    
    class Config:
        from_attributes = True

class ParticipanteFilaBase(BaseModel):
    cpf: str
    nome: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    prioridade: bool = False

class ParticipanteFilaCreate(ParticipanteFilaBase):
    fila_id: int

class ParticipanteFilaUpdate(BaseModel):
    status: Optional[str] = None
    notificado: Optional[bool] = None

class ParticipanteFilaResponse(ParticipanteFilaBase):
    id: int
    fila_id: int
    posicao: int
    senha: str
    hora_entrada: datetime
    hora_chamada: Optional[datetime]
    hora_atendimento: Optional[datetime]
    status: str
    notificado: bool
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA ANALYTICS ==================

class EventoAnalyticsBase(BaseModel):
    data_analise: date
    total_participantes: int = 0
    total_vendas: Decimal = Decimal("0.00")
    ticket_medio: Decimal = Decimal("0.00")
    taxa_conversao: float = 0.0
    tempo_medio_permanencia: Optional[int] = None

class EventoAnalyticsCreate(EventoAnalyticsBase):
    evento_id: int
    heatmap_data: Optional[Dict[str, Any]] = None
    top_produtos: Optional[List[Dict[str, Any]]] = None
    top_horarios: Optional[List[Dict[str, Any]]] = None
    previsao_proxima: Optional[Dict[str, Any]] = None

class EventoAnalyticsResponse(EventoAnalyticsBase):
    id: int
    evento_id: int
    pico_ocupacao: Optional[datetime]
    heatmap_data: Optional[Dict[str, Any]]
    top_produtos: Optional[List[Dict[str, Any]]]
    top_horarios: Optional[List[Dict[str, Any]]]
    previsao_proxima: Optional[Dict[str, Any]]
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA CAMPANHAS DE MARKETING ==================

class CampanhaMarketingBase(BaseModel):
    nome: str
    tipo: str  # email, sms, push, whatsapp
    conteudo_titulo: Optional[str] = None
    conteudo_mensagem: str
    conteudo_html: Optional[str] = None
    imagem_url: Optional[str] = None
    botao_acao: Optional[str] = None
    link_acao: Optional[str] = None

class CampanhaMarketingCreate(CampanhaMarketingBase):
    evento_id: Optional[int] = None
    workspace_id: Optional[int] = None
    segmento_alvo: Optional[Dict[str, Any]] = None
    agendada_para: Optional[datetime] = None

class CampanhaMarketingUpdate(BaseModel):
    nome: Optional[str] = None
    conteudo_titulo: Optional[str] = None
    conteudo_mensagem: Optional[str] = None
    conteudo_html: Optional[str] = None
    imagem_url: Optional[str] = None
    agendada_para: Optional[datetime] = None
    status: Optional[str] = None

class CampanhaMarketingResponse(CampanhaMarketingBase):
    id: int
    evento_id: Optional[int]
    workspace_id: Optional[int]
    segmento_alvo: Optional[Dict[str, Any]]
    agendada_para: Optional[datetime]
    enviada_em: Optional[datetime]
    total_destinatarios: int
    total_enviados: int
    total_aberturas: int
    total_cliques: int
    total_conversoes: int
    status: str
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA AUDIT TRAIL ==================

class AuditLogBase(BaseModel):
    acao: str
    entidade: str
    entidade_id: Optional[int] = None
    dados_anteriores: Optional[Dict[str, Any]] = None
    dados_novos: Optional[Dict[str, Any]] = None
    metadados: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    usuario_id: Optional[int] = None
    workspace_id: Optional[int] = None
    ip_origem: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogResponse(AuditLogBase):
    id: int
    usuario_id: Optional[int]
    workspace_id: Optional[int]
    ip_origem: Optional[str]
    user_agent: Optional[str]
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA TRANSFERÊNCIA DE INGRESSOS ==================

class TransferenciaIngressoBase(BaseModel):
    cpf_destino: str
    nome_destino: str
    email_destino: Optional[str] = None
    telefone_destino: Optional[str] = None
    motivo: Optional[str] = None

class TransferenciaIngressoCreate(TransferenciaIngressoBase):
    transacao_original_id: int
    cpf_origem: str
    nome_origem: str

class TransferenciaIngressoConfirm(BaseModel):
    codigo_autorizacao: str

class TransferenciaIngressoResponse(TransferenciaIngressoBase):
    id: int
    transacao_original_id: int
    cpf_origem: str
    nome_origem: str
    codigo_autorizacao: str
    confirmada: bool
    confirmada_em: Optional[datetime]
    cancelada: bool
    cancelada_em: Optional[datetime]
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA ANÚNCIOS ==================

class AnuncioBase(BaseModel):
    titulo: str
    mensagem: str
    tipo: str = "info"  # info, alerta, emergencia, promocao
    prioridade: int = 0
    canais: List[str] = ["app"]
    imagem_url: Optional[str] = None
    link_acao: Optional[str] = None

class AnuncioCreate(AnuncioBase):
    evento_id: Optional[int] = None
    workspace_id: Optional[int] = None
    segmento_alvo: Optional[Dict[str, Any]] = None
    exibir_de: Optional[datetime] = None
    exibir_ate: Optional[datetime] = None

class AnuncioUpdate(BaseModel):
    titulo: Optional[str] = None
    mensagem: Optional[str] = None
    ativo: Optional[bool] = None
    exibir_ate: Optional[datetime] = None

class AnuncioResponse(AnuncioBase):
    id: int
    evento_id: Optional[int]
    workspace_id: Optional[int]
    segmento_alvo: Optional[Dict[str, Any]]
    exibir_de: Optional[datetime]
    exibir_ate: Optional[datetime]
    total_visualizacoes: int
    total_cliques: int
    ativo: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA LISTA DE ESPERA ==================

class ListaEsperaBase(BaseModel):
    cpf: str
    nome: str
    email: str
    telefone: Optional[str] = None
    quantidade_desejada: int = 1

class ListaEsperaCreate(ListaEsperaBase):
    evento_id: int
    lista_id: Optional[int] = None

class ListaEsperaResponse(ListaEsperaBase):
    id: int
    evento_id: int
    lista_id: Optional[int]
    posicao: int
    notificado: bool
    notificado_em: Optional[datetime]
    convertido: bool
    convertido_em: Optional[datetime]
    expirado: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA NETWORKING ==================

class NetworkingPerfilBase(BaseModel):
    bio: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    linkedin: Optional[str] = None
    interesses: List[str] = []
    buscando: List[str] = []
    oferecendo: List[str] = []
    disponivel_networking: bool = True

class NetworkingPerfilCreate(NetworkingPerfilBase):
    usuario_id: int
    evento_id: int
    foto_perfil_url: Optional[str] = None
    agenda_disponivel: Optional[Dict[str, Any]] = None

class NetworkingPerfilUpdate(NetworkingPerfilBase):
    foto_perfil_url: Optional[str] = None
    agenda_disponivel: Optional[Dict[str, Any]] = None

class NetworkingPerfilResponse(NetworkingPerfilBase):
    id: int
    usuario_id: int
    evento_id: int
    foto_perfil_url: Optional[str]
    agenda_disponivel: Optional[Dict[str, Any]]
    verificado: bool
    score_networking: int
    criado_em: datetime
    
    class Config:
        from_attributes = True

class NetworkingConexaoBase(BaseModel):
    tipo: str  # conexao, reuniao, troca_cartao
    mensagem: Optional[str] = None
    data_reuniao: Optional[datetime] = None
    local_reuniao: Optional[str] = None

class NetworkingConexaoCreate(NetworkingConexaoBase):
    evento_id: int
    perfil_origem_id: int
    perfil_destino_id: int

class NetworkingConexaoUpdate(BaseModel):
    aceita: Optional[bool] = None
    data_reuniao: Optional[datetime] = None
    local_reuniao: Optional[str] = None
    notas: Optional[str] = None
    avaliacao: Optional[int] = None

class NetworkingConexaoResponse(NetworkingConexaoBase):
    id: int
    evento_id: int
    perfil_origem_id: int
    perfil_destino_id: int
    aceita: Optional[bool]
    notas: Optional[str]
    avaliacao: Optional[int]
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ================== SCHEMAS PARA EVENTOS ONLINE ==================

class EventoOnlineBase(BaseModel):
    plataforma: str  # zoom, teams, youtube, custom
    link_transmissao: Optional[str] = None
    senha_acesso: Optional[str] = None
    link_sala_espera: Optional[str] = None
    capacidade_online: Optional[int] = None
    gravacao_habilitada: bool = True
    chat_habilitado: bool = True
    qa_habilitado: bool = True
    networking_virtual: bool = False

class EventoOnlineCreate(EventoOnlineBase):
    evento_id: int

class EventoOnlineUpdate(EventoOnlineBase):
    link_gravacao: Optional[str] = None
    estatisticas: Optional[Dict[str, Any]] = None

class EventoOnlineResponse(EventoOnlineBase):
    id: int
    evento_id: int
    link_gravacao: Optional[str]
    estatisticas: Optional[Dict[str, Any]]
    criado_em: datetime
    
    class Config:
        from_attributes = True