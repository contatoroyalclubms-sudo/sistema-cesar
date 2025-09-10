"""
Router para Clientes Completo - CRM avançado
Gestão de clientes, fidelidade, segmentação, histórico
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Usuario, Cliente, Venda, TransacaoCashless, Evento,
    HistoricoCliente, SegmentacaoCliente, ProgramaFidelidade,
    NivelFidelidade, PontosFidelidade, CategoriaCliente
)
from ..schemas_meep_complete import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    ProgramaFidelidade as ProgramaFidelidadeSchema
)

router = APIRouter(
    prefix="/api/clientes",
    tags=["Clientes & CRM"]
)

@router.get("/dashboard")
async def dashboard_clientes(
    periodo_dias: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard de clientes com métricas principais
    Replica funcionalidade: Sistema Clientes > Dashboard
    """
    
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Total de clientes
    total_clientes = db.query(func.count(Cliente.id)).filter(
        Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
    ).scalar()
    
    # Novos clientes no período
    novos_clientes = db.query(func.count(Cliente.id)).filter(
        and_(
            Cliente.criado_em >= data_inicio,
            Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
        )
    ).scalar()
    
    # Clientes ativos (com compras no período)
    clientes_ativos = db.query(
        func.count(func.distinct(Venda.cliente_cpf))
    ).filter(
        Venda.criado_em >= data_inicio
    ).scalar()
    
    # Taxa de ativação
    taxa_ativacao = (clientes_ativos / total_clientes * 100) if total_clientes > 0 else 0
    
    # Ticket médio por cliente
    ticket_medio = db.query(
        func.avg(Venda.valor_total)
    ).filter(
        and_(
            Venda.criado_em >= data_inicio,
            Venda.status == "CONCLUIDA"
        )
    ).scalar() or Decimal(0)
    
    # Lifetime Value médio
    ltv_medio = db.query(
        func.avg(
            db.query(func.sum(Venda.valor_total)).filter(
                Venda.cliente_cpf == Cliente.cpf
            ).scalar_subquery()
        )
    ).scalar() or 0
    
    # Top 10 clientes por valor
    top_clientes = db.query(
        Cliente.nome,
        Cliente.cpf,
        func.sum(Venda.valor_total).label("valor_total")
    ).join(
        Venda, Venda.cliente_cpf == Cliente.cpf
    ).group_by(
        Cliente.id, Cliente.nome, Cliente.cpf
    ).order_by(
        desc("valor_total")
    ).limit(10).all()
    
    # Distribuição por nível de fidelidade
    distribuicao_fidelidade = db.query(
        Cliente.nivel_fidelidade,
        func.count(Cliente.id).label("quantidade")
    ).group_by(
        Cliente.nivel_fidelidade
    ).all()
    
    return {
        "periodo_dias": periodo_dias,
        "metricas": {
            "total_clientes": total_clientes,
            "novos_clientes": novos_clientes,
            "clientes_ativos": clientes_ativos,
            "taxa_ativacao": float(taxa_ativacao),
            "ticket_medio": float(ticket_medio),
            "ltv_medio": float(ltv_medio)
        },
        "top_clientes": [
            {
                "nome": c.nome,
                "cpf": c.cpf,
                "valor_total": float(c.valor_total)
            }
            for c in top_clientes
        ],
        "distribuicao_fidelidade": [
            {
                "nivel": f.nivel_fidelidade,
                "quantidade": f.quantidade
            }
            for f in distribuicao_fidelidade
        ]
    }

@router.post("/create", response_model=ClienteResponse)
async def criar_cliente(
    cliente: ClienteCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar novo cliente
    Replica funcionalidade: Sistema Clientes > Novo Cliente
    """
    
    # Verificar se CPF já existe
    cliente_existente = db.query(Cliente).filter(
        Cliente.cpf == cliente.cpf
    ).first()
    
    if cliente_existente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Criar cliente
    novo_cliente = Cliente(
        nome=cliente.nome,
        cpf=cliente.cpf,
        email=cliente.email,
        telefone=cliente.telefone,
        data_nascimento=cliente.data_nascimento,
        categoria_id=cliente.categoria_id,
        tag_rfid=cliente.tag_rfid,
        empresa_id=cliente.empresa_id,
        nivel_fidelidade="BRONZE",
        pontos_fidelidade=0,
        saldo_cashless=Decimal(0),
        ativo=True
    )
    
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    
    # Registrar histórico
    historico = HistoricoCliente(
        cliente_id=novo_cliente.id,
        evento="CADASTRO",
        descricao="Cliente cadastrado no sistema",
        usuario_id=current_user.id
    )
    db.add(historico)
    db.commit()
    
    return novo_cliente

@router.get("/list", response_model=List[ClienteResponse])
async def listar_clientes(
    q: Optional[str] = None,
    categoria_id: Optional[int] = None,
    nivel_fidelidade: Optional[str] = None,
    ativo: Optional[bool] = True,
    page: int = 1,
    size: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar clientes com filtros e paginação
    """
    
    query = db.query(Cliente)
    
    if current_user.empresa_id:
        query = query.filter(Cliente.empresa_id == current_user.empresa_id)
    
    if q:
        query = query.filter(
            or_(
                Cliente.nome.ilike(f"%{q}%"),
                Cliente.cpf.ilike(f"%{q}%"),
                Cliente.email.ilike(f"%{q}%")
            )
        )
    
    if categoria_id:
        query = query.filter(Cliente.categoria_id == categoria_id)
    
    if nivel_fidelidade:
        query = query.filter(Cliente.nivel_fidelidade == nivel_fidelidade)
    
    if ativo is not None:
        query = query.filter(Cliente.ativo == ativo)
    
    # Paginação
    offset = (page - 1) * size
    clientes = query.offset(offset).limit(size).all()
    
    return clientes

@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obter_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter detalhes completos de um cliente
    """
    
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente

@router.get("/{cliente_id}/historico")
async def historico_cliente(
    cliente_id: int,
    limit: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Histórico completo do cliente
    Replica funcionalidade: Sistema Clientes > Histórico
    """
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Histórico de vendas
    vendas = db.query(Venda).filter(
        Venda.cliente_cpf == cliente.cpf
    ).order_by(desc(Venda.criado_em)).limit(limit).all()
    
    # Histórico de transações cashless
    transacoes = db.query(TransacaoCashless).filter(
        TransacaoCashless.cliente_id == cliente_id
    ).order_by(desc(TransacaoCashless.criado_em)).limit(limit).all()
    
    # Histórico de eventos
    historico_eventos = db.query(HistoricoCliente).filter(
        HistoricoCliente.cliente_id == cliente_id
    ).order_by(desc(HistoricoCliente.criado_em)).limit(limit).all()
    
    # Estatísticas do cliente
    total_compras = len(vendas)
    valor_total = sum(v.valor_total for v in vendas)
    ticket_medio = valor_total / total_compras if total_compras > 0 else Decimal(0)
    ultima_compra = vendas[0].criado_em if vendas else None
    
    return {
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "cpf": cliente.cpf,
            "nivel_fidelidade": cliente.nivel_fidelidade,
            "pontos_fidelidade": cliente.pontos_fidelidade,
            "saldo_cashless": float(cliente.saldo_cashless)
        },
        "estatisticas": {
            "total_compras": total_compras,
            "valor_total": float(valor_total),
            "ticket_medio": float(ticket_medio),
            "ultima_compra": ultima_compra.isoformat() if ultima_compra else None
        },
        "vendas": [
            {
                "id": v.id,
                "numero_venda": v.numero_venda,
                "valor_total": float(v.valor_total),
                "tipo_pagamento": v.tipo_pagamento,
                "criado_em": v.criado_em.isoformat()
            }
            for v in vendas
        ],
        "transacoes_cashless": [
            {
                "id": t.id,
                "tipo": t.tipo,
                "valor": float(t.valor),
                "descricao": t.descricao,
                "criado_em": t.criado_em.isoformat()
            }
            for t in transacoes
        ],
        "historico_eventos": [
            {
                "evento": h.evento,
                "descricao": h.descricao,
                "criado_em": h.criado_em.isoformat()
            }
            for h in historico_eventos
        ]
    }

@router.post("/{cliente_id}/pontos/adicionar")
async def adicionar_pontos(
    cliente_id: int,
    pontos: int = Query(..., gt=0),
    motivo: str = Query(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Adicionar pontos de fidelidade
    Replica funcionalidade: Sistema Fidelidade > Adicionar Pontos
    """
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Adicionar pontos
    pontos_anteriores = cliente.pontos_fidelidade
    cliente.pontos_fidelidade += pontos
    
    # Verificar mudança de nível
    nivel_anterior = cliente.nivel_fidelidade
    
    if cliente.pontos_fidelidade >= 10000:
        cliente.nivel_fidelidade = "DIAMANTE"
    elif cliente.pontos_fidelidade >= 5000:
        cliente.nivel_fidelidade = "OURO"
    elif cliente.pontos_fidelidade >= 1000:
        cliente.nivel_fidelidade = "PRATA"
    else:
        cliente.nivel_fidelidade = "BRONZE"
    
    # Registrar movimentação de pontos
    registro_pontos = PontosFidelidade(
        cliente_id=cliente_id,
        tipo="CREDITO",
        pontos=pontos,
        saldo_anterior=pontos_anteriores,
        saldo_posterior=cliente.pontos_fidelidade,
        motivo=motivo,
        usuario_id=current_user.id
    )
    db.add(registro_pontos)
    
    # Registrar histórico
    historico = HistoricoCliente(
        cliente_id=cliente_id,
        evento="PONTOS_ADICIONADOS",
        descricao=f"Adicionados {pontos} pontos. Motivo: {motivo}",
        usuario_id=current_user.id
    )
    db.add(historico)
    
    # Se mudou de nível, registrar
    if nivel_anterior != cliente.nivel_fidelidade:
        historico_nivel = HistoricoCliente(
            cliente_id=cliente_id,
            evento="MUDANCA_NIVEL",
            descricao=f"Nível alterado de {nivel_anterior} para {cliente.nivel_fidelidade}",
            usuario_id=current_user.id
        )
        db.add(historico_nivel)
    
    db.commit()
    
    return {
        "cliente_id": cliente_id,
        "pontos_adicionados": pontos,
        "saldo_anterior": pontos_anteriores,
        "saldo_atual": cliente.pontos_fidelidade,
        "nivel_anterior": nivel_anterior,
        "nivel_atual": cliente.nivel_fidelidade,
        "mudou_nivel": nivel_anterior != cliente.nivel_fidelidade
    }

@router.post("/{cliente_id}/pontos/resgatar")
async def resgatar_pontos(
    cliente_id: int,
    pontos: int = Query(..., gt=0),
    tipo_resgate: str = Query(..., description="DESCONTO, PRODUTO, CASHBACK"),
    valor: Decimal = Query(...),
    descricao: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resgatar pontos de fidelidade
    """
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if cliente.pontos_fidelidade < pontos:
        raise HTTPException(status_code=400, detail="Pontos insuficientes")
    
    # Descontar pontos
    pontos_anteriores = cliente.pontos_fidelidade
    cliente.pontos_fidelidade -= pontos
    
    # Se for cashback, adicionar ao saldo cashless
    if tipo_resgate == "CASHBACK":
        cliente.saldo_cashless += valor
    
    # Registrar movimentação de pontos
    registro_pontos = PontosFidelidade(
        cliente_id=cliente_id,
        tipo="DEBITO",
        pontos=pontos,
        saldo_anterior=pontos_anteriores,
        saldo_posterior=cliente.pontos_fidelidade,
        motivo=f"Resgate {tipo_resgate}: {descricao or valor}",
        usuario_id=current_user.id
    )
    db.add(registro_pontos)
    
    # Registrar histórico
    historico = HistoricoCliente(
        cliente_id=cliente_id,
        evento="PONTOS_RESGATADOS",
        descricao=f"Resgatados {pontos} pontos - {tipo_resgate}: {valor}",
        usuario_id=current_user.id
    )
    db.add(historico)
    
    db.commit()
    
    return {
        "cliente_id": cliente_id,
        "pontos_resgatados": pontos,
        "saldo_anterior": pontos_anteriores,
        "saldo_atual": cliente.pontos_fidelidade,
        "tipo_resgate": tipo_resgate,
        "valor": float(valor),
        "cashback_adicionado": tipo_resgate == "CASHBACK"
    }

@router.get("/segmentacao/analise")
async def analise_segmentacao_clientes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Análise de segmentação RFM (Recency, Frequency, Monetary)
    Replica funcionalidade: Sistema Clientes > Segmentação
    """
    
    # Buscar dados de clientes com compras
    clientes_dados = db.query(
        Cliente.id,
        Cliente.nome,
        Cliente.cpf,
        func.max(Venda.criado_em).label("ultima_compra"),
        func.count(Venda.id).label("frequencia"),
        func.sum(Venda.valor_total).label("valor_total")
    ).join(
        Venda, Venda.cliente_cpf == Cliente.cpf
    ).group_by(
        Cliente.id, Cliente.nome, Cliente.cpf
    ).all()
    
    agora = datetime.now()
    segmentos = {
        "champions": [],
        "loyal_customers": [],
        "potential_loyalists": [],
        "new_customers": [],
        "promising": [],
        "need_attention": [],
        "about_to_sleep": [],
        "at_risk": [],
        "cannot_lose_them": [],
        "hibernating": [],
        "lost": []
    }
    
    for cliente in clientes_dados:
        # Calcular Recency (dias desde última compra)
        recency = (agora - cliente.ultima_compra).days
        frequency = cliente.frequencia
        monetary = float(cliente.valor_total)
        
        # Scores RFM (1-5)
        if recency <= 30:
            r_score = 5
        elif recency <= 90:
            r_score = 4
        elif recency <= 180:
            r_score = 3
        elif recency <= 365:
            r_score = 2
        else:
            r_score = 1
        
        if frequency >= 10:
            f_score = 5
        elif frequency >= 5:
            f_score = 4
        elif frequency >= 3:
            f_score = 3
        elif frequency >= 2:
            f_score = 2
        else:
            f_score = 1
        
        if monetary >= 5000:
            m_score = 5
        elif monetary >= 2000:
            m_score = 4
        elif monetary >= 1000:
            m_score = 3
        elif monetary >= 500:
            m_score = 2
        else:
            m_score = 1
        
        # Segmentação baseada nos scores
        rfm_score = f"{r_score}{f_score}{m_score}"
        
        cliente_info = {
            "id": cliente.id,
            "nome": cliente.nome,
            "cpf": cliente.cpf,
            "recency": recency,
            "frequency": frequency,
            "monetary": monetary,
            "rfm_score": rfm_score
        }
        
        # Classificação em segmentos
        if r_score >= 4 and f_score >= 4 and m_score >= 4:
            segmentos["champions"].append(cliente_info)
        elif r_score >= 3 and f_score >= 4:
            segmentos["loyal_customers"].append(cliente_info)
        elif r_score >= 4 and f_score <= 2:
            segmentos["new_customers"].append(cliente_info)
        elif r_score >= 3 and f_score >= 2 and m_score >= 3:
            segmentos["potential_loyalists"].append(cliente_info)
        elif r_score >= 3 and m_score >= 4:
            segmentos["promising"].append(cliente_info)
        elif r_score == 3 and f_score <= 3:
            segmentos["need_attention"].append(cliente_info)
        elif r_score == 2 and f_score <= 2:
            segmentos["about_to_sleep"].append(cliente_info)
        elif r_score == 2 and f_score >= 3:
            segmentos["at_risk"].append(cliente_info)
        elif r_score == 1 and f_score >= 4:
            segmentos["cannot_lose_them"].append(cliente_info)
        elif r_score == 1 and f_score <= 2:
            segmentos["hibernating"].append(cliente_info)
        else:
            segmentos["lost"].append(cliente_info)
    
    # Estatísticas por segmento
    estatisticas = {}
    for segmento, clientes in segmentos.items():
        if clientes:
            estatisticas[segmento] = {
                "quantidade": len(clientes),
                "valor_medio": sum(c["monetary"] for c in clientes) / len(clientes),
                "frequencia_media": sum(c["frequency"] for c in clientes) / len(clientes)
            }
        else:
            estatisticas[segmento] = {
                "quantidade": 0,
                "valor_medio": 0,
                "frequencia_media": 0
            }
    
    return {
        "total_clientes_analisados": len(clientes_dados),
        "segmentos": segmentos,
        "estatisticas": estatisticas,
        "recomendacoes": {
            "champions": "Recompense-os. Eles podem ser defensores da marca.",
            "loyal_customers": "Upsell produtos de maior valor. Peça reviews.",
            "potential_loyalists": "Ofereça programa de membership/fidelidade.",
            "new_customers": "Fornecer suporte on-boarding, experiencia gratuita.",
            "promising": "Criar conscientização da marca, oferecer testes gratuitos.",
            "need_attention": "Fazer ofertas limitadas, recomendar baseado em histórico.",
            "about_to_sleep": "Compartilhar recursos valiosos, recomendar produtos/ser.",
            "at_risk": "Enviar emails personalizados para se reconectar, oferecer renovacoes.",
            "cannot_lose_them": "Ganhar de volta via renovacoes ou produtos mais novos.",
            "hibernating": "Ofertas com grandes descontos para recriaçao de interesse",
            "lost": "Revitalizar interesse com pesquisa, ignore ou foque em outros"
        }
    }

@router.post("/categorias/create")
async def criar_categoria_cliente(
    nome: str,
    descricao: Optional[str] = None,
    cor: Optional[str] = None,
    desconto_percentual: Optional[Decimal] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar categoria de clientes
    Replica funcionalidade: Sistema Clientes > Categorias
    """
    
    nova_categoria = CategoriaCliente(
        nome=nome,
        descricao=descricao,
        cor=cor,
        desconto_percentual=desconto_percentual,
        empresa_id=current_user.empresa_id,
        ativo=True
    )
    
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    
    return nova_categoria

@router.get("/aniversariantes")
async def aniversariantes_mes(
    mes: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista de aniversariantes do mês
    """
    
    if not mes:
        mes = date.today().month
    
    aniversariantes = db.query(Cliente).filter(
        and_(
            extract('month', Cliente.data_nascimento) == mes,
            Cliente.ativo == True,
            Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
        )
    ).order_by(
        extract('day', Cliente.data_nascimento)
    ).all()
    
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "email": c.email,
            "telefone": c.telefone,
            "data_nascimento": c.data_nascimento.isoformat() if c.data_nascimento else None,
            "idade": (
                date.today().year - c.data_nascimento.year -
                ((date.today().month, date.today().day) < 
                 (c.data_nascimento.month, c.data_nascimento.day))
            ) if c.data_nascimento else None
        }
        for c in aniversariantes
    ]

@router.get("/inativos")
async def clientes_inativos(
    dias_sem_compra: int = 90,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clientes inativos (sem compras há X dias)
    """
    
    data_limite = datetime.now() - timedelta(days=dias_sem_compra)
    
    # Clientes com última compra antes da data limite
    clientes_inativos = db.query(
        Cliente.id,
        Cliente.nome,
        Cliente.cpf,
        Cliente.email,
        Cliente.telefone,
        func.max(Venda.criado_em).label("ultima_compra"),
        func.sum(Venda.valor_total).label("valor_total")
    ).join(
        Venda, Venda.cliente_cpf == Cliente.cpf
    ).filter(
        Cliente.empresa_id == current_user.empresa_id if current_user.empresa_id else True
    ).group_by(
        Cliente.id, Cliente.nome, Cliente.cpf, Cliente.email, Cliente.telefone
    ).having(
        func.max(Venda.criado_em) < data_limite
    ).all()
    
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "email": c.email,
            "telefone": c.telefone,
            "ultima_compra": c.ultima_compra.isoformat(),
            "dias_sem_compra": (datetime.now() - c.ultima_compra).days,
            "valor_total_historico": float(c.valor_total),
            "risco_perda": (
                "Alto" if (datetime.now() - c.ultima_compra).days > 180 else
                "Médio" if (datetime.now() - c.ultima_compra).days > 120 else
                "Baixo"
            )
        }
        for c in clientes_inativos
    ]
