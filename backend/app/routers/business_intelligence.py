"""
Router para Business Intelligence e análises avançadas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
import json
import pandas as pd
from io import BytesIO
import base64

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    DashboardBI, DashboardBICreate, DashboardBIUpdate,
    RelatorioBI, RelatorioBICreate,
    MetricaBI, WidgetBI
)

router = APIRouter(
    prefix="/api/bi",
    tags=["business-intelligence"]
)

def calcular_metricas_evento(evento_id: int, db: Session) -> Dict[str, Any]:
    """Calcula métricas detalhadas de um evento"""
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        return {}
    
    # Vendas totais
    vendas_total = db.query(func.sum(models.Venda.valor_total)).filter(
        models.Venda.evento_id == evento_id
    ).scalar() or 0
    
    # Total de check-ins
    total_checkins = db.query(models.Checkin).filter(
        models.Checkin.evento_id == evento_id
    ).count()
    
    # Taxa de conversão
    total_convidados = db.query(models.ListaEvento).filter(
        models.ListaEvento.evento_id == evento_id
    ).count()
    
    taxa_conversao = (total_checkins / total_convidados * 100) if total_convidados > 0 else 0
    
    # Ticket médio
    total_vendas = db.query(models.Venda).filter(
        models.Venda.evento_id == evento_id
    ).count()
    
    ticket_medio = (vendas_total / total_vendas) if total_vendas > 0 else 0
    
    # Distribuição por lista
    distribuicao_listas = db.query(
        models.ListaEvento.tipo_lista,
        func.count(models.ListaEvento.id).label('total')
    ).filter(
        models.ListaEvento.evento_id == evento_id
    ).group_by(
        models.ListaEvento.tipo_lista
    ).all()
    
    return {
        "evento_nome": evento.nome,
        "vendas_total": float(vendas_total),
        "total_checkins": total_checkins,
        "total_convidados": total_convidados,
        "taxa_conversao": round(taxa_conversao, 2),
        "ticket_medio": round(ticket_medio, 2),
        "distribuicao_listas": {
            tipo: total for tipo, total in distribuicao_listas
        }
    }

def gerar_serie_temporal(
    modelo: Any,
    campo_data: str,
    campo_valor: str,
    periodo_dias: int,
    db: Session,
    filtros: Dict = None
) -> List[Dict[str, Any]]:
    """Gera série temporal de dados"""
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=periodo_dias)
    
    query = db.query(
        func.date(getattr(modelo, campo_data)).label('data'),
        func.sum(getattr(modelo, campo_valor)).label('valor')
    ).filter(
        getattr(modelo, campo_data) >= data_inicio,
        getattr(modelo, campo_data) <= data_fim
    )
    
    if filtros:
        for campo, valor in filtros.items():
            query = query.filter(getattr(modelo, campo) == valor)
    
    dados = query.group_by(
        func.date(getattr(modelo, campo_data))
    ).order_by('data').all()
    
    return [
        {"data": str(d.data), "valor": float(d.valor or 0)}
        for d in dados
    ]

@router.get("/dashboards/", response_model=List[DashboardBI])
def listar_dashboards(
    skip: int = 0,
    limit: int = 100,
    publico: Optional[bool] = None,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista dashboards disponíveis"""
    query = db.query(models.DashboardBI).filter(
        or_(
            models.DashboardBI.criado_por_id == current_user.id,
            models.DashboardBI.publico == True
        )
    )
    
    if publico is not None:
        query = query.filter(models.DashboardBI.publico == publico)
    
    if categoria:
        query = query.filter(models.DashboardBI.categoria == categoria)
    
    dashboards = query.order_by(
        models.DashboardBI.criado_em.desc()
    ).offset(skip).limit(limit).all()
    
    return dashboards

@router.get("/dashboards/{dashboard_id}", response_model=DashboardBI)
def obter_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém um dashboard específico com dados atualizados"""
    dashboard = db.query(models.DashboardBI).filter(
        models.DashboardBI.id == dashboard_id
    ).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    
    # Verificar permissão
    if not dashboard.publico and dashboard.criado_por_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para acessar este dashboard")
    
    # Atualizar métricas dos widgets
    if dashboard.widgets:
        widgets = json.loads(dashboard.widgets) if isinstance(dashboard.widgets, str) else dashboard.widgets
        for widget in widgets:
            widget["dados_atualizados"] = obter_dados_widget(widget, db)
        dashboard.widgets = widgets
    
    return dashboard

def obter_dados_widget(widget: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Obtém dados atualizados para um widget"""
    tipo = widget.get("tipo")
    configuracao = widget.get("configuracao", {})
    
    if tipo == "vendas_total":
        periodo = configuracao.get("periodo_dias", 30)
        data_inicio = datetime.now() - timedelta(days=periodo)
        
        valor = db.query(func.sum(models.Venda.valor_total)).filter(
            models.Venda.criado_em >= data_inicio
        ).scalar() or 0
        
        return {"valor": float(valor), "periodo": periodo}
    
    elif tipo == "checkins_hoje":
        hoje = datetime.now().date()
        total = db.query(models.Checkin).filter(
            func.date(models.Checkin.data_checkin) == hoje
        ).count()
        
        return {"total": total, "data": str(hoje)}
    
    elif tipo == "grafico_vendas":
        periodo = configuracao.get("periodo_dias", 7)
        return gerar_serie_temporal(
            models.Venda,
            "criado_em",
            "valor_total",
            periodo,
            db
        )
    
    elif tipo == "top_promoters":
        limite = configuracao.get("limite", 5)
        periodo = configuracao.get("periodo_dias", 30)
        data_inicio = datetime.now() - timedelta(days=periodo)
        
        top = db.query(
            models.Usuario.nome,
            func.count(models.ListaEvento.id).label('total')
        ).join(
            models.ListaEvento,
            models.Usuario.id == models.ListaEvento.promotor_id
        ).filter(
            models.ListaEvento.criado_em >= data_inicio
        ).group_by(
            models.Usuario.id
        ).order_by(
            func.count(models.ListaEvento.id).desc()
        ).limit(limite).all()
        
        return [{"nome": nome, "total": total} for nome, total in top]
    
    return {}

@router.post("/dashboards/", response_model=DashboardBI)
def criar_dashboard(
    dashboard: DashboardBICreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo dashboard"""
    widgets = json.dumps(dashboard.widgets) if dashboard.widgets else None
    filtros = json.dumps(dashboard.filtros) if dashboard.filtros else None
    
    db_dashboard = models.DashboardBI(
        **dashboard.model_dump(exclude={'widgets', 'filtros'}),
        widgets=widgets,
        filtros=filtros,
        criado_por_id=current_user.id
    )
    
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    
    return db_dashboard

@router.put("/dashboards/{dashboard_id}", response_model=DashboardBI)
def atualizar_dashboard(
    dashboard_id: int,
    dashboard_update: DashboardBIUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um dashboard existente"""
    dashboard = db.query(models.DashboardBI).filter(
        models.DashboardBI.id == dashboard_id,
        models.DashboardBI.criado_por_id == current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=404,
            detail="Dashboard não encontrado ou sem permissão"
        )
    
    update_data = dashboard_update.model_dump(exclude_unset=True)
    
    if 'widgets' in update_data and update_data['widgets']:
        update_data['widgets'] = json.dumps(update_data['widgets'])
    
    if 'filtros' in update_data and update_data['filtros']:
        update_data['filtros'] = json.dumps(update_data['filtros'])
    
    for key, value in update_data.items():
        setattr(dashboard, key, value)
    
    dashboard.atualizado_em = datetime.now()
    db.commit()
    db.refresh(dashboard)
    
    return dashboard

@router.delete("/dashboards/{dashboard_id}")
def deletar_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deleta um dashboard"""
    dashboard = db.query(models.DashboardBI).filter(
        models.DashboardBI.id == dashboard_id,
        models.DashboardBI.criado_por_id == current_user.id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=404,
            detail="Dashboard não encontrado ou sem permissão"
        )
    
    db.delete(dashboard)
    db.commit()
    
    return {"message": "Dashboard deletado com sucesso"}

# ====== RELATÓRIOS ======

@router.get("/relatorios/", response_model=List[RelatorioBI])
def listar_relatorios(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    periodo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista relatórios disponíveis"""
    query = db.query(models.RelatorioBI).filter(
        or_(
            models.RelatorioBI.criado_por_id == current_user.id,
            models.RelatorioBI.publico == True
        )
    )
    
    if tipo:
        query = query.filter(models.RelatorioBI.tipo == tipo)
    
    if periodo:
        query = query.filter(models.RelatorioBI.periodo == periodo)
    
    relatorios = query.order_by(
        models.RelatorioBI.criado_em.desc()
    ).offset(skip).limit(limit).all()
    
    return relatorios

@router.post("/relatorios/gerar")
def gerar_relatorio(
    relatorio: RelatorioBICreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera um novo relatório"""
    tipo = relatorio.tipo
    filtros = relatorio.filtros or {}
    
    dados = {}
    
    if tipo == "vendas":
        dados = gerar_relatorio_vendas(filtros, db)
    elif tipo == "checkins":
        dados = gerar_relatorio_checkins(filtros, db)
    elif tipo == "financeiro":
        dados = gerar_relatorio_financeiro(filtros, db)
    elif tipo == "promotores":
        dados = gerar_relatorio_promotores(filtros, db)
    elif tipo == "eventos":
        dados = gerar_relatorio_eventos(filtros, db)
    
    # Salvar relatório
    db_relatorio = models.RelatorioBI(
        nome=relatorio.nome,
        descricao=relatorio.descricao,
        tipo=tipo,
        periodo=relatorio.periodo,
        filtros=json.dumps(filtros),
        dados=json.dumps(dados),
        formato=relatorio.formato or "json",
        publico=relatorio.publico or False,
        criado_por_id=current_user.id
    )
    
    db.add(db_relatorio)
    db.commit()
    
    # Formatar resposta baseado no formato solicitado
    if relatorio.formato == "excel":
        # Converter para Excel
        df = pd.DataFrame(dados.get("detalhes", []))
        output = BytesIO()
        df.to_excel(output, index=False)
        excel_data = base64.b64encode(output.getvalue()).decode()
        
        return {
            "id": db_relatorio.id,
            "formato": "excel",
            "dados": excel_data,
            "filename": f"relatorio_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    
    return {
        "id": db_relatorio.id,
        "formato": "json",
        "dados": dados
    }

def gerar_relatorio_vendas(filtros: Dict, db: Session) -> Dict[str, Any]:
    """Gera relatório de vendas"""
    query = db.query(models.Venda)
    
    if "evento_id" in filtros:
        query = query.filter(models.Venda.evento_id == filtros["evento_id"])
    
    if "data_inicio" in filtros:
        query = query.filter(models.Venda.criado_em >= filtros["data_inicio"])
    
    if "data_fim" in filtros:
        query = query.filter(models.Venda.criado_em <= filtros["data_fim"])
    
    vendas = query.all()
    
    total_vendas = sum(v.valor_total for v in vendas)
    ticket_medio = (total_vendas / len(vendas)) if vendas else 0
    
    # Vendas por dia
    vendas_por_dia = {}
    for venda in vendas:
        data = venda.criado_em.date()
        if data not in vendas_por_dia:
            vendas_por_dia[data] = 0
        vendas_por_dia[data] += venda.valor_total
    
    return {
        "resumo": {
            "total_vendas": float(total_vendas),
            "quantidade_vendas": len(vendas),
            "ticket_medio": round(ticket_medio, 2)
        },
        "vendas_por_dia": [
            {"data": str(data), "valor": float(valor)}
            for data, valor in sorted(vendas_por_dia.items())
        ],
        "detalhes": [
            {
                "id": v.id,
                "data": v.criado_em.isoformat(),
                "valor": float(v.valor_total),
                "evento_id": v.evento_id
            }
            for v in vendas[:100]  # Limitar detalhes
        ]
    }

def gerar_relatorio_checkins(filtros: Dict, db: Session) -> Dict[str, Any]:
    """Gera relatório de check-ins"""
    query = db.query(models.Checkin)
    
    if "evento_id" in filtros:
        query = query.filter(models.Checkin.evento_id == filtros["evento_id"])
    
    if "data_inicio" in filtros:
        query = query.filter(models.Checkin.data_checkin >= filtros["data_inicio"])
    
    if "data_fim" in filtros:
        query = query.filter(models.Checkin.data_checkin <= filtros["data_fim"])
    
    checkins = query.all()
    
    # Check-ins por hora
    checkins_por_hora = {}
    for checkin in checkins:
        hora = checkin.data_checkin.hour
        if hora not in checkins_por_hora:
            checkins_por_hora[hora] = 0
        checkins_por_hora[hora] += 1
    
    return {
        "resumo": {
            "total_checkins": len(checkins),
            "media_por_hora": len(checkins) / 24 if checkins else 0
        },
        "distribuicao_horaria": [
            {"hora": hora, "quantidade": qtd}
            for hora, qtd in sorted(checkins_por_hora.items())
        ]
    }

def gerar_relatorio_financeiro(filtros: Dict, db: Session) -> Dict[str, Any]:
    """Gera relatório financeiro"""
    # Implementação simplificada
    periodo_dias = filtros.get("periodo_dias", 30)
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Receitas
    receitas = db.query(func.sum(models.Venda.valor_total)).filter(
        models.Venda.criado_em >= data_inicio
    ).scalar() or 0
    
    # Custos (exemplo simplificado)
    custos = receitas * 0.3  # 30% de custo estimado
    
    return {
        "resumo": {
            "receita_total": float(receitas),
            "custo_total": float(custos),
            "lucro_liquido": float(receitas - custos),
            "margem_lucro": round(((receitas - custos) / receitas * 100) if receitas > 0 else 0, 2)
        }
    }

def gerar_relatorio_promotores(filtros: Dict, db: Session) -> Dict[str, Any]:
    """Gera relatório de performance de promotores"""
    periodo_dias = filtros.get("periodo_dias", 30)
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Top promotores
    promotores = db.query(
        models.Usuario.nome,
        func.count(models.ListaEvento.id).label('convites'),
        func.count(models.Checkin.id).label('checkins')
    ).outerjoin(
        models.ListaEvento,
        models.Usuario.id == models.ListaEvento.promotor_id
    ).outerjoin(
        models.Checkin,
        models.ListaEvento.id == models.Checkin.lista_id
    ).filter(
        models.ListaEvento.criado_em >= data_inicio
    ).group_by(
        models.Usuario.id
    ).all()
    
    return {
        "promotores": [
            {
                "nome": p.nome,
                "convites": p.convites,
                "checkins": p.checkins,
                "taxa_conversao": round((p.checkins / p.convites * 100) if p.convites > 0 else 0, 2)
            }
            for p in promotores
        ]
    }

def gerar_relatorio_eventos(filtros: Dict, db: Session) -> Dict[str, Any]:
    """Gera relatório de eventos"""
    query = db.query(models.Evento)
    
    if "ativo" in filtros:
        query = query.filter(models.Evento.ativo == filtros["ativo"])
    
    eventos = query.all()
    
    relatorio_eventos = []
    for evento in eventos:
        metricas = calcular_metricas_evento(evento.id, db)
        relatorio_eventos.append({
            "id": evento.id,
            "nome": evento.nome,
            "data": evento.data_evento.isoformat() if evento.data_evento else None,
            **metricas
        })
    
    return {
        "total_eventos": len(eventos),
        "eventos": relatorio_eventos
    }

@router.get("/metricas/tempo-real")
def obter_metricas_tempo_real(
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém métricas em tempo real"""
    hoje = datetime.now().date()
    
    metricas = {
        "timestamp": datetime.now().isoformat(),
        "hoje": {
            "vendas": 0,
            "checkins": 0,
            "novos_clientes": 0
        },
        "ultimas_24h": {
            "vendas": 0,
            "checkins": 0
        }
    }
    
    # Filtros base
    filtro_hoje = func.date(models.Venda.criado_em) == hoje
    filtro_24h = models.Venda.criado_em >= datetime.now() - timedelta(hours=24)
    
    if evento_id:
        # Métricas específicas do evento
        metricas["hoje"]["vendas"] = db.query(func.sum(models.Venda.valor_total)).filter(
            models.Venda.evento_id == evento_id,
            filtro_hoje
        ).scalar() or 0
        
        metricas["hoje"]["checkins"] = db.query(models.Checkin).filter(
            models.Checkin.evento_id == evento_id,
            func.date(models.Checkin.data_checkin) == hoje
        ).count()
    else:
        # Métricas gerais
        metricas["hoje"]["vendas"] = db.query(func.sum(models.Venda.valor_total)).filter(
            filtro_hoje
        ).scalar() or 0
        
        metricas["hoje"]["checkins"] = db.query(models.Checkin).filter(
            func.date(models.Checkin.data_checkin) == hoje
        ).count()
    
    metricas["hoje"]["novos_clientes"] = db.query(models.ClienteEvento).filter(
        func.date(models.ClienteEvento.criado_em) == hoje
    ).count()
    
    # Últimas 24 horas
    metricas["ultimas_24h"]["vendas"] = db.query(func.sum(models.Venda.valor_total)).filter(
        filtro_24h
    ).scalar() or 0
    
    metricas["ultimas_24h"]["checkins"] = db.query(models.Checkin).filter(
        models.Checkin.data_checkin >= datetime.now() - timedelta(hours=24)
    ).count()
    
    return metricas

@router.get("/analise-preditiva/{evento_id}")
def obter_analise_preditiva(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Realiza análise preditiva para um evento"""
    evento = db.query(models.Evento).filter(
        models.Evento.id == evento_id
    ).first()
    
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Análise histórica de eventos similares
    eventos_similares = db.query(models.Evento).filter(
        models.Evento.id != evento_id,
        models.Evento.ativo == False  # Eventos finalizados
    ).limit(10).all()
    
    if not eventos_similares:
        return {
            "previsao_publico": "Dados insuficientes",
            "previsao_vendas": "Dados insuficientes"
        }
    
    # Calcular médias
    media_checkins = sum(
        db.query(models.Checkin).filter(
            models.Checkin.evento_id == e.id
        ).count()
        for e in eventos_similares
    ) / len(eventos_similares)
    
    media_vendas = sum(
        db.query(func.sum(models.Venda.valor_total)).filter(
            models.Venda.evento_id == e.id
        ).scalar() or 0
        for e in eventos_similares
    ) / len(eventos_similares)
    
    # Ajustar baseado no progresso atual
    checkins_atuais = db.query(models.Checkin).filter(
        models.Checkin.evento_id == evento_id
    ).count()
    
    vendas_atuais = db.query(func.sum(models.Venda.valor_total)).filter(
        models.Venda.evento_id == evento_id
    ).scalar() or 0
    
    # Previsões simples
    fator_ajuste = 1.1  # 10% de margem otimista
    
    return {
        "evento": evento.nome,
        "analise_baseada_em": f"{len(eventos_similares)} eventos similares",
        "previsoes": {
            "publico_estimado": int(media_checkins * fator_ajuste),
            "publico_atual": checkins_atuais,
            "vendas_estimadas": round(media_vendas * fator_ajuste, 2),
            "vendas_atuais": float(vendas_atuais),
            "probabilidade_sucesso": min(95, round((checkins_atuais / media_checkins * 100) if media_checkins > 0 else 50))
        },
        "recomendacoes": gerar_recomendacoes(checkins_atuais, media_checkins, vendas_atuais, media_vendas)
    }

def gerar_recomendacoes(checkins_atuais: int, media_checkins: float, vendas_atuais: float, media_vendas: float) -> List[str]:
    """Gera recomendações baseadas na análise"""
    recomendacoes = []
    
    if checkins_atuais < media_checkins * 0.7:
        recomendacoes.append("Intensificar divulgação - público abaixo da média esperada")
    
    if vendas_atuais < media_vendas * 0.7:
        recomendacoes.append("Revisar estratégia de vendas - receita abaixo do esperado")
    
    if checkins_atuais > media_checkins * 1.2:
        recomendacoes.append("Preparar estrutura adicional - público acima do esperado")
    
    if not recomendacoes:
        recomendacoes.append("Evento dentro das expectativas - manter estratégia atual")
    
    return recomendacoes