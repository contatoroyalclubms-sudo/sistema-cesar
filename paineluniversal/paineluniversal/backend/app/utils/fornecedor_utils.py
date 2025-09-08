"""
Serviços utilitários para gestão de fornecedores
Lógica de negócio e operações auxiliares
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ..models import Usuario, Produto
from ..models_inventario import (
    Fornecedor, TipoFornecedor, StatusFornecedor, ProdutoFornecedor,
    OrdemCompra, ItemOrdemCompra, StatusOrdemCompra,
    RecebimentoMercadoria, ItemRecebimento, StatusRecebimento
)

# Constantes
FORNECEDOR_NAO_ENCONTRADO = "Fornecedor não encontrado"
PRODUTO_NAO_ENCONTRADO = "Produto não encontrado"

class FornecedorService:
    """Serviços de lógica de negócio para fornecedores"""
    
    @staticmethod
    def calcular_performance_fornecedor(
        db: Session, 
        fornecedor_id: int, 
        periodo_dias: int = 30
    ) -> Dict[str, Any]:
        """Calcular performance de um fornecedor específico"""
        
        data_inicio = datetime.now(timezone.utc) - timedelta(days=periodo_dias)
        
        # Buscar compras do período
        compras = db.query(OrdemCompra).filter(
            OrdemCompra.fornecedor_id == fornecedor_id,
            OrdemCompra.data_pedido >= data_inicio
        ).all()
        
        if not compras:
            return {
                "total_compras": 0,
                "valor_total": 0.0,
                "atraso_medio": 0.0,
                "pontualidade": 0.0,
                "classificacao": "Sem dados"
            }
        
        total_compras = len(compras)
        valor_total = sum(c.valor_total for c in compras if c.valor_total)
        
        # Calcular pontualidade (apenas compras finalizadas)
        compras_finalizadas = [c for c in compras if c.status == StatusOrdemCompra.FINALIZADA]
        entregas_pontuais = 0
        soma_atrasos = 0
        
        for compra in compras_finalizadas:
            if compra.data_entrega_real and compra.data_entrega_prevista:
                atraso = (compra.data_entrega_real - compra.data_entrega_prevista).days
                soma_atrasos += max(0, atraso)  # Apenas atrasos positivos
                if atraso <= 0:
                    entregas_pontuais += 1
        
        pontualidade = (entregas_pontuais / len(compras_finalizadas) * 100) if compras_finalizadas else 0
        atraso_medio = soma_atrasos / len(compras_finalizadas) if compras_finalizadas else 0
        
        return {
            "total_compras": total_compras,
            "valor_total": float(valor_total),
            "atraso_medio": atraso_medio,
            "pontualidade": pontualidade,
            "classificacao": FornecedorService._obter_classificacao(pontualidade, atraso_medio)
        }
    
    @staticmethod
    def _obter_classificacao(pontualidade: float, atraso_medio: float) -> str:
        """Obter classificação baseada na performance"""
        if pontualidade >= 95 and atraso_medio <= 1:
            return "Excelente"
        elif pontualidade >= 80 and atraso_medio <= 3:
            return "Bom"
        elif pontualidade >= 60:
            return "Regular"
        else:
            return "Ruim"
    
    @staticmethod
    def obter_melhor_cotacao(
        db: Session,
        produto_id: int,
        empresa_id: int,
        quantidade: Optional[float] = None
    ) -> Optional[Tuple[ProdutoFornecedor, Fornecedor]]:
        """Obter melhor cotação para um produto"""
        
        query = db.query(ProdutoFornecedor, Fornecedor).join(Fornecedor).filter(
            ProdutoFornecedor.produto_id == produto_id,
            ProdutoFornecedor.ativo == True,
            Fornecedor.empresa_id == empresa_id,
            Fornecedor.status == StatusFornecedor.ATIVO
        )
        
        # Filtrar por quantidade mínima se especificada
        if quantidade:
            query = query.filter(
                or_(
                    ProdutoFornecedor.quantidade_minima.is_(None),
                    ProdutoFornecedor.quantidade_minima <= quantidade
                )
            )
        
        # Ordenar por preço e preferência
        return query.order_by(
            desc(ProdutoFornecedor.preferencial),
            ProdutoFornecedor.preco_compra
        ).first()
    
    @staticmethod
    def calcular_economia_cotacoes(
        db: Session,
        produto_id: int,
        empresa_id: int
    ) -> List[Dict[str, Any]]:
        """Calcular economia entre diferentes cotações"""
        
        cotacoes = db.query(ProdutoFornecedor, Fornecedor).join(Fornecedor).filter(
            ProdutoFornecedor.produto_id == produto_id,
            ProdutoFornecedor.ativo == True,
            Fornecedor.empresa_id == empresa_id,
            Fornecedor.status == StatusFornecedor.ATIVO
        ).order_by(ProdutoFornecedor.preco_compra).all()
        
        if not cotacoes:
            return []
        
        melhor_preco = cotacoes[0][0].preco_compra
        resultado = []
        
        for i, (pf, f) in enumerate(cotacoes):
            economia = float(pf.preco_compra - melhor_preco)
            percentual = (economia / melhor_preco * 100) if melhor_preco > 0 else 0
            
            resultado.append({
                "fornecedor_id": f.id,
                "fornecedor_nome": f.nome,
                "preco": float(pf.preco_compra),
                "economia_valor": economia,
                "economia_percentual": percentual,
                "is_melhor": i == 0,
                "preferencial": pf.preferencial,
                "prazo_entrega": pf.prazo_entrega
            })
        
        return resultado
    
    @staticmethod
    def sugerir_fornecedores_produto(
        db: Session,
        produto_id: int,
        empresa_id: int,
        quantidade: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Sugerir fornecedores para um produto baseado em critérios"""
        
        # Buscar todos os fornecedores do produto
        fornecedores = db.query(ProdutoFornecedor, Fornecedor).join(Fornecedor).filter(
            ProdutoFornecedor.produto_id == produto_id,
            ProdutoFornecedor.ativo == True,
            Fornecedor.empresa_id == empresa_id,
            Fornecedor.status == StatusFornecedor.ATIVO
        ).all()
        
        sugestoes = []
        
        for pf, f in fornecedores:
            # Calcular performance
            performance = FornecedorService.calcular_performance_fornecedor(
                db, f.id, periodo_dias=90
            )
            
            # Calcular score
            score = FornecedorService._calcular_score_fornecedor(
                pf, f, performance, quantidade
            )
            
            sugestoes.append({
                "fornecedor": f,
                "produto_fornecedor": pf,
                "performance": performance,
                "score": score,
                "motivo": FornecedorService._obter_motivo_sugestao(pf, f, performance)
            })
        
        # Ordenar por score
        return sorted(sugestoes, key=lambda x: x['score'], reverse=True)
    
    @staticmethod
    def _calcular_score_fornecedor(
        produto_fornecedor: ProdutoFornecedor,
        fornecedor: Fornecedor,
        performance: Dict[str, Any],
        quantidade: Optional[float] = None
    ) -> float:
        """Calcular score do fornecedor (0-100)"""
        
        score = 0.0
        
        # Preço (30%)
        if produto_fornecedor.preco_compra:
            # Assumir que preços menores são melhores
            score += 30.0  # Base, ajustar conforme comparação
        
        # Performance (40%)
        if performance["pontualidade"]:
            score += (performance["pontualidade"] / 100) * 40
        
        # Preferencial (20%)
        if produto_fornecedor.preferencial:
            score += 20.0
        
        # Avaliação média (10%)
        if fornecedor.avaliacao_media:
            score += (fornecedor.avaliacao_media / 5) * 10
        
        # Penalidades
        if quantidade and produto_fornecedor.quantidade_minima:
            if quantidade < produto_fornecedor.quantidade_minima:
                score *= 0.7  # Penalidade por não atingir quantidade mínima
        
        return min(100.0, score)
    
    @staticmethod
    def _obter_motivo_sugestao(
        produto_fornecedor: ProdutoFornecedor,
        fornecedor: Fornecedor,
        performance: Dict[str, Any]
    ) -> str:
        """Obter motivo da sugestão"""
        
        motivos = []
        
        if produto_fornecedor.preferencial:
            motivos.append("Fornecedor preferencial")
        
        if performance["pontualidade"] >= 90:
            motivos.append("Alta pontualidade nas entregas")
        
        if fornecedor.avaliacao_media and fornecedor.avaliacao_media >= 4:
            motivos.append("Bem avaliado")
        
        if performance["classificacao"] == "Excelente":
            motivos.append("Performance excelente")
        
        return "; ".join(motivos) if motivos else "Disponível"
    
    @staticmethod
    def validar_documento_fornecedor(documento: str, tipo_pessoa: str) -> bool:
        """Validar documento do fornecedor (CPF/CNPJ)"""
        
        # Remover caracteres especiais
        documento = ''.join(filter(str.isdigit, documento))
        
        if tipo_pessoa == "fisica":
            return len(documento) == 11  # CPF básico
        elif tipo_pessoa == "juridica":
            return len(documento) == 14  # CNPJ básico
        
        return False
    
    @staticmethod
    def calcular_historico_compras(
        db: Session,
        fornecedor_id: int,
        meses: int = 12
    ) -> List[Dict[str, Any]]:
        """Calcular histórico de compras por mês"""
        
        data_inicio = datetime.now(timezone.utc) - timedelta(days=meses * 30)
        
        # Buscar compras do período
        compras = db.query(OrdemCompra).filter(
            OrdemCompra.fornecedor_id == fornecedor_id,
            OrdemCompra.data_pedido >= data_inicio
        ).all()
        
        # Agrupar por mês
        historico = {}
        for compra in compras:
            mes_ano = compra.data_pedido.strftime("%Y-%m")
            if mes_ano not in historico:
                historico[mes_ano] = {
                    "periodo": mes_ano,
                    "quantidade_compras": 0,
                    "valor_total": 0.0,
                    "valor_medio": 0.0
                }
            
            historico[mes_ano]["quantidade_compras"] += 1
            historico[mes_ano]["valor_total"] += float(compra.valor_total or 0)
        
        # Calcular valores médios
        for periodo in historico.values():
            if periodo["quantidade_compras"] > 0:
                periodo["valor_medio"] = periodo["valor_total"] / periodo["quantidade_compras"]
        
        return sorted(historico.values(), key=lambda x: x["periodo"])
