"""
Router para Sistema de Fornecedores
Gestão completa de fornecedores, produtos, cotações e performance
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario, Produto, Empresa
from ..models_inventario import (
    Fornecedor, TipoFornecedor, StatusFornecedor, ProdutoFornecedor,
    OrdemCompra, ItemOrdemCompra, StatusOrdemCompra,
    RecebimentoMercadoria, ItemRecebimento, StatusRecebimento
)

router = APIRouter()

# ================================================================================
# SCHEMAS PYDANTIC
# ================================================================================

from pydantic import BaseModel, EmailStr
from enum import Enum

class FornecedorCreate(BaseModel):
    nome: str
    tipo_pessoa: str  # 'fisica' ou 'juridica'
    documento: str  # CPF ou CNPJ
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    tipo_fornecedor: TipoFornecedor
    observacoes: Optional[str] = None
    prazo_pagamento: Optional[int] = None
    limite_credito: Optional[float] = None
    pessoa_contato: Optional[str] = None
    site: Optional[str] = None

class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    tipo_fornecedor: Optional[TipoFornecedor] = None
    status: Optional[StatusFornecedor] = None
    observacoes: Optional[str] = None
    prazo_pagamento: Optional[int] = None
    limite_credito: Optional[float] = None
    pessoa_contato: Optional[str] = None
    site: Optional[str] = None

class ProdutoFornecedorCreate(BaseModel):
    produto_id: int
    codigo_fornecedor: Optional[str] = None
    preco_compra: float
    prazo_entrega: Optional[int] = None
    quantidade_minima: Optional[float] = None
    observacoes: Optional[str] = None
    preferencial: bool = False

class ProdutoFornecedorUpdate(BaseModel):
    codigo_fornecedor: Optional[str] = None
    preco_compra: Optional[float] = None
    prazo_entrega: Optional[int] = None
    quantidade_minima: Optional[float] = None
    observacoes: Optional[str] = None
    preferencial: Optional[bool] = None
    ativo: Optional[bool] = None

class AvaliacaoFornecedor(BaseModel):
    qualidade_produto: int  # 1-5
    prazo_entrega: int      # 1-5
    atendimento: int        # 1-5
    preco: int             # 1-5
    observacoes: Optional[str] = None

# ================================================================================
# FORNECEDORES - CRUD
# ================================================================================

@router.post("/", response_model=dict)
async def criar_fornecedor(
    fornecedor_data: FornecedorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo fornecedor"""
    
    # Verificar documento único
    documento_existe = db.query(Fornecedor).filter(
        Fornecedor.empresa_id == current_user.empresa_id,
        Fornecedor.documento == fornecedor_data.documento
    ).first()
    
    if documento_existe:
        raise HTTPException(
            status_code=400,
            detail="Já existe um fornecedor com este documento"
        )
    
    try:
        fornecedor = Fornecedor(
            empresa_id=current_user.empresa_id,
            **fornecedor_data.model_dump(),
            criado_por_id=current_user.id
        )
        
        db.add(fornecedor)
        db.commit()
        db.refresh(fornecedor)
        
        return {
            "id": fornecedor.id,
            "message": "Fornecedor criado com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=dict)
async def listar_fornecedores(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    nome: Optional[str] = Query(None),
    tipo_fornecedor: Optional[TipoFornecedor] = Query(None),
    status: Optional[StatusFornecedor] = Query(None),
    cidade: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar fornecedores com filtros"""
    
    query = db.query(Fornecedor).filter(
        Fornecedor.empresa_id == current_user.empresa_id
    )
    
    # Aplicar filtros
    if nome:
        query = query.filter(Fornecedor.nome.ilike(f"%{nome}%"))
    if tipo_fornecedor:
        query = query.filter(Fornecedor.tipo_fornecedor == tipo_fornecedor)
    if status:
        query = query.filter(Fornecedor.status == status)
    if cidade:
        query = query.filter(Fornecedor.cidade.ilike(f"%{cidade}%"))
    
    # Contar total
    total = query.count()
    
    # Paginar
    offset = (page - 1) * size
    fornecedores = query.order_by(Fornecedor.nome).offset(offset).limit(size).all()
    
    return {
        "itens": fornecedores,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/{fornecedor_id}", response_model=dict)
async def obter_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter fornecedor por ID com dados completos"""
    
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id,
        Fornecedor.empresa_id == current_user.empresa_id
    ).first()
    
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    # Buscar produtos do fornecedor
    produtos = db.query(ProdutoFornecedor, Produto).join(Produto).filter(
        ProdutoFornecedor.fornecedor_id == fornecedor_id
    ).all()
    
    # Buscar estatísticas
    total_compras = db.query(func.count(OrdemCompra.id)).filter(
        OrdemCompra.fornecedor_id == fornecedor_id
    ).scalar() or 0
    
    valor_total_compras = db.query(func.sum(OrdemCompra.valor_total)).filter(
        OrdemCompra.fornecedor_id == fornecedor_id,
        OrdemCompra.status == StatusOrdemCompra.FINALIZADA
    ).scalar() or 0
    
    # Última compra
    ultima_compra = db.query(OrdemCompra).filter(
        OrdemCompra.fornecedor_id == fornecedor_id
    ).order_by(desc(OrdemCompra.data_pedido)).first()
    
    return {
        "fornecedor": fornecedor,
        "produtos": [
            {
                "produto_fornecedor": pf,
                "produto": p
            } for pf, p in produtos
        ],
        "estatisticas": {
            "total_compras": total_compras,
            "valor_total_compras": float(valor_total_compras),
            "ultima_compra": ultima_compra.data_pedido if ultima_compra else None,
            "quantidade_produtos": len(produtos)
        }
    }

@router.patch("/{fornecedor_id}", response_model=dict)
async def atualizar_fornecedor(
    fornecedor_id: int,
    dados: FornecedorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar dados do fornecedor"""
    
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id,
        Fornecedor.empresa_id == current_user.empresa_id
    ).first()
    
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    try:
        # Atualizar campos
        dados_dict = dados.model_dump(exclude_unset=True)
        for campo, valor in dados_dict.items():
            setattr(fornecedor, campo, valor)
        
        fornecedor.atualizado_em = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Fornecedor atualizado com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{fornecedor_id}", response_model=dict)
async def excluir_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Excluir fornecedor (soft delete)"""
    
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id,
        Fornecedor.empresa_id == current_user.empresa_id
    ).first()
    
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    # Verificar se tem compras ativas
    compras_ativas = db.query(OrdemCompra).filter(
        OrdemCompra.fornecedor_id == fornecedor_id,
        OrdemCompra.status.in_([StatusOrdemCompra.PENDENTE, StatusOrdemCompra.APROVADA])
    ).count()
    
    if compras_ativas > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir fornecedor com compras ativas"
        )
    
    try:
        fornecedor.status = StatusFornecedor.INATIVO
        fornecedor.atualizado_em = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Fornecedor inativado com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# PRODUTOS DO FORNECEDOR
# ================================================================================

@router.post("/{fornecedor_id}/produtos", response_model=dict)
async def adicionar_produto_fornecedor(
    fornecedor_id: int,
    produto_data: ProdutoFornecedorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Adicionar produto ao fornecedor"""
    
    # Verificar se fornecedor existe
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id,
        Fornecedor.empresa_id == current_user.empresa_id
    ).first()
    
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    # Verificar se produto existe
    produto = db.query(Produto).filter(
        Produto.id == produto_data.produto_id,
        Produto.empresa_id == current_user.empresa_id
    ).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Verificar se já existe a associação
    existe = db.query(ProdutoFornecedor).filter(
        ProdutoFornecedor.fornecedor_id == fornecedor_id,
        ProdutoFornecedor.produto_id == produto_data.produto_id
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=400,
            detail="Produto já associado a este fornecedor"
        )
    
    try:
        produto_fornecedor = ProdutoFornecedor(
            fornecedor_id=fornecedor_id,
            **produto_data.model_dump(),
            criado_por_id=current_user.id
        )
        
        db.add(produto_fornecedor)
        db.commit()
        
        return {"message": "Produto adicionado ao fornecedor com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{fornecedor_id}/produtos", response_model=List[dict])
async def listar_produtos_fornecedor(
    fornecedor_id: int,
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar produtos do fornecedor"""
    
    query = db.query(ProdutoFornecedor, Produto).join(Produto).filter(
        ProdutoFornecedor.fornecedor_id == fornecedor_id,
        Produto.empresa_id == current_user.empresa_id
    )
    
    if ativo is not None:
        query = query.filter(ProdutoFornecedor.ativo == ativo)
    
    produtos = query.all()
    
    return [
        {
            "produto_fornecedor": pf,
            "produto": p
        } for pf, p in produtos
    ]

@router.patch("/{fornecedor_id}/produtos/{produto_id}", response_model=dict)
async def atualizar_produto_fornecedor(
    fornecedor_id: int,
    produto_id: int,
    dados: ProdutoFornecedorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar dados do produto do fornecedor"""
    
    produto_fornecedor = db.query(ProdutoFornecedor).filter(
        ProdutoFornecedor.fornecedor_id == fornecedor_id,
        ProdutoFornecedor.produto_id == produto_id
    ).first()
    
    if not produto_fornecedor:
        raise HTTPException(
            status_code=404,
            detail="Associação produto-fornecedor não encontrada"
        )
    
    try:
        dados_dict = dados.model_dump(exclude_unset=True)
        for campo, valor in dados_dict.items():
            setattr(produto_fornecedor, campo, valor)
        
        produto_fornecedor.atualizado_em = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Produto do fornecedor atualizado com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# COTAÇÕES E COMPARAÇÕES
# ================================================================================

@router.get("/cotacao/produto/{produto_id}", response_model=List[dict])
async def obter_cotacoes_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter cotações de um produto em diferentes fornecedores"""
    
    cotacoes = db.query(ProdutoFornecedor, Fornecedor).join(Fornecedor).filter(
        ProdutoFornecedor.produto_id == produto_id,
        ProdutoFornecedor.ativo == True,
        Fornecedor.empresa_id == current_user.empresa_id,
        Fornecedor.status == StatusFornecedor.ATIVO
    ).order_by(ProdutoFornecedor.preco_compra).all()
    
    return [
        {
            "fornecedor": f,
            "produto_fornecedor": pf,
            "economia": float(pf.preco_compra - cotacoes[0][0].preco_compra) if i > 0 else 0.0
        } for i, (pf, f) in enumerate(cotacoes)
    ]

@router.get("/melhor-preco/produto/{produto_id}", response_model=dict)
async def obter_melhor_preco(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter fornecedor com melhor preço para um produto"""
    
    melhor = db.query(ProdutoFornecedor, Fornecedor).join(Fornecedor).filter(
        ProdutoFornecedor.produto_id == produto_id,
        ProdutoFornecedor.ativo == True,
        Fornecedor.empresa_id == current_user.empresa_id,
        Fornecedor.status == StatusFornecedor.ATIVO
    ).order_by(ProdutoFornecedor.preco_compra).first()
    
    if not melhor:
        raise HTTPException(
            status_code=404,
            detail="Nenhum fornecedor ativo encontrado para este produto"
        )
    
    pf, f = melhor
    
    return {
        "fornecedor": f,
        "produto_fornecedor": pf
    }

# ================================================================================
# PERFORMANCE E AVALIAÇÕES
# ================================================================================

@router.get("/performance", response_model=List[dict])
async def obter_performance_fornecedores(
    periodo_dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter performance dos fornecedores no período"""
    
    data_inicio = datetime.utcnow() - timedelta(days=periodo_dias)
    
    # Query principal com estatísticas agregadas
    performance = db.query(
        Fornecedor.id,
        Fornecedor.nome,
        func.count(OrdemCompra.id).label('total_compras'),
        func.sum(OrdemCompra.valor_total).label('valor_total'),
        func.avg(
            func.extract('days', OrdemCompra.data_entrega_real - OrdemCompra.data_entrega_prevista)
        ).label('atraso_medio'),
        func.count(
            func.case([(OrdemCompra.data_entrega_real <= OrdemCompra.data_entrega_prevista, 1)])
        ).label('entregas_pontuais')
    ).join(OrdemCompra).filter(
        Fornecedor.empresa_id == current_user.empresa_id,
        OrdemCompra.data_pedido >= data_inicio
    ).group_by(Fornecedor.id, Fornecedor.nome).all()
    
    resultado = []
    for p in performance:
        pontualidade = (p.entregas_pontuais / p.total_compras * 100) if p.total_compras > 0 else 0
        
        resultado.append({
            "fornecedor_id": p.id,
            "nome": p.nome,
            "total_compras": p.total_compras,
            "valor_total": float(p.valor_total or 0),
            "atraso_medio_dias": float(p.atraso_medio or 0),
            "pontualidade_percentual": pontualidade,
            "classificacao": (
                "Excelente" if pontualidade >= 95 and (p.atraso_medio or 0) <= 1 else
                "Bom" if pontualidade >= 80 and (p.atraso_medio or 0) <= 3 else
                "Regular" if pontualidade >= 60 else "Ruim"
            )
        })
    
    return sorted(resultado, key=lambda x: x['valor_total'], reverse=True)

@router.post("/{fornecedor_id}/avaliar", response_model=dict)
async def avaliar_fornecedor(
    fornecedor_id: int,
    avaliacao: AvaliacaoFornecedor,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Avaliar fornecedor"""
    
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id,
        Fornecedor.empresa_id == current_user.empresa_id
    ).first()
    
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    try:
        # Calcular média das avaliações
        media_geral = (
            avaliacao.qualidade_produto + 
            avaliacao.prazo_entrega + 
            avaliacao.atendimento + 
            avaliacao.preco
        ) / 4
        
        # Atualizar avaliação do fornecedor
        fornecedor.avaliacao_media = media_geral
        fornecedor.ultima_avaliacao = datetime.utcnow()
        
        # Aqui você poderia salvar o histórico de avaliações em uma tabela separada
        
        db.commit()
        
        return {
            "message": "Avaliação registrada com sucesso",
            "media_geral": media_geral
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# DASHBOARD DE FORNECEDORES
# ================================================================================

@router.get("/dashboard/resumo", response_model=dict)
async def obter_dashboard_fornecedores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Dashboard resumo dos fornecedores"""
    
    # KPIs principais
    total_fornecedores = db.query(func.count(Fornecedor.id)).filter(
        Fornecedor.empresa_id == current_user.empresa_id
    ).scalar()
    
    fornecedores_ativos = db.query(func.count(Fornecedor.id)).filter(
        Fornecedor.empresa_id == current_user.empresa_id,
        Fornecedor.status == StatusFornecedor.ATIVO
    ).scalar()
    
    # Compras últimos 30 dias
    data_30_dias = datetime.utcnow() - timedelta(days=30)
    compras_mes = db.query(func.sum(OrdemCompra.valor_total)).join(Fornecedor).filter(
        Fornecedor.empresa_id == current_user.empresa_id,
        OrdemCompra.data_pedido >= data_30_dias
    ).scalar() or 0
    
    # Top 5 fornecedores por valor
    top_fornecedores = db.query(
        Fornecedor.nome,
        func.sum(OrdemCompra.valor_total).label('total')
    ).join(OrdemCompra).filter(
        Fornecedor.empresa_id == current_user.empresa_id,
        OrdemCompra.data_pedido >= data_30_dias
    ).group_by(Fornecedor.id, Fornecedor.nome).order_by(desc('total')).limit(5).all()
    
    # Distribuição por tipo
    tipos = db.query(
        Fornecedor.tipo_fornecedor,
        func.count(Fornecedor.id).label('quantidade')
    ).filter(
        Fornecedor.empresa_id == current_user.empresa_id,
        Fornecedor.status == StatusFornecedor.ATIVO
    ).group_by(Fornecedor.tipo_fornecedor).all()
    
    return {
        "total_fornecedores": total_fornecedores,
        "fornecedores_ativos": fornecedores_ativos,
        "compras_ultimo_mes": float(compras_mes),
        "top_fornecedores": [
            {"nome": f.nome, "valor": float(f.total)}
            for f in top_fornecedores
        ],
        "distribuicao_tipos": [
            {"tipo": t.tipo_fornecedor, "quantidade": t.quantidade}
            for t in tipos
        ]
    }
