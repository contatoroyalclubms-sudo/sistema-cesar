from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.database import get_db

router = APIRouter(prefix="/api/estoque", tags=["Gestão de Estoque"])

# Schemas
class ProdutoEstoque(BaseModel):
    id: Optional[int] = None
    codigo: str
    nome: str
    categoria: str
    unidade_medida: str
    estoque_minimo: float
    estoque_maximo: float
    estoque_atual: float
    custo_medio: float
    preco_venda: float
    fornecedor_id: Optional[int]
    localizacao: Optional[str]
    ativo: bool = True

class MovimentacaoEstoque(BaseModel):
    id: Optional[int] = None
    produto_id: int
    tipo: str  # ENTRADA, SAIDA, AJUSTE, TRANSFERENCIA
    quantidade: float
    valor_unitario: float
    valor_total: float
    documento: Optional[str]
    motivo_id: Optional[int]
    observacao: Optional[str]
    data_movimento: datetime
    usuario_id: int
    lote: Optional[str]
    validade: Optional[date]

class Inventario(BaseModel):
    id: Optional[int] = None
    codigo: str
    descricao: str
    data_inicio: datetime
    data_fim: Optional[datetime]
    status: str  # ABERTO, EM_CONTAGEM, FINALIZADO, CANCELADO
    tipo: str  # TOTAL, PARCIAL, CICLICO
    responsavel_id: int
    observacoes: Optional[str]

class ItemInventario(BaseModel):
    id: Optional[int] = None
    inventario_id: int
    produto_id: int
    estoque_sistema: float
    estoque_contado: float
    diferenca: float
    custo_diferenca: float
    justificativa: Optional[str]
    conferido: bool = False

class MotivoMovimentacao(BaseModel):
    id: Optional[int] = None
    codigo: str
    descricao: str
    tipo: str  # ENTRADA, SAIDA, AJUSTE
    requer_aprovacao: bool = False
    ativo: bool = True

class CentralLancamento(BaseModel):
    id: Optional[int] = None
    tipo_documento: str  # NF_ENTRADA, NF_SAIDA, REQUISICAO, TRANSFERENCIA
    numero_documento: str
    data_documento: date
    fornecedor_id: Optional[int]
    valor_total: float
    status: str  # PENDENTE, LANCADO, CANCELADO
    observacoes: Optional[str]
    usuario_id: int

# Cadastros
@router.post("/produtos")
async def criar_produto_estoque(produto: ProdutoEstoque, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **produto.dict(),
        "created_at": datetime.now()
    }

@router.get("/produtos")
async def listar_produtos_estoque(
    categoria: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    produtos = [
        {
            "id": 1,
            "codigo": "PROD001",
            "nome": "Cerveja Heineken 600ml",
            "categoria": "Bebidas",
            "estoque_atual": 250,
            "estoque_minimo": 50,
            "custo_medio": 4.50,
            "preco_venda": 12.00
        },
        {
            "id": 2,
            "codigo": "PROD002",
            "nome": "Água Mineral 500ml",
            "categoria": "Bebidas",
            "estoque_atual": 500,
            "estoque_minimo": 100,
            "custo_medio": 1.20,
            "preco_venda": 4.00
        }
    ]

    if categoria:
        produtos = [p for p in produtos if p["categoria"] == categoria]

    return produtos

@router.put("/produtos/{produto_id}")
async def atualizar_produto_estoque(
    produto_id: int,
    produto: ProdutoEstoque,
    db: Session = Depends(get_db)
):
    return {"id": produto_id, **produto.dict(), "updated_at": datetime.now()}

# Central de Lançamento
@router.post("/central-lancamento")
async def criar_lancamento(lancamento: CentralLancamento, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **lancamento.dict(),
        "created_at": datetime.now()
    }

@router.get("/central-lancamento")
async def listar_lancamentos(
    tipo_documento: Optional[str] = None,
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "tipo_documento": "NF_ENTRADA",
            "numero_documento": "NF-2024-001",
            "data_documento": "2024-01-15",
            "valor_total": 5000.00,
            "status": "LANCADO"
        }
    ]

@router.post("/central-lancamento/{lancamento_id}/processar")
async def processar_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    return {
        "message": "Lançamento processado com sucesso",
        "lancamento_id": lancamento_id,
        "itens_processados": 15,
        "valor_total": 5000.00
    }

# Inventário
@router.post("/inventarios")
async def criar_inventario(inventario: Inventario, db: Session = Depends(get_db)):
    return {
        "id": 1,
        **inventario.dict(),
        "created_at": datetime.now()
    }

@router.get("/inventarios")
async def listar_inventarios(
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "codigo": "INV-2024-001",
            "descricao": "Inventário Mensal Janeiro",
            "data_inicio": "2024-01-01T08:00:00",
            "status": "FINALIZADO",
            "tipo": "TOTAL",
            "divergencia_total": -1250.00
        }
    ]

@router.post("/inventarios/{inventario_id}/itens")
async def adicionar_item_inventario(
    inventario_id: int,
    item: ItemInventario,
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "inventario_id": inventario_id,
        **item.dict()
    }

@router.put("/inventarios/{inventario_id}/itens/{item_id}/contagem")
async def atualizar_contagem(
    inventario_id: int,
    item_id: int,
    estoque_contado: float,
    justificativa: Optional[str] = None,
    db: Session = Depends(get_db)
):
    diferenca = estoque_contado - 100  # estoque_sistema
    return {
        "item_id": item_id,
        "estoque_sistema": 100,
        "estoque_contado": estoque_contado,
        "diferenca": diferenca,
        "custo_diferenca": diferenca * 4.50,
        "justificativa": justificativa,
        "conferido": True
    }

@router.post("/inventarios/{inventario_id}/finalizar")
async def finalizar_inventario(inventario_id: int, db: Session = Depends(get_db)):
    return {
        "message": "Inventário finalizado com sucesso",
        "inventario_id": inventario_id,
        "ajustes_realizados": 25,
        "divergencia_total": -1250.00
    }

# Posição de Estoque
@router.get("/posicao")
async def posicao_estoque(
    produto_id: Optional[int] = None,
    categoria: Optional[str] = None,
    critico: bool = False,
    db: Session = Depends(get_db)
):
    posicoes = [
        {
            "produto_id": 1,
            "produto": "Cerveja Heineken 600ml",
            "estoque_atual": 250,
            "estoque_minimo": 50,
            "estoque_maximo": 500,
            "status": "NORMAL",
            "percentual_uso": 50,
            "dias_estoque": 15,
            "valor_estoque": 1125.00
        },
        {
            "produto_id": 2,
            "produto": "Vodka Absolut 1L",
            "estoque_atual": 20,
            "estoque_minimo": 30,
            "estoque_maximo": 100,
            "status": "CRITICO",
            "percentual_uso": 20,
            "dias_estoque": 3,
            "valor_estoque": 800.00
        }
    ]

    if critico:
        posicoes = [p for p in posicoes if p["status"] == "CRITICO"]

    return posicoes

@router.get("/posicao/resumo")
async def resumo_estoque(db: Session = Depends(get_db)):
    return {
        "valor_total_estoque": 125000.00,
        "itens_total": 450,
        "itens_criticos": 12,
        "itens_excesso": 5,
        "itens_normal": 433,
        "giro_medio": 2.5,
        "cobertura_dias": 18
    }

# Movimentações - Entrada
@router.post("/entradas")
async def registrar_entrada(movimentacao: MovimentacaoEstoque, db: Session = Depends(get_db)):
    movimentacao.tipo = "ENTRADA"
    return {
        "id": 1,
        **movimentacao.dict(),
        "saldo_anterior": 100,
        "saldo_atual": 100 + movimentacao.quantidade
    }

@router.get("/entradas")
async def listar_entradas(
    produto_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "produto": "Cerveja Heineken 600ml",
            "quantidade": 100,
            "valor_unitario": 4.50,
            "valor_total": 450.00,
            "documento": "NF-123456",
            "data_movimento": "2024-01-15T10:30:00",
            "usuario": "João Silva"
        }
    ]

# Movimentações - Saída
@router.post("/saidas")
async def registrar_saida(movimentacao: MovimentacaoEstoque, db: Session = Depends(get_db)):
    movimentacao.tipo = "SAIDA"
    return {
        "id": 1,
        **movimentacao.dict(),
        "saldo_anterior": 250,
        "saldo_atual": 250 - movimentacao.quantidade
    }

@router.get("/saidas")
async def listar_saidas(
    produto_id: Optional[int] = None,
    motivo_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "produto": "Cerveja Heineken 600ml",
            "quantidade": 50,
            "valor_unitario": 4.50,
            "valor_total": 225.00,
            "motivo": "Venda PDV",
            "data_movimento": "2024-01-15T20:30:00",
            "usuario": "Maria Santos"
        }
    ]

# Transferências
@router.post("/transferencias")
async def criar_transferencia(
    produto_id: int,
    quantidade: float,
    origem: str,
    destino: str,
    observacao: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return {
        "id": 1,
        "produto_id": produto_id,
        "quantidade": quantidade,
        "origem": origem,
        "destino": destino,
        "status": "PENDENTE",
        "observacao": observacao,
        "created_at": datetime.now()
    }

@router.post("/transferencias/{transferencia_id}/confirmar")
async def confirmar_transferencia(transferencia_id: int, db: Session = Depends(get_db)):
    return {
        "message": "Transferência confirmada com sucesso",
        "transferencia_id": transferencia_id,
        "status": "CONFIRMADO"
    }

# Motivos
@router.post("/motivos")
async def criar_motivo(motivo: MotivoMovimentacao, db: Session = Depends(get_db)):
    return {"id": 1, **motivo.dict()}

@router.get("/motivos")
async def listar_motivos(
    tipo: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    motivos = [
        {"id": 1, "codigo": "VND", "descricao": "Venda PDV", "tipo": "SAIDA"},
        {"id": 2, "codigo": "QBR", "descricao": "Quebra", "tipo": "SAIDA"},
        {"id": 3, "codigo": "CMP", "descricao": "Compra", "tipo": "ENTRADA"},
        {"id": 4, "codigo": "DEV", "descricao": "Devolução", "tipo": "ENTRADA"},
        {"id": 5, "codigo": "AJS", "descricao": "Ajuste Inventário", "tipo": "AJUSTE"}
    ]

    if tipo:
        motivos = [m for m in motivos if m["tipo"] == tipo]

    return motivos

# Relatórios de Estoque
@router.get("/relatorios/movimentacao")
async def relatorio_movimentacao(
    produto_id: Optional[int] = None,
    tipo: Optional[str] = None,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):
    return {
        "periodo": f"{data_inicio} a {data_fim}",
        "total_entradas": 1500,
        "valor_entradas": 6750.00,
        "total_saidas": 1250,
        "valor_saidas": 5625.00,
        "saldo_periodo": 250,
        "movimentacoes": [
            {
                "data": "2024-01-15",
                "tipo": "ENTRADA",
                "produto": "Cerveja Heineken 600ml",
                "quantidade": 100,
                "valor": 450.00,
                "saldo": 350
            }
        ]
    }

@router.get("/relatorios/curva-abc")
async def relatorio_curva_abc(
    categoria: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return {
        "classe_a": {
            "quantidade_itens": 45,
            "percentual_itens": 10,
            "valor_total": 87500.00,
            "percentual_valor": 70,
            "produtos": [
                {"produto": "Whisky JW Black", "valor": 15000.00, "percentual": 12}
            ]
        },
        "classe_b": {
            "quantidade_itens": 90,
            "percentual_itens": 20,
            "valor_total": 25000.00,
            "percentual_valor": 20,
            "produtos": []
        },
        "classe_c": {
            "quantidade_itens": 315,
            "percentual_itens": 70,
            "valor_total": 12500.00,
            "percentual_valor": 10,
            "produtos": []
        }
    }

@router.get("/relatorios/validade")
async def relatorio_validade(
    dias_vencimento: int = 30,
    db: Session = Depends(get_db)
):
    return {
        "vencidos": [
            {
                "produto": "Suco Natural Laranja",
                "lote": "LOT-2024-001",
                "quantidade": 10,
                "validade": "2024-01-10",
                "dias_vencido": 5,
                "valor": 50.00
            }
        ],
        "a_vencer": [
            {
                "produto": "Iogurte Natural",
                "lote": "LOT-2024-002",
                "quantidade": 25,
                "validade": "2024-01-25",
                "dias_restantes": 10,
                "valor": 125.00
            }
        ],
        "total_vencidos": 1,
        "total_a_vencer": 3,
        "valor_risco": 175.00
    }

# Configurações de Estoque
@router.get("/configuracoes")
async def obter_configuracoes(db: Session = Depends(get_db)):
    return {
        "permite_estoque_negativo": False,
        "custo_medio_ponderado": True,
        "alerta_estoque_minimo": True,
        "alerta_validade_dias": 30,
        "inventario_obrigatorio_dias": 30,
        "aprovacao_ajuste_limite": 100.00
    }

@router.put("/configuracoes")
async def atualizar_configuracoes(configuracoes: dict, db: Session = Depends(get_db)):
    return {**configuracoes, "updated_at": datetime.now()}

# Auditoria de Estoque
@router.get("/auditoria")
async def listar_auditoria(
    produto_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    tipo_operacao: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return [
        {
            "id": 1,
            "data": "2024-01-15T10:30:00",
            "usuario": "João Silva",
            "operacao": "AJUSTE_INVENTARIO",
            "produto": "Cerveja Heineken 600ml",
            "quantidade_anterior": 100,
            "quantidade_nova": 95,
            "motivo": "Quebra identificada no inventário",
            "ip_address": "192.168.1.100"
        }
    ]