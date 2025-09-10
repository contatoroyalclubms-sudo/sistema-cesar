from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum, Date, Float, JSON, Time
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
    # MODELO SIMPLIFICADO: apenas campos básicos que sabemos que existem
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=False)
    ativa = Column(Boolean, default=True)
    
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
    tipo_usuario = Column(Enum(TipoProduto), nullable=False)  # ✅ Corrigido: usar tipo_usuario que existe no banco
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

# ====== MODELOS AVANÇADOS KDS E WORKFLOW ======

class FilaKDS(Base):
    __tablename__ = "filas_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    nome = Column(String(100), nullable=False)
    cor = Column(String(7), default="#3B82F6")  # Hex color
    ordem = Column(Integer, default=0)
    tempo_maximo_minutos = Column(Integer, default=30)
    auto_mover = Column(Boolean, default=True)
    notificar_atraso = Column(Boolean, default=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class FluxoKDS(Base):
    __tablename__ = "fluxos_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo = Column(String(50))  # sequencial, paralelo, condicional
    estacoes = Column(Text)  # JSON array de estação IDs
    regras = Column(Text)  # JSON com regras do fluxo
    tempo_estimado_total = Column(Integer)  # minutos
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class EtapaFluxoKDS(Base):
    __tablename__ = "etapas_fluxo_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    fluxo_id = Column(Integer, ForeignKey("fluxos_kds.id"))
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"))
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    ordem = Column(Integer)
    status = Column(String(20))  # pendente, em_preparo, concluida, pulada
    tempo_estimado = Column(Integer)  # minutos
    tempo_real = Column(Integer)  # minutos calculados
    observacoes = Column(Text)
    iniciado_em = Column(DateTime(timezone=True))
    concluido_em = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

class NotificacaoKDS(Base):
    __tablename__ = "notificacoes_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50))  # atraso, erro, alerta, info
    titulo = Column(String(200), nullable=False)
    mensagem = Column(Text)
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    lida = Column(Boolean, default=False)
    urgente = Column(Boolean, default=False)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    lida_em = Column(DateTime(timezone=True))

class TemplateFluxoKDS(Base):
    __tablename__ = "templates_fluxo_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50))  # bebidas, comidas, sobremesas, etc.
    fluxo_config = Column(Text)  # JSON com configuração do template
    tempo_estimado = Column(Integer)
    complexidade = Column(String(20))  # simples, medio, complexo
    tags = Column(Text)  # JSON array de tags
    uso_count = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))

class MetricaKDS(Base):
    __tablename__ = "metricas_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    data_coleta = Column(Date, nullable=False)
    total_pedidos = Column(Integer, default=0)
    pedidos_concluidos = Column(Integer, default=0)
    tempo_medio_preparo = Column(Float)  # minutos
    tempo_maximo_preparo = Column(Float)  # minutos
    tempo_minimo_preparo = Column(Float)  # minutos
    taxa_atraso = Column(Float)  # porcentagem
    picos_demanda = Column(Text)  # JSON com horários de pico
    eficiencia = Column(Float)  # porcentagem
    satisfacao = Column(Float)  # pontuação média
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class AlertaKDS(Base):
    __tablename__ = "alertas_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50))  # tempo_excedido, fila_cheia, equipamento_offline
    severidade = Column(String(20))  # baixa, media, alta, critica
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"), nullable=True)
    regra_config = Column(Text)  # JSON com configuração que gerou o alerta
    resolvido = Column(Boolean, default=False)
    resolvido_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    resolvido_em = Column(DateTime(timezone=True))
    notas_resolucao = Column(Text)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

# ====== SISTEMA DE SPLIT PAYMENTS AVANÇADO ======

class SplitConfiguration(Base):
    __tablename__ = "split_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo = Column(String(50))  # percentual, fixo, variavel, condicional
    configuracao = Column(Text)  # JSON com regras de split
    ativo = Column(Boolean, default=True)
    aplicar_automatico = Column(Boolean, default=False)
    condicoes_aplicacao = Column(Text)  # JSON com condições para aplicar
    taxa_plataforma = Column(Float, default=0.0)  # Taxa da plataforma
    taxa_gateway = Column(Float, default=0.0)  # Taxa do gateway
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))

class SplitRecipient(Base):
    __tablename__ = "split_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    split_config_id = Column(Integer, ForeignKey("split_configurations.id"))
    nome = Column(String(100), nullable=False)
    documento = Column(String(20))  # CPF/CNPJ
    email = Column(String(255))
    telefone = Column(String(20))
    banco_codigo = Column(String(10))
    agencia = Column(String(10))
    conta = Column(String(20))
    tipo_conta = Column(String(20))  # corrente, poupanca
    percentual = Column(Float)  # Se tipo for percentual
    valor_fixo = Column(Float)  # Se tipo for fixo
    ordem_prioridade = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    gateway_recipient_id = Column(String(100))  # ID no gateway (Stripe, Pagar.me, etc)
    meta_data = Column(Text)  # JSON com dados adicionais
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class SplitTransaction(Base):
    __tablename__ = "split_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transacao_principal_id = Column(Integer, ForeignKey("transacoes.id"))
    split_config_id = Column(Integer, ForeignKey("split_configurations.id"))
    venda_pdv_id = Column(Integer, ForeignKey("vendas_pdv.id"), nullable=True)
    valor_total = Column(Float, nullable=False)
    valor_liquido = Column(Float, nullable=False)  # Após taxas
    taxa_total = Column(Float, default=0.0)
    status = Column(String(30))  # pendente, processando, concluido, erro, cancelado
    gateway_transaction_id = Column(String(100))
    processado_em = Column(DateTime(timezone=True))
    erro_detalhes = Column(Text)
    meta_data = Column(Text)  # JSON com dados do processamento
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class SplitParcela(Base):
    __tablename__ = "split_parcelas"
    
    id = Column(Integer, primary_key=True, index=True)
    split_transaction_id = Column(Integer, ForeignKey("split_transactions.id"))
    recipient_id = Column(Integer, ForeignKey("split_recipients.id"))
    valor_bruto = Column(Float, nullable=False)
    valor_liquido = Column(Float, nullable=False)
    percentual_aplicado = Column(Float)
    taxa_aplicada = Column(Float, default=0.0)
    status = Column(String(30))  # pendente, processado, transferido, erro
    gateway_split_id = Column(String(100))
    data_transferencia = Column(DateTime(timezone=True))
    comprovante_transferencia = Column(String(255))
    erro_detalhes = Column(Text)
    tentativas_processamento = Column(Integer, default=0)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class SplitEscrow(Base):
    __tablename__ = "split_escrow"
    
    id = Column(Integer, primary_key=True, index=True)
    split_transaction_id = Column(Integer, ForeignKey("split_transactions.id"))
    recipient_id = Column(Integer, ForeignKey("split_recipients.id"))
    valor_retido = Column(Float, nullable=False)
    motivo_retencao = Column(String(50))  # garantia, disputa, analise, manual
    data_retencao = Column(DateTime(timezone=True), default=datetime.now)
    data_liberacao_prevista = Column(DateTime(timezone=True))
    data_liberacao_efetiva = Column(DateTime(timezone=True))
    status = Column(String(30))  # retido, liberado, perdido, devolvido
    observacoes = Column(Text)
    liberado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class SplitDisputa(Base):
    __tablename__ = "split_disputas"
    
    id = Column(Integer, primary_key=True, index=True)
    split_transaction_id = Column(Integer, ForeignKey("split_transactions.id"))
    tipo_disputa = Column(String(50))  # chargeback, contestacao, erro_split, fraude
    valor_disputado = Column(Float, nullable=False)
    data_inicio = Column(DateTime(timezone=True), default=datetime.now)
    data_resolucao = Column(DateTime(timezone=True))
    status = Column(String(30))  # aberta, em_analise, resolvida_favoravel, resolvida_desfavoravel
    descricao = Column(Text)
    evidencias = Column(Text)  # JSON com evidências
    decisao = Column(Text)
    impacto_recipients = Column(Text)  # JSON com impacto em cada recipient
    gateway_dispute_id = Column(String(100))
    resolvido_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class SplitAuditoria(Base):
    __tablename__ = "split_auditoria"
    
    id = Column(Integer, primary_key=True, index=True)
    split_transaction_id = Column(Integer, ForeignKey("split_transactions.id"))
    acao = Column(String(50), nullable=False)  # criacao, processamento, transferencia, erro, cancelamento
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    dados_anteriores = Column(Text)  # JSON com estado anterior
    dados_posteriores = Column(Text)  # JSON com estado posterior
    ip_origem = Column(String(45))
    user_agent = Column(String(255))
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

class SplitReconciliacao(Base):
    __tablename__ = "split_reconciliacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    data_reconciliacao = Column(Date, nullable=False)
    total_transacoes = Column(Integer, default=0)
    valor_total_bruto = Column(Float, default=0.0)
    valor_total_liquido = Column(Float, default=0.0)
    total_taxas = Column(Float, default=0.0)
    total_disputes = Column(Integer, default=0)
    valor_disputes = Column(Float, default=0.0)
    total_chargebacks = Column(Integer, default=0)
    valor_chargebacks = Column(Float, default=0.0)
    status = Column(String(30))  # pendente, processando, concluido, com_divergencias
    arquivo_reconciliacao = Column(String(255))
    divergencias = Column(Text)  # JSON com divergências encontradas
    processado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class SplitRelatorio(Base):
    __tablename__ = "split_relatorios"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_relatorio = Column(String(50), nullable=False)  # financeiro, operacional, compliance
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    filtros = Column(Text)  # JSON com filtros aplicados
    dados_relatorio = Column(Text)  # JSON com dados do relatório
    arquivo_gerado = Column(String(255))
    formato = Column(String(10))  # pdf, xlsx, csv
    status = Column(String(30))  # gerando, concluido, erro
    solicitado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    finalizado_em = Column(DateTime(timezone=True))

# ====== SISTEMA DE CREDENCIAMENTO AVANÇADO ======

class TipoCredencial(Base):
    __tablename__ = "tipos_credencial"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(50))  # participante, staff, vip, imprensa, fornecedor
    cor_identificacao = Column(String(7))  # Hex color
    icone = Column(String(50))
    template_design = Column(Text)  # JSON com template do design
    permissoes_acesso = Column(Text)  # JSON com áreas/recursos permitidos
    validade_padrao_dias = Column(Integer, default=1)
    permite_reimpressao = Column(Boolean, default=True)
    requer_aprovacao = Column(Boolean, default=False)
    limite_emissao = Column(Integer)  # null = ilimitado
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class CredencialEmitida(Base):
    __tablename__ = "credenciais_emitidas"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_credencial = Column(String(50), unique=True, nullable=False)
    tipo_credencial_id = Column(Integer, ForeignKey("tipos_credencial.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    cliente_evento_id = Column(Integer, ForeignKey("clientes_eventos.id"), nullable=True)
    nome_portador = Column(String(200), nullable=False)
    documento_portador = Column(String(20))
    email_portador = Column(String(255))
    telefone_portador = Column(String(20))
    empresa_portador = Column(String(200))
    cargo_portador = Column(String(100))
    foto_portador = Column(String(255))  # URL da foto
    qr_code_data = Column(Text)  # Dados para gerar QR Code
    data_emissao = Column(DateTime(timezone=True), default=datetime.now)
    data_validade = Column(DateTime(timezone=True))
    status = Column(String(30))  # ativa, suspensa, revogada, expirada
    motivo_status = Column(Text)
    total_impressoes = Column(Integer, default=0)
    ultimo_acesso = Column(DateTime(timezone=True))
    metadata_acesso = Column(Text)  # JSON com dados de acesso
    observacoes = Column(Text)
    emitida_por_id = Column(Integer, ForeignKey("usuarios.id"))
    aprovada_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)

class LogAcessoCredencial(Base):
    __tablename__ = "logs_acesso_credencial"
    
    id = Column(Integer, primary_key=True, index=True)
    credencial_id = Column(Integer, ForeignKey("credenciais_emitidas.id"))
    tipo_acesso = Column(String(30))  # entrada, saida, tentativa_negada
    local_acesso = Column(String(100))  # Nome do local/porta
    equipamento_id = Column(String(100))  # ID do equipamento de leitura
    ip_equipamento = Column(String(45))
    sucesso = Column(Boolean, default=True)
    motivo_negacao = Column(String(100))
    dados_biometricos = Column(Text)  # JSON se aplicável
    temperatura_corporal = Column(Float)  # Se equipamento suportar
    foto_acesso = Column(String(255))  # URL da foto capturada
    latitude = Column(Float)
    longitude = Column(Float)
    criado_em = Column(DateTime(timezone=True), default=datetime.now)

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

# ====== SISTEMA DE IMPRESSORAS ======

class TipoImpressora(enum.Enum):
    """Tipos de impressoras suportadas"""
    TERMICA = "termica"
    FISCAL = "fiscal"
    ETIQUETA = "etiqueta"
    MATRICIAL = "matricial"
    LASER = "laser"
    POS = "pos"

class StatusImpressora(enum.Enum):
    """Status da impressora"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERRO = "erro"
    MANUTENCAO = "manutencao"
    PAUSADA = "pausada"

class ModeloImpressora(enum.Enum):
    """Modelos homologados de impressoras"""
    EPSON_TM_T20 = "Epson TM-T20"
    EPSON_TM_T20X = "Epson TM-T20x"
    BEMATECH_4200 = "Bematech MP-4200"
    ELGIN_I8 = "Elgin i8"
    ELGIN_I9 = "Elgin i9"
    GENERICA = "Genérica"

# Nota: A tabela 'impressoras' já existe com estrutura diferente
# Usaremos a estrutura existente para compatibilidade

class ImpressoraInteligente(Base):
    """Sistema de roteamento inteligente de impressão"""
    __tablename__ = "impressoras_inteligentes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)  # Nome do roteamento
    impressora_id = Column(String(36), nullable=False)  # FK para impressoras.id (VARCHAR)
    tipo_impressao = Column(String(50), nullable=False)  # Ex: "pedidos", "cupom_fiscal", "comanda"
    
    # Regras de roteamento
    local_origem = Column(String(100))  # Ex: "Bar", "Balcão", "Mesas"
    categoria_produto = Column(String(100))  # Ex: "Bebidas", "Pratos", "Sobremesas"
    prioridade = Column(Integer, default=0)  # Maior número = maior prioridade
    
    # Configurações
    ativo = Column(Boolean, default=True)
    imprimir_logo = Column(Boolean, default=False)
    numero_vias = Column(Integer, default=1)
    template_id = Column(Integer, ForeignKey("templates_impressao.id"))
    
    # Horário de funcionamento
    hora_inicio = Column(String(5))  # Ex: "08:00"
    hora_fim = Column(String(5))  # Ex: "22:00"
    dias_semana = Column(String(20))  # Ex: "seg,ter,qua,qui,sex"
    
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    template = relationship("TemplateImpressao")
    evento = relationship("Evento")

class TemplateImpressao(Base):
    """Templates customizáveis para impressão"""
    __tablename__ = "templates_impressao"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # Ex: "cupom", "comanda", "pedido", "relatorio"
    
    # Configurações do template
    cabecalho = Column(Text)
    corpo = Column(Text)  # Pode conter variáveis como {{nome_produto}}, {{valor}}, etc.
    rodape = Column(Text)
    
    # Formatação
    fonte_tamanho = Column(String(10))  # Ex: "normal", "condensado", "expandido"
    negrito_titulo = Column(Boolean, default=True)
    centralizar_logo = Column(Boolean, default=True)
    separadores = Column(Boolean, default=True)
    
    # QR Code e Código de Barras
    incluir_qrcode = Column(Boolean, default=False)
    qrcode_conteudo = Column(String(500))  # Template do conteúdo do QR Code
    incluir_codigo_barras = Column(Boolean, default=False)
    codigo_barras_tipo = Column(String(20))  # Ex: "EAN13", "CODE128"
    
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    evento = relationship("Evento")

class FilaImpressao(Base):
    """Fila de jobs de impressão"""
    __tablename__ = "filas_impressao"
    
    id = Column(Integer, primary_key=True, index=True)
    impressora_id = Column(String(36), nullable=False)  # FK para impressoras.id (VARCHAR)
    tipo_documento = Column(String(50))  # Ex: "cupom", "pedido", "relatorio"
    conteudo = Column(Text, nullable=False)  # Conteúdo a ser impresso
    prioridade = Column(Integer, default=0)  # Jobs com maior prioridade são impressos primeiro
    
    # Status do job
    status = Column(String(20), default="pendente")  # pendente, processando, concluido, erro, cancelado
    tentativas = Column(Integer, default=0)
    max_tentativas = Column(Integer, default=3)
    
    # Referências
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"))
    venda_id = Column(Integer, ForeignKey("vendas.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    processado_em = Column(DateTime(timezone=True))
    erro_mensagem = Column(Text)
    
    # Relacionamentos
    # pedido = relationship("PedidoKDS")  # COMENTADO: PedidoKDS não existe ainda
    # venda = relationship("Venda")  # COMENTADO: Venda não existe, usar VendaPDV
    usuario = relationship("Usuario")

class LogImpressao(Base):
    """Logs detalhados de todas as impressões"""
    __tablename__ = "logs_impressao"
    
    id = Column(Integer, primary_key=True, index=True)
    impressora_id = Column(String(36), nullable=False)  # FK para impressoras.id (VARCHAR)
    fila_impressao_id = Column(Integer, ForeignKey("filas_impressao.id"))
    
    # Informações do documento
    tipo_documento = Column(String(50))
    tamanho_bytes = Column(Integer)
    numero_linhas = Column(Integer)
    tempo_processamento = Column(Float)  # Em segundos
    
    # Status
    sucesso = Column(Boolean, default=True)
    mensagem_erro = Column(Text)
    codigo_erro = Column(String(50))
    
    # Metadados
    ip_origem = Column(String(45))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario")
    evento = relationship("Evento")

class EquipamentoPDV(Base):
    """Equipamentos PDV (POS, Totem, Tablet, etc.)"""
    __tablename__ = "equipamentos_pdv"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)  # Ex: "MP01608", "PAG14021"
    tipo = Column(String(20), nullable=False)  # POS, Totem, Tablet, Terminal
    nome = Column(String(100))
    
    # Configuração
    perfil_venda = Column(String(50))  # Perfil de venda associado
    impressora_padrao_id = Column(String(36))  # FK para impressoras.id (VARCHAR)
    operador_id = Column(Integer, ForeignKey("operadores_pdv.id"))
    
    # Status e licenciamento
    licenciado = Column(Boolean, default=False)
    data_licenca_inicio = Column(Date)
    data_licenca_fim = Column(Date)
    status = Column(String(20), default="inativo")  # ativo, inativo, manutencao
    
    # Localização
    localizacao = Column(String(100))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Metadados
    ultima_sincronizacao = Column(DateTime(timezone=True))
    versao_software = Column(String(20))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    operador = relationship("OperadorPDV", back_populates="equipamentos")
    evento = relationship("Evento")
    empresa = relationship("Empresa")

class OperadorPDV(Base):
    """Operadores do sistema PDV"""
    __tablename__ = "operadores_pdv"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True)
    codigo_acesso = Column(String(20))  # PIN ou código de acesso
    
    # Comissionamento
    comissao_percentual = Column(Numeric(5, 2), default=0)  # Ex: 10.00 para 10%
    comissao_fixa = Column(Numeric(10, 2), default=0)  # Valor fixo por venda
    
    # Permissões
    pode_cancelar = Column(Boolean, default=False)
    pode_dar_desconto = Column(Boolean, default=False)
    desconto_maximo = Column(Numeric(5, 2), default=0)  # Percentual máximo de desconto
    
    # Status
    ativo = Column(Boolean, default=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Estatísticas
    total_vendas = Column(Integer, default=0)
    valor_total_vendido = Column(Numeric(10, 2), default=0)
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    equipamentos = relationship("EquipamentoPDV", back_populates="operador")

class LeitorQRCode(Base):
    """Leitores QR Code e equipamentos de captura"""
    __tablename__ = "leitores_qrcode"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_equipamento = Column(String(20), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    
    # Tipo e configuração
    tipo_leitor = Column(String(50))  # fixo, mobile, totem, handheld, camera
    marca = Column(String(50))  # Zebra, Honeywell, Datalogic, etc.
    modelo = Column(String(50))
    numero_serie = Column(String(100))
    
    # Conectividade
    tipo_conexao = Column(String(50))  # usb, bluetooth, wifi, ethernet, serial
    endereco_ip = Column(String(45))  # Para leitores em rede
    porta_comunicacao = Column(Integer)  # Porta TCP/UDP
    endereco_mac = Column(String(17))  # Endereço MAC para Bluetooth/WiFi
    
    # Configurações de leitura
    sensibilidade = Column(Integer, default=3)  # 1-5 (baixa-alta)
    timeout_leitura = Column(Integer, default=5000)  # Em milissegundos
    formato_suportado = Column(String(200))  # QR, DataMatrix, PDF417, Code128, etc.
    modo_operacao = Column(String(20), default="continuo")  # continuo, trigger, auto
    
    # Calibração e qualidade
    resolucao_minima = Column(Integer, default=640)  # Pixels
    qualidade_imagem = Column(Integer, default=80)  # 1-100
    zoom_automatico = Column(Boolean, default=True)
    foco_automatico = Column(Boolean, default=True)
    compensacao_luz = Column(Boolean, default=True)
    
    # Status operacional
    status = Column(String(20), default="inativo")  # ativo, inativo, manutencao, erro
    ultimo_heartbeat = Column(DateTime(timezone=True))
    versao_firmware = Column(String(20))
    temperatura_operacao = Column(Float)  # Celsius
    nivel_bateria = Column(Integer)  # 0-100% para equipamentos móveis
    
    # Localização e evento
    localizacao = Column(String(100))  # Descrição da localização física
    ponto_acesso_id = Column(Integer, ForeignKey("pontos_acesso.id"))  # FK para ponto de acesso
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Estatísticas
    total_leituras = Column(Integer, default=0)
    leituras_sucesso = Column(Integer, default=0)
    leituras_erro = Column(Integer, default=0)
    tempo_medio_leitura = Column(Float, default=0)  # Em milissegundos
    
    # Configurações avançadas
    filtro_duplicatas = Column(Boolean, default=True)  # Evita leituras duplicadas
    tempo_filtro_duplicata = Column(Integer, default=3000)  # Em milissegundos
    validacao_formato = Column(Boolean, default=True)
    log_detalhado = Column(Boolean, default=False)
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    ponto_acesso = relationship("PontoAcesso", back_populates="leitores")
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    criador = relationship("Usuario", foreign_keys=[criado_por])
    leituras = relationship("HistoricoLeituraQR", back_populates="leitor")

class PontoAcesso(Base):
    """Pontos de acesso/entrada para eventos"""
    __tablename__ = "pontos_acesso"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    
    # Tipo e configuração
    tipo_ponto = Column(String(50))  # entrada, saida, bidirecional, vip, staff
    descricao = Column(Text)
    capacidade_maxima = Column(Integer)  # Pessoas simultâneas
    
    # Localização física
    localizacao_descricao = Column(String(200))
    coordenadas_gps = Column(String(50))  # lat,lng
    andar = Column(String(10))
    setor = Column(String(50))
    
    # Configurações operacionais
    ativo = Column(Boolean, default=True)
    requer_validacao = Column(Boolean, default=True)
    permite_reentrada = Column(Boolean, default=False)
    horario_abertura = Column(Time)
    horario_fechamento = Column(Time)
    
    # Controle de fluxo
    contagem_atual = Column(Integer, default=0)  # Pessoas no local atualmente
    total_entradas = Column(Integer, default=0)
    total_saidas = Column(Integer, default=0)
    
    # Configurações de segurança
    nivel_seguranca = Column(String(20), default="normal")  # baixo, normal, alto, critico
    log_todas_tentativas = Column(Boolean, default=True)
    alerta_capacidade = Column(Boolean, default=True)
    percentual_alerta = Column(Integer, default=90)  # % da capacidade para alerta
    
    # Relacionamento com evento
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento")
    empresa = relationship("Empresa")
    leitores = relationship("LeitorQRCode", back_populates="ponto_acesso")
    movimentacoes = relationship("MovimentacaoAcesso", back_populates="ponto_acesso")

class HistoricoLeituraQR(Base):
    """Histórico de todas as leituras de QR Code"""
    __tablename__ = "historico_leitura_qr"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Dados da leitura
    codigo_lido = Column(Text, nullable=False)  # Conteúdo do QR Code lido
    codigo_decodificado = Column(Text)  # Versão processada/limpa do código
    formato_codigo = Column(String(50))  # QR, DataMatrix, etc.
    qualidade_leitura = Column(Integer)  # 1-100
    
    # Resultado da validação
    valido = Column(Boolean, default=False)
    tipo_validacao = Column(String(50))  # ingresso, credencial, produto, etc.
    resultado_validacao = Column(String(20))  # aprovado, negado, pendente, erro
    motivo_rejeicao = Column(String(200))  # Motivo se rejeitado
    
    # Contexto da leitura
    leitor_id = Column(Integer, ForeignKey("leitores_qrcode.id"), nullable=False)
    ponto_acesso_id = Column(Integer, ForeignKey("pontos_acesso.id"))
    operador_id = Column(Integer, ForeignKey("usuarios.id"))  # Quem estava operando
    
    # Dados do participante (se identificado)
    participante_cpf = Column(String(14))
    participante_nome = Column(String(100))
    participante_tipo = Column(String(50))  # vip, staff, convidado, etc.
    
    # Dados do ingresso/credencial (se aplicável)
    ingresso_id = Column(Integer)  # Referência ao ingresso
    credencial_id = Column(Integer)  # Referência à credencial
    lista_id = Column(Integer)  # Referência à lista (se convidado)
    
    # Metadados técnicos
    tempo_leitura = Column(Integer)  # Tempo em milissegundos
    tentativas = Column(Integer, default=1)  # Quantas tentativas foram necessárias
    posicao_qr_imagem = Column(String(50))  # Posição do QR na imagem (se detectado)
    
    # Informações do dispositivo
    endereco_ip = Column(String(45))
    user_agent = Column(String(500))  # Para leituras web
    sessao_id = Column(String(100))
    
    # Dados de geolocalização
    latitude = Column(Float)
    longitude = Column(Float)
    precisao_localizacao = Column(Float)  # Em metros
    
    # Auditoria e rastreabilidade
    timestamp_leitura = Column(DateTime(timezone=True), server_default=func.now())
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Relacionamentos
    leitor = relationship("LeitorQRCode", back_populates="leituras")
    ponto_acesso = relationship("PontoAcesso", back_populates="movimentacoes")
    operador = relationship("Usuario")
    evento = relationship("Evento")
    empresa = relationship("Empresa")

class MovimentacaoAcesso(Base):
    """Movimentações de entrada/saída em pontos de acesso"""
    __tablename__ = "movimentacoes_acesso"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Dados da movimentação
    tipo_movimento = Column(String(20), nullable=False)  # entrada, saida
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    
    # Participante
    cpf_participante = Column(String(14), nullable=False)
    nome_participante = Column(String(100))
    tipo_participante = Column(String(50))  # vip, staff, convidado, pagante, etc.
    
    # Contexto
    ponto_acesso_id = Column(Integer, ForeignKey("pontos_acesso.id"), nullable=False)
    leitura_qr_id = Column(Integer, ForeignKey("historico_leitura_qr.id"))  # Leitura que gerou a movimentação
    
    # Dados do acesso
    credencial_utilizada = Column(String(50))  # tipo de credencial usada
    primeira_entrada = Column(Boolean, default=False)  # Se é a primeira vez no evento
    tempo_permanencia = Column(Integer)  # Em minutos (para saídas)
    
    # Validação e segurança
    validacao_adicional = Column(String(100))  # Validações extras realizadas
    nivel_confianca = Column(Integer, default=100)  # 0-100
    sinalizadores = Column(Text)  # JSON com flags especiais
    
    # Auditoria
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Relacionamentos
    ponto_acesso = relationship("PontoAcesso", back_populates="movimentacoes")
    leitura_origem = relationship("HistoricoLeituraQR")
    evento = relationship("Evento")
    empresa = relationship("Empresa")

class ConfiguracaoEquipamento(Base):
    """Configurações específicas por tipo de equipamento"""
    __tablename__ = "configuracoes_equipamento"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação
    tipo_equipamento = Column(String(50), nullable=False)  # leitor_qr, impressora, pdv, etc.
    nome_configuracao = Column(String(100), nullable=False)
    descricao = Column(Text)
    
    # Configuração (JSON flexível)
    parametros_json = Column(Text)  # Configurações específicas em JSON
    template_configuracao = Column(Text)  # Template base para o tipo
    
    # Aplicabilidade
    marca_equipamento = Column(String(50))  # Para qual marca se aplica
    modelo_equipamento = Column(String(50))  # Para qual modelo se aplica
    versao_firmware_min = Column(String(20))  # Versão mínima do firmware
    versao_firmware_max = Column(String(20))  # Versão máxima do firmware
    
    # Status
    ativo = Column(Boolean, default=True)
    configuracao_padrao = Column(Boolean, default=False)  # Se é a config padrão do tipo
    
    # Versionamento
    versao = Column(String(10), default="1.0")
    configuracao_pai_id = Column(Integer, ForeignKey("configuracoes_equipamento.id"))  # Para herança
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    
    # Relacionamentos
    configuracao_pai = relationship("ConfiguracaoEquipamento", remote_side=[id])
    criador = relationship("Usuario", foreign_keys=[criado_por])
    evento = relationship("Evento")
    empresa = relationship("Empresa")

# ==================== MODELOS CRM E MARKETING ====================

class LeadCRM(Base):
    """Leads e prospects no sistema CRM"""
    __tablename__ = "leads_crm"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Dados pessoais
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    telefone = Column(String(20))
    cpf = Column(String(14))
    empresa = Column(String(100))
    cargo = Column(String(100))
    
    # Origem do lead
    origem = Column(String(50))  # site, evento, indicacao, campanha, etc.
    campanha_origem = Column(String(100))  # ID/nome da campanha que gerou o lead
    evento_origem_id = Column(Integer, ForeignKey("eventos.id"))  # Evento que gerou o lead
    
    # Score e classificação
    score_lead = Column(Integer, default=0)  # 0-100
    temperatura = Column(String(20), default="frio")  # frio, morno, quente
    estagio_funil = Column(String(50), default="lead")  # lead, mql, sql, oportunidade, cliente
    probabilidade_conversao = Column(Integer, default=0)  # 0-100%
    
    # Informações do negócio
    valor_potencial = Column(Numeric(10, 2), default=0)
    tipo_evento_interesse = Column(String(100))  # Tipo de evento que tem interesse
    orcamento_estimado = Column(Numeric(10, 2))
    data_evento_desejada = Column(Date)
    numero_participantes_estimado = Column(Integer)
    
    # Status e acompanhamento
    status = Column(String(20), default="novo")  # novo, contatado, qualificado, perdido, convertido
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    data_ultimo_contato = Column(DateTime(timezone=True))
    proximo_followup = Column(DateTime(timezone=True))
    
    # Dados comportamentais
    total_emails_enviados = Column(Integer, default=0)
    total_emails_abertos = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    paginas_visitadas = Column(Text)  # JSON com páginas visitadas
    eventos_participados = Column(Text)  # JSON com histórico de eventos
    
    # Segmentação
    tags = Column(Text)  # JSON com tags para segmentação
    segmento_mercado = Column(String(50))  # corporativo, educacional, saude, tecnologia, etc.
    porte_empresa = Column(String(20))  # micro, pequena, media, grande
    regiao = Column(String(50))
    
    # Observações e notas
    observacoes = Column(Text)
    motivo_perda = Column(String(200))  # Se status = perdido
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    evento_origem = relationship("Evento", foreign_keys=[evento_origem_id])
    responsavel = relationship("Usuario", foreign_keys=[responsavel_id])
    criador = relationship("Usuario", foreign_keys=[criado_por])
    atividades = relationship("AtividadeCRM", back_populates="lead")
    campanhas_relacionadas = relationship("LeadCampanha", back_populates="lead")

class CampanhaCRM(Base):
    """Campanhas de marketing e comunicação"""
    __tablename__ = "campanhas_crm"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo_campanha = Column(String(50))  # email, whatsapp, sms, social, evento
    status = Column(String(20), default="rascunho")  # rascunho, ativa, pausada, finalizada
    
    # Configurações da campanha
    data_inicio = Column(DateTime(timezone=True))
    data_fim = Column(DateTime(timezone=True))
    fuso_horario = Column(String(50), default="America/Sao_Paulo")
    
    # Conteúdo
    assunto = Column(String(200))  # Para emails
    conteudo_html = Column(Text)  # Template HTML
    conteudo_texto = Column(Text)  # Versão texto simples
    anexos = Column(Text)  # JSON com lista de anexos
    
    # Segmentação e público-alvo
    publico_alvo = Column(Text)  # JSON com critérios de segmentação
    total_destinatarios = Column(Integer, default=0)
    filtros_aplicados = Column(Text)  # JSON com filtros usados
    
    # Configurações de envio
    remetente_nome = Column(String(100))
    remetente_email = Column(String(100))
    envio_programado = Column(Boolean, default=False)
    frequencia_envio = Column(String(50))  # unico, diario, semanal, mensal
    
    # Métricas e resultados
    total_enviados = Column(Integer, default=0)
    total_entregues = Column(Integer, default=0)
    total_abertos = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    total_conversoes = Column(Integer, default=0)
    total_descadastros = Column(Integer, default=0)
    total_bounces = Column(Integer, default=0)
    total_spam = Column(Integer, default=0)
    
    # Custos e ROI
    custo_campanha = Column(Numeric(10, 2), default=0)
    receita_gerada = Column(Numeric(10, 2), default=0)
    roi_calculado = Column(Numeric(5, 2), default=0)
    
    # A/B Testing
    teste_ab_ativo = Column(Boolean, default=False)
    variante_a_assunto = Column(String(200))
    variante_b_assunto = Column(String(200))
    percentual_teste = Column(Integer, default=10)  # % do público para teste
    
    # Integração e automação
    trigger_evento = Column(String(100))  # Evento que dispara a campanha
    fluxo_automacao_id = Column(Integer, ForeignKey("fluxos_automacao.id"))
    webhook_callback = Column(String(500))
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    criador = relationship("Usuario")
    fluxo_automacao = relationship("FluxoAutomacao", back_populates="campanhas")
    envios = relationship("EnvioCampanha", back_populates="campanha")
    leads_relacionados = relationship("LeadCampanha", back_populates="campanha")

class EnvioCampanha(Base):
    """Registro de envios individuais de campanha"""
    __tablename__ = "envios_campanha"
    
    id = Column(Integer, primary_key=True, index=True)
    
    campanha_id = Column(Integer, ForeignKey("campanhas_crm.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads_crm.id"))
    
    # Dados do envio
    destinatario_nome = Column(String(100))
    destinatario_email = Column(String(100))
    destinatario_telefone = Column(String(20))
    
    # Status do envio
    status_envio = Column(String(20), default="pendente")  # pendente, enviado, entregue, falha
    data_envio = Column(DateTime(timezone=True))
    data_entrega = Column(DateTime(timezone=True))
    mensagem_erro = Column(String(500))
    
    # Engagement
    aberto = Column(Boolean, default=False)
    data_abertura = Column(DateTime(timezone=True))
    total_aberturas = Column(Integer, default=0)
    
    clicou = Column(Boolean, default=False)
    data_primeiro_click = Column(DateTime(timezone=True))
    total_clicks = Column(Integer, default=0)
    urls_clicadas = Column(Text)  # JSON
    
    respondeu = Column(Boolean, default=False)
    data_resposta = Column(DateTime(timezone=True))
    
    converteu = Column(Boolean, default=False)
    data_conversao = Column(DateTime(timezone=True))
    valor_conversao = Column(Numeric(10, 2))
    
    # Dados técnicos
    user_agent = Column(String(500))
    ip_endereco = Column(String(45))
    dispositivo = Column(String(50))
    localizacao = Column(String(100))
    
    # Relacionamentos
    campanha = relationship("CampanhaCRM", back_populates="envios")
    lead = relationship("LeadCRM")

class AtividadeCRM(Base):
    """Atividades e interações com leads"""
    __tablename__ = "atividades_crm"
    
    id = Column(Integer, primary_key=True, index=True)
    
    lead_id = Column(Integer, ForeignKey("leads_crm.id"), nullable=False)
    
    # Tipo e detalhes da atividade
    tipo_atividade = Column(String(50), nullable=False)  # email, call, meeting, note, task
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    resultado = Column(String(100))  # interessado, não interessado, agendar, etc.
    
    # Agendamento
    data_agendada = Column(DateTime(timezone=True))
    data_realizada = Column(DateTime(timezone=True))
    duracao_minutos = Column(Integer)
    
    # Status
    status = Column(String(20), default="pendente")  # pendente, concluida, cancelada
    prioridade = Column(String(20), default="media")  # baixa, media, alta, critica
    
    # Participantes
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    participantes = Column(Text)  # JSON com lista de participantes
    
    # Resultado da atividade
    pontuacao_lead = Column(Integer)  # Pontos adicionados/removidos do lead
    proximo_passo = Column(String(200))
    data_proximo_followup = Column(DateTime(timezone=True))
    
    # Anexos e referências
    anexos = Column(Text)  # JSON
    campanha_relacionada_id = Column(Integer, ForeignKey("campanhas_crm.id"))
    evento_relacionado_id = Column(Integer, ForeignKey("eventos.id"))
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    lead = relationship("LeadCRM", back_populates="atividades")
    responsavel = relationship("Usuario", foreign_keys=[responsavel_id])
    criador = relationship("Usuario", foreign_keys=[criado_por])
    campanha_relacionada = relationship("CampanhaCRM")
    evento_relacionado = relationship("Evento")

class FluxoAutomacao(Base):
    """Fluxos de automação de marketing"""
    __tablename__ = "fluxos_automacao"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Configurações básicas
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=False)
    
    # Trigger do fluxo
    trigger_tipo = Column(String(50), nullable=False)  # evento, data, acao, score
    trigger_configuracao = Column(Text)  # JSON com configuração do trigger
    
    # Configurações do fluxo
    etapas_fluxo = Column(Text)  # JSON com definição das etapas
    condicoes_saida = Column(Text)  # JSON com condições para sair do fluxo
    limite_execucoes = Column(Integer)  # Limite de vezes que pode executar por lead
    
    # Métricas
    total_leads_entraram = Column(Integer, default=0)
    total_leads_completaram = Column(Integer, default=0)
    total_leads_sairam = Column(Integer, default=0)
    taxa_conversao = Column(Numeric(5, 2), default=0)
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    criador = relationship("Usuario")
    campanhas = relationship("CampanhaCRM", back_populates="fluxo_automacao")
    execucoes = relationship("ExecucaoFluxoAutomacao", back_populates="fluxo")

class ExecucaoFluxoAutomacao(Base):
    """Execuções individuais de fluxos de automação"""
    __tablename__ = "execucoes_fluxo_automacao"
    
    id = Column(Integer, primary_key=True, index=True)
    
    fluxo_id = Column(Integer, ForeignKey("fluxos_automacao.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads_crm.id"), nullable=False)
    
    # Estado da execução
    status = Column(String(20), default="ativa")  # ativa, pausada, concluida, cancelada
    etapa_atual = Column(Integer, default=1)
    data_inicio = Column(DateTime(timezone=True), server_default=func.now())
    data_fim = Column(DateTime(timezone=True))
    
    # Dados da execução
    etapas_completadas = Column(Text)  # JSON com histórico das etapas
    variaveis_contexto = Column(Text)  # JSON com variáveis do contexto
    
    # Relacionamentos
    fluxo = relationship("FluxoAutomacao", back_populates="execucoes")
    lead = relationship("LeadCRM")

class SegmentoCRM(Base):
    """Segmentos de leads para campanhas direcionadas"""
    __tablename__ = "segmentos_crm"
    
    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    
    # Critérios de segmentação
    criterios_filtro = Column(Text)  # JSON com critérios de filtro
    query_sql = Column(Text)  # Query SQL para filtros avançados
    
    # Configurações
    dinamico = Column(Boolean, default=True)  # Se atualiza automaticamente
    data_ultima_atualizacao = Column(DateTime(timezone=True))
    total_leads = Column(Integer, default=0)
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    criador = relationship("Usuario")

class LeadCampanha(Base):
    """Relacionamento entre leads e campanhas"""
    __tablename__ = "leads_campanhas"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads_crm.id"))
    campanha_id = Column(Integer, ForeignKey("campanhas_crm.id"))
    
    # Dados da relação
    adicionado_em = Column(DateTime(timezone=True), server_default=func.now())
    origem_adicao = Column(String(50))  # manual, automatica, segmento
    
    # Relacionamentos
    lead = relationship("LeadCRM", back_populates="campanhas_relacionadas")
    campanha = relationship("CampanhaCRM", back_populates="leads_relacionados")

class TemplateComunicacao(Base):
    """Templates para emails, WhatsApp, SMS"""
    __tablename__ = "templates_comunicacao"
    
    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)  # email, whatsapp, sms
    categoria = Column(String(50))  # boas-vindas, followup, promocional, transacional
    
    # Conteúdo
    assunto = Column(String(200))  # Para emails
    conteudo_html = Column(Text)
    conteudo_texto = Column(Text)
    variaveis_disponiveis = Column(Text)  # JSON com variáveis que podem ser usadas
    
    # Configurações
    ativo = Column(Boolean, default=True)
    publico = Column(Boolean, default=False)  # Se outros usuários podem usar
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    criador = relationship("Usuario")



# ==================== IMPORTAR MODELOS MEEP COMPLETOS ====================
# Import all additional MEEP models to make them available through main models module
from .models_meep_complete import *


# ==================== IMPORTAR MODELOS MEEP COMPLETOS ====================
# Import all additional MEEP models to make them available through main models module
from .models_meep_complete import *
