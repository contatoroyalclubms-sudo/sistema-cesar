"""
MEEP Auto Sync Service - Sincronização Automática
Serviço que roda em background para manter dados sincronizados
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from pathlib import Path

from .meep_sync import MeepSyncService, SyncDirection
from ..database import get_db

logger = logging.getLogger(__name__)

class MeepAutoSyncService:
    """Serviço de sincronização automática MEEP"""
    
    def __init__(self):
        self.sync_service = MeepSyncService()
        self.running = False
        self.task = None
        self.interval = int(os.getenv("MEEP_SYNC_INTERVAL", "3600"))  # 1 hora padrão
        self.last_sync = None
        self.sync_stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "last_error": None
        }
        self.load_state()
    
    def load_state(self):
        """Carregar estado anterior da sincronização"""
        state_file = Path("data/sync/meep_sync_state.json")
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)
                    self.last_sync = datetime.fromisoformat(state.get("last_sync")) if state.get("last_sync") else None
                    self.sync_stats = state.get("stats", self.sync_stats)
                    logger.info(f"Estado de sincronização carregado. Última sync: {self.last_sync}")
            except Exception as e:
                logger.error(f"Erro ao carregar estado: {e}")
    
    def save_state(self):
        """Salvar estado atual da sincronização"""
        state_file = Path("data/sync/meep_sync_state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "stats": self.sync_stats,
            "interval": self.interval,
            "running": self.running
        }
        
        try:
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    async def start(self):
        """Iniciar sincronização automática"""
        if self.running:
            logger.warning("Sincronização já está rodando")
            return
        
        self.running = True
        logger.info(f"Iniciando sincronização automática (intervalo: {self.interval}s)")
        
        # Criar task assíncrona
        self.task = asyncio.create_task(self._sync_loop())
    
    async def stop(self):
        """Parar sincronização automática"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Parando sincronização automática...")
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.save_state()
        logger.info("Sincronização automática parada")
    
    async def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.running:
            try:
                # Verificar se é hora de sincronizar
                if self.should_sync():
                    await self.perform_sync()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(60)  # Verificar a cada minuto
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no loop de sincronização: {e}")
                self.sync_stats["last_error"] = str(e)
                await asyncio.sleep(60)
    
    def should_sync(self) -> bool:
        """Verificar se deve sincronizar agora"""
        if not self.last_sync:
            return True
        
        elapsed = datetime.utcnow() - self.last_sync
        return elapsed.total_seconds() >= self.interval
    
    async def perform_sync(self):
        """Executar sincronização"""
        logger.info("Iniciando sincronização automática...")
        start_time = datetime.utcnow()
        
        try:
            # Executar sincronização bidirecional
            result = await self.sync_service.sync_all(
                direction=SyncDirection.BIDIRECTIONAL
            )
            
            # Atualizar estatísticas
            self.last_sync = datetime.utcnow()
            self.sync_stats["total_syncs"] += 1
            
            if result["status"] == "completed":
                self.sync_stats["successful_syncs"] += 1
                
                # Log de resumo
                logger.info(f"Sincronização concluída em {(datetime.utcnow() - start_time).total_seconds():.2f}s")
                logger.info(f"Eventos: {result['events']['synced']} sincronizados, {result['events']['errors']} erros")
                logger.info(f"Participantes: {result['attendees']['synced']} sincronizados")
                logger.info(f"Check-ins: {result['checkins']['synced']} sincronizados")
                logger.info(f"Transações: {result['transactions']['synced']} sincronizadas")
                
                # Notificar dashboard se houver mudanças
                if self.has_changes(result):
                    await self.notify_dashboard(result)
            else:
                self.sync_stats["failed_syncs"] += 1
                logger.error(f"Sincronização falhou: {result.get('errors')}")
            
            # Salvar estado
            self.save_state()
            
        except Exception as e:
            logger.error(f"Erro na sincronização automática: {e}")
            self.sync_stats["failed_syncs"] += 1
            self.sync_stats["last_error"] = str(e)
            self.save_state()
    
    def has_changes(self, result: Dict[str, Any]) -> bool:
        """Verificar se houve mudanças na sincronização"""
        total_synced = (
            result["events"]["synced"] +
            result["tickets"]["synced"] +
            result["attendees"]["synced"] +
            result["checkins"]["synced"] +
            result["transactions"]["synced"]
        )
        return total_synced > 0
    
    async def notify_dashboard(self, result: Dict[str, Any]):
        """Notificar dashboard sobre atualizações"""
        try:
            # Preparar mensagem
            message = {
                "type": "sync_update",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "events_synced": result["events"]["synced"],
                    "attendees_synced": result["attendees"]["synced"],
                    "checkins_synced": result["checkins"]["synced"],
                    "transactions_synced": result["transactions"]["synced"]
                }
            }
            
            # TODO: Enviar via WebSocket para dashboard
            # await websocket_manager.broadcast(json.dumps(message))
            
            logger.info(f"Dashboard notificado sobre {message['data']}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar dashboard: {e}")
    
    async def force_sync(self) -> Dict[str, Any]:
        """Forçar sincronização imediata"""
        logger.info("Forçando sincronização manual...")
        await self.perform_sync()
        return self.get_status()
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status da sincronização automática"""
        return {
            "running": self.running,
            "interval": self.interval,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "next_sync": (
                (self.last_sync + timedelta(seconds=self.interval)).isoformat()
                if self.last_sync else None
            ),
            "stats": self.sync_stats
        }
    
    def set_interval(self, interval: int):
        """Alterar intervalo de sincronização"""
        if interval < 60:
            raise ValueError("Intervalo mínimo é 60 segundos")
        
        self.interval = interval
        logger.info(f"Intervalo de sincronização alterado para {interval}s")
        self.save_state()

# Instância global do serviço
auto_sync_service = MeepAutoSyncService()

async def start_auto_sync():
    """Iniciar sincronização automática"""
    await auto_sync_service.start()

async def stop_auto_sync():
    """Parar sincronização automática"""
    await auto_sync_service.stop()

def get_sync_status() -> Dict[str, Any]:
    """Obter status da sincronização"""
    return auto_sync_service.get_status()