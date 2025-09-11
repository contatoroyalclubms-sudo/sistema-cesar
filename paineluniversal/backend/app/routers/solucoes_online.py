"""
Router para gerenciamento de soluções online e configuração de aplicativos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_
import json
import base64
from PIL import Image
from io import BytesIO

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    ConfiguracaoApp, ConfiguracaoAppCreate, ConfiguracaoAppUpdate,
    SolucaoOnline, SolucaoOnlineCreate, SolucaoOnlineUpdate,
    RecursoApp, RecursoAppCreate
)

router = APIRouter(
    prefix="/api/solucoes-online",
    tags=["solucoes-online"]
)

def processar_imagem(file: UploadFile, tipo: str = "logo") -> str:
    """Processa e otimiza imagem para uso no app"""
    try:
        # Ler imagem
        contents = file.file.read()
        img = Image.open(BytesIO(contents))
        
        # Redimensionar baseado no tipo
        if tipo == "logo":
            max_size = (512, 512)
        elif tipo == "icone":
            max_size = (192, 192)
        elif tipo == "splash":
            max_size = (1080, 1920)
        else:
            max_size = (800, 800)
        
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Converter para base64
        buffered = BytesIO()
        img.save(buffered, format="PNG", optimize=True)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar imagem: {str(e)}")

def gerar_manifest_pwa(config: models.ConfiguracaoApp) -> Dict[str, Any]:
    """Gera manifest.json para PWA"""
    temas = json.loads(config.temas) if isinstance(config.temas, str) else config.temas
    
    manifest = {
        "name": config.nome_app,
        "short_name": config.nome_app[:12],
        "description": config.descricao,
        "start_url": "/",
        "display": "standalone",
        "orientation": "portrait",
        "theme_color": temas.get("primary_color", "#000000"),
        "background_color": temas.get("background_color", "#ffffff"),
        "icons": []
    }
    
    # Adicionar ícones se disponíveis
    if config.icone_url:
        manifest["icons"] = [
            {
                "src": config.icone_url,
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": config.icone_url,
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    
    return manifest

@router.get("/configuracoes/", response_model=List[ConfiguracaoApp])
def listar_configuracoes_app(
    skip: int = 0,
    limit: int = 100,
    plataforma: Optional[str] = None,
    publicado: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as configurações de aplicativos"""
    query = db.query(models.ConfiguracaoApp)
    
    if plataforma:
        query = query.filter(models.ConfiguracaoApp.plataforma == plataforma)
    
    if publicado is not None:
        query = query.filter(models.ConfiguracaoApp.publicado == publicado)
    
    configuracoes = query.order_by(
        models.ConfiguracaoApp.atualizado_em.desc()
    ).offset(skip).limit(limit).all()
    
    return configuracoes

@router.get("/configuracoes/{config_id}", response_model=ConfiguracaoApp)
def obter_configuracao_app(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém uma configuração específica de aplicativo"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    return config

@router.post("/configuracoes/", response_model=ConfiguracaoApp)
def criar_configuracao_app(
    configuracao: ConfiguracaoAppCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova configuração de aplicativo"""
    # Converter dados para JSON
    temas = json.dumps(configuracao.temas) if configuracao.temas else None
    funcionalidades = json.dumps(configuracao.funcionalidades) if configuracao.funcionalidades else None
    configuracoes_extra = json.dumps(configuracao.configuracoes_extra) if configuracao.configuracoes_extra else None
    
    db_config = models.ConfiguracaoApp(
        **configuracao.model_dump(exclude={'temas', 'funcionalidades', 'configuracoes_extra'}),
        temas=temas,
        funcionalidades=funcionalidades,
        configuracoes_extra=configuracoes_extra
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config

@router.put("/configuracoes/{config_id}", response_model=ConfiguracaoApp)
def atualizar_configuracao_app(
    config_id: int,
    config_update: ConfiguracaoAppUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma configuração de aplicativo"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    update_data = config_update.model_dump(exclude_unset=True)
    
    # Converter dados para JSON se necessário
    if 'temas' in update_data and update_data['temas']:
        update_data['temas'] = json.dumps(update_data['temas'])
    
    if 'funcionalidades' in update_data and update_data['funcionalidades']:
        update_data['funcionalidades'] = json.dumps(update_data['funcionalidades'])
    
    if 'configuracoes_extra' in update_data and update_data['configuracoes_extra']:
        update_data['configuracoes_extra'] = json.dumps(update_data['configuracoes_extra'])
    
    for key, value in update_data.items():
        setattr(config, key, value)
    
    config.atualizado_em = datetime.now()
    db.commit()
    db.refresh(config)
    
    return config

@router.post("/configuracoes/{config_id}/upload-logo")
async def upload_logo_app(
    config_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Faz upload do logo do aplicativo"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Processar imagem
    logo_base64 = processar_imagem(file, "logo")
    config.logo_url = logo_base64
    
    db.commit()
    
    return {"message": "Logo atualizado com sucesso", "logo_url": logo_base64[:100] + "..."}

@router.post("/configuracoes/{config_id}/upload-icone")
async def upload_icone_app(
    config_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Faz upload do ícone do aplicativo"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Processar imagem
    icone_base64 = processar_imagem(file, "icone")
    config.icone_url = icone_base64
    
    db.commit()
    
    return {"message": "Ícone atualizado com sucesso", "icone_url": icone_base64[:100] + "..."}

@router.post("/configuracoes/{config_id}/upload-splash")
async def upload_splash_screen(
    config_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Faz upload da splash screen do aplicativo"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Processar imagem
    splash_base64 = processar_imagem(file, "splash")
    config.splash_screen_url = splash_base64
    
    db.commit()
    
    return {"message": "Splash screen atualizada com sucesso"}

@router.post("/configuracoes/{config_id}/publicar")
def publicar_app(
    config_id: int,
    lojas: List[str] = ["google_play", "app_store"],
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Publica o aplicativo nas lojas selecionadas"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Validar configuração mínima
    if not config.nome_app or not config.bundle_id:
        raise HTTPException(
            status_code=400,
            detail="Configuração incompleta. Nome e Bundle ID são obrigatórios."
        )
    
    # Simular processo de publicação
    config.publicado = True
    config.data_publicacao = datetime.now()
    config.status_publicacao = "em_revisao"
    
    db.commit()
    
    return {
        "message": "Aplicativo enviado para publicação",
        "lojas": lojas,
        "status": "em_revisao",
        "tempo_estimado": "3-7 dias úteis"
    }

@router.get("/configuracoes/{config_id}/manifest.json")
def obter_manifest_pwa(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Obtém o manifest.json para PWA"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id,
        models.ConfiguracaoApp.plataforma.in_(["web", "pwa"])
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração PWA não encontrada")
    
    manifest = gerar_manifest_pwa(config)
    
    return manifest

# ====== SOLUÇÕES ONLINE ======

@router.get("/solucoes/", response_model=List[SolucaoOnline])
def listar_solucoes(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    ativa: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as soluções online disponíveis"""
    query = db.query(models.SolucaoOnline)
    
    if tipo:
        query = query.filter(models.SolucaoOnline.tipo == tipo)
    
    if ativa is not None:
        query = query.filter(models.SolucaoOnline.ativa == ativa)
    
    if search:
        query = query.filter(
            or_(
                models.SolucaoOnline.nome.ilike(f"%{search}%"),
                models.SolucaoOnline.descricao.ilike(f"%{search}%")
            )
        )
    
    solucoes = query.order_by(
        models.SolucaoOnline.ordem,
        models.SolucaoOnline.nome
    ).offset(skip).limit(limit).all()
    
    return solucoes

@router.get("/solucoes/{solucao_id}", response_model=SolucaoOnline)
def obter_solucao(
    solucao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém uma solução online específica"""
    solucao = db.query(models.SolucaoOnline).filter(
        models.SolucaoOnline.id == solucao_id
    ).first()
    
    if not solucao:
        raise HTTPException(status_code=404, detail="Solução não encontrada")
    
    # Incrementar visualizações
    solucao.total_acessos = (solucao.total_acessos or 0) + 1
    db.commit()
    
    return solucao

@router.post("/solucoes/", response_model=SolucaoOnline)
def criar_solucao(
    solucao: SolucaoOnlineCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova solução online"""
    recursos = json.dumps(solucao.recursos) if solucao.recursos else None
    configuracoes = json.dumps(solucao.configuracoes) if solucao.configuracoes else None
    
    db_solucao = models.SolucaoOnline(
        **solucao.model_dump(exclude={'recursos', 'configuracoes'}),
        recursos=recursos,
        configuracoes=configuracoes
    )
    
    db.add(db_solucao)
    db.commit()
    db.refresh(db_solucao)
    
    return db_solucao

@router.put("/solucoes/{solucao_id}", response_model=SolucaoOnline)
def atualizar_solucao(
    solucao_id: int,
    solucao_update: SolucaoOnlineUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma solução online"""
    solucao = db.query(models.SolucaoOnline).filter(
        models.SolucaoOnline.id == solucao_id
    ).first()
    
    if not solucao:
        raise HTTPException(status_code=404, detail="Solução não encontrada")
    
    update_data = solucao_update.model_dump(exclude_unset=True)
    
    if 'recursos' in update_data and update_data['recursos']:
        update_data['recursos'] = json.dumps(update_data['recursos'])
    
    if 'configuracoes' in update_data and update_data['configuracoes']:
        update_data['configuracoes'] = json.dumps(update_data['configuracoes'])
    
    for key, value in update_data.items():
        setattr(solucao, key, value)
    
    db.commit()
    db.refresh(solucao)
    
    return solucao

@router.delete("/solucoes/{solucao_id}")
def deletar_solucao(
    solucao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Desativa uma solução online"""
    solucao = db.query(models.SolucaoOnline).filter(
        models.SolucaoOnline.id == solucao_id
    ).first()
    
    if not solucao:
        raise HTTPException(status_code=404, detail="Solução não encontrada")
    
    solucao.ativa = False
    db.commit()
    
    return {"message": "Solução desativada com sucesso"}

# ====== RECURSOS DO APP ======

@router.get("/recursos/", response_model=List[RecursoApp])
def listar_recursos_app(
    skip: int = 0,
    limit: int = 100,
    categoria: Optional[str] = None,
    gratuito: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista recursos disponíveis para aplicativos"""
    query = db.query(models.RecursoApp)
    
    if categoria:
        query = query.filter(models.RecursoApp.categoria == categoria)
    
    if gratuito is not None:
        query = query.filter(models.RecursoApp.gratuito == gratuito)
    
    recursos = query.order_by(
        models.RecursoApp.popularidade.desc(),
        models.RecursoApp.nome
    ).offset(skip).limit(limit).all()
    
    return recursos

@router.post("/recursos/", response_model=RecursoApp)
def criar_recurso_app(
    recurso: RecursoAppCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo recurso para aplicativos"""
    dependencias = json.dumps(recurso.dependencias) if recurso.dependencias else None
    configuracao_padrao = json.dumps(recurso.configuracao_padrao) if recurso.configuracao_padrao else None
    
    db_recurso = models.RecursoApp(
        **recurso.model_dump(exclude={'dependencias', 'configuracao_padrao'}),
        dependencias=dependencias,
        configuracao_padrao=configuracao_padrao
    )
    
    db.add(db_recurso)
    db.commit()
    db.refresh(db_recurso)
    
    return db_recurso

@router.post("/configuracoes/{config_id}/adicionar-recurso/{recurso_id}")
def adicionar_recurso_ao_app(
    config_id: int,
    recurso_id: int,
    configuracao_customizada: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Adiciona um recurso a uma configuração de aplicativo"""
    config = db.query(models.ConfiguracaoApp).filter(
        models.ConfiguracaoApp.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    recurso = db.query(models.RecursoApp).filter(
        models.RecursoApp.id == recurso_id,
        models.RecursoApp.ativo == True
    ).first()
    
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso não encontrado ou inativo")
    
    # Atualizar funcionalidades do app
    funcionalidades = json.loads(config.funcionalidades) if config.funcionalidades else {}
    funcionalidades[recurso.codigo] = {
        "ativo": True,
        "nome": recurso.nome,
        "configuracao": configuracao_customizada or json.loads(recurso.configuracao_padrao or "{}")
    }
    
    config.funcionalidades = json.dumps(funcionalidades)
    
    # Atualizar contador de uso do recurso
    recurso.total_instalacoes = (recurso.total_instalacoes or 0) + 1
    
    db.commit()
    
    return {
        "message": f"Recurso {recurso.nome} adicionado com sucesso",
        "recurso": recurso.nome,
        "configuracao": funcionalidades[recurso.codigo]
    }

@router.get("/templates")
def listar_templates_app(
    categoria: Optional[str] = None,
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista templates prontos para aplicativos"""
    templates = [
        {
            "id": "eventos_basico",
            "nome": "App de Eventos Básico",
            "descricao": "Template para gestão básica de eventos",
            "categoria": "eventos",
            "recursos": ["check-in", "lista_convidados", "qr_code"],
            "preview_url": "/templates/eventos_basico.png",
            "preco": 0
        },
        {
            "id": "eventos_completo",
            "nome": "App de Eventos Completo",
            "descricao": "Solução completa para produtores de eventos",
            "categoria": "eventos",
            "recursos": ["check-in", "vendas", "pdv", "gamificacao", "relatorios"],
            "preview_url": "/templates/eventos_completo.png",
            "preco": 99.90
        },
        {
            "id": "clube_fidelidade",
            "nome": "Clube de Fidelidade",
            "descricao": "App para programa de fidelidade e recompensas",
            "categoria": "fidelidade",
            "recursos": ["pontos", "recompensas", "niveis", "cupons"],
            "preview_url": "/templates/clube_fidelidade.png",
            "preco": 49.90
        },
        {
            "id": "marketplace_ingressos",
            "nome": "Marketplace de Ingressos",
            "descricao": "Plataforma de venda de ingressos online",
            "categoria": "vendas",
            "recursos": ["catalogo", "carrinho", "pagamento", "entrega_digital"],
            "preview_url": "/templates/marketplace_ingressos.png",
            "preco": 149.90
        },
        {
            "id": "gestao_equipe",
            "nome": "Gestão de Equipe de Eventos",
            "descricao": "App para coordenação de equipes em eventos",
            "categoria": "gestao",
            "recursos": ["escalas", "comunicacao", "tarefas", "relatorios"],
            "preview_url": "/templates/gestao_equipe.png",
            "preco": 79.90
        }
    ]
    
    if categoria:
        templates = [t for t in templates if t["categoria"] == categoria]
    
    return templates

@router.post("/configuracoes/criar-de-template/{template_id}")
def criar_app_de_template(
    template_id: str,
    nome_personalizado: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma configuração de app baseada em um template"""
    # Obter template (simulado)
    templates = {
        "eventos_basico": {
            "funcionalidades": ["check-in", "lista_convidados", "qr_code"],
            "temas": {
                "primary_color": "#007bff",
                "secondary_color": "#6c757d",
                "background_color": "#ffffff",
                "text_color": "#333333"
            }
        },
        "eventos_completo": {
            "funcionalidades": ["check-in", "vendas", "pdv", "gamificacao", "relatorios"],
            "temas": {
                "primary_color": "#28a745",
                "secondary_color": "#ffc107",
                "background_color": "#f8f9fa",
                "text_color": "#212529"
            }
        }
    }
    
    if template_id not in templates:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    template = templates[template_id]
    
    # Criar configuração
    db_config = models.ConfiguracaoApp(
        nome_app=nome_personalizado,
        descricao=f"App criado a partir do template {template_id}",
        plataforma="pwa",
        versao="1.0.0",
        bundle_id=f"com.app.{nome_personalizado.lower().replace(' ', '')}",
        temas=json.dumps(template["temas"]),
        funcionalidades=json.dumps({f: {"ativo": True} for f in template["funcionalidades"]}),
        template_origem=template_id
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return {
        "message": "App criado com sucesso a partir do template",
        "config_id": db_config.id,
        "nome": db_config.nome_app,
        "template": template_id
    }