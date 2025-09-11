from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, Time, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date, time
from enum import Enum as PyEnum
from typing import Optional, Dict, Any, List

from .database import Base

# === ENUMS ===

class TipoRecurso(PyEnum):
    MESA = "MESA"
    SALA_REUNIAO = "SALA_REUNIAO"
    ESPACO_EVENTO = "ESPACO_EVENTO"
    EQUIPAMENTO = "EQUIPAMENTO"
    SERVICO = "SERVICO"
    PROFISSIONAL = "PROFISSIONAL"
    VEICULO = "VEICULO"
    QUADRA = "QUADRA"
    ESTACIONAMENTO = "ESTACIONAMENTO"

class StatusReserva(PyEnum):
    PENDENTE = "PENDENTE"
    CONFIRMADA = "CONFIRMADA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"
    NAO_COMPARECEU = "NAO_COMPARECEU"
    EM_ANALISE = "EM_ANALISE"
    REJEITADA = "REJEITADA"

class TipoAprovacao(PyEnum):
    AUTOMATICA = "AUTOMATICA"
    MANUAL = "MANUAL"
    CONDICIONAL = "CONDICIONAL"

class FrequenciaRepeticao(PyEnum):
    UNICA = "UNICA"
    DIARIA = "DIARIA"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"
    PERSONALIZADA = "PERSONALIZADA"

class TipoNotificacao(PyEnum):
    CONFIRMACAO = "CONFIRMACAO"
    LEMBRETE = "LEMBRETE"
    CANCELAMENTO = "CANCELAMENTO"
    ALTERACAO = "ALTERACAO"
    DISPONIBILIDADE = "DISPONIBILIDADE"

class StatusListaEspera(PyEnum):
    ATIVA = "ATIVA"
    ATENDIDA = "ATENDIDA"
    CANCELADA = "CANCELADA"
    EXPIRADA = "EXPIRADA"

class TipoPagamento(PyEnum):
    GRATIS = "GRATIS"
    PAGO_ANTECIPADO = "PAGO_ANTECIPADO"
    PAGO_LOCAL = "PAGO_LOCAL"
    FIADO = "FIADO"

class PrioridadeReserva(PyEnum):
    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"
    CRITICA = "CRITICA"
    VIP = "VIP"

# === MODELS ===

class ConfiguracaoReserva(Base):
    """Configurações gerais do sistema de reservas"""
    __tablename__ = "configuracoes_reserva"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Configurações gerais
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Horários de funcionamento
    horario_abertura = Column(Time, nullable=False, default=time(8, 0))
    horario_fechamento = Column(Time, nullable=False, default=time(22, 0))
    dias_funcionamento = Column(JSON, default=["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"])
    
    # Configurações de reserva
    antecedencia_minima = Column(Integer, default=60)  # minutos
    antecedencia_maxima = Column(Integer, default=43200)  # minutos (30 dias)
    duracao_padrao = Column(Integer, default=120)  # minutos
    duracao_minima = Column(Integer, default=30)  # minutos
    duracao_maxima = Column(Integer, default=480)  # minutos
    intervalo_slots = Column(Integer, default=30)  # minutos
    
    # Aprovação e limites
    tipo_aprovacao = Column(SQLEnum(TipoAprovacao), default=TipoAprovacao.AUTOMATICA)
    limite_reservas_por_cliente = Column(Integer, default=5)
    limite_reservas_por_dia = Column(Integer, default=100)
    permite_reagendamento = Column(Boolean, default=True)
    permite_cancelamento = Column(Boolean, default=True)
    tempo_limite_cancelamento = Column(Integer, default=60)  # minutos antes do horário
    
    # Notificações
    enviar_confirmacao = Column(Boolean, default=True)
    enviar_lembrete = Column(Boolean, default=True)
    tempo_lembrete = Column(Integer, default=60)  # minutos antes
    template_confirmacao = Column(Text)
    template_lembrete = Column(Text)
    template_cancelamento = Column(Text)
    
    # Lista de espera
    habilitar_lista_espera = Column(Boolean, default=True)
    tempo_resposta_lista_espera = Column(Integer, default=15)  # minutos
    
    # Integração
    sincronizar_google_calendar = Column(Boolean, default=False)
    webhook_confirmacao = Column(String(500))
    webhook_cancelamento = Column(String(500))
    
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="configuracoes_reserva")
    recursos = relationship("RecursoDisponivel", back_populates="configuracao")

class TipoRecursoConfig(Base):
    """Configuração de tipos de recursos"""
    __tablename__ = "tipos_recurso_config"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    configuracao_id = Column(Integer, ForeignKey("configuracoes_reserva.id"), nullable=False)
    
    # Identificação
    nome = Column(String(100), nullable=False)
    tipo = Column(SQLEnum(TipoRecurso), nullable=False)
    descricao = Column(Text)
    cor_calendario = Column(String(7), default="#3B82F6")  # Cor hexadecimal
    icone = Column(String(50), default="calendar")
    ativo = Column(Boolean, default=True)
    
    # Configurações específicas
    capacidade_maxima = Column(Integer, default=1)
    permite_multiplas_reservas = Column(Boolean, default=False)
    requer_aprovacao = Column(Boolean, default=False)
    tempo_preparacao = Column(Integer, default=0)  # minutos
    tempo_limpeza = Column(Integer, default=0)  # minutos
    
    # Preços
    valor_base = Column(Numeric(10, 2), default=0)
    valor_por_hora = Column(Numeric(10, 2), default=0)
    valor_por_pessoa = Column(Numeric(10, 2), default=0)
    taxa_adicional = Column(Numeric(10, 2), default=0)
    
    # Regras
    duracao_minima = Column(Integer, default=30)  # minutos
    duracao_maxima = Column(Integer, default=480)  # minutos
    antecedencia_minima = Column(Integer, default=60)  # minutos
    limite_reservas_simultaneas = Column(Integer, default=1)
    
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    empresa = relationship("Empresa")
    configuracao = relationship("ConfiguracaoReserva")
    recursos = relationship("RecursoDisponivel", back_populates="tipo_config")

class RecursoDisponivel(Base):
    """Recursos específicos disponíveis para reserva"""
    __tablename__ = "recursos_disponiveis"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    configuracao_id = Column(Integer, ForeignKey("configuracoes_reserva.id"), nullable=False)
    tipo_config_id = Column(Integer, ForeignKey("tipos_recurso_config.id"), nullable=False)
    
    # Identificação
    nome = Column(String(100), nullable=False)
    codigo = Column(String(50))  # Código interno
    descricao = Column(Text)
    localizacao = Column(String(200))
    ativo = Column(Boolean, default=True)
    
    # Características
    capacidade = Column(Integer, default=1)
    area_metros = Column(Numeric(8, 2))
    caracteristicas = Column(JSON, default=[])  # Lista de características
    equipamentos_inclusos = Column(JSON, default=[])  # Lista de equipamentos
    
    # Disponibilidade
    disponivel_24h = Column(Boolean, default=False)
    horario_inicio = Column(Time)
    horario_fim = Column(Time)
    dias_disponiveis = Column(JSON, default=["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"])
    
    # Configurações específicas
    permite_reserva_online = Column(Boolean, default=True)
    requer_aprovacao_especial = Column(Boolean, default=False)
    observacoes_especiais = Column(Text)
    
    # Preços específicos (sobrescreve o tipo)
    valor_personalizado = Column(Boolean, default=False)
    valor_base = Column(Numeric(10, 2))
    valor_por_hora = Column(Numeric(10, 2))
    valor_por_pessoa = Column(Numeric(10, 2))
    
    # Metadados
    metadata_extra = Column(JSON, default={})
    ordem_exibicao = Column(Integer, default=0)
    
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    empresa = relationship("Empresa")
    configuracao = relationship("ConfiguracaoReserva", back_populates="recursos")
    tipo_config = relationship("TipoRecursoConfig", back_populates="recursos")
    reservas = relationship("Reserva", back_populates="recurso")
    disponibilidades = relationship("DisponibilidadeRecurso", back_populates="recurso")
    bloqueios = relationship("BloqueioRecurso", back_populates="recurso")

class DisponibilidadeRecurso(Base):
    """Disponibilidade específica de recursos por período"""
    __tablename__ = "disponibilidade_recursos"
    
    id = Column(Integer, primary_key=True, index=True)
    recurso_id = Column(Integer, ForeignKey("recursos_disponiveis.id"), nullable=False)
    
    # Período
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    
    # Configurações
    disponivel = Column(Boolean, default=True)
    capacidade_especial = Column(Integer)  # Sobrescreve capacidade padrão
    valor_especial = Column(Numeric(10, 2))  # Preço especial para o período
    observacoes = Column(Text)
    
    # Recorrência
    recorrente = Column(Boolean, default=False)
    frequencia_repeticao = Column(SQLEnum(FrequenciaRepeticao), default=FrequenciaRepeticao.UNICA)
    dias_semana = Column(JSON, default=[])  # Para recorrência semanal
    ate_data = Column(Date)  # Até quando repetir
    
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    recurso = relationship("RecursoDisponivel", back_populates="disponibilidades")

class BloqueioRecurso(Base):
    """Bloqueios e indisponibilidades de recursos"""
    __tablename__ = "bloqueios_recursos"
    
    id = Column(Integer, primary_key=True, index=True)
    recurso_id = Column(Integer, ForeignKey("recursos_disponiveis.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Período do bloqueio
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    
    # Informações
    motivo = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo_bloqueio = Column(String(50), default="MANUTENCAO")  # MANUTENCAO, EVENTO_PRIVADO, LIMPEZA, etc.
    
    # Configurações
    bloqueia_reservas = Column(Boolean, default=True)
    bloqueia_lista_espera = Column(Boolean, default=True)
    permite_override = Column(Boolean, default=False)  # Admin pode sobrescrever
    
    # Notificações
    notificar_afetados = Column(Boolean, default=True)
    mensagem_notificacao = Column(Text)
    
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    recurso = relationship("RecursoDisponivel", back_populates="bloqueios")
    usuario = relationship("Usuario")

class Reserva(Base):
    """Reservas realizadas"""
    __tablename__ = "reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    recurso_id = Column(Integer, ForeignKey("recursos_disponiveis.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    
    # Identificação
    codigo_reserva = Column(String(20), unique=True, nullable=False)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    
    # Período da reserva
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    data_checkin = Column(DateTime)
    data_checkout = Column(DateTime)
    
    # Informações da reserva
    numero_pessoas = Column(Integer, default=1)
    observacoes_cliente = Column(Text)
    observacoes_internas = Column(Text)
    requisitos_especiais = Column(JSON, default=[])
    
    # Status e controle
    status = Column(SQLEnum(StatusReserva), default=StatusReserva.PENDENTE)
    prioridade = Column(SQLEnum(PrioridadeReserva), default=PrioridadeReserva.NORMAL)
    confirmada_em = Column(DateTime)
    confirmada_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Recorrência
    reserva_pai_id = Column(Integer, ForeignKey("reservas.id"))  # Para reservas recorrentes
    frequencia_repeticao = Column(SQLEnum(FrequenciaRepeticao), default=FrequenciaRepeticao.UNICA)
    ate_data = Column(Date)
    dias_semana = Column(JSON, default=[])
    
    # Financeiro
    tipo_pagamento = Column(SQLEnum(TipoPagamento), default=TipoPagamento.GRATIS)
    valor_total = Column(Numeric(10, 2), default=0)
    valor_entrada = Column(Numeric(10, 2), default=0)
    valor_pago = Column(Numeric(10, 2), default=0)
    desconto_aplicado = Column(Numeric(10, 2), default=0)
    motivo_desconto = Column(String(200))
    
    # Contatos
    telefone_contato = Column(String(20))
    email_contato = Column(String(100))
    
    # Controle de qualidade
    avaliacao_servico = Column(Integer)  # 1-5
    comentario_avaliacao = Column(Text)
    data_avaliacao = Column(DateTime)
    
    # Metadados
    origem_reserva = Column(String(50), default="SISTEMA")  # SISTEMA, TELEFONE, WHATSAPP, SITE
    ip_origem = Column(String(45))
    user_agent = Column(String(500))
    dados_extras = Column(JSON, default={})
    
    # Timestamps
    criada_em = Column(DateTime, default=datetime.now)
    atualizada_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cancelada_em = Column(DateTime)
    cancelada_por = Column(Integer, ForeignKey("usuarios.id"))
    motivo_cancelamento = Column(String(500))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    recurso = relationship("RecursoDisponivel", back_populates="reservas")
    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    evento = relationship("Evento")
    confirmador = relationship("Usuario", foreign_keys=[confirmada_por])
    cancelador = relationship("Usuario", foreign_keys=[cancelada_por])
    reserva_pai = relationship("Reserva", remote_side=[id])
    reservas_filhas = relationship("Reserva", remote_side=[reserva_pai_id])
    itens_adicionais = relationship("ItemAdicionalReserva", back_populates="reserva")
    historico = relationship("HistoricoReserva", back_populates="reserva")
    lista_espera = relationship("ListaEspera", back_populates="reserva_relacionada")

class ItemAdicionalReserva(Base):
    """Itens adicionais contratados junto com a reserva"""
    __tablename__ = "itens_adicionais_reserva"
    
    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    
    # Item
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(50))
    
    # Quantidades e valores
    quantidade = Column(Integer, default=1)
    valor_unitario = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2), default=0)
    
    # Configurações
    obrigatorio = Column(Boolean, default=False)
    incluido_no_preco = Column(Boolean, default=False)
    disponivel_no_local = Column(Boolean, default=True)
    
    # Controle
    confirmado = Column(Boolean, default=False)
    entregue = Column(Boolean, default=False)
    data_entrega = Column(DateTime)
    
    criado_em = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    reserva = relationship("Reserva", back_populates="itens_adicionais")

class ListaEspera(Base):
    """Lista de espera para horários indisponíveis"""
    __tablename__ = "lista_espera"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    recurso_id = Column(Integer, ForeignKey("recursos_disponiveis.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    reserva_relacionada_id = Column(Integer, ForeignKey("reservas.id"), nullable=True)
    
    # Preferências
    data_preferida = Column(Date, nullable=False)
    hora_inicio_preferida = Column(Time)
    hora_fim_preferida = Column(Time)
    duracao_desejada = Column(Integer, default=120)  # minutos
    numero_pessoas = Column(Integer, default=1)
    
    # Flexibilidade
    aceita_outros_horarios = Column(Boolean, default=True)
    aceita_outros_recursos = Column(Boolean, default=False)
    horarios_alternativos = Column(JSON, default=[])
    recursos_alternativos = Column(JSON, default=[])
    
    # Contato
    telefone_contato = Column(String(20))
    email_contato = Column(String(100))
    prefere_whatsapp = Column(Boolean, default=True)
    prefere_email = Column(Boolean, default=True)
    prefere_telefone = Column(Boolean, default=False)
    
    # Controle
    status = Column(SQLEnum(StatusListaEspera), default=StatusListaEspera.ATIVA)
    prioridade = Column(SQLEnum(PrioridadeReserva), default=PrioridadeReserva.NORMAL)
    posicao_fila = Column(Integer, default=1)
    
    # Configurações
    expira_em = Column(DateTime)
    tempo_resposta_limite = Column(Integer, default=15)  # minutos para responder
    tentativas_contato = Column(Integer, default=0)
    maximo_tentativas = Column(Integer, default=3)
    
    # Resultado
    atendida_em = Column(DateTime)
    reserva_criada_id = Column(Integer, ForeignKey("reservas.id"))
    motivo_cancelamento = Column(String(500))
    
    criada_em = Column(DateTime, default=datetime.now)
    atualizada_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    empresa = relationship("Empresa")
    recurso = relationship("RecursoDisponivel")
    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    reserva_relacionada = relationship("Reserva", foreign_keys=[reserva_relacionada_id])
    reserva_criada = relationship("Reserva", foreign_keys=[reserva_criada_id])

class HistoricoReserva(Base):
    """Histórico de alterações nas reservas"""
    __tablename__ = "historico_reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Alteração
    acao = Column(String(50), nullable=False)  # CRIADA, CONFIRMADA, ALTERADA, CANCELADA, etc.
    campo_alterado = Column(String(100))
    valor_anterior = Column(Text)
    valor_novo = Column(Text)
    motivo = Column(String(500))
    
    # Contexto
    ip_origem = Column(String(45))
    user_agent = Column(String(500))
    dados_contexto = Column(JSON, default={})
    
    criado_em = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    reserva = relationship("Reserva", back_populates="historico")
    usuario = relationship("Usuario")

class NotificacaoReserva(Base):
    """Notificações enviadas relacionadas a reservas"""
    __tablename__ = "notificacoes_reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Notificação
    tipo = Column(SQLEnum(TipoNotificacao), nullable=False)
    canal = Column(String(20), nullable=False)  # EMAIL, SMS, WHATSAPP, PUSH
    destinatario = Column(String(100), nullable=False)
    
    # Conteúdo
    assunto = Column(String(200))
    mensagem = Column(Text, nullable=False)
    template_usado = Column(String(100))
    variaveis_template = Column(JSON, default={})
    
    # Controle de entrega
    enviada = Column(Boolean, default=False)
    enviada_em = Column(DateTime)
    entregue = Column(Boolean, default=False)
    entregue_em = Column(DateTime)
    lida = Column(Boolean, default=False)
    lida_em = Column(DateTime)
    
    # Agendamento
    agendada_para = Column(DateTime)
    tentativas_envio = Column(Integer, default=0)
    maximo_tentativas = Column(Integer, default=3)
    
    # Resposta
    respondida = Column(Boolean, default=False)
    resposta_em = Column(DateTime)
    resposta_conteudo = Column(Text)
    
    # Erros
    erro_envio = Column(Text)
    ultimo_erro = Column(DateTime)
    
    criada_em = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    reserva = relationship("Reserva")
    usuario = relationship("Usuario")

class ConfiguracaoCalendario(Base):
    """Configurações de integração com calendários externos"""
    __tablename__ = "configuracoes_calendario"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Configuração
    nome = Column(String(100), nullable=False)
    tipo_calendario = Column(String(50), nullable=False)  # GOOGLE, OUTLOOK, ICAL, etc.
    ativo = Column(Boolean, default=True)
    
    # Credenciais e configurações
    configuracao_api = Column(JSON, default={})  # Tokens, IDs, etc.
    calendario_id_externo = Column(String(200))
    sincronizacao_bidirecional = Column(Boolean, default=False)
    
    # Configurações de sincronização
    sincronizar_automaticamente = Column(Boolean, default=True)
    intervalo_sincronizacao = Column(Integer, default=15)  # minutos
    ultima_sincronizacao = Column(DateTime)
    
    # Filtros
    tipos_recurso_sincronizar = Column(JSON, default=[])
    status_reserva_sincronizar = Column(JSON, default=["CONFIRMADA", "EM_ANDAMENTO"])
    
    # Mapeamento de campos
    mapeamento_campos = Column(JSON, default={})
    prefixo_titulo = Column(String(50), default="[Reserva]")
    incluir_detalhes = Column(Boolean, default=True)
    
    criada_em = Column(DateTime, default=datetime.now)
    atualizada_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

# === TEMPLATES E CONFIGURAÇÕES PADRÃO ===

TIPOS_RECURSO_PADRAO = [
    {
        "nome": "Mesa para 2 pessoas",
        "tipo": TipoRecurso.MESA,
        "capacidade_maxima": 2,
        "valor_base": 0,
        "duracao_minima": 60,
        "duracao_maxima": 180,
        "cor_calendario": "#3B82F6"
    },
    {
        "nome": "Mesa para 4 pessoas",
        "tipo": TipoRecurso.MESA,
        "capacidade_maxima": 4,
        "valor_base": 0,
        "duracao_minima": 60,
        "duracao_maxima": 240,
        "cor_calendario": "#10B981"
    },
    {
        "nome": "Mesa para 6 pessoas",
        "tipo": TipoRecurso.MESA,
        "capacidade_maxima": 6,
        "valor_base": 0,
        "duracao_minima": 90,
        "duracao_maxima": 300,
        "cor_calendario": "#F59E0B"
    },
    {
        "nome": "Sala de Reunião Pequena",
        "tipo": TipoRecurso.SALA_REUNIAO,
        "capacidade_maxima": 8,
        "valor_por_hora": 50.00,
        "duracao_minima": 30,
        "duracao_maxima": 480,
        "requer_aprovacao": True,
        "cor_calendario": "#8B5CF6"
    },
    {
        "nome": "Espaço para Eventos",
        "tipo": TipoRecurso.ESPACO_EVENTO,
        "capacidade_maxima": 100,
        "valor_base": 500.00,
        "duracao_minima": 240,
        "duracao_maxima": 720,
        "requer_aprovacao": True,
        "cor_calendario": "#EF4444"
    }
]

TEMPLATES_NOTIFICACAO_PADRAO = {
    "confirmacao_email": {
        "assunto": "Reserva Confirmada - {codigo_reserva}",
        "conteudo": """
        Olá {nome_cliente},
        
        Sua reserva foi confirmada com sucesso!
        
        📅 Data: {data_reserva}
        🕒 Horário: {hora_inicio} às {hora_fim}
        🏷️ Recurso: {nome_recurso}
        👥 Pessoas: {numero_pessoas}
        💰 Valor: {valor_total}
        
        Código da reserva: {codigo_reserva}
        
        Em caso de dúvidas, entre em contato conosco.
        
        Atenciosamente,
        {nome_empresa}
        """
    },
    "lembrete_whatsapp": {
        "conteudo": """
        🔔 *Lembrete de Reserva*
        
        Olá {nome_cliente}! Sua reserva é em {tempo_restante}.
        
        📍 {nome_recurso}
        🕒 {hora_inicio} às {hora_fim}
        👥 {numero_pessoas} pessoas
        
        Código: {codigo_reserva}
        
        Aguardamos você! 😊
        """
    },
    "cancelamento_sms": {
        "conteudo": "Reserva {codigo_reserva} cancelada. {nome_recurso} em {data_reserva} às {hora_inicio}. Motivo: {motivo_cancelamento}. {nome_empresa}"
    }
}

CONFIGURACAO_PADRAO = {
    "horario_abertura": "08:00",
    "horario_fechamento": "22:00",
    "dias_funcionamento": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"],
    "antecedencia_minima": 60,
    "antecedencia_maxima": 43200,
    "duracao_padrao": 120,
    "intervalo_slots": 30,
    "tipo_aprovacao": "AUTOMATICA",
    "limite_reservas_por_cliente": 5,
    "permite_reagendamento": True,
    "permite_cancelamento": True,
    "tempo_limite_cancelamento": 60,
    "enviar_confirmacao": True,
    "enviar_lembrete": True,
    "tempo_lembrete": 60,
    "habilitar_lista_espera": True,
    "tempo_resposta_lista_espera": 15
}
