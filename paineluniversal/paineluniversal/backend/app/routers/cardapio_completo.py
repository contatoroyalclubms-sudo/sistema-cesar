"""
Router para Cardápio Digital Completo - Funcionalidades avançadas
Gerenciamento de cardápios, categorias, modificadores e personalizações
"""

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import uuid
import qrcode
import io
import base64

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Usuario, Produto, Categoria, Cardapio, CardapioProduto,
    Empresa, Evento, ModificadorProduto, PersonalizacaoProduto
)
from ..schemas_meep_complete import (
    CardapioCreate, CardapioUpdate, CardapioResponse,
    ProdutoResponse
)

router = APIRouter(
    prefix="/api/cardapio",
    tags=["Cardápio Digital"]
)

@router.post("/create", response_model=CardapioResponse)
async def criar_cardapio(
    cardapio: CardapioCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar novo cardápio digital com QR Code
    Replica funcionalidade: Sistema Cardápio > Novo Cardápio
    """
    
    # Gerar UUID único
    cardapio_uuid = str(uuid.uuid4())
    
    # Criar cardápio
    novo_cardapio = Cardapio(
        nome=cardapio.nome,
        descricao=cardapio.descricao,
        tipo=cardapio.tipo,
        empresa_id=cardapio.empresa_id,
        uuid=cardapio_uuid,
        ativo=True
    )
    
    db.add(novo_cardapio)
    db.flush()
    
    # Adicionar produtos ao cardápio
    if cardapio.produto_ids:
        for ordem, produto_id in enumerate(cardapio.produto_ids):
            assoc = CardapioProduto(
                cardapio_id=novo_cardapio.id,
                produto_id=produto_id,
                ordem_exibicao=ordem
            )
            db.add(assoc)
    
    # Gerar URL digital
    novo_cardapio.url_digital = f"https://menu.sistema.com/{cardapio_uuid}"
    
    # Gerar QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(novo_cardapio.url_digital)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    novo_cardapio.qr_code_url = f"data:image/png;base64,{img_str}"
    
    db.commit()
    db.refresh(novo_cardapio)
    
    return novo_cardapio

@router.get("/list", response_model=List[CardapioResponse])
async def listar_cardapios(
    tipo: Optional[str] = None,
    ativo: Optional[bool] = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar cardápios da empresa
    """
    
    query = db.query(Cardapio)
    
    if current_user.empresa_id:
        query = query.filter(Cardapio.empresa_id == current_user.empresa_id)
    
    if tipo:
        query = query.filter(Cardapio.tipo == tipo)
    
    if ativo is not None:
        query = query.filter(Cardapio.ativo == ativo)
    
    cardapios = query.all()
    
    # Carregar produtos de cada cardápio
    for cardapio in cardapios:
        produtos = db.query(Produto).join(
            CardapioProduto,
            CardapioProduto.produto_id == Produto.id
        ).filter(
            CardapioProduto.cardapio_id == cardapio.id
        ).order_by(
            CardapioProduto.ordem_exibicao
        ).all()
        
        cardapio.produtos = produtos
    
    return cardapios

@router.put("/{cardapio_id}/reorder-products")
async def reordenar_produtos(
    cardapio_id: int,
    produto_ids: List[int] = Body(..., description="Lista de IDs na nova ordem"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reordenar produtos no cardápio (drag & drop)
    Replica funcionalidade: Sistema Cardápio > Arrastar e Soltar
    """
    
    # Verificar se cardápio existe
    cardapio = db.query(Cardapio).filter(
        Cardapio.id == cardapio_id
    ).first()
    
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Remover associações antigas
    db.query(CardapioProduto).filter(
        CardapioProduto.cardapio_id == cardapio_id
    ).delete()
    
    # Criar novas associações com nova ordem
    for ordem, produto_id in enumerate(produto_ids):
        assoc = CardapioProduto(
            cardapio_id=cardapio_id,
            produto_id=produto_id,
            ordem_exibicao=ordem
        )
        db.add(assoc)
    
    db.commit()
    
    return {"message": "Produtos reordenados com sucesso"}

@router.post("/categories/create")
async def criar_categoria(
    nome: str,
    descricao: Optional[str] = None,
    imagem_url: Optional[str] = None,
    ordem: Optional[int] = 0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar categoria de produtos
    """
    
    nova_categoria = Categoria(
        nome=nome,
        descricao=descricao,
        imagem_url=imagem_url,
        ordem_exibicao=ordem,
        empresa_id=current_user.empresa_id
    )
    
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    
    return nova_categoria

@router.get("/categories", response_model=List[Dict[str, Any]])
async def listar_categorias(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar categorias com contagem de produtos
    """
    
    categorias = db.query(
        Categoria,
        func.count(Produto.id).label("total_produtos")
    ).outerjoin(
        Produto,
        Produto.categoria_id == Categoria.id
    ).filter(
        Categoria.empresa_id == current_user.empresa_id if current_user.empresa_id else True
    ).group_by(
        Categoria.id
    ).order_by(
        Categoria.ordem_exibicao
    ).all()
    
    return [
        {
            "id": cat.Categoria.id,
            "nome": cat.Categoria.nome,
            "descricao": cat.Categoria.descricao,
            "imagem_url": cat.Categoria.imagem_url,
            "ordem_exibicao": cat.Categoria.ordem_exibicao,
            "total_produtos": cat.total_produtos,
            "ativo": cat.Categoria.ativo
        }
        for cat in categorias
    ]

@router.post("/modifiers/create")
async def criar_modificador(
    produto_id: int,
    nome: str,
    tipo: str = "OPCIONAL",  # OPCIONAL, OBRIGATORIO, MULTIPLO
    opcoes: List[Dict[str, Any]] = Body(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar modificadores para produtos (adicionais, tamanhos, etc)
    Replica funcionalidade: Sistema Cardápio > Modificadores
    """
    
    # Verificar se produto existe
    produto = db.query(Produto).filter(
        Produto.id == produto_id
    ).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Criar modificador
    novo_modificador = ModificadorProduto(
        produto_id=produto_id,
        nome=nome,
        tipo=tipo,
        opcoes=opcoes,
        ativo=True
    )
    
    db.add(novo_modificador)
    db.commit()
    db.refresh(novo_modificador)
    
    return novo_modificador

@router.get("/public/{uuid}", response_model=Dict[str, Any])
async def cardapio_publico(
    uuid: str,
    db: Session = Depends(get_db)
):
    """
    Visualizar cardápio público por UUID (sem autenticação)
    Usado para QR Code e links compartilhados
    """
    
    cardapio = db.query(Cardapio).filter(
        and_(
            Cardapio.uuid == uuid,
            Cardapio.ativo == True
        )
    ).first()
    
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Carregar produtos com categorias
    produtos_por_categoria = db.query(
        Categoria.nome.label("categoria"),
        Categoria.id.label("categoria_id"),
        Produto
    ).join(
        Produto,
        Produto.categoria_id == Categoria.id
    ).join(
        CardapioProduto,
        CardapioProduto.produto_id == Produto.id
    ).filter(
        and_(
            CardapioProduto.cardapio_id == cardapio.id,
            Produto.disponivel_app == True
        )
    ).order_by(
        Categoria.ordem_exibicao,
        CardapioProduto.ordem_exibicao
    ).all()
    
    # Organizar por categoria
    categorias = {}
    for item in produtos_por_categoria:
        if item.categoria not in categorias:
            categorias[item.categoria] = {
                "id": item.categoria_id,
                "nome": item.categoria,
                "produtos": []
            }
        
        categorias[item.categoria]["produtos"].append({
            "id": item.Produto.id,
            "nome": item.Produto.nome,
            "descricao": item.Produto.descricao,
            "preco": float(item.Produto.preco),
            "imagem_url": item.Produto.imagem_url
        })
    
    # Informações da empresa
    empresa = db.query(Empresa).filter(
        Empresa.id == cardapio.empresa_id
    ).first()
    
    return {
        "cardapio": {
            "id": cardapio.id,
            "nome": cardapio.nome,
            "descricao": cardapio.descricao,
            "tipo": cardapio.tipo
        },
        "empresa": {
            "nome": empresa.nome if empresa else "Estabelecimento",
            "logo_url": empresa.logo_url if empresa else None
        },
        "categorias": list(categorias.values()),
        "total_produtos": sum(len(cat["produtos"]) for cat in categorias.values())
    }

@router.post("/duplicate/{cardapio_id}")
async def duplicar_cardapio(
    cardapio_id: int,
    novo_nome: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duplicar cardápio existente
    """
    
    # Buscar cardápio original
    cardapio_original = db.query(Cardapio).filter(
        Cardapio.id == cardapio_id
    ).first()
    
    if not cardapio_original:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Criar cópia
    novo_uuid = str(uuid.uuid4())
    novo_cardapio = Cardapio(
        nome=novo_nome,
        descricao=cardapio_original.descricao,
        tipo=cardapio_original.tipo,
        empresa_id=cardapio_original.empresa_id,
        uuid=novo_uuid,
        url_digital=f"https://menu.sistema.com/{novo_uuid}",
        ativo=True
    )
    
    db.add(novo_cardapio)
    db.flush()
    
    # Copiar produtos
    produtos_originais = db.query(CardapioProduto).filter(
        CardapioProduto.cardapio_id == cardapio_id
    ).all()
    
    for prod in produtos_originais:
        nova_assoc = CardapioProduto(
            cardapio_id=novo_cardapio.id,
            produto_id=prod.produto_id,
            ordem_exibicao=prod.ordem_exibicao
        )
        db.add(nova_assoc)
    
    db.commit()
    db.refresh(novo_cardapio)
    
    return novo_cardapio

@router.get("/analytics/{cardapio_id}")
async def analytics_cardapio(
    cardapio_id: int,
    periodo_dias: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analytics de visualizações e interações do cardápio
    """
    
    # Simular dados de analytics (em produção, seria tracking real)
    return {
        "cardapio_id": cardapio_id,
        "periodo_dias": periodo_dias,
        "metricas": {
            "visualizacoes_total": 1250,
            "visualizacoes_unicas": 890,
            "tempo_medio_sessao": "3:45",
            "taxa_conversao": 12.5,
            "produtos_mais_vistos": [
                {"produto": "Hamburguer Especial", "visualizacoes": 245},
                {"produto": "Pizza Margherita", "visualizacoes": 189},
                {"produto": "Refrigerante", "visualizacoes": 156}
            ],
            "horarios_pico": [
                {"hora": "12:00-13:00", "visualizacoes": 320},
                {"hora": "19:00-20:00", "visualizacoes": 410},
                {"hora": "20:00-21:00", "visualizacoes": 290}
            ],
            "dispositivos": {
                "mobile": 78,
                "desktop": 18,
                "tablet": 4
            }
        }
    }
