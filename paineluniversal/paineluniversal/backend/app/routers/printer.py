from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import obter_usuario_atual
from ..models import Usuario, Evento
from ..services.printer_service import PrinterService
from ..schemas_printer import (
    Impressora, ImpressoraCreate, ImpressoraUpdate,
    PrintTemplate, PrintTemplateCreate, PrintTemplateUpdate,
    PrintJobResponse, ImprimirReciboRequest, ImprimirPedidoRequest,
    ImprimirComandaRequest, StatusImpressorasResponse, FilaImpressaoResponse
)

router = APIRouter(prefix="/api/printer", tags=["Impressoras Térmicas"])

def get_printer_service(db: Session = Depends(get_db)) -> PrinterService:
    return PrinterService(db)

def get_evento_id_from_user(current_user: Usuario = Depends(obter_usuario_atual)) -> int:
    # Por simplicidade, vamos usar um evento padrão
    # Em produção, isso viria do contexto do usuário
    return 1  # Ou extrair de current_user.evento_id_atual

# ==================== ENDPOINTS IMPRESSORAS ====================

@router.post("/impressoras", response_model=Impressora)
async def criar_impressora(
    impressora: ImpressoraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar nova impressora térmica"""
    from ..models import Impressora as ImpressoraModel
    
    # Verificar se evento existe
    evento = db.query(Evento).filter(Evento.id == impressora.evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Verificar duplicação de endereço no mesmo evento
    impressora_existente = db.query(ImpressoraModel).filter(
        ImpressoraModel.evento_id == impressora.evento_id,
        ImpressoraModel.endereco == impressora.endereco,
        ImpressoraModel.ativo == True
    ).first()
    
    if impressora_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma impressora ativa com este endereço no evento"
        )
    
    db_impressora = ImpressoraModel(**impressora.dict())
    db.add(db_impressora)
    db.commit()
    db.refresh(db_impressora)
    
    return db_impressora

@router.get("/impressoras", response_model=List[Impressora])
async def listar_impressoras(
    evento_id: int = Depends(get_evento_id_from_user),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de impressora"),
    service: PrinterService = Depends(get_printer_service),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar impressoras do evento"""
    impressoras = service.listar_impressoras_evento(evento_id)
    
    if ativo is not None:
        impressoras = [imp for imp in impressoras if imp.ativo == ativo]
    
    if tipo:
        impressoras = [imp for imp in impressoras if imp.tipo.value == tipo]
    
    return impressoras

@router.get("/impressoras/{impressora_id}", response_model=Impressora)
async def obter_impressora(
    impressora_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Obter detalhes de uma impressora"""
    from ..models import Impressora as ImpressoraModel
    
    impressora = db.query(ImpressoraModel).filter(ImpressoraModel.id == impressora_id).first()
    if not impressora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impressora não encontrada"
        )
    
    return impressora

@router.put("/impressoras/{impressora_id}", response_model=Impressora)
async def atualizar_impressora(
    impressora_id: str,
    impressora_update: ImpressoraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar configurações da impressora"""
    from ..models import Impressora as ImpressoraModel
    
    impressora = db.query(ImpressoraModel).filter(ImpressoraModel.id == impressora_id).first()
    if not impressora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impressora não encontrada"
        )
    
    update_data = impressora_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(impressora, field, value)
    
    impressora.atualizado_em = datetime.now()
    db.commit()
    db.refresh(impressora)
    
    return impressora

@router.delete("/impressoras/{impressora_id}")
async def deletar_impressora(
    impressora_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Deletar impressora (soft delete)"""
    from ..models import Impressora as ImpressoraModel
    
    impressora = db.query(ImpressoraModel).filter(ImpressoraModel.id == impressora_id).first()
    if not impressora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impressora não encontrada"
        )
    
    impressora.ativo = False
    impressora.atualizado_em = datetime.now()
    db.commit()
    
    return {"message": "Impressora desativada com sucesso"}

# ==================== ENDPOINTS IMPRESSÃO ====================

@router.post("/imprimir/recibo", response_model=PrintJobResponse)
async def imprimir_recibo_caixa(
    request: ImprimirReciboRequest,
    evento_id: int = Depends(get_evento_id_from_user),
    service: PrinterService = Depends(get_printer_service),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Imprimir recibo de caixa"""
    
    job = await service.criar_job_recibo_caixa(
        request=request,
        cpf_operador=current_user.cpf,
        usuario_id=current_user.id,
        evento_id=evento_id,
        ip_cliente=None  # TODO: extrair do request
    )
    
    return job

@router.post("/imprimir/pedido", response_model=List[PrintJobResponse])
async def imprimir_pedido_cozinha(
    request: ImprimirPedidoRequest,
    evento_id: int = Depends(get_evento_id_from_user),
    service: PrinterService = Depends(get_printer_service),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Imprimir pedido para cozinha/bar (roteamento automático)"""
    
    jobs = await service.criar_job_pedido_cozinha(
        request=request,
        cpf_operador=current_user.cpf,
        usuario_id=current_user.id,
        evento_id=evento_id,
        ip_cliente=None
    )
    
    return jobs

@router.post("/imprimir/comanda", response_model=PrintJobResponse)
async def imprimir_comanda(
    request: ImprimirComandaRequest,
    evento_id: int = Depends(get_evento_id_from_user),
    service: PrinterService = Depends(get_printer_service),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Imprimir operações de comanda (recarga, fechamento)"""
    # TODO: Implementar lógica para impressão de comandas
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade em desenvolvimento"
    )

# ==================== ENDPOINTS STATUS E MONITORAMENTO ====================

@router.get("/status", response_model=StatusImpressorasResponse)
async def obter_status_impressoras(
    evento_id: int = Depends(get_evento_id_from_user),
    service: PrinterService = Depends(get_printer_service),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Obter status geral das impressoras"""
    
    status = service.obter_status_fila(evento_id)
    return StatusImpressorasResponse(**status)

@router.get("/fila", response_model=List[FilaImpressaoResponse])
async def obter_fila_impressao(
    evento_id: int = Depends(get_evento_id_from_user),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Obter status da fila de impressão por impressora"""
    # TODO: Implementar listagem detalhada da fila
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento"
    )

@router.post("/impressoras/{impressora_id}/heartbeat")
async def receber_heartbeat(
    impressora_id: str,
    status_data: dict,
    db: Session = Depends(get_db)
):
    """Receber heartbeat de impressora (para bridges locais)"""
    from ..models import Impressora as ImpressoraModel, StatusImpressora
    
    impressora = db.query(ImpressoraModel).filter(ImpressoraModel.id == impressora_id).first()
    if not impressora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impressora não encontrada"
        )
    
    # Atualizar status baseado no heartbeat
    impressora.ultimo_heartbeat = datetime.now()
    impressora.status = StatusImpressora.ONLINE if status_data.get("online") else StatusImpressora.OFFLINE
    
    if "ip_bridge" in status_data:
        impressora.ip_bridge = status_data["ip_bridge"]
    
    if "versao_driver" in status_data:
        impressora.versao_driver = status_data["versao_driver"]
    
    db.commit()
    
    return {"message": "Heartbeat recebido com sucesso"}

# ==================== ENDPOINTS TEMPLATES ====================

@router.get("/templates", response_model=List[PrintTemplate])
async def listar_templates(
    evento_id: int = Depends(get_evento_id_from_user),
    tipo_job: Optional[str] = Query(None, description="Filtrar por tipo de job"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar templates de impressão"""
    from ..models import PrintTemplate as PrintTemplateModel
    
    query = db.query(PrintTemplateModel).filter(
        PrintTemplateModel.evento_id == evento_id,
        PrintTemplateModel.ativo == True
    )
    
    if tipo_job:
        query = query.filter(PrintTemplateModel.tipo_job == tipo_job)
    
    return query.all()

@router.post("/templates", response_model=PrintTemplate)
async def criar_template(
    template: PrintTemplateCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo template de impressão"""
    from ..models import PrintTemplate as PrintTemplateModel
    
    db_template = PrintTemplateModel(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.post("/impressoras/{impressora_id}/teste")
async def testar_impressora(
    impressora_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Enviar teste de impressão para uma impressora"""
    from ..models import Impressora as ImpressoraModel, PrintJob, TipoPrintJob
    import json
    
    impressora = db.query(ImpressoraModel).filter(ImpressoraModel.id == impressora_id).first()
    if not impressora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impressora não encontrada"
        )
    
    # Criar job de teste
    payload_teste = {
        "teste": {
            "titulo": "TESTE DE IMPRESSÃO",
            "data": datetime.now().isoformat(),
            "impressora": impressora.nome,
            "operador": current_user.nome
        },
        "configuracoes": {
            "corte_automatico": True,
            "densidade": impressora.densidade
        }
    }
    
    job_teste = PrintJob(
        impressora_id=impressora.id,
        tipo=TipoPrintJob.RELATORIO,
        prioridade=3,  # Prioridade urgente para testes
        payload=json.dumps(payload_teste),
        evento_id=impressora.evento_id,
        cpf_operador=current_user.cpf,
        usuario_id=current_user.id
    )
    
    db.add(job_teste)
    db.commit()
    db.refresh(job_teste)
    
    return {
        "sucesso": True,
        "mensagem": f"Teste enviado para {impressora.nome}",
        "job_id": job_teste.id
    }
