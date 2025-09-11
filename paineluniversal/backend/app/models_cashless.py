"""
Modelos para o Sistema Cashless baseado na análise do sistema Meep
Implementa funcionalidades avançadas de cartões, mesas, categorias e permissões
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from .models import CategoriaCliente, ClienteCategoria, Cargo, Permissao  # Importando para evitar duplicação
import enum
from decimal import Decimal
from typing import Dict, List, Any, Optional

# ================================================================================
# ENUMS PARA SISTEMA CASHLESS
# ================================================================================

class StatusCartaoCashless(enum.Enum):
    ATIVO = "ativo"
    BLOQUEADO = "bloqueado"
    CANCELADO = "cancelado"
    PENDENTE_ATIVACAO = "pendente_ativacao"

class TipoCartaoCashless(enum.Enum):
    RFID = "rfid"
    NFC = "nfc"
    QR_CODE = "qr_code"
    CODIGO_BARRAS = "codigo_barras"
    VIRTUAL = "virtual"

class StatusMesa(enum.Enum):
    DISPONIVEL = "disponivel"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"
    MANUTENCAO = "manutencao"
    INATIVA = "inativa"

class TipoMesa(enum.Enum):
    COMUM = "comum"
    VIP = "vip"
    CAMAROTE = "camarote"
    BAR = "bar"
    EXTERNA = "externa"
    ESPECIAL = "especial"

class StatusGrupoCartao(enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    ARQUIVADO = "arquivado"

class StatusRecarga(enum.Enum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    CANCELADA = "cancelada"
    ESTORNADA = "estornada"
    PROCESSANDO = "processando"

class TipoMovimentacao(enum.Enum):
    CREDITO = "credito"
    DEBITO = "debito"
    ESTORNO = "estorno"
    BLOQUEIO = "bloqueio"
    DESBLOQUEIO = "desbloqueio"
    TRANSFERENCIA = "transferencia"
    BONUS = "bonus"

class StatusComandaDigital(enum.Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    FECHADA = "fechada"
    CANCELADA = "cancelada"

class TipoTerminalPagamento(enum.Enum):
    MOVEL = "movel"
    FIXO = "fixo"
    VIRTUAL = "virtual"
    INTEGRADO = "integrado"

class TipoCategoriaCliente(enum.Enum):
    VIP = "vip"
    SOCIO = "socio"
    PREMIUM = "premium"
    REGULAR = "regular"
    CORPORATIVO = "corporativo"

class StatusCategoriaCliente(enum.Enum):
    ATIVA = "ativa"
    INATIVA = "inativa"
    TEMPORARIA = "temporaria"

class TipoPermissao(enum.Enum):
    # Permissões de Sistema
    ADMIN_TOTAL = "admin_total"
    GESTAO_USUARIOS = "gestao_usuarios"
    GESTAO_EMPRESA = "gestao_empresa"
    
    # Permissões de Eventos
    CRIAR_EVENTO = "criar_evento"
    EDITAR_EVENTO = "editar_evento"
    EXCLUIR_EVENTO = "excluir_evento"
    VISUALIZAR_EVENTO = "visualizar_evento"
    
    # Permissões de PDV
    OPERAR_PDV = "operar_pdv"
    CANCELAR_VENDA = "cancelar_venda"
    ESTORNAR_VENDA = "estornar_venda"
    DESCONTO_VENDA = "desconto_venda"
    
    # Permissões de Cashless
    GESTAO_CARTOES = "gestao_cartoes"
    BLOQUEAR_CARTAO = "bloquear_cartao"
    RECARREGAR_CARTAO = "recarregar_cartao"
    EXTRATO_CARTAO = "extrato_cartao"
    
    # Permissões de Relatórios
    RELATORIO_VENDAS = "relatorio_vendas"
    RELATORIO_FINANCEIRO = "relatorio_financeiro"
    RELATORIO_ESTOQUE = "relatorio_estoque"
    RELATORIO_CLIENTES = "relatorio_clientes"
    
    # Permissões de Mesas
    GESTAO_MESAS = "gestao_mesas"
    ABRIR_MESA = "abrir_mesa"
    FECHAR_MESA = "fechar_mesa"
    TRANSFERIR_MESA = "transferir_mesa"

# ================================================================================
# MODELOS PARA CATEGORIAS DE CLIENTES (importado de models.py)
# ================================================================================
# CategoriaCliente já está definida em models.py - removendo duplicação

# ClienteCategoria já está definida em models.py - removendo duplicação

# ================================================================================
# MODELOS PARA SISTEMA DE PERMISSÕES
# ================================================================================

# Cargo e Permissao já estão definidas em models.py - removendo duplicação

class CargoPermissao(Base):
    """Associação entre cargos e suas permissões"""
    __tablename__ = "cargos_permissoes"
    
    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    permissao_id = Column(Integer, ForeignKey("permissoes.id"), nullable=False)
    concedida_em = Column(DateTime(timezone=True), server_default=func.now())
    concedida_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    cargo = relationship("Cargo", back_populates="permissoes")
    permissao = relationship("Permissao", back_populates="cargos")
    concedente = relationship("Usuario", foreign_keys=[concedida_por])

class UsuarioCargo(Base):
    """Associação entre usuários e seus cargos"""
    __tablename__ = "usuarios_cargos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    data_inicio = Column(Date, nullable=False, default=func.current_date())
    data_fim = Column(Date)  # Null = permanente
    ativo = Column(Boolean, default=True)
    atribuido_por = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    cargo = relationship("Cargo", back_populates="usuarios")
    atribuinte = relationship("Usuario", foreign_keys=[atribuido_por])

# ================================================================================
# MODELOS PARA SISTEMA DE MESAS
# ================================================================================

class Mesa(Base):
    """Sistema de gestão de mesas do estabelecimento"""
    __tablename__ = "mesas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), nullable=False)  # ex: "001", "BAR D", "CAM1"
    nome_personalizado = Column(String(50))  # ex: "elite", "gold", "stylo"
    tipo = Column(Enum(TipoMesa), default=TipoMesa.COMUM)
    capacidade = Column(Integer, default=4)
    
    # Localização física
    area = Column(String(50))  # ex: "Salão Principal", "Área VIP", "Varanda"
    posicao_x = Column(Integer)  # Coordenada X no mapa
    posicao_y = Column(Integer)  # Coordenada Y no mapa
    andar = Column(String(10), default="Térreo")
    
    # Status e configurações
    status = Column(Enum(StatusMesa), default=StatusMesa.DISPONIVEL)
    ativa = Column(Boolean, default=True)
    permite_reserva = Column(Boolean, default=True)
    valor_consumacao_minima = Column(Numeric(10, 2), default=0)
    
    # QR Code e identificação
    qr_code_mesa = Column(String(100), unique=True)
    codigo_identificacao = Column(String(20), unique=True)
    
    # Configurações especiais
    observacoes = Column(Text)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    evento = relationship("Evento")
    comandas = relationship("ComandaCashless", back_populates="mesa")
    cardapios = relationship("MesaCardapio", back_populates="mesa")

class MesaCardapio(Base):
    """Associação entre mesas e cardápios digitais específicos"""
    __tablename__ = "mesas_cardapios"
    
    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    cardapio_id = Column(Integer, ForeignKey("cardapios_digitais.id"), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    mesa = relationship("Mesa", back_populates="cardapios")
    cardapio = relationship("CardapioDigital", back_populates="mesas")

# ================================================================================
# MODELOS PARA SISTEMA CASHLESS AVANÇADO
# ================================================================================

class GrupoCartao(Base):
    """Grupos para organização de cartões cashless"""
    __tablename__ = "grupos_cartoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    cor = Column(String(7), default="#3b82f6")
    icone = Column(String(50))
    
    # Configurações do grupo
    limite_recarga_diario = Column(Numeric(10, 2))
    limite_gasto_diario = Column(Numeric(10, 2))
    desconto_automatico = Column(Numeric(5, 2), default=0)
    cashback_percentual = Column(Numeric(5, 2), default=0)
    
    # Status e controle
    status = Column(Enum(StatusGrupoCartao), default=StatusGrupoCartao.ATIVO)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    evento = relationship("Evento")
    cartoes = relationship("CartaoCashless", back_populates="grupo")

class CartaoCashless(Base):
    """Cartões cashless avançados para o sistema"""
    __tablename__ = "cartoes_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_cartao = Column(String(20), unique=True, nullable=False)
    codigo_rfid = Column(String(50), unique=True)
    codigo_nfc = Column(String(50), unique=True)
    qr_code = Column(String(100), unique=True)
    codigo_barras = Column(String(50))
    
    # Dados do portador
    cpf_portador = Column(String(14), index=True)
    nome_portador = Column(String(255))
    telefone_portador = Column(String(20))
    email_portador = Column(String(255))
    
    # Configurações do cartão
    tipo = Column(Enum(TipoCartaoCashless), nullable=False)
    status = Column(Enum(StatusCartaoCashless), default=StatusCartaoCashless.PENDENTE_ATIVACAO)
    saldo_atual = Column(Numeric(10, 2), default=0)
    saldo_bonus = Column(Numeric(10, 2), default=0)
    limite_credito = Column(Numeric(10, 2), default=0)
    
    # Controles de segurança
    senha_cartao = Column(String(255))  # Hash da senha se necessário
    tentativas_senha = Column(Integer, default=0)
    bloqueado_por_tentativas = Column(Boolean, default=False)
    
    # Relacionamentos e grupos
    grupo_id = Column(Integer, ForeignKey("grupos_cartoes.id"))
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    
    # Datas importantes
    data_ativacao = Column(DateTime(timezone=True))
    data_ultimo_uso = Column(DateTime(timezone=True))
    data_vencimento = Column(Date)
    
    # Controle
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    evento = relationship("Evento")
    grupo = relationship("GrupoCartao", back_populates="cartoes")
    mesa = relationship("Mesa")
    transacoes = relationship("TransacaoCashless", back_populates="cartao")
    recargas = relationship("RecargaCashless", back_populates="cartao")

class PreAtivacaoCartao(Base):
    """Sistema de pré-ativação de cartões"""
    __tablename__ = "pre_ativacoes_cartoes"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_cartao = Column(String(20), nullable=False)
    tag_identificacao = Column(String(50), nullable=False)
    
    # Dados de vinculação
    cpf_cliente = Column(String(14), nullable=False, index=True)
    nome_cliente = Column(String(255), nullable=False)
    telefone_cliente = Column(String(20))
    email_cliente = Column(String(255))
    
    # Controle da pré-ativação
    vinculado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    vinculado_em = Column(DateTime(timezone=True), server_default=func.now())
    ativado = Column(Boolean, default=False)
    data_ativacao = Column(DateTime(timezone=True))
    
    # Configurações iniciais
    saldo_inicial = Column(Numeric(10, 2), default=0)
    grupo_id = Column(Integer, ForeignKey("grupos_cartoes.id"))
    observacoes = Column(Text)
    
    # Relacionamentos
    vinculador = relationship("Usuario", foreign_keys=[vinculado_por])
    grupo = relationship("GrupoCartao")

class RecargaCashless(Base):
    """Histórico de recargas dos cartões cashless"""
    __tablename__ = "recargas_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    cartao_id = Column(Integer, ForeignKey("cartoes_cashless.id"), nullable=False)
    valor_recarga = Column(Numeric(10, 2), nullable=False)
    valor_bonus = Column(Numeric(10, 2), default=0)
    metodo_pagamento = Column(String(50))  # pix, cartao, dinheiro, etc.
    
    # Dados da transação de pagamento
    codigo_transacao_pagamento = Column(String(100))
    status_pagamento = Column(String(20), default="pendente")
    
    # Controle
    operador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    pdv_id = Column(String(50))  # Identificação do PDV usado
    ip_origem = Column(String(45))
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cartao = relationship("CartaoCashless", back_populates="recargas")
    operador = relationship("Usuario", foreign_keys=[operador_id])

class TransacaoCashless(Base):
    """Transações realizadas com cartões cashless"""
    __tablename__ = "transacoes_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    cartao_id = Column(Integer, ForeignKey("cartoes_cashless.id"), nullable=False)
    valor_transacao = Column(Numeric(10, 2), nullable=False)
    valor_desconto = Column(Numeric(10, 2), default=0)
    valor_final = Column(Numeric(10, 2), nullable=False)
    
    # Detalhes da compra
    produtos_json = Column(JSON)  # Lista de produtos comprados
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    pdv_id = Column(String(50))
    operador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Controle de estorno
    estornada = Column(Boolean, default=False)
    data_estorno = Column(DateTime(timezone=True))
    motivo_estorno = Column(String(255))
    estornada_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cartao = relationship("CartaoCashless", back_populates="transacoes")
    mesa = relationship("Mesa")
    operador = relationship("Usuario", foreign_keys=[operador_id])
    estornador = relationship("Usuario", foreign_keys=[estornada_por])

class ComandaCashless(Base):
    """Comandas integradas ao sistema cashless (evolução da tabela comandas)"""
    __tablename__ = "comandas_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_comanda = Column(String(20), unique=True, nullable=False)
    
    # Vinculação com cartão cashless
    cartao_id = Column(Integer, ForeignKey("cartoes_cashless.id"))
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    
    # Dados do cliente
    cpf_cliente = Column(String(14), index=True)
    nome_cliente = Column(String(255))
    categoria_cliente_id = Column(Integer, ForeignKey("categorias_clientes.id"))
    
    # Saldos e controles
    saldo_atual = Column(Numeric(10, 2), default=0)
    saldo_bloqueado = Column(Numeric(10, 2), default=0)
    consumacao_minima = Column(Numeric(10, 2), default=0)
    taxa_servico_percentual = Column(Numeric(5, 2), default=10)
    
    # Status e configurações
    status = Column(String(20), default="ativa")  # ativa, bloqueada, fechada
    permite_credito = Column(Boolean, default=False)
    limite_credito = Column(Numeric(10, 2), default=0)
    
    # Controle operacional
    aberta_por = Column(Integer, ForeignKey("usuarios.id"))
    aberta_em = Column(DateTime(timezone=True), server_default=func.now())
    fechada_por = Column(Integer, ForeignKey("usuarios.id"))
    fechada_em = Column(DateTime(timezone=True))
    
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    cartao = relationship("CartaoCashless")
    mesa = relationship("Mesa", back_populates="comandas")
    categoria_cliente = relationship("CategoriaCliente")
    operador_abertura = relationship("Usuario", foreign_keys=[aberta_por])
    operador_fechamento = relationship("Usuario", foreign_keys=[fechada_por])
    empresa = relationship("Empresa")
    evento = relationship("Evento")

# ================================================================================
# MODELOS PARA CARDÁPIOS DIGITAIS
# ================================================================================

class CardapioDigital(Base):
    """Cardápios digitais para acesso via QR Code"""
    __tablename__ = "cardapios_digitais"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    uuid_cardapio = Column(String(36), unique=True, nullable=False)  # UUID para URL
    
    # Configurações visuais
    cor_primaria = Column(String(7), default="#3b82f6")
    cor_secundaria = Column(String(7), default="#1f2937")
    logo_url = Column(String(500))
    imagem_fundo_url = Column(String(500))
    
    # Configurações funcionais
    ativo = Column(Boolean, default=True)
    publico = Column(Boolean, default=True)
    permite_pedidos = Column(Boolean, default=False)
    exibe_precos = Column(Boolean, default=True)
    
    # URLs e acessos
    url_personalizada = Column(String(255))  # Ex: /cardapio/unica-club
    qr_code_acesso = Column(String(100), unique=True)
    total_acessos = Column(Integer, default=0)
    ultimo_acesso = Column(DateTime(timezone=True))
    
    # Controle
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    criado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    evento = relationship("Evento")
    criador = relationship("Usuario", foreign_keys=[criado_por])
    categorias = relationship("CategoriaCardapioDigital", back_populates="cardapio")
    mesas = relationship("MesaCardapio", back_populates="cardapio")

class CategoriaCardapioDigital(Base):
    """Categorias para organização dos produtos no cardápio digital"""
    __tablename__ = "categorias_cardapio_digital"
    
    id = Column(Integer, primary_key=True, index=True)
    cardapio_id = Column(Integer, ForeignKey("cardapios_digitais.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    ordem = Column(Integer, default=1)
    cor = Column(String(7), default="#6b7280")
    icone = Column(String(50))
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cardapio = relationship("CardapioDigital", back_populates="categorias")
    produtos = relationship("ProdutoCardapioDigital", back_populates="categoria")

class ProdutoCardapioDigital(Base):
    """Produtos específicos para cardápios digitais"""
    __tablename__ = "produtos_cardapio_digital"
    
    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias_cardapio_digital.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"))  # Pode referenciar produto existente
    
    # Dados específicos para o cardápio digital (podem sobrescrever dados do produto)
    nome_exibicao = Column(String(255))
    descricao_exibicao = Column(Text)
    preco_exibicao = Column(Numeric(10, 2))
    imagem_url = Column(String(500))
    
    # Configurações
    ordem = Column(Integer, default=1)
    destaque = Column(Boolean, default=False)
    disponivel = Column(Boolean, default=True)
    permite_observacoes = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    categoria = relationship("CategoriaCardapioDigital", back_populates="produtos")
    produto = relationship("Produto")

# ================================================================================
# MODELOS CASHLESS AVANÇADOS - BASEADO NA ANÁLISE MEEP
# ================================================================================

class RecargaCashlessAvancado(Base):
    """Modelo avançado para controle de recargas do sistema cashless"""
    __tablename__ = "recargas_cashless_avancado"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_recarga = Column(String(50), unique=True, nullable=False, index=True)
    cartao_id = Column(Integer, ForeignKey("cartoes_cashless.id"), nullable=False)
    valor_recarga = Column(Numeric(10, 2), nullable=False)
    valor_bonus = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2), nullable=False)
    forma_pagamento = Column(String(50), nullable=False)  # PIX, CARTAO, DINHEIRO, etc
    status = Column(Enum(StatusRecarga), default=StatusRecarga.PENDENTE)
    
    # Dados do operador/cliente
    cpf_operador = Column(String(14))
    nome_operador = Column(String(255))
    cpf_cliente = Column(String(14))
    nome_cliente = Column(String(255))
    
    # Dados técnicos
    terminal_id = Column(String(50))
    ip_origem = Column(String(45))
    transacao_externa_id = Column(String(100))  # ID da transação no gateway
    
    # Metadata e controle
    observacoes = Column(Text)
    metadados = Column(JSON)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Aprovação
    aprovado_em = Column(DateTime(timezone=True))
    aprovado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    cartao = relationship("CartaoCashless", back_populates="recargas")
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    aprovador = relationship("Usuario")

class MovimentacaoCashless(Base):
    """Modelo para controle de movimentações financeiras dos cartões"""
    __tablename__ = "movimentacoes_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_movimento = Column(String(50), unique=True, nullable=False, index=True)
    cartao_id = Column(Integer, ForeignKey("cartoes_cashless.id"), nullable=False)
    
    # Tipo e valores
    tipo_movimentacao = Column(Enum(TipoMovimentacao), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    saldo_anterior = Column(Numeric(10, 2), nullable=False)
    saldo_posterior = Column(Numeric(10, 2), nullable=False)
    
    # Referências
    descricao = Column(String(500))
    referencia_id = Column(Integer)  # ID da venda, recarga, etc que originou
    referencia_tipo = Column(String(50))  # 'venda', 'recarga', 'estorno', etc
    referencia_numero = Column(String(50))  # Número da venda, recarga, etc
    
    # Dados técnicos
    terminal_id = Column(String(50))
    ip_origem = Column(String(45))
    cpf_operador = Column(String(14))
    nome_operador = Column(String(255))
    
    # Metadata
    metadados = Column(JSON)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cartao = relationship("CartaoCashless", back_populates="movimentacoes")
    evento = relationship("Evento")
    empresa = relationship("Empresa")

class ConfiguracaoCashlessEvento(Base):
    """Configurações específicas do sistema cashless por evento"""
    __tablename__ = "configuracoes_cashless_evento"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), unique=True, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Configurações de cartão
    tipos_cartao_habilitados = Column(JSON, default=["rfid", "nfc", "qr_code"])
    valor_minimo_recarga = Column(Numeric(10, 2), default=10.00)
    valor_maximo_recarga = Column(Numeric(10, 2), default=1000.00)
    valores_recarga_sugeridos = Column(JSON, default=[20, 50, 100, 200])
    limite_diario_padrao = Column(Numeric(10, 2), default=500.00)
    
    # Configurações de bonus
    bonus_habilitado = Column(Boolean, default=False)
    bonus_percentual = Column(Numeric(5, 2), default=0)
    bonus_valor_minimo = Column(Numeric(10, 2), default=50.00)
    tabela_bonus = Column(JSON)  # Estrutura: [{"valor_min": 50, "bonus": 5}, ...]
    
    # Configurações de validade
    dias_validade_cartao = Column(Integer, default=30)
    permite_cartao_sem_validade = Column(Boolean, default=True)
    auto_renovar_cartao = Column(Boolean, default=False)
    
    # Configurações de segurança
    exige_cpf_recarga = Column(Boolean, default=True)
    exige_cpf_consumo = Column(Boolean, default=False)
    permite_saldo_negativo = Column(Boolean, default=False)
    valor_maximo_saldo_negativo = Column(Numeric(10, 2), default=0)
    valor_maximo_por_transacao = Column(Numeric(10, 2), default=500.00)
    
    # Configurações de operação
    permite_recarga_online = Column(Boolean, default=True)
    permite_recarga_presencial = Column(Boolean, default=True)
    permite_estorno_operador = Column(Boolean, default=True)
    tempo_limite_estorno_horas = Column(Integer, default=24)
    permite_transferencia_cartoes = Column(Boolean, default=False)
    
    # Configurações de notificação
    envia_sms_recarga = Column(Boolean, default=False)
    envia_email_recarga = Column(Boolean, default=False)
    envia_sms_consumo = Column(Boolean, default=False)
    envia_push_recarga = Column(Boolean, default=True)
    
    # Templates de mensagens
    template_sms_recarga = Column(Text)
    template_email_recarga = Column(Text)
    template_push_recarga = Column(Text)
    template_sms_consumo = Column(Text)
    
    # Configurações avançadas
    taxa_servico_recarga = Column(Numeric(5, 2), default=0)
    permite_recarga_parcelada = Column(Boolean, default=False)
    integra_gateway_pagamento = Column(Boolean, default=True)
    gateway_pagamento_config = Column(JSON)
    
    # Controle
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento")
    empresa = relationship("Empresa")

class TerminalPagamentoCashless(Base):
    """Terminais para operação do sistema cashless"""
    __tablename__ = "terminais_pagamento_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoTerminalPagamento), nullable=False)
    
    # Localização
    localizacao = Column(String(255))
    setor_id = Column(Integer, ForeignKey("setores.id"))
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    
    # Configurações técnicas
    ip_address = Column(String(45))
    mac_address = Column(String(17))
    leitor_rfid_habilitado = Column(Boolean, default=True)
    leitor_nfc_habilitado = Column(Boolean, default=True)
    leitor_qr_habilitado = Column(Boolean, default=True)
    impressora_conectada = Column(Boolean, default=False)
    
    # Configurações operacionais
    valor_maximo_transacao = Column(Numeric(10, 2), default=500.00)
    permite_estorno = Column(Boolean, default=True)
    tempo_limite_transacao = Column(Integer, default=30)  # segundos
    
    # Metadata e controle
    metadados = Column(JSON)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Operação
    ativo = Column(Boolean, default=True)
    online = Column(Boolean, default=False)
    ultima_comunicacao = Column(DateTime(timezone=True))
    versao_software = Column(String(20))
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    setor = relationship("Setor")
    mesa = relationship("Mesa")

class ComandaDigital(Base):
    """Comandas digitais integradas com sistema cashless"""
    __tablename__ = "comandas_digitais"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_comanda = Column(String(50), nullable=False, index=True)
    qr_code = Column(String(200), unique=True, nullable=False, index=True)
    url_acesso = Column(String(500), unique=True, nullable=False)
    
    # Vinculações
    cartao_id = Column(Integer, ForeignKey("cartoes_cashless.id"))
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    cliente_cpf = Column(String(14))
    cliente_nome = Column(String(255))
    cliente_telefone = Column(String(20))
    
    # Status e controle
    status = Column(Enum(StatusComandaDigital), default=StatusComandaDigital.ATIVA)
    valor_total = Column(Numeric(10, 2), default=0)
    valor_pago = Column(Numeric(10, 2), default=0)
    valor_pendente = Column(Numeric(10, 2), default=0)
    
    # Configurações
    limite_credito = Column(Numeric(10, 2), default=0)
    permite_pedido_sem_saldo = Column(Boolean, default=False)
    tempo_limite_minutos = Column(Integer, default=240)  # 4 horas
    
    # Metadata
    observacoes = Column(Text)
    metadados = Column(JSON)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Timestamps
    aberta_em = Column(DateTime(timezone=True), server_default=func.now())
    fechada_em = Column(DateTime(timezone=True))
    atualizada_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    cartao = relationship("CartaoCashless")
    mesa = relationship("Mesa")
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    pedidos = relationship("PedidoComandaDigital", back_populates="comanda")

class PedidoComandaDigital(Base):
    """Pedidos realizados através das comandas digitais"""
    __tablename__ = "pedidos_comanda_digital"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(50), nullable=False, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas_digitais.id"), nullable=False)
    
    # Produtos
    produtos = Column(JSON, nullable=False)  # Lista de produtos com qtd, preço, etc
    valor_produtos = Column(Numeric(10, 2), nullable=False)
    valor_servico = Column(Numeric(10, 2), default=0)
    valor_desconto = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2), nullable=False)
    
    # Status
    status = Column(String(50), default="pendente")  # pendente, preparando, pronto, entregue, cancelado
    
    # Observações
    observacoes_cliente = Column(Text)
    observacoes_cozinha = Column(Text)
    
    # Controle
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    comanda = relationship("ComandaDigital", back_populates="pedidos")
    evento = relationship("Evento")
    empresa = relationship("Empresa")

# ================================================================================
# ATUALIZAÇÕES DOS MODELOS EXISTENTES PARA INTEGRAÇÃO CASHLESS
# ================================================================================

# Atualizando relacionamentos no modelo CartaoCashless
CartaoCashless.recargas = relationship("RecargaCashless", back_populates="cartao")
CartaoCashless.movimentacoes = relationship("MovimentacaoCashless", back_populates="cartao")
