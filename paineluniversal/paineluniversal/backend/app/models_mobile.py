"""
Modelos específicos para o App PDV Mobile
Extensões dos modelos principais para funcionalidades mobile
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid

class StatusSessaoGarcom(enum.Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"

class TipoValidacaoNFC(enum.Enum):
    COMANDA = "comanda"
    PULSEIRA = "pulseira"
    CARTAO = "cartao"

class StatusValidacaoNFC(enum.Enum):
    SUCESSO = "sucesso"
    FALHA_CPF = "falha_cpf"
    FALHA_SALDO = "falha_saldo"
    COMANDA_BLOQUEADA = "comanda_bloqueada"
    NFC_ERRO = "nfc_erro"

class SessaoGarcom(Base):
    """Sessões de trabalho dos garçons no app mobile"""
    __tablename__ = "sessoes_garcom"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    garcom_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    
    # Controle de sessão
    token_sessao = Column(String(255), unique=True, nullable=False)
    device_id = Column(String(255))  # ID único do dispositivo
    app_version = Column(String(50))
    device_info = Column(Text)  # JSON com info do device
    
    # Status e timestamps
    status = Column(Enum(StatusSessaoGarcom), default=StatusSessaoGarcom.ATIVA)
    inicio_sessao = Column(DateTime(timezone=True), server_default=func.now())
    fim_sessao = Column(DateTime(timezone=True))
    ultimo_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    
    # Configurações da sessão
    area_atendimento = Column(String(255))  # Área designada para o garçom
    mesa_inicial = Column(Integer)
    mesa_final = Column(Integer)
    configuracoes = Column(Text)  # JSON com preferências do garçom
    
    # Métricas da sessão
    total_vendas = Column(Integer, default=0)
    valor_total_vendido = Column(Numeric(10, 2), default=0)
    total_comandas_atendidas = Column(Integer, default=0)
    
    # Relacionamentos
    garcom = relationship("Usuario")
    evento = relationship("Evento")
    pedidos = relationship("PedidoMobile", back_populates="sessao")
    validacoes_nfc = relationship("ValidacaoNFCMobile", back_populates="sessao")

class ValidacaoNFCMobile(Base):
    """Log de validações NFC realizadas no app mobile"""
    __tablename__ = "validacoes_nfc_mobile"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sessao_id = Column(String(36), ForeignKey("sessoes_garcom.id"), nullable=False)
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    
    # Dados NFC
    nfc_uid = Column(String(255))  # UID único do chip NFC
    nfc_data = Column(Text)  # Dados brutos lidos do NFC
    tipo_validacao = Column(Enum(TipoValidacaoNFC), nullable=False)
    
    # Validação CPF
    cpf_informado = Column(String(3))  # 3 dígitos informados
    cpf_esperado = Column(String(3))   # 3 primeiros dígitos do CPF cadastrado
    cpf_valido = Column(Boolean, default=False)
    
    # Resultado da validação
    status = Column(Enum(StatusValidacaoNFC), nullable=False)
    saldo_disponivel = Column(Numeric(10, 2))
    limite_credito = Column(Numeric(10, 2))
    
    # Auditoria
    ip_origem = Column(String(45))
    device_info = Column(Text)
    timestamp_validacao = Column(DateTime(timezone=True), server_default=func.now())
    detalhes_erro = Column(Text)
    
    # Relacionamentos
    sessao = relationship("SessaoGarcom", back_populates="validacoes_nfc")
    comanda = relationship("Comanda")

class CategoriaMobile(Base):
    """Categorias específicas para o app mobile (com cores e ícones)"""
    __tablename__ = "categorias_mobile"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    icone = Column(String(50), nullable=False)  # emoji ou nome do ícone
    cor = Column(String(7), nullable=False)      # hex color
    ordem_exibicao = Column(Integer, default=1)
    
    # Configurações para mobile
    destino_impressao = Column(String(50))  # bar, cozinha, sobremesa, etc
    tempo_preparo_medio = Column(Integer, default=10)  # minutos
    
    # Vinculação
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    ativo = Column(Boolean, default=True)
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    evento = relationship("Evento")
    produtos = relationship("ProdutoMobile", back_populates="categoria")

class ProdutoMobile(Base):
    """Produtos com informações específicas para mobile"""
    __tablename__ = "produtos_mobile"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    categoria_mobile_id = Column(Integer, ForeignKey("categorias_mobile.id"), nullable=False)
    
    # Configurações mobile específicas
    imagem_mobile = Column(String(500))  # URL otimizada para mobile
    destaque = Column(Boolean, default=False)  # Produto em destaque
    novo = Column(Boolean, default=False)       # Badge "NOVO"
    promocao = Column(Boolean, default=False)   # Badge "PROMOÇÃO"
    
    # Configurações de venda
    vendas_rapidas = Column(Boolean, default=False)  # Acesso rápido no app
    ordem_categoria = Column(Integer, default=1)     # Ordem dentro da categoria
    
    # Informações adicionais
    tempo_preparo = Column(Integer)  # minutos (override da categoria)
    ingredientes = Column(Text)      # Lista de ingredientes
    observacoes_padrao = Column(String(255))  # Observações padrão
    
    ativo_mobile = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    produto = relationship("Produto")
    categoria = relationship("CategoriaMobile", back_populates="produtos")
    itens_pedido = relationship("ItemPedidoMobile", back_populates="produto_mobile")

class StatusPedidoMobile(enum.Enum):
    CARRINHO = "carrinho"          # No carrinho, ainda não enviado
    ENVIADO = "enviado"            # Enviado para impressão
    PREPARANDO = "preparando"      # Em preparo na cozinha/bar
    PRONTO = "pronto"              # Pronto para entrega
    ENTREGUE = "entregue"          # Entregue ao cliente
    CANCELADO = "cancelado"        # Cancelado

class PedidoMobile(Base):
    """Pedidos realizados através do app mobile"""
    __tablename__ = "pedidos_mobile"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_pedido = Column(String(20), unique=True, nullable=False)
    
    # Vinculações
    sessao_id = Column(String(36), ForeignKey("sessoes_garcom.id"), nullable=False)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    
    # Dados do cliente
    cpf_cliente = Column(String(14))
    nome_cliente = Column(String(255))
    mesa_numero = Column(String(20))
    area_atendimento = Column(String(100))
    
    # Valores
    valor_total = Column(Numeric(10, 2), nullable=False)
    valor_desconto = Column(Numeric(10, 2), default=0)
    valor_final = Column(Numeric(10, 2), nullable=False)
    
    # Status e controle
    status = Column(Enum(StatusPedidoMobile), default=StatusPedidoMobile.CARRINHO)
    observacoes_gerais = Column(Text)
    prioridade = Column(Integer, default=1)  # 1=normal, 2=alta, 3=urgente
    
    # Tempos
    tempo_estimado_preparo = Column(Integer)  # minutos
    enviado_impressao_em = Column(DateTime(timezone=True))
    iniciado_preparo_em = Column(DateTime(timezone=True))
    pronto_em = Column(DateTime(timezone=True))
    entregue_em = Column(DateTime(timezone=True))
    
    # Auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    sessao = relationship("SessaoGarcom", back_populates="pedidos")
    comanda = relationship("Comanda")
    evento = relationship("Evento")
    itens = relationship("ItemPedidoMobile", back_populates="pedido")
    impressoes = relationship("ImpressaoPedidoMobile", back_populates="pedido")

class ItemPedidoMobile(Base):
    """Itens dos pedidos mobile"""
    __tablename__ = "itens_pedido_mobile"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(String(36), ForeignKey("pedidos_mobile.id"), nullable=False)
    produto_mobile_id = Column(Integer, ForeignKey("produtos_mobile.id"), nullable=False)
    
    # Quantidade e preços
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    preco_total = Column(Numeric(10, 2), nullable=False)
    
    # Customizações
    observacoes = Column(Text)
    sem_ingredientes = Column(String(255))  # Lista de ingredientes a remover
    extras = Column(String(255))            # Lista de extras adicionados
    
    # Status individual do item
    status_preparo = Column(String(20), default="pendente")
    tempo_preparo_estimado = Column(Integer)  # minutos
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    pedido = relationship("PedidoMobile", back_populates="itens")
    produto_mobile = relationship("ProdutoMobile", back_populates="itens_pedido")

class StatusImpressaoMobile(enum.Enum):
    PENDENTE = "pendente"
    ENVIADA = "enviada"
    SUCESSO = "sucesso"
    ERRO = "erro"
    RETRY = "retry"

class ImpressaoPedidoMobile(Base):
    """Log de impressões dos pedidos mobile"""
    __tablename__ = "impressoes_pedido_mobile"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("pedidos_mobile.id"), nullable=False)
    impressora_id = Column(String(36), ForeignKey("impressoras.id"), nullable=False)
    
    # Controle de impressão
    tipo_impressao = Column(String(50), nullable=False)  # cozinha, bar, caixa
    template_usado = Column(String(255))
    conteudo_impresso = Column(Text)  # Conteúdo que foi impresso
    
    # Status
    status = Column(Enum(StatusImpressaoMobile), default=StatusImpressaoMobile.PENDENTE)
    tentativas = Column(Integer, default=0)
    max_tentativas = Column(Integer, default=3)
    
    # Auditoria
    enviado_em = Column(DateTime(timezone=True), server_default=func.now())
    impresso_em = Column(DateTime(timezone=True))
    erro_msg = Column(Text)
    
    # Relacionamentos
    pedido = relationship("PedidoMobile", back_populates="impressoes")
    impressora = relationship("Impressora")

class ConfiguracaoMobile(Base):
    """Configurações específicas do app mobile por evento"""
    __tablename__ = "configuracoes_mobile"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False, unique=True)
    
    # Configurações NFC
    nfc_habilitado = Column(Boolean, default=True)
    nfc_timeout_segundos = Column(Integer, default=30)
    cpf_max_tentativas = Column(Integer, default=3)
    
    # Configurações de interface
    tema_escuro = Column(Boolean, default=True)
    tamanho_fonte = Column(String(10), default="normal")
    vibrar_feedback = Column(Boolean, default=True)
    som_notificacao = Column(Boolean, default=False)
    
    # Configurações operacionais
    modo_offline = Column(Boolean, default=True)
    sync_automatico = Column(Boolean, default=True)
    backup_local = Column(Boolean, default=True)
    
    # Limites e validações
    valor_maximo_pedido = Column(Numeric(10, 2), default=1000)
    itens_maximos_pedido = Column(Integer, default=50)
    timeout_sessao_minutos = Column(Integer, default=480)  # 8 horas
    
    # Configurações de impressão
    impressao_automatica = Column(Boolean, default=True)
    impressao_duplicada = Column(Boolean, default=False)
    impressao_prioritaria = Column(Boolean, default=False)
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento
    evento = relationship("Evento")

class LogAtividadeMobile(Base):
    """Log de atividades do app mobile para auditoria"""
    __tablename__ = "logs_atividade_mobile"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sessao_id = Column(String(36), ForeignKey("sessoes_garcom.id"))
    
    # Atividade
    acao = Column(String(100), nullable=False)  # login, logout, pedido_criado, nfc_lido, etc
    detalhes = Column(Text)  # JSON com detalhes da ação
    resultado = Column(String(20), default="sucesso")  # sucesso, erro, warning
    
    # Contexto
    tela_app = Column(String(50))
    funcionalidade = Column(String(50))
    dados_entrada = Column(Text)  # JSON com dados de entrada
    dados_saida = Column(Text)    # JSON com resultado
    
    # Auditoria
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_origem = Column(String(45))
    device_info = Column(Text)
    
    # Relacionamento
    sessao = relationship("SessaoGarcom")

class ComandaNFC(Base):
    """Extensão da tabela Comanda para funcionalidades NFC específicas"""
    __tablename__ = "comandas_nfc"
    
    id = Column(Integer, primary_key=True, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False, unique=True)
    
    # Dados NFC
    nfc_uid = Column(String(255), unique=True, nullable=False)
    nfc_tipo = Column(Enum(TipoValidacaoNFC), default=TipoValidacaoNFC.COMANDA)
    nfc_versao = Column(String(10), default="1.0")
    
    # Configurações de segurança
    cpf_hash = Column(String(255))  # Hash dos 3 primeiros dígitos para validação
    bloqueada_tentativas = Column(Boolean, default=False)
    tentativas_cpf_erradas = Column(Integer, default=0)
    max_tentativas_cpf = Column(Integer, default=3)
    
    # Histórico de uso
    primeira_leitura = Column(DateTime(timezone=True))
    ultima_leitura = Column(DateTime(timezone=True))
    total_leituras = Column(Integer, default=0)
    total_pedidos = Column(Integer, default=0)
    
    # Status e configurações
    ativa_nfc = Column(Boolean, default=True)
    requer_cpf = Column(Boolean, default=True)
    limite_por_leitura = Column(Numeric(10, 2))
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento
    comanda = relationship("Comanda")
