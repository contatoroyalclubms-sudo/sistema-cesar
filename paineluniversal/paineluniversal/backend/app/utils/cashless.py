"""
Utilitários para Sistema Cashless
Funções auxiliares para operações do sistema cashless
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets

from ..models_cashless import (
    CartaoCashless, RecargaCashless, MovimentacaoCashless,
    ConfiguracaoCashlessEvento, StatusRecarga, TipoMovimentacao
)
from ..models import Evento, Usuario

class CashlessService:
    """Serviço para operações do sistema cashless"""
    
    @staticmethod
    def gerar_numero_cartao() -> str:
        """Gerar número único para cartão cashless"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = secrets.token_hex(4).upper()
        return f"CARD{timestamp}{random_part}"
    
    @staticmethod
    def gerar_numero_recarga() -> str:
        """Gerar número único para recarga"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = secrets.token_hex(3).upper()
        return f"REC{timestamp}{random_part}"
    
    @staticmethod
    def gerar_numero_movimento() -> str:
        """Gerar número único para movimentação"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = secrets.token_hex(3).upper()
        return f"MOV{timestamp}{random_part}"
    
    @staticmethod
    def gerar_qr_code_cartao(cartao_id: int) -> str:
        """Gerar QR Code único para cartão"""
        uuid_part = str(uuid.uuid4()).replace('-', '')
        return f"CASHLESS_{cartao_id}_{uuid_part}"
    
    @staticmethod
    def calcular_bonus(
        valor_recarga: Decimal, 
        config: ConfiguracaoCashlessEvento
    ) -> Decimal:
        """Calcular valor do bônus baseado na configuração"""
        if not config or not config.bonus_habilitado:
            return Decimal('0')
        
        if valor_recarga < config.bonus_valor_minimo:
            return Decimal('0')
        
        # Verificar se há tabela de bônus personalizada
        if config.tabela_bonus:
            for regra in config.tabela_bonus:
                if valor_recarga >= regra.get('valor_min', 0):
                    bonus_percentual = regra.get('bonus', 0)
                    return (valor_recarga * Decimal(str(bonus_percentual))) / 100
        
        # Usar percentual padrão
        return (valor_recarga * config.bonus_percentual) / 100
    
    @staticmethod
    def validar_limite_recarga(
        valor_recarga: Decimal,
        config: ConfiguracaoCashlessEvento
    ) -> tuple[bool, str]:
        """Validar se o valor da recarga está dentro dos limites"""
        if not config:
            return True, ""
        
        if valor_recarga < config.valor_minimo_recarga:
            return False, f"Valor mínimo para recarga: R$ {config.valor_minimo_recarga}"
        
        if valor_recarga > config.valor_maximo_recarga:
            return False, f"Valor máximo para recarga: R$ {config.valor_maximo_recarga}"
        
        return True, ""
    
    @staticmethod
    def validar_limite_diario(
        cartao_id: int,
        valor_transacao: Decimal,
        db: Session,
        config: ConfiguracaoCashlessEvento
    ) -> tuple[bool, str]:
        """Validar limite diário do cartão"""
        if not config or not config.limite_diario_padrao:
            return True, ""
        
        # Buscar movimentações do dia
        hoje = datetime.now().date()
        movimentacoes_hoje = db.query(
            func.sum(MovimentacaoCashless.valor)
        ).filter(
            MovimentacaoCashless.cartao_id == cartao_id,
            MovimentacaoCashless.tipo_movimentacao == TipoMovimentacao.DEBITO,
            func.date(MovimentacaoCashless.criado_em) == hoje
        ).scalar() or Decimal('0')
        
        if movimentacoes_hoje + valor_transacao > config.limite_diario_padrao:
            return False, f"Limite diário excedido. Limite: R$ {config.limite_diario_padrao}"
        
        return True, ""
    
    @staticmethod
    def validar_saldo_cartao(
        cartao: CartaoCashless,
        valor_transacao: Decimal,
        config: ConfiguracaoCashlessEvento
    ) -> tuple[bool, str]:
        """Validar se o cartão tem saldo suficiente"""
        if cartao.saldo_atual >= valor_transacao:
            return True, ""
        
        # Verificar se permite saldo negativo
        if config and config.permite_saldo_negativo:
            deficit = valor_transacao - cartao.saldo_atual
            if deficit <= config.valor_maximo_saldo_negativo:
                return True, ""
            else:
                return False, f"Limite de saldo negativo excedido. Máximo: R$ {config.valor_maximo_saldo_negativo}"
        
        return False, "Saldo insuficiente"
    
    @staticmethod
    def criar_movimentacao_credito(
        cartao_id: int,
        valor: Decimal,
        descricao: str,
        referencia_id: Optional[int] = None,
        referencia_tipo: Optional[str] = None,
        referencia_numero: Optional[str] = None,
        cpf_operador: Optional[str] = None,
        nome_operador: Optional[str] = None,
        terminal_id: Optional[str] = None,
        db: Session = None
    ) -> MovimentacaoCashless:
        """Criar movimentação de crédito"""
        cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
        if not cartao:
            raise ValueError("Cartão não encontrado")
        
        saldo_anterior = cartao.saldo_atual
        saldo_posterior = saldo_anterior + valor
        
        movimentacao = MovimentacaoCashless(
            numero_movimento=CashlessService.gerar_numero_movimento(),
            cartao_id=cartao_id,
            tipo_movimentacao=TipoMovimentacao.CREDITO,
            valor=valor,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_posterior,
            descricao=descricao,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
            referencia_numero=referencia_numero,
            cpf_operador=cpf_operador,
            nome_operador=nome_operador,
            terminal_id=terminal_id,
            evento_id=cartao.evento_id,
            empresa_id=cartao.empresa_id
        )
        
        # Atualizar saldo do cartão
        cartao.saldo_atual = saldo_posterior
        cartao.ultima_utilizacao = datetime.now()
        
        return movimentacao
    
    @staticmethod
    def criar_movimentacao_debito(
        cartao_id: int,
        valor: Decimal,
        descricao: str,
        referencia_id: Optional[int] = None,
        referencia_tipo: Optional[str] = None,
        referencia_numero: Optional[str] = None,
        cpf_operador: Optional[str] = None,
        nome_operador: Optional[str] = None,
        terminal_id: Optional[str] = None,
        db: Session = None
    ) -> MovimentacaoCashless:
        """Criar movimentação de débito"""
        cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
        if not cartao:
            raise ValueError("Cartão não encontrado")
        
        # Buscar configurações
        config = db.query(ConfiguracaoCashlessEvento).filter(
            ConfiguracaoCashlessEvento.evento_id == cartao.evento_id
        ).first()
        
        # Validar saldo
        saldo_valido, mensagem = CashlessService.validar_saldo_cartao(cartao, valor, config)
        if not saldo_valido:
            raise ValueError(mensagem)
        
        # Validar limite diário
        limite_valido, mensagem = CashlessService.validar_limite_diario(
            cartao_id, valor, db, config
        )
        if not limite_valido:
            raise ValueError(mensagem)
        
        saldo_anterior = cartao.saldo_atual
        saldo_posterior = saldo_anterior - valor
        
        movimentacao = MovimentacaoCashless(
            numero_movimento=CashlessService.gerar_numero_movimento(),
            cartao_id=cartao_id,
            tipo_movimentacao=TipoMovimentacao.DEBITO,
            valor=valor,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_posterior,
            descricao=descricao,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
            referencia_numero=referencia_numero,
            cpf_operador=cpf_operador,
            nome_operador=nome_operador,
            terminal_id=terminal_id,
            evento_id=cartao.evento_id,
            empresa_id=cartao.empresa_id
        )
        
        # Atualizar saldo do cartão
        cartao.saldo_atual = saldo_posterior
        cartao.ultima_utilizacao = datetime.now()
        
        return movimentacao
    
    @staticmethod
    def processar_recarga_aprovada(
        recarga: RecargaCashless,
        aprovador_id: int,
        db: Session
    ) -> MovimentacaoCashless:
        """Processar aprovação de recarga e criar movimentação"""
        # Atualizar status da recarga
        recarga.status = StatusRecarga.APROVADA
        recarga.aprovado_por = aprovador_id
        recarga.aprovado_em = datetime.now()
        
        # Criar movimentação de crédito
        movimentacao = CashlessService.criar_movimentacao_credito(
            cartao_id=recarga.cartao_id,
            valor=recarga.valor_total,
            descricao=f"Recarga aprovada - {recarga.numero_recarga}",
            referencia_id=recarga.id,
            referencia_tipo="recarga",
            referencia_numero=recarga.numero_recarga,
            cpf_operador=recarga.cpf_operador,
            nome_operador=recarga.nome_operador,
            db=db
        )
        
        return movimentacao
    
    @staticmethod
    def transferir_saldo(
        origem_cartao_id: int,
        destino_cartao_id: int,
        valor: Decimal,
        motivo: str,
        operador_id: int,
        db: Session
    ) -> tuple[MovimentacaoCashless, MovimentacaoCashless]:
        """Transferir saldo entre cartões"""
        cartao_origem = db.query(CartaoCashless).filter(
            CartaoCashless.id == origem_cartao_id
        ).first()
        cartao_destino = db.query(CartaoCashless).filter(
            CartaoCashless.id == destino_cartao_id
        ).first()
        
        if not cartao_origem or not cartao_destino:
            raise ValueError("Cartão não encontrado")
        
        if cartao_origem.evento_id != cartao_destino.evento_id:
            raise ValueError("Cartões devem ser do mesmo evento")
        
        # Buscar configurações
        config = db.query(ConfiguracaoCashlessEvento).filter(
            ConfiguracaoCashlessEvento.evento_id == cartao_origem.evento_id
        ).first()
        
        if config and not config.permite_transferencia_cartoes:
            raise ValueError("Transferência entre cartões não permitida")
        
        # Validar saldo origem
        saldo_valido, mensagem = CashlessService.validar_saldo_cartao(
            cartao_origem, valor, config
        )
        if not saldo_valido:
            raise ValueError(f"Cartão origem: {mensagem}")
        
        # Buscar operador
        operador = db.query(Usuario).filter(Usuario.id == operador_id).first()
        operador_nome = operador.nome if operador else "Sistema"
        operador_cpf = getattr(operador, 'cpf', None) if operador else None
        
        # Criar débito no cartão origem
        movimentacao_origem = CashlessService.criar_movimentacao_debito(
            cartao_id=origem_cartao_id,
            valor=valor,
            descricao=f"Transferência para cartão {cartao_destino.numero_cartao} - {motivo}",
            referencia_id=destino_cartao_id,
            referencia_tipo="transferencia",
            cpf_operador=operador_cpf,
            nome_operador=operador_nome,
            db=db
        )
        
        # Criar crédito no cartão destino
        movimentacao_destino = CashlessService.criar_movimentacao_credito(
            cartao_id=destino_cartao_id,
            valor=valor,
            descricao=f"Transferência do cartão {cartao_origem.numero_cartao} - {motivo}",
            referencia_id=origem_cartao_id,
            referencia_tipo="transferencia",
            cpf_operador=operador_cpf,
            nome_operador=operador_nome,
            db=db
        )
        
        return movimentacao_origem, movimentacao_destino
    
    @staticmethod
    def estornar_movimentacao(
        movimentacao_id: int,
        motivo: str,
        operador_id: int,
        db: Session
    ) -> MovimentacaoCashless:
        """Estornar movimentação"""
        movimentacao_original = db.query(MovimentacaoCashless).filter(
            MovimentacaoCashless.id == movimentacao_id
        ).first()
        
        if not movimentacao_original:
            raise ValueError("Movimentação não encontrada")
        
        # Buscar configurações
        cartao = movimentacao_original.cartao
        config = db.query(ConfiguracaoCashlessEvento).filter(
            ConfiguracaoCashlessEvento.evento_id == cartao.evento_id
        ).first()
        
        if config and not config.permite_estorno_operador:
            raise ValueError("Estorno não permitido")
        
        # Verificar tempo limite
        if config and config.tempo_limite_estorno_horas:
            limite_tempo = movimentacao_original.criado_em + timedelta(
                hours=config.tempo_limite_estorno_horas
            )
            if datetime.now() > limite_tempo:
                raise ValueError("Tempo limite para estorno excedido")
        
        # Criar movimentação de estorno (tipo oposto)
        tipo_estorno = (
            TipoMovimentacao.CREDITO 
            if movimentacao_original.tipo_movimentacao == TipoMovimentacao.DEBITO
            else TipoMovimentacao.DEBITO
        )
        
        operador = db.query(Usuario).filter(Usuario.id == operador_id).first()
        operador_nome = operador.nome if operador else "Sistema"
        operador_cpf = getattr(operador, 'cpf', None) if operador else None
        
        if tipo_estorno == TipoMovimentacao.CREDITO:
            movimentacao_estorno = CashlessService.criar_movimentacao_credito(
                cartao_id=cartao.id,
                valor=movimentacao_original.valor,
                descricao=f"Estorno de {movimentacao_original.numero_movimento} - {motivo}",
                referencia_id=movimentacao_original.id,
                referencia_tipo="estorno",
                referencia_numero=movimentacao_original.numero_movimento,
                cpf_operador=operador_cpf,
                nome_operador=operador_nome,
                db=db
            )
        else:
            movimentacao_estorno = CashlessService.criar_movimentacao_debito(
                cartao_id=cartao.id,
                valor=movimentacao_original.valor,
                descricao=f"Estorno de {movimentacao_original.numero_movimento} - {motivo}",
                referencia_id=movimentacao_original.id,
                referencia_tipo="estorno",
                referencia_numero=movimentacao_original.numero_movimento,
                cpf_operador=operador_cpf,
                nome_operador=operador_nome,
                db=db
            )
        
        return movimentacao_estorno
    
    @staticmethod
    def obter_extrato_cartao(
        cartao_id: int,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Obter extrato completo do cartão"""
        cartao = db.query(CartaoCashless).filter(CartaoCashless.id == cartao_id).first()
        if not cartao:
            raise ValueError("Cartão não encontrado")
        
        query = db.query(MovimentacaoCashless).filter(
            MovimentacaoCashless.cartao_id == cartao_id
        )
        
        if data_inicio:
            query = query.filter(MovimentacaoCashless.criado_em >= data_inicio)
        if data_fim:
            query = query.filter(MovimentacaoCashless.criado_em <= data_fim)
        
        movimentacoes = query.order_by(MovimentacaoCashless.criado_em.desc()).all()
        
        # Calcular totais
        total_creditos = sum(
            m.valor for m in movimentacoes 
            if m.tipo_movimentacao in [TipoMovimentacao.CREDITO, TipoMovimentacao.BONUS]
        )
        total_debitos = sum(
            m.valor for m in movimentacoes 
            if m.tipo_movimentacao == TipoMovimentacao.DEBITO
        )
        
        return {
            "cartao": {
                "id": cartao.id,
                "numero_cartao": cartao.numero_cartao,
                "saldo_atual": float(cartao.saldo_atual),
                "status": cartao.status,
                "ultima_utilizacao": cartao.ultima_utilizacao
            },
            "periodo": {
                "data_inicio": data_inicio,
                "data_fim": data_fim
            },
            "resumo": {
                "total_movimentacoes": len(movimentacoes),
                "total_creditos": float(total_creditos),
                "total_debitos": float(total_debitos),
                "saldo_periodo": float(total_creditos - total_debitos)
            },
            "movimentacoes": [
                {
                    "id": m.id,
                    "numero_movimento": m.numero_movimento,
                    "tipo": m.tipo_movimentacao.value,
                    "valor": float(m.valor),
                    "saldo_anterior": float(m.saldo_anterior),
                    "saldo_posterior": float(m.saldo_posterior),
                    "descricao": m.descricao,
                    "data": m.criado_em,
                    "referencia_tipo": m.referencia_tipo,
                    "referencia_numero": m.referencia_numero
                }
                for m in movimentacoes
            ]
        }
