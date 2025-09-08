"""
Modelos expandidos para Sistema de Fidelidade
Sistema completo de níveis, pontuação, campanhas e recompensas
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
import enum

from .models import Base, Usuario, Produto, Empresa, Cliente

# ================================================================================
# ENUMS
# ================================================================================

class TipoNivelFidelidade(enum.Enum):
    BRONZE = "bronze"
    PRATA = "prata"
    OURO = "ouro"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class TipoMovimentacaoPonto(enum.Enum):
    ACUMULO = "acumulo"
    RESGATE = "resgate"
    EXPIRACAO = "expiracao"
    AJUSTE = "ajuste"
    BONUS = "bonus"
    INDICACAO = "indicacao"

class StatusCampanha(enum.Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"
    AGENDADA = "agendada"

class TipoRecompensa(enum.Enum):
    DESCONTO_PERCENTUAL = "desconto_percentual"
    DESCONTO_VALOR = "desconto_valor"
    PRODUTO_GRATIS = "produto_gratis"
    CASHBACK = "cashback"
    UPGRADE_NIVEL = "upgrade_nivel"

class StatusIndicacao(enum.Enum):
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"

# ================================================================================
# MODELOS
# ================================================================================

class NivelFidelidade(Base):
    """Níveis de fidelidade com benefícios específicos"""
    __tablename__ = "niveis_fidelidade"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Dados do nível
    nome = Column(String(100), nullable=False)
    tipo = Column(SQLEnum(TipoNivelFidelidade), nullable=False)
    cor_hexadecimal = Column(String(7), default="#888888")
    icone = Column(String(100))
    
    # Critérios para atingir o nível
    pontos_minimos = Column(Integer, default=0)
    valor_gasto_minimo = Column(Numeric(15, 2), default=0)
    compras_minimas = Column(Integer, default=0)
    
    # Benefícios do nível
    multiplicador_pontos = Column(Float, default=1.0)
    desconto_percentual = Column(Float, default=0.0)
    frete_gratis = Column(Boolean, default=False)
    acesso_ofertas_exclusivas = Column(Boolean, default=False)
    suporte_prioritario = Column(Boolean, default=False)
    
    # Configurações
    ativo = Column(Boolean, default=True)
    ordem_exibicao = Column(Integer, default=0)
    descricao = Column(Text)
    
    # Auditoria
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="niveis_fidelidade")
    criado_por = relationship("Usuario")
    clientes = relationship("Cliente", back_populates="nivel_fidelidade")

class PontuacaoCliente(Base):
    """Histórico detalhado de pontuação por cliente"""
    __tablename__ = "pontuacao_clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Movimentação
    tipo_movimentacao = Column(SQLEnum(TipoMovimentacaoPonto), nullable=False)
    pontos = Column(Integer, nullable=False)
    pontos_antes = Column(Integer, default=0)
    pontos_depois = Column(Integer, default=0)
    
    # Origem da movimentação
    venda_id = Column(Integer, ForeignKey("vendas.id"))
    campanha_id = Column(Integer, ForeignKey("campanhas_fidelidade.id"))
    resgate_id = Column(Integer, ForeignKey("resgates_recompensa.id"))
    indicacao_id = Column(Integer, ForeignKey("indicacoes_cliente.id"))
    
    # Detalhes
    multiplicador_aplicado = Column(Float, default=1.0)
    valor_compra = Column(Numeric(15, 2))
    motivo = Column(String(500))
    observacoes = Column(Text)
    
    # Expiração
    data_expiracao = Column(DateTime)
    expirado = Column(Boolean, default=False)
    
    # Auditoria
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    cliente = relationship("Cliente", back_populates="pontuacoes")
    criado_por = relationship("Usuario")

class CampanhaFidelidade(Base):
    """Campanhas promocionais de fidelidade"""
    __tablename__ = "campanhas_fidelidade"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Dados da campanha
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    codigo = Column(String(50), unique=True)
    
    # Período
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    
    # Configurações
    status = Column(SQLEnum(StatusCampanha), default=StatusCampanha.AGENDADA)
    publico_alvo = Column(String(100))  # 'todos', 'nivel_bronze', 'nivel_prata', etc.
    limite_participantes = Column(Integer)
    participantes_atuais = Column(Integer, default=0)
    
    # Regras de pontuação
    multiplicador_pontos = Column(Float, default=1.0)
    pontos_bonus = Column(Integer, default=0)
    valor_minimo_compra = Column(Numeric(15, 2))
    produtos_elegíveis = Column(Text)  # JSON com IDs dos produtos
    
    # Recompensas
    tipo_recompensa = Column(SQLEnum(TipoRecompensa))
    valor_recompensa = Column(Numeric(15, 2))
    produto_recompensa_id = Column(Integer, ForeignKey("produtos.id"))
    
    # Configurações avançadas
    limite_uso_por_cliente = Column(Integer, default=1)
    requer_codigo = Column(Boolean, default=False)
    combina_com_outras = Column(Boolean, default=True)
    
    # Auditoria
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    produto_recompensa = relationship("Produto")
    criado_por = relationship("Usuario")
    pontuacoes = relationship("PontuacaoCliente", back_populates="campanha")

class IndicacaoCliente(Base):
    """Sistema de indicações entre clientes"""
    __tablename__ = "indicacoes_cliente"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Participantes
    cliente_indicador_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente_indicado_id = Column(Integer, ForeignKey("clientes.id"))
    
    # Dados da indicação
    codigo_indicacao = Column(String(20), unique=True, nullable=False)
    nome_indicado = Column(String(200))
    email_indicado = Column(String(200))
    telefone_indicado = Column(String(20))
    
    # Status
    status = Column(SQLEnum(StatusIndicacao), default=StatusIndicacao.PENDENTE)
    data_confirmacao = Column(DateTime)
    primeira_compra_realizada = Column(Boolean, default=False)
    
    # Recompensas
    pontos_indicador = Column(Integer, default=0)
    pontos_indicado = Column(Integer, default=0)
    recompensa_indicador = Column(Numeric(15, 2))
    recompensa_indicado = Column(Numeric(15, 2))
    
    # Auditoria
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    cliente_indicador = relationship("Cliente", foreign_keys=[cliente_indicador_id])
    cliente_indicado = relationship("Cliente", foreign_keys=[cliente_indicado_id])
    pontuacoes = relationship("PontuacaoCliente", back_populates="indicacao")

class ResgateRecompensa(Base):
    """Histórico de resgates de recompensas"""
    __tablename__ = "resgates_recompensa"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Dados do resgate
    codigo_resgate = Column(String(20), unique=True, nullable=False)
    tipo_recompensa = Column(SQLEnum(TipoRecompensa), nullable=False)
    pontos_utilizados = Column(Integer, nullable=False)
    
    # Recompensa
    valor_desconto = Column(Numeric(15, 2))
    percentual_desconto = Column(Float)
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    valor_cashback = Column(Numeric(15, 2))
    
    # Status
    utilizado = Column(Boolean, default=False)
    data_utilizacao = Column(DateTime)
    venda_id = Column(Integer, ForeignKey("vendas.id"))
    
    # Validade
    data_expiracao = Column(DateTime)
    expirado = Column(Boolean, default=False)
    
    # Auditoria
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    cliente = relationship("Cliente", back_populates="resgates")
    produto = relationship("Produto")
    criado_por = relationship("Usuario")
    pontuacoes = relationship("PontuacaoCliente", back_populates="resgate")

class RegrasAcumuloPontos(Base):
    """Regras flexíveis para acúmulo de pontos"""
    __tablename__ = "regras_acumulo_pontos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Identificação
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    
    # Configurações básicas
    ativa = Column(Boolean, default=True)
    prioridade = Column(Integer, default=0)  # Ordem de aplicação
    
    # Critérios de aplicação
    valor_minimo = Column(Numeric(15, 2))
    valor_maximo = Column(Numeric(15, 2))
    produtos_incluidos = Column(Text)  # JSON com IDs
    produtos_excluidos = Column(Text)  # JSON com IDs
    categorias_incluidas = Column(Text)  # JSON com IDs
    niveis_cliente = Column(Text)  # JSON com níveis elegíveis
    
    # Configuração de pontos
    pontos_por_real = Column(Float, default=1.0)
    pontos_fixos = Column(Integer, default=0)
    multiplicador = Column(Float, default=1.0)
    pontos_bonus = Column(Integer, default=0)
    
    # Período de validade
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    dias_semana = Column(String(20))  # 'seg,ter,qua,qui,sex,sab,dom'
    horario_inicio = Column(String(5))  # 'HH:MM'
    horario_fim = Column(String(5))  # 'HH:MM'
    
    # Limites
    limite_pontos_por_compra = Column(Integer)
    limite_pontos_por_dia = Column(Integer)
    limite_pontos_por_mes = Column(Integer)
    limite_uso_por_cliente = Column(Integer)
    
    # Auditoria
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    criado_por = relationship("Usuario")

class HistoricoNivelCliente(Base):
    """Histórico de mudanças de nível dos clientes"""
    __tablename__ = "historico_nivel_cliente"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Mudança de nível
    nivel_anterior_id = Column(Integer, ForeignKey("niveis_fidelidade.id"))
    nivel_novo_id = Column(Integer, ForeignKey("niveis_fidelidade.id"), nullable=False)
    
    # Motivo da mudança
    motivo = Column(String(500))
    pontos_na_mudanca = Column(Integer, default=0)
    valor_gasto_na_mudanca = Column(Numeric(15, 2))
    compras_na_mudanca = Column(Integer, default=0)
    
    # Auditoria
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    cliente = relationship("Cliente")
    nivel_anterior = relationship("NivelFidelidade", foreign_keys=[nivel_anterior_id])
    nivel_novo = relationship("NivelFidelidade", foreign_keys=[nivel_novo_id])
    criado_por = relationship("Usuario")

# ================================================================================
# ATUALIZAR RELACIONAMENTOS NOS MODELOS EXISTENTES
# ================================================================================

# Adicionar relacionamentos aos modelos existentes
# Isso seria feito através de migration ou atualizando os arquivos originais

"""
No modelo Cliente, adicionar:
    nivel_fidelidade_id = Column(Integer, ForeignKey("niveis_fidelidade.id"))
    pontos_atuais = Column(Integer, default=0)
    pontos_totais_acumulados = Column(Integer, default=0)
    pontos_totais_resgatados = Column(Integer, default=0)
    valor_total_gasto = Column(Numeric(15, 2), default=0)
    total_compras = Column(Integer, default=0)
    data_ultima_compra = Column(DateTime)
    codigo_indicacao = Column(String(20), unique=True)
    
    # Relacionamentos
    nivel_fidelidade = relationship("NivelFidelidade", back_populates="clientes")
    pontuacoes = relationship("PontuacaoCliente", back_populates="cliente")
    resgates = relationship("ResgateRecompensa", back_populates="cliente")
    indicacoes_feitas = relationship("IndicacaoCliente", foreign_keys="IndicacaoCliente.cliente_indicador_id")
    indicacoes_recebidas = relationship("IndicacaoCliente", foreign_keys="IndicacaoCliente.cliente_indicado_id")

No modelo Empresa, adicionar:
    niveis_fidelidade = relationship("NivelFidelidade", back_populates="empresa")
"""
