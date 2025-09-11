"""
Serviço avançado do sistema KDS com workflow e automação
Baseado na arquitetura MEEP para gestão completa de cozinha
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case, desc, asc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date, time
import json
import asyncio
from dataclasses import dataclass

from ..models import (
    FilaKDS, FluxoKDS, EtapaFluxoKDS, NotificacaoKDS, 
    TemplateFluxoKDS, MetricaKDS, AlertaKDS, PedidoKDS, 
    EstacaoKDS, ItemPedidoKDS, Usuario
)
from ..schemas_kds_avancado import (
    TipoFluxoKDS, StatusEtapaKDS, TipoNotificacaoKDS,
    SeveridadeAlerta, DashboardKDSMetricas, FluxoKDSCompleto,
    EstacaoKDSStatus, ResumoOperacionalKDS
)

@dataclass
class ConfiguracaoFluxo:
    """Configuração de um fluxo de trabalho KDS"""
    nome: str
    estacoes: List[int]
    tipo: TipoFluxoKDS
    regras: Dict[str, Any]
    tempo_estimado: int

class KDSAvancadoService:
    """Serviço principal para operações avançadas do KDS"""
    
    def __init__(self, db: Session):
        self.db = db
        
    # ====== GESTÃO DE FLUXOS ======
    
    def criar_fluxo_automatico(
        self, 
        pedido_id: int,
        categoria_produto: str,
        complexidade: str = "medio"
    ) -> FluxoKDS:
        """
        Cria automaticamente um fluxo baseado no tipo de produto
        """
        # Buscar template adequado
        template = self.db.query(TemplateFluxoKDS).filter(
            TemplateFluxoKDS.categoria == categoria_produto,
            TemplateFluxoKDS.complexidade == complexidade,
            TemplateFluxoKDS.ativo == True
        ).first()
        
        if not template:
            # Template padrão se não encontrar específico
            template = self.db.query(TemplateFluxoKDS).filter(
                TemplateFluxoKDS.categoria == "geral",
                TemplateFluxoKDS.ativo == True
            ).first()
        
        if template:
            # Incrementar uso do template
            template.uso_count += 1
            
            # Criar fluxo baseado no template
            fluxo_config = json.loads(template.fluxo_config) if isinstance(template.fluxo_config, str) else template.fluxo_config
            
            novo_fluxo = FluxoKDS(
                nome=f"Fluxo para Pedido #{pedido_id}",
                tipo=fluxo_config.get("tipo", "sequencial"),
                estacoes=json.dumps(fluxo_config.get("estacoes", [])),
                regras=json.dumps(fluxo_config.get("regras", {})),
                tempo_estimado_total=template.tempo_estimado
            )
            
            self.db.add(novo_fluxo)
            self.db.flush()
            
            # Criar etapas do fluxo
            self._criar_etapas_fluxo(novo_fluxo.id, pedido_id, fluxo_config)
            
            self.db.commit()
            return novo_fluxo
        
        raise ValueError(f"Nenhum template encontrado para categoria: {categoria_produto}")
    
    def _criar_etapas_fluxo(
        self, 
        fluxo_id: int, 
        pedido_id: int, 
        fluxo_config: Dict[str, Any]
    ):
        """Cria as etapas individuais do fluxo"""
        estacoes = fluxo_config.get("estacoes", [])
        tempos_estimados = fluxo_config.get("tempos_por_estacao", {})
        
        for ordem, estacao_id in enumerate(estacoes):
            etapa = EtapaFluxoKDS(
                fluxo_id=fluxo_id,
                pedido_id=pedido_id,
                estacao_id=estacao_id,
                ordem=ordem,
                tempo_estimado=tempos_estimados.get(str(estacao_id), 15)
            )
            self.db.add(etapa)
    
    def avancar_etapa_fluxo(
        self,
        etapa_id: int,
        novo_status: StatusEtapaKDS,
        observacoes: Optional[str] = None
    ) -> EtapaFluxoKDS:
        """
        Avança uma etapa do fluxo e gerencia transições automáticas
        """
        etapa = self.db.query(EtapaFluxoKDS).filter(
            EtapaFluxoKDS.id == etapa_id
        ).first()
        
        if not etapa:
            raise ValueError("Etapa não encontrada")
        
        status_anterior = etapa.status
        etapa.status = novo_status
        
        if observacoes:
            etapa.observacoes = observacoes
            
        # Gerenciar timestamps
        agora = datetime.now()
        
        if novo_status == StatusEtapaKDS.EM_PREPARO and status_anterior != StatusEtapaKDS.EM_PREPARO:
            etapa.iniciado_em = agora
            
        elif novo_status == StatusEtapaKDS.CONCLUIDA and status_anterior != StatusEtapaKDS.CONCLUIDA:
            etapa.concluido_em = agora
            
            if etapa.iniciado_em:
                tempo_real = (agora - etapa.iniciado_em).total_seconds() / 60
                etapa.tempo_real = int(tempo_real)
            
            # Verificar se pode avançar próxima etapa
            self._verificar_proxima_etapa(etapa.fluxo_id, etapa.pedido_id, etapa.ordem)
        
        self.db.commit()
        return etapa
    
    def _verificar_proxima_etapa(self, fluxo_id: int, pedido_id: int, ordem_atual: int):
        """Verifica e ativa automaticamente a próxima etapa se aplicável"""
        fluxo = self.db.query(FluxoKDS).filter(FluxoKDS.id == fluxo_id).first()
        
        if not fluxo:
            return
            
        # Para fluxos sequenciais, ativar próxima etapa automaticamente
        if fluxo.tipo == "sequencial":
            proxima_etapa = self.db.query(EtapaFluxoKDS).filter(
                EtapaFluxoKDS.fluxo_id == fluxo_id,
                EtapaFluxoKDS.pedido_id == pedido_id,
                EtapaFluxoKDS.ordem == ordem_atual + 1,
                EtapaFluxoKDS.status == StatusEtapaKDS.PENDENTE
            ).first()
            
            if proxima_etapa:
                # Criar notificação para a próxima estação
                self._criar_notificacao(
                    TipoNotificacaoKDS.INFO,
                    "Nova Etapa Disponível",
                    f"Etapa {proxima_etapa.ordem + 1} do pedido está pronta para iniciar",
                    proxima_etapa.estacao_id,
                    pedido_id
                )
    
    # ====== SISTEMA DE ALERTAS INTELIGENTE ======
    
    def verificar_alertas_automaticos(self) -> List[AlertaKDS]:
        """
        Verifica e cria alertas automáticos baseado nas regras configuradas
        """
        alertas_criados = []
        agora = datetime.now()
        
        # 1. Alertas de tempo excedido
        alertas_criados.extend(self._verificar_alertas_tempo())
        
        # 2. Alertas de fila cheia
        alertas_criados.extend(self._verificar_alertas_fila())
        
        # 3. Alertas de eficiência baixa
        alertas_criados.extend(self._verificar_alertas_eficiencia())
        
        # 4. Alertas de equipamentos offline (simulado)
        alertas_criados.extend(self._verificar_alertas_equipamentos())
        
        self.db.commit()
        return alertas_criados
    
    def _verificar_alertas_tempo(self) -> List[AlertaKDS]:
        """Verifica pedidos que excederam o tempo estimado"""
        alertas = []
        limite_atraso = datetime.now() - timedelta(minutes=30)
        
        pedidos_atrasados = self.db.query(PedidoKDS).join(EtapaFluxoKDS).filter(
            EtapaFluxoKDS.status == StatusEtapaKDS.EM_PREPARO,
            EtapaFluxoKDS.iniciado_em < limite_atraso,
            # Não existe alerta não resolvido para este pedido
            ~self.db.query(AlertaKDS).filter(
                AlertaKDS.pedido_id == PedidoKDS.id,
                AlertaKDS.tipo == "tempo_excedido",
                AlertaKDS.resolvido == False
            ).exists()
        ).all()
        
        for pedido in pedidos_atrasados:
            alerta = AlertaKDS(
                tipo="tempo_excedido",
                severidade=SeveridadeAlerta.ALTA,
                titulo=f"Pedido #{pedido.numero_pedido} com atraso",
                descricao=f"Pedido excedeu tempo estimado em mais de 30 minutos",
                estacao_id=pedido.estacao_id,
                pedido_id=pedido.id,
                regra_config=json.dumps({"limite_minutos": 30})
            )
            
            self.db.add(alerta)
            alertas.append(alerta)
        
        return alertas
    
    def _verificar_alertas_fila(self) -> List[AlertaKDS]:
        """Verifica filas que estão muito cheias"""
        alertas = []
        
        estacoes_sobrecarregadas = self.db.query(
            EstacaoKDS.id,
            EstacaoKDS.nome,
            func.count(PedidoKDS.id).label('total_pedidos')
        ).join(PedidoKDS).filter(
            PedidoKDS.status.in_(['pendente', 'em_preparo']),
            EstacaoKDS.ativo == True
        ).group_by(EstacaoKDS.id, EstacaoKDS.nome).having(
            func.count(PedidoKDS.id) > 10  # Limite de 10 pedidos por estação
        ).all()
        
        for estacao_id, nome, total in estacoes_sobrecarregadas:
            # Verificar se já não existe alerta ativo
            alerta_existente = self.db.query(AlertaKDS).filter(
                AlertaKDS.estacao_id == estacao_id,
                AlertaKDS.tipo == "fila_cheia",
                AlertaKDS.resolvido == False
            ).first()
            
            if not alerta_existente:
                alerta = AlertaKDS(
                    tipo="fila_cheia",
                    severidade=SeveridadeAlerta.MEDIA,
                    titulo=f"Fila da {nome} sobrecarregada",
                    descricao=f"Estação possui {total} pedidos na fila",
                    estacao_id=estacao_id,
                    regra_config=json.dumps({"limite_pedidos": 10, "total_atual": total})
                )
                
                self.db.add(alerta)
                alertas.append(alerta)
        
        return alertas
    
    def _verificar_alertas_eficiencia(self) -> List[AlertaKDS]:
        """Verifica estações com eficiência baixa"""
        alertas = []
        data_inicio = datetime.now() - timedelta(hours=2)
        
        # Calcular eficiência das últimas 2 horas
        eficiencia_estacoes = self.db.query(
            EstacaoKDS.id,
            EstacaoKDS.nome,
            func.count(PedidoKDS.id).label('total_pedidos'),
            func.count(
                case([(PedidoKDS.status == 'entregue', 1)])
            ).label('pedidos_concluidos')
        ).join(PedidoKDS).filter(
            PedidoKDS.created_at >= data_inicio,
            EstacaoKDS.ativo == True
        ).group_by(EstacaoKDS.id, EstacaoKDS.nome).all()
        
        for estacao_id, nome, total, concluidos in eficiencia_estacoes:
            if total > 5:  # Só alertar se houver volume mínimo
                eficiencia = (concluidos / total) * 100 if total > 0 else 0
                
                if eficiencia < 50:  # Eficiência menor que 50%
                    alerta_existente = self.db.query(AlertaKDS).filter(
                        AlertaKDS.estacao_id == estacao_id,
                        AlertaKDS.tipo == "eficiencia_baixa",
                        AlertaKDS.resolvido == False,
                        AlertaKDS.criado_em >= data_inicio
                    ).first()
                    
                    if not alerta_existente:
                        alerta = AlertaKDS(
                            tipo="eficiencia_baixa",
                            severidade=SeveridadeAlerta.MEDIA,
                            titulo=f"Eficiência baixa na {nome}",
                            descricao=f"Eficiência de {eficiencia:.1f}% nas últimas 2 horas",
                            estacao_id=estacao_id,
                            regra_config=json.dumps({
                                "eficiencia_minima": 50,
                                "eficiencia_atual": eficiencia,
                                "periodo_horas": 2
                            })
                        )
                        
                        self.db.add(alerta)
                        alertas.append(alerta)
        
        return alertas
    
    def _verificar_alertas_equipamentos(self) -> List[AlertaKDS]:
        """Simula verificação de equipamentos offline"""
        # Esta função seria integrada com sistemas de monitoramento reais
        # Por agora, simularemos alguns cenários
        return []
    
    # ====== NOTIFICAÇÕES INTELIGENTES ======
    
    def _criar_notificacao(
        self,
        tipo: TipoNotificacaoKDS,
        titulo: str,
        mensagem: str,
        estacao_id: int,
        pedido_id: Optional[int] = None,
        usuario_id: Optional[int] = None,
        urgente: bool = False
    ) -> NotificacaoKDS:
        """Cria uma nova notificação no sistema"""
        notificacao = NotificacaoKDS(
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            estacao_id=estacao_id,
            pedido_id=pedido_id,
            usuario_id=usuario_id,
            urgente=urgente
        )
        
        self.db.add(notificacao)
        return notificacao
    
    def processar_notificacoes_automaticas(self) -> List[NotificacaoKDS]:
        """Processa e cria notificações automáticas baseadas em eventos"""
        notificacoes_criadas = []
        
        # 1. Notificações de pedidos próximos ao prazo
        notificacoes_criadas.extend(self._notificar_pedidos_proximo_prazo())
        
        # 2. Notificações de mudanças de turno
        notificacoes_criadas.extend(self._notificar_mudanca_turno())
        
        # 3. Notificações de metas alcançadas
        notificacoes_criadas.extend(self._notificar_metas_alcancadas())
        
        self.db.commit()
        return notificacoes_criadas
    
    def _notificar_pedidos_proximo_prazo(self) -> List[NotificacaoKDS]:
        """Notifica sobre pedidos próximos ao prazo limite"""
        notificacoes = []
        limite_alerta = datetime.now() + timedelta(minutes=10)
        
        # Buscar pedidos que vencerão em 10 minutos
        pedidos_proximo_prazo = self.db.query(PedidoKDS).join(EtapaFluxoKDS).filter(
            EtapaFluxoKDS.status == StatusEtapaKDS.EM_PREPARO,
            # Lógica simplificada: pedidos iniciados há mais de 20 min (assumindo 30 min total)
            EtapaFluxoKDS.iniciado_em < datetime.now() - timedelta(minutes=20)
        ).all()
        
        for pedido in pedidos_proximo_prazo:
            # Verificar se já não foi notificado recentemente
            notificacao_recente = self.db.query(NotificacaoKDS).filter(
                NotificacaoKDS.pedido_id == pedido.id,
                NotificacaoKDS.tipo == TipoNotificacaoKDS.ALERTA,
                NotificacaoKDS.criado_em >= datetime.now() - timedelta(minutes=15)
            ).first()
            
            if not notificacao_recente:
                notificacao = self._criar_notificacao(
                    TipoNotificacaoKDS.ALERTA,
                    f"Prazo próximo - Pedido #{pedido.numero_pedido}",
                    "Pedido deve ser finalizado em breve para cumprir prazo estimado",
                    pedido.estacao_id,
                    pedido.id,
                    urgente=True
                )
                notificacoes.append(notificacao)
        
        return notificacoes
    
    def _notificar_mudanca_turno(self) -> List[NotificacaoKDS]:
        """Notifica sobre mudanças de turno e status das estações"""
        # Implementação futura - requer integração com sistema de RH
        return []
    
    def _notificar_metas_alcancadas(self) -> List[NotificacaoKDS]:
        """Notifica quando metas diárias são alcançadas"""
        notificacoes = []
        hoje = date.today()
        
        # Buscar métricas do dia para cada estação
        metricas_hoje = self.db.query(MetricaKDS).filter(
            MetricaKDS.data_coleta == hoje
        ).all()
        
        for metrica in metricas_hoje:
            # Exemplo: meta de 100 pedidos por dia
            if metrica.total_pedidos >= 100 and metrica.pedidos_concluidos >= 95:
                # Verificar se já notificou hoje
                notificacao_existente = self.db.query(NotificacaoKDS).filter(
                    NotificacaoKDS.estacao_id == metrica.estacao_id,
                    NotificacaoKDS.tipo == TipoNotificacaoKDS.INFO,
                    NotificacaoKDS.titulo.contains("Meta alcançada"),
                    func.date(NotificacaoKDS.criado_em) == hoje
                ).first()
                
                if not notificacao_existente:
                    estacao = self.db.query(EstacaoKDS).filter(
                        EstacaoKDS.id == metrica.estacao_id
                    ).first()
                    
                    if estacao:
                        notificacao = self._criar_notificacao(
                            TipoNotificacaoKDS.INFO,
                            f"Meta alcançada - {estacao.nome}",
                            f"Parabéns! {metrica.pedidos_concluidos} pedidos concluídos hoje",
                            metrica.estacao_id
                        )
                        notificacoes.append(notificacao)
        
        return notificacoes
    
    # ====== ANALYTICS E MÉTRICAS ======
    
    def gerar_dashboard_metricas(self, periodo_horas: int = 24) -> DashboardKDSMetricas:
        """
        Gera métricas consolidadas para o dashboard principal
        """
        data_inicio = datetime.now() - timedelta(hours=periodo_horas)
        
        # Métricas gerais
        total_estacoes_ativas = self.db.query(EstacaoKDS).filter(
            EstacaoKDS.ativo == True
        ).count()
        
        total_pedidos_fila = self.db.query(PedidoKDS).filter(
            PedidoKDS.status.in_(['pendente', 'em_preparo'])
        ).count()
        
        # Tempo médio atual (últimas 2 horas)
        tempos_recentes = self.db.query(
            func.avg(
                func.extract('epoch', 
                    PedidoKDS.finalizado_em - PedidoKDS.iniciado_em
                ) / 60
            ).label('tempo_medio')
        ).filter(
            PedidoKDS.status == 'entregue',
            PedidoKDS.finalizado_em >= datetime.now() - timedelta(hours=2),
            PedidoKDS.iniciado_em.isnot(None),
            PedidoKDS.finalizado_em.isnot(None)
        ).scalar() or 0
        
        # Eficiência geral
        total_periodo = self.db.query(PedidoKDS).filter(
            PedidoKDS.created_at >= data_inicio
        ).count()
        
        concluidos_periodo = self.db.query(PedidoKDS).filter(
            PedidoKDS.created_at >= data_inicio,
            PedidoKDS.status == 'entregue'
        ).count()
        
        eficiencia_geral = (concluidos_periodo / total_periodo * 100) if total_periodo > 0 else 0
        
        # Alertas e notificações
        alertas_ativos = self.db.query(AlertaKDS).filter(
            AlertaKDS.resolvido == False
        ).count()
        
        notificacoes_nao_lidas = self.db.query(NotificacaoKDS).filter(
            NotificacaoKDS.lida == False
        ).count()
        
        # Performance por estação
        estacoes_performance = self._calcular_performance_estacoes(data_inicio)
        
        # Gráficos
        pedidos_por_hora = self._gerar_grafico_pedidos_hora(data_inicio)
        tempos_preparo_historico = self._gerar_grafico_tempos_historico(data_inicio)
        distribuicao_tipos = self._gerar_grafico_tipos_pedido(data_inicio)
        
        return DashboardKDSMetricas(
            total_estacoes_ativas=total_estacoes_ativas,
            total_pedidos_fila=total_pedidos_fila,
            tempo_medio_atual=float(tempos_recentes),
            eficiencia_geral=eficiencia_geral,
            alertas_ativos=alertas_ativos,
            notificacoes_nao_lidas=notificacoes_nao_lidas,
            estacoes_performance=estacoes_performance,
            pedidos_por_hora=pedidos_por_hora,
            tempos_preparo_historico=tempos_preparo_historico,
            distribuicao_tipos_pedido=distribuicao_tipos
        )
    
    def _calcular_performance_estacoes(self, data_inicio: datetime) -> List[Dict[str, Any]]:
        """Calcula performance individual de cada estação"""
        performance = []
        
        estacoes = self.db.query(EstacaoKDS).filter(EstacaoKDS.ativo == True).all()
        
        for estacao in estacoes:
            pedidos_query = self.db.query(PedidoKDS).filter(
                PedidoKDS.estacao_id == estacao.id,
                PedidoKDS.created_at >= data_inicio
            )
            
            total = pedidos_query.count()
            concluidos = pedidos_query.filter(PedidoKDS.status == 'entregue').count()
            em_andamento = pedidos_query.filter(
                PedidoKDS.status.in_(['pendente', 'em_preparo'])
            ).count()
            
            # Tempo médio
            tempo_medio = pedidos_query.filter(
                PedidoKDS.status == 'entregue',
                PedidoKDS.iniciado_em.isnot(None),
                PedidoKDS.finalizado_em.isnot(None)
            ).with_entities(
                func.avg(
                    func.extract('epoch', 
                        PedidoKDS.finalizado_em - PedidoKDS.iniciado_em
                    ) / 60
                )
            ).scalar() or 0
            
            eficiencia = (concluidos / total * 100) if total > 0 else 0
            
            performance.append({
                "estacao_id": estacao.id,
                "nome": estacao.nome,
                "tipo": estacao.tipo,
                "total_pedidos": total,
                "pedidos_concluidos": concluidos,
                "pedidos_em_andamento": em_andamento,
                "tempo_medio_minutos": float(tempo_medio),
                "eficiencia": eficiencia,
                "status": "ativa" if estacao.ativo else "inativa"
            })
        
        return performance
    
    def _gerar_grafico_pedidos_hora(self, data_inicio: datetime) -> List[Dict[str, Any]]:
        """Gera dados para gráfico de pedidos por hora"""
        result = self.db.query(
            func.extract('hour', PedidoKDS.created_at).label('hora'),
            func.count(PedidoKDS.id).label('total')
        ).filter(
            PedidoKDS.created_at >= data_inicio
        ).group_by(
            func.extract('hour', PedidoKDS.created_at)
        ).order_by('hora').all()
        
        return [
            {"hora": int(hora), "total": total}
            for hora, total in result
        ]
    
    def _gerar_grafico_tempos_historico(self, data_inicio: datetime) -> List[Dict[str, Any]]:
        """Gera dados para gráfico de tempos de preparo histórico"""
        result = self.db.query(
            func.date(PedidoKDS.created_at).label('data'),
            func.avg(
                func.extract('epoch', 
                    PedidoKDS.finalizado_em - PedidoKDS.iniciado_em
                ) / 60
            ).label('tempo_medio')
        ).filter(
            PedidoKDS.created_at >= data_inicio,
            PedidoKDS.status == 'entregue',
            PedidoKDS.iniciado_em.isnot(None),
            PedidoKDS.finalizado_em.isnot(None)
        ).group_by(
            func.date(PedidoKDS.created_at)
        ).order_by('data').all()
        
        return [
            {"data": data.isoformat(), "tempo_medio": float(tempo)}
            for data, tempo in result if tempo is not None
        ]
    
    def _gerar_grafico_tipos_pedido(self, data_inicio: datetime) -> List[Dict[str, Any]]:
        """Gera dados para gráfico de distribuição de tipos de pedido"""
        # Exemplo simplificado - seria baseado em categorias reais de produtos
        result = self.db.query(
            EstacaoKDS.tipo.label('tipo_estacao'),
            func.count(PedidoKDS.id).label('total')
        ).join(PedidoKDS).filter(
            PedidoKDS.created_at >= data_inicio
        ).group_by(EstacaoKDS.tipo).all()
        
        return [
            {"tipo": tipo, "total": total}
            for tipo, total in result
        ]
    
    def gerar_resumo_operacional(self, periodo_horas: int = 24) -> ResumoOperacionalKDS:
        """
        Gera resumo operacional completo com análises e recomendações
        """
        data_inicio = datetime.now() - timedelta(hours=periodo_horas)
        
        # Métricas básicas
        total_pedidos = self.db.query(PedidoKDS).filter(
            PedidoKDS.created_at >= data_inicio
        ).count()
        
        pedidos_concluidos = self.db.query(PedidoKDS).filter(
            PedidoKDS.created_at >= data_inicio,
            PedidoKDS.status == 'entregue'
        ).count()
        
        pedidos_em_andamento = self.db.query(PedidoKDS).filter(
            PedidoKDS.status.in_(['pendente', 'em_preparo'])
        ).count()
        
        # Tempo médio de preparo
        tempo_medio = self.db.query(
            func.avg(
                func.extract('epoch', 
                    PedidoKDS.finalizado_em - PedidoKDS.iniciado_em
                ) / 60
            )
        ).filter(
            PedidoKDS.created_at >= data_inicio,
            PedidoKDS.status == 'entregue',
            PedidoKDS.iniciado_em.isnot(None),
            PedidoKDS.finalizado_em.isnot(None)
        ).scalar() or 0
        
        # Análise de picos de demanda
        pico_demanda = self._analisar_picos_demanda(data_inicio)
        
        # Eficiência por estação
        eficiencia_estacoes = self._calcular_performance_estacoes(data_inicio)
        
        # Identificar problemas e gerar recomendações
        problemas = self._identificar_problemas_operacionais(data_inicio)
        recomendacoes = self._gerar_recomendacoes(eficiencia_estacoes, problemas)
        
        return ResumoOperacionalKDS(
            periodo=f"Últimas {periodo_horas} horas",
            total_pedidos=total_pedidos,
            pedidos_concluidos=pedidos_concluidos,
            pedidos_em_andamento=pedidos_em_andamento,
            tempo_medio_preparo=float(tempo_medio),
            pico_demanda=pico_demanda,
            eficiencia_por_estacao=eficiencia_estacoes,
            problemas_identificados=problemas,
            recomendacoes=recomendacoes
        )
    
    def _analisar_picos_demanda(self, data_inicio: datetime) -> Dict[str, Any]:
        """Analisa os horários de pico de demanda"""
        pedidos_por_hora = self.db.query(
            func.extract('hour', PedidoKDS.created_at).label('hora'),
            func.count(PedidoKDS.id).label('total')
        ).filter(
            PedidoKDS.created_at >= data_inicio
        ).group_by(
            func.extract('hour', PedidoKDS.created_at)
        ).all()
        
        if not pedidos_por_hora:
            return {"horario_pico": None, "volume_pico": 0}
        
        # Encontrar horário com maior volume
        hora_pico, volume_pico = max(pedidos_por_hora, key=lambda x: x.total)
        
        return {
            "horario_pico": f"{int(hora_pico)}:00",
            "volume_pico": volume_pico,
            "distribuicao_horaria": [
                {"hora": f"{int(h)}:00", "volume": v}
                for h, v in pedidos_por_hora
            ]
        }
    
    def _identificar_problemas_operacionais(self, data_inicio: datetime) -> List[str]:
        """Identifica problemas operacionais baseado nas métricas"""
        problemas = []
        
        # Verificar estações com baixa eficiência
        estacoes_baixa_eficiencia = self.db.query(EstacaoKDS).join(PedidoKDS).filter(
            PedidoKDS.created_at >= data_inicio,
            EstacaoKDS.ativo == True
        ).group_by(EstacaoKDS.id, EstacaoKDS.nome).having(
            func.count(
                case([(PedidoKDS.status == 'entregue', 1)])
            ) / func.count(PedidoKDS.id) * 100 < 70
        ).all()
        
        if estacoes_baixa_eficiencia:
            problemas.append(
                f"Eficiência baixa identificada em {len(estacoes_baixa_eficiencia)} estação(ões)"
            )
        
        # Verificar tempos de preparo altos
        tempo_medio_geral = self.db.query(
            func.avg(
                func.extract('epoch', 
                    PedidoKDS.finalizado_em - PedidoKDS.iniciado_em
                ) / 60
            )
        ).filter(
            PedidoKDS.created_at >= data_inicio,
            PedidoKDS.status == 'entregue',
            PedidoKDS.iniciado_em.isnot(None),
            PedidoKDS.finalizado_em.isnot(None)
        ).scalar() or 0
        
        if tempo_medio_geral > 30:  # Mais de 30 minutos
            problemas.append(
                f"Tempo médio de preparo elevado: {tempo_medio_geral:.1f} minutos"
            )
        
        # Verificar alertas não resolvidos
        alertas_criticos = self.db.query(AlertaKDS).filter(
            AlertaKDS.resolvido == False,
            AlertaKDS.severidade.in_(['alta', 'critica'])
        ).count()
        
        if alertas_criticos > 0:
            problemas.append(f"{alertas_criticos} alerta(s) crítico(s) não resolvido(s)")
        
        return problemas
    
    def _gerar_recomendacoes(
        self, 
        eficiencia_estacoes: List[Dict[str, Any]], 
        problemas: List[str]
    ) -> List[str]:
        """Gera recomendações baseadas na análise dos dados"""
        recomendacoes = []
        
        # Recomendações baseadas em eficiência
        estacoes_baixa = [e for e in eficiencia_estacoes if e['eficiencia'] < 70]
        if estacoes_baixa:
            recomendacoes.append(
                "Considerar redistribuição de pedidos ou reforço nas estações com baixa eficiência"
            )
        
        # Recomendações baseadas em volume
        volume_alto = any(e['pedidos_em_andamento'] > 10 for e in eficiencia_estacoes)
        if volume_alto:
            recomendacoes.append(
                "Avaliar abertura de estações adicionais durante picos de demanda"
            )
        
        # Recomendações baseadas em tempo
        tempo_alto = any(e['tempo_medio_minutos'] > 30 for e in eficiencia_estacoes)
        if tempo_alto:
            recomendacoes.append(
                "Revisar processos operacionais para reduzir tempo de preparo"
            )
        
        # Recomendações gerais
        if not problemas:
            recomendacoes.append(
                "Operação funcionando dentro dos parâmetros normais - manter monitoramento"
            )
        
        return recomendacoes