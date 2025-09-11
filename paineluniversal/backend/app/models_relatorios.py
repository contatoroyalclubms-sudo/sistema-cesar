from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, JSON, Numeric, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any, List

Base = declarative_base()

# Enums para o sistema de relatórios
class TipoRelatorio(PyEnum):
    VENDAS = "vendas"
    FINANCEIRO = "financeiro"
    ESTOQUE = "estoque"
    MARKETING = "marketing"
    OPERACIONAL = "operacional"
    FIDELIDADE = "fidelidade"
    COMUNICACAO = "comunicacao"
    RH = "rh"
    EXECUTIVO = "executivo"
    COMPLIANCE = "compliance"
    PERSONALIZADO = "personalizado"

class StatusRelatorio(PyEnum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    RASCUNHO = "rascunho"
    ARQUIVADO = "arquivado"

class StatusExecucao(PyEnum):
    PENDENTE = "pendente"
    EXECUTANDO = "executando"
    CONCLUIDO = "concluido"
    ERRO = "erro"
    CANCELADO = "cancelado"

class FormatoExportacao(PyEnum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"

class TipoVisualizacao(PyEnum):
    TABELA = "tabela"
    GRAFICO_LINHA = "grafico_linha"
    GRAFICO_BARRA = "grafico_barra"
    GRAFICO_PIZZA = "grafico_pizza"
    HEATMAP = "heatmap"
    KPI = "kpi"
    FUNIL = "funil"
    GAUGE = "gauge"
    MAPA = "mapa"

class FrequenciaAgendamento(PyEnum):
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"
    PERSONALIZADO = "personalizado"

class TipoWidget(PyEnum):
    METRICA = "metrica"
    GRAFICO = "grafico"
    TABELA = "tabela"
    MAPA = "mapa"
    TEXTO = "texto"
    IFRAME = "iframe"

class NivelPermissao(PyEnum):
    PUBLICO = "publico"
    EMPRESA = "empresa"
    DEPARTAMENTO = "departamento"
    PRIVADO = "privado"

# Model para categorização e configuração de relatórios
class ConfiguracaoRelatorio(Base):
    __tablename__ = "configuracoes_relatorio"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo = Column(Enum(TipoRelatorio), nullable=False)
    categoria = Column(String(50))  # Subcategoria personalizada
    
    # Configuração do relatório
    query_sql = Column(Text)  # Query SQL principal
    configuracao_visual = Column(JSON, default={})  # Configurações de layout
    filtros_disponiveis = Column(JSON, default=[])  # Filtros disponíveis
    parametros_padrao = Column(JSON, default={})  # Valores padrão
    
    # Configurações de performance
    cache_duracao = Column(Integer, default=300)  # Cache em segundos
    timeout_execucao = Column(Integer, default=60)  # Timeout em segundos
    limite_registros = Column(Integer, default=10000)
    
    # Metadados
    tags = Column(JSON, default=[])  # Tags para organização
    autor_id = Column(Integer, ForeignKey("usuarios.id"))
    versao = Column(String(10), default="1.0")
    
    # Status e permissões
    status = Column(Enum(StatusRelatorio), default=StatusRelatorio.RASCUNHO)
    nivel_permissao = Column(Enum(NivelPermissao), default=NivelPermissao.EMPRESA)
    publico = Column(Boolean, default=False)
    
    # Estatísticas de uso
    total_execucoes = Column(Integer, default=0)
    ultima_execucao = Column(DateTime)
    tempo_medio_execucao = Column(Numeric(8, 2), default=0.0)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="configuracoes_relatorio")
    autor = relationship("Usuario")
    execucoes = relationship("ExecucaoRelatorio", back_populates="configuracao")
    agendamentos = relationship("AgendamentoRelatorio", back_populates="configuracao")
    compartilhamentos = relationship("CompartilhamentoRelatorio", back_populates="configuracao")
    
    # Índices
    __table_args__ = (
        Index('idx_config_empresa_tipo', 'empresa_id', 'tipo'),
        Index('idx_config_status', 'status'),
        Index('idx_config_publico', 'publico'),
    )

# Model para execuções de relatórios
class ExecucaoRelatorio(Base):
    __tablename__ = "execucoes_relatorio"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    configuracao_id = Column(Integer, ForeignKey("configuracoes_relatorio.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Parâmetros da execução
    parametros = Column(JSON, default={})  # Parâmetros usados
    filtros_aplicados = Column(JSON, default={})  # Filtros aplicados
    
    # Status e timing
    status = Column(Enum(StatusExecucao), default=StatusExecucao.PENDENTE)
    iniciado_em = Column(DateTime, default=func.now())
    concluido_em = Column(DateTime)
    tempo_execucao = Column(Numeric(8, 2))  # Em segundos
    
    # Resultados
    total_registros = Column(Integer, default=0)
    dados_resultado = Column(JSON)  # Resultado serializado (para relatórios pequenos)
    arquivo_resultado = Column(String(500))  # Caminho do arquivo gerado
    hash_cache = Column(String(64))  # Hash para cache
    
    # Metadados da execução
    ip_usuario = Column(String(45))
    user_agent = Column(String(500))
    origem = Column(String(50))  # web, api, agendamento, etc.
    
    # Erro e debugging
    erro_detalhes = Column(Text)
    stack_trace = Column(Text)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    configuracao = relationship("ConfiguracaoRelatorio", back_populates="execucoes")
    usuario = relationship("Usuario")
    exportacoes = relationship("ExportacaoRelatorio", back_populates="execucao")
    
    # Índices
    __table_args__ = (
        Index('idx_execucao_empresa', 'empresa_id'),
        Index('idx_execucao_status', 'status'),
        Index('idx_execucao_data', 'iniciado_em'),
        Index('idx_execucao_config', 'configuracao_id'),
    )

# Model para agendamentos automáticos
class AgendamentoRelatorio(Base):
    __tablename__ = "agendamentos_relatorio"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    configuracao_id = Column(Integer, ForeignKey("configuracoes_relatorio.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Configuração do agendamento
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    frequencia = Column(Enum(FrequenciaAgendamento), nullable=False)
    configuracao_cron = Column(String(100))  # Expressão cron para agendamentos personalizados
    
    # Parâmetros fixos
    parametros_fixos = Column(JSON, default={})
    filtros_fixos = Column(JSON, default={})
    formato_exportacao = Column(Enum(FormatoExportacao), default=FormatoExportacao.PDF)
    
    # Configurações de entrega
    emails_destinatarios = Column(JSON, default=[])  # Lista de emails
    salvar_arquivo = Column(Boolean, default=True)
    pasta_destino = Column(String(500))
    
    # Configurações avançadas
    ativo = Column(Boolean, default=True)
    fuso_horario = Column(String(50), default="America/Sao_Paulo")
    horario_execucao = Column(String(5), default="09:00")  # HH:MM
    
    # Controle de execução
    proxima_execucao = Column(DateTime)
    ultima_execucao = Column(DateTime)
    total_execucoes = Column(Integer, default=0)
    execucoes_com_erro = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    configuracao = relationship("ConfiguracaoRelatorio", back_populates="agendamentos")
    usuario = relationship("Usuario")
    
    # Índices
    __table_args__ = (
        Index('idx_agendamento_empresa', 'empresa_id'),
        Index('idx_agendamento_ativo', 'ativo'),
        Index('idx_agendamento_proxima', 'proxima_execucao'),
    )

# Model para compartilhamento e permissões
class CompartilhamentoRelatorio(Base):
    __tablename__ = "compartilhamentos_relatorio"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    configuracao_id = Column(Integer, ForeignKey("configuracoes_relatorio.id"), nullable=False)
    
    # Destinatário do compartilhamento
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    email_externo = Column(String(100))  # Para compartilhamento com externos
    token_acesso = Column(String(100))  # Token único para acesso
    
    # Permissões
    pode_visualizar = Column(Boolean, default=True)
    pode_executar = Column(Boolean, default=True)
    pode_exportar = Column(Boolean, default=False)
    pode_editar = Column(Boolean, default=False)
    
    # Configurações do compartilhamento
    data_expiracao = Column(DateTime)
    limite_execucoes = Column(Integer)
    execucoes_realizadas = Column(Integer, default=0)
    
    # Status
    ativo = Column(Boolean, default=True)
    revogado = Column(Boolean, default=False)
    revogado_em = Column(DateTime)
    revogado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Auditoria
    ultimo_acesso = Column(DateTime)
    total_acessos = Column(Integer, default=0)
    ip_ultimo_acesso = Column(String(45))
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa")
    configuracao = relationship("ConfiguracaoRelatorio", back_populates="compartilhamentos")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    
    # Índices
    __table_args__ = (
        Index('idx_compartilhamento_empresa', 'empresa_id'),
        Index('idx_compartilhamento_token', 'token_acesso'),
        Index('idx_compartilhamento_ativo', 'ativo'),
    )

# Model para dashboards executivos
class DashboardExecutivo(Base):
    __tablename__ = "dashboards_executivo"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(50))
    
    # Configuração do layout
    layout_configuracao = Column(JSON, default={})  # Grid layout, posições, tamanhos
    configuracao_tema = Column(JSON, default={})  # Cores, fontes, estilo
    
    # Configurações de atualização
    auto_refresh = Column(Boolean, default=True)
    intervalo_refresh = Column(Integer, default=300)  # Em segundos
    cache_habilitado = Column(Boolean, default=True)
    
    # Permissões e compartilhamento
    publico = Column(Boolean, default=False)
    nivel_permissao = Column(Enum(NivelPermissao), default=NivelPermissao.PRIVADO)
    
    # Metadados
    tags = Column(JSON, default=[])
    favorito = Column(Boolean, default=False)
    
    # Estatísticas
    total_visualizacoes = Column(Integer, default=0)
    ultima_visualizacao = Column(DateTime)
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="dashboards_executivo")
    usuario = relationship("Usuario")
    widgets = relationship("WidgetDashboard", back_populates="dashboard")
    
    # Índices
    __table_args__ = (
        Index('idx_dashboard_empresa', 'empresa_id'),
        Index('idx_dashboard_usuario', 'usuario_id'),
        Index('idx_dashboard_publico', 'publico'),
    )

# Model para widgets de dashboard
class WidgetDashboard(Base):
    __tablename__ = "widgets_dashboard"
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards_executivo.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoWidget), nullable=False)
    descricao = Column(Text)
    
    # Configuração do widget
    configuracao_relatorio_id = Column(Integer, ForeignKey("configuracoes_relatorio.id"))
    query_customizada = Column(Text)
    parametros = Column(JSON, default={})
    
    # Layout e visualização
    posicao_x = Column(Integer, default=0)
    posicao_y = Column(Integer, default=0)
    largura = Column(Integer, default=4)
    altura = Column(Integer, default=3)
    
    configuracao_visual = Column(JSON, default={})  # Cores, tipos de gráfico, etc.
    tipo_visualizacao = Column(Enum(TipoVisualizacao))
    
    # Configurações de atualização
    auto_refresh = Column(Boolean, default=True)
    intervalo_refresh = Column(Integer, default=300)
    
    # Cache e performance
    ultimo_resultado = Column(JSON)  # Cache do último resultado
    ultima_atualizacao = Column(DateTime)
    tempo_execucao = Column(Numeric(6, 2))
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    dashboard = relationship("DashboardExecutivo", back_populates="widgets")
    configuracao_relatorio = relationship("ConfiguracaoRelatorio")
    
    # Índices
    __table_args__ = (
        Index('idx_widget_dashboard', 'dashboard_id'),
        Index('idx_widget_ativo', 'ativo'),
    )

# Model para métricas de negócio
class MetricaNegocio(Base):
    __tablename__ = "metricas_negocio"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Informações da métrica
    nome = Column(String(100), nullable=False)
    codigo = Column(String(50), nullable=False)  # Código único da métrica
    descricao = Column(Text)
    categoria = Column(String(50))
    
    # Configuração do cálculo
    formula_sql = Column(Text, nullable=False)  # Query SQL para calcular
    unidade = Column(String(20))  # %, R$, un, etc.
    formato_exibicao = Column(String(50))  # Formatação para exibição
    
    # Metas e alertas
    meta_valor = Column(Numeric(15, 2))
    meta_tipo = Column(String(20))  # maior_que, menor_que, igual_a
    alerta_habilitado = Column(Boolean, default=False)
    alerta_threshold = Column(Numeric(15, 2))
    
    # Configurações de cálculo
    frequencia_calculo = Column(Enum(FrequenciaAgendamento), default=FrequenciaAgendamento.DIARIO)
    periodo_analise = Column(String(20), default="30_dias")  # Período padrão de análise
    
    # Cache e performance
    ultimo_valor = Column(Numeric(15, 2))
    ultimo_calculo = Column(DateTime)
    tempo_calculo = Column(Numeric(6, 2))
    
    # Histórico
    manter_historico = Column(Boolean, default=True)
    dias_historico = Column(Integer, default=365)
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="metricas_negocio")
    historico = relationship("HistoricoMetrica", back_populates="metrica")
    
    # Índices
    __table_args__ = (
        Index('idx_metrica_empresa', 'empresa_id'),
        Index('idx_metrica_codigo', 'codigo'),
        Index('idx_metrica_ativo', 'ativo'),
    )

# Model para histórico de métricas
class HistoricoMetrica(Base):
    __tablename__ = "historico_metricas"
    
    id = Column(Integer, primary_key=True, index=True)
    metrica_id = Column(Integer, ForeignKey("metricas_negocio.id"), nullable=False)
    
    # Dados do cálculo
    data_referencia = Column(DateTime, nullable=False)
    valor = Column(Numeric(15, 2), nullable=False)
    meta_atingida = Column(Boolean)
    
    # Contexto adicional
    parametros_calculo = Column(JSON)
    detalhes_calculo = Column(JSON)
    
    # Timestamps
    calculado_em = Column(DateTime, default=func.now())
    
    # Relacionamentos
    metrica = relationship("MetricaNegocio", back_populates="historico")
    
    # Índices
    __table_args__ = (
        Index('idx_historico_metrica_data', 'metrica_id', 'data_referencia'),
    )

# Model para exportações
class ExportacaoRelatorio(Base):
    __tablename__ = "exportacoes_relatorio"
    
    id = Column(Integer, primary_key=True, index=True)
    execucao_id = Column(Integer, ForeignKey("execucoes_relatorio.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Configuração da exportação
    formato = Column(Enum(FormatoExportacao), nullable=False)
    nome_arquivo = Column(String(200), nullable=False)
    caminho_arquivo = Column(String(500))
    
    # Configurações de formato
    configuracoes_exportacao = Column(JSON, default={})  # Opções específicas do formato
    
    # Metadados
    tamanho_arquivo = Column(Integer)  # Em bytes
    total_registros_exportados = Column(Integer)
    
    # Status
    concluida = Column(Boolean, default=False)
    erro = Column(Text)
    
    # Timestamps
    iniciada_em = Column(DateTime, default=func.now())
    concluida_em = Column(DateTime)
    
    # Relacionamentos
    execucao = relationship("ExecucaoRelatorio", back_populates="exportacoes")
    usuario = relationship("Usuario")
    
    # Índices
    __table_args__ = (
        Index('idx_exportacao_execucao', 'execucao_id'),
        Index('idx_exportacao_usuario', 'usuario_id'),
    )

# Templates de relatórios padrão do sistema
TEMPLATES_RELATORIOS_PADRAO = [
    {
        "nome": "Vendas por Período",
        "tipo": TipoRelatorio.VENDAS,
        "categoria": "performance",
        "descricao": "Análise de vendas por período com comparativos",
        "query_sql": """
            SELECT 
                DATE(created_at) as data,
                COUNT(*) as total_pedidos,
                SUM(valor_total) as receita_total,
                AVG(valor_total) as ticket_medio
            FROM pedidos 
            WHERE empresa_id = :empresa_id 
                AND created_at BETWEEN :data_inicio AND :data_fim
            GROUP BY DATE(created_at)
            ORDER BY data
        """,
        "filtros_disponiveis": [
            {"nome": "data_inicio", "tipo": "date", "obrigatorio": True},
            {"nome": "data_fim", "tipo": "date", "obrigatorio": True}
        ]
    },
    {
        "nome": "Produtos Mais Vendidos",
        "tipo": TipoRelatorio.VENDAS,
        "categoria": "produtos",
        "descricao": "Ranking de produtos por quantidade e receita",
        "query_sql": """
            SELECT 
                p.nome as produto,
                SUM(ip.quantidade) as quantidade_vendida,
                SUM(ip.quantidade * ip.preco_unitario) as receita,
                COUNT(DISTINCT pe.id) as pedidos
            FROM produtos p
            JOIN itens_pedido ip ON p.id = ip.produto_id
            JOIN pedidos pe ON ip.pedido_id = pe.id
            WHERE pe.empresa_id = :empresa_id 
                AND pe.created_at BETWEEN :data_inicio AND :data_fim
            GROUP BY p.id, p.nome
            ORDER BY quantidade_vendida DESC
            LIMIT 20
        """,
        "filtros_disponiveis": [
            {"nome": "data_inicio", "tipo": "date", "obrigatorio": True},
            {"nome": "data_fim", "tipo": "date", "obrigatorio": True}
        ]
    },
    {
        "nome": "Fluxo de Caixa",
        "tipo": TipoRelatorio.FINANCEIRO,
        "categoria": "fluxo",
        "descricao": "Fluxo de caixa detalhado com entradas e saídas",
        "query_sql": """
            SELECT 
                DATE(data_transacao) as data,
                tipo_transacao,
                SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) as entradas,
                SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) as saidas,
                SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE -valor END) as saldo_dia
            FROM transacoes_financeiras
            WHERE empresa_id = :empresa_id 
                AND data_transacao BETWEEN :data_inicio AND :data_fim
            GROUP BY DATE(data_transacao), tipo_transacao
            ORDER BY data
        """,
        "filtros_disponiveis": [
            {"nome": "data_inicio", "tipo": "date", "obrigatorio": True},
            {"nome": "data_fim", "tipo": "date", "obrigatorio": True}
        ]
    }
]

# KPIs padrão do sistema
KPIS_PADRAO = [
    {
        "nome": "Receita Total",
        "codigo": "receita_total",
        "categoria": "financeiro",
        "formula_sql": """
            SELECT COALESCE(SUM(valor_total), 0)
            FROM pedidos 
            WHERE empresa_id = :empresa_id 
                AND status = 'concluido'
                AND created_at >= :data_inicio
        """,
        "unidade": "R$",
        "formato_exibicao": "currency"
    },
    {
        "nome": "Ticket Médio",
        "codigo": "ticket_medio",
        "categoria": "vendas",
        "formula_sql": """
            SELECT COALESCE(AVG(valor_total), 0)
            FROM pedidos 
            WHERE empresa_id = :empresa_id 
                AND status = 'concluido'
                AND created_at >= :data_inicio
        """,
        "unidade": "R$",
        "formato_exibicao": "currency"
    },
    {
        "nome": "Total de Pedidos",
        "codigo": "total_pedidos",
        "categoria": "vendas",
        "formula_sql": """
            SELECT COUNT(*)
            FROM pedidos 
            WHERE empresa_id = :empresa_id 
                AND created_at >= :data_inicio
        """,
        "unidade": "un",
        "formato_exibicao": "number"
    },
    {
        "nome": "Taxa de Conversão",
        "codigo": "taxa_conversao",
        "categoria": "marketing",
        "formula_sql": """
            SELECT COALESCE(
                (COUNT(CASE WHEN status = 'concluido' THEN 1 END) * 100.0 / COUNT(*)), 
                0
            )
            FROM pedidos 
            WHERE empresa_id = :empresa_id 
                AND created_at >= :data_inicio
        """,
        "unidade": "%",
        "formato_exibicao": "percentage"
    }
]
