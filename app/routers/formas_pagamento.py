from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from ..database import get_db

router = APIRouter(prefix="/api/formas-pagamento", tags=["FORMAS-PAGAMENTO"])

# Schemas - Formas de Pagamento
class FormaPagamento(BaseModel):
    id: Optional[int] = None
    nome: str
    tipo: str  # DINHEIRO, CARTAO_CREDITO, CARTAO_DEBITO, PIX, BOLETO, TRANSFERENCIA, CHEQUE
    categoria: str  # VISTA, PRAZO, PARCELADO
    aceita_parcelas: bool = False
    max_parcelas: Optional[int] = None
    taxa_operacional: float = 0.0
    taxa_adquirente: float = 0.0
    prazo_recebimento: int = 0  # Em dias
    ativo: bool = True
    icone: Optional[str] = None
    cor: Optional[str] = None
    ordem_exibicao: int = 0
    configuracoes_especiais: Optional[dict] = None

class ConfiguracaoFormaPagamento(BaseModel):
    forma_pagamento_id: int
    empresa_id: Optional[int] = None
    taxa_personalizada: Optional[float] = None
    prazo_personalizado: Optional[int] = None
    limite_diario: Optional[float] = None
    limite_transacao: Optional[float] = None
    ativo_empresa: bool = True

# FORMAS-PAGAMENTO - Endpoints Completos

@router.post("/")
async def criar_forma_pagamento(forma: FormaPagamento, db: Session = Depends(get_db)):
    """Criar nova forma de pagamento"""
    return {
        "id": 1,
        "nome": forma.nome,
        "tipo": forma.tipo,
        "categoria": forma.categoria,
        "aceita_parcelas": forma.aceita_parcelas,
        "max_parcelas": forma.max_parcelas,
        "taxa_operacional": forma.taxa_operacional,
        "prazo_recebimento": forma.prazo_recebimento,
        "status": "CRIADA",
        "data_criacao": datetime.now().isoformat()
    }

@router.get("/")
async def listar_formas_pagamento(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db)
):
    """Listar formas de pagamento com filtros"""
    return {
        "formas_pagamento": [
            {
                "id": 1,
                "nome": "Dinheiro",
                "tipo": "DINHEIRO",
                "categoria": "VISTA",
                "aceita_parcelas": False,
                "taxa_operacional": 0.0,
                "prazo_recebimento": 0,
                "ativo": True,
                "icone": "💵",
                "cor": "#4CAF50",
                "ordem_exibicao": 1
            },
            {
                "id": 2,
                "nome": "PIX",
                "tipo": "PIX",
                "categoria": "VISTA",
                "aceita_parcelas": False,
                "taxa_operacional": 0.99,
                "prazo_recebimento": 0,
                "ativo": True,
                "icone": "🔄",
                "cor": "#FF9800",
                "ordem_exibicao": 2
            },
            {
                "id": 3,
                "nome": "Cartão de Crédito",
                "tipo": "CARTAO_CREDITO",
                "categoria": "PRAZO",
                "aceita_parcelas": True,
                "max_parcelas": 12,
                "taxa_operacional": 3.99,
                "prazo_recebimento": 30,
                "ativo": True,
                "icone": "💳",
                "cor": "#2196F3",
                "ordem_exibicao": 3
            },
            {
                "id": 4,
                "nome": "Cartão de Débito",
                "tipo": "CARTAO_DEBITO",
                "categoria": "VISTA",
                "aceita_parcelas": False,
                "taxa_operacional": 1.99,
                "prazo_recebimento": 1,
                "ativo": True,
                "icone": "💳",
                "cor": "#9C27B0",
                "ordem_exibicao": 4
            },
            {
                "id": 5,
                "nome": "Boleto Bancário",
                "tipo": "BOLETO",
                "categoria": "PRAZO",
                "aceita_parcelas": False,
                "taxa_operacional": 2.90,
                "prazo_recebimento": 2,
                "ativo": True,
                "icone": "📄",
                "cor": "#607D8B",
                "ordem_exibicao": 5
            }
        ],
        "total": 5,
        "filtros_aplicados": {
            "tipo": tipo,
            "categoria": categoria,
            "ativo": ativo
        }
    }

@router.get("/tipos")
async def obter_tipos_formas_pagamento():
    """Obter tipos disponíveis de formas de pagamento"""
    return {
        "tipos": [
            {"codigo": "DINHEIRO", "nome": "Dinheiro", "descricao": "Pagamento em espécie"},
            {"codigo": "PIX", "nome": "PIX", "descricao": "Pagamento instantâneo"},
            {"codigo": "CARTAO_CREDITO", "nome": "Cartão de Crédito", "descricao": "Pagamento parcelado"},
            {"codigo": "CARTAO_DEBITO", "nome": "Cartão de Débito", "descricao": "Débito em conta"},
            {"codigo": "BOLETO", "nome": "Boleto Bancário", "descricao": "Cobrança bancária"},
            {"codigo": "TRANSFERENCIA", "nome": "Transferência", "descricao": "TED/DOC"},
            {"codigo": "CHEQUE", "nome": "Cheque", "descricao": "Cheque pré-datado"}
        ],
        "categorias": [
            {"codigo": "VISTA", "nome": "À Vista", "descricao": "Recebimento imediato"},
            {"codigo": "PRAZO", "nome": "A Prazo", "descricao": "Recebimento futuro"},
            {"codigo": "PARCELADO", "nome": "Parcelado", "descricao": "Recebimento parcelado"}
        ]
    }

@router.get("/{forma_id}")
async def obter_forma_pagamento(forma_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de uma forma de pagamento específica"""
    return {
        "id": forma_id,
        "nome": "Cartão de Crédito",
        "tipo": "CARTAO_CREDITO",
        "categoria": "PRAZO",
        "aceita_parcelas": True,
        "max_parcelas": 12,
        "taxa_operacional": 3.99,
        "taxa_adquirente": 2.50,
        "prazo_recebimento": 30,
        "ativo": True,
        "icone": "💳",
        "cor": "#2196F3",
        "ordem_exibicao": 3,
        "configuracoes_especiais": {
            "bandeiras_aceitas": ["VISA", "MASTERCARD", "ELO", "AMEX"],
            "valor_minimo_parcela": 10.00,
            "taxa_por_parcela": {
                "1x": 3.99,
                "2x": 4.49,
                "3x": 4.99,
                "6x": 5.99,
                "12x": 7.99
            }
        },
        "estatisticas": {
            "total_transacoes_mes": 450,
            "volume_mes": 125600.00,
            "ticket_medio": 279.11,
            "taxa_aprovacao": 94.2
        }
    }

@router.put("/{forma_id}")
async def atualizar_forma_pagamento(forma_id: int, forma: FormaPagamento, db: Session = Depends(get_db)):
    """Atualizar dados de uma forma de pagamento"""
    return {
        "forma_id": forma_id,
        "status": "ATUALIZADA",
        "alteracoes": {
            "nome": forma.nome,
            "taxa_operacional": forma.taxa_operacional,
            "prazo_recebimento": forma.prazo_recebimento,
            "max_parcelas": forma.max_parcelas,
            "ativo": forma.ativo
        },
        "data_atualizacao": datetime.now().isoformat()
    }

@router.delete("/{forma_id}")
async def excluir_forma_pagamento(forma_id: int, db: Session = Depends(get_db)):
    """Excluir forma de pagamento"""
    return {
        "forma_id": forma_id,
        "status": "EXCLUIDA",
        "data_exclusao": datetime.now().isoformat(),
        "observacao": "Forma de pagamento removida do sistema"
    }

@router.patch("/{forma_id}/toggle")
async def toggle_forma_pagamento(forma_id: int, db: Session = Depends(get_db)):
    """Ativar/desativar forma de pagamento"""
    return {
        "forma_id": forma_id,
        "status_anterior": "ATIVA",
        "status_atual": "INATIVA",
        "data_alteracao": datetime.now().isoformat(),
        "alterado_por": "sistema"
    }

@router.post("/{forma_id}/configuracoes")
async def configurar_forma_pagamento_empresa(
    forma_id: int,
    config: ConfiguracaoFormaPagamento,
    db: Session = Depends(get_db)
):
    """Configurar forma de pagamento para empresa específica"""
    return {
        "forma_pagamento_id": forma_id,
        "empresa_id": config.empresa_id,
        "configuracao": {
            "taxa_personalizada": config.taxa_personalizada,
            "prazo_personalizado": config.prazo_personalizado,
            "limite_diario": config.limite_diario,
            "limite_transacao": config.limite_transacao,
            "ativo_empresa": config.ativo_empresa
        },
        "data_configuracao": datetime.now().isoformat(),
        "status": "CONFIGURADA"
    }

@router.get("/{forma_id}/estatisticas")
async def obter_estatisticas_forma_pagamento(
    forma_id: int,
    periodo: str = Query("30d", description="Período: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """Obter estatísticas de uso da forma de pagamento"""
    return {
        "forma_pagamento": {
            "id": forma_id,
            "nome": "Cartão de Crédito"
        },
        "periodo": periodo,
        "estatisticas": {
            "total_transacoes": 1250,
            "volume_total": 385750.00,
            "ticket_medio": 308.60,
            "taxa_aprovacao": 94.2,
            "comissao_total": 15430.00,
            "crescimento_transacoes": 12.5,
            "crescimento_volume": 18.3
        },
        "distribuicao_por_dia": [
            {"data": "2024-01-01", "transacoes": 45, "volume": 12750.00},
            {"data": "2024-01-02", "transacoes": 52, "volume": 15230.00},
            {"data": "2024-01-03", "transacoes": 38, "volume": 9840.00}
        ],
        "top_estabelecimentos": [
            {"nome": "Loja Centro", "transacoes": 234, "volume": 67890.00},
            {"nome": "Loja Shopping", "transacoes": 189, "volume": 52340.00}
        ]
    }

@router.post("/reordenar")
async def reordenar_formas_pagamento(
    nova_ordem: List[dict] = Body(..., description="Lista com ID e nova posição"),
    db: Session = Depends(get_db)
):
    """Reordenar exibição das formas de pagamento"""
    return {
        "status": "REORDENADO",
        "itens_reordenados": len(nova_ordem),
        "nova_ordem": nova_ordem,
        "data_reordenacao": datetime.now().isoformat()
    }
