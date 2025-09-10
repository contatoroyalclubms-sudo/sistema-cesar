"""
Router para Marketing e Automação - Sistema completo de campanhas
Campanhas, segmentação, automações, cupons e comunicação
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import random
import string
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Usuario, Cliente, Venda, Evento, Empresa,
    Campanha, SegmentacaoCliente, Automacao, ExecucaoAutomacao,
    CupomDesconto, UsoCupom, ComunicacaoCliente, TemplateEmail
)
from ..schemas_meep_complete import (
    CampanhaCreate, CampanhaResponse,
    CupomDescontoCreate, CupomDescontoResponse,
    AutomacaoCreate, AutomacaoResponse
)

router = APIRouter(
    prefix="/api/marketing",
    tags=["Marketing & Automação"]
)

@router.post("/campanhas/create", response_model=CampanhaResponse)
async def criar_campanha(
    campanha: CampanhaCreate,
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova campanha de marketing
    Replica funcionalidade: Sistema Marketing > Nova Campanha
    """
    
    # Criar campanha
    nova_campanha = Campanha(
        nome=campanha.nome,
        descricao=campanha.descricao,
        tipo=campanha.tipo,
        segmentacao=campanha.segmentacao,
        conteudo=campanha.conteudo,
        data_inicio=campanha.data_inicio,
        data_fim=campanha.data_fim,
        empresa_id=current_user.empresa_id,
        criado_por=current_user.id,
        status="RASCUNHO"
    )
    
    db.add(nova_campanha)
    db.commit()
    db.refresh(nova_campanha)
    
    # Agendar envio se a campanha começar hoje
    if campanha.data_inicio.date() <= date.today():
        background_tasks.add_task(
            processar_campanha,
            nova_campanha.id,
            db
        )
    
    return nova_campanha

@router.get("/campanhas/list", response_model=List[CampanhaResponse])
async def listar_campanhas(
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar campanhas de marketing
    """
    
    query = db.query(Campanha)
    
    if current_user.empresa_id:
        query = query.filter(Campanha.empresa_id == current_user.empresa_id)
    
    if status:
        query = query.filter(Campanha.status == status)
    
    if tipo:
        query = query.filter(Campanha.tipo == tipo)
    
    campanhas = query.order_by(desc(Campanha.criado_em)).all()
    
    return campanhas

@router.post("/campanhas/{campanha_id}/activate")
async def ativar_campanha(
    campanha_id: int,
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ativar e enviar campanha
    Replica funcionalidade: Sistema Marketing > Enviar Campanha
    """
    
    campanha = db.query(Campanha).filter(
        Campanha.id == campanha_id
    ).first()
    
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    if campanha.status != "RASCUNHO":
        raise HTTPException(status_code=400, detail="Campanha já foi ativada")
    
    # Ativar campanha
    campanha.status = "ATIVA"
    db.commit()
    
    # Processar envio em background
    background_tasks.add_task(
        processar_campanha,
        campanha_id,
        db
    )
    
    return {"message": "Campanha ativada e sendo processada"}

def processar_campanha(campanha_id: int, db: Session):
    """
    Processar e enviar campanha para clientes segmentados
    """
    
    campanha = db.query(Campanha).filter(Campanha.id == campanha_id).first()
    if not campanha:
        return
    
    # Buscar clientes baseado na segmentação
    query = db.query(Cliente)
    
    # Aplicar filtros de segmentação
    segmentacao = campanha.segmentacao
    
    if "idade_min" in segmentacao:
        query = query.filter(
            Cliente.data_nascimento <= date.today() - timedelta(days=segmentacao["idade_min"] * 365)
        )
    
    if "idade_max" in segmentacao:
        query = query.filter(
            Cliente.data_nascimento >= date.today() - timedelta(days=segmentacao["idade_max"] * 365)
        )
    
    if "nivel_fidelidade" in segmentacao:
        query = query.filter(
            Cliente.nivel_fidelidade.in_(segmentacao["nivel_fidelidade"])
        )
    
    if "ultima_compra_dias" in segmentacao:
        data_limite = datetime.now() - timedelta(days=segmentacao["ultima_compra_dias"])
        query = query.join(Venda, Venda.cliente_cpf == Cliente.cpf).filter(
            Venda.criado_em >= data_limite
        )
    
    clientes = query.all()
    
    # Enviar para cada cliente
    enviados = 0
    for cliente in clientes:
        if campanha.tipo == "EMAIL" and cliente.email:
            # Simular envio de email
            comunicacao = ComunicacaoCliente(
                cliente_id=cliente.id,
                campanha_id=campanha_id,
                tipo="EMAIL",
                destinatario=cliente.email,
                conteudo=campanha.conteudo,
                status="ENVIADO",
                enviado_em=datetime.now()
            )
            db.add(comunicacao)
            enviados += 1
        
        elif campanha.tipo == "SMS" and cliente.telefone:
            # Simular envio de SMS
            comunicacao = ComunicacaoCliente(
                cliente_id=cliente.id,
                campanha_id=campanha_id,
                tipo="SMS",
                destinatario=cliente.telefone,
                conteudo=campanha.conteudo.get("mensagem", "")[:160],
                status="ENVIADO",
                enviado_em=datetime.now()
            )
            db.add(comunicacao)
            enviados += 1
        
        elif campanha.tipo == "PUSH":
            # Simular push notification
            comunicacao = ComunicacaoCliente(
                cliente_id=cliente.id,
                campanha_id=campanha_id,
                tipo="PUSH",
                destinatario=str(cliente.id),
                conteudo=campanha.conteudo,
                status="ENVIADO",
                enviado_em=datetime.now()
            )
            db.add(comunicacao)
            enviados += 1
    
    # Atualizar estatísticas da campanha
    campanha.enviados = enviados
    campanha.status = "CONCLUIDA" if datetime.now() > campanha.data_fim else "ATIVA"
    
    db.commit()

@router.post("/cupons/create", response_model=CupomDescontoResponse)
async def criar_cupom(
    cupom: CupomDescontoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar cupom de desconto
    Replica funcionalidade: Sistema Marketing > Cupons
    """
    
    # Verificar se código já existe
    cupom_existente = db.query(CupomDesconto).filter(
        CupomDesconto.codigo == cupom.codigo
    ).first()
    
    if cupom_existente:
        raise HTTPException(status_code=400, detail="Código de cupom já existe")
    
    # Criar cupom
    novo_cupom = CupomDesconto(
        codigo=cupom.codigo,
        descricao=cupom.descricao,
        tipo=cupom.tipo,
        valor=cupom.valor,
        quantidade_maxima=cupom.quantidade_maxima,
        quantidade_usada=0,
        valido_de=cupom.valido_de,
        valido_ate=cupom.valido_ate,
        condicoes=cupom.condicoes,
        empresa_id=current_user.empresa_id,
        ativo=True
    )
    
    db.add(novo_cupom)
    db.commit()
    db.refresh(novo_cupom)
    
    return novo_cupom

@router.post("/cupons/generate-batch")
async def gerar_cupons_lote(
    quantidade: int = Query(..., ge=1, le=1000),
    prefixo: str = Query(..., max_length=10),
    tipo: str = "PERCENTUAL",
    valor: Decimal = Query(...),
    validade_dias: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gerar lote de cupons únicos
    Replica funcionalidade: Sistema Marketing > Gerar Cupons em Lote
    """
    
    cupons_gerados = []
    valido_de = datetime.now()
    valido_ate = valido_de + timedelta(days=validade_dias)
    
    for i in range(quantidade):
        # Gerar código único
        codigo = f"{prefixo}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        cupom = CupomDesconto(
            codigo=codigo,
            descricao=f"Cupom gerado em lote - {prefixo}",
            tipo=tipo,
            valor=valor,
            quantidade_maxima=1,
            quantidade_usada=0,
            valido_de=valido_de,
            valido_ate=valido_ate,
            condicoes={},
            empresa_id=current_user.empresa_id,
            ativo=True
        )
        
        db.add(cupom)
        cupons_gerados.append(codigo)
    
    db.commit()
    
    return {
        "quantidade_gerada": quantidade,
        "prefixo": prefixo,
        "validade": validade_dias,
        "cupons": cupons_gerados[:10],  # Mostrar apenas os 10 primeiros
        "mensagem": f"{quantidade} cupons gerados com sucesso"
    }

@router.post("/cupons/validate")
async def validar_cupom(
    codigo: str,
    valor_compra: Decimal,
    cliente_cpf: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Validar cupom de desconto
    """
    
    cupom = db.query(CupomDesconto).filter(
        and_(
            CupomDesconto.codigo == codigo,
            CupomDesconto.ativo == True
        )
    ).first()
    
    if not cupom:
        return {"valido": False, "mensagem": "Cupom inválido"}
    
    # Verificar validade
    agora = datetime.now()
    if agora < cupom.valido_de or agora > cupom.valido_ate:
        return {"valido": False, "mensagem": "Cupom fora do período de validade"}
    
    # Verificar quantidade
    if cupom.quantidade_maxima and cupom.quantidade_usada >= cupom.quantidade_maxima:
        return {"valido": False, "mensagem": "Cupom esgotado"}
    
    # Verificar condições
    if "valor_minimo" in cupom.condicoes:
        if valor_compra < cupom.condicoes["valor_minimo"]:
            return {
                "valido": False,
                "mensagem": f"Valor mínimo de R$ {cupom.condicoes['valor_minimo']:.2f}"
            }
    
    # Calcular desconto
    if cupom.tipo == "PERCENTUAL":
        desconto = valor_compra * (cupom.valor / 100)
    else:
        desconto = min(cupom.valor, valor_compra)
    
    return {
        "valido": True,
        "desconto": float(desconto),
        "tipo": cupom.tipo,
        "valor": float(cupom.valor),
        "mensagem": "Cupom válido"
    }

@router.post("/automacao/create", response_model=AutomacaoResponse)
async def criar_automacao(
    automacao: AutomacaoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar automação de marketing
    Replica funcionalidade: Sistema Automação > Nova Automação
    """
    
    nova_automacao = Automacao(
        nome=automacao.nome,
        gatilho=automacao.gatilho,
        condicoes=automacao.condicoes,
        acoes=automacao.acoes,
        empresa_id=current_user.empresa_id,
        status=True,
        execucoes=0
    )
    
    db.add(nova_automacao)
    db.commit()
    db.refresh(nova_automacao)
    
    return nova_automacao

@router.get("/automacao/list", response_model=List[AutomacaoResponse])
async def listar_automacoes(
    ativo: Optional[bool] = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar automações configuradas
    """
    
    query = db.query(Automacao)
    
    if current_user.empresa_id:
        query = query.filter(Automacao.empresa_id == current_user.empresa_id)
    
    if ativo is not None:
        query = query.filter(Automacao.status == ativo)
    
    automacoes = query.all()
    
    return automacoes

@router.post("/automacao/trigger")
async def disparar_automacao(
    gatilho: str,
    contexto: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Disparar automações baseadas em gatilho
    Replica funcionalidade: Sistema Automação > Processar Gatilho
    """
    
    # Buscar automações ativas com este gatilho
    automacoes = db.query(Automacao).filter(
        and_(
            Automacao.gatilho == gatilho,
            Automacao.status == True
        )
    ).all()
    
    for automacao in automacoes:
        # Verificar condições
        if verificar_condicoes(automacao.condicoes, contexto):
            # Executar ações em background
            background_tasks.add_task(
                executar_acoes_automacao,
                automacao.id,
                contexto,
                db
            )
    
    return {
        "gatilho": gatilho,
        "automacoes_disparadas": len(automacoes)
    }

def verificar_condicoes(condicoes: Dict, contexto: Dict) -> bool:
    """
    Verificar se as condições da automação são atendidas
    """
    
    for campo, condicao in condicoes.items():
        if campo not in contexto:
            return False
        
        valor_contexto = contexto[campo]
        
        if isinstance(condicao, dict):
            if "min" in condicao and valor_contexto < condicao["min"]:
                return False
            if "max" in condicao and valor_contexto > condicao["max"]:
                return False
            if "igual" in condicao and valor_contexto != condicao["igual"]:
                return False
            if "contem" in condicao and condicao["contem"] not in valor_contexto:
                return False
        else:
            if valor_contexto != condicao:
                return False
    
    return True

def executar_acoes_automacao(automacao_id: int, contexto: Dict, db: Session):
    """
    Executar ações de uma automação
    """
    
    automacao = db.query(Automacao).filter(Automacao.id == automacao_id).first()
    if not automacao:
        return
    
    for acao in automacao.acoes:
        tipo_acao = acao.get("tipo")
        
        if tipo_acao == "ENVIAR_EMAIL":
            # Enviar email
            cliente_id = contexto.get("cliente_id")
            if cliente_id:
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                if cliente and cliente.email:
                    comunicacao = ComunicacaoCliente(
                        cliente_id=cliente_id,
                        tipo="EMAIL",
                        destinatario=cliente.email,
                        conteudo=acao.get("conteudo", {}),
                        status="ENVIADO",
                        enviado_em=datetime.now()
                    )
                    db.add(comunicacao)
        
        elif tipo_acao == "ADICIONAR_PONTOS":
            # Adicionar pontos de fidelidade
            cliente_id = contexto.get("cliente_id")
            if cliente_id:
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                if cliente:
                    cliente.pontos_fidelidade += acao.get("pontos", 0)
        
        elif tipo_acao == "CRIAR_CUPOM":
            # Criar cupom personalizado
            cliente_id = contexto.get("cliente_id")
            if cliente_id:
                codigo = f"AUTO-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
                cupom = CupomDesconto(
                    codigo=codigo,
                    descricao=acao.get("descricao", "Cupom automático"),
                    tipo=acao.get("tipo", "PERCENTUAL"),
                    valor=Decimal(str(acao.get("valor", 10))),
                    quantidade_maxima=1,
                    quantidade_usada=0,
                    valido_de=datetime.now(),
                    valido_ate=datetime.now() + timedelta(days=acao.get("validade_dias", 30)),
                    condicoes={"cliente_id": cliente_id},
                    ativo=True
                )
                db.add(cupom)
    
    # Registrar execução
    execucao = ExecucaoAutomacao(
        automacao_id=automacao_id,
        contexto=contexto,
        executado_em=datetime.now(),
        sucesso=True
    )
    db.add(execucao)
    
    # Atualizar contador
    automacao.execucoes += 1
    automacao.ultima_execucao = datetime.now()
    
    db.commit()

@router.get("/analytics/campaigns")
async def analytics_campanhas(
    periodo_dias: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analytics de campanhas de marketing
    Replica funcionalidade: Sistema Marketing > Analytics
    """
    
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Campanhas no período
    campanhas = db.query(Campanha).filter(
        and_(
            Campanha.criado_em >= data_inicio,
            Campanha.empresa_id == current_user.empresa_id if current_user.empresa_id else True
        )
    ).all()
    
    # Métricas gerais
    total_campanhas = len(campanhas)
    total_enviados = sum(c.enviados for c in campanhas)
    total_abertos = sum(c.abertos for c in campanhas)
    total_cliques = sum(c.cliques for c in campanhas)
    total_conversoes = sum(c.conversoes for c in campanhas)
    
    # Taxa média de abertura
    taxa_abertura = (total_abertos / total_enviados * 100) if total_enviados > 0 else 0
    
    # Taxa média de cliques
    taxa_cliques = (total_cliques / total_enviados * 100) if total_enviados > 0 else 0
    
    # Taxa média de conversão
    taxa_conversao = (total_conversoes / total_enviados * 100) if total_enviados > 0 else 0
    
    # Campanhas por tipo
    campanhas_por_tipo = {}
    for campanha in campanhas:
        if campanha.tipo not in campanhas_por_tipo:
            campanhas_por_tipo[campanha.tipo] = 0
        campanhas_por_tipo[campanha.tipo] += 1
    
    # Top campanhas por conversão
    top_campanhas = sorted(
        campanhas,
        key=lambda c: c.conversoes,
        reverse=True
    )[:5]
    
    return {
        "periodo_dias": periodo_dias,
        "metricas_gerais": {
            "total_campanhas": total_campanhas,
            "total_enviados": total_enviados,
            "taxa_abertura": taxa_abertura,
            "taxa_cliques": taxa_cliques,
            "taxa_conversao": taxa_conversao
        },
        "campanhas_por_tipo": campanhas_por_tipo,
        "top_campanhas": [
            {
                "nome": c.nome,
                "tipo": c.tipo,
                "enviados": c.enviados,
                "conversoes": c.conversoes,
                "roi": ((c.conversoes * 100) / c.enviados) if c.enviados > 0 else 0
            }
            for c in top_campanhas
        ]
    }

@router.get("/segmentation/analysis")
async def analise_segmentacao(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Análise de segmentação de clientes
    Replica funcionalidade: Sistema Marketing > Segmentação
    """
    
    # Total de clientes
    total_clientes = db.query(func.count(Cliente.id)).scalar()
    
    # Segmentação por nível de fidelidade
    segmentacao_fidelidade = db.query(
        Cliente.nivel_fidelidade,
        func.count(Cliente.id).label("quantidade")
    ).group_by(
        Cliente.nivel_fidelidade
    ).all()
    
    # Segmentação por frequência de compra
    clientes_frequencia = db.query(
        Cliente.id,
        func.count(Venda.id).label("total_compras")
    ).join(
        Venda,
        Venda.cliente_cpf == Cliente.cpf
    ).group_by(
        Cliente.id
    ).all()
    
    frequencia_segmentos = {
        "alta_frequencia": 0,  # > 10 compras
        "media_frequencia": 0,  # 5-10 compras
        "baixa_frequencia": 0,  # 1-4 compras
        "sem_compras": 0
    }
    
    for cliente in clientes_frequencia:
        if cliente.total_compras > 10:
            frequencia_segmentos["alta_frequencia"] += 1
        elif cliente.total_compras >= 5:
            frequencia_segmentos["media_frequencia"] += 1
        elif cliente.total_compras >= 1:
            frequencia_segmentos["baixa_frequencia"] += 1
    
    frequencia_segmentos["sem_compras"] = total_clientes - sum(frequencia_segmentos.values())
    
    # Segmentação por valor gasto
    clientes_valor = db.query(
        Cliente.id,
        func.sum(Venda.valor_total).label("valor_total")
    ).join(
        Venda,
        Venda.cliente_cpf == Cliente.cpf
    ).group_by(
        Cliente.id
    ).all()
    
    valor_segmentos = {
        "alto_valor": 0,  # > R$ 5000
        "medio_valor": 0,  # R$ 1000-5000
        "baixo_valor": 0   # < R$ 1000
    }
    
    for cliente in clientes_valor:
        if cliente.valor_total > 5000:
            valor_segmentos["alto_valor"] += 1
        elif cliente.valor_total >= 1000:
            valor_segmentos["medio_valor"] += 1
        else:
            valor_segmentos["baixo_valor"] += 1
    
    return {
        "total_clientes": total_clientes,
        "segmentacao_fidelidade": [
            {"nivel": s.nivel_fidelidade, "quantidade": s.quantidade}
            for s in segmentacao_fidelidade
        ],
        "segmentacao_frequencia": frequencia_segmentos,
        "segmentacao_valor": valor_segmentos,
        "recomendacoes": [
            {
                "segmento": "alta_frequencia + alto_valor",
                "acao": "Programa VIP exclusivo",
                "potencial": "Alto"
            },
            {
                "segmento": "baixa_frequencia + alto_valor",
                "acao": "Campanha de reativação",
                "potencial": "Médio"
            },
            {
                "segmento": "sem_compras",
                "acao": "Cupom de primeira compra",
                "potencial": "Baixo"
            }
        ]
    }
