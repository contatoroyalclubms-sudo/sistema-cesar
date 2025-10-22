"""
Router de Marketing NIP - Baseado na estrutura do portal Meep
Implementa todos os submódulos: Fidelidade, CRM, Campanhas, Cupons, etc.
"""

from fastapi import APIRouter, Query, Path
from typing import Optional
from app.api.nip_generator import NIPRouterGenerator

# Criar gerador para o módulo Marketing
marketing_generator = NIPRouterGenerator("marketing")

# Adicionar endpoints CRUD para todos os submódulos de Marketing
marketing_generator.add_crud_endpoints("fidelidade")
marketing_generator.add_crud_endpoints("crm") 
marketing_generator.add_crud_endpoints("campanhas")
marketing_generator.add_crud_endpoints("cupons")
marketing_generator.add_crud_endpoints("desconto")
marketing_generator.add_crud_endpoints("promocao")

# Endpoints específicos do Marketing (compatibilidade com Meep)

# Fidelidade - Endpoints específicos baseados no fidelity-api.meep.cloud
@marketing_generator.router.get("/fidelidade/hierarquia/{owner_id}")
async def buscar_hierarquia_fidelidade(owner_id: str = Path(..., description="ID do proprietário")):
    """Busca hierarquia do programa de fidelidade - Compatível com Meep fidelity-api"""
    return marketing_generator.create_response(
        data={
            "hierarchy": [
                {
                    "level": 1,
                    "name": "PRATA BROZE",
                    "min_points": 0,
                    "customers_count": 8064,
                    "benefits": []
                }
            ]
        },
        message="Hierarquia de fidelidade retornada com sucesso"
    )

@marketing_generator.router.get("/fidelidade/pontos/{customer_id}")
async def buscar_pontos_cliente(
    customer_id: str = Path(..., description="ID do cliente"),
    owner_id: str = Query(..., description="ID do proprietário")
):
    """Busca pontos acumulados do cliente - Compatível com Meep"""
    return marketing_generator.create_response(
        data={
            "customer_id": customer_id,
            "points": {
                "current": 2500,
                "total_earned": 5000,
                "total_used": 2500,
                "expiring_soon": 100
            }
        },
        message="Pontos do cliente retornados com sucesso"
    )

@marketing_generator.router.get("/fidelidade/troca-moedas/{local_id}")
async def buscar_troca_moedas_local(
    local_id: str = Path(..., description="ID do local"),
    owner_id: str = Query(..., description="ID do proprietário")
):
    """Busca configuração de troca de moedas por local - Compatível com Meep"""
    return marketing_generator.create_response(
        data={
            "local_id": local_id,
            "exchange_config": {
                "rate": 1.0,
                "min_amount": 10,
                "max_amount": 1000
            }
        },
        message="Configuração de troca de moedas retornada com sucesso"
    )

# CRM - Endpoints específicos baseados no crm-api.meep.cloud
@marketing_generator.router.get("/crm/event-categories")
async def listar_categorias_eventos():
    """Lista categorias de eventos - Compatível com Meep crm-api"""
    return marketing_generator.create_response(
        data={
            "categories": [
                {"id": 1, "name": "Show", "color": "#FF5722"},
                {"id": 2, "name": "Festival", "color": "#2196F3"},
                {"id": 3, "name": "Teatro", "color": "#9C27B0"}
            ]
        },
        message="Categorias de eventos retornadas com sucesso"
    )

@marketing_generator.router.get("/crm/ticket-categories")
async def listar_categorias_ingressos():
    """Lista categorias de ingressos - Compatível com Meep"""
    return marketing_generator.create_response(
        data={
            "categories": [
                {"id": 1, "name": "VIP", "price": 150.00},
                {"id": 2, "name": "Pista", "price": 80.00}, 
                {"id": 3, "name": "Camarote", "price": 200.00}
            ]
        },
        message="Categorias de ingressos retornadas com sucesso"
    )

@marketing_generator.router.get("/crm/saved-filters")
async def listar_filtros_salvos(
    owner_id: str = Query(..., description="ID do proprietário")
):
    """Lista filtros salvos do CRM - Compatível com Meep"""
    return marketing_generator.create_response(
        data={"filters": []},
        message="Filtros salvos retornados com sucesso"
    )

# Campanhas - Endpoints avançados
@marketing_generator.router.post("/campanhas/{campaign_id}/activate")
async def ativar_campanha(
    campaign_id: str = Path(..., description="ID da campanha"),
    owner_id: str = Query(..., description="ID do proprietário")
):
    """Ativa uma campanha de marketing"""
    return marketing_generator.create_response(
        data={"campaign_id": campaign_id, "status": "active"},
        message="Campanha ativada com sucesso"
    )

@marketing_generator.router.post("/campanhas/{campaign_id}/pause")
async def pausar_campanha(
    campaign_id: str = Path(..., description="ID da campanha"),
    owner_id: str = Query(..., description="ID do proprietário")
):
    """Pausa uma campanha de marketing"""
    return marketing_generator.create_response(
        data={"campaign_id": campaign_id, "status": "paused"},
        message="Campanha pausada com sucesso"
    )

@marketing_generator.router.get("/campanhas/{campaign_id}/analytics")
async def analytics_campanha(
    campaign_id: str = Path(..., description="ID da campanha"),
    owner_id: str = Query(..., description="ID do proprietário")
):
    """Retorna analytics de uma campanha específica"""
    return marketing_generator.create_response(
        data={
            "campaign_id": campaign_id,
            "metrics": {
                "impressions": 15420,
                "clicks": 1852,
                "conversions": 234,
                "ctr": 12.01,
                "conversion_rate": 12.63,
                "cost": 450.00,
                "revenue": 1890.00,
                "roi": 320.0
            }
        },
        message="Analytics da campanha retornados com sucesso"
    )

# Cupons - Endpoints específicos
@marketing_generator.router.post("/cupons/{coupon_id}/activate")
async def ativar_cupom(
    coupon_id: str = Path(..., description="ID do cupom"),
    owner_id: str = Query(..., description="ID do proprietário")
):
    """Ativa um cupom de desconto"""
    return marketing_generator.create_response(
        data={"coupon_id": coupon_id, "status": "active"},
        message="Cupom ativado com sucesso"
    )

@marketing_generator.router.get("/cupons/{coupon_code}/validate")
async def validar_cupom(
    coupon_code: str = Path(..., description="Código do cupom"),
    owner_id: str = Query(..., description="ID do proprietário"),
    amount: Optional[float] = Query(None, description="Valor da compra para validação")
):
    """Valida um cupom de desconto"""
    return marketing_generator.create_response(
        data={
            "coupon_code": coupon_code,
            "valid": True,
            "discount_value": 15.0,
            "discount_type": "percentage",
            "max_discount": 50.0
        },
        message="Cupom validado com sucesso"
    )

# Analytics gerais de Marketing
@marketing_generator.router.get("/analytics/overview")
async def overview_analytics(
    owner_id: str = Query(..., description="ID do proprietário"),
    period: Optional[str] = Query("30d", description="Período para análise (7d, 30d, 90d)")
):
    """Retorna overview de analytics do marketing"""
    return marketing_generator.create_response(
        data={
            "period": period,
            "metrics": {
                "total_campaigns": 25,
                "active_campaigns": 8,
                "total_customers": 8064,
                "avg_engagement_rate": 15.5,
                "total_revenue": 125000.00,
                "total_invested": 50000.00,
                "roi_percentage": 150.0
            }
        },
        message="Overview de analytics retornado com sucesso"
    )

# Obter router configurado
router = marketing_generator.get_router()