from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum, Date, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
from datetime import datetime

class StatusEvento(enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    CANCELADO = "cancelado"

class TipoLista(enum.Enum):
    VIP = "vip"
    FREE = "free"
    PAGANTE = "pagante"
    PROMOTER = "promoter"
    ANIVERSARIO = "aniversario"
    DESCONTO = "desconto"

class StatusTransacao(enum.Enum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    CANCELADA = "cancelada"

# Removido enum TipoUsuario - agora usando string com validação
# Valores válidos: 'admin', 'promoter', 'cliente'

class Empresa(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    # Dados básicos da empresa
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    inscricao_estadual = Column(String(20))
    inscricao_municipal = Column(String(20))
    
    # Dados de contato
    email = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=False)
    telefone_secundario = Column(String(20))
    whatsapp = Column(String(20))
    site = Column(String(255))
    
    # Responsável
    responsavel_nome = Column(String(255))
    responsavel_cargo = Column(String(100))
    responsavel_email = Column(String(255))
    responsavel_telefone = Column(String(20))
    
    # Endereço completo
    cep = Column(String(10))
    logradouro = Column(String(255))
    numero = Column(String(10))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Dados bancários
    banco = Column(String(100))
    agencia = Column(String(10))
    conta = Column(String(20))
    tipo_conta = Column(String(20))  # 'corrente' ou 'poupanca'
    
    # Observações
    observacoes = Column(Text)
    
    # Status e controle
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    eventos = relationship("Evento", back_populates="empresa")

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefone = Column(String(20))
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False, default="cliente")  # Campo principal para tipo de usuário
    ativo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    eventos_criados = relationship("Evento", back_populates="criador")
    promocoes = relationship("PromoterEvento", back_populates="promoter")
    transacoes = relationship("Transacao", back_populates="usuario")
    checkins = relationship("Checkin", back_populates="usuario")

class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    data_evento = Column(DateTime(timezone=True), nullable=False)
    local = Column(String(255), nullable=False)
    endereco = Column(Text)
    limite_idade = Column(Integer, default=18)
    capacidade_maxima = Column(Integer)
    status = Column(Enum(StatusEvento), default=StatusEvento.ATIVO)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    criador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    empresa = relationship("Empresa", back_populates="eventos")
    criador = relationship("Usuario", back_populates="eventos_criados")
    listas = relationship("Lista", back_populates="evento")
    promoters = relationship("PromoterEvento", back_populates="evento")
    transacoes = relationship("Transacao", back_populates="evento")
    checkins = relationship("Checkin", back_populates="evento")

class Lista(Base):
    __tablename__ = "listas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    tipo = Column(Enum(TipoLista), nullable=False)
    preco = Column(Numeric(10, 2), default=0)
    limite_vendas = Column(Integer)
    vendas_realizadas = Column(Integer, default=0)
    ativa = Column(Boolean, default=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    promoter_id = Column(Integer, ForeignKey("usuarios.id"))
    descricao = Column(Text)
    codigo_cupom = Column(String(50))
    desconto_percentual = Column(Numeric(5, 2), default=0)
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento", back_populates="listas")
    promoter = relationship("Usuario")
    transacoes = relationship("Transacao", back_populates="lista")

class PromoterEvento(Base):
    __tablename__ = "promoter_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    promoter_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    meta_vendas = Column(Integer, default=0)
    vendas_realizadas = Column(Integer, default=0)
    comissao_percentual = Column(Numeric(5, 2), default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    promoter = relationship("Usuario", back_populates="promocoes")
    evento = relationship("Evento", back_populates="promoters")

class Transacao(Base):
    __tablename__ = "transacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    cpf_comprador = Column(String(14), nullable=False, index=True)
    nome_comprador = Column(String(255), nullable=False)
    email_comprador = Column(String(255))
    telefone_comprador = Column(String(20))
    valor = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(StatusTransacao), default=StatusTransacao.PENDENTE)
    metodo_pagamento = Column(String(50))
    codigo_transacao = Column(String(100), unique=True)
    qr_code_ticket = Column(String(100), unique=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    lista_id = Column(Integer, ForeignKey("listas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    ip_origem = Column(String(45))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento", back_populates="transacoes")
    lista = relationship("Lista", back_populates="transacoes")
    usuario = relationship("Usuario", back_populates="transacoes")

class Checkin(Base):
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(14), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    transacao_id = Column(Integer, ForeignKey("transacoes.id"))
    metodo_checkin = Column(String(20))  # cpf, qr_code, cartao
    validacao_cpf = Column(String(3))  # 3 primeiros dígitos para validação
    ip_origem = Column(String(45))
    checkin_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento", back_populates="checkins")
    usuario = relationship("Usuario", back_populates="checkins")
    transacao = relationship("Transacao")

# Adicionar antes dos enums de produto
class CategoriaProduto(Base):
    __tablename__ = "categorias_produtos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    cor = Column(String(7), default="#3b82f6")  # Hex color
    ativo = Column(Boolean, default=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento")
    empresa = relationship("Empresa")

class TipoProduto(enum.Enum):
    BEBIDA = "BEBIDA"
    COMIDA = "COMIDA"
    INGRESSO = "INGRESSO"
    FICHA = "FICHA"
    COMBO = "COMBO"
    VOUCHER = "VOUCHER"

class StatusProduto(enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    ESGOTADO = "ESGOTADO"

class TipoComanda(enum.Enum):
    FISICA = "FISICA"
    VIRTUAL = "VIRTUAL"
    RFID = "RFID"
    NFC = "NFC"

class StatusComanda(enum.Enum):
    ATIVA = "ATIVA"
    BLOQUEADA = "BLOQUEADA"
    CANCELADA = "CANCELADA"

class StatusVendaPDV(enum.Enum):
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    CANCELADA = "CANCELADA"
    ESTORNADA = "ESTORNADA"

class TipoPagamentoPDV(enum.Enum):
    PIX = "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    DINHEIRO = "DINHEIRO"
    SALDO_COMANDA = "SALDO_COMANDA"
    VOUCHER = "VOUCHER"
    SPLIT = "SPLIT"

class Produto(Base):
    __tablename__ = "produtos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    tipo = Column(Enum(TipoProduto), nullable=False)
    preco = Column(Numeric(10, 2), nullable=False)
    codigo_interno = Column(String(20))
    estoque_atual = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=0)
    estoque_maximo = Column(Integer, default=1000)
    controla_estoque = Column(Boolean, default=True)
    status = Column(Enum(StatusProduto), default=StatusProduto.ATIVO)
    categoria = Column(String(100))  # Campo principal para categoria
    imagem_url = Column(String(500))
    # evento_id REMOVIDO - produtos são globais, não atrelados a eventos específicos
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    empresa = relationship("Empresa")
    # evento relationship REMOVIDO - produtos não são mais vinculados a eventos
    itens_venda = relationship("ItemVendaPDV", back_populates="produto")
    movimentos_estoque = relationship("MovimentoEstoque", back_populates="produto")

class Comanda(Base):
    __tablename__ = "comandas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_comanda = Column(String(20), unique=True, nullable=False)
    cpf_cliente = Column(String(14), index=True)
    nome_cliente = Column(String(255))
    tipo = Column(Enum(TipoComanda), nullable=False)
    codigo_rfid = Column(String(50), unique=True)
    qr_code = Column(String(100), unique=True)
    saldo_atual = Column(Numeric(10, 2), default=0)
    saldo_bloqueado = Column(Numeric(10, 2), default=0)
    status = Column(Enum(StatusComanda), default=StatusComanda.ATIVA)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    vendas = relationship("VendaPDV", back_populates="comanda")
    recargas = relationship("RecargaComanda", back_populates="comanda")

class VendaPDV(Base):
    __tablename__ = "vendas_pdv"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_venda = Column(String(20), unique=True, nullable=False)
    cpf_cliente = Column(String(14), index=True)
    nome_cliente = Column(String(255))
    valor_total = Column(Numeric(10, 2), nullable=False)
    valor_desconto = Column(Numeric(10, 2), default=0)
    valor_final = Column(Numeric(10, 2), nullable=False)
    tipo_pagamento = Column(Enum(TipoPagamentoPDV), nullable=False)
    status = Column(Enum(StatusVendaPDV), default=StatusVendaPDV.PENDENTE)
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    usuario_vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    promoter_id = Column(Integer, ForeignKey("usuarios.id"))
    cupom_codigo = Column(String(50))
    observacoes = Column(Text)
    ip_origem = Column(String(45))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    comanda = relationship("Comanda", back_populates="vendas")
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    vendedor = relationship("Usuario", foreign_keys=[usuario_vendedor_id])
    promoter = relationship("Usuario", foreign_keys=[promoter_id])
    itens = relationship("ItemVendaPDV", back_populates="venda")
    pagamentos = relationship("PagamentoPDV", back_populates="venda")

class ItemVendaPDV(Base):
    __tablename__ = "itens_venda_pdv"
    
    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas_pdv.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    preco_total = Column(Numeric(10, 2), nullable=False)
    desconto_aplicado = Column(Numeric(10, 2), default=0)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    venda = relationship("VendaPDV", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_venda")

class PagamentoPDV(Base):
    __tablename__ = "pagamentos_pdv"
    
    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas_pdv.id"), nullable=False)
    tipo_pagamento = Column(Enum(TipoPagamentoPDV), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    codigo_transacao = Column(String(100))
    promoter_id = Column(Integer, ForeignKey("usuarios.id"))
    comissao_percentual = Column(Numeric(5, 2), default=0)
    valor_comissao = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="APROVADA")
    detalhes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    venda = relationship("VendaPDV", back_populates="pagamentos")
    promoter = relationship("Usuario")

class RecargaComanda(Base):
    __tablename__ = "recargas_comanda"
    
    id = Column(Integer, primary_key=True, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    tipo_pagamento = Column(Enum(TipoPagamentoPDV), nullable=False)
    codigo_transacao = Column(String(100))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(String(20), default="APROVADA")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    comanda = relationship("Comanda", back_populates="recargas")
    usuario = relationship("Usuario")

class MovimentoEstoque(Base):
    __tablename__ = "movimentos_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    tipo_movimento = Column(String(20), nullable=False)  # entrada, saida, ajuste
    quantidade = Column(Integer, nullable=False)
    estoque_anterior = Column(Integer, nullable=False)
    estoque_atual = Column(Integer, nullable=False)
    motivo = Column(String(100))
    venda_id = Column(Integer, ForeignKey("vendas_pdv.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    produto = relationship("Produto", back_populates="movimentos_estoque")
    venda = relationship("VendaPDV")
    usuario = relationship("Usuario")

# Enums para Formas de Pagamento
class TipoFormaPagamento(enum.Enum):
    DINHEIRO = "DINHEIRO"
    PIX = "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    TRANSFERENCIA = "TRANSFERENCIA"
    BOLETO = "BOLETO"
    VOUCHER = "VOUCHER"
    CREDITO_LOJA = "CREDITO_LOJA"

class StatusFormaPagamento(enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    MANUTENCAO = "MANUTENCAO"

# Modelo de Formas de Pagamento
class FormaPagamento(Base):
    __tablename__ = "formas_pagamento"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    codigo = Column(String(50), nullable=False, unique=True)
    tipo = Column(Enum(TipoFormaPagamento), nullable=False)
    status = Column(Enum(StatusFormaPagamento), default=StatusFormaPagamento.ATIVO)
    descricao = Column(Text)
    taxa_percentual = Column(Numeric(5,2), default=0.00)  # Taxa em percentual (ex: 2.50 para 2.5%)
    taxa_fixa = Column(Numeric(10,2), default=0.00)  # Taxa fixa em reais
    tempo_compensacao = Column(Integer, default=0)  # Tempo em horas para compensação
    limite_minimo = Column(Numeric(10,2), default=0.00)  # Valor mínimo aceito
    limite_maximo = Column(Numeric(10,2))  # Valor máximo aceito (NULL = ilimitado)
    icone = Column(String(100))  # Nome do ícone ou URL da imagem
    cor_hex = Column(String(7))  # Cor hexadecimal (ex: #1E40AF)
    configuracoes_extras = Column(Text)  # JSON com configurações específicas
    ordem_exibicao = Column(Integer, default=1)  # Ordem na listagem
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    criador = relationship("Usuario", foreign_keys=[criado_por])

# Enums para Import/Export
class StatusImportacao(enum.Enum):
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDA = "CONCLUIDA"
    ERRO = "ERRO"
    CANCELADA = "CANCELADA"

class TipoOperacao(enum.Enum):
    IMPORTACAO = "IMPORTACAO"
    EXPORTACAO = "EXPORTACAO"

class StatusValidacao(enum.Enum):
    VALIDO = "VALIDO"
    ERRO_CRITICO = "ERRO_CRITICO"
    AVISO = "AVISO"

# Tabelas de Import/Export
class OperacaoImportExport(Base):
    __tablename__ = "operacoes_import_export"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_operacao = Column(Enum(TipoOperacao), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    formato_arquivo = Column(String(10), nullable=False)  # csv, xlsx, json, xml
    tamanho_arquivo = Column(Integer)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Status e progresso
    status = Column(Enum(StatusImportacao), default=StatusImportacao.PENDENTE)
    total_registros = Column(Integer, default=0)
    registros_processados = Column(Integer, default=0)
    registros_sucesso = Column(Integer, default=0)
    registros_erro = Column(Integer, default=0)
    registros_aviso = Column(Integer, default=0)
    
    # Configurações
    mapeamento_campos = Column(Text)  # JSON com mapeamento de campos
    filtros_aplicados = Column(Text)  # JSON com filtros para exportação
    campos_personalizados = Column(Text)  # JSON com campos selecionados
    
    # Tempos
    inicio_processamento = Column(DateTime(timezone=True))
    fim_processamento = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Logs e resultados
    log_detalhado = Column(Text)
    url_arquivo_resultado = Column(String(500))
    resumo_operacao = Column(Text)  # JSON com resumo detalhado
    
    # Relationships
    usuario = relationship("Usuario")
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    validacoes = relationship("ValidacaoImportacao", back_populates="operacao")
    
class ValidacaoImportacao(Base):
    __tablename__ = "validacoes_importacao"
    
    id = Column(Integer, primary_key=True, index=True)
    operacao_id = Column(Integer, ForeignKey("operacoes_import_export.id"), nullable=False)
    linha_arquivo = Column(Integer, nullable=False)
    campo = Column(String(100))
    tipo_validacao = Column(String(50))  # required, unique, pattern, range, etc.
    status = Column(Enum(StatusValidacao), nullable=False)
    mensagem = Column(Text, nullable=False)
    valor_original = Column(String(500))
    valor_sugerido = Column(String(500))
    corrigido = Column(Boolean, default=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    operacao = relationship("OperacaoImportExport", back_populates="validacoes")

class TemplateImportacao(Base):
    __tablename__ = "templates_importacao"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    formato = Column(String(10), nullable=False)  # csv, xlsx, json
    mapeamento_padrao = Column(Text, nullable=False)  # JSON
    campos_obrigatorios = Column(Text)  # JSON array
    validacoes_personalizadas = Column(Text)  # JSON
    ativo = Column(Boolean, default=True)
    usuario_criador_id = Column(Integer, ForeignKey("usuarios.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    usuario_criador = relationship("Usuario")
    empresa = relationship("Empresa")

class CaixaPDV(Base):
    __tablename__ = "caixa_pdv"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_caixa = Column(String(10), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    usuario_operador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    valor_abertura = Column(Numeric(10, 2), default=0)
    valor_vendas = Column(Numeric(10, 2), default=0)
    valor_sangrias = Column(Numeric(10, 2), default=0)
    valor_fechamento = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="aberto")  # aberto, fechado
    data_abertura = Column(DateTime(timezone=True), server_default=func.now())
    data_fechamento = Column(DateTime(timezone=True))
    observacoes = Column(Text)
    
    evento = relationship("Evento")
    operador = relationship("Usuario")

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    
    id = Column(Integer, primary_key=True, index=True)
    cpf_usuario = Column(String(14), nullable=False, index=True)
    acao = Column(String(100), nullable=False)
    tabela_afetada = Column(String(50))
    registro_id = Column(Integer)
    dados_anteriores = Column(Text)
    dados_novos = Column(Text)
    ip_origem = Column(String(45))
    user_agent = Column(Text)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    promoter_id = Column(Integer, ForeignKey("usuarios.id"))
    status = Column(String(20), default="sucesso")
    detalhes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    promoter = relationship("Usuario")


class TipoMovimentacaoFinanceira(enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    REPASSE_PROMOTER = "repasse_promoter"
    RECEITA_VENDAS = "receita_vendas"
    RECEITA_LISTAS = "receita_listas"


class StatusMovimentacaoFinanceira(enum.Enum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    CANCELADA = "cancelada"


class MovimentacaoFinanceira(Base):
    __tablename__ = "movimentacoes_financeiras"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    tipo = Column(Enum(TipoMovimentacaoFinanceira), nullable=False)
    categoria = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(StatusMovimentacaoFinanceira), default=StatusMovimentacaoFinanceira.PENDENTE)
    
    usuario_responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    promoter_id = Column(Integer, ForeignKey("usuarios.id"))
    
    comprovante_url = Column(String(500))
    numero_documento = Column(String(100))
    
    observacoes = Column(Text)
    data_vencimento = Column(Date)
    data_pagamento = Column(Date)
    metodo_pagamento = Column(String(50))
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")
    usuario_responsavel = relationship("Usuario", foreign_keys=[usuario_responsavel_id])
    promoter = relationship("Usuario", foreign_keys=[promoter_id])


class CaixaEvento(Base):
    __tablename__ = "caixas_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    data_abertura = Column(DateTime(timezone=True), server_default=func.now())
    data_fechamento = Column(DateTime(timezone=True))
    
    saldo_inicial = Column(Numeric(10, 2), default=0)
    total_entradas = Column(Numeric(10, 2), default=0)
    total_saidas = Column(Numeric(10, 2), default=0)
    total_vendas_pdv = Column(Numeric(10, 2), default=0)
    total_vendas_listas = Column(Numeric(10, 2), default=0)
    saldo_final = Column(Numeric(10, 2), default=0)
    
    status = Column(String(20), default="aberto")
    usuario_abertura_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_fechamento_id = Column(Integer, ForeignKey("usuarios.id"))
    
    observacoes_abertura = Column(Text)
    observacoes_fechamento = Column(Text)
    
    evento = relationship("Evento")
    usuario_abertura = relationship("Usuario", foreign_keys=[usuario_abertura_id])
    usuario_fechamento = relationship("Usuario", foreign_keys=[usuario_fechamento_id])

class TipoConquista(enum.Enum):
    VENDAS = "vendas"
    PRESENCA = "presenca"
    FIDELIDADE = "fidelidade"
    CRESCIMENTO = "crescimento"
    ESPECIAL = "especial"

class NivelBadge(enum.Enum):
    BRONZE = "bronze"
    PRATA = "prata"
    OURO = "ouro"
    PLATINA = "platina"
    DIAMANTE = "diamante"
    LENDA = "lenda"

class Conquista(Base):
    __tablename__ = "conquistas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    tipo = Column(Enum(TipoConquista), nullable=False)
    criterio_valor = Column(Integer, nullable=False)
    badge_nivel = Column(Enum(NivelBadge), nullable=False)
    icone = Column(String(50))
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class PromoterConquista(Base):
    __tablename__ = "promoter_conquistas"
    
    id = Column(Integer, primary_key=True, index=True)
    promoter_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    conquista_id = Column(Integer, ForeignKey("conquistas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    valor_alcancado = Column(Integer, nullable=False)
    data_conquista = Column(DateTime(timezone=True), server_default=func.now())
    notificado = Column(Boolean, default=False)
    
    promoter = relationship("Usuario")
    conquista = relationship("Conquista")
    evento = relationship("Evento")

class MetricaPromoter(Base):
    __tablename__ = "metricas_promoters"
    
    id = Column(Integer, primary_key=True, index=True)
    promoter_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    
    total_vendas = Column(Integer, default=0)
    receita_gerada = Column(Numeric(10, 2), default=0)
    total_convidados = Column(Integer, default=0)
    total_presentes = Column(Integer, default=0)
    taxa_presenca = Column(Numeric(5, 2), default=0)
    taxa_conversao = Column(Numeric(5, 2), default=0)
    crescimento_vendas = Column(Numeric(5, 2), default=0)
    
    posicao_vendas = Column(Integer)
    posicao_presenca = Column(Integer)
    posicao_geral = Column(Integer)
    badge_atual = Column(Enum(NivelBadge), default=NivelBadge.BRONZE)
    
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    promoter = relationship("Usuario")
    evento = relationship("Evento")


# =====================================================
# MEEP Integration Tables
# =====================================================

class ClienteEvento(Base):
    __tablename__ = "clientes_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    nome_completo = Column(String(255), nullable=False)
    nome_social = Column(String(255))
    data_nascimento = Column(Date)
    nome_mae = Column(String(255))
    telefone = Column(String(20))
    email = Column(String(255))
    status = Column(String(50), default='ativo')
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relações adicionadas
    categorias = relationship("ClienteCategoria", back_populates="cliente")

class ValidacaoAcesso(Base):
    __tablename__ = "validacoes_acesso"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    cliente_id = Column(Integer, ForeignKey("clientes_eventos.id"))
    cpf_hash = Column(String(255), nullable=False)
    qr_code_data = Column(Text, nullable=False)
    cpf_digits = Column(String(3), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp_validacao = Column(DateTime(timezone=True), server_default=func.now())
    sucesso = Column(Boolean, default=False)
    motivo_falha = Column(Text)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    device_info = Column(Text)  # JSON string
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    cliente = relationship("ClienteEvento")

class EquipamentoEvento(Base):
    __tablename__ = "equipamentos_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    tipo = Column(String(100), nullable=False)  # 'tablet', 'qr_reader', 'printer', 'pos'
    ip_address = Column(String(45), nullable=False)
    mac_address = Column(String(17))
    status = Column(String(50), default='offline')
    ultima_atividade = Column(DateTime(timezone=True))
    configuracao = Column(Text)  # JSON string
    localizacao = Column(String(255))
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    heartbeat_interval = Column(Integer, default=30)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")
    responsavel = relationship("Usuario")

class SessaoOperador(Base):
    __tablename__ = "sessoes_operadores"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    equipamento_id = Column(Integer, ForeignKey("equipamentos_eventos.id"))
    token_sessao = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))
    inicio_sessao = Column(DateTime(timezone=True), server_default=func.now())
    fim_sessao = Column(DateTime(timezone=True))
    ativo = Column(Boolean, default=True)
    configuracoes = Column(Text)  # JSON string
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    usuario = relationship("Usuario")
    evento = relationship("Evento")
    equipamento = relationship("EquipamentoEvento")

class PrevisaoIA(Base):
    __tablename__ = "previsoes_ia"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    tipo_previsao = Column(String(100), nullable=False)  # 'fluxo_horario', 'pico_entrada', 'estimativa_total'
    dados_entrada = Column(Text, nullable=False)  # JSON string
    resultado_previsao = Column(Text, nullable=False)  # JSON string
    confiabilidade = Column(Numeric(5, 2))  # Percentual de confiança
    timestamp_previsao = Column(DateTime(timezone=True), server_default=func.now())
    aplicada = Column(Boolean, default=False)
    feedback_real = Column(Text)  # JSON string
    precisao_real = Column(Numeric(5, 2))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")

class AnalyticsMEEP(Base):
    __tablename__ = "analytics_meep"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    metrica = Column(String(100), nullable=False)
    valor = Column(Numeric(15, 2))
    valor_anterior = Column(Numeric(15, 2))
    percentual_mudanca = Column(Numeric(5, 2))
    periodo = Column(String(50))  # 'hora', 'dia', 'semana', 'mes'
    timestamp_coleta = Column(DateTime(timezone=True), server_default=func.now())
    dados_detalhados = Column(Text)  # JSON string
    alertas = Column(Text)  # JSON string
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")

class LogSegurancaMEEP(Base):
    __tablename__ = "logs_seguranca_meep"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    tipo_evento = Column(String(100), nullable=False)  # 'tentativa_acesso', 'validacao_cpf', 'erro_sistema'
    gravidade = Column(String(20), default='info')  # 'info', 'warning', 'error', 'critical'
    ip_address = Column(String(45))
    user_agent = Column(Text)
    dados_evento = Column(Text, nullable=False)  # JSON string
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    resolvido = Column(Boolean, default=False)
    timestamp_evento = Column(DateTime(timezone=True), server_default=func.now())
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    usuario = relationship("Usuario")

# ============ SISTEMA DE IMPRESSORAS TÉRMICAS ============
import uuid

class TipoImpressora(enum.Enum):
    COZINHA = "cozinha"
    BAR = "bar"
    SOBREMESA = "sobremesa"
    CAIXA = "caixa"
    GERENCIAL = "gerencial"

class InterfaceImpressora(enum.Enum):
    USB = "usb"
    NETWORK = "network"  # TCP/IP via WiFi/Ethernet
    BLUETOOTH = "bluetooth"

class StatusImpressora(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERRO = "erro"
    MANUTENCAO = "manutencao"

class StatusPrintJob(enum.Enum):
    QUEUED = "queued"
    PRINTING = "printing"
    DONE = "done"
    ERROR = "error"
    RETRY = "retry"

class TipoPrintJob(enum.Enum):
    RECIBO_CAIXA = "recibo_caixa"
    PEDIDO_COZINHA = "pedido_cozinha"
    PEDIDO_BAR = "pedido_bar"
    COMANDA_RECHARGE = "comanda_recharge"
    RELATORIO = "relatorio"

class Impressora(Base):
    __tablename__ = "impressoras"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)  # "Cozinha 01", "Bar Principal"
    tipo = Column(Enum(TipoImpressora), nullable=False)
    interface = Column(Enum(InterfaceImpressora), nullable=False)
    endereco = Column(String(255), nullable=False)  # IP:porta, USB vid:pid, BT MAC
    
    # Especificações técnicas
    largura_mm = Column(Integer, default=80)  # 58mm ou 80mm
    colunas = Column(Integer, default=42)     # 32 colunas (58mm) ou 42 (80mm)
    perfil_escpos = Column(String(50), default="epson")  # epson, star, bematech
    densidade = Column(Integer, default=8)    # Intensidade de impressão
    
    # Configuração operacional
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    localizacao = Column(String(255))  # "Cozinha Andar 1", "Bar Terraço"
    ativo = Column(Boolean, default=True)
    impressora_backup_id = Column(String(36), ForeignKey("impressoras.id"))
    
    # Status e monitoramento
    status = Column(Enum(StatusImpressora), default=StatusImpressora.OFFLINE)
    ultimo_heartbeat = Column(DateTime(timezone=True))
    ip_bridge = Column(String(45))  # IP do bridge local quando USB/BT
    versao_driver = Column(String(50))
    
    # Configurações avançadas (JSON)
    configuracoes = Column(Text)  # {"corte_automatico": true, "beep": false, etc}
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")
    impressora_backup = relationship("Impressora", remote_side=[id])
    jobs = relationship("PrintJob", back_populates="impressora")

class PrintTemplate(Base):
    __tablename__ = "print_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)  # "Recibo Caixa Padrão"
    tipo_job = Column(Enum(TipoPrintJob), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    
    # Template Handlebars/Jinja2
    template_content = Column(Text, nullable=False)
    
    # Comandos ESC/POS específicos (JSON)
    comandos_escpos = Column(Text)  # {"densidade": 8, "corte": true, "pulse": false}
    
    # Configurações de layout
    largura_colunas = Column(Integer, default=42)
    fonte_tamanho = Column(String(10), default="normal")  # small, normal, large
    
    ativo = Column(Boolean, default=True)
    padrao = Column(Boolean, default=False)  # Template padrão para o tipo
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")

class PrintJob(Base):
    __tablename__ = "print_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    impressora_id = Column(String(36), ForeignKey("impressoras.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("print_templates.id"))
    
    tipo = Column(Enum(TipoPrintJob), nullable=False)
    prioridade = Column(Integer, default=1)  # 1=normal, 2=alta, 3=urgente
    
    # Dados para renderização do template (JSON)
    payload = Column(Text, nullable=False)
    
    # Relacionamentos com entidades do sistema
    venda_pdv_id = Column(Integer, ForeignKey("vendas_pdv.id"))
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    
    # Controle de execução
    status = Column(Enum(StatusPrintJob), default=StatusPrintJob.QUEUED)
    tentativas = Column(Integer, default=0)
    max_tentativas = Column(Integer, default=3)
    erro_msg = Column(Text)
    
    # Auditoria
    cpf_operador = Column(String(11), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    ip_cliente = Column(String(45))
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    processado_em = Column(DateTime(timezone=True))
    impresso_em = Column(DateTime(timezone=True))
    
    # Relacionamentos
    impressora = relationship("Impressora", back_populates="jobs")
    template = relationship("PrintTemplate")
    venda_pdv = relationship("VendaPDV")
    comanda = relationship("Comanda")
    evento = relationship("Evento")
    usuario = relationship("Usuario")

class PrintJobLog(Base):
    __tablename__ = "print_job_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), ForeignKey("print_jobs.id"), nullable=False)
    status_anterior = Column(Enum(StatusPrintJob))
    status_novo = Column(Enum(StatusPrintJob), nullable=False)
    mensagem = Column(Text)
    detalhes_erro = Column(Text)  # Stack trace, código de erro da impressora
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    job = relationship("PrintJob")

# ====== NOVOS MODELOS BASEADOS NA ENGENHARIA REVERSA ======

# Sistema de Categorias de Clientes
class CategoriaCliente(Base):
    __tablename__ = "categorias_clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text)
    icone = Column(String(50))  # Nome do ícone material-ui
    cor = Column(String(7))  # Cor hexadecimal
    lista_convidado = Column(Boolean, default=False)  # Se aparece em listas de convidados
    desconto_padrao = Column(Numeric(5, 2))  # Desconto padrão em %
    beneficios = Column(Text)  # JSON com benefícios da categoria
    ordem = Column(Integer, default=0)  # Ordem de exibição
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    clientes = relationship("ClienteCategoria", back_populates="categoria")

# Associação Cliente-Categoria
class ClienteCategoria(Base):
    __tablename__ = "clientes_categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes_eventos.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias_clientes.id"), nullable=False)
    data_inicio = Column(DateTime(timezone=True), server_default=func.now())
    data_fim = Column(DateTime(timezone=True))  # Null = ativo
    observacoes = Column(Text)
    
    cliente = relationship("ClienteEvento", back_populates="categorias")
    categoria = relationship("CategoriaCliente", back_populates="clientes")

# Sistema de Pesquisa de Satisfação
class PesquisaSatisfacao(Base):
    __tablename__ = "pesquisas_satisfacao"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    tipo_integracao = Column(String(50))  # 'track.co', 'interno', 'google_forms'
    url_pesquisa = Column(String(500))
    qr_code = Column(Text)  # Base64 do QR Code
    configuracoes = Column(Text)  # JSON com configs específicas
    ativa = Column(Boolean, default=True)
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    total_respostas = Column(Integer, default=0)
    nota_media = Column(Numeric(3, 2))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    respostas = relationship("RespostaPesquisa", back_populates="pesquisa")

class RespostaPesquisa(Base):
    __tablename__ = "respostas_pesquisa"
    
    id = Column(Integer, primary_key=True, index=True)
    pesquisa_id = Column(Integer, ForeignKey("pesquisas_satisfacao.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes_eventos.id"))
    nota = Column(Integer)  # 1-10
    comentario = Column(Text)
    dados_resposta = Column(Text)  # JSON com todas as respostas
    origem = Column(String(50))  # 'app', 'qrcode', 'totem', 'pos'
    ip_origem = Column(String(45))
    data_resposta = Column(DateTime(timezone=True), server_default=func.now())
    
    pesquisa = relationship("PesquisaSatisfacao", back_populates="respostas")
    cliente = relationship("ClienteEvento")

# Sistema de Fidelidade
class ProgramaFidelidade(Base):
    __tablename__ = "programas_fidelidade"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo_programa = Column(String(50))  # 'pontos', 'cashback', 'niveis'
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    niveis = relationship("NivelFidelidade", back_populates="programa")
    participantes = relationship("ParticipanteFidelidade", back_populates="programa")

class NivelFidelidade(Base):
    __tablename__ = "niveis_fidelidade"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("programas_fidelidade.id"), nullable=False)
    nome = Column(String(50), nullable=False)  # 'Bronze', 'Prata', 'Ouro'
    pontos_minimos = Column(Integer, default=0)
    pontos_maximos = Column(Integer)
    cor = Column(String(7))  # Cor hexadecimal
    icone = Column(String(50))
    beneficios = Column(Text)  # JSON com benefícios
    desconto_percentual = Column(Numeric(5, 2))
    multiplicador_pontos = Column(Numeric(3, 2), default=1.0)
    ordem = Column(Integer, default=0)
    
    programa = relationship("ProgramaFidelidade", back_populates="niveis")

class ParticipanteFidelidade(Base):
    __tablename__ = "participantes_fidelidade"
    
    id = Column(Integer, primary_key=True, index=True)
    programa_id = Column(Integer, ForeignKey("programas_fidelidade.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes_eventos.id"), nullable=False)
    nivel_atual_id = Column(Integer, ForeignKey("niveis_fidelidade.id"))
    pontos_totais = Column(Integer, default=0)
    pontos_disponiveis = Column(Integer, default=0)
    data_adesao = Column(DateTime(timezone=True), server_default=func.now())
    data_ultima_movimentacao = Column(DateTime(timezone=True))
    
    programa = relationship("ProgramaFidelidade", back_populates="participantes")
    cliente = relationship("ClienteEvento")
    nivel_atual = relationship("NivelFidelidade")
    movimentacoes = relationship("MovimentacaoPontos", back_populates="participante")

class MovimentacaoPontos(Base):
    __tablename__ = "movimentacoes_pontos"
    
    id = Column(Integer, primary_key=True, index=True)
    participante_id = Column(Integer, ForeignKey("participantes_fidelidade.id"), nullable=False)
    tipo = Column(String(20))  # 'credito', 'debito', 'expiracao'
    pontos = Column(Integer, nullable=False)
    descricao = Column(String(255))
    referencia_tipo = Column(String(50))  # 'venda', 'bonus', 'resgate'
    referencia_id = Column(Integer)  # ID da venda, bonus, etc
    data_movimentacao = Column(DateTime(timezone=True), server_default=func.now())
    data_expiracao = Column(DateTime(timezone=True))
    
    participante = relationship("ParticipanteFidelidade", back_populates="movimentacoes")

# Sistema de Automação
class Automacao(Base):
    __tablename__ = "automacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    gatilho_tipo = Column(String(50))  # 'evento', 'horario', 'condicao', 'webhook'
    gatilho_config = Column(Text)  # JSON com configuração do gatilho
    acoes = Column(Text)  # JSON com lista de ações
    condicoes = Column(Text)  # JSON com condições
    status = Column(String(20), default='ativo')  # 'ativo', 'inativo', 'pausado'
    ultima_execucao = Column(DateTime(timezone=True))
    proxima_execucao = Column(DateTime(timezone=True))
    execucoes_total = Column(Integer, default=0)
    execucoes_sucesso = Column(Integer, default=0)
    execucoes_erro = Column(Integer, default=0)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    logs = relationship("LogAutomacao", back_populates="automacao")

class LogAutomacao(Base):
    __tablename__ = "logs_automacao"
    
    id = Column(Integer, primary_key=True, index=True)
    automacao_id = Column(Integer, ForeignKey("automacoes.id"), nullable=False)
    status = Column(String(20))  # 'sucesso', 'erro', 'parcial'
    gatilho_dados = Column(Text)  # JSON com dados do gatilho
    acoes_executadas = Column(Text)  # JSON com resultado das ações
    erro_mensagem = Column(Text)
    tempo_execucao = Column(Integer)  # Em millisegundos
    data_execucao = Column(DateTime(timezone=True), server_default=func.now())
    
    automacao = relationship("Automacao", back_populates="logs")

# Sistema de Business Intelligence (BI)
class DashboardBI(Base):
    __tablename__ = "dashboards_bi"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo = Column(String(50))  # 'operacional', 'financeiro', 'vendas', 'custom'
    layout = Column(Text)  # JSON com configuração do layout
    filtros_padrao = Column(Text)  # JSON com filtros padrão
    publico = Column(Boolean, default=False)
    usuario_criador_id = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    widgets = relationship("WidgetBI", back_populates="dashboard")
    
class WidgetBI(Base):
    __tablename__ = "widgets_bi"
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards_bi.id"), nullable=False)
    tipo = Column(String(50))  # 'grafico_linha', 'grafico_pizza', 'kpi', 'tabela', 'mapa'
    titulo = Column(String(100))
    consulta_sql = Column(Text)  # Query para buscar dados
    configuracao = Column(Text)  # JSON com configuração do widget
    posicao_x = Column(Integer, default=0)
    posicao_y = Column(Integer, default=0)
    largura = Column(Integer, default=4)
    altura = Column(Integer, default=4)
    auto_refresh = Column(Integer)  # Segundos para auto-refresh
    
    dashboard = relationship("DashboardBI", back_populates="widgets")

# Sistema de Integrações
class Integracao(Base):
    __tablename__ = "integracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # 'comunicacao', 'erp', 'fiscal', 'delivery', 'pagamento'
    provedor = Column(String(50))  # 'whatsapp', 'ifood', 'omie', etc
    status = Column(String(20), default='desconectado')  # 'conectado', 'desconectado', 'erro'
    configuracao = Column(Text)  # JSON com credenciais e configs (criptografado)
    webhook_url = Column(String(500))
    ultima_sincronizacao = Column(DateTime(timezone=True))
    proxima_sincronizacao = Column(DateTime(timezone=True))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    logs = relationship("LogIntegracao", back_populates="integracao")

class LogIntegracao(Base):
    __tablename__ = "logs_integracao"
    
    id = Column(Integer, primary_key=True, index=True)
    integracao_id = Column(Integer, ForeignKey("integracoes.id"), nullable=False)
    tipo_operacao = Column(String(50))  # 'envio', 'recepcao', 'sincronizacao'
    status = Column(String(20))  # 'sucesso', 'erro', 'pendente'
    dados_enviados = Column(Text)
    dados_recebidos = Column(Text)
    erro_mensagem = Column(Text)
    tempo_resposta = Column(Integer)  # Em millisegundos
    data_operacao = Column(DateTime(timezone=True), server_default=func.now())
    
    integracao = relationship("Integracao", back_populates="logs")

# Sistema de Soluções Online
class ConfiguracaoApp(Base):
    __tablename__ = "configuracoes_app"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    visivel_no_app = Column(Boolean, default=True)
    permite_consumo = Column(Boolean, default=True)
    pagamento_online = Column(Boolean, default=False)
    checkin_proximidade = Column(Boolean, default=True)
    distancia_checkin = Column(Integer, default=0)  # Em metros
    checkin_remoto = Column(Boolean, default=False)
    ativacao_qrcode = Column(Boolean, default=False)
    categoria_app = Column(String(50))
    tipo_operacao = Column(String(50))  # 'ficha', 'cartao', 'comanda', 'mesa'
    cardapio_id = Column(Integer)
    notificacao_push = Column(Boolean, default=True)
    destaque_perfil = Column(Boolean, default=False)
    taxa_servico_habilitada = Column(Boolean, default=False)
    taxa_servico_percentual = Column(Numeric(5, 2), default=0)
    configuracao_adicional = Column(Text)  # JSON com configs extras
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")

# COMENTADO - DUPLICAÇÃO COM models_cashless.py
# class CardapioDigital(Base):
#     __tablename__ = "cardapios_digitais"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     evento_id = Column(Integer, ForeignKey("eventos.id"))
#     nome = Column(String(100), nullable=False)
#     slug = Column(String(100), unique=True)
#     uuid = Column(String(36), unique=True)  # UUID para URL única
#     qr_code = Column(Text)  # Base64 do QR Code
#     url_completa = Column(String(500))
#     ativo = Column(Boolean, default=True)
#     visualizacoes = Column(Integer, default=0)
#     configuracao = Column(Text)  # JSON com configuração do layout
#     criado_em = Column(DateTime(timezone=True), server_default=func.now())
#     
#     evento = relationship("Evento")

# Sistema de Tickets/Ingressos
class EventoTicket(Base):
    __tablename__ = "eventos_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    data_inicio_vendas = Column(DateTime(timezone=True))
    data_fim_vendas = Column(DateTime(timezone=True))
    capacidade_total = Column(Integer)
    vendidos = Column(Integer, default=0)
    status = Column(String(20), default='ativo')  # 'ativo', 'pausado', 'esgotado', 'finalizado'
    imagem_capa = Column(Text)
    configuracao = Column(Text)  # JSON com configs do evento
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    # lotes = relationship("LoteTicket", back_populates="evento_ticket")  # TEMPORARIAMENTE COMENTADO - CONFLITO
    # 
    # vendas = relationship("VendaTicket", back_populates="evento_ticket")  # TEMPORARIAMENTE COMENTADO  # COMENTADO - CONFLITO BACK_POPULATES

class LoteTicket(Base):
    __tablename__ = "lotes_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_ticket_id = Column(Integer, ForeignKey("eventos_tickets.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    numero = Column(Integer, default=1)
    quantidade = Column(Integer, nullable=False)
    vendidos = Column(Integer, default=0)
    valor = Column(Numeric(10, 2), nullable=False)
    taxa_servico = Column(Numeric(10, 2), default=0)
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # #  evento_ticket = relationship("EventoTicket", back_populates="lotes")  # TEMPORARIAMENTE COMENTADO  # TEMPORARIAMENTE COMENTADO

class VendaTicket(Base):
    __tablename__ = "vendas_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_ticket_id = Column(Integer, ForeignKey("eventos_tickets.id"), nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes_tickets.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes_eventos.id"))
    codigo_venda = Column(String(20), unique=True)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Numeric(10, 2), nullable=False)
    taxa_servico = Column(Numeric(10, 2))
    valor_total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20))  # 'pendente', 'pago', 'cancelado', 'usado'
    forma_pagamento = Column(String(50))
    qr_code = Column(Text)  # QR Code do ingresso
    data_venda = Column(DateTime(timezone=True), server_default=func.now())
    data_uso = Column(DateTime(timezone=True))
    
    # 
    
    # evento_ticket = relationship("EventoTicket", back_populates="vendas")  # TEMPORARIAMENTE COMENTADO  # COMENTADO - CONFLITO BACK_POPULATES
    lote = relationship("LoteTicket")
    cliente = relationship("ClienteEvento")

# Sistema aprimorado de Colaboradores e Cargos
class Cargo(Base):
    __tablename__ = "cargos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text)
    nivel_hierarquia = Column(Integer, default=0)  # Para organização hierárquica
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    permissoes = relationship("PermissaoCargo", back_populates="cargo")
    colaboradores = relationship("Colaborador", back_populates="cargo")

class Permissao(Base):
    __tablename__ = "permissoes"
    
    id = Column(Integer, primary_key=True, index=True)
    modulo = Column(String(50), nullable=False)  # 'dashboard', 'vendas', 'estoque', etc
    acao = Column(String(50), nullable=False)  # 'visualizar', 'criar', 'editar', 'deletar'
    descricao = Column(String(255))
    
    cargos = relationship("PermissaoCargo", back_populates="permissao")

class PermissaoCargo(Base):
    __tablename__ = "permissoes_cargos"
    
    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    permissao_id = Column(Integer, ForeignKey("permissoes.id"), nullable=False)
    
    cargo = relationship("Cargo", back_populates="permissoes")
    permissao = relationship("Permissao", back_populates="cargos")

class Colaborador(Base):
    __tablename__ = "colaboradores"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    matricula = Column(String(20), unique=True)
    data_admissao = Column(Date)
    data_demissao = Column(Date)
    salario = Column(Numeric(10, 2))
    comissao_percentual = Column(Numeric(5, 2))
    meta_mensal = Column(Numeric(10, 2))
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    usuario = relationship("Usuario")
    cargo = relationship("Cargo", back_populates="colaboradores")
    empresa = relationship("Empresa")

# Sistema de Mapa de Operação
class MapaOperacao(Base):
    __tablename__ = "mapas_operacao"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # 'setores', 'mesas', 'areas', 'pontos_venda'
    configuracao_layout = Column(Text)  # JSON com layout do mapa
    imagem_fundo = Column(Text)  # Base64 ou URL da imagem de fundo
    largura = Column(Integer)
    altura = Column(Integer)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    elementos = relationship("ElementoMapa", back_populates="mapa")

class ElementoMapa(Base):
    __tablename__ = "elementos_mapa"
    
    id = Column(Integer, primary_key=True, index=True)
    mapa_id = Column(Integer, ForeignKey("mapas_operacao.id"), nullable=False)
    tipo = Column(String(50))  # 'mesa', 'setor', 'pdv', 'entrada', 'saida', 'bar'
    codigo = Column(String(50))
    nome = Column(String(100))
    capacidade = Column(Integer)
    status = Column(String(20))  # 'livre', 'ocupado', 'reservado', 'manutencao'
    posicao_x = Column(Integer)
    posicao_y = Column(Integer)
    largura = Column(Integer)
    altura = Column(Integer)
    rotacao = Column(Integer, default=0)
    cor = Column(String(7))
    icone = Column(String(50))
    dados_adicionais = Column(Text)  # JSON com dados específicos
    
    mapa = relationship("MapaOperacao", back_populates="elementos")

# Import inventory models to ensure they are registered with SQLAlchemy
try:
    from .inventory.models import (
        Category, Unit, Product, Location, MovementReason,
        StockMovement, StockMovementLine, StockLevel,
        MovementTypeEnum, ReasonDirectionEnum
    )
except ImportError:
    # Inventory module is optional, ignore if not available
    pass

# Import mobile models to ensure they are registered with SQLAlchemy
try:
    from .models_mobile import (
        SessaoGarcom, ValidacaoNFCMobile, CategoriaMobile, ProdutoMobile,
        PedidoMobile, ItemPedidoMobile, ConfiguracaoMobile, ComandaNFC,
        LogAtividadeMobile, ImpressaoPedidoMobile
    )
except ImportError:
    # Mobile module is optional, ignore if not available
    pass

# ====== MODELOS ADICIONAIS FALTANTES ======

class FluxoTrabalho(Base):
    __tablename__ = "fluxos_trabalho"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(50))
    passos = Column(Text)  # JSON com passos do fluxo
    variaveis = Column(Text)  # JSON com variáveis do fluxo
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))

class ExecucaoFluxo(Base):
    __tablename__ = "execucoes_fluxo"
    
    id = Column(Integer, primary_key=True, index=True)
    fluxo_id = Column(Integer, ForeignKey("fluxos_trabalho.id"))
    status = Column(String(20))  # pendente, executando, sucesso, erro, cancelado
    contexto = Column(Text)  # JSON com contexto da execução
    resultado = Column(Text)  # JSON com resultado
    erro = Column(Text)
    iniciado_em = Column(DateTime(timezone=True), default=datetime.now)
    finalizado_em = Column(DateTime(timezone=True))

class WebhookIntegracao(Base):
    __tablename__ = "webhooks_integracao"
    
    id = Column(Integer, primary_key=True, index=True)
    integracao_id = Column(Integer, ForeignKey("integracoes.id"))
    url = Column(String(255), nullable=False)
    evento = Column(String(50), nullable=False)
    ativo = Column(Boolean, default=True)
    headers = Column(Text)  # JSON
    secret = Column(String(255))
    total_chamadas = Column(Integer, default=0)
    total_erros = Column(Integer, default=0)
    ultima_chamada = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

class SolucaoOnline(Base):
    __tablename__ = "solucoes_online"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # app, web, pwa, api
    descricao = Column(Text)
    url = Column(String(255))
    recursos = Column(Text)  # JSON lista de recursos
    configuracoes = Column(Text)  # JSON
    icone = Column(String(255))
    ordem = Column(Integer, default=0)
    ativa = Column(Boolean, default=True)
    total_acessos = Column(Integer, default=0)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class RecursoApp(Base):
    __tablename__ = "recursos_app"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    categoria = Column(String(50))
    descricao = Column(Text)
    versao = Column(String(20))
    dependencias = Column(Text)  # JSON
    configuracao_padrao = Column(Text)  # JSON
    documentacao_url = Column(String(255))
    gratuito = Column(Boolean, default=True)
    preco = Column(Float)
    popularidade = Column(Integer, default=0)
    total_instalacoes = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class TipoTicket(Base):
    __tablename__ = "tipos_ticket"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    preco_base = Column(Float, nullable=False)
    quantidade_total = Column(Integer, nullable=False)
    quantidade_disponivel = Column(Integer)
    quantidade_vendida = Column(Integer, default=0)
    quantidade_por_pessoa = Column(Integer, default=1)
    beneficios = Column(Text)  # JSON
    restricoes = Column(Text)  # JSON
    categoria = Column(String(50))
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)
    
    # evento = relationship("Evento", back_populates="tipos_ticket")  # COMENTADO - CONFLITO BACK_POPULATES
    # lotes = relationship("LoteTicket", back_populates="tipo_ticket")  # TEMPORARIAMENTE COMENTADO - CONFLITO
    # 
    # tickets = relationship("Ticket", back_populates="tipo_ticket")  # COMENTADO - CONFLITO

# TEMPORARIAMENTE COMENTADO - CONFLITO COM LoteTicket da linha 1320
# class LoteTicket(Base):
#     __tablename__ = "lotes_ticket"
    
#     id = Column(Integer, primary_key=True, index=True)
#     tipo_ticket_id = Column(Integer, ForeignKey("tipos_ticket.id"))
#     nome = Column(String(100), nullable=False)
#     quantidade = Column(Integer, nullable=False)
#     quantidade_vendida = Column(Integer, default=0)
#     preco = Column(Float, nullable=False)
#     data_inicio = Column(DateTime(timezone=True), nullable=False)
#     data_fim = Column(DateTime(timezone=True))
#     ordem = Column(Integer, default=0)
#     ativo = Column(Boolean, default=True)
#     criado_em = Column(DateTime(timezone=True), default=datetime.now)
    
#     #      tipo_ticket = relationship("TipoTicket", back_populates="lotes")  # TEMPORARIAMENTE COMENTADO
    # 
    # tickets = relationship("Ticket", back_populates="lote")  # COMENTADO - CONFLITO

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_ticket_id = Column(Integer, ForeignKey("tipos_ticket.id"))
    lote_id = Column(Integer, ForeignKey("lotes_ticket.id"))
    cliente_id = Column(Integer, ForeignKey("clientes_eventos.id"))
    codigo = Column(String(50), unique=True, nullable=False)
    qr_code = Column(Text)
    status = Column(String(20))  # disponivel, reservado, vendido, usado, cancelado
    valor_pago = Column(Float)
    forma_pagamento = Column(String(50))
    nome_titular = Column(String(100))
    cpf_titular = Column(String(20))
    email_titular = Column(String(100))
    telefone_titular = Column(String(20))
    data_compra = Column(DateTime(timezone=True), default=datetime.now)
    data_uso = Column(DateTime(timezone=True))
    usado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    data_cancelamento = Column(DateTime(timezone=True))
    motivo_cancelamento = Column(Text)
    
    # 
    
    # tipo_ticket = relationship("TipoTicket", back_populates="tickets")  # COMENTADO - CONFLITO
    # lote = relationship("LoteTicket", back_populates="tickets")  # COMENTADO - CONFLITO
    cliente = relationship("ClienteEvento")

class TransferenciaTicket(Base):
    __tablename__ = "transferencias_ticket"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    cliente_anterior_id = Column(Integer, ForeignKey("clientes_eventos.id"))
    cliente_novo_id = Column(Integer, ForeignKey("clientes_eventos.id"))
    motivo = Column(Text)
    data_transferencia = Column(DateTime(timezone=True), default=datetime.now)

class EscalaTrabalho(Base):
    __tablename__ = "escalas_trabalho"
    
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=False)
    tipo = Column(String(20))  # normal, plantao, revezamento, evento
    status = Column(String(20))  # agendada, em_andamento, concluida, cancelada
    local = Column(String(255))
    horas_previstas = Column(Float)
    horas_trabalhadas = Column(Float)
    checkin_realizado = Column(DateTime(timezone=True))
    checkout_realizado = Column(DateTime(timezone=True))
    localizacao_checkin = Column(Text)  # JSON com lat/lng
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    colaborador = relationship("Colaborador", back_populates="escalas")
    tarefas = relationship("TarefaColaborador", back_populates="escala")

class TarefaColaborador(Base):
    __tablename__ = "tarefas_colaborador"
    
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"))
    escala_id = Column(Integer, ForeignKey("escalas_trabalho.id"))
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    prioridade = Column(String(20))  # baixa, media, alta, urgente
    status = Column(String(20))  # pendente, em_andamento, concluida, cancelada
    prazo = Column(DateTime(timezone=True))
    data_conclusao = Column(DateTime(timezone=True))
    categoria = Column(String(50))
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    colaborador = relationship("Colaborador", back_populates="tarefas")
    escala = relationship("EscalaTrabalho", back_populates="tarefas")

# Adicionar relacionamentos aos modelos existentes
# Evento.tipos_ticket = relationship("TipoTicket", back_populates="evento")  # COMENTADO - CONFLITO RELACIONAMENTO
Colaborador.escalas = relationship("EscalaTrabalho", back_populates="colaborador")
Colaborador.tarefas = relationship("TarefaColaborador", back_populates="colaborador")

# Classes de estoque temporárias para resolver importações
class ProdutoEstoque(Base):
    __tablename__ = "produtos_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    codigo = Column(String(100))
    sku = Column(String(100), unique=True)
    categoria_id = Column(Integer)
    local_id = Column(Integer) 
    quantidade = Column(Integer, default=0)
    preco = Column(Float)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

class LocalEstoque(Base):
    __tablename__ = "locais_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    codigo = Column(String(100), unique=True)
    ativo = Column(Boolean, default=True)

class CategoriaEstoque(Base):
    __tablename__ = "categorias_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)

class ContagemEstoque(Base):
    __tablename__ = "contagens_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    status = Column(String(50), default="aberta")
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

class ItemContagemEstoque(Base):
    __tablename__ = "itens_contagem_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    contagem_id = Column(Integer, ForeignKey("contagens_estoque.id"))
    produto_id = Column(Integer, ForeignKey("produtos_estoque.id"))
    quantidade_contada = Column(Integer)
    quantidade_sistema = Column(Integer)

class AlertaEstoque(Base):
    __tablename__ = "alertas_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos_estoque.id"))
    tipo_alerta = Column(String(50))
    mensagem = Column(Text)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

class ItemContagem(Base):
    __tablename__ = "itens_contagem"
    
    id = Column(Integer, primary_key=True, index=True)
    contagem_id = Column(Integer, ForeignKey("contagens_estoque.id"))
    produto_id = Column(Integer, ForeignKey("produtos_estoque.id"))
    quantidade_contada = Column(Integer)
    quantidade_sistema = Column(Integer)

