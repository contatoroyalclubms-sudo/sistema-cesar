from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import json
import aiohttp
import logging
from ..database import get_db
from ..models import Evento, Transacao, Usuario, LogAuditoria, ClienteEvento
from ..auth_functions import verificar_permissao_admin

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/n8n", tags=["N8N Automações"])

@router.post("/webhook/meta-ads", summary="Webhook Meta Ads")
async def webhook_meta_ads(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook para receber dados do Meta Ads via N8N.
    
    **Uso:** Configure este endpoint no N8N para receber dados do Meta Ads.
    """
    
    try:
        data = await request.json()
        
        log = LogAuditoria(
            cpf_usuario="sistema",
            acao="webhook_meta_ads",
            dados_novos=json.dumps(data),
            ip_origem=request.client.host,
            status="sucesso"
        )
        db.add(log)
        db.commit()
        
        if data.get("event_type") == "lead":
            await processar_lead_meta_ads(data, db)
        elif data.get("event_type") == "purchase":
            await processar_compra_meta_ads(data, db)
        
        return {"status": "success", "message": "Webhook Meta Ads processado"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/webhook/crm", summary="Webhook CRM")
async def webhook_crm(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook para integração com CRM via N8N.
    
    **Uso:** Configure este endpoint no N8N para receber dados do CRM.
    """
    
    try:
        data = await request.json()
        
        log = LogAuditoria(
            cpf_usuario="sistema",
            acao="webhook_crm",
            dados_novos=json.dumps(data),
            ip_origem=request.client.host,
            status="sucesso"
        )
        db.add(log)
        db.commit()
        
        if data.get("action") == "new_contact":
            await processar_novo_contato_crm(data, db)
        elif data.get("action") == "update_contact":
            await processar_atualizacao_contato_crm(data, db)
        
        return {"status": "success", "message": "Webhook CRM processado"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/trigger/evento-criado", summary="Disparar automação evento criado")
async def trigger_evento_criado(
    evento_id: int,
    n8n_webhook_url: str,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_admin)
):
    """
    Disparar automação N8N quando evento é criado.
    
    **Permissões necessárias:** Admin
    """
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    payload = {
        "event": "evento_criado",
        "evento_id": evento.id,
        "evento_nome": evento.nome,
        "data_evento": evento.data_evento.isoformat(),
        "local": evento.local,
        "empresa_id": getattr(evento, 'empresa_id', None)
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(n8n_webhook_url, json=payload) as response:
                if response.status == 200:
                    return {"status": "success", "message": "Automação N8N disparada"}
                else:
                    return {"status": "error", "message": f"Erro HTTP {response.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/trigger/venda-realizada", summary="Disparar automação venda realizada")
async def trigger_venda_realizada(
    transacao_id: int,
    n8n_webhook_url: str,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_admin)
):
    """
    Disparar automação N8N quando venda é realizada.
    
    **Permissões necessárias:** Admin
    """
    
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    payload = {
        "event": "venda_realizada",
        "transacao_id": transacao.id,
        "evento_id": transacao.evento_id,
        "cpf_comprador": transacao.cpf_comprador,
        "nome_comprador": transacao.nome_comprador,
        "valor": float(transacao.valor),
        "lista_id": transacao.lista_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(n8n_webhook_url, json=payload) as response:
                if response.status == 200:
                    return {"status": "success", "message": "Automação N8N disparada"}
                else:
                    return {"status": "error", "message": f"Erro HTTP {response.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def processar_lead_meta_ads(data: Dict[str, Any], db: Session):
    """
    Processar lead do Meta Ads recebido via N8N webhook
    
    Estrutura esperada do payload:
    {
        "event_type": "lead",
        "lead_id": "123456789",
        "form_id": "987654321", 
        "campaign_id": "111111111",
        "ad_id": "222222222",
        "created_time": "2025-01-16T10:30:00Z",
        "field_data": {
            "nome": "João Silva",
            "email": "joao@email.com",
            "telefone": "11999999999"
        },
        "evento_id": 1  # Opcional: ID do evento relacionado
    }
    """
    try:
        logger.info(f" Processando lead Meta Ads: {data.get('lead_id', 'N/A')}")
        
        # Extrair dados do lead
        lead_id = data.get('lead_id')
        form_id = data.get('form_id')
        campaign_id = data.get('campaign_id')
        ad_id = data.get('ad_id')
        created_time = data.get('created_time')
        
        # Dados do formulário
        field_data = data.get('field_data', {})
        nome = field_data.get('nome', 'Lead Meta Ads')
        email = field_data.get('email')
        telefone = field_data.get('telefone')
        
        # Evento relacionado (opcional)
        evento_id = data.get('evento_id')
        evento = None
        if evento_id:
            evento = db.query(Evento).filter(Evento.id == evento_id).first()
        
        # Validar dados mínimos
        if not email or "@" not in email:
            logger.warning(f"️ Lead sem email válido: {lead_id}")
            return {"status": "warning", "message": "Lead sem email válido"}
        
        # Verificar se lead já foi processado
        log_existente = db.query(LogAuditoria).filter(
            LogAuditoria.acao == "LEAD_META_ADS_PROCESSADO",
            LogAuditoria.detalhes.contains(f"lead_id:{lead_id}")
        ).first()
        
        if log_existente:
            logger.info(f"ℹ️ Lead já processado: {lead_id}")
            return {"status": "success", "message": "Lead já processado anteriormente"}
        
        # Tentar criar/atualizar cliente
        cliente_existente = db.query(ClienteEvento).filter(
            ClienteEvento.email == email
        ).first()
        
        if cliente_existente:
            # Atualizar dados do cliente existente
            if nome and nome != "Lead Meta Ads":
                cliente_existente.nome_completo = nome
            if telefone:
                cliente_existente.telefone = telefone
            cliente_existente.status = "lead_meta_ads_atualizado"
            
            logger.info(f" Cliente atualizado: {email}")
            cliente_id = cliente_existente.id
        else:
            # Criar novo cliente com CPF temporário
            import random
            cpf_temp = f"99{random.randint(100000000, 999999999)}"
            
            novo_cliente = ClienteEvento(
                cpf=cpf_temp,
                nome_completo=nome,
                email=email,
                telefone=telefone,
                status="lead_meta_ads"
            )
            db.add(novo_cliente)
            db.flush()  # Para obter o ID
            
            logger.info(f" Novo cliente criado: {email}")
            cliente_id = novo_cliente.id
        
        # Log de auditoria detalhado
        log_auditoria = LogAuditoria(
            cpf_usuario="SYSTEM_META_ADS",
            acao="LEAD_META_ADS_PROCESSADO",
            tabela_afetada="clientes_eventos",
            registro_id=cliente_id,
            dados_novos=json.dumps({
                "lead_id": lead_id,
                "form_id": form_id,
                "campaign_id": campaign_id,
                "ad_id": ad_id,
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "evento_id": evento_id,
                "evento_nome": evento.nome if evento else None,
                "created_time": created_time
            }),
            evento_id=evento_id,
            status="sucesso",
            detalhes=f"Lead Meta Ads processado - lead_id:{lead_id} - {nome} ({email})"
        )
        db.add(log_auditoria)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Lead Meta Ads processado com sucesso",
            "cliente_id": cliente_id,
            "lead_id": lead_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erro ao processar lead Meta Ads: {e}")
        db.rollback()
        raise Exception(f"Erro ao processar lead: {str(e)}")

async def processar_compra_meta_ads(data: Dict[str, Any], db: Session):
    """
    Processar compra/conversão do Meta Ads recebida via N8N webhook
    
    Estrutura esperada do payload:
    {
        "event_type": "purchase",
        "purchase_id": "123456789",
        "campaign_id": "111111111",
        "ad_id": "222222222",
        "customer_data": {
            "cpf": "12345678901",
            "nome": "João Silva",
            "email": "joao@email.com",
            "telefone": "11999999999"
        },
        "purchase_data": {
            "valor": 99.90,
            "lista_id": 1,
            "evento_id": 1,
            "metodo_pagamento": "PIX"
        },
        "created_time": "2025-01-16T10:30:00Z"
    }
    """
    try:
        logger.info(f" Processando compra Meta Ads: {data.get('purchase_id', 'N/A')}")
        
        # Extrair dados da compra
        purchase_id = data.get('purchase_id')
        campaign_id = data.get('campaign_id')
        ad_id = data.get('ad_id')
        created_time = data.get('created_time')
        
        # Dados do cliente
        customer_data = data.get('customer_data', {})
        cpf = customer_data.get('cpf')
        nome = customer_data.get('nome')
        email = customer_data.get('email')
        telefone = customer_data.get('telefone')
        
        # Dados da compra
        purchase_data = data.get('purchase_data', {})
        valor = purchase_data.get('valor', 0)
        lista_id = purchase_data.get('lista_id')
        evento_id = purchase_data.get('evento_id')
        metodo_pagamento = purchase_data.get('metodo_pagamento', 'PIX')
        
        # Validações
        if not cpf or len(cpf.replace('.', '').replace('-', '')) != 11:
            logger.error(f" CPF inválido na compra Meta Ads: {cpf}")
            return {"status": "error", "message": "CPF inválido"}
        
        if not evento_id or not lista_id:
            logger.error(f" Evento ou Lista não informados: evento={evento_id}, lista={lista_id}")
            return {"status": "error", "message": "Evento ou Lista não informados"}
        
        if valor <= 0:
            logger.error(f" Valor inválido: {valor}")
            return {"status": "error", "message": "Valor inválido"}
        
        # Verificar se evento e lista existem
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            logger.error(f" Evento não encontrado: {evento_id}")
            return {"status": "error", "message": "Evento não encontrado"}
        
        # Limpar CPF
        cpf_limpo = cpf.replace('.', '').replace('-', '')
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        
        # Verificar se transação já existe
        transacao_existente = db.query(Transacao).filter(
            Transacao.cpf_comprador == cpf_formatado,
            Transacao.evento_id == evento_id,
            Transacao.lista_id == lista_id,
            Transacao.valor == valor
        ).first()
        
        if transacao_existente:
            logger.info(f"ℹ️ Transação já existe: {transacao_existente.id}")
            return {
                "status": "success", 
                "message": "Transação já processada",
                "transacao_id": transacao_existente.id
            }
        
        # Criar nova transação
        nova_transacao = Transacao(
            cpf_comprador=cpf_formatado,
            nome_comprador=nome,
            email_comprador=email,
            telefone_comprador=telefone,
            valor=valor,
            metodo_pagamento=metodo_pagamento,
            evento_id=evento_id,
            lista_id=lista_id,
            status="aprovada",  # Assumir que compras do Meta Ads já são aprovadas
            codigo_transacao=f"META_{purchase_id}",
            ip_origem="META_ADS"
        )
        
        db.add(nova_transacao)
        db.flush()  # Para obter o ID
        
        # Atualizar/criar cliente se necessário
        cliente_existente = db.query(ClienteEvento).filter(
            ClienteEvento.cpf == cpf_limpo
        ).first()
        
        if not cliente_existente and email:
            novo_cliente = ClienteEvento(
                cpf=cpf_limpo,
                nome_completo=nome,
                email=email,
                telefone=telefone,
                status="comprador_meta_ads"
            )
            db.add(novo_cliente)
        
        # Log de auditoria
        log_auditoria = LogAuditoria(
            cpf_usuario=cpf_formatado,
            acao="COMPRA_META_ADS_PROCESSADA",
            tabela_afetada="transacoes",
            registro_id=nova_transacao.id,
            dados_novos=json.dumps({
                "purchase_id": purchase_id,
                "campaign_id": campaign_id,
                "ad_id": ad_id,
                "valor": float(valor),
                "metodo_pagamento": metodo_pagamento,
                "created_time": created_time
            }),
            evento_id=evento_id,
            status="sucesso",
            detalhes=f"Compra Meta Ads processada - purchase_id:{purchase_id} - {nome} - R$ {valor}"
        )
        db.add(log_auditoria)
        
        db.commit()
        
        logger.info(f" Compra Meta Ads processada: {nova_transacao.id}")
        
        return {
            "status": "success",
            "message": "Compra Meta Ads processada com sucesso",
            "transacao_id": nova_transacao.id,
            "purchase_id": purchase_id,
            "valor": float(valor),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erro ao processar compra Meta Ads: {e}")
        db.rollback()
        raise Exception(f"Erro ao processar compra: {str(e)}")

async def processar_novo_contato_crm(data: Dict[str, Any], db: Session):
    """
    Processar novo contato do CRM via N8N webhook
    
    Estrutura esperada do payload:
    {
        "action": "new_contact",
        "contact_id": "123456",
        "contact_data": {
            "cpf": "12345678901",
            "nome": "João Silva",
            "email": "joao@email.com",
            "telefone": "11999999999",
            "endereco": "Rua X, 123",
            "cidade": "São Paulo",
            "estado": "SP"
        },
        "source": "website|whatsapp|telefone|presencial",
        "tags": ["lead", "evento", "vip"],
        "evento_interesse": 1
    }
    """
    try:
        logger.info(f" Processando novo contato CRM: {data.get('contact_id', 'N/A')}")
        
        # Extrair dados
        contact_id = data.get('contact_id')
        contact_data = data.get('contact_data', {})
        source = data.get('source', 'crm')
        tags = data.get('tags', [])
        evento_interesse = data.get('evento_interesse')
        
        # Dados do contato
        cpf = contact_data.get('cpf')
        nome = contact_data.get('nome')
        email = contact_data.get('email')
        telefone = contact_data.get('telefone')
        endereco = contact_data.get('endereco')
        cidade = contact_data.get('cidade')
        estado = contact_data.get('estado')
        
        # Validar dados mínimos
        if not nome or not (email or telefone):
            logger.warning(f"️ Contato com dados insuficientes: {contact_id}")
            return {"status": "warning", "message": "Dados insuficientes para criar contato"}
        
        # Limpar e validar CPF se fornecido
        cpf_limpo = None
        if cpf:
            cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')
            if len(cpf_limpo) == 11 and cpf_limpo.isdigit():
                # CPF válido
                pass
            else:
                logger.warning(f"️ CPF inválido fornecido: {cpf}")
                cpf_limpo = None
        
        # Se não há CPF, gerar um temporário
        if not cpf_limpo:
            import random
            cpf_limpo = f"88{random.randint(100000000, 999999999)}"  # 88 para contatos CRM
        
        # Verificar se contato já existe
        cliente_existente = None
        if email:
            cliente_existente = db.query(ClienteEvento).filter(
                ClienteEvento.email == email
            ).first()
        
        if not cliente_existente and cpf_limpo != cpf:  # Se não é CPF temporário
            cliente_existente = db.query(ClienteEvento).filter(
                ClienteEvento.cpf == cpf_limpo
            ).first()
        
        if cliente_existente:
            # Atualizar cliente existente
            if nome:
                cliente_existente.nome_completo = nome
            if telefone:
                cliente_existente.telefone = telefone
            if email and not cliente_existente.email:
                cliente_existente.email = email
            
            cliente_existente.status = f"crm_{source}_atualizado"
            
            logger.info(f" Contato CRM atualizado: {cliente_existente.id}")
            cliente_id = cliente_existente.id
        else:
            # Criar novo cliente
            novo_cliente = ClienteEvento(
                cpf=cpf_limpo,
                nome_completo=nome,
                email=email,
                telefone=telefone,
                status=f"crm_{source}"
            )
            db.add(novo_cliente)
            db.flush()
            
            logger.info(f" Novo contato CRM criado: {novo_cliente.id}")
            cliente_id = novo_cliente.id
        
        # Log de auditoria
        log_auditoria = LogAuditoria(
            cpf_usuario="SYSTEM_CRM",
            acao="CONTATO_CRM_PROCESSADO",
            tabela_afetada="clientes_eventos",
            registro_id=cliente_id,
            dados_novos=json.dumps({
                "contact_id": contact_id,
                "source": source,
                "tags": tags,
                "endereco": endereco,
                "cidade": cidade,
                "estado": estado,
                "evento_interesse": evento_interesse
            }),
            evento_id=evento_interesse,
            status="sucesso",
            detalhes=f"Contato CRM processado - contact_id:{contact_id} - {nome} - {source}"
        )
        db.add(log_auditoria)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Contato CRM processado com sucesso",
            "cliente_id": cliente_id,
            "contact_id": contact_id,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erro ao processar contato CRM: {e}")
        db.rollback()
        raise Exception(f"Erro ao processar contato CRM: {str(e)}")


async def processar_atualizacao_contato_crm(data: Dict[str, Any], db: Session):
    """
    Processar atualização de contato do CRM via N8N webhook
    
    Estrutura esperada do payload:
    {
        "action": "update_contact",
        "contact_id": "123456",
        "cliente_id": 789,  # ID interno do cliente
        "updates": {
            "nome": "João Silva Santos",
            "telefone": "11888888888",
            "email": "joao.santos@email.com",
            "status": "cliente_ativo"
        },
        "changed_fields": ["nome", "telefone"]
    }
    """
    try:
        logger.info(f" Processando atualização contato CRM: {data.get('contact_id', 'N/A')}")
        
        # Extrair dados
        contact_id = data.get('contact_id')
        cliente_id = data.get('cliente_id')
        updates = data.get('updates', {})
        changed_fields = data.get('changed_fields', [])
        
        # Tentar encontrar cliente
        cliente = None
        if cliente_id:
            cliente = db.query(ClienteEvento).filter(ClienteEvento.id == cliente_id).first()
        
        # Se não encontrou por ID, tentar por email ou CPF nos updates
        if not cliente:
            if updates.get('email'):
                cliente = db.query(ClienteEvento).filter(
                    ClienteEvento.email == updates['email']
                ).first()
            elif updates.get('cpf'):
                cpf_limpo = updates['cpf'].replace('.', '').replace('-', '').replace(' ', '')
                cliente = db.query(ClienteEvento).filter(
                    ClienteEvento.cpf == cpf_limpo
                ).first()
        
        if not cliente:
            logger.warning(f"️ Cliente não encontrado para atualização: {contact_id}")
            return {"status": "warning", "message": "Cliente não encontrado"}
        
        # Dados antes da atualização (para auditoria)
        dados_anteriores = {
            "nome_completo": cliente.nome_completo,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "status": cliente.status
        }
        
        # Aplicar atualizações
        if 'nome' in updates and updates['nome']:
            cliente.nome_completo = updates['nome']
        
        if 'email' in updates and updates['email']:
            # Verificar se email já existe em outro cliente
            email_existente = db.query(ClienteEvento).filter(
                ClienteEvento.email == updates['email'],
                ClienteEvento.id != cliente.id
            ).first()
            
            if not email_existente:
                cliente.email = updates['email']
            else:
                logger.warning(f"️ Email já existe em outro cliente: {updates['email']}")
        
        if 'telefone' in updates and updates['telefone']:
            cliente.telefone = updates['telefone']
        
        if 'status' in updates and updates['status']:
            cliente.status = updates['status']
        
        # Log de auditoria
        log_auditoria = LogAuditoria(
            cpf_usuario="SYSTEM_CRM",
            acao="CONTATO_CRM_ATUALIZADO",
            tabela_afetada="clientes_eventos",
            registro_id=cliente.id,
            dados_anteriores=json.dumps(dados_anteriores),
            dados_novos=json.dumps(updates),
            status="sucesso",
            detalhes=f"Contato CRM atualizado - contact_id:{contact_id} - campos: {', '.join(changed_fields)}"
        )
        db.add(log_auditoria)
        
        db.commit()
        
        logger.info(f" Contato CRM atualizado: {cliente.id}")
        
        return {
            "status": "success",
            "message": "Contato CRM atualizado com sucesso",
            "cliente_id": cliente.id,
            "contact_id": contact_id,
            "changed_fields": changed_fields,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erro ao atualizar contato CRM: {e}")
        db.rollback()
        raise Exception(f"Erro ao atualizar contato CRM: {str(e)}")
