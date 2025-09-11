"""
Utilities para Sistema de Estoque
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
    
    # ================================================================================
    # GESTÃO DE ESTOQUE
    # ================================================================================
    
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
        observacoes: Optional[str] = None,
        ordem_compra_id: Optional[int] = None,
        venda_pdv_id: Optional[int] = None
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
            ordem_compra_id=ordem_compra_id,
            venda_pdv_id=venda_pdv_id,
            saldo_anterior=saldo_anterior,
            saldo_atual=novo_saldo,
            criado_por_id=usuario_id
        )
        
        # Atualizar estoque
        estoque.quantidade_atual = novo_saldo
        estoque.quantidade_disponivel = novo_saldo - estoque.quantidade_reservada
        estoque.ultima_movimentacao = datetime.now(timezone.utc)
        
        # Atualizar custos para entradas
        if "entrada" in tipo_movimentacao.value and valor_unitario:
            self._atualizar_custo_estoque(estoque, quantidade, valor_unitario, saldo_anterior)
            estoque.ultima_compra = datetime.now(timezone.utc)
        
        if "saida" in tipo_movimentacao.value:
            estoque.ultima_venda = datetime.now(timezone.utc)
        
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
            # O custo médio seria calculado baseado na ordem de entrada
        
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
    
    # ================================================================================
    # TRANSFERÊNCIAS
    # ================================================================================
    
    def criar_transferencia(
        self,
        empresa_id: int,
        local_origem_id: int,
        local_destino_id: int,
        itens: List[Dict],
        usuario_id: int,
        motivo: Optional[str] = None,
        observacoes: Optional[str] = None
    ) -> TransferenciaEstoque:
        """Criar transferência entre locais"""
        
        # Gerar número único
        numero = f"TRF-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        transferencia = TransferenciaEstoque(
            empresa_id=empresa_id,
            local_origem_id=local_origem_id,
            local_destino_id=local_destino_id,
            numero=numero,
            motivo=motivo,
            observacoes=observacoes,
            criado_por_id=usuario_id
        )
        
        self.db.add(transferencia)
        self.db.flush()
        
        # Criar itens da transferência
        for item_data in itens:
            item = ItemTransferencia(
                transferencia_id=transferencia.id,
                produto_id=item_data['produto_id'],
                quantidade_solicitada=item_data['quantidade'],
                observacoes=item_data.get('observacoes')
            )
            self.db.add(item)
        
        self.db.commit()
        return transferencia
    
    def executar_transferencia(self, transferencia_id: int, usuario_id: int) -> bool:
        """Executar transferência (baixa do origem)"""
        transferencia = self.db.query(TransferenciaEstoque).filter(
            TransferenciaEstoque.id == transferencia_id
        ).first()
        
        if not transferencia or transferencia.status != "pendente":
            return False
        
        # Baixar estoque do local de origem
        for item in transferencia.itens:
            try:
                # Verificar estoque disponível
                estoque_origem = self.obter_ou_criar_estoque(
                    item.produto_id, 
                    transferencia.local_origem_id
                )
                
                if estoque_origem.quantidade_disponivel < item.quantidade_solicitada:
                    raise ValueError(f"Estoque insuficiente para produto {item.produto_id}")
                
                # Movimentar saída do origem
                self.movimentar_estoque(
                    produto_id=item.produto_id,
                    local_id=transferencia.local_origem_id,
                    tipo_movimentacao=TipoMovimentacaoEstoque.SAIDA_TRANSFERENCIA,
                    quantidade=item.quantidade_solicitada,
                    valor_unitario=estoque_origem.custo_medio,
                    usuario_id=usuario_id,
                    numero_documento=transferencia.numero,
                    observacoes=f"Transferência para {transferencia.local_destino.nome}"
                )
                
                item.quantidade_enviada = item.quantidade_solicitada
                
            except Exception as e:
                self.db.rollback()
                raise e
        
        transferencia.status = "enviada"
        transferencia.data_envio = datetime.utcnow()
        transferencia.enviado_por_id = usuario_id
        
        self.db.commit()
        return True
    
    def receber_transferencia(self, transferencia_id: int, usuario_id: int, itens_recebidos: List[Dict]) -> bool:
        """Receber transferência (entrada no destino)"""
        transferencia = self.db.query(TransferenciaEstoque).filter(
            TransferenciaEstoque.id == transferencia_id
        ).first()
        
        if not transferencia or transferencia.status != "enviada":
            return False
        
        # Entrada no local de destino
        for item_recebido in itens_recebidos:
            item = next((i for i in transferencia.itens if i.produto_id == item_recebido['produto_id']), None)
            if not item:
                continue
            
            quantidade_recebida = Decimal(str(item_recebido['quantidade_recebida']))
            
            # Movimentar entrada no destino
            self.movimentar_estoque(
                produto_id=item.produto_id,
                local_id=transferencia.local_destino_id,
                tipo_movimentacao=TipoMovimentacaoEstoque.ENTRADA_TRANSFERENCIA,
                quantidade=quantidade_recebida,
                valor_unitario=item_recebido.get('valor_unitario'),
                usuario_id=usuario_id,
                numero_documento=transferencia.numero,
                observacoes=f"Transferência de {transferencia.local_origem.nome}",
                transferencia_id=transferencia.id
            )
            
            item.quantidade_recebida = quantidade_recebida
        
        transferencia.status = "recebida"
        transferencia.data_recebimento = datetime.utcnow()
        transferencia.recebido_por_id = usuario_id
        
        self.db.commit()
        return True
    
    # ================================================================================
    # INVENTÁRIO FÍSICO
    # ================================================================================
    
    def criar_inventario(
        self,
        empresa_id: int,
        local_estoque_id: int,
        descricao: str,
        usuario_id: int,
        tipo_inventario: str = "completo",
        considera_custo: bool = True,
        motivo: Optional[str] = None
    ) -> InventarioFisico:
        """Criar inventário físico"""
        
        numero = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        inventario = InventarioFisico(
            empresa_id=empresa_id,
            local_estoque_id=local_estoque_id,
            numero=numero,
            descricao=descricao,
            tipo_inventario=tipo_inventario,
            considera_custo=considera_custo,
            motivo=motivo,
            criado_por_id=usuario_id
        )
        
        self.db.add(inventario)
        self.db.flush()
        
        # Se for inventário completo, criar contagens para todos os produtos
        if tipo_inventario == "completo":
            estoques = self.db.query(EstoqueProduto).filter(
                EstoqueProduto.local_id == local_estoque_id
            ).all()
            
            for estoque in estoques:
                contagem = ContagemInventario(
                    inventario_id=inventario.id,
                    produto_id=estoque.produto_id,
                    quantidade_sistema=estoque.quantidade_atual,
                    custo_unitario=estoque.custo_medio if considera_custo else None
                )
                self.db.add(contagem)
        
        self.db.commit()
        return inventario
    
    def registrar_contagem(
        self,
        inventario_id: int,
        produto_id: int,
        quantidade_contada: Decimal,
        usuario_id: int,
        observacoes: Optional[str] = None,
        motivo_diferenca: Optional[str] = None
    ) -> ContagemInventario:
        """Registrar contagem de inventário"""
        
        inventario = self.db.query(InventarioFisico).filter(
            InventarioFisico.id == inventario_id
        ).first()
        
        if not inventario or inventario.status != StatusInventarioFisico.EM_ANDAMENTO:
            raise ValueError("Inventário não está em andamento")
        
        # Buscar ou criar contagem
        contagem = self.db.query(ContagemInventario).filter(
            ContagemInventario.inventario_id == inventario_id,
            ContagemInventario.produto_id == produto_id
        ).first()
        
        if not contagem:
            # Obter quantidade do sistema
            estoque = self.obter_ou_criar_estoque(produto_id, inventario.local_estoque_id)
            
            contagem = ContagemInventario(
                inventario_id=inventario_id,
                produto_id=produto_id,
                quantidade_sistema=estoque.quantidade_atual,
                custo_unitario=estoque.custo_medio if inventario.considera_custo else None
            )
            self.db.add(contagem)
        
        # Registrar contagem
        contagem.quantidade_contada = quantidade_contada
        contagem.quantidade_diferenca = quantidade_contada - contagem.quantidade_sistema
        contagem.data_contagem = datetime.utcnow()
        contagem.observacoes = observacoes
        contagem.motivo_diferenca = motivo_diferenca
        contagem.contado_por_id = usuario_id
        
        if inventario.considera_custo and contagem.custo_unitario:
            contagem.valor_diferenca = contagem.quantidade_diferenca * contagem.custo_unitario
        
        self.db.commit()
        return contagem
    
    def aplicar_ajustes_inventario(self, inventario_id: int, usuario_id: int) -> int:
        """Aplicar ajustes do inventário ao estoque"""
        
        inventario = self.db.query(InventarioFisico).filter(
            InventarioFisico.id == inventario_id
        ).first()
        
        if not inventario or inventario.status != StatusInventarioFisico.FINALIZADO:
            raise ValueError("Inventário deve estar finalizado para aplicar ajustes")
        
        contagens = self.db.query(ContagemInventario).filter(
            ContagemInventario.inventario_id == inventario_id,
            ContagemInventario.aprovado == True,
            ContagemInventario.ajuste_aplicado == False,
            ContagemInventario.quantidade_diferenca != 0
        ).all()
        
        ajustes_aplicados = 0
        
        for contagem in contagens:
            # Determinar tipo de movimentação
            if contagem.quantidade_diferenca > 0:
                tipo_mov = TipoMovimentacaoEstoque.ENTRADA_INVENTARIO
                quantidade = contagem.quantidade_diferenca
            else:
                tipo_mov = TipoMovimentacaoEstoque.SAIDA_INVENTARIO
                quantidade = abs(contagem.quantidade_diferenca)
            
            # Aplicar ajuste
            self.movimentar_estoque(
                produto_id=contagem.produto_id,
                local_id=inventario.local_estoque_id,
                tipo_movimentacao=tipo_mov,
                quantidade=quantidade,
                valor_unitario=contagem.custo_unitario,
                usuario_id=usuario_id,
                numero_documento=inventario.numero,
                observacoes=f"Ajuste inventário: {contagem.motivo_diferenca or 'Divergência identificada'}",
                inventario_id=inventario_id
            )
            
            contagem.ajuste_aplicado = True
            ajustes_aplicados += 1
        
        inventario.status = StatusInventarioFisico.APROVADO
        inventario.data_aprovacao = datetime.utcnow()
        inventario.aprovado_por_id = usuario_id
        
        self.db.commit()
        return ajustes_aplicados
    
    # ================================================================================
    # RELATÓRIOS E ANÁLISES
    # ================================================================================
    
    def calcular_giro_estoque(self, produto_id: int, local_id: int, periodo_dias: int = 30) -> Decimal:
        """Calcular giro do estoque para um produto"""
        
        data_inicio = datetime.utcnow() - timedelta(days=periodo_dias)
        
        # Quantidade vendida no período
        vendas = self.db.query(func.sum(MovimentacaoEstoque.quantidade)).filter(
            MovimentacaoEstoque.produto_id == produto_id,
            MovimentacaoEstoque.local_origem_id == local_id,
            MovimentacaoEstoque.tipo_movimentacao.like('%saida_venda%'),
            MovimentacaoEstoque.data_movimento >= data_inicio
        ).scalar() or Decimal('0')
        
        # Estoque médio do período
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
        
        data_inicio = datetime.utcnow() - timedelta(days=periodo_dias)
        
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
    
    def gerar_sugestao_compra(self, local_id: int, fornecedor_id: Optional[int] = None) -> List[Dict]:
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
