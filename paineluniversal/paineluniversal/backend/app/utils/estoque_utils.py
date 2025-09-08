"""
Utilities para Sistema de Estoque - Versão Simplificada
Funções auxiliares e lógicas de negócio para controle de inventário
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta, date, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
import uuid

from ..models import Produto, Usuario
from ..models_inventario import (
    EstoqueProduto, LocalEstoque, MovimentacaoEstoque, TipoMovimentacaoEstoque,
    Fornecedor, OrdemCompra, ItemOrdemCompra, StatusOrdemCompra,
    InventarioFisico, ContagemInventario, StatusInventarioFisico,
    TransferenciaEstoque, ItemTransferencia, MetodoControleEstoque,
    RecebimentoMercadoria, ItemRecebimento, StatusRecebimento
)

class EstoqueService:
    """Serviço principal para operações de estoque"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obter_ou_criar_estoque(self, produto_id: int, local_id: int) -> EstoqueProduto:
        """Obter registro de estoque existente ou criar novo"""
        estoque = self.db.query(EstoqueProduto).filter(
            EstoqueProduto.produto_id == produto_id,
            EstoqueProduto.local_id == local_id
        ).first()
        
        if not estoque:
            estoque = EstoqueProduto(
                produto_id=produto_id,
                local_id=local_id,
                quantidade_atual=Decimal('0'),
                quantidade_reservada=Decimal('0'),
                quantidade_disponivel=Decimal('0'),
                custo_medio=Decimal('0'),
                ultimo_custo=Decimal('0')
            )
            self.db.add(estoque)
            self.db.flush()
        
        return estoque
    
    def movimentar_estoque(
        self,
        produto_id: int,
        local_id: int,
        tipo_movimentacao: TipoMovimentacaoEstoque,
        quantidade: Decimal,
        valor_unitario: Optional[Decimal] = None,
        usuario_id: Optional[int] = None,
        numero_documento: Optional[str] = None,
        observacoes: Optional[str] = None
    ) -> MovimentacaoEstoque:
        """Realizar movimentação de estoque com atualização automática"""
        
        estoque = self.obter_ou_criar_estoque(produto_id, local_id)
        saldo_anterior = estoque.quantidade_atual
        
        # Calcular novo saldo
        if "entrada" in tipo_movimentacao.value:
            novo_saldo = saldo_anterior + quantidade
        else:  # saída
            novo_saldo = saldo_anterior - quantidade
            if novo_saldo < 0:
                raise ValueError(f"Estoque insuficiente. Saldo atual: {saldo_anterior}, Tentativa de saída: {quantidade}")
        
        # Criar movimentação
        movimentacao = MovimentacaoEstoque(
            estoque_produto_id=estoque.id,
            produto_id=produto_id,
            local_destino_id=local_id if "entrada" in tipo_movimentacao.value else None,
            local_origem_id=local_id if "saida" in tipo_movimentacao.value else None,
            tipo_movimentacao=tipo_movimentacao,
            quantidade=quantidade,
            valor_unitario=valor_unitario,
            valor_total=valor_unitario * quantidade if valor_unitario else None,
            numero_documento=numero_documento,
            observacoes=observacoes,
            saldo_anterior=saldo_anterior,
            saldo_atual=novo_saldo,
            criado_por_id=usuario_id
        )
        
        # Atualizar estoque
        estoque.quantidade_atual = novo_saldo
        estoque.quantidade_disponivel = novo_saldo - estoque.quantidade_reservada
        
        # Atualizar custos para entradas
        if "entrada" in tipo_movimentacao.value and valor_unitario:
            self._atualizar_custo_estoque(estoque, quantidade, valor_unitario, saldo_anterior)
        
        self.db.add(movimentacao)
        self.db.commit()
        
        return movimentacao
    
    def _atualizar_custo_estoque(
        self, 
        estoque: EstoqueProduto, 
        quantidade_entrada: Decimal, 
        valor_unitario: Decimal,
        saldo_anterior: Decimal
    ):
        """Atualizar custo do estoque baseado no método de controle"""
        
        if estoque.metodo_controle == MetodoControleEstoque.CUSTO_MEDIO:
            # Custo médio ponderado
            if saldo_anterior > 0:
                valor_estoque_anterior = saldo_anterior * estoque.custo_medio
                valor_entrada = quantidade_entrada * valor_unitario
                novo_saldo = saldo_anterior + quantidade_entrada
                estoque.custo_medio = (valor_estoque_anterior + valor_entrada) / novo_saldo
            else:
                estoque.custo_medio = valor_unitario
        
        elif estoque.metodo_controle == MetodoControleEstoque.FIFO:
            # Para FIFO, mantemos o último custo para entradas
            estoque.ultimo_custo = valor_unitario
        
        elif estoque.metodo_controle == MetodoControleEstoque.LIFO:
            # Para LIFO, o último custo se torna o custo atual
            estoque.custo_medio = valor_unitario
        
        estoque.ultimo_custo = valor_unitario
    
    def reservar_estoque(self, produto_id: int, local_id: int, quantidade: Decimal) -> bool:
        """Reservar quantidade do estoque para venda"""
        estoque = self.obter_ou_criar_estoque(produto_id, local_id)
        
        if estoque.quantidade_disponivel >= quantidade:
            estoque.quantidade_reservada += quantidade
            estoque.quantidade_disponivel -= quantidade
            self.db.commit()
            return True
        
        return False
    
    def liberar_reserva(self, produto_id: int, local_id: int, quantidade: Decimal):
        """Liberar reserva de estoque"""
        estoque = self.obter_ou_criar_estoque(produto_id, local_id)
        
        quantidade_liberada = min(estoque.quantidade_reservada, quantidade)
        estoque.quantidade_reservada -= quantidade_liberada
        estoque.quantidade_disponivel += quantidade_liberada
        self.db.commit()
    
    def calcular_giro_estoque(self, produto_id: int, local_id: int, periodo_dias: int = 30) -> Decimal:
        """Calcular giro do estoque para um produto"""
        
        data_inicio = datetime.now(timezone.utc) - timedelta(days=periodo_dias)
        
        # Quantidade vendida no período
        vendas = self.db.query(func.sum(MovimentacaoEstoque.quantidade)).filter(
            MovimentacaoEstoque.produto_id == produto_id,
            MovimentacaoEstoque.local_origem_id == local_id,
            MovimentacaoEstoque.tipo_movimentacao.like('%saida_venda%'),
            MovimentacaoEstoque.data_movimento >= data_inicio
        ).scalar() or Decimal('0')
        
        # Estoque atual
        estoque_atual = self.db.query(EstoqueProduto.quantidade_atual).filter(
            EstoqueProduto.produto_id == produto_id,
            EstoqueProduto.local_id == local_id
        ).scalar() or Decimal('0')
        
        if estoque_atual > 0:
            # Giro = Vendas / Estoque Médio (por mês)
            giro = (vendas / estoque_atual) * (30 / periodo_dias)
            return giro
        
        return Decimal('0')
    
    def calcular_cobertura_estoque(self, produto_id: int, local_id: int, periodo_dias: int = 30) -> int:
        """Calcular dias de cobertura do estoque"""
        
        data_inicio = datetime.now(timezone.utc) - timedelta(days=periodo_dias)
        
        # Consumo médio diário
        vendas = self.db.query(func.sum(MovimentacaoEstoque.quantidade)).filter(
            MovimentacaoEstoque.produto_id == produto_id,
            MovimentacaoEstoque.local_origem_id == local_id,
            MovimentacaoEstoque.tipo_movimentacao.like('%saida_venda%'),
            MovimentacaoEstoque.data_movimento >= data_inicio
        ).scalar() or Decimal('0')
        
        consumo_medio_diario = vendas / periodo_dias
        
        # Estoque atual
        estoque_atual = self.db.query(EstoqueProduto.quantidade_atual).filter(
            EstoqueProduto.produto_id == produto_id,
            EstoqueProduto.local_id == local_id
        ).scalar() or Decimal('0')
        
        if consumo_medio_diario > 0:
            cobertura = int(estoque_atual / consumo_medio_diario)
            return cobertura
        
        return 0
    
    def atualizar_estatisticas_estoque(self, produto_id: Optional[int] = None, local_id: Optional[int] = None):
        """Atualizar estatísticas de giro e cobertura"""
        
        query = self.db.query(EstoqueProduto)
        if produto_id:
            query = query.filter(EstoqueProduto.produto_id == produto_id)
        if local_id:
            query = query.filter(EstoqueProduto.local_id == local_id)
        
        estoques = query.all()
        
        for estoque in estoques:
            estoque.giro_estoque = self.calcular_giro_estoque(
                estoque.produto_id, 
                estoque.local_id
            )
            estoque.cobertura_dias = self.calcular_cobertura_estoque(
                estoque.produto_id, 
                estoque.local_id
            )
        
        self.db.commit()
    
    def gerar_sugestao_compra(self, local_id: int) -> List[Dict]:
        """Gerar sugestão de compra baseada em pontos de pedido"""
        
        query = self.db.query(EstoqueProduto, Produto).join(Produto).filter(
            EstoqueProduto.local_id == local_id,
            EstoqueProduto.quantidade_atual <= EstoqueProduto.ponto_pedido,
            EstoqueProduto.ponto_pedido > 0
        )
        
        sugestoes = []
        
        for estoque, produto in query.all():
            # Calcular quantidade sugerida
            quantidade_sugerida = estoque.estoque_maximo - estoque.quantidade_atual
            if quantidade_sugerida <= 0:
                quantidade_sugerida = estoque.estoque_minimo * 2  # 2x o mínimo como fallback
            
            sugestao = {
                "produto_id": produto.id,
                "produto_nome": produto.nome,
                "produto_codigo": produto.codigo,
                "quantidade_atual": float(estoque.quantidade_atual),
                "estoque_minimo": float(estoque.estoque_minimo),
                "ponto_pedido": float(estoque.ponto_pedido),
                "quantidade_sugerida": float(quantidade_sugerida),
                "ultimo_custo": float(estoque.ultimo_custo),
                "valor_total_sugerido": float(quantidade_sugerida * estoque.ultimo_custo),
                "giro_estoque": float(estoque.giro_estoque),
                "cobertura_dias": estoque.cobertura_dias
            }
            
            sugestoes.append(sugestao)
        
        return sorted(sugestoes, key=lambda x: x['valor_total_sugerido'], reverse=True)
    
    def obter_alertas_estoque(self, local_id: int) -> Dict[str, List[Dict]]:
        """Obter alertas de estoque (baixo, alto, zerado)"""
        
        estoques = self.db.query(EstoqueProduto, Produto).join(Produto).filter(
            EstoqueProduto.local_id == local_id
        ).all()
        
        alertas = {
            "estoque_baixo": [],
            "estoque_zerado": [],
            "estoque_alto": []
        }
        
        for estoque, produto in estoques:
            if estoque.quantidade_atual == 0:
                alertas["estoque_zerado"].append({
                    "produto_id": produto.id,
                    "produto_nome": produto.nome,
                    "quantidade_atual": float(estoque.quantidade_atual)
                })
            elif estoque.quantidade_atual <= estoque.estoque_minimo:
                alertas["estoque_baixo"].append({
                    "produto_id": produto.id,
                    "produto_nome": produto.nome,
                    "quantidade_atual": float(estoque.quantidade_atual),
                    "estoque_minimo": float(estoque.estoque_minimo)
                })
            elif estoque.quantidade_atual >= estoque.estoque_maximo:
                alertas["estoque_alto"].append({
                    "produto_id": produto.id,
                    "produto_nome": produto.nome,
                    "quantidade_atual": float(estoque.quantidade_atual),
                    "estoque_maximo": float(estoque.estoque_maximo)
                })
        
        return alertas

# ================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================

def gerar_numero_documento(prefixo: str) -> str:
    """Gerar número único para documentos"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefixo}-{timestamp}"

def validar_transferencia_locais(local_origem_id: int, local_destino_id: int) -> bool:
    """Validar se transferência entre locais é permitida"""
    if local_origem_id == local_destino_id:
        return False
    return True

def calcular_valor_total_estoque(estoques: List[EstoqueProduto]) -> Decimal:
    """Calcular valor total de uma lista de estoques"""
    valor_total = Decimal('0')
    for estoque in estoques:
        valor_item = estoque.quantidade_atual * estoque.custo_medio
        valor_total += valor_item
    return valor_total
