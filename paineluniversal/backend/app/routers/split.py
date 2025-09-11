"""
Router para Sistema de Split de Pagamentos
Endpoints para gerenciar regras, execuções e relatórios de split
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..database import get_db
from ..auth_functions import obter_usuario_atual
from ..models import Usuario, VendaPDV
from ..models_split import SplitRule, SplitExecution, ConfiguracaoSplitGlobal
from ..schemas_split import (
    SplitRuleCreate, SplitRuleUpdate, SplitRuleResponse,
    SplitExecutionCreate, SplitExecutionResponse,
    CalculoSplitRequest, CalculoSplitResponse, SplitCalculado,
    FiltroRelatorioSplit, RelatorioSplitResponse,
    ConfiguracaoSplitGlobalCreate, ConfiguracaoSplitGlobalUpdate, ConfiguracaoSplitGlobalResponse,
    DashboardSplitResponse, TotaisRelatorio, StatusRelatorio, BeneficiarioRelatorio
)
from ..services.split_service import SplitService

router = APIRouter(
    prefix="/api/split",
    tags=["split"],
    responses={404: {"description": "Not found"}},
)


# ==================== REGRAS DE SPLIT ====================

@router.post("/rules", response_model=SplitRuleResponse)
async def criar_regra_split(
    regra: SplitRuleCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Cria uma nova regra de split de pagamentos
    
    Permissões: Admin ou Gerente
    """
    # Verificar permissões
    if usuario_atual.tipo_usuario not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="Sem permissão para criar regras de split")
    
    # Criar regra
    nova_regra = SplitRule(
        **regra.dict(exclude={'dados_pagamento', 'condicoes'}),
        dados_pagamento=regra.dados_pagamento.dict() if regra.dados_pagamento else {},
        condicoes=regra.condicoes.dict() if regra.condicoes else {}
    )
    
    db.add(nova_regra)
    db.commit()
    db.refresh(nova_regra)
    
    return nova_regra


@router.get("/rules", response_model=List[SplitRuleResponse])
async def listar_regras_split(
    evento_id: Optional[int] = Query(None),
    empresa_id: Optional[int] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Lista regras de split configuradas
    """
    query = db.query(SplitRule)
    
    if evento_id:
        query = query.filter(SplitRule.evento_id == evento_id)
    
    if empresa_id:
        query = query.filter(SplitRule.empresa_id == empresa_id)
    
    if ativo is not None:
        query = query.filter(SplitRule.ativo == ativo)
    
    # Ordenar por prioridade
    regras = query.order_by(SplitRule.prioridade.asc()).all()
    
    # Adicionar estatísticas
    for regra in regras:
        execucoes = db.query(SplitExecution).filter(
            SplitExecution.rule_id == regra.id
        ).all()
        
        regra.total_execucoes = len(execucoes)
        regra.valor_total_processado = sum(e.valor_split for e in execucoes)
    
    return regras


@router.get("/rules/{rule_id}", response_model=SplitRuleResponse)
async def obter_regra_split(
    rule_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Obtém detalhes de uma regra de split específica
    """
    regra = db.query(SplitRule).filter(SplitRule.id == rule_id).first()
    
    if not regra:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    
    return regra


@router.put("/rules/{rule_id}", response_model=SplitRuleResponse)
async def atualizar_regra_split(
    rule_id: int,
    atualizacao: SplitRuleUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Atualiza uma regra de split existente
    
    Permissões: Admin ou Gerente
    """
    # Verificar permissões
    if usuario_atual.tipo_usuario not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="Sem permissão para atualizar regras de split")
    
    regra = db.query(SplitRule).filter(SplitRule.id == rule_id).first()
    
    if not regra:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    
    # Atualizar campos
    for campo, valor in atualizacao.dict(exclude_unset=True).items():
        if campo == 'dados_pagamento' and valor:
            setattr(regra, campo, valor)
        elif campo == 'condicoes' and valor:
            setattr(regra, campo, valor)
        else:
            setattr(regra, campo, valor)
    
    db.commit()
    db.refresh(regra)
    
    return regra


@router.delete("/rules/{rule_id}")
async def excluir_regra_split(
    rule_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Exclui uma regra de split (soft delete - apenas desativa)
    
    Permissões: Admin
    """
    # Verificar permissões
    if usuario_atual.tipo_usuario != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir regras")
    
    regra = db.query(SplitRule).filter(SplitRule.id == rule_id).first()
    
    if not regra:
        raise HTTPException(status_code=404, detail="Regra não encontrada")
    
    # Soft delete - apenas desativar
    regra.ativo = False
    db.commit()
    
    return {"message": "Regra desativada com sucesso"}


# ==================== CÁLCULO E EXECUÇÃO ====================

@router.post("/calculate", response_model=CalculoSplitResponse)
async def calcular_splits(
    request: CalculoSplitRequest,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Calcula os splits para uma venda sem executar
    Útil para simulação e preview
    """
    service = SplitService(db)
    
    # Verificar se venda existe
    venda = db.query(VendaPDV).filter(VendaPDV.id == request.venda_id).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    # Calcular splits
    splits = service.calcular_splits(request.venda_id)
    
    # Preparar resposta
    splits_calculados = [
        SplitCalculado(**split) for split in splits
    ]
    
    valor_total_splits = sum(s.valor for s in splits_calculados)
    
    return CalculoSplitResponse(
        venda_id=request.venda_id,
        valor_total_venda=float(venda.total),
        splits=splits_calculados,
        valor_total_splits=valor_total_splits,
        valor_organizador=float(venda.total) - valor_total_splits
    )


@router.post("/execute", response_model=List[SplitExecutionResponse])
async def executar_splits(
    request: SplitExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Executa os splits para uma venda
    Pode processar pagamentos imediatamente ou agendar para depois
    """
    service = SplitService(db)
    
    # Verificar se venda existe e não tem splits já executados
    venda = db.query(VendaPDV).filter(VendaPDV.id == request.venda_id).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    # Verificar se já existem splits para esta venda
    splits_existentes = db.query(SplitExecution).filter(
        SplitExecution.venda_id == request.venda_id
    ).first()
    
    if splits_existentes:
        raise HTTPException(status_code=400, detail="Splits já executados para esta venda")
    
    # Executar splits
    execucoes = service.executar_splits(request.venda_id)
    
    # Se solicitado, processar pagamentos em background
    if request.executar_agora:
        background_tasks.add_task(
            service.processar_pagamentos_splits,
            execucoes
        )
    
    return execucoes


@router.get("/executions", response_model=List[SplitExecutionResponse])
async def listar_execucoes(
    venda_id: Optional[int] = Query(None),
    beneficiario_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Lista execuções de split com filtros
    """
    query = db.query(SplitExecution)
    
    if venda_id:
        query = query.filter(SplitExecution.venda_id == venda_id)
    
    if beneficiario_id:
        query = query.filter(SplitExecution.beneficiario_id == beneficiario_id)
    
    if status:
        query = query.filter(SplitExecution.status == status)
    
    if data_inicio:
        query = query.filter(SplitExecution.data_execucao >= data_inicio)
    
    if data_fim:
        data_fim_datetime = datetime.combine(data_fim, datetime.max.time())
        query = query.filter(SplitExecution.data_execucao <= data_fim_datetime)
    
    # Ordenar por data decrescente
    execucoes = query.order_by(SplitExecution.data_execucao.desc()).limit(limit).offset(offset).all()
    
    return execucoes


@router.post("/executions/{execution_id}/retry")
async def reprocessar_split(
    execution_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Reprocessa um split que falhou
    
    Permissões: Admin ou Gerente
    """
    if usuario_atual.tipo_usuario not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="Sem permissão para reprocessar splits")
    
    execucao = db.query(SplitExecution).filter(SplitExecution.id == execution_id).first()
    
    if not execucao:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    
    if execucao.status not in ["erro", "pendente"]:
        raise HTTPException(status_code=400, detail="Apenas splits com erro ou pendentes podem ser reprocessados")
    
    # Reprocessar em background
    service = SplitService(db)
    background_tasks.add_task(
        service.processar_pagamentos_splits,
        [execucao]
    )
    
    return {"message": "Split agendado para reprocessamento"}


# ==================== RELATÓRIOS ====================

@router.post("/reports/detailed", response_model=RelatorioSplitResponse)
async def gerar_relatorio_detalhado(
    filtros: FiltroRelatorioSplit,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Gera relatório detalhado de splits com filtros
    """
    service = SplitService(db)
    
    relatorio = service.gerar_relatorio_splits(
        evento_id=filtros.evento_id,
        beneficiario_id=filtros.beneficiario_id,
        data_inicio=filtros.data_inicio,
        data_fim=filtros.data_fim
    )
    
    # Converter para schema
    return RelatorioSplitResponse(
        periodo=relatorio['periodo'],
        totais=TotaisRelatorio(**relatorio['totais']),
        por_status=[StatusRelatorio(**s) for s in relatorio['por_status'].values()],
        por_beneficiario=[BeneficiarioRelatorio(**b) for b in relatorio['por_beneficiario']],
        execucoes=relatorio['execucoes'][:50]  # Limitar a 50 para resposta
    )


@router.get("/dashboard", response_model=DashboardSplitResponse)
async def obter_dashboard_splits(
    periodo: str = Query("7d", regex="^(7d|30d|90d|1y)$"),
    evento_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Obtém dashboard com métricas de split
    """
    # Calcular período
    hoje = datetime.now()
    if periodo == "7d":
        data_inicio = hoje - timedelta(days=7)
    elif periodo == "30d":
        data_inicio = hoje - timedelta(days=30)
    elif periodo == "90d":
        data_inicio = hoje - timedelta(days=90)
    else:  # 1y
        data_inicio = hoje - timedelta(days=365)
    
    # Buscar execuções
    query = db.query(SplitExecution).filter(
        SplitExecution.data_execucao >= data_inicio
    )
    
    if evento_id:
        query = query.join(VendaPDV).filter(VendaPDV.evento_id == evento_id)
    
    execucoes = query.all()
    
    # Calcular métricas
    total_splits = len(execucoes)
    valor_total_processado = sum(e.valor_split for e in execucoes)
    valor_total_taxas = sum(e.valor_taxa for e in execucoes)
    valor_total_liquido = sum(e.valor_liquido for e in execucoes)
    
    # Por status
    splits_pagos = len([e for e in execucoes if e.status.value == "pago"])
    splits_pendentes = len([e for e in execucoes if e.status.value == "pendente"])
    splits_erro = len([e for e in execucoes if e.status.value == "erro"])
    
    # Top beneficiários
    beneficiarios = {}
    for execucao in execucoes:
        key = f"{execucao.beneficiario_tipo.value}:{execucao.beneficiario_id}"
        if key not in beneficiarios:
            beneficiarios[key] = {
                'nome': execucao.beneficiario_nome,
                'tipo': execucao.beneficiario_tipo.value,
                'quantidade': 0,
                'valor_bruto': 0,
                'valor_liquido': 0
            }
        
        beneficiarios[key]['quantidade'] += 1
        beneficiarios[key]['valor_bruto'] += float(execucao.valor_split)
        beneficiarios[key]['valor_liquido'] += float(execucao.valor_liquido)
    
    top_beneficiarios = sorted(
        beneficiarios.values(),
        key=lambda x: x['valor_liquido'],
        reverse=True
    )[:10]
    
    # Próximos pagamentos
    proximos_pagamentos = db.query(SplitExecution).filter(
        SplitExecution.status == "pendente"
    ).order_by(SplitExecution.data_execucao.asc()).limit(10).all()
    
    return DashboardSplitResponse(
        periodo=periodo,
        total_splits=total_splits,
        valor_total_processado=float(valor_total_processado),
        valor_total_taxas=float(valor_total_taxas),
        valor_total_liquido=float(valor_total_liquido),
        splits_pagos=splits_pagos,
        splits_pendentes=splits_pendentes,
        splits_erro=splits_erro,
        top_beneficiarios=[BeneficiarioRelatorio(**b) for b in top_beneficiarios],
        evolucao_diaria=[],  # TODO: Implementar evolução temporal
        proximos_pagamentos=proximos_pagamentos
    )


# ==================== CONFIGURAÇÃO GLOBAL ====================

@router.post("/config", response_model=ConfiguracaoSplitGlobalResponse)
async def criar_configuracao_global(
    config: ConfiguracaoSplitGlobalCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Cria configuração global de split para empresa
    
    Permissões: Admin
    """
    if usuario_atual.tipo_usuario != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem configurar split global")
    
    # Verificar se já existe configuração
    config_existente = db.query(ConfiguracaoSplitGlobal).filter(
        ConfiguracaoSplitGlobal.empresa_id == config.empresa_id
    ).first()
    
    if config_existente:
        raise HTTPException(status_code=400, detail="Configuração já existe para esta empresa")
    
    # Criar configuração
    nova_config = ConfiguracaoSplitGlobal(
        **config.dict(),
        criado_por=usuario_atual.id
    )
    
    db.add(nova_config)
    db.commit()
    db.refresh(nova_config)
    
    return nova_config


@router.get("/config/{empresa_id}", response_model=ConfiguracaoSplitGlobalResponse)
async def obter_configuracao_global(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Obtém configuração global de split da empresa
    """
    config = db.query(ConfiguracaoSplitGlobal).filter(
        ConfiguracaoSplitGlobal.empresa_id == empresa_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    return config


@router.put("/config/{empresa_id}", response_model=ConfiguracaoSplitGlobalResponse)
async def atualizar_configuracao_global(
    empresa_id: int,
    atualizacao: ConfiguracaoSplitGlobalUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """
    Atualiza configuração global de split
    
    Permissões: Admin
    """
    if usuario_atual.tipo_usuario != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem atualizar configuração")
    
    config = db.query(ConfiguracaoSplitGlobal).filter(
        ConfiguracaoSplitGlobal.empresa_id == empresa_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Atualizar campos
    for campo, valor in atualizacao.dict(exclude_unset=True).items():
        setattr(config, campo, valor)
    
    db.commit()
    db.refresh(config)
    
    return config