from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class MEEPEvento(Base):
    __tablename__ = "meep_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    meep_id = Column(String(100), unique=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    
    # Dados do MEEP
    nome = Column(String(255), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    local = Column(String(500))
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Métricas
    total_inscritos = Column(Integer, default=0)
    total_presentes = Column(Integer, default=0)
    total_vendas = Column(Float, default=0.0)
    taxa_conversao = Column(Float, default=0.0)
    
    # Dados JSON flexíveis
    dados_completos = Column(JSON)
    metricas_detalhadas = Column(JSON)
    
    # Controle
    ultima_sincronizacao = Column(DateTime, default=datetime.utcnow)
    sincronizado = Column(Boolean, default=False)
    erro_sincronizacao = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    participantes = relationship("MEEPParticipante", back_populates="meep_evento")
    capturas = relationship("MEEPCaptura", back_populates="meep_evento")

class MEEPParticipante(Base):
    __tablename__ = "meep_participantes"
    
    id = Column(Integer, primary_key=True, index=True)
    meep_evento_id = Column(Integer, ForeignKey("meep_eventos.id"))
    
    # Dados do participante
    cpf = Column(String(11), index=True)
    nome = Column(String(255))
    email = Column(String(255))
    telefone = Column(String(20))
    
    # Status
    inscrito = Column(Boolean, default=True)
    presente = Column(Boolean, default=False)
    pagamento_status = Column(String(50))
    valor_pago = Column(Float, default=0.0)
    
    # Dados adicionais
    dados_extras = Column(JSON)
    
    # Timestamps
    data_inscricao = Column(DateTime)
    data_checkin = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    meep_evento = relationship("MEEPEvento", back_populates="participantes")

class MEEPCaptura(Base):
    __tablename__ = "meep_capturas"
    
    id = Column(Integer, primary_key=True, index=True)
    meep_evento_id = Column(Integer, ForeignKey("meep_eventos.id"))
    
    # Dados da captura
    tipo = Column(String(50))
    url = Column(String(500))
    status = Column(String(50))
    
    # Resultados
    total_registros = Column(Integer, default=0)
    registros_processados = Column(Integer, default=0)
    dados_capturados = Column(JSON)
    
    # Controle
    iniciado_em = Column(DateTime)
    finalizado_em = Column(DateTime)
    erro_mensagem = Column(Text)
    tentativas = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    meep_evento = relationship("MEEPEvento", back_populates="capturas")

class MEEPAnalytics(Base):
    __tablename__ = "meep_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    
    # Métricas agregadas
    periodo = Column(String(50))
    data_referencia = Column(DateTime)
    
    # KPIs
    total_eventos = Column(Integer, default=0)
    total_participantes = Column(Integer, default=0)
    taxa_ocupacao = Column(Float, default=0.0)
    receita_total = Column(Float, default=0.0)
    ticket_medio = Column(Float, default=0.0)
    
    # Análises
    analise_demografica = Column(JSON)
    analise_geografica = Column(JSON)
    analise_temporal = Column(JSON)
    previsoes = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
