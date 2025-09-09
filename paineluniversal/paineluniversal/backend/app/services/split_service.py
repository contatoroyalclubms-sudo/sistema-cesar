"""
Service para Sistema de Split de Pagamentos
Gerencia cálculos, execuções e integrações com gateways
"""

from typing import List, Dict, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import json
import logging

from ..models_split import (
    SplitRule, SplitExecution, SplitAgregado,
    TipoCalculoSplit, TipoBeneficiario, StatusSplit,
    ConfiguracaoSplitGlobal, HistoricoSplit
)
from ..models import VendaPDV, ItemVendaPDV, Evento, Usuario

logger = logging.getLogger(__name__)


class SplitService:
    """Service principal para gerenciar splits de pagamento"""
    
    def __init__(self, db: Session):
        self.db = db
        self.gateways = self._initialize_gateways()
    
    def _initialize_gateways(self) -> Dict:
        """Inicializa os gateways de pagamento disponíveis"""
        return {
            'stripe': StripeGateway(),
            'pagseguro': PagSeguroGateway(),
            'mercadopago': MercadoPagoGateway(),
            'manual': ManualGateway()  # Para testes e processamento manual
        }
    
    # ==================== CÁLCULO DE SPLITS ====================
    
    def calcular_splits(self, venda_id: int) -> List[Dict]:
        """
        Calcula os splits para uma venda baseado nas regras configuradas
        """
        venda = self.db.query(VendaPDV).filter(VendaPDV.id == venda_id).first()
        if not venda:
            raise ValueError(f"Venda {venda_id} não encontrada")
        
        # Buscar regras aplicáveis
        regras = self._buscar_regras_aplicaveis(venda)
        
        # Calcular splits
        splits = []
        valor_restante = Decimal(str(venda.total))
        valor_total_splits = Decimal('0')
        
        for regra in regras:
            if self._verificar_condicoes(regra, venda):
                split_calculado = self._calcular_valor_split(regra, venda, valor_restante)
                
                if split_calculado['valor'] > 0:
                    splits.append(split_calculado)
                    valor_total_splits += split_calculado['valor']
                    
                    # Se for percentual, não deduzir do valor restante
                    if regra.tipo_calculo != TipoCalculoSplit.PERCENTUAL:
                        valor_restante -= split_calculado['valor']
        
        # Adicionar split para o organizador (valor restante)
        if valor_restante > 0 and valor_total_splits < venda.total:
            valor_organizador = venda.total - valor_total_splits
            splits.append({
                'rule_id': None,
                'beneficiario_tipo': TipoBeneficiario.EMPRESA.value,
                'beneficiario_id': str(venda.evento.empresa_id),
                'beneficiario_nome': 'Organizador do Evento',
                'valor': float(valor_organizador),
                'tipo_calculo': 'residual',
                'prioridade': 999
            })
        
        return splits
    
    def _buscar_regras_aplicaveis(self, venda: VendaPDV) -> List[SplitRule]:
        """Busca regras de split aplicáveis para a venda"""
        query = self.db.query(SplitRule).filter(
            SplitRule.ativo == True,
            or_(
                SplitRule.evento_id == venda.evento_id,
                SplitRule.empresa_id == venda.evento.empresa_id
            )
        )
        
        # Filtrar por data de vigência
        hoje = datetime.now()
        query = query.filter(
            or_(
                SplitRule.data_inicio == None,
                SplitRule.data_inicio <= hoje
            ),
            or_(
                SplitRule.data_fim == None,
                SplitRule.data_fim >= hoje
            )
        )
        
        # Ordenar por prioridade
        return query.order_by(SplitRule.prioridade.asc()).all()
    
    def _verificar_condicoes(self, regra: SplitRule, venda: VendaPDV) -> bool:
        """Verifica se as condições da regra são atendidas"""
        if not regra.condicoes:
            return True
        
        condicoes = regra.condicoes
        
        # Verificar valor mínimo/máximo
        if 'min_valor' in condicoes and venda.total < condicoes['min_valor']:
            return False
        if 'max_valor' in condicoes and venda.total > condicoes['max_valor']:
            return False
        
        # Verificar produtos
        if 'produto_ids' in condicoes:
            produtos_venda = [item.produto_id for item in venda.itens]
            if not any(pid in condicoes['produto_ids'] for pid in produtos_venda):
                return False
        
        # Verificar categorias
        if 'categoria_ids' in condicoes:
            categorias_venda = [item.produto.categoria_id for item in venda.itens]
            if not any(cid in condicoes['categoria_ids'] for cid in categorias_venda):
                return False
        
        # Verificar dia da semana
        if 'dias_semana' in condicoes:
            dia_atual = venda.data_venda.weekday()
            if dia_atual not in condicoes['dias_semana']:
                return False
        
        # Verificar horário
        if 'horario_inicio' in condicoes or 'horario_fim' in condicoes:
            hora_venda = venda.data_venda.time()
            
            if 'horario_inicio' in condicoes:
                hora_inicio = datetime.strptime(condicoes['horario_inicio'], '%H:%M').time()
                if hora_venda < hora_inicio:
                    return False
            
            if 'horario_fim' in condicoes:
                hora_fim = datetime.strptime(condicoes['horario_fim'], '%H:%M').time()
                if hora_venda > hora_fim:
                    return False
        
        return True
    
    def _calcular_valor_split(self, regra: SplitRule, venda: VendaPDV, valor_base: Decimal) -> Dict:
        """Calcula o valor do split baseado na regra"""
        valor_split = Decimal('0')
        
        if regra.tipo_calculo == TipoCalculoSplit.PERCENTUAL:
            valor_split = (venda.total * regra.valor) / 100
            
        elif regra.tipo_calculo == TipoCalculoSplit.VALOR_FIXO:
            valor_split = min(regra.valor, valor_base)
            
        elif regra.tipo_calculo == TipoCalculoSplit.VALOR_POR_ITEM:
            quantidade_itens = sum(item.quantidade for item in venda.itens)
            valor_split = regra.valor * quantidade_itens
            valor_split = min(valor_split, valor_base)
        
        # Aplicar limites
        if regra.valor_minimo and valor_split < regra.valor_minimo:
            valor_split = Decimal('0')  # Não executar se abaixo do mínimo
        
        if regra.valor_maximo and valor_split > regra.valor_maximo:
            valor_split = regra.valor_maximo
        
        return {
            'rule_id': regra.id,
            'beneficiario_tipo': regra.beneficiario_tipo.value,
            'beneficiario_id': regra.beneficiario_id,
            'beneficiario_nome': regra.beneficiario_nome,
            'dados_pagamento': regra.dados_pagamento,
            'valor': float(valor_split),
            'tipo_calculo': regra.tipo_calculo.value,
            'prioridade': regra.prioridade
        }
    
    # ==================== EXECUÇÃO DE SPLITS ====================
    
    def executar_splits(self, venda_id: int, splits: List[Dict] = None) -> List[SplitExecution]:
        """
        Executa os splits calculados ou recalcula se não fornecidos
        """
        if not splits:
            splits = self.calcular_splits(venda_id)
        
        venda = self.db.query(VendaPDV).filter(VendaPDV.id == venda_id).first()
        execucoes = []
        
        for split in splits:
            execucao = self._criar_execucao_split(venda, split)
            self.db.add(execucao)
            execucoes.append(execucao)
        
        self.db.commit()
        
        # Processar pagamentos se configurado
        config = self._get_configuracao_global(venda.evento.empresa_id)
        if config and config.processar_automaticamente:
            self.processar_pagamentos_splits(execucoes)
        
        return execucoes
    
    def _criar_execucao_split(self, venda: VendaPDV, split: Dict) -> SplitExecution:
        """Cria uma execução de split"""
        execucao = SplitExecution(
            venda_id=venda.id,
            rule_id=split.get('rule_id'),
            valor_venda=venda.total,
            valor_base_calculo=venda.total,
            valor_split=split['valor'],
            valor_liquido=split['valor'],  # Será ajustado após processar taxas
            beneficiario_tipo=split['beneficiario_tipo'],
            beneficiario_id=split['beneficiario_id'],
            beneficiario_nome=split['beneficiario_nome'],
            dados_pagamento=split.get('dados_pagamento', {}),
            status=StatusSplit.PENDENTE
        )
        
        # Registrar no histórico
        self._registrar_historico(
            execution_id=None,
            rule_id=split.get('rule_id'),
            acao='execucao_split',
            descricao=f"Split criado para venda #{venda.id}",
            dados_acao=split
        )
        
        return execucao
    
    def processar_pagamentos_splits(self, execucoes: List[SplitExecution]):
        """Processa os pagamentos dos splits via gateway"""
        config = self._get_configuracao_global(execucoes[0].venda.evento.empresa_id)
        gateway = self.gateways.get(config.gateway_padrao, self.gateways['manual'])
        
        for execucao in execucoes:
            try:
                # Processar pagamento via gateway
                resultado = gateway.processar_pagamento(
                    valor=execucao.valor_liquido,
                    beneficiario=execucao.dados_pagamento,
                    referencia=f"SPLIT-{execucao.id}"
                )
                
                # Atualizar execução
                execucao.status = StatusSplit.PAGO if resultado['sucesso'] else StatusSplit.ERRO
                execucao.gateway_usado = config.gateway_padrao
                execucao.gateway_transaction_id = resultado.get('transaction_id')
                execucao.gateway_response = resultado
                execucao.data_processamento = datetime.now()
                
                if resultado['sucesso']:
                    execucao.data_pagamento = datetime.now()
                    execucao.valor_taxa = resultado.get('taxa', 0)
                    execucao.valor_liquido = execucao.valor_split - execucao.valor_taxa
                else:
                    execucao.erro_mensagem = resultado.get('erro')
                    execucao.data_erro = datetime.now()
                
                self.db.commit()
                
                # Registrar no histórico
                self._registrar_historico(
                    execution_id=execucao.id,
                    acao='pagamento' if resultado['sucesso'] else 'erro',
                    descricao=f"Pagamento {'realizado' if resultado['sucesso'] else 'falhou'}",
                    dados_acao=resultado
                )
                
            except Exception as e:
                logger.error(f"Erro ao processar split {execucao.id}: {str(e)}")
                execucao.status = StatusSplit.ERRO
                execucao.erro_mensagem = str(e)
                execucao.tentativas += 1
                self.db.commit()
    
    # ==================== RELATÓRIOS E AGREGAÇÕES ====================
    
    def gerar_relatorio_splits(
        self, 
        evento_id: Optional[int] = None,
        beneficiario_id: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> Dict:
        """Gera relatório detalhado de splits"""
        query = self.db.query(SplitExecution)
        
        if evento_id:
            query = query.join(VendaPDV).filter(VendaPDV.evento_id == evento_id)
        
        if beneficiario_id:
            query = query.filter(SplitExecution.beneficiario_id == beneficiario_id)
        
        if data_inicio:
            query = query.filter(SplitExecution.data_execucao >= data_inicio)
        
        if data_fim:
            query = query.filter(SplitExecution.data_execucao <= data_fim)
        
        execucoes = query.all()
        
        # Calcular totais
        total_bruto = sum(e.valor_split for e in execucoes)
        total_taxas = sum(e.valor_taxa for e in execucoes)
        total_liquido = sum(e.valor_liquido for e in execucoes)
        
        # Agrupar por status
        por_status = {}
        for status in StatusSplit:
            splits_status = [e for e in execucoes if e.status == status]
            por_status[status.value] = {
                'quantidade': len(splits_status),
                'valor': sum(e.valor_split for e in splits_status)
            }
        
        # Agrupar por beneficiário
        por_beneficiario = {}
        for execucao in execucoes:
            key = f"{execucao.beneficiario_tipo.value}:{execucao.beneficiario_id}"
            if key not in por_beneficiario:
                por_beneficiario[key] = {
                    'nome': execucao.beneficiario_nome,
                    'tipo': execucao.beneficiario_tipo.value,
                    'quantidade': 0,
                    'valor_bruto': 0,
                    'valor_liquido': 0
                }
            
            por_beneficiario[key]['quantidade'] += 1
            por_beneficiario[key]['valor_bruto'] += float(execucao.valor_split)
            por_beneficiario[key]['valor_liquido'] += float(execucao.valor_liquido)
        
        return {
            'periodo': {
                'inicio': data_inicio.isoformat() if data_inicio else None,
                'fim': data_fim.isoformat() if data_fim else None
            },
            'totais': {
                'quantidade': len(execucoes),
                'valor_bruto': float(total_bruto),
                'valor_taxas': float(total_taxas),
                'valor_liquido': float(total_liquido)
            },
            'por_status': por_status,
            'por_beneficiario': list(por_beneficiario.values()),
            'execucoes': [self._serializar_execucao(e) for e in execucoes[:100]]  # Limitar a 100
        }
    
    def agregar_splits_periodo(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        evento_id: Optional[int] = None
    ):
        """Agrega splits por período para otimizar relatórios"""
        query = self.db.query(SplitExecution).filter(
            SplitExecution.data_execucao >= data_inicio,
            SplitExecution.data_execucao <= data_fim
        )
        
        if evento_id:
            query = query.join(VendaPDV).filter(VendaPDV.evento_id == evento_id)
        
        execucoes = query.all()
        
        # Agrupar por beneficiário
        agregados = {}
        for execucao in execucoes:
            key = f"{execucao.beneficiario_tipo.value}:{execucao.beneficiario_id}"
            
            if key not in agregados:
                agregados[key] = SplitAgregado(
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    beneficiario_tipo=execucao.beneficiario_tipo,
                    beneficiario_id=execucao.beneficiario_id,
                    beneficiario_nome=execucao.beneficiario_nome,
                    evento_id=evento_id,
                    empresa_id=execucao.venda.evento.empresa_id
                )
            
            agregado = agregados[key]
            agregado.quantidade_splits += 1
            agregado.valor_total_bruto += execucao.valor_split
            agregado.valor_total_taxas += execucao.valor_taxa
            agregado.valor_total_liquido += execucao.valor_liquido
            
            if execucao.status == StatusSplit.PAGO:
                agregado.quantidade_pagos += 1
            elif execucao.status == StatusSplit.PENDENTE:
                agregado.quantidade_pendentes += 1
            elif execucao.status == StatusSplit.ERRO:
                agregado.quantidade_erros += 1
        
        # Salvar agregações
        for agregado in agregados.values():
            self.db.add(agregado)
        
        self.db.commit()
    
    # ==================== UTILITÁRIOS ====================
    
    def _get_configuracao_global(self, empresa_id: int) -> Optional[ConfiguracaoSplitGlobal]:
        """Obtém configuração global de split da empresa"""
        return self.db.query(ConfiguracaoSplitGlobal).filter(
            ConfiguracaoSplitGlobal.empresa_id == empresa_id
        ).first()
    
    def _registrar_historico(
        self,
        execution_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        acao: str = '',
        descricao: str = '',
        dados_acao: Dict = None,
        usuario_id: Optional[int] = None
    ):
        """Registra ação no histórico para auditoria"""
        historico = HistoricoSplit(
            execution_id=execution_id,
            rule_id=rule_id,
            acao=acao,
            descricao=descricao,
            dados_acao=dados_acao or {},
            usuario_id=usuario_id
        )
        self.db.add(historico)
    
    def _serializar_execucao(self, execucao: SplitExecution) -> Dict:
        """Serializa execução para JSON"""
        return {
            'id': execucao.id,
            'venda_id': execucao.venda_id,
            'beneficiario': {
                'tipo': execucao.beneficiario_tipo.value,
                'id': execucao.beneficiario_id,
                'nome': execucao.beneficiario_nome
            },
            'valores': {
                'split': float(execucao.valor_split),
                'taxa': float(execucao.valor_taxa),
                'liquido': float(execucao.valor_liquido)
            },
            'status': execucao.status.value,
            'gateway': execucao.gateway_usado,
            'data_execucao': execucao.data_execucao.isoformat() if execucao.data_execucao else None,
            'data_pagamento': execucao.data_pagamento.isoformat() if execucao.data_pagamento else None
        }


# ==================== GATEWAYS DE PAGAMENTO ====================

class BaseGateway:
    """Interface base para gateways de pagamento"""
    
    def processar_pagamento(self, valor: float, beneficiario: Dict, referencia: str) -> Dict:
        raise NotImplementedError


class StripeGateway(BaseGateway):
    """Gateway para Stripe"""
    
    def processar_pagamento(self, valor: float, beneficiario: Dict, referencia: str) -> Dict:
        # TODO: Implementar integração real com Stripe
        # Por enquanto, simular sucesso
        import random
        sucesso = random.random() > 0.1  # 90% de sucesso
        
        return {
            'sucesso': sucesso,
            'transaction_id': f"stripe_{referencia}_{datetime.now().timestamp()}",
            'taxa': valor * 0.029,  # 2.9% de taxa
            'erro': None if sucesso else "Pagamento recusado pelo gateway"
        }


class PagSeguroGateway(BaseGateway):
    """Gateway para PagSeguro"""
    
    def processar_pagamento(self, valor: float, beneficiario: Dict, referencia: str) -> Dict:
        # TODO: Implementar integração real com PagSeguro
        return {
            'sucesso': True,
            'transaction_id': f"pagseguro_{referencia}_{datetime.now().timestamp()}",
            'taxa': valor * 0.0399,  # 3.99% de taxa
            'erro': None
        }


class MercadoPagoGateway(BaseGateway):
    """Gateway para MercadoPago"""
    
    def processar_pagamento(self, valor: float, beneficiario: Dict, referencia: str) -> Dict:
        # TODO: Implementar integração real com MercadoPago
        return {
            'sucesso': True,
            'transaction_id': f"mp_{referencia}_{datetime.now().timestamp()}",
            'taxa': valor * 0.0499,  # 4.99% de taxa
            'erro': None
        }


class ManualGateway(BaseGateway):
    """Gateway manual para testes e processamento offline"""
    
    def processar_pagamento(self, valor: float, beneficiario: Dict, referencia: str) -> Dict:
        return {
            'sucesso': True,
            'transaction_id': f"manual_{referencia}",
            'taxa': 0,
            'erro': None,
            'observacao': "Processamento manual - aguardando confirmação"
        }