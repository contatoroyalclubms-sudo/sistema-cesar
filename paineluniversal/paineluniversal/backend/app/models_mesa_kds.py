"""
Sistema de Mesas + KDS (Kitchen Display System) - Implementação Completa Meep
==============================================================================

Modelos para sistema avançado de gestão de mesas e cozinha baseado na 
engenharia reversa do sistema Meep.

Funcionalidades impl    pedido_id = Column(Integer, ForeignKey("pedidos_mesa.id"))
    estacao_id = Column(Integer, ForeignKey("estacao_kds.id"))
    mesa_id = Column(Integer, ForeignKey("mesas.id"))ntadas:
- Gestão avançada de mesas com status em tempo real
- Sistema KDS (Kitchen Display System) para cozinha
- Controle de pedidos por mesa
- Notificações e alertas automatizados
- Integração com sistema cashless
- Relatórios de performance e tempo
"""

import enum
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Time, Numeric, ForeignKey, Enum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .models import Base

# ================================================================================
# ENUMS PARA SISTEMA DE MESAS + KDS
# ================================================================================

class StatusPedidoMesa(enum.Enum):
    """Status dos pedidos de mesa"""
    PENDENTE = "pendente"              # Pedido criado, aguardando confirmação
    CONFIRMADO = "confirmado"          # Pedido confirmado, enviado para cozinha
    PREPARANDO = "preparando"          # Em preparo na cozinha
    PRONTO = "pronto"                  # Pronto para entrega
    ENTREGUE = "entregue"             # Entregue ao cliente
    CANCELADO = "cancelado"           # Cancelado
    PAUSADO = "pausado"               # Pausado temporariamente

class PrioridadePedido(enum.Enum):
    """Prioridade do pedido"""
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"
    VIP = "vip"

class TipoNotificacaoKDS(enum.Enum):
    """Tipos de notificação do KDS"""
    NOVO_PEDIDO = "novo_pedido"
    PEDIDO_ATRASADO = "pedido_atrasado"
    PEDIDO_URGENTE = "pedido_urgente"
    MESA_ESPERANDO = "mesa_esperando"
    ALERTA_TEMPO = "alerta_tempo"
    SISTEMA = "sistema"

class StatusItemPedido(enum.Enum):
    """Status individual dos itens do pedido"""
    PENDENTE = "pendente"
    PREPARANDO = "preparando"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

class TipoEstacaoKDS(enum.Enum):
    """Tipos de estação na cozinha"""
    GERAL = "geral"                   # Estação geral
    BEBIDAS = "bebidas"               # Estação de bebidas
    PRATOS_QUENTES = "pratos_quentes" # Estação de pratos quentes
    PRATOS_FRIOS = "pratos_frios"     # Estação de pratos frios
    SOBREMESAS = "sobremesas"         # Estação de sobremesas
    GRELHADOS = "grelhados"           # Estação de grelhados
    MASSAS = "massas"                 # Estação de massas
    SALADAS = "saladas"               # Estação de saladas

class ModoPedidoMesa(enum.Enum):
    """Modo de operação do pedido"""
    MESA = "mesa"                     # Pedido direto na mesa
    BALCAO = "balcao"                # Pedido no balcão para retirada
    DELIVERY = "delivery"             # Pedido para entrega
    TAKEOUT = "takeout"              # Pedido para viagem

# ================================================================================
# MODELOS PARA PEDIDOS DE MESA
# ================================================================================

class PedidoMesa(Base):
    """Pedidos vinculados a mesas com controle completo de status"""
    __tablename__ = "pedidos_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(20), unique=True, nullable=False, index=True)  # ex: "M001-240904-001"
    
    # Vinculação com mesa
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    numero_mesa = Column(String(10), nullable=False)  # Cache do número da mesa
    
    # Informações do pedido
    nome_cliente = Column(String(255))
    cpf_cliente = Column(String(14))
    telefone_cliente = Column(String(20))
    observacoes = Column(Text)
    observacoes_cozinha = Column(Text)  # Observações específicas para a cozinha
    
    # Status e controle
    status = Column(Enum(StatusPedidoMesa), default=StatusPedidoMesa.PENDENTE)
    prioridade = Column(Enum(PrioridadePedido), default=PrioridadePedido.NORMAL)
    modo_pedido = Column(Enum(ModoPedidoMesa), default=ModoPedidoMesa.MESA)
    
    # Valores financeiros
    valor_subtotal = Column(Numeric(10, 2), default=0)
    valor_desconto = Column(Numeric(10, 2), default=0)
    valor_acrescimo = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2), default=0)
    
    # Tempos de controle
    tempo_estimado_preparo = Column(Integer, default=0)  # em minutos
    data_pedido = Column(DateTime(timezone=True), server_default=func.now())
    data_confirmacao = Column(DateTime(timezone=True))
    data_inicio_preparo = Column(DateTime(timezone=True))
    data_conclusao = Column(DateTime(timezone=True))
    data_entrega = Column(DateTime(timezone=True))
    
    # Controle de usuários
    usuario_criacao_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_confirmacao_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario_entrega_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Integração com sistemas
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    
    # Metadados para KDS
    estacao_responsavel = Column(Enum(TipoEstacaoKDS), default=TipoEstacaoKDS.GERAL)
    alertas_enviados = Column(JSON, default=list)  # Lista de alertas já enviados
    configuracoes_kds = Column(JSON, default=dict)  # Configurações específicas do KDS
    
    # Relacionamentos
    mesa = relationship("Mesa")
    itens = relationship("ItemPedidoMesa", back_populates="pedido")
    usuario_criacao = relationship("Usuario", foreign_keys=[usuario_criacao_id])
    usuario_confirmacao = relationship("Usuario", foreign_keys=[usuario_confirmacao_id])
    usuario_entrega = relationship("Usuario", foreign_keys=[usuario_entrega_id])
    notificacoes = relationship("NotificacaoKDS", back_populates="pedido")
    
    # Índices para performance - COMENTADOS porque foram criados via SQL direto
    # __table_args__ = (
    #     Index('idx_pedido_mesa_status_data', 'status', 'data_pedido'),
    #     Index('idx_pedido_mesa_empresa_evento', 'empresa_id', 'evento_id'),
    #     Index('idx_pedido_mesa_numero', 'numero_pedido'),
    # )

class ItemPedidoMesa(Base):
    """Itens específicos dos pedidos de mesa"""
    __tablename__ = "itens_pedido_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_mesa.id"), nullable=False)
    
    # Informações do produto
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    nome_produto = Column(String(255), nullable=False)
    categoria_produto = Column(String(100))
    codigo_produto = Column(String(50))
    
    # Quantidade e valores
    quantidade = Column(Numeric(10, 3), nullable=False, default=1)
    valor_unitario = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    
    # Status individual do item
    status = Column(Enum(StatusItemPedido), default=StatusItemPedido.PENDENTE)
    
    # Customizações e observações
    observacoes = Column(Text)
    modificacoes = Column(JSON, default=list)  # Lista de modificações
    ingredientes_removidos = Column(JSON, default=list)
    ingredientes_adicionados = Column(JSON, default=list)
    
    # Controle de preparo
    tempo_estimado_item = Column(Integer, default=0)  # em minutos
    estacao_preparo = Column(Enum(TipoEstacaoKDS), default=TipoEstacaoKDS.GERAL)
    prioridade_preparo = Column(Integer, default=1)  # 1=normal, 5=urgente
    
    # Tempos de controle
    data_inicio_preparo = Column(DateTime(timezone=True))
    data_conclusao_preparo = Column(DateTime(timezone=True))
    data_entrega = Column(DateTime(timezone=True))
    
    # Responsáveis
    responsavel_preparo_id = Column(Integer, ForeignKey("usuarios.id"))
    responsavel_entrega_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    pedido = relationship("PedidoMesa", back_populates="itens")
    responsavel_preparo = relationship("Usuario", foreign_keys=[responsavel_preparo_id])
    responsavel_entrega = relationship("Usuario", foreign_keys=[responsavel_entrega_id])
    
    # Índices
    # __table_args__ = ( # COMENTADO - índices criados via SQL
    # Index('idx_item_pedido_status_estacao', 'status', 'estacao_preparo'),
    # Index('idx_item_pedido_tempos', 'data_inicio_preparo', 'data_conclusao_preparo'),
    # )

# ================================================================================
# MODELOS PARA KDS (KITCHEN DISPLAY SYSTEM)
# ================================================================================

class EstacaoKDS(Base):
    """Estações de trabalho na cozinha"""
    __tablename__ = "estacoes_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoEstacaoKDS), nullable=False)
    descricao = Column(Text)
    
    # Configurações da estação
    cor_tema = Column(String(7), default="#2563eb")  # Cor para identificação
    icone = Column(String(50))
    posicao_ordem = Column(Integer, default=1)  # Ordem de exibição
    
    # Capacidade e limitações
    capacidade_maxima_pedidos = Column(Integer, default=10)
    tempo_alerta_atraso = Column(Integer, default=30)  # minutos
    tempo_alerta_urgente = Column(Integer, default=45)  # minutos
    
    # Configurações de display
    configuracoes_tela = Column(JSON, default=dict)  # Configurações específicas
    ativa = Column(Boolean, default=True)
    
    # Localização física
    setor_cozinha = Column(String(100))  # ex: "Cozinha Principal", "Bar"
    equipamentos = Column(JSON, default=list)  # Lista de equipamentos
    
    # Controle
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    notificacoes = relationship("NotificacaoKDS", back_populates="estacao")

class ConfiguracaoKDS(Base):
    """Configurações globais do sistema KDS"""
    __tablename__ = "configuracoes_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação
    nome_configuracao = Column(String(100), nullable=False)
    tipo_configuracao = Column(String(50), nullable=False)  # ex: "global", "estacao", "produto"
    
    # Configurações gerais
    tempo_alerta_padrao = Column(Integer, default=30)  # minutos
    tempo_critico_padrao = Column(Integer, default=45)  # minutos
    som_notificacao = Column(Boolean, default=True)
    vibrar_notificacao = Column(Boolean, default=False)
    
    # Configurações de display
    tamanho_fonte = Column(String(10), default="medium")
    tema_cor = Column(String(20), default="blue")
    mostrar_fotos_produtos = Column(Boolean, default=True)
    mostrar_tempo_decorrido = Column(Boolean, default=True)
    mostrar_observacoes = Column(Boolean, default=True)
    
    # Configurações de auto-atualização
    intervalo_atualizacao = Column(Integer, default=5)  # segundos
    auto_refresh = Column(Boolean, default=True)
    notificacao_tempo_real = Column(Boolean, default=True)
    
    # Configurações avançadas
    configuracoes_extras = Column(JSON, default=dict)
    
    # Controle
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

class NotificacaoKDS(Base):
    """Notificações e alertas do sistema KDS"""
    __tablename__ = "notificacoes_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação da notificação
    tipo = Column(Enum(TipoNotificacaoKDS), nullable=False)
    titulo = Column(String(255), nullable=False)
    mensagem = Column(Text, nullable=False)
    urgencia = Column(Enum(PrioridadePedido), default=PrioridadePedido.NORMAL)
    
    # Vinculações
    pedido_id = Column(Integer, ForeignKey("pedidos_mesa.id"))
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    
    # Status da notificação
    lida = Column(Boolean, default=False)
    data_leitura = Column(DateTime(timezone=True))
    usuario_leitura_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Configurações de exibição
    som = Column(Boolean, default=True)
    vibrar = Column(Boolean, default=False)
    cor_destaque = Column(String(7), default="#ef4444")  # Vermelho para alertas
    
    # Metadados
    dados_extras = Column(JSON, default=dict)  # Dados adicionais da notificação
    
    # Controle temporal
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_expiracao = Column(DateTime(timezone=True))  # Quando a notificação expira
    
    # Relacionamentos
    pedido = relationship("PedidoMesa", back_populates="notificacoes")
    estacao = relationship("EstacaoKDS", back_populates="notificacoes")
    mesa = relationship("Mesa")
    usuario_leitura = relationship("Usuario", foreign_keys=[usuario_leitura_id])
    
    # Índices
    # __table_args__ = ( # COMENTADO - índices criados via SQL
    # Index('idx_notificacao_tipo_status', 'tipo', 'lida'),
    # Index('idx_notificacao_data_urgencia', 'data_criacao', 'urgencia'),
    # Index('idx_notificacao_estacao', 'estacao_id', 'lida'),
    # )

# ================================================================================
# MODELOS PARA RELATÓRIOS E ANALYTICS
# ================================================================================

class RelatorioTempoMesa(Base):
    """Relatórios de tempo e performance das mesas"""
    __tablename__ = "relatorios_tempo_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Período do relatório
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    
    # Identificação
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    numero_mesa = Column(String(10))
    
    # Métricas de tempo
    tempo_medio_preparo = Column(Integer, default=0)  # minutos
    tempo_medio_entrega = Column(Integer, default=0)  # minutos
    tempo_medio_ocupacao = Column(Integer, default=0)  # minutos
    tempo_total_ocupada = Column(Integer, default=0)  # minutos
    
    # Métricas de pedidos
    total_pedidos = Column(Integer, default=0)
    pedidos_no_prazo = Column(Integer, default=0)
    pedidos_atrasados = Column(Integer, default=0)
    pedidos_cancelados = Column(Integer, default=0)
    
    # Métricas financeiras
    faturamento_total = Column(Numeric(10, 2), default=0)
    ticket_medio = Column(Numeric(10, 2), default=0)
    
    # Métricas de eficiência
    taxa_ocupacao = Column(Numeric(5, 2), default=0)  # Percentual
    taxa_sucesso = Column(Numeric(5, 2), default=0)   # Percentual de pedidos no prazo
    indice_satisfacao = Column(Numeric(5, 2), default=0)  # Baseado em feedback
    
    # Controle
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    gerado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    mesa = relationship("Mesa")
    
    # Índices
    # __table_args__ = ( # COMENTADO - índices criados via SQL
    # Index('idx_relatorio_tempo_periodo', 'data_inicio', 'data_fim'),
    # Index('idx_relatorio_tempo_mesa', 'mesa_id', 'data_inicio'),
    # )

class LogEventoKDS(Base):
    """Log de eventos do sistema KDS para auditoria"""
    __tablename__ = "logs_eventos_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação do evento
    tipo_evento = Column(String(50), nullable=False)  # ex: "pedido_criado", "status_alterado"
    descricao = Column(Text, nullable=False)
    
    # Vinculações
    pedido_id = Column(Integer, ForeignKey("pedidos_mesa.id"))
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    
    # Dados do evento
    dados_antes = Column(JSON, default=dict)  # Estado anterior
    dados_depois = Column(JSON, default=dict)  # Estado posterior
    metadados = Column(JSON, default=dict)     # Metadados adicionais
    
    # Informações técnicas
    ip_origem = Column(String(45))
    user_agent = Column(Text)
    
    # Controle temporal
    data_evento = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    pedido = relationship("PedidoMesa")
    mesa = relationship("Mesa")
    usuario = relationship("Usuario")
    estacao = relationship("EstacaoKDS")
    
    # Índices
    # __table_args__ = ( # COMENTADO - índices criados via SQL
    # Index('idx_log_evento_tipo_data', 'tipo_evento', 'data_evento'),
    # Index('idx_log_evento_pedido', 'pedido_id', 'data_evento'),
    # Index('idx_log_evento_usuario', 'usuario_id', 'data_evento'),
    # )
