"""
Modelos completos do banco de dados - Sistema Universal com funcionalidades MEEP
Baseado na engenharia reversa completa do sistema MEEP
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum, JSON, Date, Time, Numeric, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base

# ==================== ENUMS ====================

class TipoUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    GERENCIA = "GERENCIA"
    PROMOTER = "PROMOTER"
    COLABORADOR = "COLABORADOR"
    CLIENTE = "CLIENTE"
    CAIXA = "CAIXA"
    GARCOM = "GARCOM"

class StatusComanda(str, enum.Enum):
    ABERTA = "ABERTA"
    FECHADA = "FECHADA"
    BLOQUEADA = "BLOQUEADA"
    CANCELADA = "CANCELADA"

class TipoPagamento(str, enum.Enum):
    DINHEIRO = "DINHEIRO"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    PIX = "PIX"
    CASHLESS = "CASHLESS"
    FIADO = "FIADO"
    CORTESIA = "CORTESIA"

class StatusPedido(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PREPARANDO = "PREPARANDO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

class TipoOperacao(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    TRANSFERENCIA = "TRANSFERENCIA"
    AJUSTE = "AJUSTE"

class SegmentoEmpresa(str, enum.Enum):
    BARES = "BARES"
    RESTAURANTES = "RESTAURANTES"
    BALADAS = "BALADAS"
    EVENTOS_SHOWS = "EVENTOS_SHOWS"
    HOTEIS = "HOTEIS"
    ESTADIOS = "ESTADIOS"
    ESCOLAS = "ESCOLAS"
    FOOD_PARK = "FOOD_PARK"

class StatusIntegracao(str, enum.Enum):
    CONECTADO = "CONECTADO"
    DESCONECTADO = "DESCONECTADO"
    EM_BREVE = "EM_BREVE"
    ERRO = "ERRO"

class NivelFidelidade(str, enum.Enum):
    BRONZE = "BRONZE"
    PRATA = "PRATA"
    OURO = "OURO"
    PLATINA = "PLATINA"
    DIAMANTE = "DIAMANTE"

# ==================== TABELAS DE ASSOCIAÇÃO ====================

# Associação entre usuários e cargos
usuario_cargo = Table('usuario_cargo', Base.metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id')),
    Column('cargo_id', Integer, ForeignKey('cargos.id'))
)

# Associação entre cargos e permissões
cargo_permissao = Table('cargo_permissao', Base.metadata,
    Column('cargo_id', Integer, ForeignKey('cargos.id')),
    Column('permissao_id', Integer, ForeignKey('permissoes.id'))
)

# Associação entre produtos e categorias
produto_categoria = Table('produto_categoria', Base.metadata,
    Column('produto_id', Integer, ForeignKey('produtos.id')),
    Column('categoria_id', Integer, ForeignKey('categorias_produto.id'))
)

# Associação entre cardápios e produtos
cardapio_produto = Table('cardapio_produto', Base.metadata,
    Column('cardapio_id', Integer, ForeignKey('cardapios.id')),
    Column('produto_id', Integer, ForeignKey('produtos.id')),
    Column('ordem', Integer, default=0)
)

# ==================== MODELOS PRINCIPAIS ====================

# Empresa já está definida em models.py - comentado para evitar duplicação
# class Empresa(Base):
#     __tablename__ = "empresas"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     nome = Column(String(200), nullable=False)
#     cnpj = Column(String(18), unique=True, nullable=False)
#     segmento = Column(SQLEnum(SegmentoEmpresa), default=SegmentoEmpresa.BARES)
#     plano = Column(String(50), default="PREMIUM")
#     logo_url = Column(String(500))
#     configuracoes = Column(JSON, default={})
#     ativo = Column(Boolean, default=True)
#     criado_em = Column(DateTime(timezone=True), server_default=func.now())
#     
#     # Relacionamentos
#     usuarios = relationship("Usuario", back_populates="empresa")
#     eventos = relationship("Evento", back_populates="empresa")
#     produtos = relationship("Produto", back_populates="empresa")
#     cardapios = relationship("Cardapio", back_populates="empresa")
#     clientes = relationship("Cliente", back_populates="empresa")

# Usuario já está definido em models.py - comentado para evitar duplicação
# class Usuario(Base):
#     __tablename__ = "usuarios"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     empresa_id = Column(Integer, ForeignKey("empresas.id"))
#     nome = Column(String(200), nullable=False)
#     email = Column(String(200), unique=True, nullable=False)
#     cpf = Column(String(14), unique=True, nullable=False)
#     telefone = Column(String(20))
#     senha_hash = Column(String(200), nullable=False)
#     tipo = Column(SQLEnum(TipoUsuario), default=TipoUsuario.CLIENTE)
#     avatar_url = Column(String(500))
#     ativo = Column(Boolean, default=True)
#     ultimo_acesso = Column(DateTime(timezone=True))
#     criado_em = Column(DateTime(timezone=True), server_default=func.now())
#     
#     # Relacionamentos
#     empresa = relationship("Empresa", back_populates="usuarios")
#     cargos = relationship("Cargo", secondary=usuario_cargo, back_populates="usuarios")
#     vendas = relationship("Venda", back_populates="vendedor")
#     comandas = relationship("Comanda", back_populates="cliente")

class Cargo(Base):
    __tablename__ = "cargos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    nivel = Column(Integer, default=1)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    usuarios = relationship("Usuario", secondary=usuario_cargo, back_populates="cargos")
    permissoes = relationship("Permissao", secondary=cargo_permissao, back_populates="cargos")

class Permissao(Base):
    __tablename__ = "permissoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text)
    modulo = Column(String(50))
    acao = Column(String(50))
    
    # Relacionamentos
    cargos = relationship("Cargo", secondary=cargo_permissao, back_populates="permissoes")

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    nome = Column(String(200), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    email = Column(String(200))
    telefone = Column(String(20))
    data_nascimento = Column(Date)
    categoria_id = Column(Integer, ForeignKey("categorias_cliente.id"))
    pontos_fidelidade = Column(Integer, default=0)
    nivel_fidelidade = Column(SQLEnum(NivelFidelidade), default=NivelFidelidade.BRONZE)
    saldo_cashless = Column(Numeric(10, 2), default=0)
    tag_rfid = Column(String(50), unique=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="clientes")
    categoria = relationship("CategoriaCliente", back_populates="clientes")
    cartoes = relationship("CartaoCashless", back_populates="cliente")
    transacoes = relationship("TransacaoCashless", back_populates="cliente")

class CategoriaCliente(Base):
    __tablename__ = "categorias_cliente"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    desconto_percentual = Column(Float, default=0)
    beneficios = Column(JSON, default=[])
    
    # Relacionamentos
    clientes = relationship("Cliente", back_populates="categoria")

class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    local = Column(String(500))
    capacidade_maxima = Column(Integer)
    idade_minima = Column(Integer)
    configuracoes = Column(JSON, default={})
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="eventos")
    listas = relationship("Lista", back_populates="evento")
    checkins = relationship("Checkin", back_populates="evento")
    vendas = relationship("Venda", back_populates="evento")

class Produto(Base):
    __tablename__ = "produtos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    codigo = Column(String(50), unique=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    preco = Column(Numeric(10, 2), nullable=False)
    preco_custo = Column(Numeric(10, 2))
    imagem_url = Column(String(500))
    unidade_medida = Column(String(20))
    estoque_atual = Column(Numeric(10, 3), default=0)
    estoque_minimo = Column(Numeric(10, 3), default=0)
    pontos_fidelidade = Column(Integer, default=0)
    disponivel_app = Column(Boolean, default=True)
    disponivel_pdv = Column(Boolean, default=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="produtos")
    categorias = relationship("CategoriaProduto", secondary=produto_categoria, back_populates="produtos")
    cardapios = relationship("Cardapio", secondary=cardapio_produto, back_populates="produtos")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="produto")

class CategoriaProduto(Base):
    __tablename__ = "categorias_produto"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    imagem_url = Column(String(500))
    ordem = Column(Integer, default=0)
    
    # Relacionamentos
    produtos = relationship("Produto", secondary=produto_categoria, back_populates="categorias")

class Cardapio(Base):
    __tablename__ = "cardapios"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    uuid = Column(String(36), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo = Column(String(50))  # APP, PDV, DIGITAL, DELIVERY
    url_digital = Column(String(500))
    qr_code_url = Column(String(500))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="cardapios")
    produtos = relationship("Produto", secondary=cardapio_produto, back_populates="cardapios")

class Comanda(Base):
    __tablename__ = "comandas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    mesa = Column(String(20))
    status = Column(SQLEnum(StatusComanda), default=StatusComanda.ABERTA)
    valor_total = Column(Numeric(10, 2), default=0)
    taxa_servico = Column(Numeric(10, 2), default=0)
    desconto = Column(Numeric(10, 2), default=0)
    observacoes = Column(Text)
    aberta_em = Column(DateTime(timezone=True), server_default=func.now())
    fechada_em = Column(DateTime(timezone=True))
    
    # Relacionamentos
    cliente = relationship("Usuario", back_populates="comandas")
    pedidos = relationship("Pedido", back_populates="comanda")
    pagamentos = relationship("Pagamento", back_populates="comanda")

class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Numeric(10, 3), nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(StatusPedido), default=StatusPedido.PENDENTE)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    preparado_em = Column(DateTime(timezone=True))
    entregue_em = Column(DateTime(timezone=True))
    
    # Relacionamentos
    comanda = relationship("Comanda", back_populates="pedidos")
    produto = relationship("Produto")

class Venda(Base):
    __tablename__ = "vendas"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"))
    cliente_cpf = Column(String(14))
    numero_venda = Column(String(50), unique=True)
    valor_total = Column(Numeric(10, 2), nullable=False)
    desconto = Column(Numeric(10, 2), default=0)
    tipo_pagamento = Column(SQLEnum(TipoPagamento))
    status = Column(String(20), default="CONCLUIDA")
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="vendas")
    vendedor = relationship("Usuario", back_populates="vendas")
    itens = relationship("ItemVenda", back_populates="venda")

class ItemVenda(Base):
    __tablename__ = "itens_venda"
    
    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Numeric(10, 3), nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    
    # Relacionamentos
    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    tipo_pagamento = Column(SQLEnum(TipoPagamento))
    valor = Column(Numeric(10, 2), nullable=False)
    referencia = Column(String(100))  # Número da transação, código PIX, etc
    status = Column(String(20), default="APROVADO")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    comanda = relationship("Comanda", back_populates="pagamentos")

class CartaoCashless(Base):
    __tablename__ = "cartoes_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    numero = Column(String(50), unique=True, nullable=False)
    tag_rfid = Column(String(50), unique=True)
    saldo = Column(Numeric(10, 2), default=0)
    limite_credito = Column(Numeric(10, 2), default=0)
    bloqueado = Column(Boolean, default=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="cartoes")
    transacoes = relationship("TransacaoCashless", back_populates="cartao")

class TransacaoCashless(Base):
    __tablename__ = "transacoes_cashless"
    
    id = Column(Integer, primary_key=True, index=True)
    cartao_id = Column(Integer, ForeignKey("cartoes_cashless.id"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    tipo = Column(String(20))  # RECARGA, CONSUMO, ESTORNO
    valor = Column(Numeric(10, 2), nullable=False)
    saldo_anterior = Column(Numeric(10, 2))
    saldo_posterior = Column(Numeric(10, 2))
    descricao = Column(String(200))
    referencia = Column(String(100))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cartao = relationship("CartaoCashless", back_populates="transacoes")
    cliente = relationship("Cliente", back_populates="transacoes")

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    tipo_operacao = Column(SQLEnum(TipoOperacao))
    quantidade = Column(Numeric(10, 3), nullable=False)
    saldo_anterior = Column(Numeric(10, 3))
    saldo_posterior = Column(Numeric(10, 3))
    motivo = Column(String(200))
    documento = Column(String(100))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    produto = relationship("Produto", back_populates="movimentacoes")
    usuario = relationship("Usuario")

class Checkin(Base):
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    lista_id = Column(Integer, ForeignKey("listas.id"))
    nome = Column(String(200))
    cpf = Column(String(14))
    tipo_entrada = Column(String(50))  # QR_CODE, MANUAL, FACIAL, RFID
    horario_entrada = Column(DateTime(timezone=True), server_default=func.now())
    horario_saida = Column(DateTime(timezone=True))
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="checkins")
    lista = relationship("Lista", back_populates="checkins")

class Lista(Base):
    __tablename__ = "listas"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # VIP, PAGANTE, CORTESIA, PROMOTER
    quantidade_maxima = Column(Integer)
    valor = Column(Numeric(10, 2), default=0)
    ativa = Column(Boolean, default=True)
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="listas")
    checkins = relationship("Checkin", back_populates="lista")
    convidados = relationship("Convidado", back_populates="lista")

class Convidado(Base):
    __tablename__ = "convidados"
    
    id = Column(Integer, primary_key=True, index=True)
    lista_id = Column(Integer, ForeignKey("listas.id"))
    nome = Column(String(200), nullable=False)
    cpf = Column(String(14))
    email = Column(String(200))
    telefone = Column(String(20))
    confirmado = Column(Boolean, default=False)
    presente = Column(Boolean, default=False)
    
    # Relacionamentos
    lista = relationship("Lista", back_populates="convidados")

class ConfiguracaoImpressora(Base):
    __tablename__ = "configuracoes_impressora"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    modelo = Column(String(100))
    ip = Column(String(15))
    porta = Column(Integer, default=9100)
    tipo = Column(String(50))  # TERMICA, FISCAL, ETIQUETA
    local = Column(String(100))  # BAR, COZINHA, CAIXA
    ativa = Column(Boolean, default=True)
    configuracoes = Column(JSON, default={})

class Integracao(Base):
    __tablename__ = "integracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # COMUNICACAO, ERP, FISCAL, DELIVERY, PESQUISA
    status = Column(SQLEnum(StatusIntegracao), default=StatusIntegracao.DESCONECTADO)
    configuracoes = Column(JSON, default={})
    token = Column(String(500))
    webhook_url = Column(String(500))
    ultima_sincronizacao = Column(DateTime(timezone=True))

class Automacao(Base):
    __tablename__ = "automacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    gatilho = Column(String(100))  # VENDA_REALIZADA, CLIENTE_CADASTRADO, etc
    condicoes = Column(JSON, default={})
    acoes = Column(JSON, default=[])
    status = Column(Boolean, default=True)
    execucoes = Column(Integer, default=0)
    ultima_execucao = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nome = Column(String(100))
    tipo = Column(String(50))  # GRAFICO, METRICA, TABELA, MAPA
    configuracoes = Column(JSON, default={})
    posicao = Column(JSON, default={})  # x, y, width, height
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    usuario = relationship("Usuario")

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    acao = Column(String(100))
    modulo = Column(String(50))
    entidade = Column(String(50))
    entidade_id = Column(Integer)
    dados_anteriores = Column(JSON)
    dados_novos = Column(JSON)
    ip = Column(String(45))
    user_agent = Column(String(500))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario")

class NotificacaoPush(Base):
    __tablename__ = "notificacoes_push"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    titulo = Column(String(200))
    mensagem = Column(Text)
    tipo = Column(String(50))
    lida = Column(Boolean, default=False)
    enviada = Column(Boolean, default=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario")

class PesquisaSatisfacao(Base):
    __tablename__ = "pesquisas_satisfacao"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    nota_geral = Column(Integer)  # 1-5
    nota_atendimento = Column(Integer)
    nota_produtos = Column(Integer)
    nota_ambiente = Column(Integer)
    comentarios = Column(Text)
    respondido_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    cliente = relationship("Cliente")
    evento = relationship("Evento")

class CampanhaMarketing(Base):
    __tablename__ = "campanhas_marketing"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo = Column(String(50))  # EMAIL, SMS, PUSH, WHATSAPP
    segmentacao = Column(JSON, default={})
    conteudo = Column(JSON, default={})
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    status = Column(String(20), default="RASCUNHO")
    enviados = Column(Integer, default=0)
    abertos = Column(Integer, default=0)
    cliques = Column(Integer, default=0)
    conversoes = Column(Integer, default=0)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class CupomDesconto(Base):
    __tablename__ = "cupons_desconto"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200))
    tipo = Column(String(20))  # PERCENTUAL, VALOR_FIXO
    valor = Column(Numeric(10, 2))
    quantidade_maxima = Column(Integer)
    quantidade_usada = Column(Integer, default=0)
    valido_de = Column(DateTime(timezone=True))
    valido_ate = Column(DateTime(timezone=True))
    condicoes = Column(JSON, default={})
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

# Criar índices para melhorar performance
from sqlalchemy import Index

# Índices compostos para queries frequentes
Index('idx_cliente_cpf_empresa', Cliente.cpf, Cliente.empresa_id)
Index('idx_produto_codigo_empresa', Produto.codigo, Produto.empresa_id)
Index('idx_comanda_numero_status', Comanda.numero, Comanda.status)
Index('idx_venda_evento_data', Venda.evento_id, Venda.criado_em)
Index('idx_checkin_evento_data', Checkin.evento_id, Checkin.horario_entrada)