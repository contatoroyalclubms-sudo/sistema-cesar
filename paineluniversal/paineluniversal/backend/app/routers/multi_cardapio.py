from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import qrcode
import io
import base64
from fastapi.responses import StreamingResponse

from ..database import get_db
from ..models import Usuario, Evento
from ..models_extended import (
    CardapioDigital, CategoriaCardapio, ItemCardapio, 
    ModificadorCardapio, GrupoModificadores, RestricaoHoraria,
    CardapioQRCode, AnalyticsCardapio
)
from ..schemas_extended import (
    CardapioDigitalCreate, CardapioDigitalUpdate, CardapioDigitalResponse,
    CategoriaCardapioCreate, CategoriaCardapioUpdate, CategoriaCardapioResponse,
    ItemCardapioCreate, ItemCardapioUpdate, ItemCardapioResponse,
    ModificadorCardapioCreate, ModificadorCardapioResponse,
    GrupoModificadoresCreate, GrupoModificadoresResponse,
    RestricaoHorariaCreate, RestricaoHorariaResponse,
    CardapioQRCodeResponse, AnalyticsCardapioResponse,
    CardapioReorderRequest, CategoriaReorderRequest
)
from ..auth_functions import get_current_user

router = APIRouter(prefix="/api/multi-cardapio", tags=["multi-cardapio"])

# Cardápios Digitais
@router.post("/cardapios", response_model=CardapioDigitalResponse)
def create_cardapio(
    cardapio: CardapioDigitalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo cardápio digital"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    # Verificar limite de 9 cardápios por evento
    count = db.query(CardapioDigital).filter_by(evento_id=cardapio.evento_id).count()
    if count >= 9:
        raise HTTPException(status_code=400, detail="Limite de 9 cardápios por evento atingido")
    
    db_cardapio = CardapioDigital(**cardapio.dict())
    db_cardapio.criado_por = current_user.id
    db.add(db_cardapio)
    db.commit()
    db.refresh(db_cardapio)
    
    # Gerar QR Code automático
    qr_code = generate_qr_code(db_cardapio, db)
    
    return db_cardapio

@router.get("/cardapios", response_model=List[CardapioDigitalResponse])
def list_cardapios(
    evento_id: Optional[int] = Query(None),
    ativo: Optional[bool] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar cardápios digitais"""
    query = db.query(CardapioDigital)
    
    if evento_id:
        query = query.filter_by(evento_id=evento_id)
    if ativo is not None:
        query = query.filter_by(ativo=ativo)
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    return query.order_by(CardapioDigital.ordem).all()

@router.get("/cardapios/{cardapio_id}", response_model=CardapioDigitalResponse)
def get_cardapio(
    cardapio_id: int,
    db: Session = Depends(get_db)
):
    """Obter cardápio específico (público)"""
    cardapio = db.query(CardapioDigital).filter_by(id=cardapio_id).first()
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Registrar visualização
    analytics = db.query(AnalyticsCardapio).filter_by(
        cardapio_id=cardapio_id,
        data=datetime.now().date()
    ).first()
    
    if analytics:
        analytics.visualizacoes += 1
    else:
        analytics = AnalyticsCardapio(
            cardapio_id=cardapio_id,
            data=datetime.now().date(),
            visualizacoes=1
        )
        db.add(analytics)
    
    db.commit()
    return cardapio

@router.put("/cardapios/{cardapio_id}", response_model=CardapioDigitalResponse)
def update_cardapio(
    cardapio_id: int,
    cardapio: CardapioDigitalUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar cardápio digital"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_cardapio = db.query(CardapioDigital).filter_by(id=cardapio_id).first()
    if not db_cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    for key, value in cardapio.dict(exclude_unset=True).items():
        setattr(db_cardapio, key, value)
    
    db.commit()
    db.refresh(db_cardapio)
    return db_cardapio

@router.delete("/cardapios/{cardapio_id}")
def delete_cardapio(
    cardapio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Excluir cardápio digital"""
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")
    
    db_cardapio = db.query(CardapioDigital).filter_by(id=cardapio_id).first()
    if not db_cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    db.delete(db_cardapio)
    db.commit()
    return {"message": "Cardápio excluído com sucesso"}

@router.post("/cardapios/{cardapio_id}/duplicate", response_model=CardapioDigitalResponse)
def duplicate_cardapio(
    cardapio_id: int,
    novo_nome: str = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Duplicar cardápio com todas as categorias e itens"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    # Buscar cardápio original
    original = db.query(CardapioDigital).filter_by(id=cardapio_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Criar cópia
    novo_cardapio = CardapioDigital(
        evento_id=original.evento_id,
        nome=novo_nome,
        descricao=original.descricao,
        tipo=original.tipo,
        moeda=original.moeda,
        taxa_servico=original.taxa_servico,
        configuracoes=original.configuracoes,
        criado_por=current_user.id
    )
    db.add(novo_cardapio)
    db.flush()
    
    # Copiar categorias e itens
    categorias_map = {}
    for cat in original.categorias:
        nova_cat = CategoriaCardapio(
            cardapio_id=novo_cardapio.id,
            nome=cat.nome,
            descricao=cat.descricao,
            imagem_url=cat.imagem_url,
            ordem=cat.ordem,
            ativo=cat.ativo
        )
        db.add(nova_cat)
        db.flush()
        categorias_map[cat.id] = nova_cat.id
        
        # Copiar itens da categoria
        for item in cat.itens:
            novo_item = ItemCardapio(
                categoria_id=nova_cat.id,
                nome=item.nome,
                descricao=item.descricao,
                preco=item.preco,
                preco_promocional=item.preco_promocional,
                imagem_url=item.imagem_url,
                tags=item.tags,
                alergenos=item.alergenos,
                calorias=item.calorias,
                tempo_preparo=item.tempo_preparo,
                disponivel=item.disponivel,
                estoque=item.estoque,
                ordem=item.ordem
            )
            db.add(novo_item)
    
    db.commit()
    db.refresh(novo_cardapio)
    return novo_cardapio

# Categorias
@router.post("/categorias", response_model=CategoriaCardapioResponse)
def create_categoria(
    categoria: CategoriaCardapioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova categoria"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_categoria = CategoriaCardapio(**categoria.dict())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.get("/categorias", response_model=List[CategoriaCardapioResponse])
def list_categorias(
    cardapio_id: int = Query(...),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar categorias de um cardápio"""
    query = db.query(CategoriaCardapio).filter_by(cardapio_id=cardapio_id)
    
    if ativo is not None:
        query = query.filter_by(ativo=ativo)
    
    return query.order_by(CategoriaCardapio.ordem).all()

@router.put("/categorias/{categoria_id}", response_model=CategoriaCardapioResponse)
def update_categoria(
    categoria_id: int,
    categoria: CategoriaCardapioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar categoria"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_categoria = db.query(CategoriaCardapio).filter_by(id=categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    for key, value in categoria.dict(exclude_unset=True).items():
        setattr(db_categoria, key, value)
    
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.post("/categorias/reorder")
def reorder_categorias(
    reorder: CategoriaReorderRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Reordenar categorias (drag & drop)"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    for item in reorder.items:
        db.query(CategoriaCardapio).filter_by(id=item.id).update({"ordem": item.ordem})
    
    db.commit()
    return {"message": "Categorias reordenadas com sucesso"}

# Itens do Cardápio
@router.post("/itens", response_model=ItemCardapioResponse)
def create_item(
    item: ItemCardapioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo item"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_item = ItemCardapio(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/itens", response_model=List[ItemCardapioResponse])
def list_itens(
    categoria_id: Optional[int] = Query(None),
    cardapio_id: Optional[int] = Query(None),
    disponivel: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar itens do cardápio"""
    query = db.query(ItemCardapio)
    
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    elif cardapio_id:
        query = query.join(CategoriaCardapio).filter(
            CategoriaCardapio.cardapio_id == cardapio_id
        )
    
    if disponivel is not None:
        query = query.filter_by(disponivel=disponivel)
    
    if search:
        query = query.filter(
            or_(
                ItemCardapio.nome.ilike(f"%{search}%"),
                ItemCardapio.descricao.ilike(f"%{search}%"),
                ItemCardapio.tags.ilike(f"%{search}%")
            )
        )
    
    return query.order_by(ItemCardapio.ordem).all()

@router.get("/itens/{item_id}", response_model=ItemCardapioResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Obter item específico"""
    item = db.query(ItemCardapio).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    # Registrar visualização
    categoria = db.query(CategoriaCardapio).filter_by(id=item.categoria_id).first()
    if categoria:
        analytics = db.query(AnalyticsCardapio).filter_by(
            cardapio_id=categoria.cardapio_id,
            data=datetime.now().date()
        ).first()
        
        if analytics:
            item_views = analytics.itens_mais_vistos or {}
            item_views[str(item_id)] = item_views.get(str(item_id), 0) + 1
            analytics.itens_mais_vistos = item_views
        else:
            analytics = AnalyticsCardapio(
                cardapio_id=categoria.cardapio_id,
                data=datetime.now().date(),
                itens_mais_vistos={str(item_id): 1}
            )
            db.add(analytics)
        
        db.commit()
    
    return item

@router.put("/itens/{item_id}", response_model=ItemCardapioResponse)
def update_item(
    item_id: int,
    item: ItemCardapioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar item"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_item = db.query(ItemCardapio).filter_by(id=item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/itens/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Excluir item"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_item = db.query(ItemCardapio).filter_by(id=item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item excluído com sucesso"}

@router.post("/itens/batch-update")
def batch_update_itens(
    updates: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar múltiplos itens de uma vez"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    for update in updates:
        item_id = update.pop("id")
        db.query(ItemCardapio).filter_by(id=item_id).update(update)
    
    db.commit()
    return {"message": f"{len(updates)} itens atualizados com sucesso"}

# Modificadores
@router.post("/modificadores", response_model=ModificadorCardapioResponse)
def create_modificador(
    modificador: ModificadorCardapioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo modificador"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_modificador = ModificadorCardapio(**modificador.dict())
    db.add(db_modificador)
    db.commit()
    db.refresh(db_modificador)
    return db_modificador

@router.get("/modificadores", response_model=List[ModificadorCardapioResponse])
def list_modificadores(
    grupo_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar modificadores"""
    query = db.query(ModificadorCardapio)
    
    if grupo_id:
        query = query.filter_by(grupo_id=grupo_id)
    
    return query.all()

# Grupos de Modificadores
@router.post("/grupos-modificadores", response_model=GrupoModificadoresResponse)
def create_grupo_modificadores(
    grupo: GrupoModificadoresCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar grupo de modificadores"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_grupo = GrupoModificadores(**grupo.dict())
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo

# Restrições Horárias
@router.post("/restricoes-horarias", response_model=RestricaoHorariaResponse)
def create_restricao_horaria(
    restricao: RestricaoHorariaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar restrição horária"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    db_restricao = RestricaoHoraria(**restricao.dict())
    db.add(db_restricao)
    db.commit()
    db.refresh(db_restricao)
    return db_restricao

# QR Codes
@router.get("/qr-codes/{cardapio_id}")
def get_qr_code(
    cardapio_id: int,
    size: int = Query(300, ge=100, le=1000),
    format: str = Query("png", regex="^(png|svg)$"),
    db: Session = Depends(get_db)
):
    """Gerar/obter QR Code do cardápio"""
    cardapio = db.query(CardapioDigital).filter_by(id=cardapio_id).first()
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    # Buscar QR Code existente ou gerar novo
    qr_record = db.query(CardapioQRCode).filter_by(cardapio_id=cardapio_id).first()
    if not qr_record:
        qr_record = generate_qr_code(cardapio, db)
    
    # Gerar imagem do QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_record.url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return StreamingResponse(buf, media_type=f"image/{format}")

def generate_qr_code(cardapio: CardapioDigital, db: Session) -> CardapioQRCode:
    """Gerar e salvar QR Code para cardápio"""
    # URL base configurável
    base_url = "https://seu-dominio.com"
    url = f"{base_url}/cardapio/{cardapio.id}"
    short_url = f"{base_url}/c/{cardapio.id}"
    
    qr_code = CardapioQRCode(
        cardapio_id=cardapio.id,
        url=url,
        short_url=short_url
    )
    db.add(qr_code)
    db.commit()
    db.refresh(qr_code)
    return qr_code

# Analytics
@router.get("/analytics/{cardapio_id}", response_model=List[AnalyticsCardapioResponse])
def get_analytics(
    cardapio_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter analytics do cardápio"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    query = db.query(AnalyticsCardapio).filter_by(cardapio_id=cardapio_id)
    
    if start_date:
        query = query.filter(AnalyticsCardapio.data >= start_date.date())
    if end_date:
        query = query.filter(AnalyticsCardapio.data <= end_date.date())
    
    return query.order_by(desc(AnalyticsCardapio.data)).all()

@router.get("/analytics/summary/{cardapio_id}")
def get_analytics_summary(
    cardapio_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter resumo de analytics"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    start_date = datetime.now() - timedelta(days=days)
    
    analytics = db.query(AnalyticsCardapio).filter(
        and_(
            AnalyticsCardapio.cardapio_id == cardapio_id,
            AnalyticsCardapio.data >= start_date.date()
        )
    ).all()
    
    # Processar dados
    total_views = sum(a.visualizacoes for a in analytics)
    total_conversions = sum(a.conversoes for a in analytics)
    conversion_rate = (total_conversions / total_views * 100) if total_views > 0 else 0
    
    # Itens mais populares
    all_items = {}
    for a in analytics:
        if a.itens_mais_vistos:
            for item_id, views in a.itens_mais_vistos.items():
                all_items[item_id] = all_items.get(item_id, 0) + views
    
    top_items = sorted(all_items.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "periodo": f"Últimos {days} dias",
        "visualizacoes_totais": total_views,
        "conversoes_totais": total_conversions,
        "taxa_conversao": round(conversion_rate, 2),
        "media_visualizacoes_dia": round(total_views / days, 2),
        "itens_mais_populares": top_items
    }

@router.post("/cardapios/{cardapio_id}/toggle-status")
def toggle_cardapio_status(
    cardapio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Ativar/desativar cardápio"""
    if current_user.tipo not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    cardapio = db.query(CardapioDigital).filter_by(id=cardapio_id).first()
    if not cardapio:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    
    cardapio.ativo = not cardapio.ativo
    db.commit()
    
    return {
        "message": f"Cardápio {'ativado' if cardapio.ativo else 'desativado'} com sucesso",
        "ativo": cardapio.ativo
    }