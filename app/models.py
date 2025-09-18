from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Modelos baseados na documentação completa

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200))
    cnpj = Column(String(20), unique=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200))
    email = Column(String(200), unique=True)
    cpf = Column(String(11), unique=True)
    senha = Column(String(255))
    tipo = Column(String(50))
    ativo = Column(Boolean, default=True)

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200))
    data = Column(DateTime)
    local = Column(String(500))
    capacidade = Column(Integer)
    preco = Column(Float)
    status = Column(String(50))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))

class Lista(Base):
    __tablename__ = "listas"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    promoter_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo = Column(String(50))
    limite = Column(Integer)

class Transacao(Base):
    __tablename__ = "transacoes"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50))
    valor = Column(Float)
    status = Column(String(50))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    data = Column(DateTime, default=datetime.now)

class Checkin(Base):
    __tablename__ = "checkins"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    data_hora = Column(DateTime, default=datetime.now)
    metodo = Column(String(50))

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200))
    preco = Column(Float)
    estoque = Column(Integer)
    categoria = Column(String(100))
    ativo = Column(Boolean, default=True)

class VendaPDV(Base):
    __tablename__ = "vendas_pdv"
    id = Column(Integer, primary_key=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    valor_total = Column(Float)
    forma_pagamento = Column(String(50))
    data = Column(DateTime, default=datetime.now)

class MEEPIntegration(Base):
    __tablename__ = "meep_integrations"
    id = Column(Integer, primary_key=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    meep_event_id = Column(String(100))
    status = Column(String(50))
    sync_data = Column(JSON)
    ultimo_sync = Column(DateTime)
