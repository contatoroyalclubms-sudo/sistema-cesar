"""
Router para gerenciamento de integrações com sistemas externos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
import json
import httpx
import hmac
import hashlib
from enum import Enum

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    Integracao, IntegracaoCreate, IntegracaoUpdate,
    WebhookIntegracao, WebhookIntegracaoCreate,
    LogIntegracao
)

router = APIRouter(
    prefix="/api/integracoes",
    tags=["integracoes"]
)

class TipoIntegracao(str, Enum):
    PAGAMENTO = "pagamento"
    CRM = "crm"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    ANALYTICS = "analytics"
    REDES_SOCIAIS = "redes_sociais"
    TICKETEIRA = "ticketeira"
    FISCAL = "fiscal"
    CONTABIL = "contabil"

class StatusIntegracao(str, Enum):
    CONFIGURANDO = "configurando"
    ATIVA = "ativa"
    INATIVA = "inativa"
    ERRO = "erro"
    PAUSADA = "pausada"

def validar_credenciais(tipo: str, credenciais: Dict) -> bool:
    """Valida credenciais de integração"""
    if tipo == "pagamento":
        return all(k in credenciais for k in ["api_key", "merchant_id"])
    elif tipo == "whatsapp":
        return all(k in credenciais for k in ["token", "phone_number_id"])
    elif tipo == "email":
        return all(k in credenciais for k in ["smtp_host", "smtp_port", "username", "password"])
    elif tipo == "analytics":
        return "tracking_id" in credenciais
    return True

async def testar_conexao(integracao: models.Integracao) -> Dict[str, Any]:
    """Testa conexão com o serviço integrado"""
    credenciais = json.loads(integracao.credenciais) if isinstance(integracao.credenciais, str) else integracao.credenciais
    configuracao = json.loads(integracao.configuracao) if isinstance(integracao.configuracao, str) else integracao.configuracao
    
    resultado = {
        "sucesso": False,
        "mensagem": "",
        "detalhes": {}
    }
    
    try:
        if integracao.tipo == "pagamento":
            # Testar API de pagamento
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {credenciais.get('api_key')}"}
                response = await client.get(
                    f"{configuracao.get('base_url')}/v1/status",
                    headers=headers,
                    timeout=10.0
                )
                resultado["sucesso"] = response.status_code == 200
                resultado["mensagem"] = "Conexão estabelecida com sucesso" if resultado["sucesso"] else f"Erro: {response.status_code}"
        
        elif integracao.tipo == "whatsapp":
            # Testar WhatsApp Business API
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {credenciais.get('token')}"}
                response = await client.get(
                    f"https://graph.facebook.com/v17.0/{credenciais.get('phone_number_id')}",
                    headers=headers,
                    timeout=10.0
                )
                resultado["sucesso"] = response.status_code == 200
                resultado["mensagem"] = "WhatsApp conectado" if resultado["sucesso"] else "Erro na conexão"
        
        elif integracao.tipo == "email":
            # Testar conexão SMTP
            import smtplib
            try:
                server = smtplib.SMTP(credenciais.get("smtp_host"), credenciais.get("smtp_port"))
                if credenciais.get("use_tls"):
                    server.starttls()
                server.login(credenciais.get("username"), credenciais.get("password"))
                server.quit()
                resultado["sucesso"] = True
                resultado["mensagem"] = "Email configurado corretamente"
            except Exception as e:
                resultado["mensagem"] = f"Erro SMTP: {str(e)}"
        
        else:
            resultado["sucesso"] = True
            resultado["mensagem"] = f"Integração {integracao.tipo} pronta"
    
    except Exception as e:
        resultado["mensagem"] = f"Erro ao testar conexão: {str(e)}"
    
    return resultado

def gerar_webhook_signature(payload: str, secret: str) -> str:
    """Gera assinatura HMAC para webhook"""
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

@router.get("/", response_model=List[Integracao])
def listar_integracoes(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as integrações disponíveis"""
    query = db.query(models.Integracao)
    
    if tipo:
        query = query.filter(models.Integracao.tipo == tipo)
    
    if status:
        query = query.filter(models.Integracao.status == status)
    
    if search:
        query = query.filter(
            or_(
                models.Integracao.nome.ilike(f"%{search}%"),
                models.Integracao.descricao.ilike(f"%{search}%")
            )
        )
    
    integracoes = query.order_by(
        models.Integracao.status == "ativa",
        models.Integracao.criado_em.desc()
    ).offset(skip).limit(limit).all()
    
    # Remover credenciais sensíveis da resposta
    for integracao in integracoes:
        integracao.credenciais = None
    
    return integracoes

@router.get("/{integracao_id}", response_model=Integracao)
def obter_integracao(
    integracao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém uma integração específica"""
    integracao = db.query(models.Integracao).filter(
        models.Integracao.id == integracao_id
    ).first()
    
    if not integracao:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    
    # Remover credenciais sensíveis
    integracao.credenciais = None
    
    return integracao

@router.post("/", response_model=Integracao)
async def criar_integracao(
    integracao: IntegracaoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova integração"""
    # Validar credenciais
    if not validar_credenciais(integracao.tipo, integracao.credenciais or {}):
        raise HTTPException(
            status_code=400,
            detail="Credenciais inválidas para o tipo de integração"
        )
    
    # Converter para JSON
    credenciais = json.dumps(integracao.credenciais) if integracao.credenciais else None
    configuracao = json.dumps(integracao.configuracao) if integracao.configuracao else None
    
    db_integracao = models.Integracao(
        **integracao.model_dump(exclude={'credenciais', 'configuracao'}),
        credenciais=credenciais,
        configuracao=configuracao,
        status="configurando"
    )
    
    db.add(db_integracao)
    db.commit()
    db.refresh(db_integracao)
    
    # Testar conexão em background
    background_tasks.add_task(
        testar_e_ativar_integracao,
        db_integracao.id,
        db
    )
    
    # Remover credenciais da resposta
    db_integracao.credenciais = None
    
    return db_integracao

async def testar_e_ativar_integracao(integracao_id: int, db: Session):
    """Testa e ativa integração em background"""
    integracao = db.query(models.Integracao).filter(
        models.Integracao.id == integracao_id
    ).first()
    
    if not integracao:
        return
    
    resultado = await testar_conexao(integracao)
    
    if resultado["sucesso"]:
        integracao.status = "ativa"
        integracao.ultimo_teste = datetime.now()
    else:
        integracao.status = "erro"
        integracao.erro_mensagem = resultado["mensagem"]
    
    # Criar log
    log = models.LogIntegracao(
        integracao_id=integracao_id,
        tipo_evento="teste_conexao",
        sucesso=resultado["sucesso"],
        mensagem=resultado["mensagem"],
        detalhes=json.dumps(resultado.get("detalhes", {}))
    )
    
    db.add(log)
    db.commit()

@router.put("/{integracao_id}", response_model=Integracao)
async def atualizar_integracao(
    integracao_id: int,
    integracao_update: IntegracaoUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma integração existente"""
    integracao = db.query(models.Integracao).filter(
        models.Integracao.id == integracao_id
    ).first()
    
    if not integracao:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    
    update_data = integracao_update.model_dump(exclude_unset=True)
    
    # Converter para JSON se necessário
    if 'credenciais' in update_data and update_data['credenciais']:
        # Validar novas credenciais
        if not validar_credenciais(integracao.tipo, update_data['credenciais']):
            raise HTTPException(
                status_code=400,
                detail="Credenciais inválidas"
            )
        update_data['credenciais'] = json.dumps(update_data['credenciais'])
        # Marcar para re-teste
        integracao.status = "configurando"
    
    if 'configuracao' in update_data and update_data['configuracao']:
        update_data['configuracao'] = json.dumps(update_data['configuracao'])
    
    for key, value in update_data.items():
        setattr(integracao, key, value)
    
    db.commit()
    db.refresh(integracao)
    
    # Re-testar se credenciais foram atualizadas
    if integracao.status == "configurando":
        background_tasks.add_task(
            testar_e_ativar_integracao,
            integracao_id,
            db
        )
    
    # Remover credenciais da resposta
    integracao.credenciais = None
    
    return integracao

@router.delete("/{integracao_id}")
def deletar_integracao(
    integracao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Desativa uma integração"""
    integracao = db.query(models.Integracao).filter(
        models.Integracao.id == integracao_id
    ).first()
    
    if not integracao:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    
    integracao.status = "inativa"
    integracao.ativa = False
    db.commit()
    
    return {"message": "Integração desativada com sucesso"}

@router.post("/{integracao_id}/testar")
async def testar_integracao(
    integracao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Testa conexão com uma integração"""
    integracao = db.query(models.Integracao).filter(
        models.Integracao.id == integracao_id
    ).first()
    
    if not integracao:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    
    resultado = await testar_conexao(integracao)
    
    # Atualizar status
    integracao.ultimo_teste = datetime.now()
    if resultado["sucesso"]:
        integracao.status = "ativa"
        integracao.erro_mensagem = None
    else:
        integracao.status = "erro"
        integracao.erro_mensagem = resultado["mensagem"]
    
    # Criar log
    log = models.LogIntegracao(
        integracao_id=integracao_id,
        tipo_evento="teste_manual",
        sucesso=resultado["sucesso"],
        mensagem=resultado["mensagem"],
        detalhes=json.dumps(resultado.get("detalhes", {})),
        usuario_id=current_user.id
    )
    
    db.add(log)
    db.commit()
    
    return resultado

# ====== WEBHOOKS ======

@router.get("/{integracao_id}/webhooks", response_model=List[WebhookIntegracao])
def listar_webhooks(
    integracao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista webhooks de uma integração"""
    webhooks = db.query(models.WebhookIntegracao).filter(
        models.WebhookIntegracao.integracao_id == integracao_id
    ).all()
    
    return webhooks

@router.post("/{integracao_id}/webhooks", response_model=WebhookIntegracao)
def criar_webhook(
    integracao_id: int,
    webhook: WebhookIntegracaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um webhook para uma integração"""
    # Verificar se integração existe
    integracao = db.query(models.Integracao).filter(
        models.Integracao.id == integracao_id
    ).first()
    
    if not integracao:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    
    # Gerar secret para assinatura
    import secrets
    secret = secrets.token_urlsafe(32)
    
    headers = json.dumps(webhook.headers) if webhook.headers else None
    
    db_webhook = models.WebhookIntegracao(
        **webhook.model_dump(exclude={'headers'}),
        integracao_id=integracao_id,
        headers=headers,
        secret=secret
    )
    
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    
    return db_webhook

@router.post("/webhook/{webhook_id}/processar")
async def processar_webhook(
    webhook_id: int,
    payload: Dict[str, Any],
    signature: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Processa um webhook recebido"""
    webhook = db.query(models.WebhookIntegracao).filter(
        models.WebhookIntegracao.id == webhook_id,
        models.WebhookIntegracao.ativo == True
    ).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook não encontrado ou inativo")
    
    # Validar assinatura se configurada
    if webhook.secret and signature:
        expected_signature = gerar_webhook_signature(
            json.dumps(payload),
            webhook.secret
        )
        if signature != expected_signature:
            raise HTTPException(status_code=401, detail="Assinatura inválida")
    
    # Processar payload baseado no evento
    try:
        resultado = await processar_evento_webhook(webhook, payload, db)
        
        # Criar log de sucesso
        log = models.LogIntegracao(
            integracao_id=webhook.integracao_id,
            tipo_evento=f"webhook_{webhook.evento}",
            sucesso=True,
            mensagem="Webhook processado com sucesso",
            detalhes=json.dumps(resultado)
        )
        db.add(log)
        
        # Atualizar contador
        webhook.total_chamadas = (webhook.total_chamadas or 0) + 1
        webhook.ultima_chamada = datetime.now()
        
        db.commit()
        
        return {"status": "success", "resultado": resultado}
    
    except Exception as e:
        # Criar log de erro
        log = models.LogIntegracao(
            integracao_id=webhook.integracao_id,
            tipo_evento=f"webhook_{webhook.evento}_erro",
            sucesso=False,
            mensagem=str(e),
            detalhes=json.dumps({"payload": payload})
        )
        db.add(log)
        
        webhook.total_erros = (webhook.total_erros or 0) + 1
        webhook.ultima_chamada = datetime.now()
        
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {str(e)}")

async def processar_evento_webhook(
    webhook: models.WebhookIntegracao,
    payload: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """Processa evento específico do webhook"""
    evento = webhook.evento
    resultado = {"evento": evento, "processado": False}
    
    if evento == "pagamento_confirmado":
        # Processar pagamento
        pedido_id = payload.get("order_id")
        valor = payload.get("amount")
        
        # Atualizar status do pedido
        # ... lógica de atualização ...
        
        resultado["processado"] = True
        resultado["pedido_id"] = pedido_id
        resultado["valor"] = valor
    
    elif evento == "cliente_criado":
        # Criar/atualizar cliente no sistema
        cliente_data = payload.get("customer", {})
        
        # ... lógica de criação/atualização ...
        
        resultado["processado"] = True
        resultado["cliente_id"] = cliente_data.get("id")
    
    elif evento == "ticket_vendido":
        # Processar venda de ticket
        ticket_data = payload.get("ticket", {})
        
        # ... lógica de processamento ...
        
        resultado["processado"] = True
        resultado["ticket_id"] = ticket_data.get("id")
    
    return resultado

@router.get("/{integracao_id}/logs")
def listar_logs_integracao(
    integracao_id: int,
    skip: int = 0,
    limit: int = 100,
    tipo_evento: Optional[str] = None,
    sucesso: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista logs de uma integração"""
    query = db.query(models.LogIntegracao).filter(
        models.LogIntegracao.integracao_id == integracao_id
    )
    
    if tipo_evento:
        query = query.filter(models.LogIntegracao.tipo_evento == tipo_evento)
    
    if sucesso is not None:
        query = query.filter(models.LogIntegracao.sucesso == sucesso)
    
    logs = query.order_by(
        models.LogIntegracao.data_evento.desc()
    ).offset(skip).limit(limit).all()
    
    return logs

@router.get("/marketplace")
def listar_marketplace_integracoes(
    categoria: Optional[str] = None,
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista integrações disponíveis no marketplace"""
    integracoes = [
        {
            "id": "stripe",
            "nome": "Stripe",
            "descricao": "Processamento de pagamentos online",
            "categoria": "pagamento",
            "icone": "credit-card",
            "popularidade": 5,
            "preco": "2.9% + R$ 0,60 por transação"
        },
        {
            "id": "mercadopago",
            "nome": "Mercado Pago",
            "descricao": "Pagamentos e split de receita",
            "categoria": "pagamento",
            "icone": "shopping-cart",
            "popularidade": 5,
            "preco": "A partir de 1.99%"
        },
        {
            "id": "sendgrid",
            "nome": "SendGrid",
            "descricao": "Envio de emails transacionais",
            "categoria": "email",
            "icone": "mail",
            "popularidade": 4,
            "preco": "Gratuito até 100 emails/dia"
        },
        {
            "id": "twilio",
            "nome": "Twilio",
            "descricao": "SMS e WhatsApp Business",
            "categoria": "comunicacao",
            "icone": "message-circle",
            "popularidade": 4,
            "preco": "A partir de $0.0075 por SMS"
        },
        {
            "id": "google_analytics",
            "nome": "Google Analytics",
            "descricao": "Análise de dados e comportamento",
            "categoria": "analytics",
            "icone": "bar-chart",
            "popularidade": 5,
            "preco": "Gratuito"
        },
        {
            "id": "facebook_pixel",
            "nome": "Facebook Pixel",
            "descricao": "Rastreamento de conversões",
            "categoria": "analytics",
            "icone": "activity",
            "popularidade": 4,
            "preco": "Gratuito"
        },
        {
            "id": "mailchimp",
            "nome": "Mailchimp",
            "descricao": "Email marketing e automação",
            "categoria": "marketing",
            "icone": "send",
            "popularidade": 4,
            "preco": "Gratuito até 500 contatos"
        },
        {
            "id": "hubspot",
            "nome": "HubSpot",
            "descricao": "CRM completo",
            "categoria": "crm",
            "icone": "users",
            "popularidade": 4,
            "preco": "Gratuito para funcionalidades básicas"
        }
    ]
    
    if categoria:
        integracoes = [i for i in integracoes if i["categoria"] == categoria]
    
    return integracoes