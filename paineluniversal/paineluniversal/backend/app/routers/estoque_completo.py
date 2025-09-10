"""
Router para Estoque Completo - Sistema de controle de estoque avançado
Movimentações, inventário, alertas, fornecedores e compras
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Usuario, Produto, MovimentacaoEstoque, Fornecedor, CompraFornecedor,
    ItemCompra, InventarioFisico, ItemInventario, AlertaEstoque,
    LocalEstoque, TransferenciaEstoque, CategoriaEstoque
)
from ..schemas_meep_complete import (
    MovimentacaoEstoqueCreate, MovimentacaoEstoqueResponse
)

router = APIRouter(
    prefix="/api/estoque",
    tags=["Estoque & Inventário"]
)

@router.get("/dashboard")
async def dashboard_estoque(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard do estoque com visão geral
    Replica funcionalidade: Sistema Estoque > Dashboard
    """
    
    # Produtos em falta (estoque zero ou abaixo do mínimo)
    produtos_falta = db.query(Produto).filter(
        or_(
            Produto.estoque_atual <= 0,
            Produto.estoque_atual <= Produto.estoque_minimo
        )
    ).count()
    
    # Valor total do estoque
    valor_total_estoque = db.query(
        func.sum(Produto.estoque_atual * Produto.preco_custo)
    ).filter(
        Produto.preco_custo.isnot(None)
    ).scalar() or Decimal(0)
    
    # Produtos mais movimentados (30 dias)
    data_inicio = datetime.now() - timedelta(days=30)
    
    produtos_movimentados = db.query(
        Produto.nome,
        func.sum(MovimentacaoEstoque.quantidade).label("total_movimentacao")
    ).join(
        MovimentacaoEstoque,
        MovimentacaoEstoque.produto_id == Produto.id
    ).filter(
        MovimentacaoEstoque.criado_em >= data_inicio
    ).group_by(
        Produto.id, Produto.nome
    ).order_by(
        desc("total_movimentacao")
    ).limit(10).all()
    
    # Alertas ativos
    alertas_ativos = db.query(AlertaEstoque).filter(
        AlertaEstoque.ativo == True
    ).count()
    
    # Movimentações hoje
    hoje = date.today()
    movimentacoes_hoje = db.query(MovimentacaoEstoque).filter(
        func.date(MovimentacaoEstoque.criado_em) == hoje
    ).count()
    
    return {
        "resumo": {
            "produtos_total": db.query(func.count(Produto.id)).scalar(),
            "produtos_falta": produtos_falta,
            "valor_total_estoque": float(valor_total_estoque),
            "alertas_ativos": alertas_ativos,
            "movimentacoes_hoje": movimentacoes_hoje
        },
        "produtos_mais_movimentados": [
            {
                "produto": p.nome,
                "movimentacao": float(p.total_movimentacao)
            }
            for p in produtos_movimentados
        ],
        "alertas": [
            "Produtos em falta: {}".format(produtos_falta),
            "Alertas ativos: {}".format(alertas_ativos)
        ]
    }

@router.post("/movimentacao/create", response_model=MovimentacaoEstoqueResponse)
async def criar_movimentacao(
    movimentacao: MovimentacaoEstoqueCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar movimentação de estoque
    Replica funcionalidade: Sistema Estoque > Nova Movimentação
    """
    
    # Buscar produto
    produto = db.query(Produto).filter(
        Produto.id == movimentacao.produto_id
    ).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Calcular saldos
    saldo_anterior = produto.estoque_atual
    
    if movimentacao.tipo_operacao in ["ENTRADA", "TRANSFERENCIA_ENTRADA", "AJUSTE_POSITIVO"]:
        saldo_posterior = saldo_anterior + movimentacao.quantidade
    else:  # SAIDA, TRANSFERENCIA_SAIDA, AJUSTE_NEGATIVO
        saldo_posterior = saldo_anterior - movimentacao.quantidade
        
        # Verificar se há estoque suficiente
        if saldo_posterior < 0 and movimentacao.tipo_operacao != "AJUSTE_NEGATIVO":
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Disponível: {saldo_anterior}"
            )
    
    # Criar movimentação
    nova_movimentacao = MovimentacaoEstoque(
        produto_id=movimentacao.produto_id,
        tipo_operacao=movimentacao.tipo_operacao,
        quantidade=movimentacao.quantidade,
        saldo_anterior=saldo_anterior,
        saldo_posterior=saldo_posterior,
        motivo=movimentacao.motivo,
        documento=movimentacao.documento,
        usuario_id=movimentacao.usuario_id
    )
    
    db.add(nova_movimentacao)
    
    # Atualizar estoque do produto
    produto.estoque_atual = saldo_posterior
    
    # Verificar alertas
    if saldo_posterior <= produto.estoque_minimo:
        # Criar alerta de estoque baixo
        alerta_existente = db.query(AlertaEstoque).filter(
            and_(
                AlertaEstoque.produto_id == produto.id,
                AlertaEstoque.tipo == "ESTOQUE_BAIXO",
                AlertaEstoque.ativo == True
            )
        ).first()
        
        if not alerta_existente:
            alerta = AlertaEstoque(
                produto_id=produto.id,
                tipo="ESTOQUE_BAIXO",
                mensagem=f"Produto {produto.nome} com estoque baixo: {saldo_posterior}",
                nivel="MEDIO",
                ativo=True
            )
            db.add(alerta)
    
    db.commit()
    db.refresh(nova_movimentacao)
    
    return nova_movimentacao

@router.get("/movimentacoes", response_model=List[MovimentacaoEstoqueResponse])
async def listar_movimentacoes(
    produto_id: Optional[int] = None,
    tipo_operacao: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar movimentações de estoque com filtros
    """
    
    query = db.query(MovimentacaoEstoque)
    
    if produto_id:
        query = query.filter(MovimentacaoEstoque.produto_id == produto_id)
    
    if tipo_operacao:
        query = query.filter(MovimentacaoEstoque.tipo_operacao == tipo_operacao)
    
    if data_inicio:
        query = query.filter(func.date(MovimentacaoEstoque.criado_em) >= data_inicio)
    
    if data_fim:
        query = query.filter(func.date(MovimentacaoEstoque.criado_em) <= data_fim)
    
    movimentacoes = query.order_by(
        desc(MovimentacaoEstoque.criado_em)
    ).limit(limit).all()
    
    return movimentacoes

@router.post("/inventario/create")
async def criar_inventario(
    local_id: Optional[int] = None,
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar novo inventário físico
    Replica funcionalidade: Sistema Estoque > Inventário
    """
    
    # Criar inventário
    novo_inventario = InventarioFisico(
        codigo=f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        local_id=local_id,
        usuario_id=current_user.id,
        observacoes=observacoes,
        status="EM_ANDAMENTO"
    )
    
    db.add(novo_inventario)
    db.flush()
    
    # Adicionar todos os produtos ao inventário
    produtos = db.query(Produto).filter(Produto.ativo == True).all()
    
    for produto in produtos:
        item = ItemInventario(
            inventario_id=novo_inventario.id,
            produto_id=produto.id,
            estoque_sistema=produto.estoque_atual,
            estoque_fisico=None,  # A ser preenchido durante contagem
            diferenca=None
        )
        db.add(item)
    
    db.commit()
    db.refresh(novo_inventario)
    
    return {
        "id": novo_inventario.id,
        "codigo": novo_inventario.codigo,
        "status": novo_inventario.status,
        "total_produtos": len(produtos)
    }

@router.put("/inventario/{inventario_id}/item/{item_id}")
async def atualizar_item_inventario(
    inventario_id: int,
    item_id: int,
    estoque_fisico: Decimal,
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar contagem de item do inventário
    """
    
    item = db.query(ItemInventario).filter(
        and_(
            ItemInventario.id == item_id,
            ItemInventario.inventario_id == inventario_id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    # Atualizar contagem
    item.estoque_fisico = estoque_fisico
    item.diferenca = estoque_fisico - item.estoque_sistema
    item.observacoes = observacoes
    item.contado_em = datetime.now()
    
    db.commit()
    
    return {
        "item_id": item_id,
        "estoque_sistema": float(item.estoque_sistema),
        "estoque_fisico": float(estoque_fisico),
        "diferenca": float(item.diferenca)
    }

@router.post("/inventario/{inventario_id}/finalizar")
async def finalizar_inventario(
    inventario_id: int,
    aplicar_ajustes: bool = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalizar inventário e aplicar ajustes
    Replica funcionalidade: Sistema Estoque > Finalizar Inventário
    """
    
    inventario = db.query(InventarioFisico).filter(
        InventarioFisico.id == inventario_id
    ).first()
    
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventário não encontrado")
    
    if inventario.status != "EM_ANDAMENTO":
        raise HTTPException(status_code=400, detail="Inventário já finalizado")
    
    # Buscar itens com diferenças
    itens = db.query(ItemInventario).filter(
        and_(
            ItemInventario.inventario_id == inventario_id,
            ItemInventario.diferenca != 0
        )
    ).all()
    
    ajustes_aplicados = 0
    
    if aplicar_ajustes:
        for item in itens:
            if item.diferenca != 0:
                # Criar movimentação de ajuste
                tipo_operacao = "AJUSTE_POSITIVO" if item.diferenca > 0 else "AJUSTE_NEGATIVO"
                quantidade = abs(item.diferenca)
                
                movimentacao = MovimentacaoEstoque(
                    produto_id=item.produto_id,
                    tipo_operacao=tipo_operacao,
                    quantidade=quantidade,
                    saldo_anterior=item.estoque_sistema,
                    saldo_posterior=item.estoque_fisico,
                    motivo=f"Ajuste por inventário {inventario.codigo}",
                    documento=inventario.codigo,
                    usuario_id=current_user.id
                )
                db.add(movimentacao)
                
                # Atualizar estoque do produto
                produto = db.query(Produto).filter(
                    Produto.id == item.produto_id
                ).first()
                if produto:
                    produto.estoque_atual = item.estoque_fisico
                
                ajustes_aplicados += 1
    
    # Finalizar inventário
    inventario.status = "CONCLUIDO"
    inventario.finalizado_em = datetime.now()
    
    db.commit()
    
    return {
        "inventario_id": inventario_id,
        "status": "CONCLUIDO",
        "total_diferencas": len(itens),
        "ajustes_aplicados": ajustes_aplicados
    }

@router.post("/fornecedores/create")
async def criar_fornecedor(
    nome: str,
    cnpj: Optional[str] = None,
    contato: Optional[str] = None,
    email: Optional[str] = None,
    telefone: Optional[str] = None,
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cadastrar novo fornecedor
    Replica funcionalidade: Sistema Estoque > Fornecedores
    """
    
    novo_fornecedor = Fornecedor(
        nome=nome,
        cnpj=cnpj,
        contato=contato,
        email=email,
        telefone=telefone,
        observacoes=observacoes,
        empresa_id=current_user.empresa_id,
        ativo=True
    )
    
    db.add(novo_fornecedor)
    db.commit()
    db.refresh(novo_fornecedor)
    
    return novo_fornecedor

@router.post("/compras/create")
async def criar_compra(
    fornecedor_id: int,
    itens: List[Dict[str, Any]] = Body(..., description="Lista de itens da compra"),
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar pedido de compra
    Replica funcionalidade: Sistema Estoque > Compras
    """
    
    # Gerar número da compra
    numero_compra = f"CP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Calcular total
    valor_total = Decimal(0)
    for item in itens:
        valor_total += Decimal(str(item["quantidade"])) * Decimal(str(item["preco_unitario"]))
    
    # Criar compra
    nova_compra = CompraFornecedor(
        numero_compra=numero_compra,
        fornecedor_id=fornecedor_id,
        valor_total=valor_total,
        observacoes=observacoes,
        usuario_id=current_user.id,
        status="PENDENTE"
    )
    
    db.add(nova_compra)
    db.flush()
    
    # Adicionar itens
    for item_data in itens:
        item = ItemCompra(
            compra_id=nova_compra.id,
            produto_id=item_data["produto_id"],
            quantidade=Decimal(str(item_data["quantidade"])),
            preco_unitario=Decimal(str(item_data["preco_unitario"])),
            valor_total=Decimal(str(item_data["quantidade"])) * Decimal(str(item_data["preco_unitario"]))
        )
        db.add(item)
    
    db.commit()
    db.refresh(nova_compra)
    
    return {
        "id": nova_compra.id,
        "numero_compra": numero_compra,
        "valor_total": float(valor_total),
        "status": nova_compra.status
    }

@router.put("/compras/{compra_id}/receber")
async def receber_compra(
    compra_id: int,
    itens_recebidos: List[Dict[str, Any]] = Body(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Receber itens de compra e dar entrada no estoque
    """
    
    compra = db.query(CompraFornecedor).filter(
        CompraFornecedor.id == compra_id
    ).first()
    
    if not compra:
        raise HTTPException(status_code=404, detail="Compra não encontrada")
    
    if compra.status != "PENDENTE":
        raise HTTPException(status_code=400, detail="Compra já foi processada")
    
    # Processar cada item recebido
    for item_recebido in itens_recebidos:
        produto_id = item_recebido["produto_id"]
        quantidade_recebida = Decimal(str(item_recebido["quantidade_recebida"]))
        
        if quantidade_recebida > 0:
            # Criar movimentação de entrada
            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            if produto:
                movimentacao = MovimentacaoEstoque(
                    produto_id=produto_id,
                    tipo_operacao="ENTRADA",
                    quantidade=quantidade_recebida,
                    saldo_anterior=produto.estoque_atual,
                    saldo_posterior=produto.estoque_atual + quantidade_recebida,
                    motivo=f"Recebimento compra {compra.numero_compra}",
                    documento=compra.numero_compra,
                    usuario_id=current_user.id
                )
                db.add(movimentacao)
                
                # Atualizar estoque
                produto.estoque_atual += quantidade_recebida
    
    # Atualizar status da compra
    compra.status = "RECEBIDA"
    compra.recebida_em = datetime.now()
    
    db.commit()
    
    return {
        "compra_id": compra_id,
        "status": "RECEBIDA",
        "message": "Compra recebida e estoque atualizado"
    }

@router.get("/alertas")
async def listar_alertas(
    ativo: bool = True,
    nivel: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar alertas de estoque
    Replica funcionalidade: Sistema Estoque > Alertas
    """
    
    query = db.query(AlertaEstoque)
    
    if ativo is not None:
        query = query.filter(AlertaEstoque.ativo == ativo)
    
    if nivel:
        query = query.filter(AlertaEstoque.nivel == nivel)
    
    alertas = query.order_by(desc(AlertaEstoque.criado_em)).all()
    
    return [
        {
            "id": a.id,
            "produto_id": a.produto_id,
            "tipo": a.tipo,
            "mensagem": a.mensagem,
            "nivel": a.nivel,
            "ativo": a.ativo,
            "criado_em": a.criado_em.isoformat()
        }
        for a in alertas
    ]

@router.get("/relatorio/giro")
async def relatorio_giro_estoque(
    periodo_dias: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Relatório de giro de estoque
    """
    
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Produtos com movimentação
    produtos_giro = db.query(
        Produto.id,
        Produto.nome,
        Produto.estoque_atual,
        func.sum(
            func.case(
                (MovimentacaoEstoque.tipo_operacao == "SAIDA", MovimentacaoEstoque.quantidade),
                else_=0
            )
        ).label("total_saidas"),
        func.avg(Produto.estoque_atual).label("estoque_medio")
    ).outerjoin(
        MovimentacaoEstoque,
        and_(
            MovimentacaoEstoque.produto_id == Produto.id,
            MovimentacaoEstoque.criado_em >= data_inicio
        )
    ).group_by(
        Produto.id, Produto.nome, Produto.estoque_atual
    ).all()
    
    resultado = []
    for produto in produtos_giro:
        if produto.total_saidas and produto.estoque_medio:
            giro = float(produto.total_saidas) / float(produto.estoque_medio)
        else:
            giro = 0
        
        resultado.append({
            "produto_id": produto.id,
            "produto_nome": produto.nome,
            "estoque_atual": float(produto.estoque_atual),
            "total_saidas": float(produto.total_saidas or 0),
            "giro_estoque": round(giro, 2),
            "classificacao": (
                "Alto" if giro > 4 else
                "Médio" if giro > 2 else
                "Baixo"
            )
        })
    
    # Ordenar por giro
    resultado.sort(key=lambda x: x["giro_estoque"], reverse=True)
    
    return {
        "periodo_dias": periodo_dias,
        "produtos": resultado[:50],  # Top 50
        "resumo": {
            "produtos_alto_giro": len([p for p in resultado if p["giro_estoque"] > 4]),
            "produtos_baixo_giro": len([p for p in resultado if p["giro_estoque"] < 2]),
            "giro_medio": sum(p["giro_estoque"] for p in resultado) / len(resultado) if resultado else 0
        }
    }
