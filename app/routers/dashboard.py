from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/api/dashboard", tags=["DASHBOARD"])

# Schemas para Dashboard
class SaldoResponse(BaseModel):
    saldo_disponivel: float
    saldo_a_liberar: float
    saldo_retido: float
    total_movimentacoes: float

class MovimentacaoPorForma(BaseModel):
    forma_pagamento: str
    valor: float
    quantidade: int
    percentual: float

class DetalhamentoComandasResponse(BaseModel):
    total_comandas: int
    comandas_fechadas: int
    comandas_abertas: int
    com_taxa_servico: int
    valor_taxa_servico: float
    sem_taxa_servico: int
    comandas_sem_consumo: int
    total_pessoas: int

class TicketMedioResponse(BaseModel):
    ticket_medio_conta: float
    ticket_medio_pessoa: float
    tickets_zero: int

# DASHBOARD GERAL - Igual ao Meep

@router.get("/geral/resumo", response_model=dict)
async def dashboard_geral_resumo(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    caixa_id: Optional[int] = Query(None, description="ID do caixa para filtro")
):
    """Dashboard Geral - Resumo completo igual ao Meep"""
    return {
        "status": "success",
        "data": {
            "periodo": f"{data_inicio or 'início'} até {data_fim or 'hoje'}",
            "caixa_filtro": caixa_id,
            "resumo_gerado": datetime.now().isoformat()
        }
    }

@router.get("/geral/saldos", response_model=SaldoResponse)
async def dashboard_geral_saldos():
    """Dashboard Geral - Saldos (disponível, a liberar, retido)"""
    return SaldoResponse(
        saldo_disponivel=2061.56,
        saldo_a_liberar=0.00,
        saldo_retido=148.07,
        total_movimentacoes=28984.03
    )

@router.get("/geral/movimentacoes-por-forma", response_model=List[MovimentacaoPorForma])
async def dashboard_geral_movimentacoes_forma():
    """Dashboard Geral - Movimentações por forma de pagamento"""
    return [
        MovimentacaoPorForma(forma_pagamento="Crédito", valor=0.00, quantidade=0, percentual=0.0),
        MovimentacaoPorForma(forma_pagamento="Débito", valor=0.00, quantidade=0, percentual=0.0),
        MovimentacaoPorForma(forma_pagamento="Dinheiro", valor=24561.19, quantidade=187, percentual=84.7),
        MovimentacaoPorForma(forma_pagamento="PIX", valor=0.00, quantidade=0, percentual=0.0),
        MovimentacaoPorForma(forma_pagamento="Voucher", valor=0.00, quantidade=0, percentual=0.0),
        MovimentacaoPorForma(forma_pagamento="Outros", valor=4422.84, quantidade=69, percentual=15.3)
    ]

@router.get("/geral/comandas", response_model=DetalhamentoComandasResponse)
async def dashboard_geral_comandas():
    """Dashboard Geral - Detalhamento de comandas"""
    return DetalhamentoComandasResponse(
        total_comandas=256,
        comandas_fechadas=251,
        comandas_abertas=5,
        com_taxa_servico=74,
        valor_taxa_servico=1593.87,
        sem_taxa_servico=50,
        comandas_sem_consumo=130,
        total_pessoas=0
    )

@router.get("/geral/ticket-medio", response_model=TicketMedioResponse)
async def dashboard_geral_ticket_medio():
    """Dashboard Geral - Ticket médio"""
    return TicketMedioResponse(
        ticket_medio_conta=233.74,
        ticket_medio_pessoa=0.00,
        tickets_zero=130
    )

@router.get("/geral/graficos/movimentacoes")
async def dashboard_geral_graficos_movimentacoes(
    periodo: str = Query("24h", description="Período: 24h, 7d, 30d")
):
    """Dashboard Geral - Gráfico de movimentações por tempo"""
    return {
        "status": "success",
        "data": {
            "periodo": periodo,
            "pontos": [
                {"timestamp": "28/09/25 - 22:20", "valor": 0},
                {"timestamp": "29/09/25 - 01:06", "valor": 1500},
                {"timestamp": "29/09/25 - 03:52", "valor": 3000},
                {"timestamp": "29/09/25 - 06:38", "valor": 6000}
            ],
            "formas_pagamento": [
                {"nome": "Crédito", "cor": "#FF6B6B", "dados": [0, 0, 0, 0]},
                {"nome": "Débito", "cor": "#4ECDC4", "dados": [0, 0, 0, 0]}, 
                {"nome": "Dinheiro", "cor": "#45B7D1", "dados": [0, 800, 2100, 4800]},
                {"nome": "PIX", "cor": "#96CEB4", "dados": [0, 0, 0, 0]},
                {"nome": "Voucher", "cor": "#FFEAA7", "dados": [0, 0, 0, 0]},
                {"nome": "Outros", "cor": "#DDA0DD", "dados": [0, 700, 900, 1200]}
            ]
        }
    }

@router.get("/geral/top-produtos")
async def dashboard_geral_top_produtos(limit: int = Query(10, description="Limite de produtos")):
    """Dashboard Geral - Top produtos mais vendidos"""
    return {
        "status": "success", 
        "data": {
            "periodo": "últimos 30 dias",
            "produtos": [
                {"nome": "Produto A", "vendas": 145, "receita": 2890.50},
                {"nome": "Produto B", "vendas": 98, "receita": 1960.00},
                {"nome": "Produto C", "vendas": 76, "receita": 1520.00}
            ]
        }
    }

@router.get("/geral/top-clientes") 
async def dashboard_geral_top_clientes(limit: int = Query(10, description="Limite de clientes")):
    """Dashboard Geral - Top clientes"""
    return {
        "status": "success",
        "data": {
            "periodo": "últimos 30 dias",
            "clientes": [
                {"nome": "Cliente VIP", "compras": 23, "total_gasto": 4560.80},
                {"nome": "Cliente Gold", "compras": 18, "total_gasto": 3240.50},
                {"nome": "Cliente Silver", "compras": 12, "total_gasto": 2180.30}
            ]
        }
    }

# DASHBOARD CLIENTES - Igual ao Meep

@router.get("/clientes/resumo")
async def dashboard_clientes_resumo(
    evento_id: Optional[int] = Query(None, description="ID do evento para filtro")
):
    """Dashboard Clientes - Resumo com filtro por evento"""
    return {
        "status": "success",
        "data": {
            "evento_filtro": evento_id,
            "total_clientes": 1456,
            "clientes_ativos": 892,
            "novos_clientes_mes": 78,
            "taxa_retencao": 67.5,
            "ticket_medio_cliente": 156.80
        }
    }

@router.get("/clientes/segmentacao")
async def dashboard_clientes_segmentacao():
    """Dashboard Clientes - Segmentação de clientes"""
    return {
        "status": "success",
        "data": {
            "por_categoria": [
                {"categoria": "VIP", "quantidade": 156, "percentual": 10.7},
                {"categoria": "Gold", "quantidade": 289, "percentual": 19.8},
                {"categoria": "Silver", "quantidade": 478, "percentual": 32.8},
                {"categoria": "Bronze", "quantidade": 533, "percentual": 36.7}
            ],
            "por_frequencia": [
                {"tipo": "Frequentes", "quantidade": 234, "percentual": 16.1},
                {"tipo": "Regulares", "quantidade": 567, "percentual": 38.9},
                {"tipo": "Esporádicos", "quantidade": 655, "percentual": 45.0}
            ]
        }
    }

@router.get("/clientes/analise-comportamento")
async def dashboard_clientes_analise_comportamento():
    """Dashboard Clientes - Análise de comportamento"""
    return {
        "status": "success",
        "data": {
            "horarios_pico": ["19:00-21:00", "21:00-23:00"],
            "dias_semana_preferidos": ["Sexta", "Sábado", "Domingo"],
            "produtos_preferidos": ["Bebidas", "Petiscos", "Pratos principais"],
            "sazonalidade": {
                "alta_temporada": ["Dezembro", "Janeiro", "Julho"],
                "baixa_temporada": ["Março", "Abril", "Agosto"]
            }
        }
    }

# ENDPOINTS ORIGINAIS MANTIDOS PARA COMPATIBILIDADE

@router.get("/resumo")
async def dashboard_resumo():
    """Endpoint resumo do modulo dashboard (compatibilidade)"""
    return {"status": "success", "module": "dashboard", "endpoint": "resumo", "redirect": "/api/dashboard/geral/resumo"}

@router.get("/ranking")
async def dashboard_ranking():
    """Endpoint ranking do modulo dashboard (compatibilidade)"""
    return {"status": "success", "module": "dashboard", "endpoint": "ranking", "redirect": "/api/dashboard/geral/top-clientes"}

@router.get("/vendas")
async def dashboard_vendas():
    """Endpoint vendas do modulo dashboard (compatibilidade)"""
    return {"status": "success", "module": "dashboard", "endpoint": "vendas", "redirect": "/api/dashboard/geral/movimentacoes-por-forma"}

@router.get("/aniversariantes")
async def dashboard_aniversariantes():
    """Endpoint aniversariantes do modulo dashboard"""
    return {"status": "success", "module": "dashboard", "endpoint": "aniversariantes"}

@router.get("/tempo-real")
async def dashboard_tempo_real():
    """Endpoint tempo-real do modulo dashboard"""
    return {"status": "success", "module": "dashboard", "endpoint": "tempo-real"}

@router.get("/avancado")
async def dashboard_avancado():
    """Endpoint avancado do modulo dashboard"""
    return {"status": "success", "module": "dashboard", "endpoint": "avancado"}

@router.get("/graficos")
async def dashboard_graficos():
    """Endpoint graficos do modulo dashboard (compatibilidade)"""
    return {"status": "success", "module": "dashboard", "endpoint": "graficos", "redirect": "/api/dashboard/geral/graficos/movimentacoes"}
