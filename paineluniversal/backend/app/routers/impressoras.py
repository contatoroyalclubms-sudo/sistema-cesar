"""
Router FastAPI para Sistema de Impressoras
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import (
    Impressora, ImpressoraInteligente, TemplateImpressao,
    FilaImpressao, LogImpressao, EquipamentoPDV, OperadorPDV,
    Usuario, Evento
)
from ..schemas.impressoras import (
    # Impressora
    ImpressoraCreate, ImpressoraUpdate, ImpressoraResponse,
    # Impressora Inteligente
    ImpressoraInteligenteCreate, ImpressoraInteligenteUpdate, ImpressoraInteligenteResponse,
    # Template
    TemplateImpressaoCreate, TemplateImpressaoUpdate, TemplateImpressaoResponse,
    # Fila
    FilaImpressaoCreate, FilaImpressaoResponse,
    # Log
    LogImpressaoResponse,
    # Equipamento
    EquipamentoPDVCreate, EquipamentoPDVUpdate, EquipamentoPDVResponse,
    # Operador
    OperadorPDVCreate, OperadorPDVUpdate, OperadorPDVResponse,
    # Status e Teste
    StatusImpressoraResponse, TesteImpressaoRequest, TesteImpressaoResponse,
    # Enums
    StatusImpressoraEnum, StatusFilaEnum
)
from ..auth_functions import obter_usuario_atual
from ..services.impressao_service import ImpressaoService

router = APIRouter(
    prefix="/api/impressoras",
    tags=["impressoras"]
)

# ====== ROTAS DE IMPRESSORA ======

@router.get("/", response_model=List[ImpressoraResponse])
async def listar_impressoras(
    evento_id: Optional[int] = Query(None),
    ativa: Optional[bool] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar todas as impressoras com filtros opcionais"""
    query = db.query(Impressora)
    
    if evento_id:
        query = query.filter(Impressora.evento_id == evento_id)
    if ativa is not None:
        query = query.filter(Impressora.ativa == ativa)
    if tipo:
        query = query.filter(Impressora.tipo == tipo)
    
    impressoras = query.all()
    return impressoras


@router.get("/{impressora_id}", response_model=ImpressoraResponse)
async def obter_impressora(
    impressora_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Obter detalhes de uma impressora específica"""
    impressora = db.query(Impressora).filter(Impressora.id == impressora_id).first()
    if not impressora:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    return impressora


@router.post("/", response_model=ImpressoraResponse, status_code=status.HTTP_201_CREATED)
async def criar_impressora(
    impressora: ImpressoraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar uma nova impressora"""
    # Verificar se já existe uma impressora com o mesmo IP e porta
    impressora_existente = db.query(Impressora).filter(
        Impressora.ip == impressora.ip,
        Impressora.porta == impressora.porta
    ).first()
    
    if impressora_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe uma impressora configurada com o IP {impressora.ip}:{impressora.porta}"
        )
    
    nova_impressora = Impressora(**impressora.model_dump())
    db.add(nova_impressora)
    db.commit()
    db.refresh(nova_impressora)
    
    return nova_impressora


@router.put("/{impressora_id}", response_model=ImpressoraResponse)
async def atualizar_impressora(
    impressora_id: int,
    impressora: ImpressoraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar uma impressora existente"""
    impressora_db = db.query(Impressora).filter(Impressora.id == impressora_id).first()
    if not impressora_db:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    
    # Verificar se o novo IP:porta já está em uso por outra impressora
    if impressora.ip or impressora.porta:
        novo_ip = impressora.ip or impressora_db.ip
        nova_porta = impressora.porta or impressora_db.porta
        
        conflito = db.query(Impressora).filter(
            Impressora.id != impressora_id,
            Impressora.ip == novo_ip,
            Impressora.porta == nova_porta
        ).first()
        
        if conflito:
            raise HTTPException(
                status_code=400,
                detail=f"IP {novo_ip}:{nova_porta} já está em uso por outra impressora"
            )
    
    for key, value in impressora.model_dump(exclude_unset=True).items():
        setattr(impressora_db, key, value)
    
    impressora_db.atualizada_em = datetime.utcnow()
    db.commit()
    db.refresh(impressora_db)
    
    return impressora_db


@router.delete("/{impressora_id}")
async def excluir_impressora(
    impressora_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Excluir uma impressora"""
    impressora = db.query(Impressora).filter(Impressora.id == impressora_id).first()
    if not impressora:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    
    # Verificar se há jobs na fila
    jobs_pendentes = db.query(FilaImpressao).filter(
        FilaImpressao.impressora_id == impressora_id,
        FilaImpressao.status.in_([StatusFilaEnum.PENDENTE, StatusFilaEnum.PROCESSANDO])
    ).count()
    
    if jobs_pendentes > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir. Existem {jobs_pendentes} jobs pendentes na fila"
        )
    
    db.delete(impressora)
    db.commit()
    
    return {"message": "Impressora excluída com sucesso"}


# ====== ROTAS DE STATUS E TESTE ======

@router.get("/{impressora_id}/status", response_model=StatusImpressoraResponse)
async def verificar_status_impressora(
    impressora_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Verificar status de uma impressora"""
    impressora = db.query(Impressora).filter(Impressora.id == impressora_id).first()
    if not impressora:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    
    # Verificar conectividade
    service = ImpressaoService()
    online = await service.verificar_conectividade(impressora.ip, impressora.porta)
    
    # Atualizar status no banco
    impressora.status = StatusImpressoraEnum.ONLINE if online else StatusImpressoraEnum.OFFLINE
    impressora.ultima_verificacao = datetime.utcnow()
    db.commit()
    
    return StatusImpressoraResponse(
        impressora_id=impressora.id,
        nome=impressora.nome,
        ip=impressora.ip,
        porta=impressora.porta,
        status=impressora.status,
        online=online,
        ultima_verificacao=impressora.ultima_verificacao,
        mensagem="Impressora online e pronta" if online else "Impressora offline ou sem resposta"
    )


@router.post("/{impressora_id}/teste", response_model=TesteImpressaoResponse)
async def testar_impressora(
    impressora_id: int,
    teste: TesteImpressaoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Enviar teste de impressão"""
    impressora = db.query(Impressora).filter(Impressora.id == impressora_id).first()
    if not impressora:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    
    service = ImpressaoService()
    resultado = await service.enviar_teste_impressao(
        impressora=impressora,
        tipo_teste=teste.tipo_teste,
        mensagem_customizada=teste.mensagem_customizada
    )
    
    # Registrar log em background
    background_tasks.add_task(
        registrar_log_impressao,
        db=db,
        impressora_id=impressora_id,
        tipo_documento="teste",
        sucesso=resultado['sucesso'],
        mensagem_erro=resultado.get('erro'),
        usuario_id=current_user.id
    )
    
    return TesteImpressaoResponse(
        sucesso=resultado['sucesso'],
        impressora_id=impressora_id,
        tempo_resposta=resultado['tempo_resposta'],
        mensagem=resultado['mensagem'],
        detalhes=resultado.get('detalhes')
    )


# ====== ROTAS DE IMPRESSORA INTELIGENTE ======

@router.get("/inteligentes/", response_model=List[ImpressoraInteligenteResponse])
async def listar_impressoras_inteligentes(
    evento_id: Optional[int] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar roteamentos inteligentes"""
    query = db.query(ImpressoraInteligente)
    
    if evento_id:
        query = query.filter(ImpressoraInteligente.evento_id == evento_id)
    if ativo is not None:
        query = query.filter(ImpressoraInteligente.ativo == ativo)
    
    return query.all()


@router.post("/inteligentes/", response_model=ImpressoraInteligenteResponse)
async def criar_roteamento_inteligente(
    roteamento: ImpressoraInteligenteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo roteamento inteligente"""
    # Verificar se a impressora existe
    impressora = db.query(Impressora).filter(Impressora.id == roteamento.impressora_id).first()
    if not impressora:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    
    novo_roteamento = ImpressoraInteligente(**roteamento.model_dump())
    db.add(novo_roteamento)
    db.commit()
    db.refresh(novo_roteamento)
    
    return novo_roteamento


@router.put("/inteligentes/{roteamento_id}", response_model=ImpressoraInteligenteResponse)
async def atualizar_roteamento_inteligente(
    roteamento_id: int,
    roteamento: ImpressoraInteligenteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar roteamento inteligente"""
    roteamento_db = db.query(ImpressoraInteligente).filter(
        ImpressoraInteligente.id == roteamento_id
    ).first()
    
    if not roteamento_db:
        raise HTTPException(status_code=404, detail="Roteamento não encontrado")
    
    for key, value in roteamento.model_dump(exclude_unset=True).items():
        setattr(roteamento_db, key, value)
    
    db.commit()
    db.refresh(roteamento_db)
    
    return roteamento_db


@router.delete("/inteligentes/{roteamento_id}")
async def excluir_roteamento_inteligente(
    roteamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Excluir roteamento inteligente"""
    roteamento = db.query(ImpressoraInteligente).filter(
        ImpressoraInteligente.id == roteamento_id
    ).first()
    
    if not roteamento:
        raise HTTPException(status_code=404, detail="Roteamento não encontrado")
    
    db.delete(roteamento)
    db.commit()
    
    return {"message": "Roteamento excluído com sucesso"}


# ====== ROTAS DE TEMPLATE ======

@router.get("/templates/", response_model=List[TemplateImpressaoResponse])
async def listar_templates(
    evento_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar templates de impressão"""
    query = db.query(TemplateImpressao)
    
    if evento_id:
        query = query.filter(TemplateImpressao.evento_id == evento_id)
    if tipo:
        query = query.filter(TemplateImpressao.tipo == tipo)
    if ativo is not None:
        query = query.filter(TemplateImpressao.ativo == ativo)
    
    return query.all()


@router.post("/templates/", response_model=TemplateImpressaoResponse)
async def criar_template(
    template: TemplateImpressaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo template de impressão"""
    novo_template = TemplateImpressao(**template.model_dump())
    db.add(novo_template)
    db.commit()
    db.refresh(novo_template)
    
    return novo_template


@router.put("/templates/{template_id}", response_model=TemplateImpressaoResponse)
async def atualizar_template(
    template_id: int,
    template: TemplateImpressaoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar template existente"""
    template_db = db.query(TemplateImpressao).filter(
        TemplateImpressao.id == template_id
    ).first()
    
    if not template_db:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    for key, value in template.model_dump(exclude_unset=True).items():
        setattr(template_db, key, value)
    
    db.commit()
    db.refresh(template_db)
    
    return template_db


@router.delete("/templates/{template_id}")
async def excluir_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Excluir template"""
    template = db.query(TemplateImpressao).filter(
        TemplateImpressao.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    # Verificar se está em uso
    em_uso = db.query(ImpressoraInteligente).filter(
        ImpressoraInteligente.template_id == template_id
    ).count()
    
    if em_uso > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Template está em uso por {em_uso} roteamentos"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template excluído com sucesso"}


# ====== ROTAS DE FILA DE IMPRESSÃO ======

@router.get("/fila/", response_model=List[FilaImpressaoResponse])
async def listar_fila_impressao(
    impressora_id: Optional[int] = Query(None),
    status: Optional[StatusFilaEnum] = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar jobs na fila de impressão"""
    query = db.query(FilaImpressao)
    
    if impressora_id:
        query = query.filter(FilaImpressao.impressora_id == impressora_id)
    if status:
        query = query.filter(FilaImpressao.status == status)
    
    query = query.order_by(FilaImpressao.prioridade.desc(), FilaImpressao.criado_em)
    
    return query.limit(limit).all()


@router.post("/fila/", response_model=FilaImpressaoResponse)
async def adicionar_fila_impressao(
    job: FilaImpressaoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Adicionar job à fila de impressão"""
    # Verificar se a impressora existe
    impressora = db.query(Impressora).filter(Impressora.id == job.impressora_id).first()
    if not impressora:
        raise HTTPException(status_code=404, detail="Impressora não encontrada")
    
    novo_job = FilaImpressao(
        **job.model_dump(),
        usuario_id=current_user.id
    )
    db.add(novo_job)
    db.commit()
    db.refresh(novo_job)
    
    # Processar job em background
    background_tasks.add_task(processar_job_impressao, novo_job.id, db)
    
    return novo_job


@router.delete("/fila/{job_id}")
async def cancelar_job_impressao(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Cancelar job na fila"""
    job = db.query(FilaImpressao).filter(FilaImpressao.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    if job.status in [StatusFilaEnum.CONCLUIDO, StatusFilaEnum.CANCELADO]:
        raise HTTPException(
            status_code=400,
            detail=f"Job já está {job.status}"
        )
    
    job.status = StatusFilaEnum.CANCELADO
    db.commit()
    
    return {"message": "Job cancelado com sucesso"}


# ====== ROTAS DE LOG ======

@router.get("/logs/", response_model=List[LogImpressaoResponse])
async def listar_logs_impressao(
    impressora_id: Optional[int] = Query(None),
    usuario_id: Optional[int] = Query(None),
    evento_id: Optional[int] = Query(None),
    sucesso: Optional[bool] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar logs de impressão"""
    query = db.query(LogImpressao)
    
    if impressora_id:
        query = query.filter(LogImpressao.impressora_id == impressora_id)
    if usuario_id:
        query = query.filter(LogImpressao.usuario_id == usuario_id)
    if evento_id:
        query = query.filter(LogImpressao.evento_id == evento_id)
    if sucesso is not None:
        query = query.filter(LogImpressao.sucesso == sucesso)
    
    query = query.order_by(LogImpressao.data_hora.desc())
    
    return query.limit(limit).all()


# ====== ROTAS DE EQUIPAMENTO PDV ======

@router.get("/equipamentos/", response_model=List[EquipamentoPDVResponse])
async def listar_equipamentos(
    evento_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    licenciado: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar equipamentos PDV"""
    query = db.query(EquipamentoPDV)
    
    if evento_id:
        query = query.filter(EquipamentoPDV.evento_id == evento_id)
    if tipo:
        query = query.filter(EquipamentoPDV.tipo == tipo)
    if licenciado is not None:
        query = query.filter(EquipamentoPDV.licenciado == licenciado)
    
    return query.all()


@router.post("/equipamentos/", response_model=EquipamentoPDVResponse)
async def criar_equipamento(
    equipamento: EquipamentoPDVCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo equipamento PDV"""
    # Verificar se código já existe
    if db.query(EquipamentoPDV).filter(
        EquipamentoPDV.codigo == equipamento.codigo
    ).first():
        raise HTTPException(
            status_code=400,
            detail=f"Código {equipamento.codigo} já está em uso"
        )
    
    novo_equipamento = EquipamentoPDV(**equipamento.model_dump())
    db.add(novo_equipamento)
    db.commit()
    db.refresh(novo_equipamento)
    
    return novo_equipamento


@router.put("/equipamentos/{equipamento_id}", response_model=EquipamentoPDVResponse)
async def atualizar_equipamento(
    equipamento_id: int,
    equipamento: EquipamentoPDVUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar equipamento PDV"""
    equipamento_db = db.query(EquipamentoPDV).filter(
        EquipamentoPDV.id == equipamento_id
    ).first()
    
    if not equipamento_db:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    
    for key, value in equipamento.model_dump(exclude_unset=True).items():
        setattr(equipamento_db, key, value)
    
    equipamento_db.ultima_sincronizacao = datetime.utcnow()
    db.commit()
    db.refresh(equipamento_db)
    
    return equipamento_db


@router.delete("/equipamentos/{equipamento_id}")
async def excluir_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Excluir equipamento PDV"""
    equipamento = db.query(EquipamentoPDV).filter(
        EquipamentoPDV.id == equipamento_id
    ).first()
    
    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    
    db.delete(equipamento)
    db.commit()
    
    return {"message": "Equipamento excluído com sucesso"}


# ====== ROTAS DE OPERADOR PDV ======

@router.get("/operadores/", response_model=List[OperadorPDVResponse])
async def listar_operadores(
    evento_id: Optional[int] = Query(None),
    ativo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar operadores PDV"""
    query = db.query(OperadorPDV)
    
    if evento_id:
        query = query.filter(OperadorPDV.evento_id == evento_id)
    if ativo is not None:
        query = query.filter(OperadorPDV.ativo == ativo)
    
    return query.all()


@router.post("/operadores/", response_model=OperadorPDVResponse)
async def criar_operador(
    operador: OperadorPDVCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo operador PDV"""
    # Verificar se CPF já existe
    if operador.cpf and db.query(OperadorPDV).filter(
        OperadorPDV.cpf == operador.cpf
    ).first():
        raise HTTPException(
            status_code=400,
            detail="CPF já cadastrado"
        )
    
    novo_operador = OperadorPDV(**operador.model_dump())
    db.add(novo_operador)
    db.commit()
    db.refresh(novo_operador)
    
    return novo_operador


@router.put("/operadores/{operador_id}", response_model=OperadorPDVResponse)
async def atualizar_operador(
    operador_id: int,
    operador: OperadorPDVUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar operador PDV"""
    operador_db = db.query(OperadorPDV).filter(
        OperadorPDV.id == operador_id
    ).first()
    
    if not operador_db:
        raise HTTPException(status_code=404, detail="Operador não encontrado")
    
    # Verificar CPF se estiver sendo atualizado
    if operador.cpf and operador.cpf != operador_db.cpf:
        if db.query(OperadorPDV).filter(
            OperadorPDV.cpf == operador.cpf,
            OperadorPDV.id != operador_id
        ).first():
            raise HTTPException(
                status_code=400,
                detail="CPF já está em uso"
            )
    
    for key, value in operador.model_dump(exclude_unset=True).items():
        setattr(operador_db, key, value)
    
    db.commit()
    db.refresh(operador_db)
    
    return operador_db


@router.delete("/operadores/{operador_id}")
async def excluir_operador(
    operador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Excluir operador PDV"""
    operador = db.query(OperadorPDV).filter(
        OperadorPDV.id == operador_id
    ).first()
    
    if not operador:
        raise HTTPException(status_code=404, detail="Operador não encontrado")
    
    # Verificar se está vinculado a equipamentos
    equipamentos = db.query(EquipamentoPDV).filter(
        EquipamentoPDV.operador_id == operador_id
    ).count()
    
    if equipamentos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Operador está vinculado a {equipamentos} equipamentos"
        )
    
    db.delete(operador)
    db.commit()
    
    return {"message": "Operador excluído com sucesso"}


# ====== FUNÇÕES AUXILIARES ======

async def registrar_log_impressao(
    db: Session,
    impressora_id: int,
    tipo_documento: str,
    sucesso: bool,
    mensagem_erro: Optional[str] = None,
    usuario_id: Optional[int] = None,
    evento_id: Optional[int] = None
):
    """Registrar log de impressão"""
    log = LogImpressao(
        impressora_id=impressora_id,
        tipo_documento=tipo_documento,
        sucesso=sucesso,
        mensagem_erro=mensagem_erro,
        usuario_id=usuario_id,
        evento_id=evento_id
    )
    db.add(log)
    db.commit()


async def processar_job_impressao(job_id: int, db: Session):
    """Processar job de impressão (será implementado com o serviço)"""
    job = db.query(FilaImpressao).filter(FilaImpressao.id == job_id).first()
    if not job:
        return
    
    try:
        job.status = StatusFilaEnum.PROCESSANDO
        db.commit()
        
        # Aqui será feita a integração com o serviço de impressão
        service = ImpressaoService()
        impressora = db.query(Impressora).filter(Impressora.id == job.impressora_id).first()
        
        resultado = await service.processar_job(impressora, job)
        
        if resultado['sucesso']:
            job.status = StatusFilaEnum.CONCLUIDO
            job.processado_em = datetime.utcnow()
            
            # Atualizar estatísticas da impressora
            impressora.total_impressoes += 1
            impressora.ultima_impressao = datetime.utcnow()
        else:
            job.tentativas += 1
            if job.tentativas >= job.max_tentativas:
                job.status = StatusFilaEnum.ERRO
                job.erro_mensagem = resultado.get('erro', 'Erro desconhecido')
            else:
                job.status = StatusFilaEnum.PENDENTE  # Volta para a fila
        
        db.commit()
        
        # Registrar log
        await registrar_log_impressao(
            db=db,
            impressora_id=job.impressora_id,
            tipo_documento=job.tipo_documento,
            sucesso=resultado['sucesso'],
            mensagem_erro=resultado.get('erro'),
            usuario_id=job.usuario_id
        )
        
    except Exception as e:
        job.status = StatusFilaEnum.ERRO
        job.erro_mensagem = str(e)
        db.commit()
