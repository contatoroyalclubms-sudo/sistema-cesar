from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, JSON, Numeric, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any, List

Base = declarative_base()

# Enums para o sistema de comunicação
class TipoCanal(PyEnum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SISTEMA = "sistema"
    CHAT_INTERNO = "chat_interno"

class StatusCanal(PyEnum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    CONFIGURANDO = "configurando"
    ERRO = "erro"
    SUSPENSO = "suspenso"

class TipoTemplate(PyEnum):
    MARKETING = "marketing"
    TRANSACIONAL = "transacional"
    NOTIFICACAO = "notificacao"
    PROMOCIONAL = "promocional"
    OPERACIONAL = "operacional"

class StatusMensagem(PyEnum):
    PENDENTE = "pendente"
    ENVIANDO = "enviando"
    ENVIADA = "enviada"
    ENTREGUE = "entregue"
    LIDA = "lida"
    ERRO = "erro"
    REJEITADA = "rejeitada"

class TipoCampanha(PyEnum):
    IMEDIATA = "imediata"
    AGENDADA = "agendada"
    RECORRENTE = "recorrente"
    GATILHO = "gatilho"
    AB_TEST = "ab_test"

class StatusCampanha(PyEnum):
    RASCUNHO = "rascunho"
    AGENDADA = "agendada"
    ATIVA = "ativa"
    PAUSADA = "pausada"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"

class TipoEvento(PyEnum):
    NOVO_PEDIDO = "novo_pedido"
    PAGAMENTO_APROVADO = "pagamento_aprovado"
    PEDIDO_PRONTO = "pedido_pronto"
    ANIVERSARIO = "aniversario"
    CARRINHO_ABANDONADO = "carrinho_abandonado"
    NOVA_PROMOCAO = "nova_promocao"
    FEEDBACK_PEDIDO = "feedback_pedido"
    LEMBRETE_EVENTO = "lembrete_evento"
    PONTO_FIDELIDADE = "ponto_fidelidade"
    NIVEL_FIDELIDADE = "nivel_fidelidade"

class PrioridadeMensagem(PyEnum):
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    CRITICA = "critica"

# Model para configuração de canais de comunicação
class CanalComunicacao(Base):
    __tablename__ = "canais_comunicacao"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoCanal), nullable=False)
    descricao = Column(Text)
    status = Column(Enum(StatusCanal), default=StatusCanal.CONFIGURANDO)
    
    # Configurações específicas do canal (JSON flexível)
    configuracoes = Column(JSON, default={})
    
    # Limites e configurações
    limite_diario = Column(Integer, default=1000)
    limite_mensal = Column(Integer, default=30000)
    tempo_throttle = Column(Integer, default=1)  # segundos entre envios
    
    # Status operacional
    ativo = Column(Boolean, default=True)
    ultimo_teste = Column(DateTime)
    ultimo_erro = Column(Text)
    
    # Métricas
    total_enviados = Column(Integer, default=0)
    total_entregues = Column(Integer, default=0)
    total_erros = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="canais_comunicacao")
    templates = relationship("TemplateMensagem", back_populates="canal")
    mensagens = relationship("Mensagem", back_populates="canal")
    
    # Índices
    __table_args__ = (
        Index('idx_canal_empresa_tipo', 'empresa_id', 'tipo'),
        Index('idx_canal_status', 'status'),
    )

# Model para templates de mensagens
class TemplateMensagem(Base):
    __tablename__ = "templates_mensagem"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    canal_id = Column(Integer, ForeignKey("canais_comunicacao.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoTemplate), nullable=False)
    assunto = Column(String(200))  # Para email
    conteudo = Column(Text, nullable=False)
    conteudo_html = Column(Text)  # Para emails com HTML
    
    # Variáveis dinâmicas disponíveis
    variaveis = Column(JSON, default=[])  # Lista de variáveis como {nome, cliente, pedido}
    
    # Configurações específicas
    configuracoes = Column(JSON, default={})
    
    # Status e aprovação (para WhatsApp Business)
    aprovado_whatsapp = Column(Boolean, default=False)
    codigo_template_whatsapp = Column(String(100))
    
    # Métricas
    total_usado = Column(Integer, default=0)
    taxa_entrega = Column(Numeric(5, 2), default=0.0)
    taxa_abertura = Column(Numeric(5, 2), default=0.0)
    taxa_clique = Column(Numeric(5, 2), default=0.0)
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="templates_mensagem")
    canal = relationship("CanalComunicacao", back_populates="templates")
    mensagens = relationship("Mensagem", back_populates="template")
    
    # Índices
    __table_args__ = (
        Index('idx_template_empresa_canal', 'empresa_id', 'canal_id'),
        Index('idx_template_tipo', 'tipo'),
    )

# Model para contatos e listas
class ContatoComunicacao(Base):
    __tablename__ = "contatos_comunicacao"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)  # Pode ser contato externo
    
    # Informações de contato
    nome = Column(String(100), nullable=False)
    email = Column(String(100))
    telefone = Column(String(20))
    whatsapp = Column(String(20))
    
    # Dados adicionais
    dados_extras = Column(JSON, default={})  # Campos personalizados
    
    # Preferências de comunicação
    aceita_marketing = Column(Boolean, default=True)
    aceita_promocional = Column(Boolean, default=True)
    aceita_whatsapp = Column(Boolean, default=True)
    aceita_email = Column(Boolean, default=True)
    aceita_sms = Column(Boolean, default=False)
    
    # Segmentação
    tags = Column(JSON, default=[])  # Lista de tags para segmentação
    segmentos = Column(JSON, default=[])  # Segmentos automáticos
    
    # Status
    ativo = Column(Boolean, default=True)
    bloqueado = Column(Boolean, default=False)
    motivo_bloqueio = Column(Text)
    
    # Métricas
    total_mensagens_recebidas = Column(Integer, default=0)
    total_mensagens_abertas = Column(Integer, default=0)
    total_cliques = Column(Integer, default=0)
    ultima_interacao = Column(DateTime)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="contatos_comunicacao")
    cliente = relationship("Cliente", back_populates="contatos_comunicacao")
    mensagens = relationship("Mensagem", back_populates="contato")
    
    # Índices
    __table_args__ = (
        Index('idx_contato_empresa', 'empresa_id'),
        Index('idx_contato_email', 'email'),
        Index('idx_contato_telefone', 'telefone'),
    )

# Model para campanhas de comunicação
class CampanhaComunicacao(Base):
    __tablename__ = "campanhas_comunicacao"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates_mensagem.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo = Column(Enum(TipoCampanha), default=TipoCampanha.IMEDIATA)
    status = Column(Enum(StatusCampanha), default=StatusCampanha.RASCUNHO)
    
    # Agendamento
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    recorrencia = Column(JSON)  # Configuração de recorrência
    
    # Segmentação
    filtros_segmentacao = Column(JSON, default={})
    total_contatos_alvo = Column(Integer, default=0)
    
    # A/B Testing
    variante_a_template_id = Column(Integer, ForeignKey("templates_mensagem.id"))
    variante_b_template_id = Column(Integer, ForeignKey("templates_mensagem.id"))
    percentual_variante_a = Column(Numeric(5, 2), default=50.0)
    
    # Métricas
    total_enviadas = Column(Integer, default=0)
    total_entregues = Column(Integer, default=0)
    total_abertas = Column(Integer, default=0)
    total_cliques = Column(Integer, default=0)
    total_conversoes = Column(Integer, default=0)
    
    # Status de execução
    iniciada_em = Column(DateTime)
    finalizada_em = Column(DateTime)
    pausada_em = Column(DateTime)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="campanhas_comunicacao")
    template = relationship("TemplateMensagem", foreign_keys=[template_id])
    variante_a = relationship("TemplateMensagem", foreign_keys=[variante_a_template_id])
    variante_b = relationship("TemplateMensagem", foreign_keys=[variante_b_template_id])
    mensagens = relationship("Mensagem", back_populates="campanha")
    
    # Índices
    __table_args__ = (
        Index('idx_campanha_empresa', 'empresa_id'),
        Index('idx_campanha_status', 'status'),
        Index('idx_campanha_data', 'data_inicio', 'data_fim'),
    )

# Model para mensagens enviadas
class Mensagem(Base):
    __tablename__ = "mensagens"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    canal_id = Column(Integer, ForeignKey("canais_comunicacao.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates_mensagem.id"), nullable=True)
    campanha_id = Column(Integer, ForeignKey("campanhas_comunicacao.id"), nullable=True)
    contato_id = Column(Integer, ForeignKey("contatos_comunicacao.id"), nullable=False)
    
    # Conteúdo da mensagem
    assunto = Column(String(200))
    conteudo = Column(Text, nullable=False)
    conteudo_html = Column(Text)
    
    # Dados do destinatário
    destinatario = Column(String(100), nullable=False)  # email ou telefone
    nome_destinatario = Column(String(100))
    
    # Status e tracking
    status = Column(Enum(StatusMensagem), default=StatusMensagem.PENDENTE)
    prioridade = Column(Enum(PrioridadeMensagem), default=PrioridadeMensagem.NORMAL)
    tentativas = Column(Integer, default=0)
    max_tentativas = Column(Integer, default=3)
    
    # IDs externos (APIs)
    id_externo = Column(String(100))  # ID da API externa (SendGrid, Twilio, etc.)
    webhook_dados = Column(JSON)  # Dados do webhook
    
    # Timestamps de tracking
    enviada_em = Column(DateTime)
    entregue_em = Column(DateTime)
    aberta_em = Column(DateTime)
    clicada_em = Column(DateTime)
    
    # Erro e debugging
    erro_detalhes = Column(Text)
    dados_debug = Column(JSON)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="mensagens")
    canal = relationship("CanalComunicacao", back_populates="mensagens")
    template = relationship("TemplateMensagem", back_populates="mensagens")
    campanha = relationship("CampanhaComunicacao", back_populates="mensagens")
    contato = relationship("ContatoComunicacao", back_populates="mensagens")
    
    # Índices
    __table_args__ = (
        Index('idx_mensagem_empresa', 'empresa_id'),
        Index('idx_mensagem_status', 'status'),
        Index('idx_mensagem_destinatario', 'destinatario'),
        Index('idx_mensagem_data', 'criado_em'),
    )

# Model para eventos automáticos de notificação
class EventoNotificacao(Base):
    __tablename__ = "eventos_notificacao"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates_mensagem.id"), nullable=False)
    
    # Configuração do evento
    nome = Column(String(100), nullable=False)
    tipo_evento = Column(Enum(TipoEvento), nullable=False)
    descricao = Column(Text)
    
    # Condições de disparo
    condicoes = Column(JSON, default={})  # Condições específicas
    delay_minutos = Column(Integer, default=0)  # Delay para envio
    
    # Filtros de aplicação
    filtros = Column(JSON, default={})  # Filtros para aplicar o evento
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Métricas
    total_disparos = Column(Integer, default=0)
    total_sucessos = Column(Integer, default=0)
    total_erros = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="eventos_notificacao")
    template = relationship("TemplateMensagem")
    
    # Índices
    __table_args__ = (
        Index('idx_evento_empresa', 'empresa_id'),
        Index('idx_evento_tipo', 'tipo_evento'),
    )

# Model para fila de envio (processamento assíncrono)
class FilaEnvio(Base):
    __tablename__ = "fila_envio"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    mensagem_id = Column(Integer, ForeignKey("mensagens.id"), nullable=False)
    
    # Configuração de envio
    prioridade = Column(Enum(PrioridadeMensagem), default=PrioridadeMensagem.NORMAL)
    agendado_para = Column(DateTime, default=func.now())
    
    # Status de processamento
    processado = Column(Boolean, default=False)
    processado_em = Column(DateTime)
    tentativas = Column(Integer, default=0)
    
    # Erro
    erro = Column(Text)
    
    # Worker info
    worker_id = Column(String(100))
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    mensagem = relationship("Mensagem")
    
    # Índices
    __table_args__ = (
        Index('idx_fila_processado', 'processado'),
        Index('idx_fila_prioridade', 'prioridade'),
        Index('idx_fila_agendado', 'agendado_para'),
    )

# Model para métricas detalhadas
class MetricaComunicacao(Base):
    __tablename__ = "metricas_comunicacao"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Referências
    canal_id = Column(Integer, ForeignKey("canais_comunicacao.id"))
    template_id = Column(Integer, ForeignKey("templates_mensagem.id"))
    campanha_id = Column(Integer, ForeignKey("campanhas_comunicacao.id"))
    
    # Período da métrica
    data_referencia = Column(DateTime, nullable=False)
    periodo = Column(String(20), default="diario")  # diario, semanal, mensal
    
    # Métricas
    total_enviadas = Column(Integer, default=0)
    total_entregues = Column(Integer, default=0)
    total_abertas = Column(Integer, default=0)
    total_cliques = Column(Integer, default=0)
    total_conversoes = Column(Integer, default=0)
    total_erros = Column(Integer, default=0)
    
    # Taxas calculadas
    taxa_entrega = Column(Numeric(5, 2), default=0.0)
    taxa_abertura = Column(Numeric(5, 2), default=0.0)
    taxa_clique = Column(Numeric(5, 2), default=0.0)
    taxa_conversao = Column(Numeric(5, 2), default=0.0)
    
    # Custos
    custo_total = Column(Numeric(10, 2), default=0.0)
    custo_por_envio = Column(Numeric(6, 4), default=0.0)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    canal = relationship("CanalComunicacao")
    template = relationship("TemplateMensagem")
    campanha = relationship("CampanhaComunicacao")
    
    # Índices
    __table_args__ = (
        Index('idx_metrica_empresa_data', 'empresa_id', 'data_referencia'),
        Index('idx_metrica_periodo', 'periodo'),
    )

# Configurações padrão do sistema
CONFIGURACOES_CANAIS_PADRAO = {
    TipoCanal.WHATSAPP: {
        "api_url": "https://graph.facebook.com/v18.0",
        "webhook_verify_token": "",
        "access_token": "",
        "phone_number_id": "",
        "business_account_id": ""
    },
    TipoCanal.EMAIL: {
        "provider": "sendgrid",  # sendgrid, ses, smtp
        "api_key": "",
        "sender_email": "",
        "sender_name": "",
        "smtp_host": "",
        "smtp_port": 587,
        "smtp_username": "",
        "smtp_password": ""
    },
    TipoCanal.SMS: {
        "provider": "twilio",  # twilio, sns
        "api_key": "",
        "api_secret": "",
        "sender_number": "",
        "account_sid": ""
    },
    TipoCanal.PUSH: {
        "provider": "fcm",  # fcm, apns
        "server_key": "",
        "project_id": "",
        "certificate_path": ""
    }
}

# Templates de sistema padrão
TEMPLATES_SISTEMA_PADRAO = [
    {
        "nome": "Novo Pedido - Cliente",
        "tipo": TipoTemplate.TRANSACIONAL,
        "canal": TipoCanal.WHATSAPP,
        "assunto": "Pedido Confirmado #{numero_pedido}",
        "conteudo": "Olá {nome_cliente}! Seu pedido #{numero_pedido} foi confirmado. Total: R$ {valor_total}. Previsão de entrega: {tempo_preparo} minutos.",
        "variaveis": ["nome_cliente", "numero_pedido", "valor_total", "tempo_preparo"]
    },
    {
        "nome": "Pedido Pronto",
        "tipo": TipoTemplate.NOTIFICACAO,
        "canal": TipoCanal.WHATSAPP,
        "assunto": "Pedido Pronto para Retirada",
        "conteudo": "🍕 Oba! Seu pedido #{numero_pedido} está pronto para retirada! Venha buscar no balcão. Obrigado!",
        "variaveis": ["numero_pedido"]
    },
    {
        "nome": "Aniversário Cliente",
        "tipo": TipoTemplate.PROMOCIONAL,
        "canal": TipoCanal.EMAIL,
        "assunto": "🎉 Parabéns, {nome_cliente}! Ganhe 20% OFF",
        "conteudo": "Feliz aniversário! Como presente, você ganhou 20% de desconto em qualquer pedido hoje. Use o cupom: ANIVERSARIO20",
        "variaveis": ["nome_cliente"]
    }
]
