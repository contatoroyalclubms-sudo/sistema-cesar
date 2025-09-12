"""
MEEP Sync Service - Sincronização Bidirecional
Kit Legal - Sem código proprietário
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib
from enum import Enum

from .meep_client import MEEPClient
from .meep_mapper import (
    map_event, map_ticket, map_attendee, map_checkin,
    map_transaction, map_analytics, reverse_map_event,
    batch_map, validate_cpf
)

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Status de sincronização"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class SyncDirection(Enum):
    """Direção da sincronização"""
    MEEP_TO_LOCAL = "meep_to_local"
    LOCAL_TO_MEEP = "local_to_meep"
    BIDIRECTIONAL = "bidirectional"

class MeepSyncService:
    """Serviço de sincronização com MEEP"""
    
    def __init__(self, db_session=None):
        self.client = MEEPClient()
        self.db = db_session
        self.sync_log = []
        self.conflicts = []
        self.cache = {}  # Cache local para evitar requisições repetidas
        
    async def sync_all(self, direction: SyncDirection = SyncDirection.BIDIRECTIONAL) -> Dict[str, Any]:
        """Sincronização completa"""
        logger.info(f"Iniciando sincronização completa: {direction.value}")
        
        results = {
            "status": SyncStatus.IN_PROGRESS.value,
            "started_at": datetime.utcnow().isoformat(),
            "direction": direction.value,
            "events": {"synced": 0, "errors": 0},
            "tickets": {"synced": 0, "errors": 0},
            "attendees": {"synced": 0, "errors": 0},
            "checkins": {"synced": 0, "errors": 0},
            "transactions": {"synced": 0, "errors": 0},
            "analytics": {"synced": 0, "errors": 0},
            "conflicts": [],
            "errors": []
        }
        
        try:
            # Login se necessário
            if not self.client.login():
                raise Exception("Falha no login MEEP")
            
            # Sincronizar cada entidade
            if direction in [SyncDirection.MEEP_TO_LOCAL, SyncDirection.BIDIRECTIONAL]:
                await self._sync_from_meep(results)
            
            if direction in [SyncDirection.LOCAL_TO_MEEP, SyncDirection.BIDIRECTIONAL]:
                await self._sync_to_meep(results)
            
            # Resolver conflitos se houver
            if self.conflicts:
                results["conflicts"] = await self._resolve_conflicts()
            
            results["status"] = SyncStatus.COMPLETED.value
            results["completed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            results["status"] = SyncStatus.FAILED.value
            results["errors"].append(str(e))
        
        finally:
            # Salvar log de sincronização
            await self._save_sync_log(results)
        
        return results
    
    async def sync_events(self, event_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Sincronizar eventos específicos"""
        logger.info(f"Sincronizando eventos: {event_ids}")
        
        synced = []
        errors = []
        
        try:
            # Buscar eventos do MEEP
            response = self.client.get("/api/events")
            if response.status_code == 200:
                meep_events = response.json()
                
                for meep_event in meep_events:
                    # Filtrar por IDs se especificado
                    if event_ids and meep_event.get("id") not in event_ids:
                        continue
                    
                    try:
                        # Mapear e salvar
                        local_event = map_event(meep_event)
                        await self._save_event(local_event)
                        synced.append(local_event["id"])
                        
                    except Exception as e:
                        logger.error(f"Erro ao sincronizar evento {meep_event.get('id')}: {e}")
                        errors.append({"event_id": meep_event.get("id"), "error": str(e)})
        
        except Exception as e:
            logger.error(f"Erro ao buscar eventos: {e}")
            errors.append({"error": str(e)})
        
        return {
            "synced": synced,
            "errors": errors,
            "total": len(synced),
            "failed": len(errors)
        }
    
    async def sync_tickets(self, event_id: int) -> Dict[str, Any]:
        """Sincronizar ingressos de um evento"""
        logger.info(f"Sincronizando ingressos do evento {event_id}")
        
        synced = []
        errors = []
        
        try:
            response = self.client.get(f"/api/events/{event_id}/tickets")
            if response.status_code == 200:
                meep_tickets = response.json()
                
                for meep_ticket in meep_tickets:
                    try:
                        local_ticket = map_ticket(meep_ticket)
                        local_ticket["evento_id"] = event_id
                        await self._save_ticket(local_ticket)
                        synced.append(local_ticket["id"])
                        
                    except Exception as e:
                        errors.append({"ticket_id": meep_ticket.get("id"), "error": str(e)})
        
        except Exception as e:
            errors.append({"error": str(e)})
        
        return {
            "synced": synced,
            "errors": errors,
            "total": len(synced),
            "failed": len(errors)
        }
    
    async def sync_attendees(self, event_id: int) -> Dict[str, Any]:
        """Sincronizar participantes de um evento"""
        logger.info(f"Sincronizando participantes do evento {event_id}")
        
        synced = []
        errors = []
        invalid_cpfs = []
        
        try:
            # Buscar participantes paginados
            all_attendees = self.client.paginate(f"/api/events/{event_id}/attendees")
            
            for meep_attendee in all_attendees:
                try:
                    local_attendee = map_attendee(meep_attendee)
                    
                    # Validar CPF
                    if not validate_cpf(local_attendee["cpf"]):
                        invalid_cpfs.append({
                            "name": local_attendee["nome"],
                            "email": local_attendee["email"],
                            "invalid_cpf": local_attendee["cpf"]
                        })
                        continue
                    
                    await self._save_attendee(local_attendee)
                    synced.append(local_attendee["cpf"])
                    
                except Exception as e:
                    errors.append({"attendee_id": meep_attendee.get("id"), "error": str(e)})
        
        except Exception as e:
            errors.append({"error": str(e)})
        
        return {
            "synced": synced,
            "errors": errors,
            "invalid_cpfs": invalid_cpfs,
            "total": len(synced),
            "failed": len(errors),
            "invalid": len(invalid_cpfs)
        }
    
    async def sync_checkins(self, event_id: int, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Sincronizar check-ins de um evento"""
        logger.info(f"Sincronizando check-ins do evento {event_id}")
        
        synced = []
        errors = []
        
        try:
            params = {"event_id": event_id}
            if since:
                params["since"] = since.isoformat()
            
            response = self.client.get("/api/checkins", params=params)
            if response.status_code == 200:
                meep_checkins = response.json()
                
                for meep_checkin in meep_checkins:
                    try:
                        local_checkin = map_checkin(meep_checkin)
                        local_checkin["evento_id"] = event_id
                        await self._save_checkin(local_checkin)
                        synced.append(local_checkin["id"])
                        
                    except Exception as e:
                        errors.append({"checkin_id": meep_checkin.get("id"), "error": str(e)})
        
        except Exception as e:
            errors.append({"error": str(e)})
        
        return {
            "synced": synced,
            "errors": errors,
            "total": len(synced),
            "failed": len(errors)
        }
    
    async def sync_transactions(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Sincronizar transações em um período"""
        logger.info(f"Sincronizando transações de {start_date} até {end_date}")
        
        synced = []
        errors = []
        
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            all_transactions = self.client.paginate("/api/transactions", params=params)
            
            for meep_transaction in all_transactions:
                try:
                    local_transaction = map_transaction(meep_transaction)
                    await self._save_transaction(local_transaction)
                    synced.append(local_transaction["id"])
                    
                except Exception as e:
                    errors.append({"transaction_id": meep_transaction.get("id"), "error": str(e)})
        
        except Exception as e:
            errors.append({"error": str(e)})
        
        return {
            "synced": synced,
            "errors": errors,
            "total": len(synced),
            "failed": len(errors)
        }
    
    async def sync_analytics(self, event_id: int) -> Dict[str, Any]:
        """Sincronizar analytics de um evento"""
        logger.info(f"Sincronizando analytics do evento {event_id}")
        
        try:
            response = self.client.get(f"/api/events/{event_id}/analytics")
            if response.status_code == 200:
                meep_analytics = response.json()
                local_analytics = map_analytics(meep_analytics)
                local_analytics["evento_id"] = event_id
                
                await self._save_analytics(local_analytics)
                
                return {
                    "status": "success",
                    "data": local_analytics
                }
        
        except Exception as e:
            logger.error(f"Erro ao sincronizar analytics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def push_event(self, local_event: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar evento local para MEEP"""
        logger.info(f"Enviando evento {local_event.get('id')} para MEEP")
        
        try:
            # Mapear para formato MEEP
            meep_event = reverse_map_event(local_event)
            
            # Verificar se já existe
            if local_event.get("meep_event_id"):
                # Atualizar
                response = self.client.put(
                    f"/api/events/{local_event['meep_event_id']}",
                    json=meep_event
                )
            else:
                # Criar novo
                response = self.client.post("/api/events", json=meep_event)
            
            if response.status_code in [200, 201]:
                result = response.json()
                # Salvar ID do MEEP
                await self._update_meep_id("evento", local_event["id"], result["id"])
                return {"status": "success", "meep_id": result["id"]}
            else:
                return {"status": "error", "error": response.text}
        
        except Exception as e:
            logger.error(f"Erro ao enviar evento: {e}")
            return {"status": "error", "error": str(e)}
    
    async def real_time_sync(self, event_id: int, interval: int = 60):
        """Sincronização em tempo real"""
        logger.info(f"Iniciando sincronização em tempo real para evento {event_id}")
        
        while True:
            try:
                # Sincronizar check-ins dos últimos minutos
                since = datetime.utcnow() - timedelta(seconds=interval)
                await self.sync_checkins(event_id, since)
                
                # Sincronizar analytics
                await self.sync_analytics(event_id)
                
                # Aguardar próximo ciclo
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Erro na sincronização em tempo real: {e}")
                await asyncio.sleep(interval)
    
    # Métodos privados de persistência
    
    async def _sync_from_meep(self, results: Dict[str, Any]):
        """Sincronizar dados do MEEP para local"""
        # Eventos
        events_result = await self.sync_events()
        results["events"]["synced"] = events_result["total"]
        results["events"]["errors"] = events_result["failed"]
        
        # Para cada evento sincronizado
        for event_id in events_result["synced"]:
            # Ingressos
            tickets_result = await self.sync_tickets(event_id)
            results["tickets"]["synced"] += tickets_result["total"]
            results["tickets"]["errors"] += tickets_result["failed"]
            
            # Participantes
            attendees_result = await self.sync_attendees(event_id)
            results["attendees"]["synced"] += attendees_result["total"]
            results["attendees"]["errors"] += attendees_result["failed"]
            
            # Check-ins
            checkins_result = await self.sync_checkins(event_id)
            results["checkins"]["synced"] += checkins_result["total"]
            results["checkins"]["errors"] += checkins_result["failed"]
            
            # Analytics
            analytics_result = await self.sync_analytics(event_id)
            if analytics_result["status"] == "success":
                results["analytics"]["synced"] += 1
            else:
                results["analytics"]["errors"] += 1
    
    async def _sync_to_meep(self, results: Dict[str, Any]):
        """Sincronizar dados locais para MEEP"""
        if not self.db:
            logger.warning("Database session não configurado, pulando sync to MEEP")
            return
        
        # Buscar eventos locais não sincronizados
        # TODO: Implementar query no banco de dados
        pass
    
    async def _resolve_conflicts(self) -> List[Dict[str, Any]]:
        """Resolver conflitos de sincronização"""
        resolved = []
        
        for conflict in self.conflicts:
            # Estratégia: último modificado ganha
            if conflict["local_updated"] > conflict["meep_updated"]:
                # Manter versão local
                resolved.append({
                    "entity": conflict["entity"],
                    "id": conflict["id"],
                    "resolution": "kept_local"
                })
            else:
                # Usar versão MEEP
                resolved.append({
                    "entity": conflict["entity"],
                    "id": conflict["id"],
                    "resolution": "used_meep"
                })
        
        return resolved
    
    async def _save_event(self, event: Dict[str, Any]):
        """Salvar evento no banco local"""
        # TODO: Implementar persistência no banco
        logger.info(f"Salvando evento: {event.get('id')}")
        pass
    
    async def _save_ticket(self, ticket: Dict[str, Any]):
        """Salvar ingresso no banco local"""
        # TODO: Implementar persistência no banco
        logger.info(f"Salvando ingresso: {ticket.get('id')}")
        pass
    
    async def _save_attendee(self, attendee: Dict[str, Any]):
        """Salvar participante no banco local"""
        # TODO: Implementar persistência no banco
        logger.info(f"Salvando participante: {attendee.get('cpf')}")
        pass
    
    async def _save_checkin(self, checkin: Dict[str, Any]):
        """Salvar check-in no banco local"""
        # TODO: Implementar persistência no banco
        logger.info(f"Salvando check-in: {checkin.get('id')}")
        pass
    
    async def _save_transaction(self, transaction: Dict[str, Any]):
        """Salvar transação no banco local"""
        # TODO: Implementar persistência no banco
        logger.info(f"Salvando transação: {transaction.get('id')}")
        pass
    
    async def _save_analytics(self, analytics: Dict[str, Any]):
        """Salvar analytics no banco local"""
        # TODO: Implementar persistência no banco
        logger.info(f"Salvando analytics para evento: {analytics.get('evento_id')}")
        pass
    
    async def _update_meep_id(self, entity: str, local_id: Any, meep_id: str):
        """Atualizar ID do MEEP na entidade local"""
        # TODO: Implementar update no banco
        logger.info(f"Atualizando {entity} {local_id} com MEEP ID: {meep_id}")
        pass
    
    async def _save_sync_log(self, results: Dict[str, Any]):
        """Salvar log de sincronização"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
        self.sync_log.append(log_entry)
        
        # Salvar em arquivo para auditoria
        try:
            with open("meep_sync_log.json", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Erro ao salvar log: {e}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Retornar status da última sincronização"""
        if self.sync_log:
            return self.sync_log[-1]
        return {"status": "no_sync_performed"}
    
    def calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calcular hash para detectar mudanças"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    async def detect_changes(self, entity: str, local_data: Dict[str, Any], meep_data: Dict[str, Any]) -> bool:
        """Detectar se houve mudanças entre versões"""
        local_hash = self.calculate_hash(local_data)
        meep_hash = self.calculate_hash(meep_data)
        return local_hash != meep_hash
    
    def close(self):
        """Fechar conexões"""
        self.client.close()