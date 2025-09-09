"""
Service para Analytics e Business Intelligence
Análises avançadas, métricas e insights
"""

from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract, desc
from collections import defaultdict
import logging
import numpy as np
from dataclasses import dataclass
import json

from ..models import (
    VendaPDV, ItemVendaPDV, ClienteEvento as Cliente, Produto, CategoriaProduto as Categoria,
    Usuario, Evento, Checkin, Empresa
)
from ..models_fidelidade import (
    ClienteFidelidade, MovimentoPontos, ResgateFidelidade,
    ConquistaPrograma, DesafioFidelidade
)

logger = logging.getLogger(__name__)


@dataclass
class MetricResult:
    """Resultado de uma métrica"""
    value: Any
    change: float
    change_type: str  # 'increase', 'decrease', 'stable'
    period: str
    confidence: float = 0.0


@dataclass
class InsightResult:
    """Resultado de um insight"""
    type: str  # 'opportunity', 'alert', 'trend'
    title: str
    description: str
    impact: Optional[str] = None
    action: Optional[str] = None
    priority: str = 'medium'  # 'low', 'medium', 'high'


class AnalyticsService:
    """Service principal para analytics e BI"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================= KPIs PRINCIPAIS =========================
    
    def get_kpis(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int] = None
    ) -> Dict[str, MetricResult]:
        """Obtém KPIs principais do período"""
        kpis = {}
        
        # Período anterior para comparação
        period_days = (end_date - start_date).days
        previous_start = start_date - timedelta(days=period_days)
        previous_end = start_date - timedelta(days=1)
        
        # Receita Total
        kpis['revenue'] = self._calculate_revenue(
            start_date, end_date, previous_start, previous_end, empresa_id
        )
        
        # Total de Vendas
        kpis['sales'] = self._calculate_sales(
            start_date, end_date, previous_start, previous_end, empresa_id
        )
        
        # Clientes Ativos
        kpis['active_customers'] = self._calculate_active_customers(
            start_date, end_date, previous_start, previous_end, empresa_id
        )
        
        # Ticket Médio
        kpis['average_ticket'] = self._calculate_average_ticket(
            start_date, end_date, previous_start, previous_end, empresa_id
        )
        
        # Taxa de Conversão
        kpis['conversion_rate'] = self._calculate_conversion_rate(
            start_date, end_date, previous_start, previous_end, empresa_id
        )
        
        # NPS Score
        kpis['nps_score'] = self._calculate_nps_score(
            start_date, end_date, previous_start, previous_end, empresa_id
        )
        
        # Taxa de Retenção
        kpis['retention_rate'] = self._calculate_retention_rate(
            start_date, end_date, empresa_id
        )
        
        # Margem de Lucro
        kpis['profit_margin'] = self._calculate_profit_margin(
            start_date, end_date, previous_start, previous_end, empresa_id
        )
        
        return kpis
    
    def _calculate_revenue(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_start: datetime,
        prev_end: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula receita total"""
        query = self.db.query(func.sum(VendaPDV.total)).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        current_revenue = query.scalar() or 0
        
        # Período anterior
        query_prev = self.db.query(func.sum(VendaPDV.total)).filter(
            VendaPDV.data_venda >= prev_start,
            VendaPDV.data_venda <= prev_end,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query_prev = query_prev.filter(VendaPDV.empresa_id == empresa_id)
        
        previous_revenue = query_prev.scalar() or 0
        
        # Calcular mudança
        change = 0
        if previous_revenue > 0:
            change = ((current_revenue - previous_revenue) / previous_revenue) * 100
        
        return MetricResult(
            value=float(current_revenue),
            change=round(change, 2),
            change_type='increase' if change > 0 else 'decrease' if change < 0 else 'stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    def _calculate_sales(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_start: datetime,
        prev_end: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula total de vendas"""
        query = self.db.query(func.count(VendaPDV.id)).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        current_sales = query.scalar() or 0
        
        # Período anterior
        query_prev = self.db.query(func.count(VendaPDV.id)).filter(
            VendaPDV.data_venda >= prev_start,
            VendaPDV.data_venda <= prev_end,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query_prev = query_prev.filter(VendaPDV.empresa_id == empresa_id)
        
        previous_sales = query_prev.scalar() or 0
        
        # Calcular mudança
        change = 0
        if previous_sales > 0:
            change = ((current_sales - previous_sales) / previous_sales) * 100
        
        return MetricResult(
            value=current_sales,
            change=round(change, 2),
            change_type='increase' if change > 0 else 'decrease' if change < 0 else 'stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    def _calculate_active_customers(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_start: datetime,
        prev_end: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula clientes ativos"""
        query = self.db.query(func.count(func.distinct(VendaPDV.cliente_id))).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        current_customers = query.scalar() or 0
        
        # Período anterior
        query_prev = self.db.query(func.count(func.distinct(VendaPDV.cliente_id))).filter(
            VendaPDV.data_venda >= prev_start,
            VendaPDV.data_venda <= prev_end,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query_prev = query_prev.filter(VendaPDV.empresa_id == empresa_id)
        
        previous_customers = query_prev.scalar() or 0
        
        # Calcular mudança
        change = 0
        if previous_customers > 0:
            change = ((current_customers - previous_customers) / previous_customers) * 100
        
        return MetricResult(
            value=current_customers,
            change=round(change, 2),
            change_type='increase' if change > 0 else 'decrease' if change < 0 else 'stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    def _calculate_average_ticket(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_start: datetime,
        prev_end: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula ticket médio"""
        query = self.db.query(func.avg(VendaPDV.total)).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        current_ticket = query.scalar() or 0
        
        # Período anterior
        query_prev = self.db.query(func.avg(VendaPDV.total)).filter(
            VendaPDV.data_venda >= prev_start,
            VendaPDV.data_venda <= prev_end,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query_prev = query_prev.filter(VendaPDV.empresa_id == empresa_id)
        
        previous_ticket = query_prev.scalar() or 0
        
        # Calcular mudança
        change = 0
        if previous_ticket > 0:
            change = ((current_ticket - previous_ticket) / previous_ticket) * 100
        
        return MetricResult(
            value=float(current_ticket),
            change=round(change, 2),
            change_type='increase' if change > 0 else 'decrease' if change < 0 else 'stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    def _calculate_conversion_rate(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_start: datetime,
        prev_end: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula taxa de conversão"""
        # Para este exemplo, vamos simular com dados mockados
        # Em produção, isso viria de analytics de website
        current_rate = 3.2
        previous_rate = 2.8
        
        change = ((current_rate - previous_rate) / previous_rate) * 100 if previous_rate > 0 else 0
        
        return MetricResult(
            value=current_rate,
            change=round(change, 2),
            change_type='increase' if change > 0 else 'decrease' if change < 0 else 'stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    def _calculate_nps_score(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_start: datetime,
        prev_end: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula NPS Score"""
        # Simulação - em produção viria de pesquisas de satisfação
        current_nps = 72
        previous_nps = 68
        
        change = current_nps - previous_nps
        
        return MetricResult(
            value=current_nps,
            change=change,
            change_type='increase' if change > 0 else 'decrease' if change < 0 else 'stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    def _calculate_retention_rate(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula taxa de retenção"""
        # Clientes que compraram no período atual
        current_customers = self.db.query(func.distinct(VendaPDV.cliente_id)).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            current_customers = current_customers.filter(VendaPDV.empresa_id == empresa_id)
        
        current_ids = [c[0] for c in current_customers.all() if c[0]]
        
        # Clientes que compraram no período anterior
        previous_customers = self.db.query(func.distinct(VendaPDV.cliente_id)).filter(
            VendaPDV.data_venda < start_date,
            VendaPDV.data_venda >= start_date - timedelta(days=30),
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            previous_customers = previous_customers.filter(VendaPDV.empresa_id == empresa_id)
        
        previous_ids = [c[0] for c in previous_customers.all() if c[0]]
        
        # Calcular retenção
        if previous_ids:
            retained = len(set(current_ids) & set(previous_ids))
            retention_rate = (retained / len(previous_ids)) * 100
        else:
            retention_rate = 0
        
        return MetricResult(
            value=round(retention_rate, 2),
            change=0,
            change_type='stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    def _calculate_profit_margin(
        self,
        start_date: datetime,
        end_date: datetime,
        prev_start: datetime,
        prev_end: datetime,
        empresa_id: Optional[int]
    ) -> MetricResult:
        """Calcula margem de lucro"""
        # Simulação - em produção viria do custo dos produtos
        current_margin = 18.5
        previous_margin = 17.2
        
        change = current_margin - previous_margin
        
        return MetricResult(
            value=current_margin,
            change=round(change, 2),
            change_type='increase' if change > 0 else 'decrease' if change < 0 else 'stable',
            period=f"{start_date.date()} to {end_date.date()}"
        )
    
    # ========================= ANÁLISES DE VENDAS =========================
    
    def get_sales_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int] = None
    ) -> Dict:
        """Análise completa de vendas"""
        return {
            'revenue_timeline': self._get_revenue_timeline(start_date, end_date, empresa_id),
            'sales_by_category': self._get_sales_by_category(start_date, end_date, empresa_id),
            'top_products': self._get_top_products(start_date, end_date, empresa_id),
            'sales_by_hour': self._get_sales_by_hour(start_date, end_date, empresa_id),
            'sales_by_weekday': self._get_sales_by_weekday(start_date, end_date, empresa_id),
            'payment_methods': self._get_payment_methods(start_date, end_date, empresa_id),
            'geographic_distribution': self._get_geographic_distribution(start_date, end_date, empresa_id)
        }
    
    def _get_revenue_timeline(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Timeline de receita"""
        query = self.db.query(
            func.date(VendaPDV.data_venda).label('date'),
            func.sum(VendaPDV.total).label('revenue'),
            func.count(VendaPDV.id).label('sales'),
            func.avg(VendaPDV.total).label('avg_ticket')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by(func.date(VendaPDV.data_venda)).order_by('date')
        
        results = []
        for row in query.all():
            results.append({
                'date': row.date.isoformat() if row.date else None,
                'revenue': float(row.revenue) if row.revenue else 0,
                'sales': row.sales,
                'avg_ticket': float(row.avg_ticket) if row.avg_ticket else 0
            })
        
        return results
    
    def _get_sales_by_category(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Vendas por categoria"""
        query = self.db.query(
            Categoria.nome.label('category'),
            func.count(ItemVendaPDV.id).label('items_sold'),
            func.sum(ItemVendaPDV.subtotal).label('revenue')
        ).join(
            Produto, ItemVendaPDV.produto_id == Produto.id
        ).join(
            Categoria, Produto.categoria_id == Categoria.id
        ).join(
            VendaPDV, ItemVendaPDV.venda_id == VendaPDV.id
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by(Categoria.nome).order_by(desc('revenue'))
        
        results = []
        total_revenue = 0
        
        for row in query.all():
            revenue = float(row.revenue) if row.revenue else 0
            total_revenue += revenue
            results.append({
                'category': row.category,
                'items_sold': row.items_sold,
                'revenue': revenue
            })
        
        # Adicionar percentual
        for result in results:
            result['percentage'] = round((result['revenue'] / total_revenue * 100), 2) if total_revenue > 0 else 0
        
        return results
    
    def _get_top_products(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int],
        limit: int = 10
    ) -> List[Dict]:
        """Top produtos mais vendidos"""
        query = self.db.query(
            Produto.nome.label('product'),
            func.sum(ItemVendaPDV.quantidade).label('quantity'),
            func.sum(ItemVendaPDV.subtotal).label('revenue'),
            func.count(func.distinct(VendaPDV.id)).label('sales_count')
        ).join(
            ItemVendaPDV, Produto.id == ItemVendaPDV.produto_id
        ).join(
            VendaPDV, ItemVendaPDV.venda_id == VendaPDV.id
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by(Produto.nome).order_by(desc('revenue')).limit(limit)
        
        results = []
        for row in query.all():
            results.append({
                'product': row.product,
                'quantity': int(row.quantity) if row.quantity else 0,
                'revenue': float(row.revenue) if row.revenue else 0,
                'sales_count': row.sales_count,
                'avg_price': float(row.revenue / row.quantity) if row.quantity else 0
            })
        
        return results
    
    def _get_sales_by_hour(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Vendas por hora do dia"""
        query = self.db.query(
            extract('hour', VendaPDV.data_venda).label('hour'),
            func.count(VendaPDV.id).label('sales'),
            func.sum(VendaPDV.total).label('revenue')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by('hour').order_by('hour')
        
        results = []
        for row in query.all():
            results.append({
                'hour': int(row.hour),
                'sales': row.sales,
                'revenue': float(row.revenue) if row.revenue else 0
            })
        
        return results
    
    def _get_sales_by_weekday(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Vendas por dia da semana"""
        # Nota: extract('dow', ...) retorna 0=domingo, 1=segunda, etc.
        query = self.db.query(
            extract('dow', VendaPDV.data_venda).label('weekday'),
            func.count(VendaPDV.id).label('sales'),
            func.sum(VendaPDV.total).label('revenue')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by('weekday').order_by('weekday')
        
        weekdays = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        results = []
        
        for row in query.all():
            results.append({
                'weekday': weekdays[int(row.weekday)],
                'weekday_num': int(row.weekday),
                'sales': row.sales,
                'revenue': float(row.revenue) if row.revenue else 0
            })
        
        return results
    
    def _get_payment_methods(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Métodos de pagamento utilizados"""
        query = self.db.query(
            VendaPDV.forma_pagamento.label('method'),
            func.count(VendaPDV.id).label('count'),
            func.sum(VendaPDV.total).label('total')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by(VendaPDV.forma_pagamento).order_by(desc('total'))
        
        results = []
        for row in query.all():
            results.append({
                'method': row.method or 'Não informado',
                'count': row.count,
                'total': float(row.total) if row.total else 0
            })
        
        return results
    
    def _get_geographic_distribution(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Distribuição geográfica das vendas"""
        # Simplificado - em produção usaria dados de endereço
        return [
            {'region': 'Sul', 'sales': 450, 'revenue': 45000},
            {'region': 'Sudeste', 'sales': 680, 'revenue': 72000},
            {'region': 'Centro-Oeste', 'sales': 120, 'revenue': 12000},
            {'region': 'Nordeste', 'sales': 234, 'revenue': 25000},
            {'region': 'Norte', 'sales': 89, 'revenue': 8900}
        ]
    
    # ========================= ANÁLISES DE CLIENTES =========================
    
    def get_customer_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int] = None
    ) -> Dict:
        """Análise completa de clientes"""
        return {
            'segmentation': self._get_customer_segmentation(start_date, end_date, empresa_id),
            'lifetime_value': self._get_customer_lifetime_value(start_date, end_date, empresa_id),
            'churn_analysis': self._get_churn_analysis(start_date, end_date, empresa_id),
            'acquisition_channels': self._get_acquisition_channels(start_date, end_date, empresa_id),
            'purchase_frequency': self._get_purchase_frequency(start_date, end_date, empresa_id),
            'customer_journey': self._get_customer_journey(start_date, end_date, empresa_id)
        }
    
    def _get_customer_segmentation(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Segmentação de clientes RFM"""
        # RFM: Recency, Frequency, Monetary
        subquery = self.db.query(
            VendaPDV.cliente_id,
            func.max(VendaPDV.data_venda).label('last_purchase'),
            func.count(VendaPDV.id).label('frequency'),
            func.sum(VendaPDV.total).label('monetary')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada',
            VendaPDV.cliente_id.isnot(None)
        )
        
        if empresa_id:
            subquery = subquery.filter(VendaPDV.empresa_id == empresa_id)
        
        subquery = subquery.group_by(VendaPDV.cliente_id).subquery()
        
        # Classificar clientes
        segments = {
            'champions': {'count': 0, 'revenue': 0},
            'loyal': {'count': 0, 'revenue': 0},
            'potential': {'count': 0, 'revenue': 0},
            'new': {'count': 0, 'revenue': 0},
            'at_risk': {'count': 0, 'revenue': 0},
            'lost': {'count': 0, 'revenue': 0}
        }
        
        results = self.db.query(subquery).all()
        now = datetime.now()
        
        for customer in results:
            days_since_purchase = (now - customer.last_purchase).days if customer.last_purchase else 999
            frequency = customer.frequency or 0
            monetary = float(customer.monetary) if customer.monetary else 0
            
            # Classificação simplificada
            if days_since_purchase <= 30 and frequency >= 5 and monetary >= 1000:
                segment = 'champions'
            elif days_since_purchase <= 60 and frequency >= 3:
                segment = 'loyal'
            elif days_since_purchase <= 30 and frequency == 1:
                segment = 'new'
            elif days_since_purchase <= 90 and monetary >= 500:
                segment = 'potential'
            elif days_since_purchase > 90 and days_since_purchase <= 180:
                segment = 'at_risk'
            else:
                segment = 'lost'
            
            segments[segment]['count'] += 1
            segments[segment]['revenue'] += monetary
        
        return [
            {
                'segment': seg,
                'count': data['count'],
                'revenue': data['revenue'],
                'avg_value': data['revenue'] / data['count'] if data['count'] > 0 else 0
            }
            for seg, data in segments.items()
        ]
    
    def _get_customer_lifetime_value(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> Dict:
        """Calcula Customer Lifetime Value"""
        query = self.db.query(
            func.avg(VendaPDV.total).label('avg_order_value'),
            func.count(func.distinct(VendaPDV.cliente_id)).label('total_customers'),
            func.count(VendaPDV.id).label('total_orders')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada',
            VendaPDV.cliente_id.isnot(None)
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        result = query.first()
        
        if result and result.total_customers > 0:
            avg_order_value = float(result.avg_order_value) if result.avg_order_value else 0
            purchase_frequency = result.total_orders / result.total_customers
            
            # CLV simplificado = AOV × Frequência × Tempo de vida médio (assumindo 2 anos)
            clv = avg_order_value * purchase_frequency * 24  # 24 meses
            
            return {
                'average_clv': clv,
                'avg_order_value': avg_order_value,
                'purchase_frequency': purchase_frequency,
                'total_customers': result.total_customers
            }
        
        return {
            'average_clv': 0,
            'avg_order_value': 0,
            'purchase_frequency': 0,
            'total_customers': 0
        }
    
    def _get_churn_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> Dict:
        """Análise de churn"""
        # Clientes ativos no período
        active_query = self.db.query(func.distinct(VendaPDV.cliente_id)).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada',
            VendaPDV.cliente_id.isnot(None)
        )
        
        if empresa_id:
            active_query = active_query.filter(VendaPDV.empresa_id == empresa_id)
        
        active_customers = set([c[0] for c in active_query.all()])
        
        # Clientes do período anterior
        prev_start = start_date - timedelta(days=90)
        prev_end = start_date - timedelta(days=1)
        
        previous_query = self.db.query(func.distinct(VendaPDV.cliente_id)).filter(
            VendaPDV.data_venda >= prev_start,
            VendaPDV.data_venda <= prev_end,
            VendaPDV.status != 'cancelada',
            VendaPDV.cliente_id.isnot(None)
        )
        
        if empresa_id:
            previous_query = previous_query.filter(VendaPDV.empresa_id == empresa_id)
        
        previous_customers = set([c[0] for c in previous_query.all()])
        
        # Calcular métricas
        retained = len(active_customers & previous_customers)
        churned = len(previous_customers - active_customers)
        new = len(active_customers - previous_customers)
        
        churn_rate = (churned / len(previous_customers) * 100) if previous_customers else 0
        retention_rate = (retained / len(previous_customers) * 100) if previous_customers else 0
        
        return {
            'churn_rate': round(churn_rate, 2),
            'retention_rate': round(retention_rate, 2),
            'churned_customers': churned,
            'retained_customers': retained,
            'new_customers': new,
            'total_customers': len(active_customers)
        }
    
    def _get_acquisition_channels(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Canais de aquisição de clientes"""
        # Simulação - em produção viria de tracking de marketing
        return [
            {'channel': 'Orgânico', 'customers': 234, 'conversion': 3.2, 'revenue': 45000},
            {'channel': 'Google Ads', 'customers': 156, 'conversion': 2.8, 'revenue': 32000},
            {'channel': 'Facebook', 'customers': 189, 'conversion': 2.5, 'revenue': 28000},
            {'channel': 'Instagram', 'customers': 267, 'conversion': 4.1, 'revenue': 52000},
            {'channel': 'Email', 'customers': 89, 'conversion': 5.2, 'revenue': 18000},
            {'channel': 'Indicação', 'customers': 123, 'conversion': 8.7, 'revenue': 38000}
        ]
    
    def _get_purchase_frequency(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> Dict:
        """Frequência de compra dos clientes"""
        query = self.db.query(
            VendaPDV.cliente_id,
            func.count(VendaPDV.id).label('purchase_count')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada',
            VendaPDV.cliente_id.isnot(None)
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by(VendaPDV.cliente_id)
        
        frequency_distribution = defaultdict(int)
        for row in query.all():
            if row.purchase_count == 1:
                frequency_distribution['one_time'] += 1
            elif row.purchase_count == 2:
                frequency_distribution['two_times'] += 1
            elif row.purchase_count <= 5:
                frequency_distribution['occasional'] += 1
            else:
                frequency_distribution['frequent'] += 1
        
        return dict(frequency_distribution)
    
    def _get_customer_journey(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[Dict]:
        """Jornada do cliente - funil de conversão"""
        # Simulação de funil
        total_visitors = 15000  # Viria de analytics
        
        # Cadastros
        registered_query = self.db.query(func.count(Cliente.id)).filter(
            Cliente.data_cadastro >= start_date,
            Cliente.data_cadastro <= end_date
        )
        registered = registered_query.scalar() or 250
        
        # Primeira compra
        first_purchase_query = self.db.query(
            func.count(func.distinct(VendaPDV.cliente_id))
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            first_purchase_query = first_purchase_query.filter(VendaPDV.empresa_id == empresa_id)
        
        first_purchase = first_purchase_query.scalar() or 100
        
        return [
            {
                'stage': 'Visitantes',
                'count': total_visitors,
                'conversion_rate': 100
            },
            {
                'stage': 'Cadastrados',
                'count': registered,
                'conversion_rate': (registered / total_visitors * 100) if total_visitors > 0 else 0
            },
            {
                'stage': 'Primeira Compra',
                'count': first_purchase,
                'conversion_rate': (first_purchase / registered * 100) if registered > 0 else 0
            }
        ]
    
    # ========================= INSIGHTS E PREDIÇÕES =========================
    
    def get_insights(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int] = None
    ) -> List[InsightResult]:
        """Gera insights automatizados"""
        insights = []
        
        # Análise de tendências
        trend_insights = self._analyze_trends(start_date, end_date, empresa_id)
        insights.extend(trend_insights)
        
        # Alertas de estoque
        stock_insights = self._analyze_stock_alerts(empresa_id)
        insights.extend(stock_insights)
        
        # Oportunidades de cross-sell
        cross_sell_insights = self._analyze_cross_sell_opportunities(start_date, end_date, empresa_id)
        insights.extend(cross_sell_insights)
        
        # Análise de sazonalidade
        seasonal_insights = self._analyze_seasonality(start_date, end_date, empresa_id)
        insights.extend(seasonal_insights)
        
        return insights
    
    def _analyze_trends(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[InsightResult]:
        """Analisa tendências"""
        insights = []
        
        # Tendência de receita
        revenue_data = self._get_revenue_timeline(start_date, end_date, empresa_id)
        if len(revenue_data) >= 7:
            revenues = [d['revenue'] for d in revenue_data[-7:]]
            trend = np.polyfit(range(len(revenues)), revenues, 1)[0]
            
            if trend > 100:
                insights.append(InsightResult(
                    type='trend',
                    title='Tendência de crescimento detectada',
                    description=f'Receita crescendo R$ {trend:.2f} por dia nos últimos 7 dias',
                    priority='high'
                ))
            elif trend < -100:
                insights.append(InsightResult(
                    type='alert',
                    title='Tendência de queda detectada',
                    description=f'Receita caindo R$ {abs(trend):.2f} por dia nos últimos 7 dias',
                    action='Revisar estratégia de vendas',
                    priority='high'
                ))
        
        return insights
    
    def _analyze_stock_alerts(
        self,
        empresa_id: Optional[int]
    ) -> List[InsightResult]:
        """Analisa alertas de estoque"""
        insights = []
        
        # Produtos com estoque baixo (simulação)
        low_stock_products = [
            {'name': 'iPhone 14', 'stock': 3, 'daily_sales': 4},
            {'name': 'AirPods', 'stock': 8, 'daily_sales': 5}
        ]
        
        for product in low_stock_products:
            days_remaining = product['stock'] / product['daily_sales'] if product['daily_sales'] > 0 else 0
            
            if days_remaining < 2:
                insights.append(InsightResult(
                    type='alert',
                    title=f'Estoque crítico: {product["name"]}',
                    description=f'Apenas {product["stock"]} unidades restantes, média de {product["daily_sales"]} vendas/dia',
                    action='Reabastecer urgentemente',
                    priority='high'
                ))
        
        return insights
    
    def _analyze_cross_sell_opportunities(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[InsightResult]:
        """Analisa oportunidades de cross-sell"""
        insights = []
        
        # Análise de produtos frequentemente comprados juntos (simulação)
        insights.append(InsightResult(
            type='opportunity',
            title='Oportunidade de cross-sell detectada',
            description='87% dos clientes que compram iPhone também compram capinha',
            action='Criar bundle com desconto',
            impact='Aumento estimado de R$ 15.000 em receita mensal',
            priority='medium'
        ))
        
        return insights
    
    def _analyze_seasonality(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int]
    ) -> List[InsightResult]:
        """Analisa padrões sazonais"""
        insights = []
        
        # Análise por dia da semana
        weekday_data = self._get_sales_by_weekday(start_date, end_date, empresa_id)
        if weekday_data:
            best_day = max(weekday_data, key=lambda x: x['revenue'])
            worst_day = min(weekday_data, key=lambda x: x['revenue'])
            
            if best_day['revenue'] > worst_day['revenue'] * 1.5:
                insights.append(InsightResult(
                    type='opportunity',
                    title=f'Pico de vendas às {best_day["weekday"]}s',
                    description=f'Vendas 50% maiores que {worst_day["weekday"]}',
                    action=f'Aumentar estoque e equipe às {best_day["weekday"]}s',
                    priority='medium'
                ))
        
        return insights
    
    # ========================= EXPORTAÇÃO =========================
    
    def export_dashboard_data(
        self,
        start_date: datetime,
        end_date: datetime,
        empresa_id: Optional[int] = None,
        format: str = 'json'
    ) -> Any:
        """Exporta dados do dashboard"""
        data = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'kpis': self.get_kpis(start_date, end_date, empresa_id),
            'sales': self.get_sales_analysis(start_date, end_date, empresa_id),
            'customers': self.get_customer_analysis(start_date, end_date, empresa_id),
            'insights': [
                {
                    'type': i.type,
                    'title': i.title,
                    'description': i.description,
                    'action': i.action,
                    'priority': i.priority
                }
                for i in self.get_insights(start_date, end_date, empresa_id)
            ]
        }
        
        if format == 'json':
            return json.dumps(data, default=str, indent=2)
        elif format == 'dict':
            return data
        else:
            raise ValueError(f"Formato não suportado: {format}")


class PredictiveAnalytics:
    """Análises preditivas usando ML simples"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def predict_next_week_revenue(
        self,
        empresa_id: Optional[int] = None
    ) -> Dict:
        """Prevê receita da próxima semana"""
        # Buscar dados históricos
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        query = self.db.query(
            func.date(VendaPDV.data_venda).label('date'),
            func.sum(VendaPDV.total).label('revenue')
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.data_venda <= end_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by(func.date(VendaPDV.data_venda))
        
        # Coletar dados
        revenues = []
        for row in query.all():
            revenues.append(float(row.revenue) if row.revenue else 0)
        
        if len(revenues) < 7:
            return {
                'predicted_revenue': 0,
                'confidence': 0,
                'error_margin': 0
            }
        
        # Média móvel simples para previsão
        recent_avg = np.mean(revenues[-7:])
        all_avg = np.mean(revenues)
        
        # Tendência linear
        x = np.arange(len(revenues))
        z = np.polyfit(x, revenues, 1)
        trend = z[0]
        
        # Previsão = média recente + tendência * 7 dias
        predicted = recent_avg + (trend * 7)
        
        # Confiança baseada na variabilidade
        std_dev = np.std(revenues)
        confidence = max(0, min(100, 100 - (std_dev / all_avg * 100))) if all_avg > 0 else 0
        
        return {
            'predicted_revenue': round(predicted * 7, 2),  # Para 7 dias
            'confidence': round(confidence, 2),
            'error_margin': round(std_dev * 2, 2),
            'trend': 'growing' if trend > 0 else 'declining' if trend < 0 else 'stable'
        }
    
    def identify_best_customers_to_target(
        self,
        empresa_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Identifica melhores clientes para targetar"""
        # Buscar clientes com padrão de compra
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        query = self.db.query(
            Cliente.id,
            Cliente.nome,
            Cliente.email,
            func.count(VendaPDV.id).label('purchase_count'),
            func.sum(VendaPDV.total).label('total_spent'),
            func.max(VendaPDV.data_venda).label('last_purchase')
        ).join(
            VendaPDV, Cliente.id == VendaPDV.cliente_id
        ).filter(
            VendaPDV.data_venda >= start_date,
            VendaPDV.status != 'cancelada'
        )
        
        if empresa_id:
            query = query.filter(VendaPDV.empresa_id == empresa_id)
        
        query = query.group_by(Cliente.id, Cliente.nome, Cliente.email)
        
        customers = []
        for row in query.all():
            days_since_purchase = (end_date - row.last_purchase).days if row.last_purchase else 999
            avg_days_between = days_since_purchase / row.purchase_count if row.purchase_count > 1 else 30
            
            # Score baseado em RFM
            recency_score = max(0, 100 - days_since_purchase)
            frequency_score = min(100, row.purchase_count * 10)
            monetary_score = min(100, float(row.total_spent) / 100)
            
            total_score = (recency_score + frequency_score + monetary_score) / 3
            
            # Identificar se está na hora de comprar novamente
            expected_next_purchase = row.last_purchase + timedelta(days=avg_days_between)
            is_due = expected_next_purchase <= end_date
            
            if is_due and total_score > 50:
                customers.append({
                    'customer_id': row.id,
                    'name': row.nome,
                    'email': row.email,
                    'score': round(total_score, 2),
                    'last_purchase_days': days_since_purchase,
                    'total_spent': float(row.total_spent),
                    'purchase_count': row.purchase_count,
                    'recommendation': 'Send personalized offer'
                })
        
        # Ordenar por score e retornar top
        customers.sort(key=lambda x: x['score'], reverse=True)
        return customers[:limit]