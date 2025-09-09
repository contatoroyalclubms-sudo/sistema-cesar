"""
Router para Sistema de Fidelidade
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..schemas import Usuario
from ..models import ClienteEvento as Cliente
from ..models_fidelidade import (
    ProgramaFidelidade,
    ClienteFidelidade,
    RecompensaPrograma,
    ResgateFidelidade,
    MovimentoPontos,
    ConquistaPrograma,
    DesafioFidelidade,
    RankingFidelidade,
    TipoMovimentoPontos
)
from ..services.fidelidade_service import FidelidadeService

router = APIRouter(
    prefix="/api/fidelidade",
    tags=["Fidelidade"]
)


# ========================= PROGRAMA =========================

@router.post("/programas")
async def criar_programa(
    nome: str,
    descricao: str,
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo programa de fidelidade"""
    if current_user.tipo_usuario not in ["admin", "empresa"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    service = FidelidadeService(db)
    programa = service.criar_programa(nome, descricao, empresa_id)
    
    return {
        "success": True,
        "programa": {
            "id": programa.id,
            "nome": programa.nome,
            "descricao": programa.descricao,
            "ativo": programa.ativo
        }
    }


@router.get("/programas")
async def listar_programas(
    empresa_id: Optional[int] = None,
    ativo: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista programas de fidelidade"""
    query = db.query(ProgramaFidelidade)
    
    if empresa_id:
        query = query.filter(ProgramaFidelidade.empresa_id == empresa_id)
    
    if ativo is not None:
        query = query.filter(ProgramaFidelidade.ativo == ativo)
    
    programas = query.all()
    
    return {
        "success": True,
        "programas": [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "ativo": p.ativo,
                "total_clientes": len(p.clientes),
                "niveis": [
                    {
                        "id": n.id,
                        "nome": n.nome,
                        "cor": n.cor,
                        "pontos_necessarios": n.pontos_necessarios,
                        "beneficios": n.beneficios
                    }
                    for n in sorted(p.niveis, key=lambda x: x.ordem)
                ]
            }
            for p in programas
        ]
    }


@router.get("/programas/{programa_id}")
async def obter_programa(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém detalhes de um programa"""
    programa = db.query(ProgramaFidelidade).get(programa_id)
    
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    return {
        "success": True,
        "programa": {
            "id": programa.id,
            "nome": programa.nome,
            "descricao": programa.descricao,
            "ativo": programa.ativo,
            "configuracoes": {
                "valor_real_por_ponto": float(programa.valor_real_por_ponto),
                "pontos_por_real": float(programa.pontos_por_real),
                "multiplicador_aniversario": programa.multiplicador_aniversario,
                "multiplicador_primeira_compra": programa.multiplicador_primeira_compra,
                "validade_pontos_dias": programa.validade_pontos_dias,
                "pontos_minimos_resgate": programa.pontos_minimos_resgate,
                "usa_niveis": programa.usa_niveis,
                "usa_conquistas": programa.usa_conquistas,
                "usa_ranking": programa.usa_ranking,
                "usa_desafios": programa.usa_desafios
            },
            "niveis": [
                {
                    "id": n.id,
                    "nome": n.nome,
                    "ordem": n.ordem,
                    "cor": n.cor,
                    "pontos_necessarios": n.pontos_necessarios,
                    "multiplicador_pontos": n.multiplicador_pontos,
                    "desconto_permanente": n.desconto_permanente,
                    "cashback_percentual": n.cashback_percentual,
                    "beneficios": n.beneficios,
                    "total_clientes": len(n.clientes)
                }
                for n in sorted(programa.niveis, key=lambda x: x.ordem)
            ],
            "estatisticas": {
                "total_clientes": len(programa.clientes),
                "total_clientes_ativos": len([c for c in programa.clientes if c.ativo]),
                "total_recompensas": len(programa.recompensas),
                "total_conquistas": len(programa.conquistas),
                "total_desafios": len(programa.desafios)
            }
        }
    }


# ========================= CLIENTE =========================

@router.post("/clientes/cadastrar")
async def cadastrar_cliente_fidelidade(
    programa_id: int,
    cpf: str,
    indicado_por_codigo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cadastra cliente no programa de fidelidade"""
    # Buscar cliente por CPF
    cliente = db.query(Cliente).filter(Cliente.cpf == cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Buscar indicador se fornecido
    indicador_id = None
    if indicado_por_codigo:
        indicador = db.query(ClienteFidelidade).filter(
            ClienteFidelidade.codigo_fidelidade == indicado_por_codigo
        ).first()
        if indicador:
            indicador_id = indicador.id
    
    service = FidelidadeService(db)
    cliente_fidelidade = service.cadastrar_cliente(
        programa_id,
        cliente.id,
        indicador_id
    )
    
    return {
        "success": True,
        "cliente_fidelidade": {
            "id": cliente_fidelidade.id,
            "codigo_fidelidade": cliente_fidelidade.codigo_fidelidade,
            "qr_code": cliente_fidelidade.qr_code,
            "pontos_disponiveis": cliente_fidelidade.pontos_disponiveis,
            "nivel": {
                "nome": cliente_fidelidade.nivel_atual.nome,
                "cor": cliente_fidelidade.nivel_atual.cor
            } if cliente_fidelidade.nivel_atual else None
        }
    }


@router.get("/clientes/meu-perfil")
async def meu_perfil_fidelidade(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém perfil de fidelidade do usuário atual"""
    # Buscar cliente do usuário
    cliente = db.query(Cliente).filter(Cliente.cpf == current_user.cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Buscar participação no programa
    cliente_fidelidade = db.query(ClienteFidelidade).filter(
        ClienteFidelidade.programa_id == programa_id,
        ClienteFidelidade.cliente_id == cliente.id
    ).first()
    
    if not cliente_fidelidade:
        return {
            "success": True,
            "cadastrado": False,
            "programa_id": programa_id
        }
    
    # Calcular próximo nível
    from ..models_fidelidade import NivelPrograma
    proximo_nivel = None
    if cliente_fidelidade.nivel_atual:
        proximo_nivel = db.query(NivelPrograma).filter(
            NivelPrograma.programa_id == programa_id,
            NivelPrograma.ordem == cliente_fidelidade.nivel_atual.ordem + 1
        ).first()
    
    return {
        "success": True,
        "cadastrado": True,
        "perfil": {
            "id": cliente_fidelidade.id,
            "codigo_fidelidade": cliente_fidelidade.codigo_fidelidade,
            "qr_code": cliente_fidelidade.qr_code,
            "ativo": cliente_fidelidade.ativo,
            "data_adesao": cliente_fidelidade.data_adesao.isoformat(),
            "pontos": {
                "disponiveis": cliente_fidelidade.pontos_disponiveis,
                "totais": cliente_fidelidade.pontos_totais,
                "expirados": cliente_fidelidade.pontos_expirados,
                "resgatados": cliente_fidelidade.pontos_resgatados
            },
            "nivel_atual": {
                "id": cliente_fidelidade.nivel_atual.id,
                "nome": cliente_fidelidade.nivel_atual.nome,
                "cor": cliente_fidelidade.nivel_atual.cor,
                "beneficios": cliente_fidelidade.nivel_atual.beneficios,
                "multiplicador_pontos": cliente_fidelidade.nivel_atual.multiplicador_pontos,
                "desconto_permanente": cliente_fidelidade.nivel_atual.desconto_permanente,
                "cashback_percentual": cliente_fidelidade.nivel_atual.cashback_percentual
            } if cliente_fidelidade.nivel_atual else None,
            "proximo_nivel": {
                "nome": proximo_nivel.nome,
                "pontos_necessarios": proximo_nivel.pontos_necessarios,
                "pontos_faltando": cliente_fidelidade.pontos_proximo_nivel
            } if proximo_nivel else None,
            "estatisticas": {
                "total_compras": cliente_fidelidade.total_compras,
                "valor_total_gasto": float(cliente_fidelidade.valor_total_gasto),
                "ticket_medio": float(cliente_fidelidade.ticket_medio) if cliente_fidelidade.ticket_medio else 0,
                "ultima_compra": cliente_fidelidade.ultima_compra.isoformat() if cliente_fidelidade.ultima_compra else None,
                "dias_sem_compra": cliente_fidelidade.dias_sem_compra,
                "total_conquistas": cliente_fidelidade.total_conquistas,
                "posicao_ranking": cliente_fidelidade.posicao_ranking,
                "total_indicacoes": cliente_fidelidade.total_indicacoes
            }
        }
    }


@router.get("/clientes/{cliente_fidelidade_id}/extrato")
async def extrato_pontos(
    cliente_fidelidade_id: int,
    limite: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém extrato de pontos do cliente"""
    cliente_fidelidade = db.query(ClienteFidelidade).get(cliente_fidelidade_id)
    
    if not cliente_fidelidade:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar permissão
    cliente = db.query(Cliente).filter(Cliente.cpf == current_user.cpf).first()
    if cliente and cliente.id != cliente_fidelidade.cliente_id:
        if current_user.tipo_usuario not in ["admin", "empresa"]:
            raise HTTPException(status_code=403, detail="Sem permissão")
    
    movimentos = db.query(MovimentoPontos).filter(
        MovimentoPontos.cliente_fidelidade_id == cliente_fidelidade_id
    ).order_by(MovimentoPontos.criado_em.desc()).limit(limite).offset(offset).all()
    
    return {
        "success": True,
        "saldo_atual": cliente_fidelidade.pontos_disponiveis,
        "movimentos": [
            {
                "id": m.id,
                "tipo": m.tipo.value,
                "pontos": m.pontos,
                "descricao": m.descricao,
                "data": m.criado_em.isoformat(),
                "saldo_apos": m.saldo_posterior,
                "multiplicador": m.multiplicador_aplicado,
                "expira_em": m.data_expiracao.isoformat() if m.data_expiracao else None,
                "expirado": m.expirado
            }
            for m in movimentos
        ]
    }


# ========================= PONTOS =========================

@router.post("/pontos/adicionar")
async def adicionar_pontos_manual(
    cliente_fidelidade_id: int,
    pontos: int,
    descricao: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Adiciona pontos manualmente"""
    if current_user.tipo_usuario not in ["admin", "empresa"]:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    service = FidelidadeService(db)
    movimento = service.adicionar_pontos(
        cliente_fidelidade_id,
        pontos,
        TipoMovimentoPontos.AJUSTE_MANUAL,
        descricao,
        usuario_id=current_user.id
    )
    
    return {
        "success": True,
        "movimento": {
            "id": movimento.id,
            "pontos": movimento.pontos,
            "saldo_posterior": movimento.saldo_posterior
        }
    }


@router.post("/pontos/processar-venda")
async def processar_venda_pontos(
    venda_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Processa pontos de uma venda"""
    from ..models import VendaPDV
    
    venda = db.query(VendaPDV).get(venda_id)
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    if not venda.cliente_id:
        raise HTTPException(status_code=400, detail="Venda sem cliente")
    
    # Buscar programa padrão
    programa = db.query(ProgramaFidelidade).filter(
        ProgramaFidelidade.ativo == True
    ).first()
    
    if not programa:
        raise HTTPException(status_code=404, detail="Nenhum programa ativo")
    
    service = FidelidadeService(db)
    movimento = service.processar_venda_pontos(
        venda_id,
        venda.cliente_id,
        programa.id
    )
    
    return {
        "success": True,
        "movimento": {
            "id": movimento.id,
            "pontos": movimento.pontos,
            "multiplicador": movimento.multiplicador_aplicado
        } if movimento else None
    }


# ========================= RECOMPENSAS =========================

@router.get("/recompensas")
async def listar_recompensas(
    programa_id: int,
    disponivel_para_mim: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista recompensas do programa"""
    if disponivel_para_mim:
        # Buscar cliente fidelidade do usuário
        cliente = db.query(Cliente).filter(Cliente.cpf == current_user.cpf).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        cliente_fidelidade = db.query(ClienteFidelidade).filter(
            ClienteFidelidade.programa_id == programa_id,
            ClienteFidelidade.cliente_id == cliente.id
        ).first()
        
        if not cliente_fidelidade:
            return {"success": True, "recompensas": []}
        
        service = FidelidadeService(db)
        recompensas = service.listar_recompensas_disponiveis(cliente_fidelidade.id)
    else:
        recompensas = db.query(RecompensaPrograma).filter(
            RecompensaPrograma.programa_id == programa_id,
            RecompensaPrograma.ativo == True
        ).all()
    
    return {
        "success": True,
        "recompensas": [
            {
                "id": r.id,
                "nome": r.nome,
                "descricao": r.descricao,
                "tipo": r.tipo.value,
                "custo_pontos": r.custo_pontos,
                "valor_desconto": float(r.valor_desconto) if r.valor_desconto else None,
                "percentual_desconto": r.percentual_desconto,
                "destaque": r.destaque,
                "imagem_url": r.imagem_url,
                "validade_dias": r.validade_dias,
                "quantidade_disponivel": r.quantidade_disponivel,
                "quantidade_resgatada": r.quantidade_resgatada,
                "nivel_minimo": {
                    "nome": r.nivel_minimo.nome,
                    "cor": r.nivel_minimo.cor
                } if r.nivel_minimo else None
            }
            for r in recompensas
        ]
    }


@router.post("/recompensas/resgatar")
async def resgatar_recompensa(
    recompensa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Resgata uma recompensa"""
    # Buscar cliente fidelidade do usuário
    cliente = db.query(Cliente).filter(Cliente.cpf == current_user.cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    recompensa = db.query(RecompensaPrograma).get(recompensa_id)
    if not recompensa:
        raise HTTPException(status_code=404, detail="Recompensa não encontrada")
    
    cliente_fidelidade = db.query(ClienteFidelidade).filter(
        ClienteFidelidade.programa_id == recompensa.programa_id,
        ClienteFidelidade.cliente_id == cliente.id
    ).first()
    
    if not cliente_fidelidade:
        raise HTTPException(status_code=404, detail="Cliente não cadastrado no programa")
    
    try:
        service = FidelidadeService(db)
        resgate = service.resgatar_recompensa(cliente_fidelidade.id, recompensa_id)
        
        return {
            "success": True,
            "resgate": {
                "id": resgate.id,
                "codigo_resgate": resgate.codigo_resgate,
                "qr_code": resgate.qr_code,
                "pontos_utilizados": resgate.pontos_utilizados,
                "expira_em": resgate.data_expiracao.isoformat() if resgate.data_expiracao else None,
                "recompensa": {
                    "nome": recompensa.nome,
                    "tipo": recompensa.tipo.value,
                    "valor_desconto": float(recompensa.valor_desconto) if recompensa.valor_desconto else None,
                    "percentual_desconto": recompensa.percentual_desconto
                }
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/resgates")
async def listar_resgates(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista resgates do usuário"""
    cliente = db.query(Cliente).filter(Cliente.cpf == current_user.cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    query = db.query(ResgateFidelidade).join(ClienteFidelidade).filter(
        ClienteFidelidade.cliente_id == cliente.id
    )
    
    if status:
        query = query.filter(ResgateFidelidade.status == status)
    
    resgates = query.order_by(ResgateFidelidade.data_resgate.desc()).all()
    
    return {
        "success": True,
        "resgates": [
            {
                "id": r.id,
                "codigo_resgate": r.codigo_resgate,
                "qr_code": r.qr_code,
                "status": r.status.value,
                "pontos_utilizados": r.pontos_utilizados,
                "data_resgate": r.data_resgate.isoformat(),
                "expira_em": r.data_expiracao.isoformat() if r.data_expiracao else None,
                "utilizado_em": r.data_utilizacao.isoformat() if r.data_utilizacao else None,
                "recompensa": {
                    "nome": r.recompensa.nome,
                    "tipo": r.recompensa.tipo.value
                }
            }
            for r in resgates
        ]
    }


@router.post("/resgates/utilizar")
async def utilizar_resgate(
    codigo_resgate: str,
    venda_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Utiliza um resgate"""
    try:
        service = FidelidadeService(db)
        resgate = service.utilizar_resgate(codigo_resgate, venda_id)
        
        return {
            "success": True,
            "resgate": {
                "id": resgate.id,
                "status": resgate.status.value,
                "utilizado_em": resgate.data_utilizacao.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========================= CONQUISTAS =========================

@router.get("/conquistas")
async def listar_conquistas(
    programa_id: int,
    minhas: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista conquistas do programa"""
    query = db.query(ConquistaPrograma).filter(
        ConquistaPrograma.programa_id == programa_id,
        ConquistaPrograma.ativo == True
    )
    
    if minhas:
        cliente = db.query(Cliente).filter(Cliente.cpf == current_user.cpf).first()
        if cliente:
            cliente_fidelidade = db.query(ClienteFidelidade).filter(
                ClienteFidelidade.programa_id == programa_id,
                ClienteFidelidade.cliente_id == cliente.id
            ).first()
            
            if cliente_fidelidade:
                query = query.join(
                    cliente_fidelidade.conquistas_desbloqueadas
                )
    
    conquistas = query.order_by(ConquistaPrograma.ordem_exibicao).all()
    
    return {
        "success": True,
        "conquistas": [
            {
                "id": c.id,
                "nome": c.nome,
                "descricao": c.descricao,
                "tipo": c.tipo.value,
                "icone_url": c.icone_url,
                "cor": c.cor,
                "raridade": c.raridade,
                "pontos_recompensa": c.pontos_recompensa,
                "criterios": c.criterios,
                "total_desbloqueios": c.total_desbloqueios,
                "oculta": c.oculta
            }
            for c in conquistas
        ]
    }


# ========================= DESAFIOS =========================

@router.get("/desafios")
async def listar_desafios(
    programa_id: int,
    ativos: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista desafios do programa"""
    query = db.query(DesafioFidelidade).filter(
        DesafioFidelidade.programa_id == programa_id
    )
    
    if ativos:
        agora = datetime.now()
        query = query.filter(
            DesafioFidelidade.ativo == True,
            DesafioFidelidade.data_inicio <= agora,
            DesafioFidelidade.data_fim >= agora
        )
    
    desafios = query.all()
    
    return {
        "success": True,
        "desafios": [
            {
                "id": d.id,
                "nome": d.nome,
                "descricao": d.descricao,
                "tipo": d.tipo,
                "data_inicio": d.data_inicio.isoformat(),
                "data_fim": d.data_fim.isoformat(),
                "criterios": d.criterios,
                "pontos_conclusao": d.pontos_conclusao,
                "bonus_velocidade": d.bonus_velocidade,
                "limite_participantes": d.limite_participantes,
                "total_participantes": d.total_participantes,
                "total_concluidos": d.total_concluidos,
                "imagem_url": d.imagem_url
            }
            for d in desafios
        ]
    }


@router.post("/desafios/{desafio_id}/participar")
async def participar_desafio(
    desafio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Participa de um desafio"""
    cliente = db.query(Cliente).filter(Cliente.cpf == current_user.cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    desafio = db.query(DesafioFidelidade).get(desafio_id)
    if not desafio:
        raise HTTPException(status_code=404, detail="Desafio não encontrado")
    
    cliente_fidelidade = db.query(ClienteFidelidade).filter(
        ClienteFidelidade.programa_id == desafio.programa_id,
        ClienteFidelidade.cliente_id == cliente.id
    ).first()
    
    if not cliente_fidelidade:
        raise HTTPException(status_code=404, detail="Cliente não cadastrado no programa")
    
    try:
        service = FidelidadeService(db)
        participacao = service.participar_desafio(cliente_fidelidade.id, desafio_id)
        
        return {
            "success": True,
            "participacao": {
                "id": participacao.id,
                "data_inicio": participacao.data_inicio.isoformat(),
                "progresso": participacao.progresso_atual,
                "percentual_completo": participacao.percentual_completo
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========================= RANKING =========================

@router.get("/ranking")
async def obter_ranking(
    programa_id: int,
    tipo: str = "mensal",
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém ranking de clientes"""
    service = FidelidadeService(db)
    ranking = service.calcular_ranking(programa_id, tipo, ano, mes)
    
    return {
        "success": True,
        "ranking": {
            "tipo": ranking.tipo_periodo,
            "ano": ranking.ano,
            "mes": ranking.mes,
            "top_pontos": ranking.ranking_pontos[:10] if ranking.ranking_pontos else [],
            "top_compras": ranking.ranking_compras[:10] if ranking.ranking_compras else [],
            "top_valor": ranking.ranking_valor[:10] if ranking.ranking_valor else [],
            "total_participantes": ranking.total_participantes,
            "pontos_distribuidos": ranking.pontos_distribuidos,
            "media_pontos": ranking.media_pontos
        }
    }


# ========================= ADMIN =========================

@router.post("/admin/processar-expiracao")
async def processar_expiracao(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Processa expiração de pontos"""
    if current_user.tipo_usuario != "admin":
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    service = FidelidadeService(db)
    service.processar_expiracao_pontos()
    
    return {"success": True, "message": "Expiração processada"}


@router.post("/admin/atualizar-dias-sem-compra")
async def atualizar_dias_sem_compra(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza dias sem compra dos clientes"""
    if current_user.tipo_usuario != "admin":
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    service = FidelidadeService(db)
    service.calcular_dias_sem_compra()
    
    return {"success": True, "message": "Dias sem compra atualizados"}