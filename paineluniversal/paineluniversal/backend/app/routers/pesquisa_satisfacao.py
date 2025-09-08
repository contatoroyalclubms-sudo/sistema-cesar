"""
Router para gerenciamento de pesquisas de satisfação
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import qrcode
import io
import base64

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    PesquisaSatisfacao, PesquisaSatisfacaoCreate, PesquisaSatisfacaoUpdate,
    RespostaPesquisa, RespostaPesquisaCreate
)

router = APIRouter(
    prefix="/api/pesquisas-satisfacao",
    tags=["pesquisas-satisfacao"]
)

def gerar_qr_code(url: str) -> str:
    """Gera QR code em base64 para uma URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

@router.get("/", response_model=List[PesquisaSatisfacao])
def listar_pesquisas(
    skip: int = 0,
    limit: int = 100,
    evento_id: Optional[int] = None,
    ativa: Optional[bool] = None,
    tipo_integracao: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as pesquisas de satisfação"""
    query = db.query(models.PesquisaSatisfacao)
    
    if evento_id:
        query = query.filter(models.PesquisaSatisfacao.evento_id == evento_id)
    
    if ativa is not None:
        query = query.filter(models.PesquisaSatisfacao.ativa == ativa)
    
    if tipo_integracao:
        query = query.filter(models.PesquisaSatisfacao.tipo_integracao == tipo_integracao)
    
    # Filtrar por pesquisas ativas no período atual
    now = datetime.now()
    query = query.filter(
        or_(
            models.PesquisaSatisfacao.data_inicio.is_(None),
            models.PesquisaSatisfacao.data_inicio <= now
        ),
        or_(
            models.PesquisaSatisfacao.data_fim.is_(None),
            models.PesquisaSatisfacao.data_fim >= now
        )
    )
    
    pesquisas = query.order_by(models.PesquisaSatisfacao.criado_em.desc()).offset(skip).limit(limit).all()
    
    return pesquisas

@router.get("/{pesquisa_id}", response_model=PesquisaSatisfacao)
def obter_pesquisa(
    pesquisa_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém uma pesquisa específica"""
    pesquisa = db.query(models.PesquisaSatisfacao).filter(
        models.PesquisaSatisfacao.id == pesquisa_id
    ).first()
    
    if not pesquisa:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada")
    
    return pesquisa

@router.post("/", response_model=PesquisaSatisfacao)
def criar_pesquisa(
    pesquisa: PesquisaSatisfacaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova pesquisa de satisfação"""
    # Converter configurações para JSON string se necessário
    configuracoes = None
    if pesquisa.configuracoes:
        import json
        configuracoes = json.dumps(pesquisa.configuracoes)
    
    # Gerar QR Code se houver URL
    qr_code = None
    if pesquisa.url_pesquisa:
        qr_code = gerar_qr_code(pesquisa.url_pesquisa)
    
    db_pesquisa = models.PesquisaSatisfacao(
        **pesquisa.model_dump(exclude={'configuracoes'}),
        configuracoes=configuracoes,
        qr_code=qr_code
    )
    
    db.add(db_pesquisa)
    db.commit()
    db.refresh(db_pesquisa)
    
    return db_pesquisa

@router.put("/{pesquisa_id}", response_model=PesquisaSatisfacao)
def atualizar_pesquisa(
    pesquisa_id: int,
    pesquisa_update: PesquisaSatisfacaoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma pesquisa existente"""
    pesquisa = db.query(models.PesquisaSatisfacao).filter(
        models.PesquisaSatisfacao.id == pesquisa_id
    ).first()
    
    if not pesquisa:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada")
    
    update_data = pesquisa_update.model_dump(exclude_unset=True)
    
    # Converter configurações para JSON string se necessário
    if 'configuracoes' in update_data and update_data['configuracoes']:
        import json
        update_data['configuracoes'] = json.dumps(update_data['configuracoes'])
    
    # Atualizar QR Code se a URL mudou
    if 'url_pesquisa' in update_data and update_data['url_pesquisa']:
        pesquisa.qr_code = gerar_qr_code(update_data['url_pesquisa'])
    
    for key, value in update_data.items():
        if key != 'qr_code':  # QR code é gerado automaticamente
            setattr(pesquisa, key, value)
    
    db.commit()
    db.refresh(pesquisa)
    
    return pesquisa

@router.delete("/{pesquisa_id}")
def deletar_pesquisa(
    pesquisa_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Desativa uma pesquisa"""
    pesquisa = db.query(models.PesquisaSatisfacao).filter(
        models.PesquisaSatisfacao.id == pesquisa_id
    ).first()
    
    if not pesquisa:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada")
    
    pesquisa.ativa = False
    db.commit()
    
    return {"message": "Pesquisa desativada com sucesso"}

# ====== ROTAS DE RESPOSTAS ======

@router.post("/responder", response_model=RespostaPesquisa)
def responder_pesquisa(
    resposta: RespostaPesquisaCreate,
    db: Session = Depends(get_db)
):
    """Registra uma resposta de pesquisa (não requer autenticação)"""
    # Verificar se a pesquisa existe e está ativa
    pesquisa = db.query(models.PesquisaSatisfacao).filter(
        models.PesquisaSatisfacao.id == resposta.pesquisa_id,
        models.PesquisaSatisfacao.ativa == True
    ).first()
    
    if not pesquisa:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada ou inativa")
    
    # Verificar se está no período válido
    now = datetime.now()
    if pesquisa.data_inicio and pesquisa.data_inicio > now:
        raise HTTPException(status_code=400, detail="Pesquisa ainda não iniciada")
    
    if pesquisa.data_fim and pesquisa.data_fim < now:
        raise HTTPException(status_code=400, detail="Pesquisa encerrada")
    
    # Converter dados_resposta para JSON string se necessário
    dados_resposta = None
    if resposta.dados_resposta:
        import json
        dados_resposta = json.dumps(resposta.dados_resposta)
    
    # Obter IP do cliente (se disponível)
    from fastapi import Request
    ip_origem = None  # Seria obtido do Request se passado como parâmetro
    
    db_resposta = models.RespostaPesquisa(
        **resposta.model_dump(exclude={'dados_resposta'}),
        dados_resposta=dados_resposta,
        ip_origem=ip_origem
    )
    
    db.add(db_resposta)
    
    # Atualizar estatísticas da pesquisa
    pesquisa.total_respostas = (pesquisa.total_respostas or 0) + 1
    
    # Recalcular média se houver nota
    if resposta.nota:
        respostas_com_nota = db.query(models.RespostaPesquisa).filter(
            models.RespostaPesquisa.pesquisa_id == pesquisa.id,
            models.RespostaPesquisa.nota.isnot(None)
        ).all()
        
        if respostas_com_nota:
            notas = [r.nota for r in respostas_com_nota] + [resposta.nota]
            pesquisa.nota_media = sum(notas) / len(notas)
    
    db.commit()
    db.refresh(db_resposta)
    
    return db_resposta

@router.get("/{pesquisa_id}/respostas", response_model=List[RespostaPesquisa])
def listar_respostas_pesquisa(
    pesquisa_id: int,
    skip: int = 0,
    limit: int = 100,
    origem: Optional[str] = None,
    cliente_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as respostas de uma pesquisa"""
    query = db.query(models.RespostaPesquisa).filter(
        models.RespostaPesquisa.pesquisa_id == pesquisa_id
    )
    
    if origem:
        query = query.filter(models.RespostaPesquisa.origem == origem)
    
    if cliente_id:
        query = query.filter(models.RespostaPesquisa.cliente_id == cliente_id)
    
    respostas = query.order_by(
        models.RespostaPesquisa.data_resposta.desc()
    ).offset(skip).limit(limit).all()
    
    return respostas

@router.get("/{pesquisa_id}/estatisticas")
def obter_estatisticas_pesquisa(
    pesquisa_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém estatísticas detalhadas de uma pesquisa"""
    pesquisa = db.query(models.PesquisaSatisfacao).filter(
        models.PesquisaSatisfacao.id == pesquisa_id
    ).first()
    
    if not pesquisa:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada")
    
    respostas = db.query(models.RespostaPesquisa).filter(
        models.RespostaPesquisa.pesquisa_id == pesquisa_id
    ).all()
    
    # Calcular estatísticas
    total_respostas = len(respostas)
    respostas_com_nota = [r for r in respostas if r.nota is not None]
    respostas_com_comentario = [r for r in respostas if r.comentario]
    
    # Distribuição de notas
    distribuicao_notas = {}
    for nota in range(1, 11):
        distribuicao_notas[nota] = sum(1 for r in respostas_com_nota if r.nota == nota)
    
    # Distribuição por origem
    distribuicao_origem = {}
    for resposta in respostas:
        origem = resposta.origem or 'desconhecido'
        distribuicao_origem[origem] = distribuicao_origem.get(origem, 0) + 1
    
    # NPS (Net Promoter Score)
    nps = 0
    if respostas_com_nota:
        promotores = sum(1 for r in respostas_com_nota if r.nota >= 9)
        detratores = sum(1 for r in respostas_com_nota if r.nota <= 6)
        nps = ((promotores - detratores) / len(respostas_com_nota)) * 100
    
    return {
        "pesquisa": {
            "id": pesquisa.id,
            "titulo": pesquisa.titulo,
            "ativa": pesquisa.ativa,
            "criado_em": pesquisa.criado_em
        },
        "estatisticas": {
            "total_respostas": total_respostas,
            "nota_media": float(pesquisa.nota_media) if pesquisa.nota_media else 0,
            "nps": round(nps, 1),
            "total_comentarios": len(respostas_com_comentario),
            "distribuicao_notas": distribuicao_notas,
            "distribuicao_origem": distribuicao_origem
        }
    }

@router.get("/integracao/parceiros")
def listar_parceiros_integracao(
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista parceiros disponíveis para integração de pesquisas"""
    return [
        {
            "id": "track.co",
            "nome": "Track.co",
            "descricao": "Ferramenta de pesquisa de satisfação do cliente",
            "icone": "crown",
            "status": "disponivel",
            "recursos": [
                "Envio automatizado em pontos de contato",
                "QR Code para pesquisas manuais",
                "Insights valiosos dos clientes"
            ]
        },
        {
            "id": "google_forms",
            "nome": "Google Forms",
            "descricao": "Formulários do Google integrados",
            "icone": "description",
            "status": "disponivel",
            "recursos": [
                "Criação de formulários personalizados",
                "Análise automática de respostas",
                "Exportação para planilhas"
            ]
        },
        {
            "id": "interno",
            "nome": "Sistema Interno",
            "descricao": "Pesquisas nativas do sistema",
            "icone": "poll",
            "status": "ativo",
            "recursos": [
                "Totalmente integrado ao sistema",
                "Customização completa",
                "Dados armazenados localmente"
            ]
        }
    ]