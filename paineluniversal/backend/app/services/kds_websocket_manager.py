"""
WebSocket Manager para KDS (Kitchen Display System)
Gerencia conexões em tempo real e broadcasting de eventos
"""

from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class KDSEventType(Enum):
    """Tipos de eventos do KDS"""
    # Pedidos
    NOVO_PEDIDO = "novo_pedido"
    PEDIDO_ATUALIZADO = "pedido_atualizado"
    PEDIDO_CANCELADO = "pedido_cancelado"
    
    # Items
    ITEM_INICIADO = "item_iniciado"
    ITEM_PRONTO = "item_pronto"
    ITEM_ENTREGUE = "item_entregue"
    
    # Alertas
    ALERTA_ATRASO = "alerta_atraso"
    ALERTA_PRIORITARIO = "alerta_prioritario"
    
    # Sistema
    HEARTBEAT = "heartbeat"
    TERMINAL_CONECTADO = "terminal_conectado"
    TERMINAL_DESCONECTADO = "terminal_desconectado"
    
    # Comandos
    MARCAR_VISUALIZADO = "marcar_visualizado"
    INICIAR_PREPARO = "iniciar_preparo"
    MARCAR_PRONTO = "marcar_pronto"
    MARCAR_ENTREGUE = "marcar_entregue"
    CANCELAR_ITEM = "cancelar_item"


class ConnectionManager:
    """Gerenciador de conexões WebSocket para KDS"""
    
    def __init__(self):
        # Conexões por setor {setor_id: {terminal_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        
        # Mapeamento terminal -> setor para lookup rápido
        self.terminal_to_setor: Dict[str, int] = {}
        
        # Filas de mensagens para reconexão
        self.message_queues: Dict[str, List[Dict]] = {}
        
        # Heartbeat tracking
        self.last_heartbeat: Dict[str, datetime] = {}
        
        # Lock para operações thread-safe
        self.lock = asyncio.Lock()
    
    async def connect(
        self, 
        websocket: WebSocket, 
        setor_id: int, 
        terminal_id: str
    ):
        """Conecta um terminal ao setor"""
        await websocket.accept()
        
        async with self.lock:
            # Inicializar estrutura do setor se não existir
            if setor_id not in self.active_connections:
                self.active_connections[setor_id] = {}
            
            # Adicionar conexão
            self.active_connections[setor_id][terminal_id] = websocket
            self.terminal_to_setor[terminal_id] = setor_id
            self.last_heartbeat[terminal_id] = datetime.now()
            
            # Processar fila de mensagens pendentes
            if terminal_id in self.message_queues:
                for message in self.message_queues[terminal_id]:
                    try:
                        await websocket.send_json(message)
                    except:
                        pass
                self.message_queues[terminal_id] = []
        
        # Notificar outros terminais do setor
        await self.broadcast_to_setor(
            setor_id,
            {
                "type": KDSEventType.TERMINAL_CONECTADO.value,
                "terminal_id": terminal_id,
                "timestamp": datetime.now().isoformat()
            },
            exclude_terminal=terminal_id
        )
        
        logger.info(f"Terminal {terminal_id} conectado ao setor {setor_id}")
    
    async def disconnect(self, terminal_id: str):
        """Desconecta um terminal"""
        async with self.lock:
            if terminal_id in self.terminal_to_setor:
                setor_id = self.terminal_to_setor[terminal_id]
                
                # Remover conexão
                if setor_id in self.active_connections:
                    if terminal_id in self.active_connections[setor_id]:
                        del self.active_connections[setor_id][terminal_id]
                    
                    # Limpar setor se vazio
                    if not self.active_connections[setor_id]:
                        del self.active_connections[setor_id]
                
                # Limpar mapeamentos
                del self.terminal_to_setor[terminal_id]
                if terminal_id in self.last_heartbeat:
                    del self.last_heartbeat[terminal_id]
                
                # Notificar outros terminais
                await self.broadcast_to_setor(
                    setor_id,
                    {
                        "type": KDSEventType.TERMINAL_DESCONECTADO.value,
                        "terminal_id": terminal_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                logger.info(f"Terminal {terminal_id} desconectado do setor {setor_id}")
    
    async def send_to_terminal(
        self, 
        terminal_id: str, 
        message: Dict,
        queue_if_offline: bool = True
    ):
        """Envia mensagem para um terminal específico"""
        if terminal_id in self.terminal_to_setor:
            setor_id = self.terminal_to_setor[terminal_id]
            
            if setor_id in self.active_connections:
                if terminal_id in self.active_connections[setor_id]:
                    websocket = self.active_connections[setor_id][terminal_id]
                    try:
                        await websocket.send_json(message)
                        return True
                    except:
                        # Conexão morta, remover
                        await self.disconnect(terminal_id)
        
        # Se não conseguiu enviar e deve enfileirar
        if queue_if_offline:
            if terminal_id not in self.message_queues:
                self.message_queues[terminal_id] = []
            self.message_queues[terminal_id].append(message)
            
            # Limitar tamanho da fila
            if len(self.message_queues[terminal_id]) > 100:
                self.message_queues[terminal_id] = self.message_queues[terminal_id][-100:]
        
        return False
    
    async def broadcast_to_setor(
        self, 
        setor_id: int, 
        message: Dict,
        exclude_terminal: str = None
    ):
        """Envia mensagem para todos os terminais de um setor"""
        if setor_id in self.active_connections:
            disconnected = []
            
            for terminal_id, websocket in self.active_connections[setor_id].items():
                if terminal_id != exclude_terminal:
                    try:
                        await websocket.send_json(message)
                    except:
                        disconnected.append(terminal_id)
            
            # Limpar conexões mortas
            for terminal_id in disconnected:
                await self.disconnect(terminal_id)
    
    async def broadcast_to_all(self, message: Dict):
        """Envia mensagem para todos os terminais conectados"""
        for setor_id in list(self.active_connections.keys()):
            await self.broadcast_to_setor(setor_id, message)
    
    async def handle_heartbeat(self, terminal_id: str):
        """Processa heartbeat de um terminal"""
        self.last_heartbeat[terminal_id] = datetime.now()
        
        # Responder com heartbeat ACK
        await self.send_to_terminal(
            terminal_id,
            {
                "type": KDSEventType.HEARTBEAT.value,
                "status": "ok",
                "timestamp": datetime.now().isoformat()
            },
            queue_if_offline=False
        )
    
    async def check_connections_health(self):
        """Verifica saúde das conexões (executar periodicamente)"""
        now = datetime.now()
        timeout_seconds = 60  # Timeout de 60 segundos sem heartbeat
        
        disconnected = []
        
        for terminal_id, last_hb in self.last_heartbeat.items():
            if (now - last_hb).total_seconds() > timeout_seconds:
                disconnected.append(terminal_id)
                logger.warning(f"Terminal {terminal_id} timeout - removendo conexão")
        
        for terminal_id in disconnected:
            await self.disconnect(terminal_id)
    
    def get_connected_terminals(self, setor_id: int = None) -> List[str]:
        """Retorna lista de terminais conectados"""
        if setor_id:
            if setor_id in self.active_connections:
                return list(self.active_connections[setor_id].keys())
            return []
        
        # Todos os terminais
        all_terminals = []
        for setor_terminals in self.active_connections.values():
            all_terminals.extend(setor_terminals.keys())
        return all_terminals
    
    def get_setor_status(self, setor_id: int) -> Dict:
        """Retorna status de um setor"""
        return {
            "setor_id": setor_id,
            "online": setor_id in self.active_connections,
            "terminals_conectados": len(self.active_connections.get(setor_id, {})),
            "terminals": self.get_connected_terminals(setor_id)
        }


class KDSEventHandler:
    """Handler para eventos do KDS"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def novo_pedido(self, pedido_data: Dict, setor_id: int):
        """Notifica novo pedido para o setor"""
        message = {
            "type": KDSEventType.NOVO_PEDIDO.value,
            "pedido": pedido_data,
            "timestamp": datetime.now().isoformat(),
            "alert": True,
            "sound": "new_order.mp3"
        }
        
        await self.manager.broadcast_to_setor(setor_id, message)
        logger.info(f"Novo pedido {pedido_data.get('numero_pedido')} enviado para setor {setor_id}")
    
    async def atualizar_pedido(
        self, 
        pedido_id: int, 
        status: str, 
        setor_id: int,
        detalhes: Dict = None
    ):
        """Notifica atualização de pedido"""
        message = {
            "type": KDSEventType.PEDIDO_ATUALIZADO.value,
            "pedido_id": pedido_id,
            "status": status,
            "detalhes": detalhes or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.manager.broadcast_to_setor(setor_id, message)
    
    async def item_pronto(
        self, 
        pedido_id: int, 
        item_id: int, 
        setor_id: int
    ):
        """Notifica que um item está pronto"""
        message = {
            "type": KDSEventType.ITEM_PRONTO.value,
            "pedido_id": pedido_id,
            "item_id": item_id,
            "timestamp": datetime.now().isoformat(),
            "sound": "item_ready.mp3"
        }
        
        await self.manager.broadcast_to_setor(setor_id, message)
    
    async def alerta_atraso(
        self, 
        pedido_id: int, 
        tempo_decorrido: int, 
        setor_id: int
    ):
        """Envia alerta de atraso"""
        message = {
            "type": KDSEventType.ALERTA_ATRASO.value,
            "pedido_id": pedido_id,
            "tempo_decorrido": tempo_decorrido,
            "timestamp": datetime.now().isoformat(),
            "alert": True,
            "sound": "alert.mp3",
            "priority": "high"
        }
        
        await self.manager.broadcast_to_setor(setor_id, message)
        logger.warning(f"Alerta de atraso: Pedido {pedido_id} com {tempo_decorrido} minutos")
    
    async def processar_comando(
        self, 
        terminal_id: str, 
        comando: Dict
    ) -> Dict:
        """Processa comando recebido de um terminal"""
        tipo_comando = comando.get("type")
        
        if tipo_comando == KDSEventType.HEARTBEAT.value:
            await self.manager.handle_heartbeat(terminal_id)
            return {"status": "ok"}
        
        elif tipo_comando == KDSEventType.MARCAR_VISUALIZADO.value:
            # Processar marcação como visualizado
            pedido_id = comando.get("pedido_id")
            # TODO: Atualizar no banco de dados
            
            # Notificar outros terminais
            setor_id = self.manager.terminal_to_setor.get(terminal_id)
            if setor_id:
                await self.manager.broadcast_to_setor(
                    setor_id,
                    {
                        "type": KDSEventType.PEDIDO_ATUALIZADO.value,
                        "pedido_id": pedido_id,
                        "status": "visualizado",
                        "terminal_id": terminal_id,
                        "timestamp": datetime.now().isoformat()
                    },
                    exclude_terminal=terminal_id
                )
            
            return {"status": "ok", "pedido_id": pedido_id}
        
        elif tipo_comando == KDSEventType.INICIAR_PREPARO.value:
            # Processar início de preparo
            pedido_id = comando.get("pedido_id")
            item_id = comando.get("item_id")
            # TODO: Atualizar no banco de dados
            
            return {"status": "ok", "pedido_id": pedido_id, "item_id": item_id}
        
        elif tipo_comando == KDSEventType.MARCAR_PRONTO.value:
            # Processar marcação como pronto
            pedido_id = comando.get("pedido_id")
            item_id = comando.get("item_id")
            # TODO: Atualizar no banco de dados
            
            # Notificar
            setor_id = self.manager.terminal_to_setor.get(terminal_id)
            if setor_id:
                await self.item_pronto(pedido_id, item_id, setor_id)
            
            return {"status": "ok", "pedido_id": pedido_id, "item_id": item_id}
        
        else:
            return {"status": "error", "message": f"Comando desconhecido: {tipo_comando}"}


# Instância global do manager
kds_manager = ConnectionManager()
kds_event_handler = KDSEventHandler(kds_manager)