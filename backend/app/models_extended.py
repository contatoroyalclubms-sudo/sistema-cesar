from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum, Date, Float, JSON, Time, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from .models import Usuario, Evento, Produto, CategoriaProduto  # Import existing models
import enum
from datetime import datetime
import uuid

# ====== SISTEMA MULTI-CARDÁPIO ======

class TipoCardapio(enum.Enum):
    PRINCIPAL = "principal"
    BEBIDAS = "bebidas"
    SOBREMESAS = "sobremesas"
    ESPECIAL = "especial"
    KIDS = "kids"
    VEGETARIANO = "vegetariano"
    FITNESS = "fitness"
    PROMOCOES = "promocoes"
    DELIVERY = "delivery"

class CardapioDigital(Base):
    __tablename__ = "cardapios_digitais"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo = Column(Enum(TipoCardapio), default=TipoCardapio.PRINCIPAL)
    ativo = Column(Boolean, default=True)
    ordem = Column(Integer, default=0)
    url_slug = Column(String(100), unique=True)
    moeda = Column(String(10), default="BRL")
    taxa_servico = Column(Numeric(5, 2), default=0)
    configuracoes = Column(JSON)  # cores, fontes, layout, etc
    criado_por = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")
    criador = relationship("Usuario")
    categorias = relationship("CategoriaCardapio", back_populates="cardapio", cascade="all, delete-orphan")
    qr_codes = relationship("CardapioQRCode", back_populates="cardapio")
    analytics = relationship("AnalyticsCardapio", back_populates="cardapio")

class CategoriaCardapio(Base):
    __tablename__ = "categorias_cardapio"
    
    id = Column(Integer, primary_key=True, index=True)
    cardapio_id = Column(Integer, ForeignKey("cardapios_digitais.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    imagem_url = Column(String(500))
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    cardapio = relationship("CardapioDigital", back_populates="categorias")
    itens = relationship("ItemCardapio", back_populates="categoria", cascade="all, delete-orphan")

class ItemCardapio(Base):
    __tablename__ = "itens_cardapio"
    
    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias_cardapio.id"), nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    preco = Column(Numeric(10, 2), nullable=False)
    preco_promocional = Column(Numeric(10, 2))
    imagem_url = Column(String(500))
    tags = Column(JSON)  # ["Vegetariano", "Sem Glúten", etc]
    alergenos = Column(JSON)  # ["Leite", "Amendoim", etc]
    calorias = Column(Integer)
    tempo_preparo = Column(Integer)  # em minutos
    disponivel = Column(Boolean, default=True)
    estoque = Column(Integer)
    ordem = Column(Integer, default=0)
    vendas_total = Column(Integer, default=0)
    avaliacao_media = Column(Numeric(3, 2))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    categoria = relationship("CategoriaCardapio", back_populates="itens")
    modificadores = relationship("ItemModificador", back_populates="item")
    restricoes = relationship("RestricaoHoraria", back_populates="item")

# Tabela associativa para modificadores
item_grupo_modificadores = Table(
    'item_grupo_modificadores',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('itens_cardapio.id')),
    Column('grupo_id', Integer, ForeignKey('grupos_modificadores.id'))
)

class GrupoModificadores(Base):
    __tablename__ = "grupos_modificadores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    obrigatorio = Column(Boolean, default=False)
    minimo = Column(Integer, default=0)
    maximo = Column(Integer, default=1)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    modificadores = relationship("ModificadorCardapio", back_populates="grupo")
    itens = relationship("ItemCardapio", secondary=item_grupo_modificadores, backref="grupos_modificadores")

class ModificadorCardapio(Base):
    __tablename__ = "modificadores_cardapio"
    
    id = Column(Integer, primary_key=True, index=True)
    grupo_id = Column(Integer, ForeignKey("grupos_modificadores.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    preco_adicional = Column(Numeric(10, 2), default=0)
    disponivel = Column(Boolean, default=True)
    estoque = Column(Integer)
    
    grupo = relationship("GrupoModificadores", back_populates="modificadores")

class ItemModificador(Base):
    __tablename__ = "itens_modificadores"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("itens_cardapio.id"), nullable=False)
    modificador_id = Column(Integer, ForeignKey("modificadores_cardapio.id"), nullable=False)
    
    item = relationship("ItemCardapio", back_populates="modificadores")
    modificador = relationship("ModificadorCardapio")

class RestricaoHoraria(Base):
    __tablename__ = "restricoes_horarias"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("itens_cardapio.id"))
    categoria_id = Column(Integer, ForeignKey("categorias_cardapio.id"))
    dia_semana = Column(Integer)  # 0=domingo, 6=sábado
    hora_inicio = Column(Time)
    hora_fim = Column(Time)
    disponivel = Column(Boolean, default=True)
    
    item = relationship("ItemCardapio", back_populates="restricoes")
    categoria = relationship("CategoriaCardapio")

class CardapioQRCode(Base):
    __tablename__ = "cardapio_qrcodes"
    
    id = Column(Integer, primary_key=True, index=True)
    cardapio_id = Column(Integer, ForeignKey("cardapios_digitais.id"), nullable=False)
    url = Column(String(500), nullable=False)
    short_url = Column(String(100))
    qr_code_data = Column(Text)  # Base64 encoded
    acessos = Column(Integer, default=0)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    cardapio = relationship("CardapioDigital", back_populates="qr_codes")

class AnalyticsCardapio(Base):
    __tablename__ = "analytics_cardapio"
    
    id = Column(Integer, primary_key=True, index=True)
    cardapio_id = Column(Integer, ForeignKey("cardapios_digitais.id"), nullable=False)
    data = Column(Date, nullable=False)
    visualizacoes = Column(Integer, default=0)
    conversoes = Column(Integer, default=0)
    itens_mais_vistos = Column(JSON)  # {"item_id": count}
    tempo_medio_visita = Column(Integer)  # em segundos
    dispositivos = Column(JSON)  # {"mobile": count, "desktop": count}
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    cardapio = relationship("CardapioDigital", back_populates="analytics")

class CardapioReorderRequest(Base):
    """Schema para reordenação drag & drop"""
    __tablename__ = "cardapio_reorder_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50))  # 'cardapio', 'categoria', 'item'
    items = Column(JSON)  # [{"id": 1, "ordem": 0}, {"id": 2, "ordem": 1}]
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class CategoriaReorderRequest(Base):
    """Schema para reordenação de categorias"""
    __tablename__ = "categoria_reorder_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    cardapio_id = Column(Integer, ForeignKey("cardapios_digitais.id"))
    items = Column(JSON)  # [{"id": 1, "ordem": 0}, {"id": 2, "ordem": 1}]
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

# ====== SISTEMA KDS (Kitchen Display System) ======

class StatusPedidoKDS(enum.Enum):
    RECEBIDO = "recebido"
    PREPARANDO = "preparando"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

class TipoEstacaoKDS(enum.Enum):
    COZINHA = "cozinha"
    BAR = "bar"
    SOBREMESA = "sobremesa"
    GRELHADOS = "grelhados"
    FRITURAS = "frituras"
    SALADAS = "saladas"
    PIZZAS = "pizzas"
    SUSHI = "sushi"

class EstacaoKDS(Base):
    __tablename__ = "estacoes_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoEstacaoKDS), nullable=False)
    ip_address = Column(String(45))
    ativo = Column(Boolean, default=True)
    tempo_medio_preparo = Column(Integer, default=15)  # minutos
    alarme_tempo = Column(Integer, default=20)  # minutos para alarme
    configuracoes = Column(JSON)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    pedidos = relationship("PedidoKDS", back_populates="estacao")

class PedidoKDS(Base):
    __tablename__ = "pedidos_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"), nullable=False)
    venda_id = Column(Integer, ForeignKey("vendas_pdv.id"))
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    mesa_id = Column(Integer, ForeignKey("mesas_evento.id"))
    numero_pedido = Column(String(20), nullable=False, unique=True)
    tipo_pedido = Column(String(50))  # 'mesa', 'balcao', 'delivery', 'drive-thru'
    prioridade = Column(Integer, default=1)  # 1=normal, 2=alta, 3=urgente
    status = Column(Enum(StatusPedidoKDS), default=StatusPedidoKDS.RECEBIDO)
    observacoes = Column(Text)
    tempo_espera = Column(Integer, default=0)  # minutos
    tempo_preparo = Column(Integer)  # minutos reais
    recebido_em = Column(DateTime(timezone=True), server_default=func.now())
    iniciado_em = Column(DateTime(timezone=True))
    pronto_em = Column(DateTime(timezone=True))
    entregue_em = Column(DateTime(timezone=True))
    cancelado_em = Column(DateTime(timezone=True))
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    estacao = relationship("EstacaoKDS", back_populates="pedidos")
    itens = relationship("ItemPedidoKDS", back_populates="pedido", cascade="all, delete-orphan")
    operador = relationship("Usuario")

class ItemPedidoKDS(Base):
    __tablename__ = "itens_pedido_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    nome_item = Column(String(200), nullable=False)
    quantidade = Column(Integer, nullable=False)
    modificadores = Column(JSON)  # ["Sem cebola", "Extra bacon"]
    observacoes = Column(Text)
    status = Column(Enum(StatusPedidoKDS), default=StatusPedidoKDS.RECEBIDO)
    preparado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    pedido = relationship("PedidoKDS", back_populates="itens")
    produto = relationship("Produto")
    preparado_por = relationship("Usuario")

class HistoricoKDS(Base):
    __tablename__ = "historico_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"), nullable=False)
    status_anterior = Column(Enum(StatusPedidoKDS))
    status_novo = Column(Enum(StatusPedidoKDS), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    observacao = Column(Text)
    tempo_decorrido = Column(Integer)  # segundos desde último status
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    usuario = relationship("Usuario")

class AlertaKDS(Base):
    __tablename__ = "alertas_kds"
    
    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacoes_kds.id"))
    pedido_id = Column(Integer, ForeignKey("pedidos_kds.id"))
    tipo_alerta = Column(String(50))  # 'tempo_excedido', 'prioridade_alta', 'retrabalho'
    mensagem = Column(Text)
    ativo = Column(Boolean, default=True)
    reconhecido = Column(Boolean, default=False)
    reconhecido_por_id = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    reconhecido_em = Column(DateTime(timezone=True))

# ====== SISTEMA DE MESAS ======

class StatusMesa(enum.Enum):
    LIVRE = "livre"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"
    CONTA = "conta"
    LIMPEZA = "limpeza"
    MANUTENCAO = "manutencao"

class TipoMesa(enum.Enum):
    NORMAL = "normal"
    VIP = "vip"
    CAMAROTE = "camarote"
    BALCAO = "balcao"
    EXTERNA = "externa"
    PRIVADA = "privada"

class SetorMesa(Base):
    __tablename__ = "setores_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    cor = Column(String(7))  # Hex color
    capacidade_total = Column(Integer)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    mesas = relationship("MesaEvento", back_populates="setor")

class MesaEvento(Base):
    __tablename__ = "mesas_evento"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    setor_id = Column(Integer, ForeignKey("setores_mesa.id"))
    numero = Column(String(20), nullable=False)
    tipo = Column(Enum(TipoMesa), default=TipoMesa.NORMAL)
    capacidade = Column(Integer, nullable=False)
    status = Column(Enum(StatusMesa), default=StatusMesa.LIVRE)
    posicao_x = Column(Integer)  # Para mapa visual
    posicao_y = Column(Integer)  # Para mapa visual
    largura = Column(Integer, default=100)
    altura = Column(Integer, default=100)
    rotacao = Column(Integer, default=0)
    formato = Column(String(20), default="quadrado")  # quadrado, redondo, retangular
    qr_code = Column(Text)  # QR Code da mesa
    garcom_id = Column(Integer, ForeignKey("usuarios.id"))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    evento = relationship("Evento")
    setor = relationship("SetorMesa", back_populates="mesas")
    garcom = relationship("Usuario")
    ocupacoes = relationship("OcupacaoMesa", back_populates="mesa")
    comandas = relationship("ComandaMesa", back_populates="mesa")

class OcupacaoMesa(Base):
    __tablename__ = "ocupacoes_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas_evento.id"), nullable=False)
    cliente_nome = Column(String(200))
    numero_pessoas = Column(Integer, default=1)
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    garcom_id = Column(Integer, ForeignKey("usuarios.id"))
    valor_consumo = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="ativa")  # ativa, encerrada
    entrada = Column(DateTime(timezone=True), server_default=func.now())
    saida = Column(DateTime(timezone=True))
    tempo_permanencia = Column(Integer)  # minutos
    observacoes = Column(Text)
    
    mesa = relationship("MesaEvento", back_populates="ocupacoes")
    comanda = relationship("Comanda")
    garcom = relationship("Usuario")

class ComandaMesa(Base):
    __tablename__ = "comandas_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas_evento.id"), nullable=False)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False)
    ativa = Column(Boolean, default=True)
    vinculada_em = Column(DateTime(timezone=True), server_default=func.now())
    desvinculada_em = Column(DateTime(timezone=True))
    
    mesa = relationship("MesaEvento", back_populates="comandas")
    comanda = relationship("Comanda")

class JuncaoMesa(Base):
    __tablename__ = "juncoes_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    mesa_principal_id = Column(Integer, ForeignKey("mesas_evento.id"), nullable=False)
    mesa_juntada_id = Column(Integer, ForeignKey("mesas_evento.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    motivo = Column(Text)
    juntada_em = Column(DateTime(timezone=True), server_default=func.now())
    separada_em = Column(DateTime(timezone=True))
    ativa = Column(Boolean, default=True)
    
    mesa_principal = relationship("MesaEvento", foreign_keys=[mesa_principal_id])
    mesa_juntada = relationship("MesaEvento", foreign_keys=[mesa_juntada_id])
    usuario = relationship("Usuario")

class TransferenciaMesa(Base):
    __tablename__ = "transferencias_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    mesa_origem_id = Column(Integer, ForeignKey("mesas_evento.id"), nullable=False)
    mesa_destino_id = Column(Integer, ForeignKey("mesas_evento.id"), nullable=False)
    comanda_id = Column(Integer, ForeignKey("comandas.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    motivo = Column(Text)
    transferida_em = Column(DateTime(timezone=True), server_default=func.now())
    
    mesa_origem = relationship("MesaEvento", foreign_keys=[mesa_origem_id])
    mesa_destino = relationship("MesaEvento", foreign_keys=[mesa_destino_id])
    comanda = relationship("Comanda")
    usuario = relationship("Usuario")

class ReservaMesa(Base):
    __tablename__ = "reservas_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    mesa_id = Column(Integer, ForeignKey("mesas_evento.id"), nullable=False)
    cliente_nome = Column(String(200), nullable=False)
    cliente_telefone = Column(String(20))
    numero_pessoas = Column(Integer)
    data_reserva = Column(DateTime(timezone=True), nullable=False)
    duracao_prevista = Column(Integer, default=120)  # minutos
    status = Column(String(20), default="confirmada")  # confirmada, cancelada, realizada
    observacoes = Column(Text)
    criada_em = Column(DateTime(timezone=True), server_default=func.now())
    criada_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    mesa = relationship("MesaEvento")
    criada_por = relationship("Usuario")

# ====== SISTEMA MAPA DE OPERAÇÕES ======

class MapaOperacional(Base):
    __tablename__ = "mapas_operacionais"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # 'mesas', 'setores', 'pdvs', 'completo'
    largura = Column(Integer, default=1920)
    altura = Column(Integer, default=1080)
    imagem_fundo = Column(Text)  # Base64 ou URL
    configuracao = Column(JSON)  # Layout e configurações visuais
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    evento = relationship("Evento")
    elementos = relationship("ElementoMapa", back_populates="mapa")

class TipoElementoMapa(enum.Enum):
    MESA = "mesa"
    PDV = "pdv"
    BAR = "bar"
    COZINHA = "cozinha"
    ENTRADA = "entrada"
    SAIDA = "saida"
    BANHEIRO = "banheiro"
    PALCO = "palco"
    AREA_VIP = "area_vip"
    ESTOQUE = "estoque"

class ElementoMapa(Base):
    __tablename__ = "elementos_mapa_operacional"
    
    id = Column(Integer, primary_key=True, index=True)
    mapa_id = Column(Integer, ForeignKey("mapas_operacionais.id"), nullable=False)
    tipo = Column(Enum(TipoElementoMapa), nullable=False)
    referencia_id = Column(Integer)  # ID da mesa, pdv, etc
    codigo = Column(String(50))
    nome = Column(String(100))
    posicao_x = Column(Integer)
    posicao_y = Column(Integer)
    largura = Column(Integer)
    altura = Column(Integer)
    rotacao = Column(Integer, default=0)
    cor = Column(String(7))
    icone = Column(String(50))
    dados = Column(JSON)  # Dados específicos do elemento
    ativo = Column(Boolean, default=True)
    
    mapa = relationship("MapaOperacional", back_populates="elementos")

# ====== FLUXOS DE TRABALHO E AUTOMAÇÃO ======

class FluxoTrabalhoExtended(Base):
    __tablename__ = "fluxos_trabalho_extended"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(50))
    passos = Column(JSON)  # Definição dos passos do fluxo
    variaveis = Column(JSON)  # Variáveis do fluxo
    gatilhos = Column(JSON)  # Condições de disparo
    acoes = Column(JSON)  # Ações a executar
    condicoes = Column(JSON)  # Condições de execução
    ativo = Column(Boolean, default=True)
    execucoes_total = Column(Integer, default=0)
    execucoes_sucesso = Column(Integer, default=0)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    criado_por = relationship("Usuario")
    execucoes = relationship("ExecucaoFluxo", back_populates="fluxo")

class ExecucaoFluxo(Base):
    __tablename__ = "execucoes_fluxo"
    
    id = Column(Integer, primary_key=True, index=True)
    fluxo_id = Column(Integer, ForeignKey("fluxos_trabalho.id"), nullable=False)
    status = Column(String(20))  # pendente, executando, sucesso, erro, cancelado
    contexto = Column(JSON)  # Contexto da execução
    resultado = Column(JSON)  # Resultado da execução
    erro = Column(Text)
    tempo_execucao = Column(Integer)  # em millisegundos
    iniciado_em = Column(DateTime(timezone=True), server_default=func.now())
    finalizado_em = Column(DateTime(timezone=True))
    
    fluxo = relationship("FluxoTrabalho", back_populates="execucoes")

# ====== WEBHOOKS E INTEGRAÇÕES ======

class WebhookIntegracao(Base):
    __tablename__ = "webhooks_integracao"
    
    id = Column(Integer, primary_key=True, index=True)
    integracao_id = Column(Integer, ForeignKey("integracoes.id"))
    nome = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    metodo = Column(String(10), default="POST")  # GET, POST, PUT, DELETE
    eventos = Column(JSON)  # ["venda.criada", "comanda.fechada", etc]
    headers = Column(JSON)  # Headers customizados
    secret = Column(String(255))  # Secret para validação
    ativo = Column(Boolean, default=True)
    total_chamadas = Column(Integer, default=0)
    total_sucesso = Column(Integer, default=0)
    total_erros = Column(Integer, default=0)
    ultima_chamada = Column(DateTime(timezone=True))
    ultimo_erro = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    integracao = relationship("Integracao")
    logs = relationship("LogWebhook", back_populates="webhook")

class LogWebhook(Base):
    __tablename__ = "logs_webhook"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks_integracao.id"), nullable=False)
    evento = Column(String(100), nullable=False)
    payload_enviado = Column(JSON)
    resposta = Column(JSON)
    status_http = Column(Integer)
    tempo_resposta = Column(Integer)  # millisegundos
    sucesso = Column(Boolean)
    erro = Column(Text)
    tentativa = Column(Integer, default=1)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    webhook = relationship("WebhookIntegracao", back_populates="logs")

# ====== SOLUÇÕES ONLINE E RECURSOS APP ======

class SolucaoOnline(Base):
    __tablename__ = "solucoes_online"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))  # app, web, pwa, api
    descricao = Column(Text)
    url = Column(String(500))
    recursos = Column(JSON)  # Lista de recursos disponíveis
    configuracoes = Column(JSON)
    icone = Column(String(255))
    ordem = Column(Integer, default=0)
    ativa = Column(Boolean, default=True)
    total_acessos = Column(Integer, default=0)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

class RecursoApp(Base):
    __tablename__ = "recursos_app"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    categoria = Column(String(50))
    descricao = Column(Text)
    versao = Column(String(20))
    dependencias = Column(JSON)
    configuracao_padrao = Column(JSON)
    documentacao_url = Column(String(500))
    gratuito = Column(Boolean, default=True)
    preco = Column(Numeric(10, 2))
    popularidade = Column(Integer, default=0)
    total_instalacoes = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

# ====== PERMISSÕES E SEGURANÇA AVANÇADA ======

class PermissaoCheckRequest(Base):
    """Request para verificar permissão"""
    __tablename__ = "permissao_check_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    modulo = Column(String(50), nullable=False)
    acao = Column(String(50), nullable=False)
    recurso_id = Column(Integer)  # ID do recurso específico
    contexto = Column(JSON)  # Contexto adicional
    resultado = Column(Boolean)
    motivo = Column(Text)
    verificado_em = Column(DateTime(timezone=True), server_default=func.now())

class PermissaoCheckResponse(Base):
    """Response de verificação de permissão"""
    __tablename__ = "permissao_check_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("permissao_check_requests.id"))
    has_permission = Column(Boolean, nullable=False)
    reason = Column(Text)
    permissoes_necessarias = Column(JSON)  # Lista de permissões necessárias
    permissoes_usuario = Column(JSON)  # Lista de permissões do usuário
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class PermissaoBulkAssignRequest(Base):
    """Request para atribuição em massa de permissões"""
    __tablename__ = "permissao_bulk_assign_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id"))
    permissao_ids = Column(JSON)  # Lista de IDs de permissões
    replace_existing = Column(Boolean, default=False)
    executado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    executado_em = Column(DateTime(timezone=True), server_default=func.now())