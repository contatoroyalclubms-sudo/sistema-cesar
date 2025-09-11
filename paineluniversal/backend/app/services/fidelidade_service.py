"""
Service para Sistema de Fidelidade
Gerenciamento de pontos, níveis, recompensas e gamificação
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging
import random
import string
import qrcode
import io
import base64
from PIL import Image

from ..models_fidelidade import (
    ProgramaFidelidade,
    NivelPrograma,
    ClienteFidelidade,
    MovimentoPontos,
    RecompensaPrograma,
    ResgateFidelidade,
    ConquistaPrograma,
    DesafioFidelidade,
    ParticipacaoDesafio,
    RankingFidelidade,
    TipoMovimentoPontos,
    StatusRecompensa,
    TipoRecompensa,
    TipoConquista
)
from ..models import ClienteEvento as Cliente, VendaPDV, Usuario

logger = logging.getLogger(__name__)


class FidelidadeService:
    """Service principal para o sistema de fidelidade"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================= PROGRAMA =========================
    
    def criar_programa(
        self,
        nome: str,
        descricao: str,
        empresa_id: Optional[int] = None,
        configuracoes: Dict = {}
    ) -> ProgramaFidelidade:
        """Cria um novo programa de fidelidade"""
        programa = ProgramaFidelidade(
            nome=nome,
            descricao=descricao,
            empresa_id=empresa_id,
            **configuracoes
        )
        
        self.db.add(programa)
        self.db.commit()
        
        # Criar níveis padrão
        self._criar_niveis_padrao(programa.id)
        
        logger.info(f"Programa de fidelidade '{nome}' criado com ID {programa.id}")
        return programa
    
    def _criar_niveis_padrao(self, programa_id: int):
        """Cria os níveis padrão do programa"""
        niveis_config = [
            {
                "nome": "Bronze",
                "ordem": 1,
                "cor": "#CD7F32",
                "pontos_necessarios": 0,
                "multiplicador_pontos": 1.0,
                "desconto_permanente": 0,
                "cashback_percentual": 0
            },
            {
                "nome": "Prata",
                "ordem": 2,
                "cor": "#C0C0C0",
                "pontos_necessarios": 500,
                "multiplicador_pontos": 1.1,
                "desconto_permanente": 2,
                "cashback_percentual": 1
            },
            {
                "nome": "Ouro",
                "ordem": 3,
                "cor": "#FFD700",
                "pontos_necessarios": 1500,
                "multiplicador_pontos": 1.25,
                "desconto_permanente": 5,
                "cashback_percentual": 2
            },
            {
                "nome": "Platina",
                "ordem": 4,
                "cor": "#E5E4E2",
                "pontos_necessarios": 3000,
                "multiplicador_pontos": 1.5,
                "desconto_permanente": 8,
                "cashback_percentual": 3,
                "beneficios": {
                    "frete_gratis": True,
                    "atendimento_prioritario": True
                }
            },
            {
                "nome": "Diamante",
                "ordem": 5,
                "cor": "#B9F2FF",
                "pontos_necessarios": 6000,
                "multiplicador_pontos": 1.75,
                "desconto_permanente": 10,
                "cashback_percentual": 5,
                "beneficios": {
                    "frete_gratis": True,
                    "entrada_prioritaria": True,
                    "acesso_vip": True,
                    "atendimento_prioritario": True,
                    "preview_produtos": True
                }
            },
            {
                "nome": "Titanium",
                "ordem": 6,
                "cor": "#878681",
                "pontos_necessarios": 10000,
                "multiplicador_pontos": 2.0,
                "desconto_permanente": 15,
                "cashback_percentual": 8,
                "beneficios": {
                    "frete_gratis": True,
                    "entrada_prioritaria": True,
                    "acesso_vip": True,
                    "atendimento_prioritario": True,
                    "preview_produtos": True,
                    "eventos_exclusivos": True,
                    "presente_aniversario": True
                }
            }
        ]
        
        for config in niveis_config:
            nivel = NivelPrograma(
                programa_id=programa_id,
                **config
            )
            self.db.add(nivel)
        
        self.db.commit()
    
    # ========================= CLIENTE =========================
    
    def cadastrar_cliente(
        self,
        programa_id: int,
        cliente_id: int,
        indicado_por_id: Optional[int] = None
    ) -> ClienteFidelidade:
        """Cadastra um cliente no programa de fidelidade"""
        # Verificar se já está cadastrado
        cliente_fidelidade = self.db.query(ClienteFidelidade).filter(
            and_(
                ClienteFidelidade.programa_id == programa_id,
                ClienteFidelidade.cliente_id == cliente_id
            )
        ).first()
        
        if cliente_fidelidade:
            if not cliente_fidelidade.ativo:
                # Reativar cliente
                cliente_fidelidade.ativo = True
                cliente_fidelidade.data_inativacao = None
                self.db.commit()
            return cliente_fidelidade
        
        # Obter programa e nível inicial
        programa = self.db.query(ProgramaFidelidade).get(programa_id)
        nivel_inicial = self.db.query(NivelPrograma).filter(
            and_(
                NivelPrograma.programa_id == programa_id,
                NivelPrograma.ordem == 1
            )
        ).first()
        
        # Gerar código único
        codigo_fidelidade = self._gerar_codigo_fidelidade()
        
        # Criar cadastro
        cliente_fidelidade = ClienteFidelidade(
            programa_id=programa_id,
            cliente_id=cliente_id,
            nivel_atual_id=nivel_inicial.id if nivel_inicial else None,
            codigo_fidelidade=codigo_fidelidade,
            qr_code=self._gerar_qr_code(codigo_fidelidade),
            indicado_por_id=indicado_por_id
        )
        
        self.db.add(cliente_fidelidade)
        self.db.commit()
        
        # Bonus de primeira adesão
        if programa.multiplicador_primeira_compra > 1:
            self.adicionar_pontos(
                cliente_fidelidade.id,
                100,  # Pontos de boas-vindas
                TipoMovimentoPontos.PRIMEIRA_COMPRA,
                "Bônus de boas-vindas",
                multiplicador=programa.multiplicador_primeira_compra
            )
        
        # Pontos para quem indicou
        if indicado_por_id:
            indicador = self.db.query(ClienteFidelidade).get(indicado_por_id)
            if indicador:
                indicador.total_indicacoes += 1
                self.adicionar_pontos(
                    indicador.id,
                    50,  # Pontos por indicação
                    TipoMovimentoPontos.REFERENCIA,
                    f"Indicação de novo cliente"
                )
        
        logger.info(f"Cliente {cliente_id} cadastrado no programa {programa_id}")
        return cliente_fidelidade
    
    def _gerar_codigo_fidelidade(self) -> str:
        """Gera código único para o cliente"""
        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            existe = self.db.query(ClienteFidelidade).filter(
                ClienteFidelidade.codigo_fidelidade == codigo
            ).first()
            if not existe:
                return codigo
    
    def _gerar_qr_code(self, codigo: str) -> str:
        """Gera QR Code em base64"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(codigo)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    # ========================= PONTOS =========================
    
    def adicionar_pontos(
        self,
        cliente_fidelidade_id: int,
        pontos_base: int,
        tipo: TipoMovimentoPontos,
        descricao: str,
        venda_id: Optional[int] = None,
        multiplicador: float = 1.0,
        usuario_id: Optional[int] = None
    ) -> MovimentoPontos:
        """Adiciona pontos ao cliente"""
        cliente_fidelidade = self.db.query(ClienteFidelidade).get(cliente_fidelidade_id)
        if not cliente_fidelidade or not cliente_fidelidade.ativo:
            raise ValueError("Cliente não encontrado ou inativo")
        
        programa = cliente_fidelidade.programa
        nivel = cliente_fidelidade.nivel_atual
        
        # Calcular multiplicador total
        multiplicador_total = multiplicador
        
        # Multiplicador do nível
        if nivel:
            multiplicador_total *= nivel.multiplicador_pontos
        
        # Multiplicador de aniversário
        cliente = cliente_fidelidade.cliente
        if cliente.data_nascimento:
            hoje = datetime.now().date()
            aniversario = cliente.data_nascimento.replace(year=hoje.year)
            if abs((hoje - aniversario).days) <= 7:  # Semana do aniversário
                multiplicador_total *= programa.multiplicador_aniversario
        
        # Calcular pontos finais
        pontos_finais = int(pontos_base * multiplicador_total)
        
        # Verificar limite diário
        if programa.pontos_maximos_dia:
            pontos_hoje = self.db.query(func.sum(MovimentoPontos.pontos)).filter(
                and_(
                    MovimentoPontos.cliente_fidelidade_id == cliente_fidelidade_id,
                    MovimentoPontos.pontos > 0,
                    func.date(MovimentoPontos.criado_em) == datetime.now().date()
                )
            ).scalar() or 0
            
            if pontos_hoje + pontos_finais > programa.pontos_maximos_dia:
                pontos_finais = max(0, programa.pontos_maximos_dia - pontos_hoje)
        
        # Calcular validade
        data_expiracao = None
        if programa.validade_pontos_dias:
            data_expiracao = datetime.now() + timedelta(days=programa.validade_pontos_dias)
        
        # Criar movimento
        movimento = MovimentoPontos(
            cliente_fidelidade_id=cliente_fidelidade_id,
            tipo=tipo,
            pontos=pontos_finais,
            saldo_anterior=cliente_fidelidade.pontos_disponiveis,
            saldo_posterior=cliente_fidelidade.pontos_disponiveis + pontos_finais,
            descricao=descricao,
            venda_id=venda_id,
            multiplicador_aplicado=multiplicador_total,
            data_expiracao=data_expiracao,
            usuario_responsavel_id=usuario_id,
            origem="Sistema"
        )
        
        # Atualizar saldo do cliente
        cliente_fidelidade.pontos_disponiveis += pontos_finais
        cliente_fidelidade.pontos_totais += pontos_finais
        
        self.db.add(movimento)
        self.db.commit()
        
        # Verificar mudança de nível
        self._verificar_nivel(cliente_fidelidade)
        
        # Verificar conquistas
        self._verificar_conquistas(cliente_fidelidade, tipo)
        
        logger.info(f"Adicionados {pontos_finais} pontos ao cliente {cliente_fidelidade_id}")
        return movimento
    
    def processar_venda_pontos(
        self,
        venda_id: int,
        cliente_id: int,
        programa_id: int
    ) -> Optional[MovimentoPontos]:
        """Processa pontos de uma venda"""
        venda = self.db.query(VendaPDV).get(venda_id)
        if not venda:
            return None
        
        # Obter ou criar cadastro do cliente
        cliente_fidelidade = self.cadastrar_cliente(programa_id, cliente_id)
        
        # Calcular pontos baseados no valor da venda
        programa = cliente_fidelidade.programa
        pontos_base = int(float(venda.total) * float(programa.pontos_por_real))
        
        # Adicionar pontos
        movimento = self.adicionar_pontos(
            cliente_fidelidade.id,
            pontos_base,
            TipoMovimentoPontos.COMPRA,
            f"Compra #{venda.id}",
            venda_id=venda_id
        )
        
        # Atualizar estatísticas
        cliente_fidelidade.total_compras += 1
        cliente_fidelidade.valor_total_gasto += venda.total
        cliente_fidelidade.ultima_compra = datetime.now()
        cliente_fidelidade.ticket_medio = cliente_fidelidade.valor_total_gasto / cliente_fidelidade.total_compras
        
        self.db.commit()
        
        return movimento
    
    def _verificar_nivel(self, cliente_fidelidade: ClienteFidelidade):
        """Verifica e atualiza o nível do cliente"""
        programa = cliente_fidelidade.programa
        if not programa.usa_niveis:
            return
        
        # Obter níveis ordenados
        niveis = self.db.query(NivelPrograma).filter(
            NivelPrograma.programa_id == programa.id
        ).order_by(desc(NivelPrograma.ordem)).all()
        
        # Verificar qual nível o cliente atingiu
        for nivel in niveis:
            condicoes_atendidas = True
            
            # Verificar pontos
            if programa.pontos_manutencao_nivel:
                # Considera pontos disponíveis
                if cliente_fidelidade.pontos_disponiveis < nivel.pontos_necessarios:
                    condicoes_atendidas = False
            else:
                # Considera pontos totais históricos
                if cliente_fidelidade.pontos_totais < nivel.pontos_necessarios:
                    condicoes_atendidas = False
            
            # Verificar compras
            if nivel.compras_necessarias > 0:
                if cliente_fidelidade.total_compras < nivel.compras_necessarias:
                    condicoes_atendidas = False
            
            # Verificar valor gasto
            if nivel.valor_gasto_necessario > 0:
                if cliente_fidelidade.valor_total_gasto < nivel.valor_gasto_necessario:
                    condicoes_atendidas = False
            
            if condicoes_atendidas:
                # Atualizar nível se mudou
                if cliente_fidelidade.nivel_atual_id != nivel.id:
                    nivel_anterior = cliente_fidelidade.nivel_atual
                    cliente_fidelidade.nivel_atual_id = nivel.id
                    cliente_fidelidade.data_ultimo_nivel = datetime.now()
                    
                    # Calcular pontos para próximo nível
                    proximo_nivel = self.db.query(NivelPrograma).filter(
                        and_(
                            NivelPrograma.programa_id == programa.id,
                            NivelPrograma.ordem == nivel.ordem + 1
                        )
                    ).first()
                    
                    if proximo_nivel:
                        cliente_fidelidade.pontos_proximo_nivel = (
                            proximo_nivel.pontos_necessarios - cliente_fidelidade.pontos_totais
                        )
                    else:
                        cliente_fidelidade.pontos_proximo_nivel = 0
                    
                    logger.info(
                        f"Cliente {cliente_fidelidade.id} subiu de nível: "
                        f"{nivel_anterior.nome if nivel_anterior else 'Sem nível'} -> {nivel.nome}"
                    )
                break
    
    def _verificar_conquistas(
        self,
        cliente_fidelidade: ClienteFidelidade,
        tipo_movimento: TipoMovimentoPontos
    ):
        """Verifica se o cliente desbloqueou alguma conquista"""
        programa = cliente_fidelidade.programa
        if not programa.usa_conquistas:
            return
        
        # Obter conquistas ativas não desbloqueadas
        conquistas = self.db.query(ConquistaPrograma).filter(
            and_(
                ConquistaPrograma.programa_id == programa.id,
                ConquistaPrograma.ativo == True,
                ~ConquistaPrograma.clientes.contains(cliente_fidelidade)
            )
        ).all()
        
        for conquista in conquistas:
            desbloqueada = False
            criterios = conquista.criterios or {}
            
            # Verificar critérios baseados no tipo
            if conquista.tipo == TipoConquista.PRIMEIRA_COMPRA:
                if cliente_fidelidade.total_compras == 1:
                    desbloqueada = True
            
            elif conquista.tipo == TipoConquista.NUMERO_COMPRAS:
                quantidade = criterios.get("quantidade", 0)
                if cliente_fidelidade.total_compras >= quantidade:
                    desbloqueada = True
            
            elif conquista.tipo == TipoConquista.VALOR_GASTO:
                valor = criterios.get("valor", 0)
                if cliente_fidelidade.valor_total_gasto >= valor:
                    desbloqueada = True
            
            elif conquista.tipo == TipoConquista.FREQUENCIA:
                dias_consecutivos = criterios.get("dias_consecutivos", 0)
                # TODO: Implementar lógica de dias consecutivos
            
            if desbloqueada:
                # Adicionar conquista ao cliente
                cliente_fidelidade.conquistas_desbloqueadas.append(conquista)
                cliente_fidelidade.total_conquistas += 1
                conquista.total_desbloqueios += 1
                
                # Dar pontos de recompensa
                if conquista.pontos_recompensa > 0:
                    self.adicionar_pontos(
                        cliente_fidelidade.id,
                        conquista.pontos_recompensa,
                        TipoMovimentoPontos.CONQUISTA,
                        f"Conquista desbloqueada: {conquista.nome}"
                    )
                
                logger.info(
                    f"Cliente {cliente_fidelidade.id} desbloqueou conquista: {conquista.nome}"
                )
    
    # ========================= RECOMPENSAS =========================
    
    def listar_recompensas_disponiveis(
        self,
        cliente_fidelidade_id: int
    ) -> List[RecompensaPrograma]:
        """Lista recompensas disponíveis para o cliente"""
        cliente_fidelidade = self.db.query(ClienteFidelidade).get(cliente_fidelidade_id)
        if not cliente_fidelidade:
            return []
        
        # Filtrar recompensas
        query = self.db.query(RecompensaPrograma).filter(
            and_(
                RecompensaPrograma.programa_id == cliente_fidelidade.programa_id,
                RecompensaPrograma.ativo == True,
                RecompensaPrograma.custo_pontos <= cliente_fidelidade.pontos_disponiveis
            )
        )
        
        # Filtrar por nível mínimo
        if cliente_fidelidade.nivel_atual_id:
            nivel_ordem = cliente_fidelidade.nivel_atual.ordem
            query = query.join(
                NivelPrograma,
                RecompensaPrograma.nivel_minimo_id == NivelPrograma.id,
                isouter=True
            ).filter(
                or_(
                    RecompensaPrograma.nivel_minimo_id.is_(None),
                    NivelPrograma.ordem <= nivel_ordem
                )
            )
        
        # Filtrar por validade
        hoje = datetime.now()
        query = query.filter(
            or_(
                RecompensaPrograma.data_inicio.is_(None),
                RecompensaPrograma.data_inicio <= hoje
            )
        ).filter(
            or_(
                RecompensaPrograma.data_fim.is_(None),
                RecompensaPrograma.data_fim >= hoje
            )
        )
        
        # Filtrar por disponibilidade
        recompensas = []
        for recompensa in query.all():
            # Verificar quantidade disponível
            if recompensa.quantidade_disponivel is not None:
                if recompensa.quantidade_resgatada >= recompensa.quantidade_disponivel:
                    continue
            
            # Verificar limite por cliente
            resgates_cliente = self.db.query(ResgateFidelidade).filter(
                and_(
                    ResgateFidelidade.cliente_fidelidade_id == cliente_fidelidade_id,
                    ResgateFidelidade.recompensa_id == recompensa.id,
                    ResgateFidelidade.status != StatusRecompensa.CANCELADA
                )
            ).count()
            
            if resgates_cliente >= recompensa.limite_por_cliente:
                continue
            
            recompensas.append(recompensa)
        
        return recompensas
    
    def resgatar_recompensa(
        self,
        cliente_fidelidade_id: int,
        recompensa_id: int
    ) -> ResgateFidelidade:
        """Resgata uma recompensa"""
        cliente_fidelidade = self.db.query(ClienteFidelidade).get(cliente_fidelidade_id)
        recompensa = self.db.query(RecompensaPrograma).get(recompensa_id)
        
        if not cliente_fidelidade or not recompensa:
            raise ValueError("Cliente ou recompensa não encontrados")
        
        # Verificar se pode resgatar
        recompensas_disponiveis = self.listar_recompensas_disponiveis(cliente_fidelidade_id)
        if recompensa not in recompensas_disponiveis:
            raise ValueError("Recompensa não disponível para este cliente")
        
        # Verificar pontos
        if cliente_fidelidade.pontos_disponiveis < recompensa.custo_pontos:
            raise ValueError("Pontos insuficientes")
        
        # Gerar código de resgate
        codigo_resgate = self._gerar_codigo_resgate()
        
        # Calcular validade
        data_expiracao = None
        if recompensa.validade_dias:
            data_expiracao = datetime.now() + timedelta(days=recompensa.validade_dias)
        
        # Criar resgate
        resgate = ResgateFidelidade(
            cliente_fidelidade_id=cliente_fidelidade_id,
            recompensa_id=recompensa_id,
            codigo_resgate=codigo_resgate,
            qr_code=self._gerar_qr_code(codigo_resgate),
            pontos_utilizados=recompensa.custo_pontos,
            data_expiracao=data_expiracao
        )
        
        # Descontar pontos
        movimento = MovimentoPontos(
            cliente_fidelidade_id=cliente_fidelidade_id,
            tipo=TipoMovimentoPontos.RESGATE,
            pontos=-recompensa.custo_pontos,
            saldo_anterior=cliente_fidelidade.pontos_disponiveis,
            saldo_posterior=cliente_fidelidade.pontos_disponiveis - recompensa.custo_pontos,
            descricao=f"Resgate: {recompensa.nome}",
            resgate_id=resgate.id
        )
        
        cliente_fidelidade.pontos_disponiveis -= recompensa.custo_pontos
        cliente_fidelidade.pontos_resgatados += recompensa.custo_pontos
        
        # Atualizar estatísticas da recompensa
        recompensa.quantidade_resgatada += 1
        
        self.db.add(resgate)
        self.db.add(movimento)
        self.db.commit()
        
        logger.info(
            f"Cliente {cliente_fidelidade_id} resgatou recompensa {recompensa.nome}"
        )
        
        return resgate
    
    def _gerar_codigo_resgate(self) -> str:
        """Gera código único para resgate"""
        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            existe = self.db.query(ResgateFidelidade).filter(
                ResgateFidelidade.codigo_resgate == codigo
            ).first()
            if not existe:
                return codigo
    
    def utilizar_resgate(
        self,
        codigo_resgate: str,
        venda_id: Optional[int] = None
    ) -> ResgateFidelidade:
        """Utiliza um resgate"""
        resgate = self.db.query(ResgateFidelidade).filter(
            ResgateFidelidade.codigo_resgate == codigo_resgate
        ).first()
        
        if not resgate:
            raise ValueError("Código de resgate inválido")
        
        if resgate.status == StatusRecompensa.UTILIZADA:
            raise ValueError("Resgate já utilizado")
        
        if resgate.status == StatusRecompensa.CANCELADA:
            raise ValueError("Resgate cancelado")
        
        if resgate.status == StatusRecompensa.EXPIRADA:
            raise ValueError("Resgate expirado")
        
        # Verificar validade
        if resgate.data_expiracao and resgate.data_expiracao < datetime.now():
            resgate.status = StatusRecompensa.EXPIRADA
            self.db.commit()
            raise ValueError("Resgate expirado")
        
        # Marcar como utilizado
        resgate.status = StatusRecompensa.UTILIZADA
        resgate.data_utilizacao = datetime.now()
        resgate.venda_utilizada_id = venda_id
        
        self.db.commit()
        
        logger.info(f"Resgate {codigo_resgate} utilizado")
        return resgate
    
    # ========================= DESAFIOS =========================
    
    def criar_desafio(
        self,
        programa_id: int,
        nome: str,
        descricao: str,
        data_inicio: datetime,
        data_fim: datetime,
        criterios: Dict,
        pontos_conclusao: int,
        **kwargs
    ) -> DesafioFidelidade:
        """Cria um novo desafio"""
        desafio = DesafioFidelidade(
            programa_id=programa_id,
            nome=nome,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            criterios=criterios,
            pontos_conclusao=pontos_conclusao,
            **kwargs
        )
        
        self.db.add(desafio)
        self.db.commit()
        
        logger.info(f"Desafio '{nome}' criado")
        return desafio
    
    def participar_desafio(
        self,
        cliente_fidelidade_id: int,
        desafio_id: int
    ) -> ParticipacaoDesafio:
        """Inscreve cliente em um desafio"""
        # Verificar se já está participando
        participacao = self.db.query(ParticipacaoDesafio).filter(
            and_(
                ParticipacaoDesafio.cliente_fidelidade_id == cliente_fidelidade_id,
                ParticipacaoDesafio.desafio_id == desafio_id
            )
        ).first()
        
        if participacao:
            return participacao
        
        desafio = self.db.query(DesafioFidelidade).get(desafio_id)
        if not desafio or not desafio.ativo:
            raise ValueError("Desafio não encontrado ou inativo")
        
        # Verificar período
        agora = datetime.now()
        if agora < desafio.data_inicio or agora > desafio.data_fim:
            raise ValueError("Desafio fora do período válido")
        
        # Verificar limite de participantes
        if desafio.limite_participantes:
            total_participantes = self.db.query(ParticipacaoDesafio).filter(
                ParticipacaoDesafio.desafio_id == desafio_id
            ).count()
            
            if total_participantes >= desafio.limite_participantes:
                raise ValueError("Limite de participantes atingido")
        
        # Criar participação
        participacao = ParticipacaoDesafio(
            cliente_fidelidade_id=cliente_fidelidade_id,
            desafio_id=desafio_id
        )
        
        desafio.total_participantes += 1
        
        self.db.add(participacao)
        self.db.commit()
        
        logger.info(f"Cliente {cliente_fidelidade_id} inscrito no desafio {desafio_id}")
        return participacao
    
    def atualizar_progresso_desafio(
        self,
        participacao_id: int,
        progresso: Dict
    ) -> ParticipacaoDesafio:
        """Atualiza progresso em um desafio"""
        participacao = self.db.query(ParticipacaoDesafio).get(participacao_id)
        if not participacao:
            return None
        
        desafio = participacao.desafio
        criterios = desafio.criterios or {}
        
        # Atualizar progresso
        participacao.progresso_atual = progresso
        
        # Calcular percentual
        concluido = False
        if criterios.get("tipo") == "compras_periodo":
            quantidade_necessaria = criterios.get("quantidade", 1)
            quantidade_atual = progresso.get("compras", 0)
            participacao.percentual_completo = min(100, (quantidade_atual / quantidade_necessaria) * 100)
            concluido = quantidade_atual >= quantidade_necessaria
        
        elif criterios.get("tipo") == "valor_minimo":
            valor_necessario = criterios.get("valor", 0)
            valor_atual = progresso.get("valor", 0)
            participacao.percentual_completo = min(100, (valor_atual / valor_necessario) * 100)
            concluido = valor_atual >= valor_necessario
        
        # Se concluído
        if concluido and not participacao.concluido:
            participacao.concluido = True
            participacao.data_conclusao = datetime.now()
            participacao.pontos_ganhos = desafio.pontos_conclusao
            
            # Bonus por velocidade
            dias_decorridos = (datetime.now() - participacao.data_inicio).days
            periodo_total = (desafio.data_fim - desafio.data_inicio).days
            if dias_decorridos < periodo_total * 0.5:  # Concluído na primeira metade
                participacao.pontos_ganhos += desafio.bonus_velocidade
            
            # Adicionar pontos
            self.adicionar_pontos(
                participacao.cliente_fidelidade_id,
                participacao.pontos_ganhos,
                TipoMovimentoPontos.CONQUISTA,
                f"Desafio concluído: {desafio.nome}"
            )
            
            desafio.total_concluidos += 1
            
            logger.info(f"Desafio {desafio.id} concluído pela participação {participacao_id}")
        
        self.db.commit()
        return participacao
    
    # ========================= RANKING =========================
    
    def calcular_ranking(
        self,
        programa_id: int,
        tipo_periodo: str = "mensal",
        ano: int = None,
        mes: int = None
    ) -> RankingFidelidade:
        """Calcula o ranking de clientes"""
        if not ano:
            ano = datetime.now().year
        if not mes and tipo_periodo == "mensal":
            mes = datetime.now().month
        
        # Verificar se já existe
        ranking = self.db.query(RankingFidelidade).filter(
            and_(
                RankingFidelidade.programa_id == programa_id,
                RankingFidelidade.tipo_periodo == tipo_periodo,
                RankingFidelidade.ano == ano,
                RankingFidelidade.mes == mes if tipo_periodo == "mensal" else None
            )
        ).first()
        
        if ranking:
            return ranking
        
        # Calcular período
        if tipo_periodo == "mensal":
            data_inicio = datetime(ano, mes, 1)
            if mes == 12:
                data_fim = datetime(ano + 1, 1, 1) - timedelta(seconds=1)
            else:
                data_fim = datetime(ano, mes + 1, 1) - timedelta(seconds=1)
        else:  # anual
            data_inicio = datetime(ano, 1, 1)
            data_fim = datetime(ano + 1, 1, 1) - timedelta(seconds=1)
        
        # Buscar clientes ativos
        clientes = self.db.query(ClienteFidelidade).filter(
            and_(
                ClienteFidelidade.programa_id == programa_id,
                ClienteFidelidade.ativo == True
            )
        ).all()
        
        # Calcular rankings
        ranking_pontos = []
        ranking_compras = []
        ranking_valor = []
        
        for cliente in clientes:
            # Pontos ganhos no período
            pontos_periodo = self.db.query(func.sum(MovimentoPontos.pontos)).filter(
                and_(
                    MovimentoPontos.cliente_fidelidade_id == cliente.id,
                    MovimentoPontos.pontos > 0,
                    MovimentoPontos.criado_em >= data_inicio,
                    MovimentoPontos.criado_em <= data_fim
                )
            ).scalar() or 0
            
            if pontos_periodo > 0:
                ranking_pontos.append({
                    "cliente_id": cliente.cliente_id,
                    "pontos": pontos_periodo,
                    "nome": cliente.cliente.nome if cliente.cliente else "Cliente"
                })
            
            # Compras no período
            # TODO: Implementar contagem de compras no período
            
            # Valor gasto no período
            # TODO: Implementar soma de valores no período
        
        # Ordenar rankings
        ranking_pontos.sort(key=lambda x: x["pontos"], reverse=True)
        for i, item in enumerate(ranking_pontos):
            item["posicao"] = i + 1
        
        # Criar registro de ranking
        ranking = RankingFidelidade(
            programa_id=programa_id,
            tipo_periodo=tipo_periodo,
            ano=ano,
            mes=mes if tipo_periodo == "mensal" else None,
            ranking_pontos=ranking_pontos[:100],  # Top 100
            ranking_compras=ranking_compras[:100],
            ranking_valor=ranking_valor[:100],
            total_participantes=len(clientes),
            pontos_distribuidos=sum(item["pontos"] for item in ranking_pontos),
            media_pontos=sum(item["pontos"] for item in ranking_pontos) / len(ranking_pontos) if ranking_pontos else 0
        )
        
        self.db.add(ranking)
        self.db.commit()
        
        # Atualizar posições nos clientes
        for item in ranking_pontos[:10]:  # Top 10
            cliente = self.db.query(ClienteFidelidade).filter(
                and_(
                    ClienteFidelidade.programa_id == programa_id,
                    ClienteFidelidade.cliente_id == item["cliente_id"]
                )
            ).first()
            
            if cliente:
                cliente.posicao_ranking = item["posicao"]
                cliente.pontos_ranking = item["pontos"]
        
        self.db.commit()
        
        logger.info(f"Ranking {tipo_periodo} calculado para {ano}/{mes if mes else ''}")
        return ranking
    
    # ========================= MANUTENÇÃO =========================
    
    def processar_expiracao_pontos(self):
        """Processa expiração de pontos"""
        hoje = datetime.now()
        
        # Buscar movimentos expirados
        movimentos_expirados = self.db.query(MovimentoPontos).filter(
            and_(
                MovimentoPontos.data_expiracao <= hoje,
                MovimentoPontos.expirado == False,
                MovimentoPontos.pontos > 0
            )
        ).all()
        
        for movimento in movimentos_expirados:
            cliente_fidelidade = movimento.cliente_fidelidade
            
            # Criar movimento de expiração
            movimento_expiracao = MovimentoPontos(
                cliente_fidelidade_id=cliente_fidelidade.id,
                tipo=TipoMovimentoPontos.EXPIRACAO,
                pontos=-movimento.pontos,
                saldo_anterior=cliente_fidelidade.pontos_disponiveis,
                saldo_posterior=cliente_fidelidade.pontos_disponiveis - movimento.pontos,
                descricao=f"Expiração de pontos do movimento #{movimento.id}"
            )
            
            # Atualizar saldo
            cliente_fidelidade.pontos_disponiveis -= movimento.pontos
            cliente_fidelidade.pontos_expirados += movimento.pontos
            
            # Marcar como expirado
            movimento.expirado = True
            
            self.db.add(movimento_expiracao)
        
        self.db.commit()
        
        logger.info(f"Processados {len(movimentos_expirados)} movimentos expirados")
    
    def calcular_dias_sem_compra(self):
        """Atualiza dias sem compra dos clientes"""
        clientes = self.db.query(ClienteFidelidade).filter(
            ClienteFidelidade.ativo == True
        ).all()
        
        hoje = datetime.now()
        
        for cliente in clientes:
            if cliente.ultima_compra:
                cliente.dias_sem_compra = (hoje - cliente.ultima_compra).days
            else:
                cliente.dias_sem_compra = (hoje - cliente.data_adesao).days
        
        self.db.commit()
        
        logger.info(f"Atualizado dias sem compra para {len(clientes)} clientes")