"""
Modelos para Sistema de Fidelidade
Programa de pontos, níveis, recompensas e gamificação
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Text, Numeric, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum
from .database import Base


class TipoMovimentoPontos(enum.Enum):
    """Tipos de movimentação de pontos"""
    COMPRA = "compra"
    BONUS = "bonus"
    RESGATE = "resgate"
    EXPIRACAO = "expiracao"
    AJUSTE_MANUAL = "ajuste_manual"
    REFERENCIA = "referencia"
    ANIVERSARIO = "aniversario"
    PRIMEIRA_COMPRA = "primeira_compra"
    META_ATINGIDA = "meta_atingida"
    CONQUISTA = "conquista"


class StatusRecompensa(enum.Enum):
    """Status de uma recompensa"""
    DISPONIVEL = "disponivel"
    RESGATADA = "resgatada"
    UTILIZADA = "utilizada"
    EXPIRADA = "expirada"
    CANCELADA = "cancelada"


class TipoRecompensa(enum.Enum):
    """Tipos de recompensa"""
    DESCONTO_PERCENTUAL = "desconto_percentual"
    DESCONTO_VALOR = "desconto_valor"
    PRODUTO_GRATIS = "produto_gratis"
    FRETE_GRATIS = "frete_gratis"
    ENTRADA_VIP = "entrada_vip"
    EXPERIENCIA = "experiencia"
    BRINDE = "brinde"
    CASHBACK = "cashback"
    UPGRADE = "upgrade"


class TipoConquista(enum.Enum):
    """Tipos de conquista/badge"""
    PRIMEIRA_COMPRA = "primeira_compra"
    NUMERO_COMPRAS = "numero_compras"
    VALOR_GASTO = "valor_gasto"
    FREQUENCIA = "frequencia"
    PRODUTO_ESPECIFICO = "produto_especifico"
    CATEGORIA = "categoria"
    HORARIO = "horario"
    EVENTO = "evento"
    SOCIAL = "social"
    ESPECIAL = "especial"


# Tabela de associação para conquistas desbloqueadas
cliente_conquistas = Table(
    'fidelidade_cliente_conquistas',
    Base.metadata,
    Column('cliente_fidelidade_id', Integer, ForeignKey('fidelidade_clientes.id')),
    Column('conquista_id', Integer, ForeignKey('fidelidade_conquistas.id')),
    Column('data_conquista', DateTime(timezone=True), server_default=func.now()),
    Column('notificado', Boolean, default=False)
)


class ProgramaFidelidade(Base):
    """Configuração do programa de fidelidade"""
    __tablename__ = "fidelidade_programas"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Informações básicas
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Configurações de pontos
    valor_real_por_ponto = Column(Numeric(10, 2), default=1.00)  # R$ 1,00 = 1 ponto
    pontos_por_real = Column(Numeric(10, 2), default=1.00)  # 1 real = 1 ponto
    
    # Multiplicadores base
    multiplicador_aniversario = Column(Float, default=2.0)
    multiplicador_primeira_compra = Column(Float, default=1.5)
    multiplicador_happy_hour = Column(Float, default=1.5)
    
    # Validade dos pontos
    validade_pontos_dias = Column(Integer, default=365)  # Dias
    permite_transferencia = Column(Boolean, default=False)
    permite_doacao = Column(Boolean, default=True)
    
    # Limites
    pontos_maximos_dia = Column(Integer, nullable=True)  # Limite diário de ganho
    pontos_minimos_resgate = Column(Integer, default=100)
    
    # Configurações de níveis
    usa_niveis = Column(Boolean, default=True)
    pontos_manutencao_nivel = Column(Boolean, default=True)  # Se precisa manter pontos para manter nível
    periodo_avaliacao_nivel = Column(Integer, default=365)  # Dias para avaliar nível
    
    # Gamificação
    usa_conquistas = Column(Boolean, default=True)
    usa_ranking = Column(Boolean, default=True)
    usa_desafios = Column(Boolean, default=True)
    
    # Notificações
    notificar_pontos = Column(Boolean, default=True)
    notificar_nivel = Column(Boolean, default=True)
    notificar_expiracao = Column(Boolean, default=True)
    dias_aviso_expiracao = Column(Integer, default=30)
    
    # Integrações
    integrar_pdv = Column(Boolean, default=True)
    integrar_ecommerce = Column(Boolean, default=False)
    integrar_app = Column(Boolean, default=True)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    niveis = relationship("NivelPrograma", back_populates="programa", cascade="all, delete-orphan")
    clientes = relationship("ClienteFidelidade", back_populates="programa")
    recompensas = relationship("RecompensaPrograma", back_populates="programa")
    conquistas = relationship("ConquistaPrograma", back_populates="programa")
    desafios = relationship("DesafioFidelidade", back_populates="programa")


class NivelPrograma(Base):
    """Níveis do programa de fidelidade"""
    __tablename__ = "fidelidade_niveis"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("fidelidade_programas.id"), nullable=False)
    
    # Informações do nível
    nome = Column(String(100), nullable=False)  # Bronze, Prata, Ouro, Platina, Diamante, Titanium
    ordem = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5, 6
    cor = Column(String(7), default="#000000")  # Cor do nível
    icone = Column(String(100))  # URL ou nome do ícone
    
    # Requisitos
    pontos_necessarios = Column(Integer, nullable=False)  # Pontos para atingir
    compras_necessarias = Column(Integer, default=0)  # Número de compras
    valor_gasto_necessario = Column(Numeric(10, 2), default=0)  # Valor total gasto
    
    # Benefícios
    multiplicador_pontos = Column(Float, default=1.0)  # Multiplicador de ganho
    desconto_permanente = Column(Float, default=0)  # Desconto % em todas as compras
    cashback_percentual = Column(Float, default=0)  # Cashback %
    
    # Benefícios especiais
    beneficios = Column(JSON, default={
        "frete_gratis": False,
        "entrada_prioritaria": False,
        "acesso_vip": False,
        "atendimento_prioritario": False,
        "preview_produtos": False,
        "eventos_exclusivos": False,
        "presente_aniversario": False
    })
    
    # Manutenção do nível
    pontos_manutencao = Column(Integer, default=0)  # Pontos necessários para manter
    periodo_manutencao = Column(Integer, default=365)  # Dias
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    programa = relationship("ProgramaFidelidade", back_populates="niveis")
    clientes = relationship("ClienteFidelidade", back_populates="nivel_atual")


class ClienteFidelidade(Base):
    """Participação do cliente no programa"""
    __tablename__ = "fidelidade_clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("fidelidade_programas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True)
    data_adesao = Column(DateTime(timezone=True), server_default=func.now())
    data_inativacao = Column(DateTime(timezone=True))
    
    # Pontos
    pontos_disponiveis = Column(Integer, default=0)
    pontos_totais = Column(Integer, default=0)  # Total histórico
    pontos_expirados = Column(Integer, default=0)
    pontos_resgatados = Column(Integer, default=0)
    
    # Nível
    nivel_atual_id = Column(Integer, ForeignKey("fidelidade_niveis.id"))
    data_ultimo_nivel = Column(DateTime(timezone=True))
    pontos_proximo_nivel = Column(Integer)  # Quantos pontos faltam
    
    # Estatísticas
    total_compras = Column(Integer, default=0)
    valor_total_gasto = Column(Numeric(10, 2), default=0)
    ticket_medio = Column(Numeric(10, 2), default=0)
    ultima_compra = Column(DateTime(timezone=True))
    dias_sem_compra = Column(Integer, default=0)
    
    # Gamificação
    total_conquistas = Column(Integer, default=0)
    posicao_ranking = Column(Integer)
    pontos_ranking = Column(Integer, default=0)
    
    # Preferências
    preferencias = Column(JSON, default={
        "notificacoes_email": True,
        "notificacoes_sms": True,
        "notificacoes_push": True,
        "compartilhar_ranking": True,
        "receber_ofertas": True
    })
    
    # Código único do cliente
    codigo_fidelidade = Column(String(20), unique=True, index=True)
    qr_code = Column(Text)  # Base64 do QR Code
    
    # Indicações
    indicado_por_id = Column(Integer, ForeignKey("fidelidade_clientes.id"))
    total_indicacoes = Column(Integer, default=0)
    pontos_indicacao = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    programa = relationship("ProgramaFidelidade", back_populates="clientes")
    cliente = relationship("Cliente")
    nivel_atual = relationship("NivelPrograma", back_populates="clientes")
    movimentos = relationship("MovimentoPontos", back_populates="cliente_fidelidade")
    resgates = relationship("ResgateFidelidade", back_populates="cliente_fidelidade")
    conquistas_desbloqueadas = relationship("ConquistaPrograma", secondary=cliente_conquistas, back_populates="clientes")
    indicador = relationship("ClienteFidelidade", remote_side=[id], backref="indicados")
    desafios_participando = relationship("ParticipacaoDesafio", back_populates="cliente_fidelidade")


class MovimentoPontos(Base):
    """Movimentações de pontos"""
    __tablename__ = "fidelidade_movimentos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_fidelidade_id = Column(Integer, ForeignKey("fidelidade_clientes.id"), nullable=False)
    
    # Tipo e valor
    tipo = Column(SQLEnum(TipoMovimentoPontos), nullable=False)
    pontos = Column(Integer, nullable=False)  # Positivo = entrada, Negativo = saída
    saldo_anterior = Column(Integer, nullable=False)
    saldo_posterior = Column(Integer, nullable=False)
    
    # Referências
    venda_id = Column(Integer, ForeignKey("vendas_pdv.id"))
    resgate_id = Column(Integer, ForeignKey("fidelidade_resgates.id"))
    
    # Detalhes
    descricao = Column(String(500))
    observacoes = Column(Text)
    multiplicador_aplicado = Column(Float, default=1.0)
    
    # Validade
    data_expiracao = Column(DateTime(timezone=True))
    expirado = Column(Boolean, default=False)
    
    # Rastreamento
    origem = Column(String(50))  # PDV, App, Site, Admin
    usuario_responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    ip_origem = Column(String(45))
    
    # Timestamp
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cliente_fidelidade = relationship("ClienteFidelidade", back_populates="movimentos")
    venda = relationship("VendaPDV")
    resgate = relationship("ResgateFidelidade", foreign_keys=[resgate_id])
    usuario_responsavel = relationship("Usuario")


class RecompensaPrograma(Base):
    """Recompensas disponíveis no programa"""
    __tablename__ = "fidelidade_recompensas"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("fidelidade_programas.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo = Column(SQLEnum(TipoRecompensa), nullable=False)
    ativo = Column(Boolean, default=True)
    destaque = Column(Boolean, default=False)
    
    # Custo e valor
    custo_pontos = Column(Integer, nullable=False)
    valor_desconto = Column(Numeric(10, 2))  # Para descontos em valor
    percentual_desconto = Column(Float)  # Para descontos percentuais
    
    # Restrições
    nivel_minimo_id = Column(Integer, ForeignKey("fidelidade_niveis.id"))
    quantidade_disponivel = Column(Integer)  # null = ilimitado
    quantidade_resgatada = Column(Integer, default=0)
    limite_por_cliente = Column(Integer, default=1)
    
    # Validade
    validade_dias = Column(Integer, default=30)  # Dias após resgate
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    
    # Condições
    condicoes = Column(JSON, default={
        "valor_minimo_compra": 0,
        "categorias_validas": [],
        "produtos_validos": [],
        "dias_semana": [],
        "horarios": [],
        "eventos_validos": []
    })
    
    # Visual
    imagem_url = Column(String(500))
    cor_destaque = Column(String(7))
    icone = Column(String(100))
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    programa = relationship("ProgramaFidelidade", back_populates="recompensas")
    nivel_minimo = relationship("NivelPrograma")
    resgates = relationship("ResgateFidelidade", back_populates="recompensa")


class ResgateFidelidade(Base):
    """Resgates realizados"""
    __tablename__ = "fidelidade_resgates"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_fidelidade_id = Column(Integer, ForeignKey("fidelidade_clientes.id"), nullable=False)
    recompensa_id = Column(Integer, ForeignKey("fidelidade_recompensas.id"), nullable=False)
    
    # Status
    status = Column(SQLEnum(StatusRecompensa), default=StatusRecompensa.RESGATADA)
    
    # Código único
    codigo_resgate = Column(String(20), unique=True, index=True)
    qr_code = Column(Text)  # Base64 do QR Code
    
    # Pontos
    pontos_utilizados = Column(Integer, nullable=False)
    
    # Validade
    data_resgate = Column(DateTime(timezone=True), server_default=func.now())
    data_expiracao = Column(DateTime(timezone=True))
    data_utilizacao = Column(DateTime(timezone=True))
    
    # Utilização
    venda_utilizada_id = Column(Integer, ForeignKey("vendas_pdv.id"))
    valor_desconto_aplicado = Column(Numeric(10, 2))
    
    # Cancelamento
    data_cancelamento = Column(DateTime(timezone=True))
    motivo_cancelamento = Column(Text)
    cancelado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    cliente_fidelidade = relationship("ClienteFidelidade", back_populates="resgates")
    recompensa = relationship("RecompensaPrograma", back_populates="resgates")
    venda_utilizada = relationship("VendaPDV")
    cancelado_por = relationship("Usuario")
    movimento_pontos = relationship("MovimentoPontos", foreign_keys="MovimentoPontos.resgate_id", uselist=False)


class ConquistaPrograma(Base):
    """Conquistas/Badges do programa"""
    __tablename__ = "fidelidade_conquistas"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("fidelidade_programas.id"), nullable=False)
    
    # Informações
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo = Column(SQLEnum(TipoConquista), nullable=False)
    ativo = Column(Boolean, default=True)
    oculta = Column(Boolean, default=False)  # Conquista secreta
    
    # Visual
    icone_url = Column(String(500))
    cor = Column(String(7))
    animacao = Column(String(50))  # Nome da animação ao desbloquear
    
    # Recompensa
    pontos_recompensa = Column(Integer, default=0)
    recompensa_extra = Column(JSON)  # Outras recompensas
    
    # Critérios
    criterios = Column(JSON, nullable=False)
    # Exemplos:
    # {"tipo": "numero_compras", "quantidade": 10}
    # {"tipo": "valor_gasto", "valor": 1000}
    # {"tipo": "frequencia", "dias_consecutivos": 7}
    # {"tipo": "produto", "produto_id": 123, "quantidade": 5}
    
    # Raridade
    raridade = Column(String(20), default="comum")  # comum, raro, epico, lendario
    ordem_exibicao = Column(Integer, default=0)
    
    # Estatísticas
    total_desbloqueios = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    programa = relationship("ProgramaFidelidade", back_populates="conquistas")
    clientes = relationship("ClienteFidelidade", secondary=cliente_conquistas, back_populates="conquistas_desbloqueadas")


class DesafioFidelidade(Base):
    """Desafios temporários para ganhar pontos extras"""
    __tablename__ = "fidelidade_desafios"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("fidelidade_programas.id"), nullable=False)
    
    # Informações
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Período
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=False)
    
    # Tipo
    tipo = Column(String(50))  # diario, semanal, mensal, especial
    recorrente = Column(Boolean, default=False)
    
    # Critérios
    criterios = Column(JSON, nullable=False)
    # Exemplos:
    # {"tipo": "compras_periodo", "quantidade": 3}
    # {"tipo": "valor_minimo", "valor": 100}
    # {"tipo": "categoria", "categoria_id": 5, "quantidade": 2}
    
    # Recompensas
    pontos_conclusao = Column(Integer, nullable=False)
    bonus_velocidade = Column(Integer, default=0)  # Bonus por completar rápido
    recompensa_extra = Column(JSON)
    
    # Limites
    limite_participantes = Column(Integer)
    nivel_minimo_id = Column(Integer, ForeignKey("fidelidade_niveis.id"))
    
    # Visual
    imagem_url = Column(String(500))
    cor_tema = Column(String(7))
    
    # Estatísticas
    total_participantes = Column(Integer, default=0)
    total_concluidos = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    programa = relationship("ProgramaFidelidade", back_populates="desafios")
    nivel_minimo = relationship("NivelPrograma")
    participantes = relationship("ParticipacaoDesafio", back_populates="desafio")


class ParticipacaoDesafio(Base):
    """Participação em desafios"""
    __tablename__ = "fidelidade_participacao_desafios"
    
    id = Column(Integer, primary_key=True, index=True)
    desafio_id = Column(Integer, ForeignKey("fidelidade_desafios.id"), nullable=False)
    cliente_fidelidade_id = Column(Integer, ForeignKey("fidelidade_clientes.id"), nullable=False)
    
    # Status
    data_inicio = Column(DateTime(timezone=True), server_default=func.now())
    data_conclusao = Column(DateTime(timezone=True))
    concluido = Column(Boolean, default=False)
    
    # Progresso
    progresso_atual = Column(JSON, default={})
    percentual_completo = Column(Float, default=0)
    
    # Recompensas
    pontos_ganhos = Column(Integer, default=0)
    recompensa_extra_recebida = Column(JSON)
    
    # Relacionamentos
    desafio = relationship("DesafioFidelidade", back_populates="participantes")
    cliente_fidelidade = relationship("ClienteFidelidade", back_populates="desafios_participando")


class RankingFidelidade(Base):
    """Ranking mensal/anual de clientes"""
    __tablename__ = "fidelidade_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("fidelidade_programas.id"), nullable=False)
    
    # Período
    tipo_periodo = Column(String(20))  # mensal, trimestral, anual
    ano = Column(Integer, nullable=False)
    mes = Column(Integer)
    trimestre = Column(Integer)
    
    # Rankings (JSON com top clientes)
    ranking_pontos = Column(JSON)  # [{"cliente_id": 1, "pontos": 1000, "posicao": 1}, ...]
    ranking_compras = Column(JSON)
    ranking_valor = Column(JSON)
    ranking_indicacoes = Column(JSON)
    
    # Estatísticas gerais
    total_participantes = Column(Integer)
    pontos_distribuidos = Column(Integer)
    media_pontos = Column(Float)
    
    # Premiação
    premios_distribuidos = Column(JSON)
    
    # Timestamps
    calculado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    programa = relationship("ProgramaFidelidade")