"""
Serviço para gerenciamento de equipamentos e QR readers
Sistema de Gestão de Eventos - Universal v5
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException, status
import logging

from ..models import (
    LeitorQRCode, PontoAcesso, HistoricoLeituraQR, 
    MovimentacaoAcesso, ConfiguracaoEquipamento,
    Usuario, Evento
)
from ..schemas_equipamentos import (
    LeitorQRCodeCreate, LeitorQRCodeUpdate, PontoAcessoCreate, 
    PontoAcessoUpdate, HistoricoLeituraQRCreate, MovimentacaoAcessoCreate,
    ConfiguracaoEquipamentoCreate, EstatisticasLeitorQR, EstatisticasPontoAcesso,
    StatusSistemaEquipamentos
)

logger = logging.getLogger(__name__)

class EquipamentosService:
    """Serviço principal para gerenciamento de equipamentos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== LEITORES QR CODE ====================
    
    def create_leitor_qr(self, leitor_data: LeitorQRCodeCreate, usuario_id: int) -> LeitorQRCode:
        """Cria um novo leitor QR Code"""
        # Verificar se código do equipamento já existe
        existing = self.db.query(LeitorQRCode).filter(
            LeitorQRCode.codigo_equipamento == leitor_data.codigo_equipamento
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Código de equipamento '{leitor_data.codigo_equipamento}' já existe"
            )
        
        leitor = LeitorQRCode(
            **leitor_data.dict(),
            criado_por=usuario_id
        )
        
        self.db.add(leitor)
        self.db.commit()
        self.db.refresh(leitor)
        
        logger.info(f"Leitor QR Code criado: {leitor.codigo_equipamento} por usuário {usuario_id}")
        return leitor
    
    def get_leitor_qr(self, leitor_id: int) -> Optional[LeitorQRCode]:
        """Busca um leitor QR Code por ID"""
        return self.db.query(LeitorQRCode).filter(LeitorQRCode.id == leitor_id).first()
    
    def get_leitores_qr(
        self, 
        evento_id: Optional[int] = None,
        status: Optional[str] = None,
        tipo_leitor: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LeitorQRCode]:
        """Lista leitores QR Code com filtros"""
        query = self.db.query(LeitorQRCode)
        
        if evento_id:
            query = query.filter(LeitorQRCode.evento_id == evento_id)
        if status:
            query = query.filter(LeitorQRCode.status == status)
        if tipo_leitor:
            query = query.filter(LeitorQRCode.tipo_leitor == tipo_leitor)
        
        return query.offset(skip).limit(limit).all()
    
    def update_leitor_qr(
        self, 
        leitor_id: int, 
        leitor_data: LeitorQRCodeUpdate
    ) -> Optional[LeitorQRCode]:
        """Atualiza um leitor QR Code"""
        leitor = self.get_leitor_qr(leitor_id)
        if not leitor:
            return None
        
        update_data = leitor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(leitor, field, value)
        
        self.db.commit()
        self.db.refresh(leitor)
        
        logger.info(f"Leitor QR Code atualizado: {leitor.codigo_equipamento}")
        return leitor
    
    def delete_leitor_qr(self, leitor_id: int) -> bool:
        """Remove um leitor QR Code"""
        leitor = self.get_leitor_qr(leitor_id)
        if not leitor:
            return False
        
        self.db.delete(leitor)
        self.db.commit()
        
        logger.info(f"Leitor QR Code removido: {leitor.codigo_equipamento}")
        return True
    
    # ==================== PONTOS DE ACESSO ====================
    
    def create_ponto_acesso(
        self, 
        ponto_data: PontoAcessoCreate, 
        usuario_id: int
    ) -> PontoAcesso:
        """Cria um novo ponto de acesso"""
        # Verificar se código já existe
        existing = self.db.query(PontoAcesso).filter(
            PontoAcesso.codigo == ponto_data.codigo
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Código de ponto de acesso '{ponto_data.codigo}' já existe"
            )
        
        ponto = PontoAcesso(**ponto_data.dict())
        
        self.db.add(ponto)
        self.db.commit()
        self.db.refresh(ponto)
        
        logger.info(f"Ponto de acesso criado: {ponto.codigo} por usuário {usuario_id}")
        return ponto
    
    def get_ponto_acesso(self, ponto_id: int) -> Optional[PontoAcesso]:
        """Busca um ponto de acesso por ID"""
        return self.db.query(PontoAcesso).filter(PontoAcesso.id == ponto_id).first()
    
    def get_pontos_acesso(
        self, 
        evento_id: Optional[int] = None,
        ativo: Optional[bool] = None,
        tipo_ponto: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PontoAcesso]:
        """Lista pontos de acesso com filtros"""
        query = self.db.query(PontoAcesso)
        
        if evento_id:
            query = query.filter(PontoAcesso.evento_id == evento_id)
        if ativo is not None:
            query = query.filter(PontoAcesso.ativo == ativo)
        if tipo_ponto:
            query = query.filter(PontoAcesso.tipo_ponto == tipo_ponto)
        
        return query.offset(skip).limit(limit).all()
    
    def update_ponto_acesso(
        self, 
        ponto_id: int, 
        ponto_data: PontoAcessoUpdate
    ) -> Optional[PontoAcesso]:
        """Atualiza um ponto de acesso"""
        ponto = self.get_ponto_acesso(ponto_id)
        if not ponto:
            return None
        
        update_data = ponto_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ponto, field, value)
        
        self.db.commit()
        self.db.refresh(ponto)
        
        logger.info(f"Ponto de acesso atualizado: {ponto.codigo}")
        return ponto
    
    # ==================== LEITURAS QR ====================
    
    def registrar_leitura_qr(
        self, 
        leitura_data: HistoricoLeituraQRCreate
    ) -> HistoricoLeituraQR:
        """Registra uma nova leitura de QR Code"""
        leitura = HistoricoLeituraQR(**leitura_data.dict())
        
        self.db.add(leitura)
        
        # Atualizar estatísticas do leitor
        leitor = self.get_leitor_qr(leitura_data.leitor_id)
        if leitor:
            leitor.total_leituras += 1
            leitor.ultimo_heartbeat = datetime.now()
            
            if leitura_data.valido:
                leitor.leituras_sucesso += 1
            else:
                leitor.leituras_erro += 1
            
            # Atualizar tempo médio de leitura
            if leitura_data.tempo_leitura:
                total_tempo = (leitor.tempo_medio_leitura * (leitor.total_leituras - 1) + 
                             leitura_data.tempo_leitura)
                leitor.tempo_medio_leitura = total_tempo / leitor.total_leituras
        
        self.db.commit()
        self.db.refresh(leitura)
        
        logger.info(f"Leitura QR registrada: leitor {leitura_data.leitor_id}")
        return leitura
    
    def get_historico_leituras(
        self, 
        leitor_id: Optional[int] = None,
        ponto_acesso_id: Optional[int] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        apenas_validas: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[HistoricoLeituraQR]:
        """Busca histórico de leituras com filtros"""
        query = self.db.query(HistoricoLeituraQR)
        
        if leitor_id:
            query = query.filter(HistoricoLeituraQR.leitor_id == leitor_id)
        if ponto_acesso_id:
            query = query.filter(HistoricoLeituraQR.ponto_acesso_id == ponto_acesso_id)
        if data_inicio:
            query = query.filter(HistoricoLeituraQR.timestamp_leitura >= data_inicio)
        if data_fim:
            query = query.filter(HistoricoLeituraQR.timestamp_leitura <= data_fim)
        if apenas_validas is not None:
            query = query.filter(HistoricoLeituraQR.valido == apenas_validas)
        
        return query.order_by(desc(HistoricoLeituraQR.timestamp_leitura)).offset(skip).limit(limit).all()
    
    # ==================== MOVIMENTAÇÕES ====================
    
    def registrar_movimentacao(
        self, 
        movimentacao_data: MovimentacaoAcessoCreate
    ) -> MovimentacaoAcesso:
        """Registra uma movimentação de entrada/saída"""
        movimentacao = MovimentacaoAcesso(**movimentacao_data.dict())
        
        self.db.add(movimentacao)
        
        # Atualizar contadores do ponto de acesso
        ponto = self.get_ponto_acesso(movimentacao_data.ponto_acesso_id)
        if ponto:
            if movimentacao_data.tipo_movimento == "entrada":
                ponto.total_entradas += 1
                ponto.contagem_atual += 1
            elif movimentacao_data.tipo_movimento == "saida":
                ponto.total_saidas += 1
                ponto.contagem_atual = max(0, ponto.contagem_atual - 1)
            
            # Verificar alertas de capacidade
            if (ponto.alerta_capacidade and ponto.capacidade_maxima and 
                ponto.contagem_atual >= (ponto.capacidade_maxima * ponto.percentual_alerta / 100)):
                logger.warning(
                    f"Alerta de capacidade no ponto {ponto.nome}: "
                    f"{ponto.contagem_atual}/{ponto.capacidade_maxima}"
                )
        
        self.db.commit()
        self.db.refresh(movimentacao)
        
        logger.info(
            f"Movimentação registrada: {movimentacao_data.tipo_movimento} "
            f"- {movimentacao_data.cpf_participante} no ponto {movimentacao_data.ponto_acesso_id}"
        )
        return movimentacao
    
    # ==================== CONFIGURAÇÕES ====================
    
    def create_configuracao(
        self, 
        config_data: ConfiguracaoEquipamentoCreate,
        usuario_id: int
    ) -> ConfiguracaoEquipamento:
        """Cria uma nova configuração de equipamento"""
        config = ConfiguracaoEquipamento(
            **config_data.dict(),
            criado_por=usuario_id
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        logger.info(f"Configuração criada: {config.nome_configuracao} por usuário {usuario_id}")
        return config
    
    def aplicar_configuracao_lote(
        self, 
        equipamentos_ids: List[int],
        configuracao_id: int
    ) -> Dict[str, Any]:
        """Aplica uma configuração a múltiplos equipamentos"""
        configuracao = self.db.query(ConfiguracaoEquipamento).filter(
            ConfiguracaoEquipamento.id == configuracao_id
        ).first()
        
        if not configuracao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada"
            )
        
        sucessos = 0
        falhas = 0
        detalhes = []
        
        for equip_id in equipamentos_ids:
            try:
                if configuracao.tipo_equipamento == "leitor_qr":
                    leitor = self.get_leitor_qr(equip_id)
                    if leitor:
                        # Aplicar configuração específica do leitor
                        params = json.loads(configuracao.parametros_json) if configuracao.parametros_json else {}
                        
                        # Exemplo de aplicação de configuração
                        if "sensibilidade" in params:
                            leitor.sensibilidade = params["sensibilidade"]
                        if "timeout_leitura" in params:
                            leitor.timeout_leitura = params["timeout_leitura"]
                        
                        self.db.commit()
                        sucessos += 1
                        detalhes.append({
                            "equipamento_id": equip_id,
                            "status": "sucesso",
                            "mensagem": "Configuração aplicada"
                        })
                    else:
                        falhas += 1
                        detalhes.append({
                            "equipamento_id": equip_id,
                            "status": "falha",
                            "mensagem": "Equipamento não encontrado"
                        })
                        
            except Exception as e:
                falhas += 1
                detalhes.append({
                    "equipamento_id": equip_id,
                    "status": "erro",
                    "mensagem": str(e)
                })
        
        return {
            "total_equipamentos": len(equipamentos_ids),
            "sucessos": sucessos,
            "falhas": falhas,
            "detalhes": detalhes
        }
    
    # ==================== ESTATÍSTICAS E RELATÓRIOS ====================
    
    def get_estatisticas_leitor(self, leitor_id: int) -> Optional[EstatisticasLeitorQR]:
        """Gera estatísticas de um leitor específico"""
        leitor = self.get_leitor_qr(leitor_id)
        if not leitor:
            return None
        
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)
        
        # Consultas de estatísticas
        leituras_hoje = self.db.query(func.count(HistoricoLeituraQR.id)).filter(
            and_(
                HistoricoLeituraQR.leitor_id == leitor_id,
                func.date(HistoricoLeituraQR.timestamp_leitura) == hoje
            )
        ).scalar()
        
        leituras_semana = self.db.query(func.count(HistoricoLeituraQR.id)).filter(
            and_(
                HistoricoLeituraQR.leitor_id == leitor_id,
                func.date(HistoricoLeituraQR.timestamp_leitura) >= inicio_semana
            )
        ).scalar()
        
        leituras_mes = self.db.query(func.count(HistoricoLeituraQR.id)).filter(
            and_(
                HistoricoLeituraQR.leitor_id == leitor_id,
                func.date(HistoricoLeituraQR.timestamp_leitura) >= inicio_mes
            )
        ).scalar()
        
        taxa_sucesso = 0.0
        if leitor.total_leituras > 0:
            taxa_sucesso = (leitor.leituras_sucesso / leitor.total_leituras) * 100
        
        return EstatisticasLeitorQR(
            leitor_id=leitor.id,
            nome_leitor=leitor.nome,
            total_leituras_hoje=leituras_hoje or 0,
            total_leituras_semana=leituras_semana or 0,
            total_leituras_mes=leituras_mes or 0,
            taxa_sucesso=round(taxa_sucesso, 2),
            tempo_medio_leitura=leitor.tempo_medio_leitura,
            ultimo_status=leitor.status,
            ultima_atividade=leitor.ultimo_heartbeat
        )
    
    def get_estatisticas_ponto_acesso(self, ponto_id: int) -> Optional[EstatisticasPontoAcesso]:
        """Gera estatísticas de um ponto de acesso específico"""
        ponto = self.get_ponto_acesso(ponto_id)
        if not ponto:
            return None
        
        hoje = datetime.now().date()
        
        # Movimentações de hoje
        movimentacoes_hoje = self.db.query(MovimentacaoAcesso).filter(
            and_(
                MovimentacaoAcesso.ponto_acesso_id == ponto_id,
                func.date(MovimentacaoAcesso.data_hora) == hoje
            )
        ).all()
        
        entradas_hoje = len([m for m in movimentacoes_hoje if m.tipo_movimento == "entrada"])
        saidas_hoje = len([m for m in movimentacoes_hoje if m.tipo_movimento == "saida"])
        
        # Calcular pico do dia
        pico_ocupacao = 0
        horario_pico = None
        
        # Esta é uma implementação simplificada
        # Em produção, seria necessário um algoritmo mais sofisticado
        ocupacao_por_hora = {}
        for mov in movimentacoes_hoje:
            hora = mov.data_hora.hour
            if hora not in ocupacao_por_hora:
                ocupacao_por_hora[hora] = 0
            
            if mov.tipo_movimento == "entrada":
                ocupacao_por_hora[hora] += 1
            else:
                ocupacao_por_hora[hora] -= 1
        
        if ocupacao_por_hora:
            max_hora = max(ocupacao_por_hora.keys(), key=lambda x: ocupacao_por_hora[x])
            pico_ocupacao = ocupacao_por_hora[max_hora]
            horario_pico = f"{max_hora:02d}:00"
        
        percentual_ocupacao = 0.0
        if ponto.capacidade_maxima and ponto.capacidade_maxima > 0:
            percentual_ocupacao = (ponto.contagem_atual / ponto.capacidade_maxima) * 100
        
        return EstatisticasPontoAcesso(
            ponto_id=ponto.id,
            nome_ponto=ponto.nome,
            total_entradas_hoje=entradas_hoje,
            total_saidas_hoje=saidas_hoje,
            ocupacao_atual=ponto.contagem_atual,
            capacidade_maxima=ponto.capacidade_maxima or 0,
            percentual_ocupacao=round(percentual_ocupacao, 2),
            pico_ocupacao_dia=max(pico_ocupacao, 0),
            horario_pico=horario_pico
        )
    
    def get_status_sistema(self) -> StatusSistemaEquipamentos:
        """Retorna status geral do sistema de equipamentos"""
        total_leitores = self.db.query(func.count(LeitorQRCode.id)).scalar()
        leitores_ativos = self.db.query(func.count(LeitorQRCode.id)).filter(
            LeitorQRCode.status == "ativo"
        ).scalar()
        leitores_inativos = self.db.query(func.count(LeitorQRCode.id)).filter(
            LeitorQRCode.status == "inativo"
        ).scalar()
        leitores_manutencao = self.db.query(func.count(LeitorQRCode.id)).filter(
            LeitorQRCode.status == "manutencao"
        ).scalar()
        
        total_pontos = self.db.query(func.count(PontoAcesso.id)).scalar()
        pontos_ativos = self.db.query(func.count(PontoAcesso.id)).filter(
            PontoAcesso.ativo == True
        ).scalar()
        
        ocupacao_total = self.db.query(func.sum(PontoAcesso.contagem_atual)).scalar()
        
        # Alertas de capacidade
        alertas_capacidade = self.db.query(func.count(PontoAcesso.id)).filter(
            and_(
                PontoAcesso.alerta_capacidade == True,
                PontoAcesso.capacidade_maxima > 0,
                PontoAcesso.contagem_atual >= (
                    PontoAcesso.capacidade_maxima * PontoAcesso.percentual_alerta / 100
                )
            )
        ).scalar()
        
        return StatusSistemaEquipamentos(
            total_leitores=total_leitores or 0,
            leitores_ativos=leitores_ativos or 0,
            leitores_inativos=leitores_inativos or 0,
            leitores_manutencao=leitores_manutencao or 0,
            total_pontos_acesso=total_pontos or 0,
            pontos_ativos=pontos_ativos or 0,
            ocupacao_total=ocupacao_total or 0,
            alertas_capacidade=alertas_capacidade or 0,
            ultima_verificacao=datetime.now()
        )
    
    # ==================== VALIDAÇÃO E PROCESSAMENTO ====================
    
    def validar_qr_code(self, codigo: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Valida um código QR lido e retorna resultado da validação"""
        try:
            # Esta é uma implementação básica
            # Em produção, incluiria validações específicas por tipo de código
            
            resultado = {
                "valido": False,
                "tipo_validacao": "desconhecido",
                "resultado_validacao": "negado",
                "motivo_rejeicao": "Formato não reconhecido",
                "dados_extraidos": {}
            }
            
            # Exemplo de validação para diferentes tipos de código
            if codigo.startswith("ING-"):  # Ingresso
                resultado.update({
                    "valido": True,
                    "tipo_validacao": "ingresso",
                    "resultado_validacao": "aprovado",
                    "motivo_rejeicao": None,
                    "dados_extraidos": {"ingresso_id": codigo[4:]}
                })
            elif codigo.startswith("CRED-"):  # Credencial
                resultado.update({
                    "valido": True,
                    "tipo_validacao": "credencial",
                    "resultado_validacao": "aprovado",
                    "motivo_rejeicao": None,
                    "dados_extraidos": {"credencial_id": codigo[5:]}
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na validação do QR Code: {e}")
            return {
                "valido": False,
                "tipo_validacao": "erro",
                "resultado_validacao": "erro",
                "motivo_rejeicao": f"Erro interno: {str(e)}",
                "dados_extraidos": {}
            }
    
    # ==================== MONITORAMENTO E ALERTAS ====================
    
    async def monitorar_equipamentos(self):
        """Monitora status dos equipamentos (executa em background)"""
        while True:
            try:
                # Verificar heartbeat dos leitores
                timeout_limite = datetime.now() - timedelta(minutes=5)
                
                leitores_timeout = self.db.query(LeitorQRCode).filter(
                    and_(
                        LeitorQRCode.status == "ativo",
                        or_(
                            LeitorQRCode.ultimo_heartbeat < timeout_limite,
                            LeitorQRCode.ultimo_heartbeat.is_(None)
                        )
                    )
                ).all()
                
                # Alterar status para "erro" em caso de timeout
                for leitor in leitores_timeout:
                    leitor.status = "erro"
                    logger.warning(f"Leitor {leitor.nome} sem heartbeat - status alterado para erro")
                
                self.db.commit()
                
                # Aguardar 1 minuto antes da próxima verificação
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de equipamentos: {e}")
                await asyncio.sleep(30)  # Esperar menos tempo em caso de erro