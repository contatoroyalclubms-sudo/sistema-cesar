"""
Schemas Pydantic para as novas funcionalidades baseadas na engenharia reversa
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

# ====== SISTEMA DE CATEGORIAS DE CLIENTES ======

class CategoriaClienteBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    icone: Optional[str] = None
    cor: Optional[str] = None
    lista_convidado: bool = False
    desconto_padrao: Optional[Decimal] = None
    beneficios: Optional[Dict[str, Any]] = None
    ordem: int = 0
    ativo: bool = True

class CategoriaClienteCreate(CategoriaClienteBase):
    pass

class CategoriaClienteUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    icone: Optional[str] = None
    cor: Optional[str] = None
    lista_convidado: Optional[bool] = None
    desconto_padrao: Optional[Decimal] = None
    beneficios: Optional[Dict[str, Any]] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None

class CategoriaCliente(CategoriaClienteBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    total_clientes: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class ClienteCategoriaBase(BaseModel):
    cliente_id: int
    categoria_id: int
    observacoes: Optional[str] = None

class ClienteCategoriaCreate(ClienteCategoriaBase):
    pass

class ClienteCategoria(ClienteCategoriaBase):
    id: int
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    categoria: Optional[CategoriaCliente] = None
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE PESQUISA DE SATISFAÇÃO ======

class PesquisaSatisfacaoBase(BaseModel):
    evento_id: Optional[int] = None
    titulo: str
    descricao: Optional[str] = None
    tipo_integracao: Optional[str] = None  # 'track.co', 'interno', 'google_forms'
    url_pesquisa: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None
    ativa: bool = True
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

class PesquisaSatisfacaoCreate(PesquisaSatisfacaoBase):
    pass

class PesquisaSatisfacaoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo_integracao: Optional[str] = None
    url_pesquisa: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None
    ativa: Optional[bool] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

class PesquisaSatisfacao(PesquisaSatisfacaoBase):
    id: int
    qr_code: Optional[str] = None
    total_respostas: int = 0
    nota_media: Optional[Decimal] = None
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RespostaPesquisaBase(BaseModel):
    pesquisa_id: int
    cliente_id: Optional[int] = None
    nota: Optional[int] = Field(None, ge=1, le=10)
    comentario: Optional[str] = None
    dados_resposta: Optional[Dict[str, Any]] = None
    origem: Optional[str] = None  # 'app', 'qrcode', 'totem', 'pos'

class RespostaPesquisaCreate(RespostaPesquisaBase):
    pass

class RespostaPesquisa(RespostaPesquisaBase):
    id: int
    ip_origem: Optional[str] = None
    data_resposta: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE FIDELIDADE ======

class ProgramaFidelidadeBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo_programa: Optional[str] = None  # 'pontos', 'cashback', 'niveis'
    ativo: bool = True

class ProgramaFidelidadeCreate(ProgramaFidelidadeBase):
    pass

class ProgramaFidelidadeUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo_programa: Optional[str] = None
    ativo: Optional[bool] = None

class ProgramaFidelidade(ProgramaFidelidadeBase):
    id: int
    criado_em: datetime
    total_participantes: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class NivelFidelidadeBase(BaseModel):
    programa_id: int
    nome: str
    pontos_minimos: int = 0
    pontos_maximos: Optional[int] = None
    cor: Optional[str] = None
    icone: Optional[str] = None
    beneficios: Optional[Dict[str, Any]] = None
    desconto_percentual: Optional[Decimal] = None
    multiplicador_pontos: Decimal = Decimal("1.0")
    ordem: int = 0

class NivelFidelidadeCreate(NivelFidelidadeBase):
    pass

class NivelFidelidade(NivelFidelidadeBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class ParticipanteFidelidadeBase(BaseModel):
    programa_id: int
    cliente_id: int

class ParticipanteFidelidadeCreate(ParticipanteFidelidadeBase):
    pass

class ParticipanteFidelidade(ParticipanteFidelidadeBase):
    id: int
    nivel_atual_id: Optional[int] = None
    pontos_totais: int = 0
    pontos_disponiveis: int = 0
    data_adesao: datetime
    data_ultima_movimentacao: Optional[datetime] = None
    nivel_atual: Optional[NivelFidelidade] = None
    
    model_config = ConfigDict(from_attributes=True)

class MovimentacaoPontosBase(BaseModel):
    participante_id: int
    tipo: str  # 'credito', 'debito', 'expiracao'
    pontos: int
    descricao: Optional[str] = None
    referencia_tipo: Optional[str] = None  # 'venda', 'bonus', 'resgate'
    referencia_id: Optional[int] = None
    data_expiracao: Optional[datetime] = None

class MovimentacaoPontosCreate(MovimentacaoPontosBase):
    pass

class MovimentacaoPontos(MovimentacaoPontosBase):
    id: int
    data_movimentacao: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE AUTOMAÇÃO ======

class AutomacaoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    gatilho_tipo: Optional[str] = None  # 'evento', 'horario', 'condicao', 'webhook'
    gatilho_config: Optional[Dict[str, Any]] = None
    acoes: Optional[List[Dict[str, Any]]] = None
    condicoes: Optional[Dict[str, Any]] = None
    status: str = 'ativo'  # 'ativo', 'inativo', 'pausado'

class AutomacaoCreate(AutomacaoBase):
    pass

class AutomacaoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    gatilho_tipo: Optional[str] = None
    gatilho_config: Optional[Dict[str, Any]] = None
    acoes: Optional[List[Dict[str, Any]]] = None
    condicoes: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class Automacao(AutomacaoBase):
    id: int
    ultima_execucao: Optional[datetime] = None
    proxima_execucao: Optional[datetime] = None
    execucoes_total: int = 0
    execucoes_sucesso: int = 0
    execucoes_erro: int = 0
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class LogAutomacaoBase(BaseModel):
    automacao_id: int
    status: str  # 'sucesso', 'erro', 'parcial'
    gatilho_dados: Optional[Dict[str, Any]] = None
    acoes_executadas: Optional[List[Dict[str, Any]]] = None
    erro_mensagem: Optional[str] = None
    tempo_execucao: Optional[int] = None

class LogAutomacao(LogAutomacaoBase):
    id: int
    data_execucao: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE BUSINESS INTELLIGENCE ======

class DashboardBIBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: Optional[str] = None  # 'operacional', 'financeiro', 'vendas', 'custom'
    layout: Optional[Dict[str, Any]] = None
    filtros_padrao: Optional[Dict[str, Any]] = None
    publico: bool = False

class DashboardBICreate(DashboardBIBase):
    pass

class DashboardBIUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    filtros_padrao: Optional[Dict[str, Any]] = None
    publico: Optional[bool] = None

class DashboardBI(DashboardBIBase):
    id: int
    usuario_criador_id: Optional[int] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    widgets: List["WidgetBI"] = []
    
    model_config = ConfigDict(from_attributes=True)

class WidgetBIBase(BaseModel):
    dashboard_id: int
    tipo: Optional[str] = None  # 'grafico_linha', 'grafico_pizza', 'kpi', 'tabela', 'mapa'
    titulo: Optional[str] = None
    consulta_sql: Optional[str] = None
    configuracao: Optional[Dict[str, Any]] = None
    posicao_x: int = 0
    posicao_y: int = 0
    largura: int = 4
    altura: int = 4
    auto_refresh: Optional[int] = None

class WidgetBICreate(WidgetBIBase):
    pass

class WidgetBI(WidgetBIBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE INTEGRAÇÕES ======

class IntegracaoBase(BaseModel):
    nome: str
    tipo: Optional[str] = None  # 'comunicacao', 'erp', 'fiscal', 'delivery', 'pagamento'
    provedor: Optional[str] = None  # 'whatsapp', 'ifood', 'omie', etc
    configuracao: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    ativo: bool = True

class IntegracaoCreate(IntegracaoBase):
    pass

class IntegracaoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    provedor: Optional[str] = None
    configuracao: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    ativo: Optional[bool] = None

class Integracao(IntegracaoBase):
    id: int
    status: str = 'desconectado'  # 'conectado', 'desconectado', 'erro'
    ultima_sincronizacao: Optional[datetime] = None
    proxima_sincronizacao: Optional[datetime] = None
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LogIntegracaoBase(BaseModel):
    integracao_id: int
    tipo_operacao: str  # 'envio', 'recepcao', 'sincronizacao'
    status: str  # 'sucesso', 'erro', 'pendente'
    dados_enviados: Optional[Dict[str, Any]] = None
    dados_recebidos: Optional[Dict[str, Any]] = None
    erro_mensagem: Optional[str] = None
    tempo_resposta: Optional[int] = None

class LogIntegracao(LogIntegracaoBase):
    id: int
    data_operacao: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE SOLUÇÕES ONLINE ======

class ConfiguracaoAppBase(BaseModel):
    evento_id: Optional[int] = None
    visivel_no_app: bool = True
    permite_consumo: bool = True
    pagamento_online: bool = False
    checkin_proximidade: bool = True
    distancia_checkin: int = 0
    checkin_remoto: bool = False
    ativacao_qrcode: bool = False
    categoria_app: Optional[str] = None
    tipo_operacao: Optional[str] = None  # 'ficha', 'cartao', 'comanda', 'mesa'
    cardapio_id: Optional[int] = None
    notificacao_push: bool = True
    destaque_perfil: bool = False
    taxa_servico_habilitada: bool = False
    taxa_servico_percentual: Decimal = Decimal("0")
    configuracao_adicional: Optional[Dict[str, Any]] = None

class ConfiguracaoAppCreate(ConfiguracaoAppBase):
    pass

class ConfiguracaoAppUpdate(BaseModel):
    visivel_no_app: Optional[bool] = None
    permite_consumo: Optional[bool] = None
    pagamento_online: Optional[bool] = None
    checkin_proximidade: Optional[bool] = None
    distancia_checkin: Optional[int] = None
    checkin_remoto: Optional[bool] = None
    ativacao_qrcode: Optional[bool] = None
    categoria_app: Optional[str] = None
    tipo_operacao: Optional[str] = None
    cardapio_id: Optional[int] = None
    notificacao_push: Optional[bool] = None
    destaque_perfil: Optional[bool] = None
    taxa_servico_habilitada: Optional[bool] = None
    taxa_servico_percentual: Optional[Decimal] = None
    configuracao_adicional: Optional[Dict[str, Any]] = None

class ConfiguracaoApp(ConfiguracaoAppBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class CardapioDigitalBase(BaseModel):
    evento_id: Optional[int] = None
    nome: str
    slug: Optional[str] = None
    configuracao: Optional[Dict[str, Any]] = None
    ativo: bool = True

class CardapioDigitalCreate(CardapioDigitalBase):
    pass

class CardapioDigitalUpdate(BaseModel):
    nome: Optional[str] = None
    slug: Optional[str] = None
    configuracao: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None

class CardapioDigital(CardapioDigitalBase):
    id: int
    uuid: str
    qr_code: Optional[str] = None
    url_completa: Optional[str] = None
    visualizacoes: int = 0
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE TICKETS/INGRESSOS ======

class EventoTicketBase(BaseModel):
    evento_id: int
    titulo: str
    descricao: Optional[str] = None
    data_inicio_vendas: Optional[datetime] = None
    data_fim_vendas: Optional[datetime] = None
    capacidade_total: Optional[int] = None
    imagem_capa: Optional[str] = None
    configuracao: Optional[Dict[str, Any]] = None

class EventoTicketCreate(EventoTicketBase):
    pass

class EventoTicketUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    data_inicio_vendas: Optional[datetime] = None
    data_fim_vendas: Optional[datetime] = None
    capacidade_total: Optional[int] = None
    imagem_capa: Optional[str] = None
    configuracao: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class EventoTicket(EventoTicketBase):
    id: int
    vendidos: int = 0
    status: str = 'ativo'  # 'ativo', 'pausado', 'esgotado', 'finalizado'
    criado_em: datetime
    lotes: List["LoteTicket"] = []
    
    model_config = ConfigDict(from_attributes=True)

class LoteTicketBase(BaseModel):
    evento_ticket_id: int
    nome: str
    numero: int = 1
    quantidade: int
    valor: Decimal
    taxa_servico: Decimal = Decimal("0")
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    descricao: Optional[str] = None
    ativo: bool = True

class LoteTicketCreate(LoteTicketBase):
    pass

class LoteTicket(LoteTicketBase):
    id: int
    vendidos: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class VendaTicketBase(BaseModel):
    evento_ticket_id: int
    lote_id: int
    cliente_id: Optional[int] = None
    quantidade: int
    forma_pagamento: Optional[str] = None

class VendaTicketCreate(VendaTicketBase):
    pass

class VendaTicket(VendaTicketBase):
    id: int
    codigo_venda: str
    valor_unitario: Decimal
    taxa_servico: Optional[Decimal] = None
    valor_total: Decimal
    status: str  # 'pendente', 'pago', 'cancelado', 'usado'
    qr_code: Optional[str] = None
    data_venda: datetime
    data_uso: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE COLABORADORES E CARGOS ======

class CargoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    nivel_hierarquia: int = 0
    ativo: bool = True

class CargoCreate(CargoBase):
    pass

class CargoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    nivel_hierarquia: Optional[int] = None
    ativo: Optional[bool] = None

class Cargo(CargoBase):
    id: int
    criado_em: datetime
    total_permissoes: int = 0
    total_colaboradores: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class PermissaoBase(BaseModel):
    modulo: str
    acao: str
    descricao: Optional[str] = None

class PermissaoCreate(PermissaoBase):
    pass

class Permissao(PermissaoBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class PermissaoCargoBase(BaseModel):
    cargo_id: int
    permissao_id: int

class PermissaoCargoCreate(PermissaoCargoBase):
    pass

class ColaboradorBase(BaseModel):
    usuario_id: int
    cargo_id: int
    empresa_id: Optional[int] = None
    matricula: Optional[str] = None
    data_admissao: Optional[date] = None
    salario: Optional[Decimal] = None
    comissao_percentual: Optional[Decimal] = None
    meta_mensal: Optional[Decimal] = None
    observacoes: Optional[str] = None
    ativo: bool = True

class ColaboradorCreate(ColaboradorBase):
    pass

class ColaboradorUpdate(BaseModel):
    cargo_id: Optional[int] = None
    empresa_id: Optional[int] = None
    matricula: Optional[str] = None
    data_admissao: Optional[date] = None
    data_demissao: Optional[date] = None
    salario: Optional[Decimal] = None
    comissao_percentual: Optional[Decimal] = None
    meta_mensal: Optional[Decimal] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class Colaborador(ColaboradorBase):
    id: int
    data_demissao: Optional[date] = None
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SISTEMA DE MAPA DE OPERAÇÃO ======

class MapaOperacaoBase(BaseModel):
    evento_id: int
    nome: str
    tipo: Optional[str] = None  # 'setores', 'mesas', 'areas', 'pontos_venda'
    configuracao_layout: Optional[Dict[str, Any]] = None
    imagem_fundo: Optional[str] = None
    largura: Optional[int] = None
    altura: Optional[int] = None
    ativo: bool = True

class MapaOperacaoCreate(MapaOperacaoBase):
    pass

class MapaOperacaoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    configuracao_layout: Optional[Dict[str, Any]] = None
    imagem_fundo: Optional[str] = None
    largura: Optional[int] = None
    altura: Optional[int] = None
    ativo: Optional[bool] = None

class MapaOperacao(MapaOperacaoBase):
    id: int
    criado_em: datetime
    elementos: List["ElementoMapa"] = []
    
    model_config = ConfigDict(from_attributes=True)

class ElementoMapaBase(BaseModel):
    mapa_id: int
    tipo: Optional[str] = None  # 'mesa', 'setor', 'pdv', 'entrada', 'saida', 'bar'
    codigo: Optional[str] = None
    nome: Optional[str] = None
    capacidade: Optional[int] = None
    status: Optional[str] = None  # 'livre', 'ocupado', 'reservado', 'manutencao'
    posicao_x: Optional[int] = None
    posicao_y: Optional[int] = None
    largura: Optional[int] = None
    altura: Optional[int] = None
    rotacao: int = 0
    cor: Optional[str] = None
    icone: Optional[str] = None
    dados_adicionais: Optional[Dict[str, Any]] = None

class ElementoMapaCreate(ElementoMapaBase):
    pass

class ElementoMapaUpdate(BaseModel):
    tipo: Optional[str] = None
    codigo: Optional[str] = None
    nome: Optional[str] = None
    capacidade: Optional[int] = None
    status: Optional[str] = None
    posicao_x: Optional[int] = None
    posicao_y: Optional[int] = None
    largura: Optional[int] = None
    altura: Optional[int] = None
    rotacao: Optional[int] = None
    cor: Optional[str] = None
    icone: Optional[str] = None
    dados_adicionais: Optional[Dict[str, Any]] = None

class ElementoMapa(ElementoMapaBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# Forward references update
DashboardBI.model_rebuild()

# ====== SCHEMAS DE AUTOMAÇÃO ======

class AutomacaoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo_gatilho: str
    ativa: bool = True
    configuracao: Optional[Dict[str, Any]] = None
    condicoes: Optional[List[Dict[str, Any]]] = None
    acoes: Optional[List[Dict[str, Any]]] = None
    frequencia: Optional[str] = None
    max_execucoes: Optional[int] = None

class AutomacaoCreate(AutomacaoBase):
    pass

class AutomacaoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo_gatilho: Optional[str] = None
    ativa: Optional[bool] = None
    configuracao: Optional[Dict[str, Any]] = None
    condicoes: Optional[List[Dict[str, Any]]] = None
    acoes: Optional[List[Dict[str, Any]]] = None
    frequencia: Optional[str] = None
    max_execucoes: Optional[int] = None

class Automacao(AutomacaoBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    ultima_execucao: Optional[datetime] = None
    proxima_execucao: Optional[datetime] = None
    total_execucoes: Optional[int] = None
    execucoes_sucesso: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class FluxoTrabalhoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    passos: Optional[List[Dict[str, Any]]] = None
    variaveis: Optional[Dict[str, Any]] = None
    ativo: bool = True

class FluxoTrabalhoCreate(FluxoTrabalhoBase):
    pass

class FluxoTrabalhoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    passos: Optional[List[Dict[str, Any]]] = None
    variaveis: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None

class FluxoTrabalho(FluxoTrabalhoBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ExecucaoFluxoBase(BaseModel):
    fluxo_id: int
    contexto: Optional[Dict[str, Any]] = None

class ExecucaoFluxoCreate(ExecucaoFluxoBase):
    pass

class ExecucaoFluxo(ExecucaoFluxoBase):
    id: int
    status: str
    iniciado_em: datetime
    finalizado_em: Optional[datetime] = None
    resultado: Optional[str] = None
    erro: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class LogAutomacao(BaseModel):
    id: int
    automacao_id: int
    usuario_id: Optional[int] = None
    tipo_evento: str
    status: str
    mensagem: Optional[str] = None
    detalhes: Optional[str] = None
    data_execucao: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SCHEMAS DE BUSINESS INTELLIGENCE ======

class WidgetBI(BaseModel):
    tipo: str
    titulo: str
    configuracao: Optional[Dict[str, Any]] = None
    posicao: Optional[Dict[str, int]] = None
    tamanho: Optional[Dict[str, int]] = None

class MetricaBI(BaseModel):
    nome: str
    valor: Any
    tipo: str
    periodo: Optional[str] = None
    comparacao: Optional[Dict[str, Any]] = None

class RelatorioBIBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: str
    periodo: Optional[str] = None
    filtros: Optional[Dict[str, Any]] = None
    formato: Optional[str] = None
    publico: bool = False

class RelatorioBICreate(RelatorioBIBase):
    pass

class RelatorioBI(RelatorioBIBase):
    id: int
    dados: Optional[str] = None
    criado_em: datetime
    criado_por_id: int
    
    model_config = ConfigDict(from_attributes=True)

# ====== SCHEMAS DE INTEGRAÇÕES ======

class IntegracaoBase(BaseModel):
    nome: str
    tipo: str
    descricao: Optional[str] = None
    url_base: Optional[str] = None
    credenciais: Optional[Dict[str, Any]] = None
    configuracao: Optional[Dict[str, Any]] = None
    ativa: bool = True

class IntegracaoCreate(IntegracaoBase):
    pass

class IntegracaoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    url_base: Optional[str] = None
    credenciais: Optional[Dict[str, Any]] = None
    configuracao: Optional[Dict[str, Any]] = None
    ativa: Optional[bool] = None

class Integracao(IntegracaoBase):
    id: int
    status: str
    ultimo_teste: Optional[datetime] = None
    erro_mensagem: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class WebhookIntegracaoBase(BaseModel):
    url: str
    evento: str
    ativo: bool = True
    headers: Optional[Dict[str, str]] = None

class WebhookIntegracaoCreate(WebhookIntegracaoBase):
    pass

class WebhookIntegracao(WebhookIntegracaoBase):
    id: int
    integracao_id: int
    secret: Optional[str] = None
    total_chamadas: Optional[int] = None
    total_erros: Optional[int] = None
    ultima_chamada: Optional[datetime] = None
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LogIntegracao(BaseModel):
    id: int
    integracao_id: int
    tipo_evento: str
    sucesso: bool
    mensagem: Optional[str] = None
    detalhes: Optional[str] = None
    usuario_id: Optional[int] = None
    data_evento: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SCHEMAS DE SOLUÇÕES ONLINE ======

class SolucaoOnlineBase(BaseModel):
    nome: str
    tipo: str
    descricao: Optional[str] = None
    url: Optional[str] = None
    recursos: Optional[List[str]] = None
    configuracoes: Optional[Dict[str, Any]] = None
    icone: Optional[str] = None
    ordem: int = 0
    ativa: bool = True

class SolucaoOnlineCreate(SolucaoOnlineBase):
    pass

class SolucaoOnlineUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    url: Optional[str] = None
    recursos: Optional[List[str]] = None
    configuracoes: Optional[Dict[str, Any]] = None
    icone: Optional[str] = None
    ordem: Optional[int] = None
    ativa: Optional[bool] = None

class SolucaoOnline(SolucaoOnlineBase):
    id: int
    total_acessos: Optional[int] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class RecursoAppBase(BaseModel):
    nome: str
    codigo: str
    categoria: str
    descricao: Optional[str] = None
    versao: str = "1.0.0"
    dependencias: Optional[List[str]] = None
    configuracao_padrao: Optional[Dict[str, Any]] = None
    documentacao_url: Optional[str] = None
    gratuito: bool = True
    preco: Optional[float] = None
    ativo: bool = True

class RecursoAppCreate(RecursoAppBase):
    pass

class RecursoApp(RecursoAppBase):
    id: int
    popularidade: int = 0
    total_instalacoes: Optional[int] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# ====== SCHEMAS DE TICKETS ======

class TipoTicketBase(BaseModel):
    evento_id: int
    nome: str
    descricao: Optional[str] = None
    preco_base: float
    quantidade_total: int
    quantidade_por_pessoa: int = 1
    beneficios: Optional[List[str]] = None
    restricoes: Optional[List[str]] = None
    categoria: Optional[str] = None
    ordem: int = 0
    ativo: bool = True

class TipoTicketCreate(TipoTicketBase):
    pass

class TipoTicketUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco_base: Optional[float] = None
    quantidade_total: Optional[int] = None
    quantidade_por_pessoa: Optional[int] = None
    beneficios: Optional[List[str]] = None
    restricoes: Optional[List[str]] = None
    categoria: Optional[str] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None

class TipoTicket(TipoTicketBase):
    id: int
    quantidade_disponivel: int
    quantidade_vendida: Optional[int] = None
    preco_atual: Optional[float] = None
    lote_atual: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class LoteTicketBase(BaseModel):
    tipo_ticket_id: int
    nome: str
    quantidade: int
    preco: float
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    ordem: int = 0
    ativo: bool = True

class LoteTicketCreate(LoteTicketBase):
    pass

class LoteTicketUpdate(BaseModel):
    nome: Optional[str] = None
    quantidade: Optional[int] = None
    preco: Optional[float] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None

class LoteTicket(LoteTicketBase):
    id: int
    quantidade_vendida: Optional[int] = None
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TicketBase(BaseModel):
    tipo_ticket_id: int
    quantidade: int = 1
    cliente_id: Optional[int] = None
    nome_titular: Optional[str] = None
    cpf_titular: Optional[str] = None
    email_titular: Optional[str] = None
    telefone_titular: Optional[str] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    nome_titular: Optional[str] = None
    cpf_titular: Optional[str] = None
    email_titular: Optional[str] = None
    telefone_titular: Optional[str] = None

class Ticket(BaseModel):
    id: int
    tipo_ticket_id: int
    lote_id: Optional[int] = None
    cliente_id: Optional[int] = None
    codigo: str
    qr_code: Optional[str] = None
    status: str
    valor_pago: float
    nome_titular: Optional[str] = None
    cpf_titular: Optional[str] = None
    email_titular: Optional[str] = None
    telefone_titular: Optional[str] = None
    data_compra: datetime
    data_uso: Optional[datetime] = None
    usado_por_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class TransferenciaTicketBase(BaseModel):
    ticket_id: int
    novo_cliente_id: int
    motivo: Optional[str] = None
    nome_titular: Optional[str] = None
    cpf_titular: Optional[str] = None
    email_titular: Optional[str] = None
    telefone_titular: Optional[str] = None

class TransferenciaTicketCreate(TransferenciaTicketBase):
    pass

class TransferenciaTicket(TransferenciaTicketBase):
    id: int
    cliente_anterior_id: int
    cliente_novo_id: int
    data_transferencia: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ====== SCHEMAS DE COLABORADORES ======

class CargoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    departamento: Optional[str] = None
    nivel_hierarquia: int = 0
    salario_base: Optional[float] = None
    requisitos: Optional[List[str]] = None
    permissoes: Optional[List[str]] = None
    ativo: bool = True

class CargoCreate(CargoBase):
    pass

class CargoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    departamento: Optional[str] = None
    nivel_hierarquia: Optional[int] = None
    salario_base: Optional[float] = None
    requisitos: Optional[List[str]] = None
    permissoes: Optional[List[str]] = None
    ativo: Optional[bool] = None

class Cargo(CargoBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ColaboradorBase(BaseModel):
    nome: str
    cpf: str
    email: str
    telefone: Optional[str] = None
    cargo_id: Optional[int] = None
    tipo: str  # fixo, temporario, freelancer, voluntario
    status: str  # ativo, inativo, ferias, afastado
    data_nascimento: Optional[datetime] = None
    data_admissao: datetime
    salario_atual: Optional[float] = None
    habilidades: Optional[List[str]] = None
    documentos: Optional[Dict[str, Any]] = None
    foto_url: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None

class ColaboradorCreate(ColaboradorBase):
    pass

class ColaboradorUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    cargo_id: Optional[int] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    salario_atual: Optional[float] = None
    habilidades: Optional[List[str]] = None
    documentos: Optional[Dict[str, Any]] = None
    foto_url: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None

class Colaborador(ColaboradorBase):
    id: int
    data_desligamento: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class EscalaTrabalhoBase(BaseModel):
    colaborador_id: int
    evento_id: Optional[int] = None
    data_inicio: datetime
    data_fim: datetime
    tipo: str  # normal, plantao, revezamento, evento
    local: Optional[str] = None
    observacoes: Optional[str] = None

class EscalaTrabalhoCreate(EscalaTrabalhoBase):
    pass

class EscalaTrabalhoUpdate(BaseModel):
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    tipo: Optional[str] = None
    local: Optional[str] = None
    observacoes: Optional[str] = None

class EscalaTrabalho(EscalaTrabalhoBase):
    id: int
    status: str
    horas_previstas: Optional[float] = None
    horas_trabalhadas: Optional[float] = None
    checkin_realizado: Optional[datetime] = None
    checkout_realizado: Optional[datetime] = None
    localizacao_checkin: Optional[str] = None
    criado_em: datetime
    criado_por_id: int
    
    model_config = ConfigDict(from_attributes=True)

class TarefaColaboradorBase(BaseModel):
    colaborador_id: int
    escala_id: Optional[int] = None
    titulo: str
    descricao: Optional[str] = None
    prioridade: str  # baixa, media, alta, urgente
    prazo: Optional[datetime] = None
    categoria: Optional[str] = None

class TarefaColaboradorCreate(TarefaColaboradorBase):
    pass

class TarefaColaboradorUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    prioridade: Optional[str] = None
    prazo: Optional[datetime] = None
    categoria: Optional[str] = None
    status: Optional[str] = None

class TarefaColaborador(TarefaColaboradorBase):
    id: int
    status: str
    data_conclusao: Optional[datetime] = None
    criado_em: datetime
    criado_por_id: int
    
    model_config = ConfigDict(from_attributes=True)