from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field
import json
import pandas as pd
import io
import base64
from enum import Enum
import asyncio
import hashlib
from pathlib import Path

from ..database import get_db
from ..models_relatorios import (
    ConfiguracaoRelatorio, ExecucaoRelatorio, AgendamentoRelatorio,
    CompartilhamentoRelatorio, DashboardExecutivo, WidgetDashboard,
    MetricaNegocio, HistoricoMetrica, ExportacaoRelatorio,
    TipoRelatorio, StatusRelatorio, StatusExecucao, FormatoExportacao,
    TipoVisualizacao, FrequenciaAgendamento, TipoWidget, NivelPermissao,
    TEMPLATES_RELATORIOS_PADRAO, KPIS_PADRAO
)
from ..auth import get_current_user

router = APIRouter()

# === SCHEMAS DE REQUEST/RESPONSE ===

class CreateRelatorioRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    tipo: TipoRelatorio
    categoria: Optional[str] = None
    query_sql: str = Field(..., min_length=1)
    configuracao_visual: Dict[str, Any] = {}
    filtros_disponiveis: List[Dict[str, Any]] = []
    parametros_padrao: Dict[str, Any] = {}
    cache_duracao: int = Field(default=300, ge=0)
    timeout_execucao: int = Field(default=60, ge=1)
    limite_registros: int = Field(default=10000, ge=1)
    tags: List[str] = []
    nivel_permissao: NivelPermissao = NivelPermissao.EMPRESA
    publico: bool = False

class UpdateRelatorioRequest(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    query_sql: Optional[str] = None
    configuracao_visual: Optional[Dict[str, Any]] = None
    filtros_disponiveis: Optional[List[Dict[str, Any]]] = None
    parametros_padrao: Optional[Dict[str, Any]] = None
    cache_duracao: Optional[int] = Field(None, ge=0)
    timeout_execucao: Optional[int] = Field(None, ge=1)
    limite_registros: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    nivel_permissao: Optional[NivelPermissao] = None
    publico: Optional[bool] = None
    status: Optional[StatusRelatorio] = None

class ExecutarRelatorioRequest(BaseModel):
    parametros: Dict[str, Any] = {}
    filtros: Dict[str, Any] = {}
    formato_exportacao: Optional[FormatoExportacao] = None
    usar_cache: bool = True

class CreateDashboardRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    layout_configuracao: Dict[str, Any] = {}
    configuracao_tema: Dict[str, Any] = {}
    auto_refresh: bool = True
    intervalo_refresh: int = Field(default=300, ge=30)
    publico: bool = False
    nivel_permissao: NivelPermissao = NivelPermissao.PRIVADO
    tags: List[str] = []

class CreateWidgetRequest(BaseModel):
    dashboard_id: int
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: TipoWidget
    descricao: Optional[str] = None
    configuracao_relatorio_id: Optional[int] = None
    query_customizada: Optional[str] = None
    parametros: Dict[str, Any] = {}
    posicao_x: int = Field(default=0, ge=0)
    posicao_y: int = Field(default=0, ge=0)
    largura: int = Field(default=4, ge=1, le=12)
    altura: int = Field(default=3, ge=1, le=12)
    configuracao_visual: Dict[str, Any] = {}
    tipo_visualizacao: Optional[TipoVisualizacao] = None
    auto_refresh: bool = True
    intervalo_refresh: int = Field(default=300, ge=30)

class CreateMetricaRequest(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    codigo: str = Field(..., min_length=1, max_length=50)
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    formula_sql: str = Field(..., min_length=1)
    unidade: Optional[str] = Field(None, max_length=20)
    formato_exibicao: Optional[str] = Field(None, max_length=50)
    meta_valor: Optional[float] = None
    meta_tipo: Optional[str] = None
    alerta_habilitado: bool = False
    alerta_threshold: Optional[float] = None
    frequencia_calculo: FrequenciaAgendamento = FrequenciaAgendamento.DIARIO
    periodo_analise: str = Field(default="30_dias", max_length=20)
    manter_historico: bool = True
    dias_historico: int = Field(default=365, ge=1)

class CreateAgendamentoRequest(BaseModel):
    configuracao_id: int
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    frequencia: FrequenciaAgendamento
    configuracao_cron: Optional[str] = None
    parametros_fixos: Dict[str, Any] = {}
    filtros_fixos: Dict[str, Any] = {}
    formato_exportacao: FormatoExportacao = FormatoExportacao.PDF
    emails_destinatarios: List[str] = []
    salvar_arquivo: bool = True
    pasta_destino: Optional[str] = None
    horario_execucao: str = Field(default="09:00", regex=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')

class DashboardRelatorios(BaseModel):
    total_relatorios: int
    relatorios_ativos: int
    total_execucoes_mes: int
    execucoes_hoje: int
    tempo_medio_execucao: float
    relatorios_mais_usados: List[Dict[str, Any]]
    execucoes_por_tipo: Dict[str, int]
    status_execucoes: Dict[str, int]
    atividade_recente: List[Dict[str, Any]]

# === UTILITÁRIOS ===

def validar_sql_seguranca(query: str) -> bool:
    """Valida se a query SQL é segura (não contém comandos perigosos)"""
    query_upper = query.upper().strip()
    
    # Comandos proibidos
    comandos_proibidos = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ]
    
    for comando in comandos_proibidos:
        if f' {comando} ' in f' {query_upper} ' or query_upper.startswith(comando + ' '):
            return False
    
    return True

def processar_parametros_query(query: str, parametros: Dict[str, Any]) -> str:
    """Processa parâmetros na query SQL"""
    try:
        # Adicionar parâmetros padrão se não fornecidos
        if 'data_inicio' not in parametros:
            parametros['data_inicio'] = (datetime.now() - timedelta(days=30)).date()
        if 'data_fim' not in parametros:
            parametros['data_fim'] = datetime.now().date()
        
        return query
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Erro ao processar parâmetros da query"
        )

def gerar_hash_cache(query: str, parametros: Dict[str, Any]) -> str:
    """Gera hash único para cache baseado na query e parâmetros"""
    cache_string = f"{query}{json.dumps(parametros, sort_keys=True)}"
    return hashlib.md5(cache_string.encode()).hexdigest()

# === ENDPOINTS DE CONFIGURAÇÃO DE RELATÓRIOS ===

@router.post("/configuracoes", response_model=Dict[str, Any])
async def criar_configuracao_relatorio(
    request: CreateRelatorioRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova configuração de relatório"""
    
    # Validar SQL
    if not validar_sql_seguranca(request.query_sql):
        raise HTTPException(
            status_code=400,
            detail="Query SQL contém comandos não permitidos"
        )
    
    configuracao = ConfiguracaoRelatorio(
        empresa_id=current_user.empresa_id,
        nome=request.nome,
        descricao=request.descricao,
        tipo=request.tipo,
        categoria=request.categoria,
        query_sql=request.query_sql,
        configuracao_visual=request.configuracao_visual,
        filtros_disponiveis=request.filtros_disponiveis,
        parametros_padrao=request.parametros_padrao,
        cache_duracao=request.cache_duracao,
        timeout_execucao=request.timeout_execucao,
        limite_registros=request.limite_registros,
        tags=request.tags,
        autor_id=current_user.id,
        nivel_permissao=request.nivel_permissao,
        publico=request.publico
    )
    
    db.add(configuracao)
    db.commit()
    db.refresh(configuracao)
    
    return {
        "id": configuracao.id,
        "message": "Configuração de relatório criada com sucesso"
    }

@router.get("/configuracoes", response_model=List[Dict[str, Any]])
async def listar_configuracoes(
    tipo: Optional[TipoRelatorio] = None,
    status: Optional[StatusRelatorio] = None,
    categoria: Optional[str] = None,
    publico: Optional[bool] = None,
    autor_id: Optional[int] = None,
    tags: Optional[str] = Query(None, description="Tags separadas por vírgula"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar configurações de relatórios"""
    
    query = db.query(ConfiguracaoRelatorio).filter(
        or_(
            ConfiguracaoRelatorio.empresa_id == current_user.empresa_id,
            ConfiguracaoRelatorio.publico == True
        )
    )
    
    if tipo is not None:
        query = query.filter(ConfiguracaoRelatorio.tipo == tipo)
    if status is not None:
        query = query.filter(ConfiguracaoRelatorio.status == status)
    if categoria:
        query = query.filter(ConfiguracaoRelatorio.categoria == categoria)
    if publico is not None:
        query = query.filter(ConfiguracaoRelatorio.publico == publico)
    if autor_id is not None:
        query = query.filter(ConfiguracaoRelatorio.autor_id == autor_id)
    if tags:
        tags_list = [tag.strip() for tag in tags.split(',')]
        for tag in tags_list:
            query = query.filter(ConfiguracaoRelatorio.tags.contains([tag]))
    
    configuracoes = query.order_by(desc(ConfiguracaoRelatorio.criado_em)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": config.id,
            "nome": config.nome,
            "descricao": config.descricao,
            "tipo": config.tipo.value,
            "categoria": config.categoria,
            "status": config.status.value,
            "autor_nome": config.autor.nome if config.autor else None,
            "publico": config.publico,
            "total_execucoes": config.total_execucoes,
            "ultima_execucao": config.ultima_execucao.isoformat() if config.ultima_execucao else None,
            "tempo_medio_execucao": float(config.tempo_medio_execucao) if config.tempo_medio_execucao else 0,
            "tags": config.tags,
            "criado_em": config.criado_em.isoformat()
        }
        for config in configuracoes
    ]

@router.get("/configuracoes/{config_id}", response_model=Dict[str, Any])
async def obter_configuracao(
    config_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes da configuração de relatório"""
    
    configuracao = db.query(ConfiguracaoRelatorio).filter(
        and_(
            ConfiguracaoRelatorio.id == config_id,
            or_(
                ConfiguracaoRelatorio.empresa_id == current_user.empresa_id,
                ConfiguracaoRelatorio.publico == True
            )
        )
    ).first()
    
    if not configuracao:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    return {
        "id": configuracao.id,
        "nome": configuracao.nome,
        "descricao": configuracao.descricao,
        "tipo": configuracao.tipo.value,
        "categoria": configuracao.categoria,
        "query_sql": configuracao.query_sql,
        "configuracao_visual": configuracao.configuracao_visual,
        "filtros_disponiveis": configuracao.filtros_disponiveis,
        "parametros_padrao": configuracao.parametros_padrao,
        "cache_duracao": configuracao.cache_duracao,
        "timeout_execucao": configuracao.timeout_execucao,
        "limite_registros": configuracao.limite_registros,
        "tags": configuracao.tags,
        "autor_nome": configuracao.autor.nome if configuracao.autor else None,
        "status": configuracao.status.value,
        "nivel_permissao": configuracao.nivel_permissao.value,
        "publico": configuracao.publico,
        "total_execucoes": configuracao.total_execucoes,
        "ultima_execucao": configuracao.ultima_execucao.isoformat() if configuracao.ultima_execucao else None,
        "tempo_medio_execucao": float(configuracao.tempo_medio_execucao) if configuracao.tempo_medio_execucao else 0,
        "criado_em": configuracao.criado_em.isoformat(),
        "atualizado_em": configuracao.atualizado_em.isoformat()
    }

@router.put("/configuracoes/{config_id}", response_model=Dict[str, Any])
async def atualizar_configuracao(
    config_id: int,
    request: UpdateRelatorioRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar configuração de relatório"""
    
    configuracao = db.query(ConfiguracaoRelatorio).filter(
        and_(
            ConfiguracaoRelatorio.id == config_id,
            ConfiguracaoRelatorio.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not configuracao:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Validar SQL se fornecido
    if request.query_sql and not validar_sql_seguranca(request.query_sql):
        raise HTTPException(
            status_code=400,
            detail="Query SQL contém comandos não permitidos"
        )
    
    # Atualizar campos
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(configuracao, field, value)
    
    db.commit()
    db.refresh(configuracao)
    
    return {"message": "Configuração atualizada com sucesso"}

# === ENDPOINTS DE EXECUÇÃO ===

@router.post("/configuracoes/{config_id}/executar", response_model=Dict[str, Any])
async def executar_relatorio(
    config_id: int,
    request: ExecutarRelatorioRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executar relatório"""
    
    configuracao = db.query(ConfiguracaoRelatorio).filter(
        and_(
            ConfiguracaoRelatorio.id == config_id,
            or_(
                ConfiguracaoRelatorio.empresa_id == current_user.empresa_id,
                ConfiguracaoRelatorio.publico == True
            )
        )
    ).first()
    
    if not configuracao:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    if configuracao.status != StatusRelatorio.ATIVO:
        raise HTTPException(
            status_code=400,
            detail="Relatório não está ativo"
        )
    
    # Verificar cache se solicitado
    hash_cache = None
    if request.usar_cache:
        hash_cache = gerar_hash_cache(configuracao.query_sql, request.parametros)
        execucao_cache = db.query(ExecucaoRelatorio).filter(
            and_(
                ExecucaoRelatorio.hash_cache == hash_cache,
                ExecucaoRelatorio.status == StatusExecucao.CONCLUIDO,
                ExecucaoRelatorio.criado_em > datetime.now() - timedelta(seconds=configuracao.cache_duracao)
            )
        ).first()
        
        if execucao_cache:
            return {
                "id": execucao_cache.id,
                "message": "Resultado obtido do cache",
                "cache_hit": True,
                "dados": execucao_cache.dados_resultado
            }
    
    # Criar nova execução
    execucao = ExecucaoRelatorio(
        empresa_id=current_user.empresa_id,
        configuracao_id=config_id,
        usuario_id=current_user.id,
        parametros=request.parametros,
        filtros_aplicados=request.filtros,
        hash_cache=hash_cache
    )
    
    db.add(execucao)
    db.commit()
    db.refresh(execucao)
    
    # Executar em background
    background_tasks.add_task(
        _processar_execucao_relatorio,
        execucao.id,
        configuracao.query_sql,
        request.parametros,
        request.formato_exportacao
    )
    
    return {
        "id": execucao.id,
        "message": "Execução iniciada",
        "cache_hit": False
    }

@router.get("/execucoes/{execucao_id}", response_model=Dict[str, Any])
async def obter_execucao(
    execucao_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter resultado da execução"""
    
    execucao = db.query(ExecucaoRelatorio).filter(
        and_(
            ExecucaoRelatorio.id == execucao_id,
            ExecucaoRelatorio.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not execucao:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    
    return {
        "id": execucao.id,
        "status": execucao.status.value,
        "iniciado_em": execucao.iniciado_em.isoformat(),
        "concluido_em": execucao.concluido_em.isoformat() if execucao.concluido_em else None,
        "tempo_execucao": float(execucao.tempo_execucao) if execucao.tempo_execucao else None,
        "total_registros": execucao.total_registros,
        "dados_resultado": execucao.dados_resultado,
        "arquivo_resultado": execucao.arquivo_resultado,
        "erro_detalhes": execucao.erro_detalhes
    }

# === ENDPOINTS DE DASHBOARDS ===

@router.post("/dashboards", response_model=Dict[str, Any])
async def criar_dashboard(
    request: CreateDashboardRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar dashboard executivo"""
    
    dashboard = DashboardExecutivo(
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        nome=request.nome,
        descricao=request.descricao,
        categoria=request.categoria,
        layout_configuracao=request.layout_configuracao,
        configuracao_tema=request.configuracao_tema,
        auto_refresh=request.auto_refresh,
        intervalo_refresh=request.intervalo_refresh,
        publico=request.publico,
        nivel_permissao=request.nivel_permissao,
        tags=request.tags
    )
    
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    
    return {
        "id": dashboard.id,
        "message": "Dashboard criado com sucesso"
    }

@router.get("/dashboards", response_model=List[Dict[str, Any]])
async def listar_dashboards(
    publico: Optional[bool] = None,
    categoria: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar dashboards"""
    
    query = db.query(DashboardExecutivo).filter(
        or_(
            DashboardExecutivo.empresa_id == current_user.empresa_id,
            DashboardExecutivo.publico == True
        )
    )
    
    if publico is not None:
        query = query.filter(DashboardExecutivo.publico == publico)
    if categoria:
        query = query.filter(DashboardExecutivo.categoria == categoria)
    
    dashboards = query.order_by(desc(DashboardExecutivo.criado_em)).all()
    
    return [
        {
            "id": dashboard.id,
            "nome": dashboard.nome,
            "descricao": dashboard.descricao,
            "categoria": dashboard.categoria,
            "publico": dashboard.publico,
            "total_widgets": len(dashboard.widgets),
            "total_visualizacoes": dashboard.total_visualizacoes,
            "ultima_visualizacao": dashboard.ultima_visualizacao.isoformat() if dashboard.ultima_visualizacao else None,
            "ativo": dashboard.ativo,
            "criado_em": dashboard.criado_em.isoformat()
        }
        for dashboard in dashboards
    ]

# === ENDPOINTS DE WIDGETS ===

@router.post("/widgets", response_model=Dict[str, Any])
async def criar_widget(
    request: CreateWidgetRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar widget para dashboard"""
    
    # Verificar se dashboard existe e pertence ao usuário
    dashboard = db.query(DashboardExecutivo).filter(
        and_(
            DashboardExecutivo.id == request.dashboard_id,
            DashboardExecutivo.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    
    widget = WidgetDashboard(
        dashboard_id=request.dashboard_id,
        nome=request.nome,
        tipo=request.tipo,
        descricao=request.descricao,
        configuracao_relatorio_id=request.configuracao_relatorio_id,
        query_customizada=request.query_customizada,
        parametros=request.parametros,
        posicao_x=request.posicao_x,
        posicao_y=request.posicao_y,
        largura=request.largura,
        altura=request.altura,
        configuracao_visual=request.configuracao_visual,
        tipo_visualizacao=request.tipo_visualizacao,
        auto_refresh=request.auto_refresh,
        intervalo_refresh=request.intervalo_refresh
    )
    
    db.add(widget)
    db.commit()
    db.refresh(widget)
    
    return {
        "id": widget.id,
        "message": "Widget criado com sucesso"
    }

# === ENDPOINTS DE MÉTRICAS ===

@router.post("/metricas", response_model=Dict[str, Any])
async def criar_metrica(
    request: CreateMetricaRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar métrica de negócio"""
    
    # Verificar se código já existe
    metrica_existente = db.query(MetricaNegocio).filter(
        and_(
            MetricaNegocio.empresa_id == current_user.empresa_id,
            MetricaNegocio.codigo == request.codigo
        )
    ).first()
    
    if metrica_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma métrica com este código"
        )
    
    # Validar SQL
    if not validar_sql_seguranca(request.formula_sql):
        raise HTTPException(
            status_code=400,
            detail="Fórmula SQL contém comandos não permitidos"
        )
    
    metrica = MetricaNegocio(
        empresa_id=current_user.empresa_id,
        nome=request.nome,
        codigo=request.codigo,
        descricao=request.descricao,
        categoria=request.categoria,
        formula_sql=request.formula_sql,
        unidade=request.unidade,
        formato_exibicao=request.formato_exibicao,
        meta_valor=request.meta_valor,
        meta_tipo=request.meta_tipo,
        alerta_habilitado=request.alerta_habilitado,
        alerta_threshold=request.alerta_threshold,
        frequencia_calculo=request.frequencia_calculo,
        periodo_analise=request.periodo_analise,
        manter_historico=request.manter_historico,
        dias_historico=request.dias_historico
    )
    
    db.add(metrica)
    db.commit()
    db.refresh(metrica)
    
    return {
        "id": metrica.id,
        "message": "Métrica criada com sucesso"
    }

@router.get("/metricas/calcular/{metrica_id}", response_model=Dict[str, Any])
async def calcular_metrica(
    metrica_id: int,
    data_referencia: Optional[date] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calcular valor da métrica"""
    
    metrica = db.query(MetricaNegocio).filter(
        and_(
            MetricaNegocio.id == metrica_id,
            MetricaNegocio.empresa_id == current_user.empresa_id
        )
    ).first()
    
    if not metrica:
        raise HTTPException(status_code=404, detail="Métrica não encontrada")
    
    if not data_referencia:
        data_referencia = datetime.now().date()
    
    try:
        # Preparar parâmetros
        parametros = {
            'empresa_id': current_user.empresa_id,
            'data_inicio': data_referencia - timedelta(days=30),
            'data_referencia': data_referencia
        }
        
        # Executar fórmula
        resultado = db.execute(text(metrica.formula_sql), parametros).scalar()
        valor = float(resultado) if resultado is not None else 0.0
        
        # Verificar meta
        meta_atingida = None
        if metrica.meta_valor is not None and metrica.meta_tipo:
            if metrica.meta_tipo == "maior_que":
                meta_atingida = valor > metrica.meta_valor
            elif metrica.meta_tipo == "menor_que":
                meta_atingida = valor < metrica.meta_valor
            elif metrica.meta_tipo == "igual_a":
                meta_atingida = abs(valor - metrica.meta_valor) < 0.01
        
        # Salvar no histórico se configurado
        if metrica.manter_historico:
            historico = HistoricoMetrica(
                metrica_id=metrica.id,
                data_referencia=datetime.combine(data_referencia, datetime.min.time()),
                valor=valor,
                meta_atingida=meta_atingida,
                parametros_calculo=parametros
            )
            db.add(historico)
        
        # Atualizar último valor
        metrica.ultimo_valor = valor
        metrica.ultimo_calculo = datetime.now()
        
        db.commit()
        
        return {
            "metrica_id": metrica.id,
            "valor": valor,
            "unidade": metrica.unidade,
            "meta_valor": metrica.meta_valor,
            "meta_atingida": meta_atingida,
            "data_referencia": data_referencia.isoformat(),
            "calculado_em": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular métrica: {str(e)}"
        )

# === DASHBOARD PRINCIPAL ===

@router.get("/dashboard", response_model=DashboardRelatorios)
async def obter_dashboard_relatorios(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dashboard principal de relatórios"""
    
    empresa_id = current_user.empresa_id
    hoje = datetime.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Estatísticas básicas
    total_relatorios = db.query(ConfiguracaoRelatorio).filter(
        ConfiguracaoRelatorio.empresa_id == empresa_id
    ).count()
    
    relatorios_ativos = db.query(ConfiguracaoRelatorio).filter(
        and_(
            ConfiguracaoRelatorio.empresa_id == empresa_id,
            ConfiguracaoRelatorio.status == StatusRelatorio.ATIVO
        )
    ).count()
    
    execucoes_mes = db.query(ExecucaoRelatorio).filter(
        and_(
            ExecucaoRelatorio.empresa_id == empresa_id,
            func.date(ExecucaoRelatorio.iniciado_em) >= inicio_mes
        )
    ).count()
    
    execucoes_hoje = db.query(ExecucaoRelatorio).filter(
        and_(
            ExecucaoRelatorio.empresa_id == empresa_id,
            func.date(ExecucaoRelatorio.iniciado_em) == hoje
        )
    ).count()
    
    # Tempo médio de execução
    tempo_medio = db.query(func.avg(ExecucaoRelatorio.tempo_execucao)).filter(
        and_(
            ExecucaoRelatorio.empresa_id == empresa_id,
            ExecucaoRelatorio.status == StatusExecucao.CONCLUIDO
        )
    ).scalar()
    
    tempo_medio_execucao = float(tempo_medio) if tempo_medio else 0.0
    
    # Relatórios mais usados
    relatorios_mais_usados = db.query(
        ConfiguracaoRelatorio.nome,
        ConfiguracaoRelatorio.total_execucoes
    ).filter(
        ConfiguracaoRelatorio.empresa_id == empresa_id
    ).order_by(desc(ConfiguracaoRelatorio.total_execucoes)).limit(5).all()
    
    relatorios_mais_usados_data = [
        {"nome": nome, "execucoes": execucoes}
        for nome, execucoes in relatorios_mais_usados
    ]
    
    # Execuções por tipo
    execucoes_por_tipo = {}
    for tipo in TipoRelatorio:
        count = db.query(ExecucaoRelatorio).join(ConfiguracaoRelatorio).filter(
            and_(
                ExecucaoRelatorio.empresa_id == empresa_id,
                ConfiguracaoRelatorio.tipo == tipo
            )
        ).count()
        if count > 0:
            execucoes_por_tipo[tipo.value] = count
    
    # Status das execuções
    status_execucoes = {}
    for status in StatusExecucao:
        count = db.query(ExecucaoRelatorio).filter(
            and_(
                ExecucaoRelatorio.empresa_id == empresa_id,
                ExecucaoRelatorio.status == status
            )
        ).count()
        if count > 0:
            status_execucoes[status.value] = count
    
    # Atividade recente
    execucoes_recentes = db.query(ExecucaoRelatorio).filter(
        ExecucaoRelatorio.empresa_id == empresa_id
    ).order_by(desc(ExecucaoRelatorio.iniciado_em)).limit(10).all()
    
    atividade_recente = [
        {
            "tipo": "execucao",
            "relatorio": execucao.configuracao.nome,
            "usuario": execucao.usuario.nome,
            "status": execucao.status.value,
            "timestamp": execucao.iniciado_em.isoformat()
        }
        for execucao in execucoes_recentes
    ]
    
    return DashboardRelatorios(
        total_relatorios=total_relatorios,
        relatorios_ativos=relatorios_ativos,
        total_execucoes_mes=execucoes_mes,
        execucoes_hoje=execucoes_hoje,
        tempo_medio_execucao=tempo_medio_execucao,
        relatorios_mais_usados=relatorios_mais_usados_data,
        execucoes_por_tipo=execucoes_por_tipo,
        status_execucoes=status_execucoes,
        atividade_recente=atividade_recente
    )

# === TEMPLATES E INICIALIZAÇÃO ===

@router.post("/inicializar-templates", response_model=Dict[str, Any])
async def inicializar_templates_padrao(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Inicializar templates padrão do sistema"""
    
    templates_criados = 0
    
    for template_data in TEMPLATES_RELATORIOS_PADRAO:
        # Verificar se já existe
        existente = db.query(ConfiguracaoRelatorio).filter(
            and_(
                ConfiguracaoRelatorio.empresa_id == current_user.empresa_id,
                ConfiguracaoRelatorio.nome == template_data["nome"]
            )
        ).first()
        
        if not existente:
            configuracao = ConfiguracaoRelatorio(
                empresa_id=current_user.empresa_id,
                nome=template_data["nome"],
                tipo=template_data["tipo"],
                categoria=template_data["categoria"],
                descricao=template_data["descricao"],
                query_sql=template_data["query_sql"],
                filtros_disponiveis=template_data["filtros_disponiveis"],
                autor_id=current_user.id,
                status=StatusRelatorio.ATIVO
            )
            db.add(configuracao)
            templates_criados += 1
    
    db.commit()
    
    return {
        "message": f"{templates_criados} templates padrão criados",
        "templates_criados": templates_criados
    }

@router.post("/inicializar-kpis", response_model=Dict[str, Any])
async def inicializar_kpis_padrao(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Inicializar KPIs padrão do sistema"""
    
    kpis_criados = 0
    
    for kpi_data in KPIS_PADRAO:
        # Verificar se já existe
        existente = db.query(MetricaNegocio).filter(
            and_(
                MetricaNegocio.empresa_id == current_user.empresa_id,
                MetricaNegocio.codigo == kpi_data["codigo"]
            )
        ).first()
        
        if not existente:
            metrica = MetricaNegocio(
                empresa_id=current_user.empresa_id,
                nome=kpi_data["nome"],
                codigo=kpi_data["codigo"],
                categoria=kpi_data["categoria"],
                formula_sql=kpi_data["formula_sql"],
                unidade=kpi_data["unidade"],
                formato_exibicao=kpi_data["formato_exibicao"]
            )
            db.add(metrica)
            kpis_criados += 1
    
    db.commit()
    
    return {
        "message": f"{kpis_criados} KPIs padrão criados",
        "kpis_criados": kpis_criados
    }

# === FUNÇÕES AUXILIARES ===

async def _processar_execucao_relatorio(
    execucao_id: int,
    query_sql: str,
    parametros: Dict[str, Any],
    formato_exportacao: Optional[FormatoExportacao]
):
    """Processar execução do relatório em background"""
    # Esta função seria implementada para executar relatórios
    # de forma assíncrona com tratamento de erro e cache
    pass

async def _gerar_exportacao_relatorio(
    execucao_id: int,
    formato: FormatoExportacao,
    dados: List[Dict[str, Any]]
):
    """Gerar arquivo de exportação"""
    # Esta função seria implementada para gerar arquivos
    # nos formatos PDF, Excel, CSV, etc.
    pass
