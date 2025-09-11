"""
Modelos para Sistema de Inventário/ERP
Implementação completa baseada na análise da engenharia reversa MEEP
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from decimal import Decimal

from .models import Base, Usuario, Produto, Empresa, Evento

# ================================================================================
# ENUMS PARA SISTEMA DE INVENTÁRIO
# ================================================================================

class TipoMovimentacaoEstoque(enum.Enum):
    ENTRADA_COMPRA = "entrada_compra"
    ENTRADA_DEVOLUCAO = "entrada_devolucao"
    ENTRADA_AJUSTE = "entrada_ajuste"
    ENTRADA_TRANSFERENCIA = "entrada_transferencia"
    ENTRADA_INVENTARIO = "entrada_inventario"
    SAIDA_VENDA = "saida_venda"
    SAIDA_PERDA = "saida_perda"
    SAIDA_AJUSTE = "saida_ajuste"
    SAIDA_TRANSFERENCIA = "saida_transferencia"
    SAIDA_INVENTARIO = "saida_inventario"
    SAIDA_DEVOLUCAO = "saida_devolucao"

class StatusOrdemCompra(enum.Enum):
    RASCUNHO = "rascunho"
    PENDENTE = "pendente"
    ENVIADA = "enviada"
    CONFIRMADA = "confirmada"
    RECEBIMENTO_PARCIAL = "recebimento_parcial"
    RECEBIDA = "recebida"
    CANCELADA = "cancelada"
    DEVOLVIDA = "devolvida"

class StatusRecebimento(enum.Enum):
    AGUARDANDO = "aguardando"
    RECEBIMENTO_PARCIAL = "recebimento_parcial"
    RECEBIDO_COMPLETO = "recebido_completo"
    RECEBIDO_DIVERGENCIA = "recebido_divergencia"
    DEVOLVIDO = "devolvido"

class MetodoControleEstoque(enum.Enum):
    FIFO = "fifo"  # First In, First Out
    LIFO = "lifo"  # Last In, First Out
    CUSTO_MEDIO = "custo_medio"
    CUSTO_ESPECIFICO = "custo_especifico"

class StatusInventarioFisico(enum.Enum):
    PLANEJADO = "planejado"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADO = "finalizado"
    APROVADO = "aprovado"
    CANCELADO = "cancelado"

class TipoFornecedor(enum.Enum):
    PESSOA_FISICA = "pessoa_fisica"
    PESSOA_JURIDICA = "pessoa_juridica"
    PRODUTOR_RURAL = "produtor_rural"
    COOPERATIVA = "cooperativa"

class StatusFornecedor(enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    BLOQUEADO = "bloqueado"
    SUSPENSO = "suspenso"

# ================================================================================
# MODELOS DE DADOS
# ================================================================================

class Fornecedor(Base):
    __tablename__ = "fornecedores"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Dados principais
    razao_social = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    tipo_fornecedor = Column(Enum(TipoFornecedor), default=TipoFornecedor.PESSOA_JURIDICA)
    status = Column(Enum(StatusFornecedor), default=StatusFornecedor.ATIVO)
    
    # Documentação
    cnpj_cpf = Column(String(18), unique=True, index=True)
    inscricao_estadual = Column(String(20))
    inscricao_municipal = Column(String(20))
    
    # Contato
    endereco = Column(String(200))
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(10))
    telefone = Column(String(20))
    email = Column(String(100))
    contato_principal = Column(String(100))
    
    # Dados comerciais
    prazo_pagamento_padrao = Column(Integer, default=30)  # dias
    desconto_padrao = Column(Numeric(5, 2), default=0)
    limite_credito = Column(Numeric(10, 2))
    banco = Column(String(100))
    agencia = Column(String(10))
    conta = Column(String(20))
    
    # Dados operacionais
    lead_time_medio = Column(Integer, default=7)  # dias
    avaliacao = Column(Integer, default=5)  # 1-5 estrelas
    observacoes = Column(Text)
    
    # Auditoria
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="fornecedores")
    criado_por = relationship("Usuario")
    ordens_compra = relationship("OrdemCompra", back_populates="fornecedor")
    produtos_fornecedor = relationship("ProdutoFornecedor", back_populates="fornecedor")

class LocalEstoque(Base):
    __tablename__ = "locais_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=True)
    
    # Dados principais
    nome = Column(String(100), nullable=False)
    descricao = Column(String(200))
    tipo = Column(String(50), default="deposito")  # deposito, loja, pdv, virtual
    
    # Localização
    endereco = Column(String(200))
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(10))
    
    # Configurações
    eh_principal = Column(Boolean, default=False)
    permite_venda = Column(Boolean, default=True)
    permite_compra = Column(Boolean, default=True)
    capacidade_maxima = Column(Numeric(10, 2))  # m³ ou kg
    responsavel = Column(String(100))
    
    # Auditoria
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    empresa = relationship("Empresa")
    evento = relationship("Evento")
    estoques = relationship("EstoqueProduto", back_populates="local")
    movimentacoes_origem = relationship("MovimentacaoEstoque", foreign_keys="MovimentacaoEstoque.local_origem_id")
    movimentacoes_destino = relationship("MovimentacaoEstoque", foreign_keys="MovimentacaoEstoque.local_destino_id")

class EstoqueProduto(Base):
    __tablename__ = "estoque_produtos"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    local_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=False)
    
    # Quantidades
    quantidade_atual = Column(Numeric(10, 3), default=0)
    quantidade_reservada = Column(Numeric(10, 3), default=0)  # para vendas pendentes
    quantidade_disponivel = Column(Numeric(10, 3), default=0)  # atual - reservada
    
    # Limites e alertas
    estoque_minimo = Column(Numeric(10, 3), default=0)
    estoque_maximo = Column(Numeric(10, 3))
    ponto_pedido = Column(Numeric(10, 3))
    
    # Custos
    custo_medio = Column(Numeric(10, 2), default=0)
    ultimo_custo = Column(Numeric(10, 2), default=0)
    metodo_controle = Column(Enum(MetodoControleEstoque), default=MetodoControleEstoque.CUSTO_MEDIO)
    
    # Dados estatísticos
    giro_estoque = Column(Numeric(5, 2), default=0)  # vezes por mês
    cobertura_dias = Column(Integer, default=0)  # dias de cobertura
    ultima_movimentacao = Column(DateTime)
    ultima_venda = Column(DateTime)
    ultima_compra = Column(DateTime)
    
    # Auditoria
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    produto = relationship("Produto")
    local = relationship("LocalEstoque", back_populates="estoques")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="estoque_produto")

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    estoque_produto_id = Column(Integer, ForeignKey("estoque_produtos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    local_origem_id = Column(Integer, ForeignKey("locais_estoque.id"))
    local_destino_id = Column(Integer, ForeignKey("locais_estoque.id"))
    
    # Dados da movimentação
    tipo_movimentacao = Column(Enum(TipoMovimentacaoEstoque), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False)
    valor_unitario = Column(Numeric(10, 2))
    valor_total = Column(Numeric(12, 2))
    
    # Referências
    ordem_compra_id = Column(Integer, ForeignKey("ordens_compra.id"))
    venda_pdv_id = Column(Integer, ForeignKey("vendas_pdv.id"))
    transferencia_id = Column(Integer, ForeignKey("transferencias_estoque.id"))
    inventario_id = Column(Integer, ForeignKey("inventarios_fisicos.id"))
    
    # Dados complementares
    numero_documento = Column(String(50))  # NF, cupom, etc
    observacoes = Column(Text)
    data_movimento = Column(DateTime, default=datetime.utcnow)
    
    # Saldos após movimentação
    saldo_anterior = Column(Numeric(10, 3))
    saldo_atual = Column(Numeric(10, 3))
    
    # Auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    estoque_produto = relationship("EstoqueProduto", back_populates="movimentacoes")
    produto = relationship("Produto")
    local_origem = relationship("LocalEstoque", foreign_keys=[local_origem_id])
    local_destino = relationship("LocalEstoque", foreign_keys=[local_destino_id])
    ordem_compra = relationship("OrdemCompra")
    criado_por = relationship("Usuario")

class OrdemCompra(Base):
    __tablename__ = "ordens_compra"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    local_entrega_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=False)
    
    # Identificação
    numero = Column(String(20), unique=True, index=True)
    status = Column(Enum(StatusOrdemCompra), default=StatusOrdemCompra.RASCUNHO)
    
    # Datas
    data_emissao = Column(DateTime, default=datetime.utcnow)
    data_entrega_prevista = Column(DateTime)
    data_entrega_realizada = Column(DateTime)
    data_vencimento = Column(DateTime)
    
    # Valores
    valor_produtos = Column(Numeric(12, 2), default=0)
    valor_frete = Column(Numeric(8, 2), default=0)
    valor_desconto = Column(Numeric(8, 2), default=0)
    valor_total = Column(Numeric(12, 2), default=0)
    
    # Condições
    forma_pagamento = Column(String(50))
    prazo_pagamento = Column(Integer)  # dias
    condicoes_especiais = Column(Text)
    observacoes = Column(Text)
    
    # Controle de recebimento
    percentual_recebido = Column(Numeric(5, 2), default=0)
    valor_recebido = Column(Numeric(12, 2), default=0)
    
    # Auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    aprovado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    fornecedor = relationship("Fornecedor", back_populates="ordens_compra")
    local_entrega = relationship("LocalEstoque")
    itens = relationship("ItemOrdemCompra", back_populates="ordem_compra", cascade="all, delete-orphan")
    recebimentos = relationship("RecebimentoMercadoria", back_populates="ordem_compra")
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    aprovado_por = relationship("Usuario", foreign_keys=[aprovado_por_id])

class ItemOrdemCompra(Base):
    __tablename__ = "itens_ordem_compra"
    
    id = Column(Integer, primary_key=True, index=True)
    ordem_compra_id = Column(Integer, ForeignKey("ordens_compra.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    
    # Dados do item
    quantidade_solicitada = Column(Numeric(10, 3), nullable=False)
    quantidade_recebida = Column(Numeric(10, 3), default=0)
    valor_unitario = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(12, 2), nullable=False)
    
    # Dados complementares
    descricao_complementar = Column(String(200))
    observacoes = Column(Text)
    
    # Status
    percentual_recebido = Column(Numeric(5, 2), default=0)
    data_ultimo_recebimento = Column(DateTime)
    
    # Relacionamentos
    ordem_compra = relationship("OrdemCompra", back_populates="itens")
    produto = relationship("Produto")
    recebimentos = relationship("ItemRecebimento", back_populates="item_ordem_compra")

class RecebimentoMercadoria(Base):
    __tablename__ = "recebimentos_mercadoria"
    
    id = Column(Integer, primary_key=True, index=True)
    ordem_compra_id = Column(Integer, ForeignKey("ordens_compra.id"), nullable=False)
    local_estoque_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=False)
    
    # Identificação
    numero_recebimento = Column(String(20), unique=True, index=True)
    numero_nota_fiscal = Column(String(20))
    serie_nota_fiscal = Column(String(5))
    chave_nfe = Column(String(44))
    
    # Dados do recebimento
    data_recebimento = Column(DateTime, default=datetime.utcnow)
    data_nota_fiscal = Column(DateTime)
    status = Column(Enum(StatusRecebimento), default=StatusRecebimento.AGUARDANDO)
    
    # Valores
    valor_produtos = Column(Numeric(12, 2), default=0)
    valor_frete = Column(Numeric(8, 2), default=0)
    valor_total_nota = Column(Numeric(12, 2), default=0)
    
    # Observações
    observacoes = Column(Text)
    motivo_divergencia = Column(Text)
    
    # Auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    recebido_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    ordem_compra = relationship("OrdemCompra", back_populates="recebimentos")
    local_estoque = relationship("LocalEstoque")
    recebido_por = relationship("Usuario")
    itens = relationship("ItemRecebimento", back_populates="recebimento", cascade="all, delete-orphan")

class ItemRecebimento(Base):
    __tablename__ = "itens_recebimento"
    
    id = Column(Integer, primary_key=True, index=True)
    recebimento_id = Column(Integer, ForeignKey("recebimentos_mercadoria.id"), nullable=False)
    item_ordem_compra_id = Column(Integer, ForeignKey("itens_ordem_compra.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    
    # Quantidades
    quantidade_solicitada = Column(Numeric(10, 3), nullable=False)
    quantidade_recebida = Column(Numeric(10, 3), nullable=False)
    quantidade_divergente = Column(Numeric(10, 3), default=0)
    
    # Valores
    valor_unitario_pedido = Column(Numeric(10, 2))
    valor_unitario_recebido = Column(Numeric(10, 2))
    valor_total = Column(Numeric(12, 2))
    
    # Qualidade
    lote = Column(String(50))
    data_fabricacao = Column(DateTime)
    data_vencimento = Column(DateTime)
    observacoes_qualidade = Column(Text)
    
    # Relacionamentos
    recebimento = relationship("RecebimentoMercadoria", back_populates="itens")
    item_ordem_compra = relationship("ItemOrdemCompra", back_populates="recebimentos")
    produto = relationship("Produto")

class TransferenciaEstoque(Base):
    __tablename__ = "transferencias_estoque"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    local_origem_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=False)
    local_destino_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=False)
    
    # Identificação
    numero = Column(String(20), unique=True, index=True)
    status = Column(String(20), default="pendente")  # pendente, enviada, recebida, cancelada
    
    # Datas
    data_solicitacao = Column(DateTime, default=datetime.utcnow)
    data_envio = Column(DateTime)
    data_recebimento = Column(DateTime)
    
    # Dados complementares
    motivo = Column(String(200))
    observacoes = Column(Text)
    transportadora = Column(String(100))
    numero_rastreamento = Column(String(50))
    
    # Auditoria
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    enviado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    recebido_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    local_origem = relationship("LocalEstoque", foreign_keys=[local_origem_id])
    local_destino = relationship("LocalEstoque", foreign_keys=[local_destino_id])
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    enviado_por = relationship("Usuario", foreign_keys=[enviado_por_id])
    recebido_por = relationship("Usuario", foreign_keys=[recebido_por_id])
    itens = relationship("ItemTransferencia", back_populates="transferencia", cascade="all, delete-orphan")

class ItemTransferencia(Base):
    __tablename__ = "itens_transferencia"
    
    id = Column(Integer, primary_key=True, index=True)
    transferencia_id = Column(Integer, ForeignKey("transferencias_estoque.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    
    # Quantidades
    quantidade_solicitada = Column(Numeric(10, 3), nullable=False)
    quantidade_enviada = Column(Numeric(10, 3), default=0)
    quantidade_recebida = Column(Numeric(10, 3), default=0)
    
    # Dados complementares
    observacoes = Column(Text)
    
    # Relacionamentos
    transferencia = relationship("TransferenciaEstoque", back_populates="itens")
    produto = relationship("Produto")

class InventarioFisico(Base):
    __tablename__ = "inventarios_fisicos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    local_estoque_id = Column(Integer, ForeignKey("locais_estoque.id"), nullable=False)
    
    # Identificação
    numero = Column(String(20), unique=True, index=True)
    descricao = Column(String(200))
    status = Column(Enum(StatusInventarioFisico), default=StatusInventarioFisico.PLANEJADO)
    
    # Datas
    data_planejamento = Column(DateTime, default=datetime.utcnow)
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    data_aprovacao = Column(DateTime)
    
    # Configurações
    tipo_inventario = Column(String(20), default="completo")  # completo, parcial, rotativo
    considera_custo = Column(Boolean, default=True)
    permite_venda_durante = Column(Boolean, default=False)
    
    # Estatísticas
    total_produtos_contados = Column(Integer, default=0)
    total_divergencias = Column(Integer, default=0)
    valor_total_divergencia = Column(Numeric(12, 2), default=0)
    
    # Observações
    motivo = Column(Text)
    observacoes = Column(Text)
    
    # Auditoria
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    aprovado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    empresa = relationship("Empresa")
    local_estoque = relationship("LocalEstoque")
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    aprovado_por = relationship("Usuario", foreign_keys=[aprovado_por_id])
    contagens = relationship("ContagemInventario", back_populates="inventario", cascade="all, delete-orphan")

class ContagemInventario(Base):
    __tablename__ = "contagens_inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    inventario_id = Column(Integer, ForeignKey("inventarios_fisicos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    
    # Quantidades
    quantidade_sistema = Column(Numeric(10, 3), default=0)
    quantidade_contada = Column(Numeric(10, 3))
    quantidade_diferenca = Column(Numeric(10, 3), default=0)
    
    # Valores
    custo_unitario = Column(Numeric(10, 2))
    valor_diferenca = Column(Numeric(12, 2), default=0)
    
    # Dados da contagem
    data_contagem = Column(DateTime, default=datetime.utcnow)
    observacoes = Column(Text)
    motivo_diferenca = Column(String(200))
    
    # Status
    conferido = Column(Boolean, default=False)
    aprovado = Column(Boolean, default=False)
    ajuste_aplicado = Column(Boolean, default=False)
    
    # Auditoria
    contado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    conferido_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    inventario = relationship("InventarioFisico", back_populates="contagens")
    produto = relationship("Produto")
    contado_por = relationship("Usuario", foreign_keys=[contado_por_id])
    conferido_por = relationship("Usuario", foreign_keys=[conferido_por_id])

class ProdutoFornecedor(Base):
    __tablename__ = "produtos_fornecedores"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    
    # Dados comerciais
    codigo_fornecedor = Column(String(50))
    descricao_fornecedor = Column(String(200))
    ultimo_preco = Column(Numeric(10, 2))
    preco_medio = Column(Numeric(10, 2))
    menor_preco = Column(Numeric(10, 2))
    
    # Dados operacionais
    lead_time = Column(Integer, default=7)  # dias
    quantidade_minima = Column(Numeric(10, 3), default=1)
    embalagem = Column(String(50))
    quantidade_por_embalagem = Column(Numeric(10, 3), default=1)
    
    # Status
    ativo = Column(Boolean, default=True)
    fornecedor_principal = Column(Boolean, default=False)
    ultima_compra = Column(DateTime)
    
    # Avaliação
    avaliacao_preco = Column(Integer, default=5)  # 1-5
    avaliacao_qualidade = Column(Integer, default=5)  # 1-5
    avaliacao_prazo = Column(Integer, default=5)  # 1-5
    
    # Auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    produto = relationship("Produto")
    fornecedor = relationship("Fornecedor", back_populates="produtos_fornecedor")

# ================================================================================
# ATUALIZAR RELACIONAMENTOS DOS MODELOS EXISTENTES
# ================================================================================

# Adicionar relacionamentos ao modelo Empresa
def update_empresa_relationships():
    from .models import Empresa
    if not hasattr(Empresa, 'fornecedores'):
        Empresa.fornecedores = relationship("Fornecedor", back_populates="empresa")

# Adicionar relacionamentos ao modelo Produto  
def update_produto_relationships():
    from .models import Produto
    if not hasattr(Produto, 'estoques'):
        Produto.estoques = relationship("EstoqueProduto", back_populates="produto")
    if not hasattr(Produto, 'movimentacoes_estoque'):
        Produto.movimentacoes_estoque = relationship("MovimentacaoEstoque", back_populates="produto")
    if not hasattr(Produto, 'fornecedores'):
        Produto.fornecedores = relationship("ProdutoFornecedor", back_populates="produto")
