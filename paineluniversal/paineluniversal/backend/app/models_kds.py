"""
Modelos para KDS (Kitchen Display System)
Sistema de gerenciamento de pedidos em tempo real
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, time
import enum
from .database import Base


class StatusPedido(enum.Enum):
    """Status do pedido no KDS"""
    RECEBIDO = "recebido"
    VISUALIZADO = "visualizado"
    PREPARANDO = "preparando"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class StatusItemPedido(enum.Enum):
    """Status individual de cada item"""
    PENDENTE = "pendente"
    PREPARANDO = "preparando"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class TipoPedido(enum.Enum):
    """Tipo de pedido"""
    BALCAO = "balcao"
    MESA = "mesa"
    DELIVERY = "delivery"
    RETIRADA = "retirada"
    DRIVE_THRU = "drive_thru"


class PrioridadePedido(enum.Enum):
    """Prioridade do pedido"""
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class SetorPreparo(Base):
    """Setores de preparo (cozinha, bar, sobremesas, etc)"""
    __tablename__ = "kds_setores_preparo"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    cor_identificacao = Column(String(7), default="#000000")  # Cor hex para identificação visual
    
    # Configurações do setor
    tempo_preparo_padrao = Column(Integer, default=15)  # Minutos
    alerta_tempo_excedido = Column(Boolean, default=True)
    som_notificacao = Column(String(100), default="default")  # Nome do arquivo de som
    
    # Impressora dedicada (opcional)
    impressora_id = Column(Integer, ForeignKey("impressoras.id"), nullable=True)
    
    # Capacidade e limites
    capacidade_simultanea = Column(Integer, default=10)  # Quantos pedidos simultâneos
    tempo_maximo_espera = Column(Integer, default=30)  # Minutos antes de alerta crítico
    
    # Status
    ativo = Column(Boolean, default=True)
    online = Column(Boolean, default=False)  # Se tem algum terminal conectado
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    produtos = relationship("ProdutoSetor", back_populates="setor")
    pedidos = relationship("PedidoKDS", back_populates="setor_principal")
    terminais = relationship("TerminalKDS", back_populates="setor")


class PedidoKDS(Base):
    """Pedido no sistema KDS"""
    __tablename__ = "kds_pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(50), unique=True, nullable=False, index=True)
    
    # Referência à venda original
    venda_id = Column(Integer, ForeignKey("vendas_pdv.id"), nullable=True)
    
    # Tipo e origem
    tipo = Column(SQLEnum(TipoPedido), default=TipoPedido.BALCAO)
    origem = Column(String(50))  # PDV, App, Site, etc
    
    # Cliente
    cliente_nome = Column(String(200))
    cliente_telefone = Column(String(20))
    mesa_numero = Column(String(20), nullable=True)
    
    # Setor principal (pode ter itens em múltiplos setores)
    setor_principal_id = Column(Integer, ForeignKey("kds_setores_preparo.id"))
    
    # Status e prioridade
    status = Column(SQLEnum(StatusPedido), default=StatusPedido.RECEBIDO)
    prioridade = Column(SQLEnum(PrioridadePedido), default=PrioridadePedido.NORMAL)
    
    # Observações
    observacoes = Column(Text)
    observacoes_cozinha = Column(Text)  # Observações específicas para a cozinha
    
    # Tempos
    tempo_estimado_total = Column(Integer)  # Minutos
    tempo_decorrido = Column(Integer, default=0)  # Minutos desde o recebimento
    
    # Timestamps detalhados
    data_pedido = Column(DateTime(timezone=True), server_default=func.now())
    data_visualizado = Column(DateTime(timezone=True))
    data_inicio_preparo = Column(DateTime(timezone=True))
    data_pronto = Column(DateTime(timezone=True))
    data_entrega = Column(DateTime(timezone=True))
    data_cancelamento = Column(DateTime(timezone=True))
    
    # Operadores
    operador_pedido_id = Column(Integer, ForeignKey("usuarios.id"))
    operador_preparo_id = Column(Integer, ForeignKey("usuarios.id"))
    operador_entrega_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Alertas
    alerta_atraso = Column(Boolean, default=False)
    alerta_prioritario = Column(Boolean, default=False)
    
    # Relacionamentos
    venda = relationship("VendaPDV", back_populates="pedido_kds")
    setor_principal = relationship("SetorPreparo", back_populates="pedidos")
    itens = relationship("ItemPedidoKDS", back_populates="pedido", cascade="all, delete-orphan")
    historico = relationship("HistoricoPedidoKDS", back_populates="pedido")


class ItemPedidoKDS(Base):
    """Item individual do pedido no KDS"""
    __tablename__ = "kds_itens_pedido"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("kds_pedidos.id"), nullable=False)
    
    # Produto
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    produto_nome = Column(String(200), nullable=False)
    quantidade = Column(Integer, nullable=False)
    
    # Setor de preparo deste item
    setor_preparo_id = Column(Integer, ForeignKey("kds_setores_preparo.id"), nullable=False)
    
    # Personalizações
    modificacoes = Column(JSON)  # Ex: ["Sem cebola", "Ponto mal passado"]
    observacoes = Column(Text)
    
    # Status e tempos
    status = Column(SQLEnum(StatusItemPedido), default=StatusItemPedido.PENDENTE)
    tempo_estimado = Column(Integer)  # Minutos
    tempo_decorrido = Column(Integer, default=0)
    
    # Ordem de preparo (para items que precisam ser preparados em sequência)
    ordem_preparo = Column(Integer, default=0)
    aguardando_item_id = Column(Integer, ForeignKey("kds_itens_pedido.id"), nullable=True)
    
    # Timestamps
    data_recebido = Column(DateTime(timezone=True), server_default=func.now())
    data_inicio_preparo = Column(DateTime(timezone=True))
    data_pronto = Column(DateTime(timezone=True))
    data_entrega = Column(DateTime(timezone=True))
    
    # Operador que preparou
    preparado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    pedido = relationship("PedidoKDS", back_populates="itens")
    produto = relationship("Produto")
    setor_preparo = relationship("SetorPreparo")
    preparado_por = relationship("Usuario")
    aguardando_item = relationship("ItemPedidoKDS", remote_side=[id])


class ProdutoSetor(Base):
    """Associação de produtos com setores de preparo"""
    __tablename__ = "kds_produtos_setor"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    setor_id = Column(Integer, ForeignKey("kds_setores_preparo.id"), nullable=False)
    
    # Tempo específico de preparo neste setor
    tempo_preparo = Column(Integer, nullable=False)  # Minutos
    
    # Se é o setor principal para este produto
    setor_principal = Column(Boolean, default=True)
    
    # Relacionamentos
    produto = relationship("Produto")
    setor = relationship("SetorPreparo", back_populates="produtos")


class TerminalKDS(Base):
    """Terminal/Display do KDS"""
    __tablename__ = "kds_terminais"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    
    # Setor associado
    setor_id = Column(Integer, ForeignKey("kds_setores_preparo.id"), nullable=False)
    
    # Tipo de terminal
    tipo = Column(String(50), default="display")  # display, expedidor, gerencial
    
    # Configurações de exibição
    configuracoes = Column(JSON, default={
        "itens_por_pagina": 6,
        "tempo_auto_refresh": 30,  # segundos
        "mostrar_tempo_decorrido": True,
        "mostrar_modificacoes": True,
        "som_habilitado": True,
        "modo_noturno": False,
        "tamanho_fonte": "medio"
    })
    
    # Status
    online = Column(Boolean, default=False)
    ultimo_heartbeat = Column(DateTime(timezone=True))
    ip_address = Column(String(45))
    
    # Estatísticas
    total_pedidos_visualizados = Column(Integer, default=0)
    total_pedidos_preparados = Column(Integer, default=0)
    tempo_medio_preparo = Column(Integer, default=0)  # Minutos
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    ultimo_login = Column(DateTime(timezone=True))
    
    # Relacionamentos
    setor = relationship("SetorPreparo", back_populates="terminais")
    usuario_logado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario_logado = relationship("Usuario")


class HistoricoPedidoKDS(Base):
    """Histórico de ações no pedido"""
    __tablename__ = "kds_historico_pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("kds_pedidos.id"), nullable=False)
    
    # Ação realizada
    acao = Column(String(50), nullable=False)  # recebido, visualizado, iniciado, pronto, entregue, cancelado
    descricao = Column(Text)
    
    # Item específico (se aplicável)
    item_id = Column(Integer, ForeignKey("kds_itens_pedido.id"), nullable=True)
    
    # Usuário e terminal
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    terminal_id = Column(Integer, ForeignKey("kds_terminais.id"))
    
    # Timestamp
    data_acao = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    pedido = relationship("PedidoKDS", back_populates="historico")
    item = relationship("ItemPedidoKDS")
    usuario = relationship("Usuario")
    terminal = relationship("TerminalKDS")


class ConfiguracaoKDS(Base):
    """Configurações globais do KDS"""
    __tablename__ = "kds_configuracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), unique=True)
    
    # Tempos padrão (em minutos)
    tempo_preparo_padrao = Column(Integer, default=15)
    tempo_alerta_amarelo = Column(Integer, default=10)  # Alerta quando passar de X minutos
    tempo_alerta_vermelho = Column(Integer, default=20)  # Alerta crítico
    
    # Comportamentos
    auto_marcar_visualizado = Column(Boolean, default=False)  # Marcar como visualizado automaticamente
    auto_marcar_pronto = Column(Boolean, default=False)  # Marcar como pronto quando todos os itens estiverem prontos
    exigir_confirmacao_entrega = Column(Boolean, default=True)
    
    # Notificações
    notificar_novo_pedido = Column(Boolean, default=True)
    notificar_pedido_atrasado = Column(Boolean, default=True)
    notificar_pedido_prioritario = Column(Boolean, default=True)
    
    # Sons
    volume_notificacao = Column(Integer, default=70)  # 0-100
    som_novo_pedido = Column(String(100), default="bell.mp3")
    som_pedido_atrasado = Column(String(100), default="alert.mp3")
    som_pedido_pronto = Column(String(100), default="done.mp3")
    
    # Horários de funcionamento
    horario_abertura = Column(Time, default=time(8, 0))
    horario_fechamento = Column(Time, default=time(22, 0))
    
    # Integrações
    integrar_com_pdv = Column(Boolean, default=True)
    integrar_com_delivery = Column(Boolean, default=False)
    webhook_novo_pedido = Column(String(500))
    webhook_pedido_pronto = Column(String(500))
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")


class MetricasKDS(Base):
    """Métricas e estatísticas do KDS"""
    __tablename__ = "kds_metricas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Período
    data = Column(DateTime(timezone=True), nullable=False)
    setor_id = Column(Integer, ForeignKey("kds_setores_preparo.id"), nullable=True)
    
    # Métricas de pedidos
    total_pedidos = Column(Integer, default=0)
    pedidos_no_prazo = Column(Integer, default=0)
    pedidos_atrasados = Column(Integer, default=0)
    pedidos_cancelados = Column(Integer, default=0)
    
    # Métricas de tempo (em minutos)
    tempo_medio_preparo = Column(Float, default=0)
    tempo_minimo_preparo = Column(Integer, default=0)
    tempo_maximo_preparo = Column(Integer, default=0)
    tempo_medio_espera = Column(Float, default=0)
    
    # Métricas de eficiência
    taxa_cumprimento_prazo = Column(Float, default=0)  # Percentual
    taxa_cancelamento = Column(Float, default=0)  # Percentual
    
    # Picos de demanda
    horario_pico = Column(Time)
    pedidos_hora_pico = Column(Integer, default=0)
    
    # Relacionamentos
    setor = relationship("SetorPreparo")