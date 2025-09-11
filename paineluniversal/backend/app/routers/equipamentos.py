"""
Router para gerenciamento de equipamentos e QR readers
Sistema de Gestão de Eventos - Universal v5
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio
import logging

from ..database import get_db
from ..auth import get_current_user
from ..models import Usuario
from ..services.equipamentos_service import EquipamentosService
from ..schemas_equipamentos import (
    LeitorQRCode, LeitorQRCodeCreate, LeitorQRCodeUpdate,
    PontoAcesso, PontoAcessoCreate, PontoAcessoUpdate,
    HistoricoLeituraQR, HistoricoLeituraQRCreate,
    MovimentacaoAcesso, MovimentacaoAcessoCreate,
    ConfiguracaoEquipamento, ConfiguracaoEquipamentoCreate,
    EstatisticasLeitorQR, EstatisticasPontoAcesso,
    StatusSistemaEquipamentos, LoteConfiguracao, ResultadoLote
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/equipamentos",
    tags=["equipamentos"],
    responses={404: {"description": "Não encontrado"}}
)

# ==================== LEITORES QR CODE ====================

@router.post("/leitores-qr", response_model=LeitorQRCode)
def create_leitor_qr(
    leitor_data: LeitorQRCodeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo leitor QR Code"""
    service = EquipamentosService(db)
    return service.create_leitor_qr(leitor_data, current_user.id)

@router.get("/leitores-qr", response_model=List[LeitorQRCode])
def list_leitores_qr(
    evento_id: Optional[int] = None,
    status: Optional[str] = None,
    tipo_leitor: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista leitores QR Code com filtros"""
    service = EquipamentosService(db)
    return service.get_leitores_qr(evento_id, status, tipo_leitor, skip, limit)

@router.get("/leitores-qr/{leitor_id}", response_model=LeitorQRCode)
def get_leitor_qr(
    leitor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Busca um leitor QR Code específico"""
    service = EquipamentosService(db)
    leitor = service.get_leitor_qr(leitor_id)
    
    if not leitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leitor QR Code não encontrado"
        )
    
    return leitor

@router.put("/leitores-qr/{leitor_id}", response_model=LeitorQRCode)
def update_leitor_qr(
    leitor_id: int,
    leitor_data: LeitorQRCodeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um leitor QR Code"""
    service = EquipamentosService(db)
    leitor = service.update_leitor_qr(leitor_id, leitor_data)
    
    if not leitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leitor QR Code não encontrado"
        )
    
    return leitor

@router.delete("/leitores-qr/{leitor_id}")
def delete_leitor_qr(
    leitor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove um leitor QR Code"""
    service = EquipamentosService(db)
    
    if not service.delete_leitor_qr(leitor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leitor QR Code não encontrado"
        )
    
    return {"message": "Leitor QR Code removido com sucesso"}

@router.get("/leitores-qr/{leitor_id}/estatisticas", response_model=EstatisticasLeitorQR)
def get_estatisticas_leitor(
    leitor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna estatísticas de um leitor específico"""
    service = EquipamentosService(db)
    stats = service.get_estatisticas_leitor(leitor_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leitor QR Code não encontrado"
        )
    
    return stats

# ==================== PONTOS DE ACESSO ====================

@router.post("/pontos-acesso", response_model=PontoAcesso)
def create_ponto_acesso(
    ponto_data: PontoAcessoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo ponto de acesso"""
    service = EquipamentosService(db)
    return service.create_ponto_acesso(ponto_data, current_user.id)

@router.get("/pontos-acesso", response_model=List[PontoAcesso])
def list_pontos_acesso(
    evento_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    tipo_ponto: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista pontos de acesso com filtros"""
    service = EquipamentosService(db)
    return service.get_pontos_acesso(evento_id, ativo, tipo_ponto, skip, limit)

@router.get("/pontos-acesso/{ponto_id}", response_model=PontoAcesso)
def get_ponto_acesso(
    ponto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Busca um ponto de acesso específico"""
    service = EquipamentosService(db)
    ponto = service.get_ponto_acesso(ponto_id)
    
    if not ponto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ponto de acesso não encontrado"
        )
    
    return ponto

@router.put("/pontos-acesso/{ponto_id}", response_model=PontoAcesso)
def update_ponto_acesso(
    ponto_id: int,
    ponto_data: PontoAcessoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um ponto de acesso"""
    service = EquipamentosService(db)
    ponto = service.update_ponto_acesso(ponto_id, ponto_data)
    
    if not ponto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ponto de acesso não encontrado"
        )
    
    return ponto

@router.get("/pontos-acesso/{ponto_id}/estatisticas", response_model=EstatisticasPontoAcesso)
def get_estatisticas_ponto_acesso(
    ponto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna estatísticas de um ponto de acesso específico"""
    service = EquipamentosService(db)
    stats = service.get_estatisticas_ponto_acesso(ponto_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ponto de acesso não encontrado"
        )
    
    return stats

# ==================== LEITURAS QR ====================

@router.post("/leituras-qr", response_model=HistoricoLeituraQR)
def registrar_leitura_qr(
    leitura_data: HistoricoLeituraQRCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registra uma nova leitura de QR Code"""
    service = EquipamentosService(db)
    return service.registrar_leitura_qr(leitura_data)

@router.get("/leituras-qr", response_model=List[HistoricoLeituraQR])
def list_historico_leituras(
    leitor_id: Optional[int] = None,
    ponto_acesso_id: Optional[int] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    apenas_validas: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista histórico de leituras QR com filtros"""
    service = EquipamentosService(db)
    
    # Converter strings de data para datetime
    dt_inicio = None
    dt_fim = None
    
    if data_inicio:
        try:
            dt_inicio = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data_inicio inválido. Use ISO 8601."
            )
    
    if data_fim:
        try:
            dt_fim = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data_fim inválido. Use ISO 8601."
            )
    
    return service.get_historico_leituras(
        leitor_id, ponto_acesso_id, dt_inicio, dt_fim, apenas_validas, skip, limit
    )

@router.post("/validar-qr")
def validar_qr_code(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Valida um código QR e retorna resultado da validação"""
    service = EquipamentosService(db)
    
    codigo = data.get("codigo")
    contexto = data.get("contexto", {})
    
    if not codigo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código QR é obrigatório"
        )
    
    return service.validar_qr_code(codigo, contexto)

# ==================== MOVIMENTAÇÕES ====================

@router.post("/movimentacoes", response_model=MovimentacaoAcesso)
def registrar_movimentacao(
    movimentacao_data: MovimentacaoAcessoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registra uma movimentação de entrada/saída"""
    service = EquipamentosService(db)
    return service.registrar_movimentacao(movimentacao_data)

# ==================== CONFIGURAÇÕES ====================

@router.post("/configuracoes", response_model=ConfiguracaoEquipamento)
def create_configuracao(
    config_data: ConfiguracaoEquipamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma nova configuração de equipamento"""
    service = EquipamentosService(db)
    return service.create_configuracao(config_data, current_user.id)

@router.post("/configuracoes/aplicar-lote", response_model=ResultadoLote)
def aplicar_configuracao_lote(
    lote_data: LoteConfiguracao,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Aplica uma configuração a múltiplos equipamentos"""
    service = EquipamentosService(db)
    return service.aplicar_configuracao_lote(
        lote_data.equipamentos_ids,
        lote_data.configuracao_id
    )

# ==================== SISTEMA E RELATÓRIOS ====================

@router.get("/status-sistema", response_model=StatusSistemaEquipamentos)
def get_status_sistema(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna status geral do sistema de equipamentos"""
    service = EquipamentosService(db)
    return service.get_status_sistema()

# ==================== WEBSOCKET PARA MONITORAMENTO ====================

class ConnectionManager:
    """Gerenciador de conexões WebSocket para monitoramento em tempo real"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove conexões mortas
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/ws/monitoramento/{evento_id}")
async def websocket_monitoramento(
    websocket: WebSocket, 
    evento_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket para monitoramento em tempo real dos equipamentos"""
    await manager.connect(websocket)
    service = EquipamentosService(db)
    
    try:
        # Enviar status inicial
        status_inicial = service.get_status_sistema()
        await websocket.send_text(json.dumps({
            "type": "status_sistema",
            "data": status_inicial.dict()
        }))
        
        # Loop de monitoramento
        while True:
            try:
                # Aguardar mensagem do cliente (heartbeat ou comando)
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Processar comando do cliente
                if message == "get_status":
                    status = service.get_status_sistema()
                    await websocket.send_text(json.dumps({
                        "type": "status_sistema",
                        "data": status.dict()
                    }))
                
            except asyncio.TimeoutError:
                # Enviar heartbeat/status periodicamente
                try:
                    status = service.get_status_sistema()
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat",
                        "data": status.dict(),
                        "timestamp": datetime.now().isoformat()
                    }))
                except:
                    break
            
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

@router.websocket("/ws/leitura-qr/{leitor_id}")
async def websocket_leitura_qr(
    websocket: WebSocket,
    leitor_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket para receber leituras QR em tempo real de um leitor específico"""
    await websocket.accept()
    service = EquipamentosService(db)
    
    try:
        while True:
            # Receber dados da leitura QR
            data = await websocket.receive_text()
            
            try:
                leitura_data = json.loads(data)
                
                # Validar o código QR
                codigo = leitura_data.get("codigo")
                contexto = leitura_data.get("contexto", {})
                
                if codigo:
                    # Validar código
                    resultado_validacao = service.validar_qr_code(codigo, contexto)
                    
                    # Criar registro de leitura
                    leitura_create = HistoricoLeituraQRCreate(
                        codigo_lido=codigo,
                        codigo_decodificado=resultado_validacao.get("dados_extraidos", {}).get("codigo_limpo", codigo),
                        leitor_id=leitor_id,
                        valido=resultado_validacao["valido"],
                        tipo_validacao=resultado_validacao["tipo_validacao"],
                        resultado_validacao=resultado_validacao["resultado_validacao"],
                        motivo_rejeicao=resultado_validacao["motivo_rejeicao"],
                        tempo_leitura=leitura_data.get("tempo_leitura"),
                        endereco_ip=leitura_data.get("ip"),
                        sessao_id=leitura_data.get("sessao_id")
                    )
                    
                    # Registrar leitura
                    leitura_registrada = service.registrar_leitura_qr(leitura_create)
                    
                    # Enviar resposta
                    response = {
                        "type": "leitura_processada",
                        "leitura_id": leitura_registrada.id,
                        "validacao": resultado_validacao,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(response))
                    
                    # Se movimentação, registrar também
                    if (resultado_validacao["valido"] and 
                        leitura_data.get("ponto_acesso_id") and
                        leitura_data.get("cpf_participante")):
                        
                        movimentacao_create = MovimentacaoAcessoCreate(
                            tipo_movimento=leitura_data.get("tipo_movimento", "entrada"),
                            cpf_participante=leitura_data["cpf_participante"],
                            nome_participante=leitura_data.get("nome_participante"),
                            ponto_acesso_id=leitura_data["ponto_acesso_id"],
                            leitura_qr_id=leitura_registrada.id,
                            credencial_utilizada=resultado_validacao["tipo_validacao"]
                        )
                        
                        movimentacao = service.registrar_movimentacao(movimentacao_create)
                        
                        # Broadcast da movimentação para outros clients
                        await manager.broadcast(json.dumps({
                            "type": "nova_movimentacao",
                            "data": {
                                "id": movimentacao.id,
                                "tipo": movimentacao.tipo_movimento,
                                "participante": movimentacao.nome_participante,
                                "ponto": movimentacao.ponto_acesso_id,
                                "timestamp": movimentacao.data_hora.isoformat()
                            }
                        }))
                
                else:
                    await websocket.send_text(json.dumps({
                        "type": "erro",
                        "message": "Código QR não fornecido"
                    }))
            
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "erro",
                    "message": "JSON inválido"
                }))
            except Exception as e:
                logger.error(f"Erro no WebSocket leitura QR: {e}")
                await websocket.send_text(json.dumps({
                    "type": "erro",
                    "message": f"Erro interno: {str(e)}"
                }))
    
    except WebSocketDisconnect:
        pass

# ==================== ENDPOINTS DE INTEGRAÇÃO ====================

@router.post("/heartbeat/{leitor_id}")
def heartbeat_leitor(
    leitor_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Recebe heartbeat de um leitor QR Code"""
    service = EquipamentosService(db)
    leitor = service.get_leitor_qr(leitor_id)
    
    if not leitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leitor não encontrado"
        )
    
    # Atualizar dados do heartbeat
    leitor.ultimo_heartbeat = datetime.now()
    leitor.status = data.get("status", "ativo")
    
    # Atualizar dados opcionais
    if "temperatura" in data:
        leitor.temperatura_operacao = data["temperatura"]
    if "nivel_bateria" in data:
        leitor.nivel_bateria = data["nivel_bateria"]
    if "versao_firmware" in data:
        leitor.versao_firmware = data["versao_firmware"]
    
    db.commit()
    
    return {"message": "Heartbeat recebido", "timestamp": leitor.ultimo_heartbeat}

@router.get("/configuracao/{leitor_id}")
def get_configuracao_leitor(
    leitor_id: int,
    db: Session = Depends(get_db)
):
    """Retorna configuração para um leitor específico"""
    service = EquipamentosService(db)
    leitor = service.get_leitor_qr(leitor_id)
    
    if not leitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leitor não encontrado"
        )
    
    # Buscar configuração específica ou padrão
    configuracao = db.query(ConfiguracaoEquipamento).filter(
        ConfiguracaoEquipamento.tipo_equipamento == "leitor_qr",
        ConfiguracaoEquipamento.ativo == True
    ).first()
    
    if configuracao:
        config_data = {}
        if configuracao.parametros_json:
            config_data = json.loads(configuracao.parametros_json)
        
        return {
            "configuracao_id": configuracao.id,
            "nome": configuracao.nome_configuracao,
            "parametros": config_data,
            "versao": configuracao.versao
        }
    
    # Configuração padrão
    return {
        "configuracao_id": None,
        "nome": "Configuração Padrão",
        "parametros": {
            "sensibilidade": 3,
            "timeout_leitura": 5000,
            "modo_operacao": "continuo",
            "filtro_duplicatas": True
        },
        "versao": "1.0"
    }