"""
Router para Split de Pagamentos
Gerencia divisão automática de pagamentos entre destinatários
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging

from ..database import get_db, Base

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/split", tags=["Split Pagamentos"])

# Modelos Pydantic para requests/responses
class RegraSplitBase(BaseModel):
    destinatario: str = Field(..., description="Nome do destinatário")
    tipo: str = Field(..., description="Tipo: 'percentual' ou 'fixo'")
    valor: float = Field(..., description="Valor ou percentual")

class RegraSplitCreate(RegraSplitBase):
    pass

class RegraSplitResponse(RegraSplitBase):
    id: int
    
    class Config:
        from_attributes = True

class SplitConfiguracaoBase(BaseModel):
    nome: str = Field(..., description="Nome da configuração")
    evento_id: Optional[int] = Field(None, description="ID do evento associado")
    ativo: bool = Field(True, description="Se a configuração está ativa")

class SplitConfiguracaoCreate(SplitConfiguracaoBase):
    regras: List[RegraSplitCreate] = Field(..., description="Lista de regras de split")

class SplitConfiguracaoResponse(SplitConfiguracaoBase):
    id: int
    regras: List[RegraSplitResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SplitCalculoRequest(BaseModel):
    valor_total: float = Field(..., description="Valor total para dividir")
    configuracao_id: int = Field(..., description="ID da configuração de split")

class SplitCalculoResponse(BaseModel):
    configuracao_id: int
    valor_total: float
    splits: Dict[str, float]
    total_distribuido: float
    diferenca: float
    valido: bool

# Modelos SQLAlchemy (definir aqui temporariamente até integrar no models.py principal)
class SplitConfiguracao(Base):
    __tablename__ = "split_configuracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    evento_id = Column(Integer, nullable=True)  # ForeignKey quando eventos estiver pronto
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    regras = relationship("SplitRegra", back_populates="configuracao", cascade="all, delete-orphan")

class SplitRegra(Base):
    __tablename__ = "split_regras"
    
    id = Column(Integer, primary_key=True, index=True)
    configuracao_id = Column(Integer, ForeignKey("split_configuracoes.id"), nullable=False)
    destinatario = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'percentual' ou 'fixo'
    valor = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    configuracao = relationship("SplitConfiguracao", back_populates="regras")

class SplitTransacao(Base):
    __tablename__ = "split_transacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    configuracao_id = Column(Integer, ForeignKey("split_configuracoes.id"), nullable=False)
    valor_total = Column(Float, nullable=False)
    splits_calculados = Column(JSON)
    venda_id = Column(Integer, nullable=True)  # ForeignKey quando vendas estiver pronto
    status = Column(String(20), default="processado")
    data_processamento = Column(DateTime, default=datetime.utcnow)

@router.post("/configuracoes/", response_model=SplitConfiguracaoResponse)
async def criar_configuracao_split(
    config: SplitConfiguracaoCreate,
    db: Session = Depends(get_db)
):
    """
    Criar nova configuração de split de pagamentos
    
    Args:
        config: Dados da configuração incluindo regras
        
    Returns:
        Configuração criada com ID gerado
    """
    try:
        # Validar regras
        total_percentual = sum(r.valor for r in config.regras if r.tipo == 'percentual')
        if total_percentual > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total de percentuais não pode exceder 100%"
            )
        
        # Criar configuração
        db_config = SplitConfiguracao(
            nome=config.nome,
            evento_id=config.evento_id,
            ativo=config.ativo
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        
        # Criar regras
        for regra_data in config.regras:
            if regra_data.tipo not in ['percentual', 'fixo']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tipo deve ser 'percentual' ou 'fixo'"
                )
            
            db_regra = SplitRegra(
                configuracao_id=db_config.id,
                destinatario=regra_data.destinatario,
                tipo=regra_data.tipo,
                valor=regra_data.valor
            )
            db.add(db_regra)
        
        db.commit()
        db.refresh(db_config)
        
        return db_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar configuração split: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/configuracoes/", response_model=List[SplitConfiguracaoResponse])
async def listar_configuracoes_split(
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Listar configurações de split
    
    Args:
        ativo: Filtrar apenas configurações ativas (True/False) ou todas (None)
        
    Returns:
        Lista de configurações
    """
    try:
        query = db.query(SplitConfiguracao)
        
        if ativo is not None:
            query = query.filter(SplitConfiguracao.ativo == ativo)
        
        configuracoes = query.all()
        return configuracoes
        
    except Exception as e:
        logger.error(f"Erro ao listar configurações split: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/configuracoes/{configuracao_id}", response_model=SplitConfiguracaoResponse)
async def obter_configuracao_split(
    configuracao_id: int,
    db: Session = Depends(get_db)
):
    """
    Obter configuração específica de split
    
    Args:
        configuracao_id: ID da configuração
        
    Returns:
        Configuração com suas regras
    """
    try:
        configuracao = db.query(SplitConfiguracao).filter(
            SplitConfiguracao.id == configuracao_id
        ).first()
        
        if not configuracao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada"
            )
        
        return configuracao
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração split: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/calcular/", response_model=SplitCalculoResponse)
async def calcular_split(
    calculo: SplitCalculoRequest,
    db: Session = Depends(get_db)
):
    """
    Calcular split para um valor específico
    
    Args:
        calculo: Valor total e ID da configuração
        
    Returns:
        Resultado do cálculo com valores por destinatário
    """
    try:
        # Buscar configuração
        configuracao = db.query(SplitConfiguracao).filter(
            SplitConfiguracao.id == calculo.configuracao_id,
            SplitConfiguracao.ativo == True
        ).first()
        
        if not configuracao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada ou inativa"
            )
        
        # Calcular splits
        splits = {}
        total_distribuido = 0
        
        for regra in configuracao.regras:
            if regra.tipo == 'percentual':
                valor_split = calculo.valor_total * (regra.valor / 100)
            elif regra.tipo == 'fixo':
                valor_split = regra.valor
            else:
                continue
            
            splits[regra.destinatario] = round(valor_split, 2)
            total_distribuido += valor_split
        
        diferenca = calculo.valor_total - total_distribuido
        valido = abs(diferenca) <= 0.01  # Tolerância de 1 centavo
        
        return SplitCalculoResponse(
            configuracao_id=calculo.configuracao_id,
            valor_total=calculo.valor_total,
            splits=splits,
            total_distribuido=round(total_distribuido, 2),
            diferenca=round(diferenca, 2),
            valido=valido
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao calcular split: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/processar/")
async def processar_split_transacao(
    calculo: SplitCalculoRequest,
    venda_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Processar e salvar uma transação de split
    
    Args:
        calculo: Dados do cálculo
        venda_id: ID da venda associada (opcional)
        
    Returns:
        Dados da transação processada
    """
    try:
        # Calcular split primeiro
        resultado_calculo = await calcular_split(calculo, db)
        
        if not resultado_calculo.valido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Split inválido. Diferença: R$ {resultado_calculo.diferenca}"
            )
        
        # Salvar transação
        transacao = SplitTransacao(
            configuracao_id=calculo.configuracao_id,
            valor_total=calculo.valor_total,
            splits_calculados=resultado_calculo.splits,
            venda_id=venda_id,
            status="processado"
        )
        
        db.add(transacao)
        db.commit()
        db.refresh(transacao)
        
        return {
            "transacao_id": transacao.id,
            "status": "processado",
            "splits": resultado_calculo.splits,
            "valor_total": calculo.valor_total,
            "data_processamento": transacao.data_processamento.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar split: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/configuracoes/{configuracao_id}")
async def desativar_configuracao_split(
    configuracao_id: int,
    db: Session = Depends(get_db)
):
    """
    Desativar configuração de split (soft delete)
    
    Args:
        configuracao_id: ID da configuração
        
    Returns:
        Confirmação da desativação
    """
    try:
        configuracao = db.query(SplitConfiguracao).filter(
            SplitConfiguracao.id == configuracao_id
        ).first()
        
        if not configuracao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada"
            )
        
        configuracao.ativo = False
        configuracao.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "message": "Configuração desativada com sucesso",
            "configuracao_id": configuracao_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar configuração split: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/transacoes/")
async def listar_transacoes_split(
    configuracao_id: Optional[int] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Listar transações de split processadas
    
    Args:
        configuracao_id: Filtrar por configuração
        data_inicio: Data de início (YYYY-MM-DD)
        data_fim: Data de fim (YYYY-MM-DD)
        limit: Limite de resultados
        
    Returns:
        Lista de transações
    """
    try:
        query = db.query(SplitTransacao)
        
        if configuracao_id:
            query = query.filter(SplitTransacao.configuracao_id == configuracao_id)
        
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(SplitTransacao.data_processamento >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.filter(SplitTransacao.data_processamento <= data_fim_dt)
        
        transacoes = query.order_by(
            SplitTransacao.data_processamento.desc()
        ).limit(limit).all()
        
        return {
            "transacoes": [
                {
                    "id": t.id,
                    "configuracao_id": t.configuracao_id,
                    "valor_total": t.valor_total,
                    "splits_calculados": t.splits_calculados,
                    "venda_id": t.venda_id,
                    "status": t.status,
                    "data_processamento": t.data_processamento.isoformat()
                }
                for t in transacoes
            ],
            "total": len(transacoes)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar transações split: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )
