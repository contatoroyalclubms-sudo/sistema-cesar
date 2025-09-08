"""
Router para Cardápios Digitais com QR Code
Implementa funcionalidades avançadas de cardápios para eventos
Baseado na análise da engenharia reversa do sistema MEEP
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import qrcode
import io
import base64
from PIL import Image

from ..database import get_db
from ..models_cashless import (
    CardapioDigital, CategoriaCardapioDigital, ProdutoCardapioDigital,
    Mesa, Evento
)
from ..models import Produto, Usuario
from ..utils.security import get_current_user

router = APIRouter(prefix="/api/v1/cardapios-digitais", tags=["Cardápios Digitais"])

# ================================================================================
# SCHEMAS LOCAIS (TEMPORÁRIOS)
# ================================================================================

from pydantic import BaseModel, Field
from typing import List, Optional

class CardapioDigitalBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    ativo: bool = True

class CardapioDigitalCreate(CardapioDigitalBase):
    evento_id: int
    empresa_id: Optional[int] = None

class CardapioDigitalUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class CategoriaCardapioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    ordem: int = Field(default=1, ge=1)
    cor: str = Field(default="#6b7280", regex="^#[0-9a-fA-F]{6}$")
    icone: Optional[str] = None

class CategoriaCardapioCreate(CategoriaCardapioBase):
    cardapio_id: int

class ProdutoCardapioBase(BaseModel):
    nome_exibicao: Optional[str] = None
    descricao_exibicao: Optional[str] = None
    preco_exibicao: Optional[float] = None
    imagem_url: Optional[str] = None
    ordem: int = Field(default=1, ge=1)
    destaque: bool = False
    disponivel: bool = True

class ProdutoCardapioCreate(ProdutoCardapioBase):
    categoria_id: int
    produto_id: Optional[int] = None

# ================================================================================
# ENDPOINTS PARA CARDÁPIOS DIGITAIS
# ================================================================================

@router.post("/cardapios", response_model=dict)
async def criar_cardapio_digital(
    cardapio: CardapioDigitalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo cardápio digital"""
    
    # Verificar se o evento existe
    evento = db.query(Evento).filter(Evento.id == cardapio.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Gerar UUID único para o cardápio
    cardapio_uuid = str(uuid.uuid4())
    url_acesso = f"https://app.paineluniversal.com/cardapio/{cardapio_uuid}"
    
    # Criar cardápio
    novo_cardapio = CardapioDigital(
        uuid=cardapio_uuid,
        nome=cardapio.nome,
        descricao=cardapio.descricao,
        url_acesso=url_acesso,
        evento_id=cardapio.evento_id,
        empresa_id=cardapio.empresa_id,
        criado_por=current_user.id,
        ativo=True
    )
    
    db.add(novo_cardapio)
    db.commit()
    db.refresh(novo_cardapio)
    
    # Gerar QR Code
    qr_code_base64 = await gerar_qr_code_cardapio(url_acesso)
    
    return {
        "id": novo_cardapio.id,
        "uuid": novo_cardapio.uuid,
        "nome": novo_cardapio.nome,
        "url_acesso": novo_cardapio.url_acesso,
        "qr_code": qr_code_base64,
        "ativo": novo_cardapio.ativo,
        "criado_em": novo_cardapio.criado_em
    }

@router.get("/cardapios/{cardapio_uuid}")
async def obter_cardapio_publico(
    cardapio_uuid: str,
    mesa_id: Optional[int] = Query(None, description="ID da mesa (opcional)"),
    db: Session = Depends(get_db)
):
    """Obter cardápio digital público pelo UUID (para clientes)"""
    
    cardapio = db.query(CardapioDigital).filter(
        CardapioDigital.uuid == cardapio_uuid,
        CardapioDigital.ativo == True
    ).first()
    
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Buscar categorias e produtos
    categorias = db.query(CategoriaCardapioDigital).filter(
        CategoriaCardapioDigital.cardapio_id == cardapio.id,
        CategoriaCardapioDigital.ativa == True
    ).order_by(CategoriaCardapioDigital.ordem).all()
    
    cardapio_completo = {
        "id": cardapio.id,
        "uuid": cardapio.uuid,
        "nome": cardapio.nome,
        "descricao": cardapio.descricao,
        "evento": {
            "id": cardapio.evento.id,
            "nome": cardapio.evento.nome,
            "data_inicio": cardapio.evento.data_inicio,
            "data_fim": cardapio.evento.data_fim
        },
        "mesa_id": mesa_id,
        "categorias": []
    }
    
    for categoria in categorias:
        produtos = db.query(ProdutoCardapioDigital).filter(
            ProdutoCardapioDigital.categoria_id == categoria.id,
            ProdutoCardapioDigital.disponivel == True
        ).order_by(
            ProdutoCardapioDigital.destaque.desc(),
            ProdutoCardapioDigital.ordem
        ).all()
        
        produtos_formatados = []
        for produto_cardapio in produtos:
            produto_data = {
                "id": produto_cardapio.id,
                "nome": produto_cardapio.nome_exibicao or (
                    produto_cardapio.produto.nome if produto_cardapio.produto else "Produto sem nome"
                ),
                "descricao": produto_cardapio.descricao_exibicao or (
                    produto_cardapio.produto.descricao if produto_cardapio.produto else ""
                ),
                "preco": produto_cardapio.preco_exibicao or (
                    float(produto_cardapio.produto.preco) if produto_cardapio.produto else 0.0
                ),
                "imagem_url": produto_cardapio.imagem_url,
                "destaque": produto_cardapio.destaque,
                "permite_observacoes": produto_cardapio.permite_observacoes,
                "produto_id": produto_cardapio.produto_id
            }
            produtos_formatados.append(produto_data)
        
        categoria_data = {
            "id": categoria.id,
            "nome": categoria.nome,
            "descricao": categoria.descricao,
            "cor": categoria.cor,
            "icone": categoria.icone,
            "produtos": produtos_formatados
        }
        cardapio_completo["categorias"].append(categoria_data)
    
    return cardapio_completo

@router.get("/cardapios")
async def listar_cardapios(
    evento_id: Optional[int] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar cardápios digitais"""
    
    query = db.query(CardapioDigital)
    
    if evento_id:
        query = query.filter(CardapioDigital.evento_id == evento_id)
    if ativo is not None:
        query = query.filter(CardapioDigital.ativo == ativo)
    
    cardapios = query.order_by(CardapioDigital.criado_em.desc()).all()
    
    return [
        {
            "id": c.id,
            "uuid": c.uuid,
            "nome": c.nome,
            "descricao": c.descricao,
            "url_acesso": c.url_acesso,
            "evento_nome": c.evento.nome,
            "ativo": c.ativo,
            "criado_em": c.criado_em,
            "total_categorias": len(c.categorias),
            "total_produtos": sum(len(cat.produtos) for cat in c.categorias)
        }
        for c in cardapios
    ]

@router.put("/cardapios/{cardapio_id}")
async def atualizar_cardapio(
    cardapio_id: int,
    cardapio_update: CardapioDigitalUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar cardápio digital"""
    
    cardapio = db.query(CardapioDigital).filter(CardapioDigital.id == cardapio_id).first()
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Atualizar campos
    if cardapio_update.nome:
        cardapio.nome = cardapio_update.nome
    if cardapio_update.descricao is not None:
        cardapio.descricao = cardapio_update.descricao
    if cardapio_update.ativo is not None:
        cardapio.ativo = cardapio_update.ativo
    
    cardapio.atualizado_em = datetime.now()
    
    db.commit()
    db.refresh(cardapio)
    
    return {
        "id": cardapio.id,
        "nome": cardapio.nome,
        "descricao": cardapio.descricao,
        "ativo": cardapio.ativo,
        "atualizado_em": cardapio.atualizado_em
    }

# ================================================================================
# ENDPOINTS PARA CATEGORIAS
# ================================================================================

@router.post("/cardapios/{cardapio_id}/categorias")
async def criar_categoria(
    cardapio_id: int,
    categoria: CategoriaCardapioBase,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova categoria no cardápio"""
    
    cardapio = db.query(CardapioDigital).filter(CardapioDigital.id == cardapio_id).first()
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    nova_categoria = CategoriaCardapioDigital(
        cardapio_id=cardapio_id,
        nome=categoria.nome,
        descricao=categoria.descricao,
        ordem=categoria.ordem,
        cor=categoria.cor,
        icone=categoria.icone
    )
    
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    
    return {
        "id": nova_categoria.id,
        "nome": nova_categoria.nome,
        "descricao": nova_categoria.descricao,
        "ordem": nova_categoria.ordem,
        "cor": nova_categoria.cor,
        "icone": nova_categoria.icone,
        "ativa": nova_categoria.ativa,
        "criado_em": nova_categoria.criado_em
    }

@router.put("/categorias/{categoria_id}")
async def atualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaCardapioBase,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar categoria do cardápio"""
    
    categoria = db.query(CategoriaCardapioDigital).filter(
        CategoriaCardapioDigital.id == categoria_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    categoria.nome = categoria_update.nome
    categoria.descricao = categoria_update.descricao
    categoria.ordem = categoria_update.ordem
    categoria.cor = categoria_update.cor
    categoria.icone = categoria_update.icone
    
    db.commit()
    db.refresh(categoria)
    
    return categoria

@router.delete("/categorias/{categoria_id}")
async def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Excluir categoria do cardápio"""
    
    categoria = db.query(CategoriaCardapioDigital).filter(
        CategoriaCardapioDigital.id == categoria_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar se há produtos vinculados
    produtos = db.query(ProdutoCardapioDigital).filter(
        ProdutoCardapioDigital.categoria_id == categoria_id
    ).count()
    
    if produtos > 0:
        # Apenas desativar se há produtos
        categoria.ativa = False
        db.commit()
        return {"message": "Categoria desativada (possui produtos vinculados)"}
    else:
        # Excluir se não há produtos
        db.delete(categoria)
        db.commit()
        return {"message": "Categoria excluída"}

# ================================================================================
# ENDPOINTS PARA PRODUTOS DO CARDÁPIO
# ================================================================================

@router.post("/categorias/{categoria_id}/produtos")
async def adicionar_produto_categoria(
    categoria_id: int,
    produto_cardapio: ProdutoCardapioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Adicionar produto à categoria do cardápio"""
    
    categoria = db.query(CategoriaCardapioDigital).filter(
        CategoriaCardapioDigital.id == categoria_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar se o produto existe (se fornecido)
    if produto_cardapio.produto_id:
        produto = db.query(Produto).filter(Produto.id == produto_cardapio.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    novo_produto_cardapio = ProdutoCardapioDigital(
        categoria_id=categoria_id,
        produto_id=produto_cardapio.produto_id,
        nome_exibicao=produto_cardapio.nome_exibicao,
        descricao_exibicao=produto_cardapio.descricao_exibicao,
        preco_exibicao=produto_cardapio.preco_exibicao,
        imagem_url=produto_cardapio.imagem_url,
        ordem=produto_cardapio.ordem,
        destaque=produto_cardapio.destaque,
        disponivel=produto_cardapio.disponivel
    )
    
    db.add(novo_produto_cardapio)
    db.commit()
    db.refresh(novo_produto_cardapio)
    
    return {
        "id": novo_produto_cardapio.id,
        "categoria_id": novo_produto_cardapio.categoria_id,
        "produto_id": novo_produto_cardapio.produto_id,
        "nome_exibicao": novo_produto_cardapio.nome_exibicao,
        "descricao_exibicao": novo_produto_cardapio.descricao_exibicao,
        "preco_exibicao": novo_produto_cardapio.preco_exibicao,
        "imagem_url": novo_produto_cardapio.imagem_url,
        "ordem": novo_produto_cardapio.ordem,
        "destaque": novo_produto_cardapio.destaque,
        "disponivel": novo_produto_cardapio.disponivel,
        "criado_em": novo_produto_cardapio.criado_em
    }

@router.put("/produtos-cardapio/{produto_cardapio_id}")
async def atualizar_produto_cardapio(
    produto_cardapio_id: int,
    produto_update: ProdutoCardapioBase,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar produto do cardápio"""
    
    produto_cardapio = db.query(ProdutoCardapioDigital).filter(
        ProdutoCardapioDigital.id == produto_cardapio_id
    ).first()
    
    if not produto_cardapio:
        raise HTTPException(status_code=404, detail="Produto do cardápio não encontrado")
    
    # Atualizar campos
    if produto_update.nome_exibicao is not None:
        produto_cardapio.nome_exibicao = produto_update.nome_exibicao
    if produto_update.descricao_exibicao is not None:
        produto_cardapio.descricao_exibicao = produto_update.descricao_exibicao
    if produto_update.preco_exibicao is not None:
        produto_cardapio.preco_exibicao = produto_update.preco_exibicao
    if produto_update.imagem_url is not None:
        produto_cardapio.imagem_url = produto_update.imagem_url
    
    produto_cardapio.ordem = produto_update.ordem
    produto_cardapio.destaque = produto_update.destaque
    produto_cardapio.disponivel = produto_update.disponivel
    
    db.commit()
    db.refresh(produto_cardapio)
    
    return produto_cardapio

@router.delete("/produtos-cardapio/{produto_cardapio_id}")
async def remover_produto_cardapio(
    produto_cardapio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remover produto do cardápio"""
    
    produto_cardapio = db.query(ProdutoCardapioDigital).filter(
        ProdutoCardapioDigital.id == produto_cardapio_id
    ).first()
    
    if not produto_cardapio:
        raise HTTPException(status_code=404, detail="Produto do cardápio não encontrado")
    
    db.delete(produto_cardapio)
    db.commit()
    
    return {"message": "Produto removido do cardápio"}

# ================================================================================
# ENDPOINTS PARA VINCULAÇÃO COM MESAS
# ================================================================================

@router.post("/cardapios/{cardapio_id}/mesas/{mesa_id}")
async def vincular_cardapio_mesa(
    cardapio_id: int,
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Vincular cardápio a uma mesa específica"""
    
    cardapio = db.query(CardapioDigital).filter(CardapioDigital.id == cardapio_id).first()
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    # Criar vinculação na tabela MesaCardapio
    # Verificar se já existe
    from ..models_cashless import MesaCardapio
    vinculacao_existente = db.query(MesaCardapio).filter(
        and_(
            MesaCardapio.cardapio_id == cardapio_id,
            MesaCardapio.mesa_id == mesa_id
        )
    ).first()
    
    if vinculacao_existente:
        raise HTTPException(status_code=400, detail="Mesa já vinculada a este cardápio")
    
    nova_vinculacao = MesaCardapio(
        cardapio_id=cardapio_id,
        mesa_id=mesa_id,
        ativa=True
    )
    
    db.add(nova_vinculacao)
    db.commit()
    
    # Gerar URL específica da mesa
    url_mesa = f"{cardapio.url_acesso}?mesa_id={mesa_id}"
    qr_code_mesa = await gerar_qr_code_cardapio(url_mesa)
    
    return {
        "cardapio_id": cardapio_id,
        "mesa_id": mesa_id,
        "mesa_numero": mesa.numero,
        "url_mesa": url_mesa,
        "qr_code_mesa": qr_code_mesa,
        "vinculado_em": nova_vinculacao.criado_em
    }

@router.get("/cardapios/{cardapio_id}/qr-code")
async def obter_qr_code_cardapio(
    cardapio_id: int,
    mesa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter QR Code do cardápio (geral ou específico da mesa)"""
    
    cardapio = db.query(CardapioDigital).filter(CardapioDigital.id == cardapio_id).first()
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    url = cardapio.url_acesso
    if mesa_id:
        url += f"?mesa_id={mesa_id}"
    
    qr_code_base64 = await gerar_qr_code_cardapio(url)
    
    return {
        "cardapio_id": cardapio_id,
        "mesa_id": mesa_id,
        "url": url,
        "qr_code": qr_code_base64
    }

# ================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================

async def gerar_qr_code_cardapio(url: str) -> str:
    """Gerar QR Code para cardápio digital"""
    try:
        # Criar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Criar imagem
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_code_base64}"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.get("/produtos/buscar")
async def buscar_produtos_para_cardapio(
    termo: str = Query(..., min_length=2),
    evento_id: Optional[int] = Query(None),
    categoria_id: Optional[int] = Query(None),
    limite: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar produtos disponíveis para adicionar ao cardápio"""
    
    query = db.query(Produto).filter(
        or_(
            Produto.nome.ilike(f"%{termo}%"),
            Produto.descricao.ilike(f"%{termo}%")
        ),
        Produto.ativo == True
    )
    
    if evento_id:
        query = query.filter(Produto.evento_id == evento_id)
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    
    produtos = query.limit(limite).all()
    
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "descricao": p.descricao,
            "preco": float(p.preco),
            "categoria_nome": p.categoria.nome if p.categoria else None,
            "ativo": p.ativo
        }
        for p in produtos
    ]
