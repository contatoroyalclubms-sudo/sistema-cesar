"""
Router para Sistema de Compras e Ordens de Compra
Gestão completa do ciclo de compras com workflow de aprovação
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario, Produto, Empresa
from ..models_inventario import (
    Fornecedor, StatusFornecedor, ProdutoFornecedor,
    OrdemCompra, ItemOrdemCompra, StatusOrdemCompra,
    RecebimentoMercadoria, ItemRecebimento, StatusRecebimento,
    EstoqueProduto, MovimentacaoEstoque, TipoMovimentacaoEstoque
)

router = APIRouter()

# ================================================================================
# SCHEMAS PYDANTIC
# ================================================================================

from pydantic import BaseModel, validator
from enum import Enum

class ItemCompraCreate(BaseModel):
    produto_id: int
    quantidade: float
    preco_unitario: float
    observacoes: Optional[str] = None

class OrdemCompraCreate(BaseModel):
    fornecedor_id: int
    data_entrega_prevista: datetime
    observacoes: Optional[str] = None
    itens: List[ItemCompraCreate]
    
    @validator('itens')
    def validar_itens(cls, v):
        if not v:
            raise ValueError('Ordem de compra deve ter pelo menos um item')
        return v

class OrdemCompraUpdate(BaseModel):
    data_entrega_prevista: Optional[datetime] = None
    observacoes: Optional[str] = None
    status: Optional[StatusOrdemCompra] = None

class ItemRecebimentoCreate(BaseModel):
    item_ordem_compra_id: int
    quantidade_recebida: float
    preco_unitario_real: Optional[float] = None
    qualidade_aprovada: bool = True
    observacoes_qualidade: Optional[str] = None

class RecebimentoCreate(BaseModel):
    ordem_compra_id: int
    data_recebimento: datetime
    numero_nota_fiscal: Optional[str] = None
    valor_frete: Optional[float] = None
    observacoes: Optional[str] = None
    itens: List[ItemRecebimentoCreate]

class AprovarCompraRequest(BaseModel):
    observacoes_aprovacao: Optional[str] = None

class FiltrosCompra(BaseModel):
    status: Optional[StatusOrdemCompra] = None
    fornecedor_id: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

# ================================================================================
# CONSTANTES
# ================================================================================

ORDEM_NAO_ENCONTRADA = "Ordem de compra não encontrada"
PRODUTO_NAO_ENCONTRADO = "Produto não encontrado"
FORNECEDOR_NAO_ENCONTRADO = "Fornecedor não encontrado"

# ================================================================================
# ORDENS DE COMPRA - CRUD
# ================================================================================

@router.post("/", response_model=dict)
async def criar_ordem_compra(
    ordem_data: OrdemCompraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova ordem de compra"""
    
    # Verificar se fornecedor existe e está ativo
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.id == ordem_data.fornecedor_id,
        Fornecedor.empresa_id == current_user.empresa_id,
        Fornecedor.status == StatusFornecedor.ATIVO
    ).first()
    
    if not fornecedor:
        raise HTTPException(
            status_code=404,
            detail="Fornecedor não encontrado ou inativo"
        )
    
    try:
        # Calcular valor total
        valor_total = Decimal('0')
        itens_validados = []
        
        for item_data in ordem_data.itens:
            # Verificar se produto existe
            produto = db.query(Produto).filter(
                Produto.id == item_data.produto_id,
                Produto.empresa_id == current_user.empresa_id
            ).first()
            
            if not produto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produto {item_data.produto_id} não encontrado"
                )
            
            valor_item = Decimal(str(item_data.quantidade)) * Decimal(str(item_data.preco_unitario))
            valor_total += valor_item
            itens_validados.append(item_data)
        
        # Gerar número da ordem
        ultimo_numero = db.query(func.max(OrdemCompra.numero_ordem)).filter(
            OrdemCompra.empresa_id == current_user.empresa_id
        ).scalar() or 0
        numero_ordem = f"OC{(ultimo_numero + 1):06d}"
        
        # Criar ordem de compra
        ordem = OrdemCompra(
            empresa_id=current_user.empresa_id,
            fornecedor_id=ordem_data.fornecedor_id,
            numero_ordem=numero_ordem,
            data_pedido=datetime.now(timezone.utc),
            data_entrega_prevista=ordem_data.data_entrega_prevista,
            valor_total=valor_total,
            status=StatusOrdemCompra.PENDENTE,
            observacoes=ordem_data.observacoes,
            criado_por_id=current_user.id
        )
        
        db.add(ordem)
        db.flush()  # Para obter o ID
        
        # Criar itens da ordem
        for item_data in itens_validados:
            item = ItemOrdemCompra(
                ordem_compra_id=ordem.id,
                produto_id=item_data.produto_id,
                quantidade=Decimal(str(item_data.quantidade)),
                preco_unitario=Decimal(str(item_data.preco_unitario)),
                valor_total=Decimal(str(item_data.quantidade)) * Decimal(str(item_data.preco_unitario)),
                observacoes=item_data.observacoes
            )
            db.add(item)
        
        db.commit()
        
        return {
            "id": ordem.id,
            "numero_ordem": numero_ordem,
            "message": "Ordem de compra criada com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=dict)
async def listar_ordens_compra(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[StatusOrdemCompra] = Query(None),
    fornecedor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar ordens de compra com filtros"""
    
    query = db.query(OrdemCompra).filter(
        OrdemCompra.empresa_id == current_user.empresa_id
    )
    
    # Aplicar filtros
    if status:
        query = query.filter(OrdemCompra.status == status)
    if fornecedor_id:
        query = query.filter(OrdemCompra.fornecedor_id == fornecedor_id)
    
    # Contar total
    total = query.count()
    
    # Paginar e incluir dados do fornecedor
    offset = (page - 1) * size
    ordens = query.join(Fornecedor).order_by(
        desc(OrdemCompra.data_pedido)
    ).offset(offset).limit(size).all()
    
    # Formatar resposta com dados do fornecedor
    itens = []
    for ordem in ordens:
        fornecedor = db.query(Fornecedor).filter(Fornecedor.id == ordem.fornecedor_id).first()
        itens.append({
            "ordem": ordem,
            "fornecedor": fornecedor
        })
    
    return {
        "itens": itens,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/{ordem_id}", response_model=dict)
async def obter_ordem_compra(
    ordem_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter ordem de compra por ID com dados completos"""
    
    ordem = db.query(OrdemCompra).filter(
        OrdemCompra.id == ordem_id,
        OrdemCompra.empresa_id == current_user.empresa_id
    ).first()
    
    if not ordem:
        raise HTTPException(status_code=404, detail=ORDEM_NAO_ENCONTRADA)
    
    # Buscar fornecedor
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == ordem.fornecedor_id).first()
    
    # Buscar itens com produtos
    itens = db.query(ItemOrdemCompra, Produto).join(Produto).filter(
        ItemOrdemCompra.ordem_compra_id == ordem_id
    ).all()
    
    # Buscar recebimentos
    recebimentos = db.query(RecebimentoMercadoria).filter(
        RecebimentoMercadoria.ordem_compra_id == ordem_id
    ).all()
    
    return {
        "ordem": ordem,
        "fornecedor": fornecedor,
        "itens": [
            {
                "item": item,
                "produto": produto
            } for item, produto in itens
        ],
        "recebimentos": recebimentos
    }

@router.patch("/{ordem_id}", response_model=dict)
async def atualizar_ordem_compra(
    ordem_id: int,
    dados: OrdemCompraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar ordem de compra"""
    
    ordem = db.query(OrdemCompra).filter(
        OrdemCompra.id == ordem_id,
        OrdemCompra.empresa_id == current_user.empresa_id
    ).first()
    
    if not ordem:
        raise HTTPException(status_code=404, detail=ORDEM_NAO_ENCONTRADA)
    
    # Verificar se pode ser editada
    if ordem.status in [StatusOrdemCompra.FINALIZADA, StatusOrdemCompra.CANCELADA]:
        raise HTTPException(
            status_code=400,
            detail="Não é possível editar ordem finalizada ou cancelada"
        )
    
    try:
        dados_dict = dados.model_dump(exclude_unset=True)
        for campo, valor in dados_dict.items():
            setattr(ordem, campo, valor)
        
        ordem.atualizado_em = datetime.now(timezone.utc)
        
        db.commit()
        
        return {"message": "Ordem de compra atualizada com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# WORKFLOW DE APROVAÇÃO
# ================================================================================

@router.post("/{ordem_id}/aprovar", response_model=dict)
async def aprovar_ordem_compra(
    ordem_id: int,
    dados: AprovarCompraRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Aprovar ordem de compra"""
    
    ordem = db.query(OrdemCompra).filter(
        OrdemCompra.id == ordem_id,
        OrdemCompra.empresa_id == current_user.empresa_id
    ).first()
    
    if not ordem:
        raise HTTPException(status_code=404, detail=ORDEM_NAO_ENCONTRADA)
    
    if ordem.status != StatusOrdemCompra.PENDENTE:
        raise HTTPException(
            status_code=400,
            detail="Apenas ordens pendentes podem ser aprovadas"
        )
    
    try:
        ordem.status = StatusOrdemCompra.APROVADA
        ordem.data_aprovacao = datetime.now(timezone.utc)
        ordem.aprovado_por_id = current_user.id
        ordem.observacoes_aprovacao = dados.observacoes_aprovacao
        ordem.atualizado_em = datetime.now(timezone.utc)
        
        db.commit()
        
        return {"message": "Ordem de compra aprovada com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ordem_id}/rejeitar", response_model=dict)
async def rejeitar_ordem_compra(
    ordem_id: int,
    dados: AprovarCompraRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Rejeitar ordem de compra"""
    
    ordem = db.query(OrdemCompra).filter(
        OrdemCompra.id == ordem_id,
        OrdemCompra.empresa_id == current_user.empresa_id
    ).first()
    
    if not ordem:
        raise HTTPException(status_code=404, detail=ORDEM_NAO_ENCONTRADA)
    
    if ordem.status != StatusOrdemCompra.PENDENTE:
        raise HTTPException(
            status_code=400,
            detail="Apenas ordens pendentes podem ser rejeitadas"
        )
    
    try:
        ordem.status = StatusOrdemCompra.CANCELADA
        ordem.data_aprovacao = datetime.now(timezone.utc)
        ordem.aprovado_por_id = current_user.id
        ordem.observacoes_aprovacao = dados.observacoes_aprovacao
        ordem.atualizado_em = datetime.now(timezone.utc)
        
        db.commit()
        
        return {"message": "Ordem de compra rejeitada com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# RECEBIMENTO DE MERCADORIAS
# ================================================================================

@router.post("/{ordem_id}/recebimentos", response_model=dict)
async def criar_recebimento(
    ordem_id: int,
    recebimento_data: RecebimentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar recebimento de mercadoria"""
    
    # Verificar se ordem existe e está aprovada
    ordem = db.query(OrdemCompra).filter(
        OrdemCompra.id == ordem_id,
        OrdemCompra.empresa_id == current_user.empresa_id,
        OrdemCompra.status == StatusOrdemCompra.APROVADA
    ).first()
    
    if not ordem:
        raise HTTPException(
            status_code=404,
            detail="Ordem de compra não encontrada ou não aprovada"
        )
    
    try:
        # Gerar número do recebimento
        ultimo_numero = db.query(func.max(RecebimentoMercadoria.numero_recebimento)).filter(
            RecebimentoMercadoria.empresa_id == current_user.empresa_id
        ).scalar() or 0
        numero_recebimento = f"REC{(ultimo_numero + 1):06d}"
        
        # Criar recebimento
        recebimento = RecebimentoMercadoria(
            empresa_id=current_user.empresa_id,
            ordem_compra_id=ordem_id,
            numero_recebimento=numero_recebimento,
            data_recebimento=recebimento_data.data_recebimento,
            numero_nota_fiscal=recebimento_data.numero_nota_fiscal,
            valor_frete=Decimal(str(recebimento_data.valor_frete or 0)),
            status=StatusRecebimento.PENDENTE,
            observacoes=recebimento_data.observacoes,
            criado_por_id=current_user.id
        )
        
        db.add(recebimento)
        db.flush()
        
        # Processar itens do recebimento
        for item_data in recebimento_data.itens:
            # Verificar se item da ordem existe
            item_ordem = db.query(ItemOrdemCompra).filter(
                ItemOrdemCompra.id == item_data.item_ordem_compra_id,
                ItemOrdemCompra.ordem_compra_id == ordem_id
            ).first()
            
            if not item_ordem:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_data.item_ordem_compra_id} não encontrado na ordem"
                )
            
            # Criar item do recebimento
            item_recebimento = ItemRecebimento(
                recebimento_id=recebimento.id,
                item_ordem_compra_id=item_data.item_ordem_compra_id,
                quantidade_recebida=Decimal(str(item_data.quantidade_recebida)),
                preco_unitario_real=Decimal(str(item_data.preco_unitario_real or item_ordem.preco_unitario)),
                qualidade_aprovada=item_data.qualidade_aprovada,
                observacoes_qualidade=item_data.observacoes_qualidade
            )
            db.add(item_recebimento)
            
            # Se qualidade aprovada, atualizar estoque
            if item_data.qualidade_aprovada:
                await _atualizar_estoque_recebimento(
                    db, current_user.empresa_id, item_ordem.produto_id,
                    item_data.quantidade_recebida, current_user.id
                )
        
        # Atualizar status da ordem se totalmente recebida
        await _verificar_conclusao_ordem(db, ordem_id)
        
        recebimento.status = StatusRecebimento.CONCLUIDO
        db.commit()
        
        return {
            "id": recebimento.id,
            "numero_recebimento": numero_recebimento,
            "message": "Recebimento criado com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================

async def _atualizar_estoque_recebimento(
    db: Session,
    empresa_id: int,
    produto_id: int,
    quantidade: float,
    usuario_id: int
):
    """Atualizar estoque após recebimento"""
    
    # Buscar posição de estoque padrão (assumindo local_id=1)
    estoque = db.query(EstoqueProduto).filter(
        EstoqueProduto.empresa_id == empresa_id,
        EstoqueProduto.produto_id == produto_id,
        EstoqueProduto.local_estoque_id == 1  # Local padrão
    ).first()
    
    if estoque:
        estoque.quantidade_disponivel += Decimal(str(quantidade))
        estoque.atualizado_em = datetime.now(timezone.utc)
    
    # Criar movimentação de entrada
    movimentacao = MovimentacaoEstoque(
        empresa_id=empresa_id,
        produto_id=produto_id,
        local_estoque_id=1,  # Local padrão
        tipo_movimentacao=TipoMovimentacaoEstoque.ENTRADA,
        quantidade=Decimal(str(quantidade)),
        motivo="Recebimento de compra",
        criado_por_id=usuario_id
    )
    db.add(movimentacao)

async def _verificar_conclusao_ordem(db: Session, ordem_id: int):
    """Verificar se ordem foi totalmente recebida"""
    
    # Buscar todos os itens da ordem
    itens_ordem = db.query(ItemOrdemCompra).filter(
        ItemOrdemCompra.ordem_compra_id == ordem_id
    ).all()
    
    # Verificar se todos foram recebidos
    todos_recebidos = True
    for item in itens_ordem:
        total_recebido = db.query(func.sum(ItemRecebimento.quantidade_recebida)).join(
            RecebimentoMercadoria
        ).filter(
            ItemRecebimento.item_ordem_compra_id == item.id,
            RecebimentoMercadoria.status == StatusRecebimento.CONCLUIDO
        ).scalar() or 0
        
        if total_recebido < item.quantidade:
            todos_recebidos = False
            break
    
    if todos_recebidos:
        ordem = db.query(OrdemCompra).filter(OrdemCompra.id == ordem_id).first()
        if ordem:
            ordem.status = StatusOrdemCompra.FINALIZADA
            ordem.data_entrega_real = datetime.now(timezone.utc)

# ================================================================================
# SUGESTÕES DE COMPRA
# ================================================================================

@router.get("/sugestoes/automaticas", response_model=List[dict])
async def obter_sugestoes_compra(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter sugestões automáticas de compra baseadas em estoque mínimo"""
    
    # Buscar produtos com estoque baixo
    produtos_baixo_estoque = db.query(
        EstoqueProduto, Produto
    ).join(Produto).filter(
        EstoqueProduto.empresa_id == current_user.empresa_id,
        EstoqueProduto.quantidade_disponivel <= EstoqueProduto.estoque_minimo
    ).all()
    
    sugestoes = []
    for estoque, produto in produtos_baixo_estoque:
        # Buscar melhor fornecedor para o produto
        melhor_fornecedor = db.query(
            ProdutoFornecedor, Fornecedor
        ).join(Fornecedor).filter(
            ProdutoFornecedor.produto_id == produto.id,
            ProdutoFornecedor.ativo == True,
            Fornecedor.status == StatusFornecedor.ATIVO,
            Fornecedor.empresa_id == current_user.empresa_id
        ).order_by(
            desc(ProdutoFornecedor.preferencial),
            ProdutoFornecedor.preco_compra
        ).first()
        
        if melhor_fornecedor:
            pf, f = melhor_fornecedor
            quantidade_sugerida = max(
                estoque.estoque_maximo - estoque.quantidade_disponivel,
                pf.quantidade_minima or 1
            )
            
            sugestoes.append({
                "produto": produto,
                "estoque_atual": float(estoque.quantidade_disponivel),
                "estoque_minimo": float(estoque.estoque_minimo),
                "fornecedor": f,
                "produto_fornecedor": pf,
                "quantidade_sugerida": float(quantidade_sugerida),
                "valor_estimado": float(quantidade_sugerida * pf.preco_compra)
            })
    
    return sugestoes

# ================================================================================
# DASHBOARD DE COMPRAS
# ================================================================================

@router.get("/dashboard/resumo", response_model=dict)
async def obter_dashboard_compras(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Dashboard resumo das compras"""
    
    # KPIs principais
    total_ordens = db.query(func.count(OrdemCompra.id)).filter(
        OrdemCompra.empresa_id == current_user.empresa_id
    ).scalar()
    
    ordens_pendentes = db.query(func.count(OrdemCompra.id)).filter(
        OrdemCompra.empresa_id == current_user.empresa_id,
        OrdemCompra.status == StatusOrdemCompra.PENDENTE
    ).scalar()
    
    # Valor de compras no mês
    inicio_mes = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0)
    compras_mes = db.query(func.sum(OrdemCompra.valor_total)).filter(
        OrdemCompra.empresa_id == current_user.empresa_id,
        OrdemCompra.data_pedido >= inicio_mes,
        OrdemCompra.status.in_([StatusOrdemCompra.APROVADA, StatusOrdemCompra.FINALIZADA])
    ).scalar() or 0
    
    # Ordens por status
    status_count = db.query(
        OrdemCompra.status,
        func.count(OrdemCompra.id).label('quantidade')
    ).filter(
        OrdemCompra.empresa_id == current_user.empresa_id
    ).group_by(OrdemCompra.status).all()
    
    # Top fornecedores
    top_fornecedores = db.query(
        Fornecedor.nome,
        func.sum(OrdemCompra.valor_total).label('total'),
        func.count(OrdemCompra.id).label('quantidade_ordens')
    ).join(OrdemCompra).filter(
        OrdemCompra.empresa_id == current_user.empresa_id,
        OrdemCompra.data_pedido >= inicio_mes
    ).group_by(Fornecedor.id, Fornecedor.nome).order_by(desc('total')).limit(5).all()
    
    return {
        "total_ordens": total_ordens,
        "ordens_pendentes": ordens_pendentes,
        "compras_mes": float(compras_mes),
        "status_distribuicao": [
            {"status": s.status, "quantidade": s.quantidade}
            for s in status_count
        ],
        "top_fornecedores": [
            {
                "nome": f.nome,
                "valor": float(f.total),
                "quantidade_ordens": f.quantidade_ordens
            }
            for f in top_fornecedores
        ]
    }
