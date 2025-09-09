"""
Service para gerenciamento de pedidos no KDS
Lógica de negócio e processamento de pedidos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import asyncio
import logging

from ..models_kds import (
    PedidoKDS, ItemPedidoKDS, SetorPreparo, ProdutoSetor,
    TerminalKDS, HistoricoPedidoKDS, ConfiguracaoKDS, MetricasKDS,
    StatusPedido, StatusItemPedido, TipoPedido, PrioridadePedido
)
from ..models import VendaPDV, ItemVendaPDV, Produto, Usuario
from .kds_websocket_manager import kds_event_handler

logger = logging.getLogger(__name__)


class KDSService:
    """Service principal para gerenciar o KDS"""
    
    def __init__(self, db: Session):
        self.db = db
        self.event_handler = kds_event_handler
    
    # ==================== CRIAÇÃO DE PEDIDOS ====================
    
    async def criar_pedido_from_venda(
        self, 
        venda_id: int,
        tipo: TipoPedido = TipoPedido.BALCAO,
        observacoes: str = None
    ) -> PedidoKDS:
        """Cria um pedido no KDS a partir de uma venda do PDV"""
        
        # Buscar venda
        venda = self.db.query(VendaPDV).filter(VendaPDV.id == venda_id).first()
        if not venda:
            raise ValueError(f"Venda {venda_id} não encontrada")
        
        # Gerar número do pedido
        numero_pedido = self._gerar_numero_pedido()
        
        # Criar pedido KDS
        pedido = PedidoKDS(
            numero_pedido=numero_pedido,
            venda_id=venda_id,
            tipo=tipo,
            origem="PDV",
            cliente_nome=venda.cliente.nome if venda.cliente else f"Cliente #{venda_id}",
            observacoes=observacoes,
            status=StatusPedido.RECEBIDO,
            prioridade=PrioridadePedido.NORMAL,
            operador_pedido_id=venda.usuario_id
        )
        
        # Adicionar itens
        tempo_total = 0
        setores_envolvidos = set()
        
        for item_venda in venda.itens:
            # Buscar setor de preparo do produto
            produto_setor = self.db.query(ProdutoSetor).filter(
                ProdutoSetor.produto_id == item_venda.produto_id,
                ProdutoSetor.setor_principal == True
            ).first()
            
            if not produto_setor:
                # Se não tem setor configurado, usar setor padrão (id=1)
                setor_id = 1
                tempo_preparo = 15  # Tempo padrão
            else:
                setor_id = produto_setor.setor_id
                tempo_preparo = produto_setor.tempo_preparo
            
            setores_envolvidos.add(setor_id)
            
            # Criar item do pedido
            item_kds = ItemPedidoKDS(
                produto_id=item_venda.produto_id,
                produto_nome=item_venda.produto.nome,
                quantidade=item_venda.quantidade,
                setor_preparo_id=setor_id,
                status=StatusItemPedido.PENDENTE,
                tempo_estimado=tempo_preparo
            )
            
            pedido.itens.append(item_kds)
            tempo_total = max(tempo_total, tempo_preparo)
        
        # Definir setor principal (o que tem mais itens)
        setor_principal_id = max(setores_envolvidos, key=lambda s: 
            sum(1 for i in pedido.itens if i.setor_preparo_id == s)
        )
        
        pedido.setor_principal_id = setor_principal_id
        pedido.tempo_estimado_total = tempo_total
        
        # Salvar pedido
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        
        # Registrar no histórico
        self._registrar_historico(
            pedido_id=pedido.id,
            acao="recebido",
            descricao=f"Pedido criado a partir da venda #{venda_id}",
            usuario_id=venda.usuario_id
        )
        
        # Notificar via WebSocket
        await self._notificar_novo_pedido(pedido)
        
        return pedido
    
    async def criar_pedido_manual(
        self,
        itens: List[Dict],
        cliente_nome: str = None,
        mesa_numero: str = None,
        tipo: TipoPedido = TipoPedido.BALCAO,
        observacoes: str = None,
        usuario_id: int = None
    ) -> PedidoKDS:
        """Cria um pedido manual no KDS"""
        
        numero_pedido = self._gerar_numero_pedido()
        
        # Criar pedido
        pedido = PedidoKDS(
            numero_pedido=numero_pedido,
            tipo=tipo,
            origem="Manual",
            cliente_nome=cliente_nome or f"Cliente #{numero_pedido}",
            mesa_numero=mesa_numero,
            observacoes=observacoes,
            status=StatusPedido.RECEBIDO,
            prioridade=PrioridadePedido.NORMAL,
            operador_pedido_id=usuario_id
        )
        
        # Adicionar itens
        tempo_total = 0
        setores_envolvidos = set()
        
        for item_data in itens:
            produto_id = item_data.get('produto_id')
            quantidade = item_data.get('quantidade', 1)
            modificacoes = item_data.get('modificacoes', [])
            
            # Buscar produto
            produto = self.db.query(Produto).filter(Produto.id == produto_id).first()
            if not produto:
                continue
            
            # Buscar setor
            produto_setor = self.db.query(ProdutoSetor).filter(
                ProdutoSetor.produto_id == produto_id,
                ProdutoSetor.setor_principal == True
            ).first()
            
            setor_id = produto_setor.setor_id if produto_setor else 1
            tempo_preparo = produto_setor.tempo_preparo if produto_setor else 15
            
            setores_envolvidos.add(setor_id)
            
            # Criar item
            item_kds = ItemPedidoKDS(
                produto_id=produto_id,
                produto_nome=produto.nome,
                quantidade=quantidade,
                setor_preparo_id=setor_id,
                modificacoes=modificacoes,
                status=StatusItemPedido.PENDENTE,
                tempo_estimado=tempo_preparo
            )
            
            pedido.itens.append(item_kds)
            tempo_total = max(tempo_total, tempo_preparo)
        
        # Definir setor principal
        if setores_envolvidos:
            pedido.setor_principal_id = list(setores_envolvidos)[0]
        
        pedido.tempo_estimado_total = tempo_total
        
        # Salvar
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        
        # Registrar histórico
        self._registrar_historico(
            pedido_id=pedido.id,
            acao="recebido",
            descricao="Pedido criado manualmente",
            usuario_id=usuario_id
        )
        
        # Notificar
        await self._notificar_novo_pedido(pedido)
        
        return pedido
    
    # ==================== ATUALIZAÇÃO DE STATUS ====================
    
    async def marcar_visualizado(
        self, 
        pedido_id: int, 
        usuario_id: int = None,
        terminal_id: int = None
    ) -> bool:
        """Marca pedido como visualizado"""
        
        pedido = self.db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
        if not pedido:
            return False
        
        if pedido.status == StatusPedido.RECEBIDO:
            pedido.status = StatusPedido.VISUALIZADO
            pedido.data_visualizado = datetime.now()
            
            # Registrar histórico
            self._registrar_historico(
                pedido_id=pedido_id,
                acao="visualizado",
                descricao="Pedido visualizado na cozinha",
                usuario_id=usuario_id,
                terminal_id=terminal_id
            )
            
            self.db.commit()
            
            # Notificar atualização
            await self.event_handler.atualizar_pedido(
                pedido_id=pedido_id,
                status="visualizado",
                setor_id=pedido.setor_principal_id
            )
            
            return True
        
        return False
    
    async def iniciar_preparo(
        self,
        pedido_id: int,
        item_id: Optional[int] = None,
        usuario_id: int = None,
        terminal_id: int = None
    ) -> bool:
        """Inicia preparo de um pedido ou item específico"""
        
        pedido = self.db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
        if not pedido:
            return False
        
        if item_id:
            # Iniciar item específico
            item = self.db.query(ItemPedidoKDS).filter(
                ItemPedidoKDS.id == item_id,
                ItemPedidoKDS.pedido_id == pedido_id
            ).first()
            
            if item and item.status == StatusItemPedido.PENDENTE:
                item.status = StatusItemPedido.PREPARANDO
                item.data_inicio_preparo = datetime.now()
                
                # Registrar histórico
                self._registrar_historico(
                    pedido_id=pedido_id,
                    acao="iniciado",
                    descricao=f"Item {item.produto_nome} iniciado",
                    item_id=item_id,
                    usuario_id=usuario_id,
                    terminal_id=terminal_id
                )
                
                # Se é o primeiro item, atualizar pedido
                if pedido.status in [StatusPedido.RECEBIDO, StatusPedido.VISUALIZADO]:
                    pedido.status = StatusPedido.PREPARANDO
                    pedido.data_inicio_preparo = datetime.now()
                    pedido.operador_preparo_id = usuario_id
                
                self.db.commit()
                
                # Notificar
                await self.event_handler.atualizar_pedido(
                    pedido_id=pedido_id,
                    status="preparando",
                    setor_id=item.setor_preparo_id,
                    detalhes={"item_id": item_id}
                )
                
                return True
        else:
            # Iniciar todos os itens
            if pedido.status in [StatusPedido.RECEBIDO, StatusPedido.VISUALIZADO]:
                pedido.status = StatusPedido.PREPARANDO
                pedido.data_inicio_preparo = datetime.now()
                pedido.operador_preparo_id = usuario_id
                
                for item in pedido.itens:
                    if item.status == StatusItemPedido.PENDENTE:
                        item.status = StatusItemPedido.PREPARANDO
                        item.data_inicio_preparo = datetime.now()
                
                # Registrar histórico
                self._registrar_historico(
                    pedido_id=pedido_id,
                    acao="iniciado",
                    descricao="Preparo iniciado",
                    usuario_id=usuario_id,
                    terminal_id=terminal_id
                )
                
                self.db.commit()
                
                # Notificar
                await self.event_handler.atualizar_pedido(
                    pedido_id=pedido_id,
                    status="preparando",
                    setor_id=pedido.setor_principal_id
                )
                
                return True
        
        return False
    
    async def marcar_item_pronto(
        self,
        pedido_id: int,
        item_id: int,
        usuario_id: int = None,
        terminal_id: int = None
    ) -> bool:
        """Marca um item como pronto"""
        
        item = self.db.query(ItemPedidoKDS).filter(
            ItemPedidoKDS.id == item_id,
            ItemPedidoKDS.pedido_id == pedido_id
        ).first()
        
        if not item:
            return False
        
        if item.status in [StatusItemPedido.PENDENTE, StatusItemPedido.PREPARANDO]:
            item.status = StatusItemPedido.PRONTO
            item.data_pronto = datetime.now()
            item.preparado_por_id = usuario_id
            
            # Calcular tempo de preparo
            if item.data_inicio_preparo:
                item.tempo_decorrido = int(
                    (item.data_pronto - item.data_inicio_preparo).total_seconds() / 60
                )
            
            # Registrar histórico
            self._registrar_historico(
                pedido_id=pedido_id,
                acao="pronto",
                descricao=f"Item {item.produto_nome} pronto",
                item_id=item_id,
                usuario_id=usuario_id,
                terminal_id=terminal_id
            )
            
            # Verificar se todos os itens estão prontos
            pedido = item.pedido
            todos_prontos = all(
                i.status in [StatusItemPedido.PRONTO, StatusItemPedido.ENTREGUE, StatusItemPedido.CANCELADO]
                for i in pedido.itens
            )
            
            if todos_prontos:
                pedido.status = StatusPedido.PRONTO
                pedido.data_pronto = datetime.now()
                
                # Calcular tempo total
                if pedido.data_inicio_preparo:
                    pedido.tempo_decorrido = int(
                        (pedido.data_pronto - pedido.data_pedido).total_seconds() / 60
                    )
            
            self.db.commit()
            
            # Notificar
            await self.event_handler.item_pronto(
                pedido_id=pedido_id,
                item_id=item_id,
                setor_id=item.setor_preparo_id
            )
            
            return True
        
        return False
    
    async def marcar_entregue(
        self,
        pedido_id: int,
        usuario_id: int = None,
        terminal_id: int = None
    ) -> bool:
        """Marca pedido como entregue"""
        
        pedido = self.db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
        if not pedido:
            return False
        
        if pedido.status == StatusPedido.PRONTO:
            pedido.status = StatusPedido.ENTREGUE
            pedido.data_entrega = datetime.now()
            pedido.operador_entrega_id = usuario_id
            
            # Marcar todos os itens como entregues
            for item in pedido.itens:
                if item.status == StatusItemPedido.PRONTO:
                    item.status = StatusItemPedido.ENTREGUE
                    item.data_entrega = datetime.now()
            
            # Registrar histórico
            self._registrar_historico(
                pedido_id=pedido_id,
                acao="entregue",
                descricao="Pedido entregue",
                usuario_id=usuario_id,
                terminal_id=terminal_id
            )
            
            self.db.commit()
            
            # Atualizar métricas
            await self._atualizar_metricas(pedido)
            
            # Notificar
            await self.event_handler.atualizar_pedido(
                pedido_id=pedido_id,
                status="entregue",
                setor_id=pedido.setor_principal_id
            )
            
            return True
        
        return False
    
    async def cancelar_pedido(
        self,
        pedido_id: int,
        motivo: str = None,
        usuario_id: int = None
    ) -> bool:
        """Cancela um pedido"""
        
        pedido = self.db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
        if not pedido:
            return False
        
        if pedido.status not in [StatusPedido.ENTREGUE, StatusPedido.CANCELADO]:
            pedido.status = StatusPedido.CANCELADO
            pedido.data_cancelamento = datetime.now()
            
            # Cancelar todos os itens
            for item in pedido.itens:
                if item.status not in [StatusItemPedido.ENTREGUE, StatusItemPedido.CANCELADO]:
                    item.status = StatusItemPedido.CANCELADO
            
            # Registrar histórico
            self._registrar_historico(
                pedido_id=pedido_id,
                acao="cancelado",
                descricao=f"Pedido cancelado. Motivo: {motivo or 'Não informado'}",
                usuario_id=usuario_id
            )
            
            self.db.commit()
            
            # Notificar
            await self.event_handler.atualizar_pedido(
                pedido_id=pedido_id,
                status="cancelado",
                setor_id=pedido.setor_principal_id,
                detalhes={"motivo": motivo}
            )
            
            return True
        
        return False
    
    # ==================== CONSULTAS ====================
    
    def listar_pedidos_setor(
        self,
        setor_id: int,
        incluir_entregues: bool = False,
        limite: int = 50
    ) -> List[PedidoKDS]:
        """Lista pedidos de um setor"""
        
        query = self.db.query(PedidoKDS).filter(
            or_(
                PedidoKDS.setor_principal_id == setor_id,
                PedidoKDS.itens.any(ItemPedidoKDS.setor_preparo_id == setor_id)
            )
        )
        
        if not incluir_entregues:
            query = query.filter(
                PedidoKDS.status.notin_([StatusPedido.ENTREGUE, StatusPedido.CANCELADO])
            )
        
        # Ordenar por prioridade e tempo
        pedidos = query.order_by(
            PedidoKDS.prioridade.desc(),
            PedidoKDS.data_pedido.asc()
        ).limit(limite).all()
        
        # Calcular tempo decorrido
        agora = datetime.now()
        for pedido in pedidos:
            pedido.tempo_decorrido = int(
                (agora - pedido.data_pedido).total_seconds() / 60
            )
        
        return pedidos
    
    def obter_pedido_completo(self, pedido_id: int) -> Optional[Dict]:
        """Obtém dados completos de um pedido"""
        
        pedido = self.db.query(PedidoKDS).filter(PedidoKDS.id == pedido_id).first()
        if not pedido:
            return None
        
        # Calcular tempo decorrido
        agora = datetime.now()
        tempo_decorrido = int((agora - pedido.data_pedido).total_seconds() / 60)
        
        # Serializar pedido
        return {
            "id": pedido.id,
            "numero_pedido": pedido.numero_pedido,
            "tipo": pedido.tipo.value,
            "cliente_nome": pedido.cliente_nome,
            "mesa_numero": pedido.mesa_numero,
            "status": pedido.status.value,
            "prioridade": pedido.prioridade.value,
            "observacoes": pedido.observacoes,
            "tempo_estimado": pedido.tempo_estimado_total,
            "tempo_decorrido": tempo_decorrido,
            "alerta_atraso": tempo_decorrido > pedido.tempo_estimado_total,
            "data_pedido": pedido.data_pedido.isoformat(),
            "itens": [
                {
                    "id": item.id,
                    "produto_nome": item.produto_nome,
                    "quantidade": item.quantidade,
                    "modificacoes": item.modificacoes or [],
                    "observacoes": item.observacoes,
                    "status": item.status.value,
                    "setor": item.setor_preparo.nome if item.setor_preparo else None,
                    "tempo_estimado": item.tempo_estimado,
                    "tempo_decorrido": item.tempo_decorrido
                }
                for item in pedido.itens
            ]
        }
    
    def obter_estatisticas_setor(
        self,
        setor_id: int,
        data_inicio: datetime = None,
        data_fim: datetime = None
    ) -> Dict:
        """Obtém estatísticas de um setor"""
        
        if not data_inicio:
            data_inicio = datetime.now().replace(hour=0, minute=0, second=0)
        if not data_fim:
            data_fim = datetime.now()
        
        # Buscar pedidos do período
        pedidos = self.db.query(PedidoKDS).filter(
            PedidoKDS.setor_principal_id == setor_id,
            PedidoKDS.data_pedido >= data_inicio,
            PedidoKDS.data_pedido <= data_fim
        ).all()
        
        # Calcular estatísticas
        total_pedidos = len(pedidos)
        pedidos_entregues = len([p for p in pedidos if p.status == StatusPedido.ENTREGUE])
        pedidos_cancelados = len([p for p in pedidos if p.status == StatusPedido.CANCELADO])
        pedidos_em_preparo = len([p for p in pedidos if p.status == StatusPedido.PREPARANDO])
        pedidos_prontos = len([p for p in pedidos if p.status == StatusPedido.PRONTO])
        
        # Calcular tempos
        tempos_preparo = []
        for pedido in pedidos:
            if pedido.status == StatusPedido.ENTREGUE and pedido.tempo_decorrido:
                tempos_preparo.append(pedido.tempo_decorrido)
        
        tempo_medio = sum(tempos_preparo) / len(tempos_preparo) if tempos_preparo else 0
        
        # Pedidos atrasados
        pedidos_atrasados = 0
        for pedido in pedidos:
            if pedido.status not in [StatusPedido.ENTREGUE, StatusPedido.CANCELADO]:
                tempo_atual = int((datetime.now() - pedido.data_pedido).total_seconds() / 60)
                if tempo_atual > pedido.tempo_estimado_total:
                    pedidos_atrasados += 1
        
        return {
            "setor_id": setor_id,
            "periodo": {
                "inicio": data_inicio.isoformat(),
                "fim": data_fim.isoformat()
            },
            "totais": {
                "total": total_pedidos,
                "entregues": pedidos_entregues,
                "cancelados": pedidos_cancelados,
                "em_preparo": pedidos_em_preparo,
                "prontos": pedidos_prontos,
                "atrasados": pedidos_atrasados
            },
            "tempos": {
                "medio_preparo": round(tempo_medio, 1),
                "minimo": min(tempos_preparo) if tempos_preparo else 0,
                "maximo": max(tempos_preparo) if tempos_preparo else 0
            },
            "taxas": {
                "cumprimento_prazo": round(
                    (pedidos_entregues - pedidos_atrasados) / pedidos_entregues * 100
                    if pedidos_entregues else 0, 1
                ),
                "cancelamento": round(
                    pedidos_cancelados / total_pedidos * 100
                    if total_pedidos else 0, 1
                )
            }
        }
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _gerar_numero_pedido(self) -> str:
        """Gera número único para pedido"""
        hoje = datetime.now()
        
        # Contar pedidos do dia
        count = self.db.query(func.count(PedidoKDS.id)).filter(
            func.date(PedidoKDS.data_pedido) == hoje.date()
        ).scalar()
        
        # Formato: YYYYMMDD-NNNN
        return f"{hoje.strftime('%Y%m%d')}-{count + 1:04d}"
    
    def _registrar_historico(
        self,
        pedido_id: int,
        acao: str,
        descricao: str = None,
        item_id: int = None,
        usuario_id: int = None,
        terminal_id: int = None
    ):
        """Registra ação no histórico"""
        
        historico = HistoricoPedidoKDS(
            pedido_id=pedido_id,
            acao=acao,
            descricao=descricao,
            item_id=item_id,
            usuario_id=usuario_id,
            terminal_id=terminal_id
        )
        
        self.db.add(historico)
    
    async def _notificar_novo_pedido(self, pedido: PedidoKDS):
        """Notifica novo pedido via WebSocket"""
        
        # Serializar pedido
        pedido_data = self.obter_pedido_completo(pedido.id)
        
        # Notificar setor principal
        await self.event_handler.novo_pedido(pedido_data, pedido.setor_principal_id)
        
        # Notificar outros setores envolvidos
        setores_notificados = {pedido.setor_principal_id}
        for item in pedido.itens:
            if item.setor_preparo_id not in setores_notificados:
                await self.event_handler.novo_pedido(pedido_data, item.setor_preparo_id)
                setores_notificados.add(item.setor_preparo_id)
    
    async def _atualizar_metricas(self, pedido: PedidoKDS):
        """Atualiza métricas do KDS"""
        
        hoje = datetime.now().date()
        
        # Buscar ou criar métrica do dia
        metrica = self.db.query(MetricasKDS).filter(
            func.date(MetricasKDS.data) == hoje,
            MetricasKDS.setor_id == pedido.setor_principal_id
        ).first()
        
        if not metrica:
            metrica = MetricasKDS(
                data=datetime.now(),
                setor_id=pedido.setor_principal_id
            )
            self.db.add(metrica)
        
        # Atualizar contadores
        metrica.total_pedidos += 1
        
        if pedido.status == StatusPedido.ENTREGUE:
            if pedido.tempo_decorrido and pedido.tempo_decorrido <= pedido.tempo_estimado_total:
                metrica.pedidos_no_prazo += 1
            else:
                metrica.pedidos_atrasados += 1
            
            # Atualizar tempos
            if pedido.tempo_decorrido:
                if metrica.tempo_medio_preparo:
                    # Média incremental
                    metrica.tempo_medio_preparo = (
                        (metrica.tempo_medio_preparo * (metrica.total_pedidos - 1) + pedido.tempo_decorrido) 
                        / metrica.total_pedidos
                    )
                else:
                    metrica.tempo_medio_preparo = pedido.tempo_decorrido
                
                # Min/Max
                if not metrica.tempo_minimo_preparo or pedido.tempo_decorrido < metrica.tempo_minimo_preparo:
                    metrica.tempo_minimo_preparo = pedido.tempo_decorrido
                
                if not metrica.tempo_maximo_preparo or pedido.tempo_decorrido > metrica.tempo_maximo_preparo:
                    metrica.tempo_maximo_preparo = pedido.tempo_decorrido
        
        elif pedido.status == StatusPedido.CANCELADO:
            metrica.pedidos_cancelados += 1
        
        # Calcular taxas
        if metrica.total_pedidos > 0:
            metrica.taxa_cumprimento_prazo = (metrica.pedidos_no_prazo / metrica.total_pedidos) * 100
            metrica.taxa_cancelamento = (metrica.pedidos_cancelados / metrica.total_pedidos) * 100
        
        self.db.commit()
    
    async def verificar_pedidos_atrasados(self):
        """Verifica e alerta sobre pedidos atrasados (executar periodicamente)"""
        
        agora = datetime.now()
        
        # Buscar pedidos em andamento
        pedidos = self.db.query(PedidoKDS).filter(
            PedidoKDS.status.in_([
                StatusPedido.RECEBIDO,
                StatusPedido.VISUALIZADO,
                StatusPedido.PREPARANDO
            ])
        ).all()
        
        for pedido in pedidos:
            tempo_decorrido = int((agora - pedido.data_pedido).total_seconds() / 60)
            
            # Verificar se está atrasado
            if tempo_decorrido > pedido.tempo_estimado_total and not pedido.alerta_atraso:
                pedido.alerta_atraso = True
                self.db.commit()
                
                # Enviar alerta
                await self.event_handler.alerta_atraso(
                    pedido_id=pedido.id,
                    tempo_decorrido=tempo_decorrido,
                    setor_id=pedido.setor_principal_id
                )
                
                logger.warning(
                    f"Pedido {pedido.numero_pedido} atrasado: "
                    f"{tempo_decorrido} minutos (estimativa: {pedido.tempo_estimado_total})"
                )