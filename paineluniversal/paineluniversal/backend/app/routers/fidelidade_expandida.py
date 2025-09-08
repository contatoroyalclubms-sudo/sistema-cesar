"""
Router para Sistema de Fidelidade Expandido
Gestão completa de níveis, pontuação, campanhas e recompensas
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random
import string

from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario, Produto, Empresa, Cliente
from ..models_fidelidade import (
    NivelFidelidade, TipoNivelFidelidade,
    PontuacaoCliente, TipoMovimentacaoPonto,
    CampanhaFidelidade, StatusCampanha, TipoRecompensa,
    IndicacaoCliente, StatusIndicacao,
    ResgateRecompensa, RegrasAcumuloPontos,
    HistoricoNivelCliente
)

router = APIRouter()

# ================================================================================
# SCHEMAS PYDANTIC
# ================================================================================

from pydantic import BaseModel, validator
from enum import Enum

class NivelFidelidadeCreate(BaseModel):
    nome: str
    tipo: TipoNivelFidelidade
    cor_hexadecimal: str = "#888888"
    icone: Optional[str] = None
    pontos_minimos: int = 0
    valor_gasto_minimo: float = 0
    compras_minimas: int = 0
    multiplicador_pontos: float = 1.0
    desconto_percentual: float = 0.0
    frete_gratis: bool = False
    acesso_ofertas_exclusivas: bool = False
    suporte_prioritario: bool = False
    descricao: Optional[str] = None

class CampanhaFidelidadeCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    publico_alvo: str = "todos"
    limite_participantes: Optional[int] = None
    multiplicador_pontos: float = 1.0
    pontos_bonus: int = 0
    valor_minimo_compra: Optional[float] = None
    tipo_recompensa: Optional[TipoRecompensa] = None
    valor_recompensa: Optional[float] = None
    produto_recompensa_id: Optional[int] = None
    requer_codigo: bool = False

class ResgateRecompensaCreate(BaseModel):
    tipo_recompensa: TipoRecompensa
    pontos_utilizados: int
    valor_desconto: Optional[float] = None
    percentual_desconto: Optional[float] = None
    produto_id: Optional[int] = None
    data_expiracao: Optional[datetime] = None

class IndicacaoCreate(BaseModel):
    nome_indicado: str
    email_indicado: str
    telefone_indicado: Optional[str] = None

class MovimentacaoPontosCreate(BaseModel):
    cliente_id: int
    tipo_movimentacao: TipoMovimentacaoPonto
    pontos: int
    motivo: str
    observacoes: Optional[str] = None

# ================================================================================
# CONSTANTES
# ================================================================================

CLIENTE_NAO_ENCONTRADO = "Cliente não encontrado"
NIVEL_NAO_ENCONTRADO = "Nível de fidelidade não encontrado"
PONTOS_INSUFICIENTES = "Pontos insuficientes"

# ================================================================================
# NÍVEIS DE FIDELIDADE
# ================================================================================

@router.post("/niveis", response_model=dict)
async def criar_nivel_fidelidade(
    nivel_data: NivelFidelidadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo nível de fidelidade"""
    
    try:
        # Verificar se já existe nível com mesmo tipo
        existe = db.query(NivelFidelidade).filter(
            NivelFidelidade.empresa_id == current_user.empresa_id,
            NivelFidelidade.tipo == nivel_data.tipo
        ).first()
        
        if existe:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um nível {nivel_data.tipo.value}"
            )
        
        nivel = NivelFidelidade(
            empresa_id=current_user.empresa_id,
            **nivel_data.model_dump(),
            criado_por_id=current_user.id
        )
        
        db.add(nivel)
        db.commit()
        db.refresh(nivel)
        
        return {
            "id": nivel.id,
            "message": "Nível de fidelidade criado com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/niveis", response_model=List[dict])
async def listar_niveis_fidelidade(
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar níveis de fidelidade"""
    
    query = db.query(NivelFidelidade).filter(
        NivelFidelidade.empresa_id == current_user.empresa_id
    )
    
    if ativo is not None:
        query = query.filter(NivelFidelidade.ativo == ativo)
    
    niveis = query.order_by(NivelFidelidade.ordem_exibicao, NivelFidelidade.pontos_minimos).all()
    
    # Adicionar estatísticas de clientes por nível
    resultado = []
    for nivel in niveis:
        total_clientes = db.query(func.count(Cliente.id)).filter(
            Cliente.empresa_id == current_user.empresa_id,
            Cliente.nivel_fidelidade_id == nivel.id
        ).scalar() or 0
        
        resultado.append({
            "nivel": nivel,
            "total_clientes": total_clientes
        })
    
    return resultado

@router.patch("/niveis/{nivel_id}", response_model=dict)
async def atualizar_nivel_fidelidade(
    nivel_id: int,
    dados: dict,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar nível de fidelidade"""
    
    nivel = db.query(NivelFidelidade).filter(
        NivelFidelidade.id == nivel_id,
        NivelFidelidade.empresa_id == current_user.empresa_id
    ).first()
    
    if not nivel:
        raise HTTPException(status_code=404, detail=NIVEL_NAO_ENCONTRADO)
    
    try:
        for campo, valor in dados.items():
            if hasattr(nivel, campo):
                setattr(nivel, campo, valor)
        
        nivel.atualizado_em = datetime.now(timezone.utc)
        db.commit()
        
        return {"message": "Nível atualizado com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# GESTÃO DE PONTOS
# ================================================================================

@router.post("/pontos/movimentacao", response_model=dict)
async def criar_movimentacao_pontos(
    movimento: MovimentacaoPontosCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar movimentação de pontos (manual)"""
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(
        Cliente.id == movimento.cliente_id,
        Cliente.empresa_id == current_user.empresa_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail=CLIENTE_NAO_ENCONTRADO)
    
    try:
        pontos_antes = cliente.pontos_atuais or 0
        
        # Validar operação
        if movimento.tipo_movimentacao == TipoMovimentacaoPonto.RESGATE:
            if pontos_antes < movimento.pontos:
                raise HTTPException(status_code=400, detail=PONTOS_INSUFICIENTES)
            pontos_depois = pontos_antes - movimento.pontos
        else:
            pontos_depois = pontos_antes + movimento.pontos
        
        # Criar movimentação
        pontuacao = PontuacaoCliente(
            empresa_id=current_user.empresa_id,
            cliente_id=movimento.cliente_id,
            tipo_movimentacao=movimento.tipo_movimentacao,
            pontos=movimento.pontos,
            pontos_antes=pontos_antes,
            pontos_depois=pontos_depois,
            motivo=movimento.motivo,
            observacoes=movimento.observacoes,
            criado_por_id=current_user.id
        )
        
        db.add(pontuacao)
        
        # Atualizar cliente
        cliente.pontos_atuais = pontos_depois
        if movimento.tipo_movimentacao == TipoMovimentacaoPonto.ACUMULO:
            cliente.pontos_totais_acumulados = (cliente.pontos_totais_acumulados or 0) + movimento.pontos
        elif movimento.tipo_movimentacao == TipoMovimentacaoPonto.RESGATE:
            cliente.pontos_totais_resgatados = (cliente.pontos_totais_resgatados or 0) + movimento.pontos
        
        # Verificar mudança de nível
        if hasattr(current_user, 'id') and current_user.id is not None:
            _verificar_mudanca_nivel(db, cliente, current_user.id)
        
        db.commit()
        
        return {
            "message": "Movimentação registrada com sucesso",
            "pontos_anteriores": pontos_antes,
            "pontos_atuais": pontos_depois
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pontos/historico/{cliente_id}", response_model=List[dict])
async def obter_historico_pontos(
    cliente_id: int,
    limite: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter histórico de pontos do cliente"""
    
    historico = db.query(PontuacaoCliente).filter(
        PontuacaoCliente.cliente_id == cliente_id,
        PontuacaoCliente.empresa_id == current_user.empresa_id
    ).order_by(desc(PontuacaoCliente.criado_em)).limit(limite).all()
    
    return [
        {
            "movimentacao": h,
            "saldo_periodo": h.pontos_depois
        } for h in historico
    ]

# ================================================================================
# CAMPANHAS DE FIDELIDADE
# ================================================================================

@router.post("/campanhas", response_model=dict)
async def criar_campanha_fidelidade(
    campanha_data: CampanhaFidelidadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova campanha de fidelidade"""
    
    try:
        # Gerar código único se necessário
        codigo = None
        if campanha_data.requer_codigo:
            codigo = _gerar_codigo_campanha()
            while db.query(CampanhaFidelidade).filter(CampanhaFidelidade.codigo == codigo).first():
                codigo = _gerar_codigo_campanha()
        
        campanha = CampanhaFidelidade(
            empresa_id=current_user.empresa_id,
            **campanha_data.model_dump(),
            codigo=codigo,
            criado_por_id=current_user.id
        )
        
        db.add(campanha)
        db.commit()
        db.refresh(campanha)
        
        return {
            "id": campanha.id,
            "codigo": codigo,
            "message": "Campanha criada com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campanhas", response_model=List[dict])
async def listar_campanhas_fidelidade(
    status: Optional[StatusCampanha] = Query(None),
    ativa: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar campanhas de fidelidade"""
    
    query = db.query(CampanhaFidelidade).filter(
        CampanhaFidelidade.empresa_id == current_user.empresa_id
    )
    
    if status:
        query = query.filter(CampanhaFidelidade.status == status)
    
    if ativa is not None:
        now = datetime.now(timezone.utc)
        if ativa:
            query = query.filter(
                CampanhaFidelidade.data_inicio <= now,
                CampanhaFidelidade.data_fim >= now,
                CampanhaFidelidade.status == StatusCampanha.ATIVA
            )
    
    campanhas = query.order_by(desc(CampanhaFidelidade.criado_em)).all()
    
    return [{"campanha": c} for c in campanhas]

# ================================================================================
# SISTEMA DE INDICAÇÕES
# ================================================================================

@router.post("/indicacoes", response_model=dict)
async def criar_indicacao(
    indicacao_data: IndicacaoCreate,
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova indicação"""
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.empresa_id == current_user.empresa_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail=CLIENTE_NAO_ENCONTRADO)
    
    try:
        # Gerar código único
        codigo = _gerar_codigo_indicacao()
        while db.query(IndicacaoCliente).filter(IndicacaoCliente.codigo_indicacao == codigo).first():
            codigo = _gerar_codigo_indicacao()
        
        indicacao = IndicacaoCliente(
            empresa_id=current_user.empresa_id,
            cliente_indicador_id=cliente_id,
            codigo_indicacao=codigo,
            **indicacao_data.model_dump(),
            pontos_indicador=100,  # Configurável
            pontos_indicado=50     # Configurável
        )
        
        db.add(indicacao)
        db.commit()
        
        return {
            "id": indicacao.id,
            "codigo_indicacao": codigo,
            "message": "Indicação criada com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/indicacoes/{codigo}/confirmar", response_model=dict)
async def confirmar_indicacao(
    codigo: str,
    cliente_indicado_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Confirmar indicação quando indicado se cadastra"""
    
    # Buscar indicação
    indicacao = db.query(IndicacaoCliente).filter(
        IndicacaoCliente.codigo_indicacao == codigo,
        IndicacaoCliente.empresa_id == current_user.empresa_id,
        IndicacaoCliente.status == StatusIndicacao.PENDENTE
    ).first()
    
    if not indicacao:
        raise HTTPException(status_code=404, detail="Código de indicação inválido")
    
    try:
        # Atualizar indicação
        indicacao.cliente_indicado_id = cliente_indicado_id
        indicacao.status = StatusIndicacao.CONFIRMADA
        indicacao.data_confirmacao = datetime.now(timezone.utc)
        
        # Recompensar indicador
        _recompensar_indicacao(db, indicacao, current_user.id)
        
        db.commit()
        
        return {"message": "Indicação confirmada com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# RESGATES E RECOMPENSAS
# ================================================================================

@router.post("/resgates", response_model=dict)
async def criar_resgate_recompensa(
    cliente_id: int,
    resgate_data: ResgateRecompensaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar resgate de recompensa"""
    
    # Verificar cliente
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.empresa_id == current_user.empresa_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail=CLIENTE_NAO_ENCONTRADO)
    
    # Verificar pontos
    if cliente.pontos_atuais < resgate_data.pontos_utilizados:
        raise HTTPException(status_code=400, detail=PONTOS_INSUFICIENTES)
    
    try:
        # Gerar código único
        codigo = _gerar_codigo_resgate()
        while db.query(ResgateRecompensa).filter(ResgateRecompensa.codigo_resgate == codigo).first():
            codigo = _gerar_codigo_resgate()
        
        # Criar resgate
        resgate = ResgateRecompensa(
            empresa_id=current_user.empresa_id,
            cliente_id=cliente_id,
            codigo_resgate=codigo,
            **resgate_data.model_dump(),
            criado_por_id=current_user.id
        )
        
        db.add(resgate)
        
        # Debitar pontos
        pontuacao = PontuacaoCliente(
            empresa_id=current_user.empresa_id,
            cliente_id=cliente_id,
            tipo_movimentacao=TipoMovimentacaoPonto.RESGATE,
            pontos=resgate_data.pontos_utilizados,
            pontos_antes=cliente.pontos_atuais,
            pontos_depois=cliente.pontos_atuais - resgate_data.pontos_utilizados,
            motivo=f"Resgate de recompensa: {resgate_data.tipo_recompensa.value}",
            resgate_id=resgate.id,
            criado_por_id=current_user.id
        )
        
        db.add(pontuacao)
        
        # Atualizar cliente
        cliente.pontos_atuais -= resgate_data.pontos_utilizados
        cliente.pontos_totais_resgatados = (cliente.pontos_totais_resgatados or 0) + resgate_data.pontos_utilizados
        
        db.commit()
        
        return {
            "id": resgate.id,
            "codigo_resgate": codigo,
            "message": "Resgate realizado com sucesso"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================================
# DASHBOARD DE FIDELIDADE
# ================================================================================

@router.get("/dashboard/resumo", response_model=dict)
async def obter_dashboard_fidelidade(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Dashboard resumo do programa de fidelidade"""
    
    # KPIs principais
    total_clientes = db.query(func.count(Cliente.id)).filter(
        Cliente.empresa_id == current_user.empresa_id
    ).scalar() or 0
    
    clientes_ativos = db.query(func.count(Cliente.id)).filter(
        Cliente.empresa_id == current_user.empresa_id,
        Cliente.pontos_atuais > 0
    ).scalar() or 0
    
    pontos_em_circulacao = db.query(func.sum(Cliente.pontos_atuais)).filter(
        Cliente.empresa_id == current_user.empresa_id
    ).scalar() or 0
    
    # Distribuição por níveis
    distribuicao_niveis = db.query(
        NivelFidelidade.nome,
        NivelFidelidade.tipo,
        func.count(Cliente.id).label('quantidade')
    ).outerjoin(Cliente).filter(
        NivelFidelidade.empresa_id == current_user.empresa_id
    ).group_by(NivelFidelidade.id, NivelFidelidade.nome, NivelFidelidade.tipo).all()
    
    # Movimentações últimos 30 dias
    data_30_dias = datetime.now(timezone.utc) - timedelta(days=30)
    movimentacoes_mes = db.query(
        TipoMovimentacaoPonto,
        func.sum(PontuacaoCliente.pontos).label('total_pontos'),
        func.count(PontuacaoCliente.id).label('total_movimentacoes')
    ).filter(
        PontuacaoCliente.empresa_id == current_user.empresa_id,
        PontuacaoCliente.criado_em >= data_30_dias
    ).group_by(PontuacaoCliente.tipo_movimentacao).all()
    
    # Campanhas ativas
    campanhas_ativas = db.query(func.count(CampanhaFidelidade.id)).filter(
        CampanhaFidelidade.empresa_id == current_user.empresa_id,
        CampanhaFidelidade.status == StatusCampanha.ATIVA,
        CampanhaFidelidade.data_inicio <= datetime.now(timezone.utc),
        CampanhaFidelidade.data_fim >= datetime.now(timezone.utc)
    ).scalar() or 0
    
    # Top clientes por pontos
    top_clientes = db.query(Cliente).filter(
        Cliente.empresa_id == current_user.empresa_id
    ).order_by(desc(Cliente.pontos_atuais)).limit(10).all()
    
    return {
        "total_clientes": total_clientes,
        "clientes_ativos": clientes_ativos,
        "pontos_em_circulacao": int(pontos_em_circulacao),
        "campanhas_ativas": campanhas_ativas,
        "distribuicao_niveis": [
            {
                "nome": d.nome,
                "tipo": d.tipo,
                "quantidade": d.quantidade
            } for d in distribuicao_niveis
        ],
        "movimentacoes_mes": [
            {
                "tipo": m[0],
                "total_pontos": int(m.total_pontos),
                "total_movimentacoes": m.total_movimentacoes
            } for m in movimentacoes_mes
        ],
        "top_clientes": [
            {
                "id": c.id,
                "nome": c.nome,
                "pontos": c.pontos_atuais,
                "nivel": c.nivel_fidelidade.nome if c.nivel_fidelidade else "Sem nível"
            } for c in top_clientes
        ]
    }

# ================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================

def _verificar_mudanca_nivel(db: Session, cliente: Cliente, usuario_id: int):
    """Verificar e aplicar mudança de nível do cliente"""
    
    # Buscar nível adequado baseado nos critérios
    nivel_adequado = db.query(NivelFidelidade).filter(
        NivelFidelidade.empresa_id == cliente.empresa_id,
        NivelFidelidade.ativo == True,
        NivelFidelidade.pontos_minimos <= (cliente.pontos_totais_acumulados or 0),
        NivelFidelidade.valor_gasto_minimo <= (cliente.valor_total_gasto or 0),
        NivelFidelidade.compras_minimas <= (cliente.total_compras or 0)
    ).order_by(desc(NivelFidelidade.pontos_minimos)).first()
    
    if nivel_adequado and nivel_adequado.id != cliente.nivel_fidelidade_id:
        # Registrar mudança no histórico
        historico = HistoricoNivelCliente(
            empresa_id=cliente.empresa_id,
            cliente_id=cliente.id,
            nivel_anterior_id=cliente.nivel_fidelidade_id,
            nivel_novo_id=nivel_adequado.id,
            motivo="Mudança automática por critérios atingidos",
            pontos_na_mudanca=cliente.pontos_totais_acumulados or 0,
            valor_gasto_na_mudanca=cliente.valor_total_gasto or 0,
            compras_na_mudanca=cliente.total_compras or 0,
            criado_por_id=usuario_id
        )
        db.add(historico)
        
        # Atualizar cliente
        cliente.nivel_fidelidade_id = nivel_adequado.id

def _recompensar_indicacao(db: Session, indicacao: IndicacaoCliente, usuario_id: int):
    """Aplicar recompensas da indicação"""
    
    # Recompensar indicador
    if indicacao.pontos_indicador > 0:
        cliente_indicador = db.query(Cliente).filter(Cliente.id == indicacao.cliente_indicador_id).first()
        if cliente_indicador:
            pontuacao = PontuacaoCliente(
                empresa_id=indicacao.empresa_id,
                cliente_id=indicacao.cliente_indicador_id,
                tipo_movimentacao=TipoMovimentacaoPonto.INDICACAO,
                pontos=indicacao.pontos_indicador,
                pontos_antes=cliente_indicador.pontos_atuais or 0,
                pontos_depois=(cliente_indicador.pontos_atuais or 0) + indicacao.pontos_indicador,
                motivo="Recompensa por indicação confirmada",
                indicacao_id=indicacao.id,
                criado_por_id=usuario_id
            )
            db.add(pontuacao)
            
            cliente_indicador.pontos_atuais = (cliente_indicador.pontos_atuais or 0) + indicacao.pontos_indicador
            cliente_indicador.pontos_totais_acumulados = (cliente_indicador.pontos_totais_acumulados or 0) + indicacao.pontos_indicador
    
    # Recompensar indicado
    if indicacao.pontos_indicado > 0 and indicacao.cliente_indicado_id:
        cliente_indicado = db.query(Cliente).filter(Cliente.id == indicacao.cliente_indicado_id).first()
        if cliente_indicado:
            pontuacao = PontuacaoCliente(
                empresa_id=indicacao.empresa_id,
                cliente_id=indicacao.cliente_indicado_id,
                tipo_movimentacao=TipoMovimentacaoPonto.BONUS,
                pontos=indicacao.pontos_indicado,
                pontos_antes=cliente_indicado.pontos_atuais or 0,
                pontos_depois=(cliente_indicado.pontos_atuais or 0) + indicacao.pontos_indicado,
                motivo="Bônus de boas-vindas por indicação",
                indicacao_id=indicacao.id,
                criado_por_id=usuario_id
            )
            db.add(pontuacao)
            
            cliente_indicado.pontos_atuais = (cliente_indicado.pontos_atuais or 0) + indicacao.pontos_indicado
            cliente_indicado.pontos_totais_acumulados = (cliente_indicado.pontos_totais_acumulados or 0) + indicacao.pontos_indicado

def _gerar_codigo_campanha() -> str:
    """Gerar código único para campanha"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def _gerar_codigo_indicacao() -> str:
    """Gerar código único para indicação"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def _gerar_codigo_resgate() -> str:
    """Gerar código único para resgate"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
