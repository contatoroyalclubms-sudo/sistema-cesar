"""
Router para Controle de Estoque
Implementa funcionalidades completas de gestão de inventário
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from ..database import get_db
from ..models import Produto, Usuario, Empresa, Evento
from ..models_inventario import (
    EstoqueProduto, LocalEstoque, MovimentacaoEstoque, TipoMovimentacaoEstoque,
    Fornecedor, OrdemCompra, ItemOrdemCompra, StatusOrdemCompra,
    InventarioFisico, ContagemInventario, StatusInventarioFisico,
    TransferenciaEstoque, ItemTransferencia, MetodoControleEstoque
)
from ..utils.security import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/estoque", tags=["Controle de Estoque"])

# ================================================================================
# SCHEMAS PARA ESTOQUE
# ================================================================================

class LocalEstoqueCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: str = "deposito"
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    eh_principal: bool = False
    permite_venda: bool = True
    permite_compra: bool = True
    capacidade_maxima: Optional[float] = None
    responsavel: Optional[str] = None

class EstoqueProdutoUpdate(BaseModel):
    estoque_minimo: Optional[float] = None
    estoque_maximo: Optional[float] = None
    ponto_pedido: Optional[float] = None
    metodo_controle: Optional[str] = None

class MovimentacaoEstoqueCreate(BaseModel):
    produto_id: int
    local_origem_id: Optional[int] = None
    local_destino_id: Optional[int] = None
    tipo_movimentacao: str
    quantidade: float
    valor_unitario: Optional[float] = None
    numero_documento: Optional[str] = None
    observacoes: Optional[str] = None

class TransferenciaCreate(BaseModel):
    local_origem_id: int
    local_destino_id: int
    motivo: Optional[str] = None
    observacoes: Optional[str] = None
    itens: List[Dict[str, Any]]

class InventarioCreate(BaseModel):
    local_estoque_id: int
    descricao: str
    tipo_inventario: str = "completo"
    considera_custo: bool = True
    permite_venda_durante: bool = False
    motivo: Optional[str] = None

class ContagemCreate(BaseModel):
    produto_id: int
    quantidade_contada: float
    observacoes: Optional[str] = None
    motivo_diferenca: Optional[str] = None

# ================================================================================
# ENDPOINTS - LOCAIS DE ESTOQUE
# ================================================================================

@router.get("/locais")
async def listar_locais_estoque(
    empresa_id: Optional[int] = Query(None),
    evento_id: Optional[int] = Query(None),
    ativo: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar locais de estoque"""
    
    query = db.query(LocalEstoque).filter(LocalEstoque.ativo == ativo)
    
    if empresa_id:
        query = query.filter(LocalEstoque.empresa_id == empresa_id)
    if evento_id:
        query = query.filter(LocalEstoque.evento_id == evento_id)
    
    locais = query.all()
    
    return [{
        "id": local.id,
        "nome": local.nome,
        "descricao": local.descricao,
        "tipo": local.tipo,
        "endereco": local.endereco,
        "cidade": local.cidade,
        "estado": local.estado,
        "eh_principal": local.eh_principal,
        "permite_venda": local.permite_venda,
        "permite_compra": local.permite_compra,
        "responsavel": local.responsavel,
        "criado_em": local.criado_em
    } for local in locais]

@router.post("/locais")
async def criar_local_estoque(
    local_data: LocalEstoqueCreate,
    empresa_id: int = Query(...),
    evento_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo local de estoque"""
    
    local = LocalEstoque(
        empresa_id=empresa_id,
        evento_id=evento_id,
        **local_data.dict()
    )
    
    db.add(local)
    db.commit()
    db.refresh(local)
    
    return {
        "id": local.id,
        "nome": local.nome,
        "message": "Local de estoque criado com sucesso"
    }

# ================================================================================
# ENDPOINTS - POSIÇÃO DE ESTOQUE
# ================================================================================

@router.get("/posicao")
async def obter_posicao_estoque(
    empresa_id: Optional[int] = Query(None),
    local_id: Optional[int] = Query(None),
    produto_id: Optional[int] = Query(None),
    categoria_id: Optional[int] = Query(None),
    apenas_com_estoque: bool = Query(False),
    apenas_estoque_baixo: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter posição atual do estoque"""
    
    query = db.query(
        EstoqueProduto,
        Produto.nome.label('produto_nome'),
        Produto.codigo.label('produto_codigo'),
        Produto.categoria_id,
        LocalEstoque.nome.label('local_nome')
    ).join(Produto).join(LocalEstoque)
    
    # Filtros
    if empresa_id:
        query = query.filter(LocalEstoque.empresa_id == empresa_id)
    if local_id:
        query = query.filter(EstoqueProduto.local_id == local_id)
    if produto_id:
        query = query.filter(EstoqueProduto.produto_id == produto_id)
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    if apenas_com_estoque:
        query = query.filter(EstoqueProduto.quantidade_atual > 0)
    if apenas_estoque_baixo:
        query = query.filter(EstoqueProduto.quantidade_atual <= EstoqueProduto.estoque_minimo)
    
    estoques = query.all()
    
    resultado = []
    for estoque, produto_nome, produto_codigo, categoria_id, local_nome in estoques:
        # Calcular status do estoque
        status = "normal"
        if estoque.quantidade_atual <= 0:
            status = "zerado"
        elif estoque.quantidade_atual <= estoque.estoque_minimo:
            status = "baixo"
        elif estoque.estoque_maximo and estoque.quantidade_atual >= estoque.estoque_maximo:
            status = "alto"
        
        resultado.append({
            "id": estoque.id,
            "produto_id": estoque.produto_id,
            "produto_nome": produto_nome,
            "produto_codigo": produto_codigo,
            "categoria_id": categoria_id,
            "local_id": estoque.local_id,
            "local_nome": local_nome,
            "quantidade_atual": float(estoque.quantidade_atual),
            "quantidade_reservada": float(estoque.quantidade_reservada),
            "quantidade_disponivel": float(estoque.quantidade_disponivel),
            "estoque_minimo": float(estoque.estoque_minimo),
            "estoque_maximo": float(estoque.estoque_maximo or 0),
            "ponto_pedido": float(estoque.ponto_pedido or 0),
            "custo_medio": float(estoque.custo_medio),
            "ultimo_custo": float(estoque.ultimo_custo),
            "metodo_controle": estoque.metodo_controle.value if estoque.metodo_controle else None,
            "status": status,
            "giro_estoque": float(estoque.giro_estoque),
            "cobertura_dias": estoque.cobertura_dias,
            "ultima_movimentacao": estoque.ultima_movimentacao,
            "ultima_venda": estoque.ultima_venda,
            "ultima_compra": estoque.ultima_compra
        })
    
    return resultado

@router.put("/posicao/{estoque_id}")
async def atualizar_configuracao_estoque(
    estoque_id: int,
    estoque_data: EstoqueProdutoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar configurações de um item do estoque"""
    
    estoque = db.query(EstoqueProduto).filter(EstoqueProduto.id == estoque_id).first()
    if not estoque:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    
    # Atualizar apenas campos fornecidos
    for field, value in estoque_data.dict(exclude_unset=True).items():
        if field == "metodo_controle" and value:
            setattr(estoque, field, MetodoControleEstoque(value))
        else:
            setattr(estoque, field, value)
    
    estoque.atualizado_em = datetime.utcnow()
    db.commit()
    
    return {"message": "Configuração de estoque atualizada com sucesso"}

# ================================================================================
# ENDPOINTS - MOVIMENTAÇÕES
# ================================================================================

@router.get("/movimentacoes")
async def listar_movimentacoes(
    empresa_id: Optional[int] = Query(None),
    local_id: Optional[int] = Query(None),
    produto_id: Optional[int] = Query(None),
    tipo_movimentacao: Optional[str] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    limite: int = Query(100, le=1000),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar movimentações de estoque"""
    
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    query = db.query(
        MovimentacaoEstoque,
        Produto.nome.label('produto_nome'),
        Produto.codigo.label('produto_codigo'),
        LocalEstoque.nome.label('local_origem_nome'),
        LocalEstoque.nome.label('local_destino_nome')
    ).join(Produto).outerjoin(
        LocalEstoque, MovimentacaoEstoque.local_origem_id == LocalEstoque.id
    )
    
    # Filtros
    query = query.filter(
        MovimentacaoEstoque.data_movimento >= data_inicio,
        MovimentacaoEstoque.data_movimento <= data_fim
    )
    
    if produto_id:
        query = query.filter(MovimentacaoEstoque.produto_id == produto_id)
    if tipo_movimentacao:
        query = query.filter(MovimentacaoEstoque.tipo_movimentacao == tipo_movimentacao)
    
    movimentacoes = query.order_by(desc(MovimentacaoEstoque.data_movimento)).offset(offset).limit(limite).all()
    
    resultado = []
    for mov, produto_nome, produto_codigo, local_origem_nome, local_destino_nome in movimentacoes:
        resultado.append({
            "id": mov.id,
            "produto_id": mov.produto_id,
            "produto_nome": produto_nome,
            "produto_codigo": produto_codigo,
            "tipo_movimentacao": mov.tipo_movimentacao.value,
            "quantidade": float(mov.quantidade),
            "valor_unitario": float(mov.valor_unitario or 0),
            "valor_total": float(mov.valor_total or 0),
            "saldo_anterior": float(mov.saldo_anterior or 0),
            "saldo_atual": float(mov.saldo_atual or 0),
            "numero_documento": mov.numero_documento,
            "observacoes": mov.observacoes,
            "data_movimento": mov.data_movimento,
            "local_origem_nome": local_origem_nome,
            "local_destino_nome": local_destino_nome,
            "criado_em": mov.criado_em
        })
    
    return resultado

@router.post("/movimentacoes")
async def criar_movimentacao(
    movimentacao_data: MovimentacaoEstoqueCreate,
    empresa_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova movimentação de estoque"""
    
    # Buscar ou criar estoque do produto
    local_id = movimentacao_data.local_destino_id or movimentacao_data.local_origem_id
    if not local_id:
        raise HTTPException(status_code=400, detail="Local de origem ou destino deve ser informado")
    
    estoque = db.query(EstoqueProduto).filter(
        EstoqueProduto.produto_id == movimentacao_data.produto_id,
        EstoqueProduto.local_id == local_id
    ).first()
    
    if not estoque:
        # Criar registro de estoque se não existir
        estoque = EstoqueProduto(
            produto_id=movimentacao_data.produto_id,
            local_id=local_id,
            quantidade_atual=0,
            quantidade_disponivel=0
        )
        db.add(estoque)
        db.flush()
    
    # Calcular saldos
    saldo_anterior = estoque.quantidade_atual
    tipo_mov = TipoMovimentacaoEstoque(movimentacao_data.tipo_movimentacao)
    
    if "entrada" in tipo_mov.value:
        novo_saldo = saldo_anterior + movimentacao_data.quantidade
    else:  # saída
        novo_saldo = saldo_anterior - movimentacao_data.quantidade
        if novo_saldo < 0:
            raise HTTPException(status_code=400, detail="Estoque insuficiente")
    
    # Criar movimentação
    movimentacao = MovimentacaoEstoque(
        estoque_produto_id=estoque.id,
        produto_id=movimentacao_data.produto_id,
        local_origem_id=movimentacao_data.local_origem_id,
        local_destino_id=movimentacao_data.local_destino_id,
        tipo_movimentacao=tipo_mov,
        quantidade=movimentacao_data.quantidade,
        valor_unitario=movimentacao_data.valor_unitario,
        valor_total=(movimentacao_data.valor_unitario or 0) * movimentacao_data.quantidade,
        numero_documento=movimentacao_data.numero_documento,
        observacoes=movimentacao_data.observacoes,
        saldo_anterior=saldo_anterior,
        saldo_atual=novo_saldo,
        criado_por_id=current_user.id
    )
    
    # Atualizar estoque
    estoque.quantidade_atual = novo_saldo
    estoque.quantidade_disponivel = novo_saldo - estoque.quantidade_reservada
    estoque.ultima_movimentacao = datetime.utcnow()
    
    # Atualizar custos para entradas
    if "entrada" in tipo_mov.value and movimentacao_data.valor_unitario:
        if estoque.metodo_controle == MetodoControleEstoque.CUSTO_MEDIO:
            # Calcular custo médio
            valor_estoque_anterior = float(saldo_anterior * estoque.custo_medio)
            valor_entrada = float(movimentacao_data.quantidade * movimentacao_data.valor_unitario)
            estoque.custo_medio = (valor_estoque_anterior + valor_entrada) / float(novo_saldo)
        
        estoque.ultimo_custo = movimentacao_data.valor_unitario
        estoque.ultima_compra = datetime.utcnow()
    
    if "saida" in tipo_mov.value:
        estoque.ultima_venda = datetime.utcnow()
    
    db.add(movimentacao)
    db.commit()
    
    return {
        "id": movimentacao.id,
        "saldo_anterior": float(saldo_anterior),
        "saldo_atual": float(novo_saldo),
        "message": "Movimentação criada com sucesso"
    }

# ================================================================================
# ENDPOINTS - ALERTAS E DASHBOARDS
# ================================================================================

@router.get("/alertas")
async def obter_alertas_estoque(
    empresa_id: Optional[int] = Query(None),
    local_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter alertas de estoque (baixo, alto, zerado)"""
    
    query = db.query(
        EstoqueProduto,
        Produto.nome.label('produto_nome'),
        Produto.codigo.label('produto_codigo'),
        LocalEstoque.nome.label('local_nome')
    ).join(Produto).join(LocalEstoque)
    
    if empresa_id:
        query = query.filter(LocalEstoque.empresa_id == empresa_id)
    if local_id:
        query = query.filter(EstoqueProduto.local_id == local_id)
    
    estoques = query.all()
    
    alertas = {
        "estoque_zerado": [],
        "estoque_baixo": [],
        "estoque_alto": [],
        "sem_movimentacao": []
    }
    
    data_limite = datetime.utcnow() - timedelta(days=90)  # 3 meses sem movimentação
    
    for estoque, produto_nome, produto_codigo, local_nome in estoques:
        item_alerta = {
            "produto_id": estoque.produto_id,
            "produto_nome": produto_nome,
            "produto_codigo": produto_codigo,
            "local_id": estoque.local_id,
            "local_nome": local_nome,
            "quantidade_atual": float(estoque.quantidade_atual),
            "estoque_minimo": float(estoque.estoque_minimo),
            "estoque_maximo": float(estoque.estoque_maximo or 0),
            "ultima_movimentacao": estoque.ultima_movimentacao
        }
        
        if estoque.quantidade_atual <= 0:
            alertas["estoque_zerado"].append(item_alerta)
        elif estoque.quantidade_atual <= estoque.estoque_minimo:
            alertas["estoque_baixo"].append(item_alerta)
        elif estoque.estoque_maximo and estoque.quantidade_atual >= estoque.estoque_maximo:
            alertas["estoque_alto"].append(item_alerta)
        
        if estoque.ultima_movimentacao and estoque.ultima_movimentacao < data_limite:
            alertas["sem_movimentacao"].append(item_alerta)
    
    return {
        "alertas": alertas,
        "resumo": {
            "total_estoque_zerado": len(alertas["estoque_zerado"]),
            "total_estoque_baixo": len(alertas["estoque_baixo"]),
            "total_estoque_alto": len(alertas["estoque_alto"]),
            "total_sem_movimentacao": len(alertas["sem_movimentacao"])
        }
    }

@router.get("/dashboard")
async def obter_dashboard_estoque(
    empresa_id: Optional[int] = Query(None),
    local_id: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Dashboard executivo do estoque"""
    
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    # Query base para estoque
    query_estoque = db.query(EstoqueProduto).join(LocalEstoque)
    if empresa_id:
        query_estoque = query_estoque.filter(LocalEstoque.empresa_id == empresa_id)
    if local_id:
        query_estoque = query_estoque.filter(EstoqueProduto.local_id == local_id)
    
    # KPIs básicos
    total_produtos = query_estoque.count()
    produtos_com_estoque = query_estoque.filter(EstoqueProduto.quantidade_atual > 0).count()
    produtos_sem_estoque = total_produtos - produtos_com_estoque
    
    # Valor total do estoque
    valor_total_estoque = db.query(
        func.sum(EstoqueProduto.quantidade_atual * EstoqueProduto.custo_medio)
    ).join(LocalEstoque).filter(
        LocalEstoque.empresa_id == empresa_id if empresa_id else True,
        EstoqueProduto.local_id == local_id if local_id else True
    ).scalar() or 0
    
    # Movimentações do período
    query_mov = db.query(MovimentacaoEstoque).filter(
        MovimentacaoEstoque.data_movimento >= data_inicio,
        MovimentacaoEstoque.data_movimento <= data_fim
    )
    
    total_movimentacoes = query_mov.count()
    total_entradas = query_mov.filter(MovimentacaoEstoque.tipo_movimentacao.like('%entrada%')).count()
    total_saidas = query_mov.filter(MovimentacaoEstoque.tipo_movimentacao.like('%saida%')).count()
    
    # Produtos mais movimentados
    produtos_movimentados = db.query(
        MovimentacaoEstoque.produto_id,
        Produto.nome.label('produto_nome'),
        func.sum(MovimentacaoEstoque.quantidade).label('total_movimentado')
    ).join(Produto).filter(
        MovimentacaoEstoque.data_movimento >= data_inicio,
        MovimentacaoEstoque.data_movimento <= data_fim
    ).group_by(
        MovimentacaoEstoque.produto_id, Produto.nome
    ).order_by(desc('total_movimentado')).limit(10).all()
    
    return {
        "periodo": {
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat()
        },
        "kpis": {
            "total_produtos": total_produtos,
            "produtos_com_estoque": produtos_com_estoque,
            "produtos_sem_estoque": produtos_sem_estoque,
            "percentual_disponibilidade": (produtos_com_estoque / total_produtos * 100) if total_produtos > 0 else 0,
            "valor_total_estoque": float(valor_total_estoque),
            "total_movimentacoes": total_movimentacoes,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas
        },
        "produtos_mais_movimentados": [
            {
                "produto_id": p.produto_id,
                "produto_nome": p.produto_nome,
                "total_movimentado": float(p.total_movimentado)
            }
            for p in produtos_movimentados
        ]
    }

@router.post("/atualizar-estatisticas", response_model=dict)
async def atualizar_estatisticas_endpoint(
    produto_id: Optional[int] = Query(None),
    local_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar estatísticas de giro e cobertura de estoque"""
    try:
        from ..utils.estoque_utils import EstoqueService
        estoque_service = EstoqueService(db)
        estoque_service.atualizar_estatisticas_estoque(produto_id, local_id)
        return {"message": "Estatísticas atualizadas com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reservar", response_model=dict)
async def reservar_estoque_endpoint(
    request: dict,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Reservar quantidade do estoque"""
    try:
        from ..utils.estoque_utils import EstoqueService
        estoque_service = EstoqueService(db)
        
        sucesso = estoque_service.reservar_estoque(
            request["produto_id"],
            request["local_id"],
            Decimal(str(request["quantidade"]))
        )
        
        return {"sucesso": sucesso}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/liberar-reserva", response_model=dict)
async def liberar_reserva_endpoint(
    request: dict,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Liberar reserva de estoque"""
    try:
        from ..utils.estoque_utils import EstoqueService
        estoque_service = EstoqueService(db)
        
        estoque_service.liberar_reserva(
            request["produto_id"],
            request["local_id"],
            Decimal(str(request["quantidade"]))
        )
        
        return {"message": "Reserva liberada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
