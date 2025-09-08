"""
Clean models_extended.py without duplicated tables from models.py
This file contains only the NEW models that don't conflict with existing ones
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum, Date, Float, JSON, Time, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from .models import Usuario, Evento, Produto, CategoriaProduto  # Import existing models
import enum
from datetime import datetime

# ====== KDS SYSTEM - NEW MODELS ======

class TipoEstacaoKDS(enum.Enum):
    COZINHA = "cozinha"
    BAR = "bar"
    EXPEDITOR = "expeditor"
    ESPECIAL = "especial"

class StatusPedidoKDS(enum.Enum):
    PENDENTE = "PENDENTE"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

class EstacaoKDS(Base):
    __tablename__ = "estacoes_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoEstacaoKDS), nullable=False, default=TipoEstacaoKDS.COZINHA)
    descricao = Column(Text)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    ativo = Column(Boolean, default=True)
    ordem_exibicao = Column(Integer, default=1)
    configuracoes = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    evento = relationship("Evento")
    pedidos = relationship("PedidoKDS", back_populates="estacao")

class PedidoKDS(Base):
    __tablename__ = "pedidos_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(50), nullable=False)
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"), nullable=False)
    status = Column(Enum(StatusPedidoKDS), nullable=False, default=StatusPedidoKDS.PENDENTE)
    tempo_estimado_minutos = Column(Integer)
    observacoes = Column(Text)
    comanda_id = Column(Integer)  # Will link to comandas when available
    venda_id = Column(Integer)    # Will link to vendas when available
    prioridade = Column(String(20), default='NORMAL')
    created_at = Column(DateTime, server_default=func.now())
    iniciado_em = Column(DateTime)
    finalizado_em = Column(DateTime)
    entregue_em = Column(DateTime)
    
    # Relationships
    estacao = relationship("EstacaoKDS", back_populates="pedidos")
    itens = relationship("ItemPedidoKDS", back_populates="pedido")

class ItemPedidoKDS(Base):
    __tablename__ = "itens_pedido_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    produto_nome = Column(String(200), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    observacoes = Column(Text)
    pronto = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    pedido = relationship("PedidoKDS", back_populates="itens")
    produto = relationship("Produto")

# ====== TABLE MANAGEMENT SYSTEM - NEW MODELS ======

class StatusMesa(enum.Enum):
    LIVRE = "LIVRE"
    OCUPADA = "OCUPADA"
    RESERVADA = "RESERVADA"
    MANUTENCAO = "MANUTENCAO"
    INATIVA = "INATIVA"

class TipoMesa(enum.Enum):
    NORMAL = "NORMAL"
    VIP = "VIP"
    REDONDA = "REDONDA"
    RETANGULAR = "RETANGULAR"
    BALCAO = "BALCAO"
    EXTERNA = "EXTERNA"

class MesaEvento(Base):
    __tablename__ = "mesas_evento"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False)
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoMesa), nullable=False, default=TipoMesa.NORMAL)
    status = Column(Enum(StatusMesa), nullable=False, default=StatusMesa.LIVRE)
    capacidade = Column(Integer, nullable=False, default=4)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    posicao_x = Column(Integer, default=0)
    posicao_y = Column(Integer, default=0)
    largura = Column(Integer, default=100)
    altura = Column(Integer, default=100)
    rotacao = Column(Integer, default=0)
    cor = Column(String(7), default='#3B82F6')
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    ocupada_em = Column(DateTime)
    liberada_em = Column(DateTime)
    reservada_em = Column(DateTime)
    
    # Relationships
    evento = relationship("Evento")

# Note: Other models from models_extended.py that conflict with models.py are NOT included here
# This ensures no table duplication errors while keeping the new KDS and Tables functionality