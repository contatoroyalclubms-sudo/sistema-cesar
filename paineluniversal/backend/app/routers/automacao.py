"""
Router para gerenciamento de automações e fluxos de trabalho
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import json
import httpx
from enum import Enum

from .. import models
from ..database import get_db
from ..auth_functions import obter_usuario_atual as get_current_user
from ..schemas_extended import (
    Automacao, AutomacaoCreate, AutomacaoUpdate,
    FluxoTrabalho, FluxoTrabalhoCreate, FluxoTrabalhoUpdate,
    ExecucaoFluxo, ExecucaoFluxoCreate,
    LogAutomacao
)

router = APIRouter(
    prefix="/api/automacao",
    tags=["automacao"]
)

class TipoGatilho(str, Enum):
    TEMPO = "tempo"
    EVENTO = "evento"
    WEBHOOK = "webhook"
    API = "api"
    MANUAL = "manual"
    CONDICAO = "condicao"

class StatusExecucao(str, Enum):
    PENDENTE = "pendente"
    EXECUTANDO = "executando"
    SUCESSO = "sucesso"
    ERRO = "erro"
    CANCELADO = "cancelado"

async def executar_acao(acao: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
    """Executa uma ação específica da automação"""
    tipo_acao = acao.get("tipo")
    parametros = acao.get("parametros", {})
    
    resultado = {
        "tipo": tipo_acao,
        "status": "sucesso",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        if tipo_acao == "email":
            # Simular envio de email
            resultado["dados"] = {
                "destinatario": parametros.get("destinatario"),
                "assunto": parametros.get("assunto"),
                "enviado": True
            }
        
        elif tipo_acao == "webhook":
            # Fazer chamada webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    parametros.get("url"),
                    json=parametros.get("dados", {}),
                    timeout=30.0
                )
                resultado["dados"] = {
                    "status_code": response.status_code,
                    "response": response.text[:500]
                }
        
        elif tipo_acao == "sms":
            # Simular envio de SMS
            resultado["dados"] = {
                "telefone": parametros.get("telefone"),
                "mensagem": parametros.get("mensagem"),
                "enviado": True
            }
        
        elif tipo_acao == "notificacao":
            # Criar notificação no sistema
            resultado["dados"] = {
                "titulo": parametros.get("titulo"),
                "mensagem": parametros.get("mensagem"),
                "tipo": parametros.get("tipo", "info")
            }
        
        elif tipo_acao == "atualizar_dados":
            # Atualizar dados no banco
            resultado["dados"] = {
                "entidade": parametros.get("entidade"),
                "campo": parametros.get("campo"),
                "valor": parametros.get("valor"),
                "atualizado": True
            }
        
        else:
            resultado["status"] = "erro"
            resultado["erro"] = f"Tipo de ação não reconhecido: {tipo_acao}"
    
    except Exception as e:
        resultado["status"] = "erro"
        resultado["erro"] = str(e)
    
    return resultado

async def executar_fluxo_background(
    fluxo_id: int,
    contexto: Dict[str, Any],
    db: Session
):
    """Executa um fluxo de trabalho em background"""
    fluxo = db.query(models.FluxoTrabalho).filter(
        models.FluxoTrabalho.id == fluxo_id
    ).first()
    
    if not fluxo:
        return
    
    # Criar registro de execução
    execucao = models.ExecucaoFluxo(
        fluxo_id=fluxo_id,
        status="executando",
        contexto=json.dumps(contexto)
    )
    db.add(execucao)
    db.commit()
    
    try:
        # Parsear e executar passos
        passos = json.loads(fluxo.passos) if isinstance(fluxo.passos, str) else fluxo.passos
        resultados = []
        
        for passo in passos:
            if passo.get("condicao"):
                # Avaliar condição (simplificado)
                if not avaliar_condicao(passo["condicao"], contexto):
                    continue
            
            resultado = await executar_acao(passo["acao"], contexto)
            resultados.append(resultado)
            
            # Atualizar contexto com resultado
            contexto[f"resultado_{passo.get('id', len(resultados))}"] = resultado
            
            if resultado["status"] == "erro":
                raise Exception(f"Erro no passo: {resultado.get('erro')}")
        
        execucao.status = "sucesso"
        execucao.resultado = json.dumps(resultados)
        
    except Exception as e:
        execucao.status = "erro"
        execucao.erro = str(e)
    
    finally:
        execucao.finalizado_em = datetime.now()
        db.commit()

def avaliar_condicao(condicao: Dict[str, Any], contexto: Dict[str, Any]) -> bool:
    """Avalia uma condição baseada no contexto"""
    # Implementação simplificada
    campo = condicao.get("campo")
    operador = condicao.get("operador")
    valor = condicao.get("valor")
    
    valor_contexto = contexto.get(campo)
    
    if operador == "igual":
        return valor_contexto == valor
    elif operador == "diferente":
        return valor_contexto != valor
    elif operador == "maior":
        return valor_contexto > valor
    elif operador == "menor":
        return valor_contexto < valor
    elif operador == "contem":
        return valor in str(valor_contexto)
    
    return False

@router.get("/", response_model=List[Automacao])
def listar_automacoes(
    skip: int = 0,
    limit: int = 100,
    ativa: Optional[bool] = None,
    tipo_gatilho: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as automações"""
    query = db.query(models.Automacao)
    
    if ativa is not None:
        query = query.filter(models.Automacao.ativa == ativa)
    
    if tipo_gatilho:
        query = query.filter(models.Automacao.tipo_gatilho == tipo_gatilho)
    
    if search:
        query = query.filter(
            or_(
                models.Automacao.nome.ilike(f"%{search}%"),
                models.Automacao.descricao.ilike(f"%{search}%")
            )
        )
    
    automacoes = query.order_by(
        models.Automacao.ativa.desc(),
        models.Automacao.criado_em.desc()
    ).offset(skip).limit(limit).all()
    
    # Adicionar estatísticas
    for automacao in automacoes:
        automacao.total_execucoes = db.query(models.LogAutomacao).filter(
            models.LogAutomacao.automacao_id == automacao.id
        ).count()
        
        automacao.execucoes_sucesso = db.query(models.LogAutomacao).filter(
            models.LogAutomacao.automacao_id == automacao.id,
            models.LogAutomacao.status == "sucesso"
        ).count()
    
    return automacoes

@router.get("/{automacao_id}", response_model=Automacao)
def obter_automacao(
    automacao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém uma automação específica"""
    automacao = db.query(models.Automacao).filter(
        models.Automacao.id == automacao_id
    ).first()
    
    if not automacao:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    
    return automacao

@router.post("/", response_model=Automacao)
def criar_automacao(
    automacao: AutomacaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova automação"""
    # Converter dados para JSON
    configuracao = json.dumps(automacao.configuracao) if automacao.configuracao else None
    acoes = json.dumps(automacao.acoes) if automacao.acoes else None
    condicoes = json.dumps(automacao.condicoes) if automacao.condicoes else None
    
    db_automacao = models.Automacao(
        **automacao.model_dump(exclude={'configuracao', 'acoes', 'condicoes'}),
        configuracao=configuracao,
        acoes=acoes,
        condicoes=condicoes,
        criado_por_id=current_user.id
    )
    
    db.add(db_automacao)
    db.commit()
    db.refresh(db_automacao)
    
    return db_automacao

@router.put("/{automacao_id}", response_model=Automacao)
def atualizar_automacao(
    automacao_id: int,
    automacao_update: AutomacaoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma automação existente"""
    automacao = db.query(models.Automacao).filter(
        models.Automacao.id == automacao_id
    ).first()
    
    if not automacao:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    
    update_data = automacao_update.model_dump(exclude_unset=True)
    
    # Converter dados para JSON se necessário
    if 'configuracao' in update_data and update_data['configuracao']:
        update_data['configuracao'] = json.dumps(update_data['configuracao'])
    
    if 'acoes' in update_data and update_data['acoes']:
        update_data['acoes'] = json.dumps(update_data['acoes'])
    
    if 'condicoes' in update_data and update_data['condicoes']:
        update_data['condicoes'] = json.dumps(update_data['condicoes'])
    
    for key, value in update_data.items():
        setattr(automacao, key, value)
    
    db.commit()
    db.refresh(automacao)
    
    return automacao

@router.delete("/{automacao_id}")
def deletar_automacao(
    automacao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Desativa uma automação"""
    automacao = db.query(models.Automacao).filter(
        models.Automacao.id == automacao_id
    ).first()
    
    if not automacao:
        raise HTTPException(status_code=404, detail="Automação não encontrada")
    
    automacao.ativa = False
    db.commit()
    
    return {"message": "Automação desativada com sucesso"}

@router.post("/{automacao_id}/executar")
async def executar_automacao(
    automacao_id: int,
    background_tasks: BackgroundTasks,
    contexto: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Executa uma automação manualmente"""
    automacao = db.query(models.Automacao).filter(
        models.Automacao.id == automacao_id,
        models.Automacao.ativa == True
    ).first()
    
    if not automacao:
        raise HTTPException(
            status_code=404, 
            detail="Automação não encontrada ou inativa"
        )
    
    # Criar log de execução
    log = models.LogAutomacao(
        automacao_id=automacao_id,
        usuario_id=current_user.id,
        status="iniciado",
        detalhes=json.dumps({
            "tipo_execucao": "manual",
            "contexto": contexto or {}
        })
    )
    db.add(log)
    db.commit()
    
    # Executar ações em background
    if automacao.acoes:
        acoes = json.loads(automacao.acoes) if isinstance(automacao.acoes, str) else automacao.acoes
        background_tasks.add_task(
            executar_fluxo_background,
            automacao_id,
            contexto or {},
            db
        )
    
    return {
        "message": "Automação iniciada com sucesso",
        "log_id": log.id
    }

# ====== FLUXOS DE TRABALHO ======

@router.get("/fluxos/", response_model=List[FluxoTrabalho])
def listar_fluxos(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os fluxos de trabalho"""
    query = db.query(models.FluxoTrabalho)
    
    if ativo is not None:
        query = query.filter(models.FluxoTrabalho.ativo == ativo)
    
    if categoria:
        query = query.filter(models.FluxoTrabalho.categoria == categoria)
    
    fluxos = query.order_by(
        models.FluxoTrabalho.criado_em.desc()
    ).offset(skip).limit(limit).all()
    
    return fluxos

@router.post("/fluxos/", response_model=FluxoTrabalho)
def criar_fluxo(
    fluxo: FluxoTrabalhoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo fluxo de trabalho"""
    passos = json.dumps(fluxo.passos) if fluxo.passos else None
    variaveis = json.dumps(fluxo.variaveis) if fluxo.variaveis else None
    
    db_fluxo = models.FluxoTrabalho(
        **fluxo.model_dump(exclude={'passos', 'variaveis'}),
        passos=passos,
        variaveis=variaveis,
        criado_por_id=current_user.id
    )
    
    db.add(db_fluxo)
    db.commit()
    db.refresh(db_fluxo)
    
    return db_fluxo

@router.get("/logs/")
def listar_logs_automacao(
    skip: int = 0,
    limit: int = 100,
    automacao_id: Optional[int] = None,
    status: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista logs de execução de automações"""
    query = db.query(models.LogAutomacao)
    
    if automacao_id:
        query = query.filter(models.LogAutomacao.automacao_id == automacao_id)
    
    if status:
        query = query.filter(models.LogAutomacao.status == status)
    
    if data_inicio:
        query = query.filter(models.LogAutomacao.data_execucao >= data_inicio)
    
    if data_fim:
        query = query.filter(models.LogAutomacao.data_execucao <= data_fim)
    
    logs = query.order_by(
        models.LogAutomacao.data_execucao.desc()
    ).offset(skip).limit(limit).all()
    
    return logs

@router.get("/estatisticas")
def obter_estatisticas_automacao(
    periodo_dias: int = 30,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obtém estatísticas de automações"""
    from datetime import timedelta
    
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Total de automações
    total_automacoes = db.query(models.Automacao).count()
    automacoes_ativas = db.query(models.Automacao).filter(
        models.Automacao.ativa == True
    ).count()
    
    # Execuções no período
    execucoes = db.query(models.LogAutomacao).filter(
        models.LogAutomacao.data_execucao >= data_inicio
    ).all()
    
    total_execucoes = len(execucoes)
    execucoes_sucesso = sum(1 for e in execucoes if e.status == "sucesso")
    execucoes_erro = sum(1 for e in execucoes if e.status == "erro")
    
    # Taxa de sucesso
    taxa_sucesso = (execucoes_sucesso / total_execucoes * 100) if total_execucoes > 0 else 0
    
    # Automações mais executadas
    from sqlalchemy import desc
    automacoes_populares = db.query(
        models.Automacao.nome,
        func.count(models.LogAutomacao.id).label('total')
    ).join(
        models.LogAutomacao
    ).filter(
        models.LogAutomacao.data_execucao >= data_inicio
    ).group_by(
        models.Automacao.id
    ).order_by(
        desc('total')
    ).limit(5).all()
    
    return {
        "periodo_dias": periodo_dias,
        "total_automacoes": total_automacoes,
        "automacoes_ativas": automacoes_ativas,
        "execucoes": {
            "total": total_execucoes,
            "sucesso": execucoes_sucesso,
            "erro": execucoes_erro,
            "taxa_sucesso": round(taxa_sucesso, 2)
        },
        "automacoes_populares": [
            {"nome": a[0], "execucoes": a[1]} for a in automacoes_populares
        ]
    }