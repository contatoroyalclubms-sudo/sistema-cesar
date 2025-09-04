"""
Router para Business Intelligence
Fornece endpoints para métricas e análises em tempo real
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from ..database import get_db
from ..models import Base

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bi", tags=["Business Intelligence"])

@router.get("/metricas-tempo-real")
async def obter_metricas_tempo_real(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtém métricas de Business Intelligence em tempo real
    
    Returns:
        Dict com métricas principais: vendas_hoje, ticket_medio, crescimento, comandas_ativas
    """
    try:
        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)
        
        # Por enquanto usar dados mock até os modelos Vendas/Comandas estarem prontos
        # TODO: Implementar queries reais quando modelos estiverem disponíveis
        logger.info("Usando dados mock para BI - modelos de Vendas ainda não implementados")
        
        # Dados mock realistas para demonstração
        vendas_hoje = 23063.01
        count_vendas = 127
        vendas_ontem = 20450.33
        
        # Calcular ticket médio
        ticket_medio = vendas_hoje / count_vendas if count_vendas > 0 else 0
        
        # Calcular crescimento
        crescimento = ((vendas_hoje - vendas_ontem) / vendas_ontem * 100) if vendas_ontem > 0 else 0
        
        # Comandas ativas (mock)
        comandas_ativas = 37
        
        # Métricas adicionais
        vendas_mes = 450000
        meta_mensal = 500000
        crescimento_mes = 8.3
        produtos_vendidos = 1247
        
        return {
            "vendas_hoje": float(vendas_hoje),
            "ticket_medio": float(ticket_medio),
            "crescimento": float(crescimento),
            "comandas_ativas": comandas_ativas,
            "vendas_mes": float(vendas_mes),
            "meta_mensal": meta_mensal,
            "crescimento_mes": crescimento_mes,
            "produtos_vendidos": produtos_vendidos,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas BI: {e}")
        # Retornar dados mock em caso de erro
        return {
            "vendas_hoje": 23063.01,
            "ticket_medio": 85.50,
            "crescimento": 12.5,
            "comandas_ativas": 37,
            "vendas_mes": 450000,
            "meta_mensal": 500000,
            "crescimento_mes": 8.3,
            "produtos_vendidos": 1247,
            "timestamp": datetime.now().isoformat(),
            "status": "mock_data",
            "error": str(e)
        }

@router.get("/graficos-dados")
async def obter_dados_graficos(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtém dados para gráficos do dashboard BI
    
    Returns:
        Dict com dados para gráficos: vendas_por_hora, formas_pagamento, etc.
    """
    try:
        hoje = datetime.now().date()
        
        # Vendas por hora (últimas 12 horas)
        vendas_por_hora = {
            "labels": ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', 
                      '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'],
            "data": [150, 300, 450, 600, 1200, 1800, 1500, 900, 1100, 1400, 1600, 800]
        }
        
        # Formas de pagamento (mock - implementar query real)
        formas_pagamento = {
            "labels": ['PIX', 'Cartão Débito', 'Cartão Crédito', 'Dinheiro', 'Outros'],
            "data": [45, 25, 20, 8, 2]
        }
        
        # Produtos mais vendidos
        # Por enquanto usar dados mock - implementar query real quando modelos estiverem prontos
        produtos_mais_vendidos = {
            "labels": ['Café Expresso', 'Cappuccino', 'Açaí 300ml', 'Sanduíche Natural', 'Croissant'],
            "data": [89, 76, 65, 54, 43]
        }
        
        # Evolução das vendas (últimos 7 dias)
        evolucao_vendas = {
            "labels": ['01/09', '02/09', '03/09', '04/09', '05/09', '06/09', '07/09'],
            "data": [18500, 21000, 19800, 23500, 22000, 25000, 23063]
        }
        
        return {
            "vendas_por_hora": vendas_por_hora,
            "formas_pagamento": formas_pagamento,
            "produtos_mais_vendidos": produtos_mais_vendidos,
            "evolucao_vendas": evolucao_vendas,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter dados de gráficos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/relatorio-performance")
async def obter_relatorio_performance(
    periodo: str = "7d",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Gera relatório de performance detalhado
    
    Args:
        periodo: Período do relatório (1d, 7d, 30d, 90d)
        
    Returns:
        Dict com relatório completo de performance
    """
    try:
        # Mapear período para dias
        periodo_dias = {
            "1d": 1,
            "7d": 7, 
            "30d": 30,
            "90d": 90
        }.get(periodo, 7)
        
        data_inicio = datetime.now().date() - timedelta(days=periodo_dias)
        
        # Calcular métricas do período
        relatorio = {
            "periodo": {
                "inicio": data_inicio.isoformat(),
                "fim": datetime.now().date().isoformat(),
                "dias": periodo_dias
            },
            "vendas": {
                "total": 0,
                "media_diaria": 0,
                "melhor_dia": None,
                "pior_dia": None
            },
            "produtos": {
                "total_vendidos": 0,
                "categoria_destaque": None,
                "produto_destaque": None
            },
            "clientes": {
                "total_atendidos": 0,
                "novos_clientes": 0,
                "ticket_medio": 0
            },
            "tendencias": {
                "crescimento": 0,
                "sazonalidade": []
            }
        }
        
        # TODO: Implementar queries reais quando tabelas estiverem prontas
        # Por enquanto, retornar dados mock estruturados
        
        return relatorio
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de performance: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/alertas-bi")
async def obter_alertas_bi(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtém alertas e notificações do sistema BI
    
    Returns:
        Lista de alertas baseados em thresholds configurados
    """
    try:
        alertas = []
        
        # Verificar se vendas estão abaixo da meta
        # Verificar produtos com estoque baixo
        # Verificar anomalias nas vendas
        # etc.
        
        # Mock de alertas
        alertas = [
            {
                "tipo": "warning",
                "titulo": "Meta mensal em risco",
                "descricao": "Vendas 10% abaixo da meta do mês",
                "prioridade": "alta",
                "timestamp": datetime.now().isoformat()
            },
            {
                "tipo": "info", 
                "titulo": "Produto em destaque",
                "descricao": "Café Expresso vendeu 50% mais hoje",
                "prioridade": "media",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return {
            "alertas": alertas,
            "total": len(alertas),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas BI: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
