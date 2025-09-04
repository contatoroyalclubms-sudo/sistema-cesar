from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models import (
    ProdutoEstoque, MovimentoEstoque, LocalEstoque, CategoriaEstoque,
    AlertaEstoque, ContagemEstoque, ItemContagem, Usuario
)
from ..schemas_extended import (
    ProdutoEstoqueCreate, ProdutoEstoqueUpdate, ProdutoEstoqueResponse,
    MovimentoEstoqueCreate, MovimentoEstoqueResponse,
    LocalEstoqueCreate, LocalEstoqueUpdate, LocalEstoqueResponse,
    CategoriaEstoqueCreate, CategoriaEstoqueUpdate, CategoriaEstoqueResponse,
    AlertaEstoqueResponse, ContagemEstoqueCreate, ContagemEstoqueResponse,
    ItemContagemCreate, ItemContagemUpdate
)
from ..auth_functions import obter_usuario_atual as get_current_user

router = APIRouter(prefix="/api/estoque", tags=["estoque"])

# ============= PRODUTOS ESTOQUE =============
@router.get("/produtos", response_model=List[ProdutoEstoqueResponse])
def listar_produtos_estoque(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    categoria_id: Optional[int] = None,
    local_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos os produtos em estoque com filtros"""
    query = db.query(ProdutoEstoque)
    
    if search:
        query = query.filter(
            or_(
                ProdutoEstoque.nome.ilike(f"%{search}%"),
                ProdutoEstoque.codigo.ilike(f"%{search}%"),
                ProdutoEstoque.sku.ilike(f"%{search}%")
            )
        )
    
    if categoria_id:
        query = query.filter(ProdutoEstoque.categoria_id == categoria_id)
    
    if local_id:
        query = query.filter(ProdutoEstoque.local_id == local_id)
    
    return query.offset(skip).limit(limit).all()

@router.post("/produtos", response_model=ProdutoEstoqueResponse)
def criar_produto_estoque(
    produto: ProdutoEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo produto no estoque"""
    # Verificar se SKU já existe
    if produto.sku:
        existing = db.query(ProdutoEstoque).filter(ProdutoEstoque.sku == produto.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="SKU já cadastrado")
    
    db_produto = ProdutoEstoque(**produto.dict())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    
    # Criar movimento de entrada inicial se houver quantidade
    if produto.quantidade_atual > 0:
        movimento = MovimentoEstoque(
            produto_estoque_id=db_produto.id,
            tipo_movimento='entrada',
            quantidade=produto.quantidade_atual,
            motivo='Estoque inicial',
            usuario_id=current_user.id,
            local_origem_id=produto.local_id,
            local_destino_id=produto.local_id
        )
        db.add(movimento)
        db.commit()
    
    return db_produto

@router.get("/produtos/{produto_id}", response_model=ProdutoEstoqueResponse)
def obter_produto_estoque(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtúm detalhes de um produto especúfico"""
    produto = db.query(ProdutoEstoque).filter(ProdutoEstoque.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto núo encontrado")
    return produto

@router.put("/produtos/{produto_id}", response_model=ProdutoEstoqueResponse)
def atualizar_produto_estoque(
    produto_id: int,
    produto_update: ProdutoEstoqueUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza informaúúes de um produto"""
    produto = db.query(ProdutoEstoque).filter(ProdutoEstoque.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto núo encontrado")
    
    for key, value in produto_update.dict(exclude_unset=True).items():
        setattr(produto, key, value)
    
    produto.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(produto)
    return produto

# ============= MOVIMENTAúúES =============
@router.get("/movimentos", response_model=List[MovimentoEstoqueResponse])
def listar_movimentos(
    skip: int = 0,
    limit: int = 100,
    produto_id: Optional[int] = None,
    tipo: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista movimentaúúes de estoque com filtros"""
    query = db.query(MovimentoEstoque)
    
    if produto_id:
        query = query.filter(MovimentoEstoque.produto_estoque_id == produto_id)
    
    if tipo:
        query = query.filter(MovimentoEstoque.tipo_movimento == tipo)
    
    if data_inicio:
        query = query.filter(MovimentoEstoque.data_movimento >= data_inicio)
    
    if data_fim:
        query = query.filter(MovimentoEstoque.data_movimento <= data_fim + timedelta(days=1))
    
    return query.order_by(MovimentoEstoque.data_movimento.desc()).offset(skip).limit(limit).all()

@router.post("/movimentos", response_model=MovimentoEstoqueResponse)
def criar_movimento(
    movimento: MovimentoEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registra uma movimentaúúo de estoque"""
    # Buscar produto
    produto = db.query(ProdutoEstoque).filter(ProdutoEstoque.id == movimento.produto_estoque_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto núo encontrado")
    
    # Validar quantidade disponúvel para saúda/transferência
    if movimento.tipo_movimento in ['saida', 'transferencia']:
        if produto.quantidade_atual < movimento.quantidade:
            raise HTTPException(
                status_code=400, 
                detail=f"Quantidade insuficiente. Disponúvel: {produto.quantidade_atual}"
            )
    
    # Criar movimento
    db_movimento = MovimentoEstoque(
        **movimento.dict(),
        usuario_id=current_user.id
    )
    db.add(db_movimento)
    
    # Atualizar quantidade do produto
    if movimento.tipo_movimento == 'entrada':
        produto.quantidade_atual += movimento.quantidade
    elif movimento.tipo_movimento == 'saida':
        produto.quantidade_atual -= movimento.quantidade
    elif movimento.tipo_movimento == 'ajuste':
        produto.quantidade_atual = movimento.quantidade_nova
    elif movimento.tipo_movimento == 'transferencia':
        # Para transferência, apenas registrar movimento (ajuste de local feito separadamente)
        produto.quantidade_atual -= movimento.quantidade
        if movimento.local_destino_id:
            produto.local_id = movimento.local_destino_id
    
    # Verificar alertas de estoque
    if produto.quantidade_atual <= produto.estoque_minimo:
        alerta = AlertaEstoque(
            produto_estoque_id=produto.id,
            tipo_alerta='estoque_minimo',
            descricao=f"Produto {produto.nome} atingiu estoque múnimo",
            nivel_critico='alto' if produto.quantidade_atual == 0 else 'medio'
        )
        db.add(alerta)
    
    produto.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(db_movimento)
    return db_movimento

# ============= LOCAIS DE ESTOQUE =============
@router.get("/locais", response_model=List[LocalEstoqueResponse])
def listar_locais(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos os locais de estoque"""
    return db.query(LocalEstoque).offset(skip).limit(limit).all()

@router.post("/locais", response_model=LocalEstoqueResponse)
def criar_local(
    local: LocalEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo local de estoque"""
    # Verificar se código já existe
    existing = db.query(LocalEstoque).filter(LocalEstoque.codigo == local.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código de local já existe")
    
    db_local = LocalEstoque(**local.dict())
    db.add(db_local)
    db.commit()
    db.refresh(db_local)
    return db_local

@router.put("/locais/{local_id}", response_model=LocalEstoqueResponse)
def atualizar_local(
    local_id: int,
    local_update: LocalEstoqueUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza informaúúes de um local"""
    local = db.query(LocalEstoque).filter(LocalEstoque.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local núo encontrado")
    
    for key, value in local_update.dict(exclude_unset=True).items():
        setattr(local, key, value)
    
    db.commit()
    db.refresh(local)
    return local

# ============= CATEGORIAS =============
@router.get("/categorias", response_model=List[CategoriaEstoqueResponse])
def listar_categorias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todas as categorias de estoque"""
    return db.query(CategoriaEstoque).offset(skip).limit(limit).all()

@router.post("/categorias", response_model=CategoriaEstoqueResponse)
def criar_categoria(
    categoria: CategoriaEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma nova categoria"""
    db_categoria = CategoriaEstoque(**categoria.dict())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.put("/categorias/{categoria_id}", response_model=CategoriaEstoqueResponse)
def atualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaEstoqueUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza uma categoria"""
    categoria = db.query(CategoriaEstoque).filter(CategoriaEstoque.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria núo encontrada")
    
    for key, value in categoria_update.dict(exclude_unset=True).items():
        setattr(categoria, key, value)
    
    db.commit()
    db.refresh(categoria)
    return categoria

# ============= ALERTAS =============
@router.get("/alertas", response_model=List[AlertaEstoqueResponse])
def listar_alertas(
    apenas_ativos: bool = True,
    nivel_critico: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista alertas de estoque"""
    query = db.query(AlertaEstoque)
    
    if apenas_ativos:
        query = query.filter(AlertaEstoque.resolvido == False)
    
    if nivel_critico:
        query = query.filter(AlertaEstoque.nivel_critico == nivel_critico)
    
    return query.order_by(AlertaEstoque.criado_em.desc()).all()

@router.patch("/alertas/{alerta_id}/resolver")
def resolver_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Marca um alerta como resolvido"""
    alerta = db.query(AlertaEstoque).filter(AlertaEstoque.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta núo encontrado")
    
    alerta.resolvido = True
    alerta.resolvido_em = datetime.utcnow()
    alerta.resolvido_por_id = current_user.id
    db.commit()
    
    return {"message": "Alerta resolvido com sucesso"}

# ============= CONTAGEM/INVENTúRIO =============
@router.get("/contagens", response_model=List[ContagemEstoqueResponse])
def listar_contagens(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista contagens de inventário"""
    query = db.query(ContagemEstoque)
    
    if status:
        query = query.filter(ContagemEstoque.status == status)
    
    return query.order_by(ContagemEstoque.data_contagem.desc()).offset(skip).limit(limit).all()

@router.post("/contagens", response_model=ContagemEstoqueResponse)
def criar_contagem(
    contagem: ContagemEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma nova contagem de inventário"""
    db_contagem = ContagemEstoque(
        **contagem.dict(),
        usuario_responsavel_id=current_user.id,
        status='em_andamento'
    )
    db.add(db_contagem)
    db.commit()
    
    # Criar itens de contagem para produtos selecionados ou todos
    if contagem.produtos_ids:
        produtos = db.query(ProdutoEstoque).filter(
            ProdutoEstoque.id.in_(contagem.produtos_ids)
        ).all()
    else:
        produtos = db.query(ProdutoEstoque).all()
    
    for produto in produtos:
        item = ItemContagem(
            contagem_id=db_contagem.id,
            produto_estoque_id=produto.id,
            quantidade_sistema=produto.quantidade_atual,
            quantidade_contada=0
        )
        db.add(item)
    
    db.commit()
    db.refresh(db_contagem)
    return db_contagem

@router.put("/contagens/{contagem_id}/itens/{item_id}")
def atualizar_item_contagem(
    contagem_id: int,
    item_id: int,
    item_update: ItemContagemUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza quantidade contada de um item"""
    item = db.query(ItemContagem).filter(
        and_(
            ItemContagem.id == item_id,
            ItemContagem.contagem_id == contagem_id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item núo encontrado")
    
    item.quantidade_contada = item_update.quantidade_contada
    item.observacoes = item_update.observacoes
    
    # Calcular divergúncia
    item.divergencia = item.quantidade_contada - item.quantidade_sistema
    
    db.commit()
    return {"message": "Item atualizado com sucesso"}

@router.post("/contagens/{contagem_id}/finalizar")
def finalizar_contagem(
    contagem_id: int,
    aplicar_ajustes: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Finaliza uma contagem e opcionalmente aplica ajustes"""
    contagem = db.query(ContagemEstoque).filter(ContagemEstoque.id == contagem_id).first()
    if not contagem:
        raise HTTPException(status_code=404, detail="Contagem núo encontrada")
    
    if contagem.status != 'em_andamento':
        raise HTTPException(status_code=400, detail="Contagem já foi finalizada")
    
    # Buscar itens com divergúncia
    itens_divergentes = db.query(ItemContagem).filter(
        and_(
            ItemContagem.contagem_id == contagem_id,
            ItemContagem.divergencia != 0
        )
    ).all()
    
    if aplicar_ajustes and itens_divergentes:
        for item in itens_divergentes:
            # Criar movimento de ajuste
            movimento = MovimentoEstoque(
                produto_estoque_id=item.produto_estoque_id,
                tipo_movimento='ajuste',
                quantidade=abs(item.divergencia),
                quantidade_nova=item.quantidade_contada,
                motivo=f'Ajuste de inventário - Contagem #{contagem_id}',
                usuario_id=current_user.id
            )
            db.add(movimento)
            
            # Atualizar quantidade do produto
            produto = db.query(ProdutoEstoque).filter(
                ProdutoEstoque.id == item.produto_estoque_id
            ).first()
            produto.quantidade_atual = item.quantidade_contada
            produto.atualizado_em = datetime.utcnow()
    
    contagem.status = 'finalizada'
    contagem.finalizada_em = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Contagem finalizada com sucesso",
        "divergencias": len(itens_divergentes),
        "ajustes_aplicados": aplicar_ajustes
    }

# ============= RELATúRIOS =============
@router.get("/relatorios/posicao-estoque")
def relatorio_posicao_estoque(
    categoria_id: Optional[int] = None,
    local_id: Optional[int] = None,
    incluir_zerados: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Gera relatúrio de posiúúo atual do estoque"""
    query = db.query(ProdutoEstoque)
    
    if categoria_id:
        query = query.filter(ProdutoEstoque.categoria_id == categoria_id)
    
    if local_id:
        query = query.filter(ProdutoEstoque.local_id == local_id)
    
    if not incluir_zerados:
        query = query.filter(ProdutoEstoque.quantidade_atual > 0)
    
    produtos = query.all()
    
    # Calcular totais
    total_itens = len(produtos)
    total_quantidade = sum(p.quantidade_atual for p in produtos)
    valor_total = sum(p.quantidade_atual * p.custo_unitario for p in produtos if p.custo_unitario)
    
    # Produtos abaixo do múnimo
    produtos_criticos = [p for p in produtos if p.quantidade_atual <= p.estoque_minimo]
    
    return {
        "data_relatorio": datetime.utcnow(),
        "resumo": {
            "total_itens": total_itens,
            "total_quantidade": total_quantidade,
            "valor_total_estoque": valor_total,
            "produtos_criticos": len(produtos_criticos)
        },
        "produtos": produtos,
        "produtos_criticos": produtos_criticos
    }

@router.get("/relatorios/movimentacao")
def relatorio_movimentacao(
    data_inicio: date,
    data_fim: date,
    produto_id: Optional[int] = None,
    tipo_movimento: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Gera relatúrio de movimentaúúo de estoque"""
    query = db.query(MovimentoEstoque).filter(
        and_(
            MovimentoEstoque.data_movimento >= data_inicio,
            MovimentoEstoque.data_movimento <= data_fim + timedelta(days=1)
        )
    )
    
    if produto_id:
        query = query.filter(MovimentoEstoque.produto_estoque_id == produto_id)
    
    if tipo_movimento:
        query = query.filter(MovimentoEstoque.tipo_movimento == tipo_movimento)
    
    movimentos = query.all()
    
    # Agrupar por tipo
    resumo_por_tipo = {}
    for mov in movimentos:
        if mov.tipo_movimento not in resumo_por_tipo:
            resumo_por_tipo[mov.tipo_movimento] = {
                "quantidade_movimentos": 0,
                "quantidade_total": 0
            }
        resumo_por_tipo[mov.tipo_movimento]["quantidade_movimentos"] += 1
        resumo_por_tipo[mov.tipo_movimento]["quantidade_total"] += mov.quantidade
    
    return {
        "periodo": {
            "inicio": data_inicio,
            "fim": data_fim
        },
        "total_movimentos": len(movimentos),
        "resumo_por_tipo": resumo_por_tipo,
        "movimentos": movimentos
    }

@router.get("/relatorios/abc")
def analise_abc(
    periodo_dias: int = 90,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Anúlise ABC de produtos baseada em movimentaúúo"""
    data_inicio = datetime.utcnow() - timedelta(days=periodo_dias)
    
    # Buscar movimentaúúes de saúda no perúodo
    movimentos = db.query(
        MovimentoEstoque.produto_estoque_id,
        func.sum(MovimentoEstoque.quantidade).label('total_saida')
    ).filter(
        and_(
            MovimentoEstoque.tipo_movimento == 'saida',
            MovimentoEstoque.data_movimento >= data_inicio
        )
    ).group_by(MovimentoEstoque.produto_estoque_id).all()
    
    # Calcular valor total e ordenar
    produtos_analise = []
    for mov in movimentos:
        produto = db.query(ProdutoEstoque).filter(ProdutoEstoque.id == mov.produto_estoque_id).first()
        if produto:
            valor_movimento = mov.total_saida * (produto.custo_unitario or 0)
            produtos_analise.append({
                "produto": produto,
                "quantidade_saida": mov.total_saida,
                "valor_movimento": valor_movimento
            })
    
    # Ordenar por valor de movimento
    produtos_analise.sort(key=lambda x: x['valor_movimento'], reverse=True)
    
    # Classificar ABC
    valor_total = sum(p['valor_movimento'] for p in produtos_analise)
    valor_acumulado = 0
    
    for item in produtos_analise:
        valor_acumulado += item['valor_movimento']
        percentual_acumulado = (valor_acumulado / valor_total * 100) if valor_total > 0 else 0
        
        if percentual_acumulado <= 80:
            item['classificacao'] = 'A'
        elif percentual_acumulado <= 95:
            item['classificacao'] = 'B'
        else:
            item['classificacao'] = 'C'
    
    # Agrupar por classificaúúo
    classificacao_resumo = {
        'A': [p for p in produtos_analise if p.get('classificacao') == 'A'],
        'B': [p for p in produtos_analise if p.get('classificacao') == 'B'],
        'C': [p for p in produtos_analise if p.get('classificacao') == 'C']
    }
    
    return {
        "periodo_analise": f"últimos {periodo_dias} dias",
        "data_inicio": data_inicio,
        "data_fim": datetime.utcnow(),
        "resumo": {
            "classe_A": {
                "quantidade": len(classificacao_resumo['A']),
                "percentual_itens": len(classificacao_resumo['A']) / len(produtos_analise) * 100 if produtos_analise else 0
            },
            "classe_B": {
                "quantidade": len(classificacao_resumo['B']),
                "percentual_itens": len(classificacao_resumo['B']) / len(produtos_analise) * 100 if produtos_analise else 0
            },
            "classe_C": {
                "quantidade": len(classificacao_resumo['C']),
                "percentual_itens": len(classificacao_resumo['C']) / len(produtos_analise) * 100 if produtos_analise else 0
            }
        },
        "produtos": produtos_analise
    }