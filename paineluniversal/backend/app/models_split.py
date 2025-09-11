"""
Modelos para Sistema de Split de Pagamentos
Baseado na análise do MEEP - Divisão automática de receitas
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base


class TipoCalculoSplit(enum.Enum):
    """Tipos de cálculo para split"""
    PERCENTUAL = "percentual"
    VALOR_FIXO = "valor_fixo"
    VALOR_POR_ITEM = "valor_por_item"


class TipoBeneficiario(enum.Enum):
    """Tipos de beneficiários do split"""
    EMPRESA = "empresa"
    FORNECEDOR = "fornecedor"
    PARCEIRO = "parceiro"
    PROMOTER = "promoter"
    VENDEDOR = "vendedor"
    AFILIADO = "afiliado"


class StatusSplit(enum.Enum):
    """Status da execução do split"""
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    PAGO = "pago"
    ERRO = "erro"
    CANCELADO = "cancelado"


class SplitRule(Base):
    """Regras de split configuradas para eventos ou produtos"""
    __tablename__ = "split_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    
    # Associação com evento ou global
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Beneficiário
    beneficiario_tipo = Column(SQLEnum(TipoBeneficiario), nullable=False)
    beneficiario_id = Column(String(100), nullable=False)  # ID do usuário, fornecedor, etc
    beneficiario_nome = Column(String(200), nullable=False)
    
    # Dados bancários/pagamento do beneficiário
    dados_pagamento = Column(JSON)  # {banco, agencia, conta, pix, etc}
    
    # Regra de cálculo
    tipo_calculo = Column(SQLEnum(TipoCalculoSplit), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)  # Percentual ou valor fixo
    
    # Condições para aplicar a regra
    condicoes = Column(JSON, default={})  
    # Ex: {
    #   "produto_ids": [1, 2, 3],
    #   "categoria_ids": [10, 20],
    #   "min_valor": 100.00,
    #   "max_valor": 1000.00,
    #   "dias_semana": [0, 6],  # Domingo e Sábado
    #   "horario_inicio": "18:00",
    #   "horario_fim": "23:00"
    # }
    
    # Prioridade (regras com maior prioridade são aplicadas primeiro)
    prioridade = Column(Integer, default=0)
    
    # Limites
    valor_minimo = Column(Numeric(10, 2), default=0)  # Valor mínimo para executar o split
    valor_maximo = Column(Numeric(10, 2), nullable=True)  # Valor máximo do split
    
    # Controle
    ativo = Column(Boolean, default=True)
    data_inicio = Column(DateTime(timezone=True), nullable=True)
    data_fim = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="split_rules")
    empresa = relationship("Empresa", back_populates="split_rules")
    execucoes = relationship("SplitExecution", back_populates="rule")


class SplitExecution(Base):
    """Execuções de split realizadas"""
    __tablename__ = "split_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Referência à venda
    venda_id = Column(Integer, ForeignKey("vendas_pdv.id"), nullable=False)
    
    # Referência à regra aplicada
    rule_id = Column(Integer, ForeignKey("split_rules.id"), nullable=False)
    
    # Valores
    valor_venda = Column(Numeric(10, 2), nullable=False)  # Valor total da venda
    valor_base_calculo = Column(Numeric(10, 2), nullable=False)  # Base para cálculo
    valor_split = Column(Numeric(10, 2), nullable=False)  # Valor calculado do split
    valor_taxa = Column(Numeric(10, 2), default=0)  # Taxa cobrada pelo gateway
    valor_liquido = Column(Numeric(10, 2), nullable=False)  # Valor líquido a receber
    
    # Detalhes do beneficiário (snapshot no momento da execução)
    beneficiario_tipo = Column(SQLEnum(TipoBeneficiario))
    beneficiario_id = Column(String(100))
    beneficiario_nome = Column(String(200))
    dados_pagamento = Column(JSON)
    
    # Status e processamento
    status = Column(SQLEnum(StatusSplit), default=StatusSplit.PENDENTE)
    
    # Resposta do gateway de pagamento
    gateway_usado = Column(String(50))  # stripe, pagseguro, mercadopago
    gateway_transaction_id = Column(String(200))
    gateway_response = Column(JSON)
    
    # Datas
    data_execucao = Column(DateTime(timezone=True), server_default=func.now())
    data_processamento = Column(DateTime(timezone=True))
    data_pagamento = Column(DateTime(timezone=True))
    data_erro = Column(DateTime(timezone=True))
    
    # Erro (se houver)
    erro_mensagem = Column(Text)
    tentativas = Column(Integer, default=0)
    
    # Relacionamentos
    venda = relationship("VendaPDV", back_populates="splits")
    rule = relationship("SplitRule", back_populates="execucoes")


class SplitAgregado(Base):
    """Agregação de splits por período para relatórios"""
    __tablename__ = "split_agregados"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Período
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=False)
    
    # Beneficiário
    beneficiario_tipo = Column(SQLEnum(TipoBeneficiario))
    beneficiario_id = Column(String(100))
    beneficiario_nome = Column(String(200))
    
    # Totais
    quantidade_splits = Column(Integer, default=0)
    valor_total_bruto = Column(Numeric(10, 2), default=0)
    valor_total_taxas = Column(Numeric(10, 2), default=0)
    valor_total_liquido = Column(Numeric(10, 2), default=0)
    
    # Status
    quantidade_pagos = Column(Integer, default=0)
    quantidade_pendentes = Column(Integer, default=0)
    quantidade_erros = Column(Integer, default=0)
    
    # Metadados
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())


class ConfiguracaoSplitGlobal(Base):
    """Configurações globais do sistema de split"""
    __tablename__ = "configuracao_split_global"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), unique=True)
    
    # Configurações de processamento
    processar_automaticamente = Column(Boolean, default=True)
    horario_processamento = Column(String(5), default="03:00")  # HH:MM
    dias_para_processar = Column(Integer, default=1)  # D+1
    
    # Taxas padrão
    taxa_split_percentual = Column(Numeric(5, 2), default=2.5)  # Taxa cobrada pelo sistema
    taxa_split_fixa = Column(Numeric(10, 2), default=0)
    
    # Limites
    valor_minimo_split = Column(Numeric(10, 2), default=10.00)
    valor_maximo_split_diario = Column(Numeric(10, 2), default=50000.00)
    
    # Gateways habilitados
    gateways_habilitados = Column(JSON, default=["stripe", "pagseguro"])
    gateway_padrao = Column(String(50), default="stripe")
    
    # Notificações
    notificar_beneficiarios = Column(Boolean, default=True)
    emails_notificacao = Column(JSON, default=[])
    
    # Auditoria
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")


class HistoricoSplit(Base):
    """Histórico de todas as operações de split para auditoria"""
    __tablename__ = "historico_split"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Referências
    execution_id = Column(Integer, ForeignKey("split_executions.id"), nullable=True)
    rule_id = Column(Integer, ForeignKey("split_rules.id"), nullable=True)
    
    # Ação realizada
    acao = Column(String(50))  # criacao_regra, execucao_split, pagamento, erro, cancelamento
    descricao = Column(Text)
    
    # Dados da ação (snapshot)
    dados_acao = Column(JSON)
    
    # Usuário que realizou a ação
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    ip_origem = Column(String(45))
    
    # Timestamp
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    execution = relationship("SplitExecution")
    rule = relationship("SplitRule")
    usuario = relationship("Usuario")