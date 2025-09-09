"""
Router para Analytics e Business Intelligence
"""

from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
import json
import csv
import io

from ..database import get_db
from ..auth import get_current_user
from ..schemas import Usuario
from ..services.analytics_service import AnalyticsService, PredictiveAnalytics

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


# ========================= KPIs =========================

@router.get("/kpis")
async def get_kpis(
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém KPIs principais"""
    # Definir período padrão se não fornecido
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Converter para datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    kpis = service.get_kpis(start_datetime, end_datetime, empresa_id)
    
    # Formatar resposta
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "kpis": {
            key: {
                "value": metric.value,
                "change": metric.change,
                "change_type": metric.change_type,
                "period": metric.period
            }
            for key, metric in kpis.items()
        }
    }


@router.get("/dashboard")
async def get_dashboard_data(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém todos os dados do dashboard"""
    # Definir período padrão
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    
    # Coletar todos os dados
    kpis = service.get_kpis(start_datetime, end_datetime, empresa_id)
    sales = service.get_sales_analysis(start_datetime, end_datetime, empresa_id)
    customers = service.get_customer_analysis(start_datetime, end_datetime, empresa_id)
    insights = service.get_insights(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "kpis": {
            key: {
                "value": metric.value,
                "change": metric.change,
                "change_type": metric.change_type
            }
            for key, metric in kpis.items()
        },
        "sales": sales,
        "customers": customers,
        "insights": [
            {
                "type": insight.type,
                "title": insight.title,
                "description": insight.description,
                "action": insight.action,
                "impact": insight.impact,
                "priority": insight.priority
            }
            for insight in insights
        ]
    }


# ========================= ANÁLISES DE VENDAS =========================

@router.get("/sales")
async def get_sales_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Análise detalhada de vendas"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    sales_data = service.get_sales_analysis(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "data": sales_data
    }


@router.get("/sales/timeline")
async def get_sales_timeline(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    granularity: str = Query("day", description="day, week, month"),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Timeline de vendas"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    timeline_data = service._get_revenue_timeline(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "granularity": granularity,
        "data": timeline_data
    }


@router.get("/sales/products")
async def get_product_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(10, le=100),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Análise de produtos mais vendidos"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    products = service._get_top_products(start_datetime, end_datetime, empresa_id, limit)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "products": products
    }


@router.get("/sales/categories")
async def get_category_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Análise de vendas por categoria"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    categories = service._get_sales_by_category(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "categories": categories
    }


# ========================= ANÁLISES DE CLIENTES =========================

@router.get("/customers")
async def get_customer_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Análise detalhada de clientes"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    customer_data = service.get_customer_analysis(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "data": customer_data
    }


@router.get("/customers/segmentation")
async def get_customer_segmentation(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Segmentação RFM de clientes"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=90)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    segmentation = service._get_customer_segmentation(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "segments": segmentation
    }


@router.get("/customers/lifetime-value")
async def get_customer_lifetime_value(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Customer Lifetime Value"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    clv = service._get_customer_lifetime_value(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "clv": clv
    }


@router.get("/customers/churn")
async def get_churn_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Análise de churn"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=90)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    churn = service._get_churn_analysis(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "churn": churn
    }


# ========================= INSIGHTS E PREDIÇÕES =========================

@router.get("/insights")
async def get_insights(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Insights automatizados"""
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    insights = service.get_insights(start_datetime, end_datetime, empresa_id)
    
    return {
        "success": True,
        "insights": [
            {
                "type": insight.type,
                "title": insight.title,
                "description": insight.description,
                "action": insight.action,
                "impact": insight.impact,
                "priority": insight.priority
            }
            for insight in insights
        ]
    }


@router.get("/predictions/revenue")
async def predict_revenue(
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Previsão de receita"""
    if current_user.tipo_usuario not in ["admin", "empresa"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    predictive = PredictiveAnalytics(db)
    prediction = predictive.predict_next_week_revenue(empresa_id)
    
    return {
        "success": True,
        "prediction": prediction
    }


@router.get("/predictions/customers")
async def predict_customer_targets(
    limit: int = Query(10, le=50),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Identifica clientes para targetar"""
    if current_user.tipo_usuario not in ["admin", "empresa"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    predictive = PredictiveAnalytics(db)
    targets = predictive.identify_best_customers_to_target(empresa_id, limit)
    
    return {
        "success": True,
        "targets": targets
    }


# ========================= EXPORTAÇÃO =========================

@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", description="json or csv"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Exporta dados de analytics"""
    if current_user.tipo_usuario not in ["admin", "empresa"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    service = AnalyticsService(db)
    
    if format == "json":
        data = service.export_dashboard_data(start_datetime, end_datetime, empresa_id, "dict")
        
        return StreamingResponse(
            io.StringIO(json.dumps(data, default=str, indent=2)),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_{start_date}_{end_date}.json"
            }
        )
    
    elif format == "csv":
        # Gerar CSV com KPIs principais
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Métrica", "Valor", "Mudança (%)", "Período"])
        
        # KPIs
        kpis = service.get_kpis(start_datetime, end_datetime, empresa_id)
        for key, metric in kpis.items():
            writer.writerow([
                key.replace("_", " ").title(),
                metric.value,
                metric.change,
                f"{start_date} to {end_date}"
            ])
        
        # Vendas por categoria
        writer.writerow([])
        writer.writerow(["Categoria", "Receita", "Percentual"])
        
        sales_data = service.get_sales_analysis(start_datetime, end_datetime, empresa_id)
        for category in sales_data.get("sales_by_category", []):
            writer.writerow([
                category["category"],
                category["revenue"],
                category.get("percentage", 0)
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_{start_date}_{end_date}.csv"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="Formato não suportado")


# ========================= TEMPO REAL =========================

@router.get("/realtime/stats")
async def get_realtime_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Estatísticas em tempo real"""
    from ..models import VendaPDV, Cliente, Checkin
    
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Vendas de hoje
    today_sales = db.query(func.count(VendaPDV.id)).filter(
        VendaPDV.data_venda >= today_start,
        VendaPDV.data_venda <= today_end,
        VendaPDV.status != 'cancelada'
    ).scalar() or 0
    
    today_revenue = db.query(func.sum(VendaPDV.total)).filter(
        VendaPDV.data_venda >= today_start,
        VendaPDV.data_venda <= today_end,
        VendaPDV.status != 'cancelada'
    ).scalar() or 0
    
    # Clientes ativos hoje
    active_customers = db.query(func.count(func.distinct(VendaPDV.cliente_id))).filter(
        VendaPDV.data_venda >= today_start,
        VendaPDV.data_venda <= today_end
    ).scalar() or 0
    
    # Check-ins hoje (se aplicável)
    today_checkins = db.query(func.count(Checkin.id)).filter(
        Checkin.data_checkin >= today_start,
        Checkin.data_checkin <= today_end
    ).scalar() or 0
    
    # Última venda
    last_sale = db.query(VendaPDV).order_by(VendaPDV.data_venda.desc()).first()
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "today": {
            "sales": today_sales,
            "revenue": float(today_revenue) if today_revenue else 0,
            "active_customers": active_customers,
            "checkins": today_checkins,
            "last_sale": {
                "time": last_sale.data_venda.isoformat() if last_sale else None,
                "value": float(last_sale.total) if last_sale else 0
            }
        }
    }