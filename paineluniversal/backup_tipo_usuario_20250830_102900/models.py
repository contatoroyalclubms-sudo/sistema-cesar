from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

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
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    telefone = Column(String(20))
    endereco = Column(Text)
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
        tipo_usuario = Column(String(20))  # Campo legado - será removido
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
    tipo_usuario=Column(Enum(TipoLista), nullable=False)
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
    tipo_usuario=Column(Enum(TipoProduto), nullable=False)
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
    tipo_usuario=Column(Enum(TipoComanda), nullable=False)
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
    tipo_usuario=Column(Enum(TipoFormaPagamento), nullable=False)
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
    tipo_usuario=Column(Enum(TipoMovimentacaoFinanceira), nullable=False)
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
    tipo_usuario=Column(Enum(TipoConquista), nullable=False)
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
    tipo_usuario=Column(String(100), nullable=False)  # 'tablet', 'qr_reader', 'printer', 'pos'
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
