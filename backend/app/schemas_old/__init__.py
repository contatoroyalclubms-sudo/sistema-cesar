# Schemas package

try:
    # Usar import direto do arquivo schemas.py (sem circular import)
    import sys
    import os
    
    # Adicionar path absoluto para o módulo schemas.py
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    schemas_path = os.path.join(parent_dir, 'schemas.py')
    
    # Executar o arquivo schemas.py como módulo
    exec(open(schemas_path).read(), globals())
    
except Exception as e:
    # Fallback: definir schemas básicos necessários
    from pydantic import BaseModel
    from typing import Optional
    from datetime import datetime
    
    class Token(BaseModel):
        access_token: str
        token_type: str
    
    class TokenData(BaseModel):
        cpf: Optional[str] = None
    
    class LoginRequest(BaseModel):
        cpf: str
        senha: str
    
    class UsuarioBase(BaseModel):
        nome: str
        email: str
        
    class UsuarioCreate(UsuarioBase):
        senha: str
        
    class UsuarioRegister(BaseModel):
        nome: str
        email: str
        cpf: str
        telefone: Optional[str] = None
        senha: str
        tipo: Optional[str] = "cliente"  # Default para cliente
        
    class Usuario(UsuarioBase):
        id: int
        ativo: bool
        
        class Config:
            from_attributes = True
    
    # Schemas de Evento (mínimos para funcionar)
    class EventoBase(BaseModel):
        nome: str
        data_evento: datetime
        
    class EventoCreate(EventoBase):
        pass
        
    class Evento(EventoBase):
        id: int
        
        class Config:
            from_attributes = True
    
    class EventoDetalhado(Evento):
        pass
    
    class EventoFiltros(BaseModel):
        nome: Optional[str] = None
    
    class PromoterEventoCreate(BaseModel):
        evento_id: int
        
    class PromoterEventoResponse(BaseModel):
        id: int
        evento_id: int
        
    # Schemas básicos para outros módulos
    class Empresa(BaseModel):
        id: int
        nome: str
        
    class EmpresaCreate(BaseModel):
        nome: str
        
    class EmpresaUpdate(BaseModel):
        nome: Optional[str] = None
        
    # Lista schemas
    class Lista(BaseModel):
        id: int
        nome: str
        
        class Config:
            from_attributes = True
            
    class ListaCreate(BaseModel):
        nome: str
        
    class ListaUpdate(BaseModel):
        nome: Optional[str] = None
        
    class ListaDetalhada(Lista):
        convidados_count: int = 0
        
    class DashboardListas(BaseModel):
        total_listas: int = 0
        
    # Convidado schemas
    class Convidado(BaseModel):
        id: int
        nome: str
        
        class Config:
            from_attributes = True
            
    class ConvidadoCreate(BaseModel):
        nome: str
        
    class ConvidadoUpdate(BaseModel):
        nome: Optional[str] = None
        
    class ConvidadoImport(BaseModel):
        nome: str
        
    # Transacao schemas
    class Transacao(BaseModel):
        id: int
        valor: float
        
        class Config:
            from_attributes = True
            
    class TransacaoCreate(BaseModel):
        valor: float
        
    class TransacaoUpdate(BaseModel):
        valor: Optional[float] = None
        
    # Checkin schemas
    class Checkin(BaseModel):
        id: int
        data_checkin: datetime
        
        class Config:
            from_attributes = True
            
    class CheckinCreate(BaseModel):
        data_checkin: datetime
        
    class CheckinUpdate(BaseModel):
        data_checkin: Optional[datetime] = None
        
    # Cupom schemas
    class Cupom(BaseModel):
        id: int
        codigo: str
        
        class Config:
            from_attributes = True
            
    class CupomCreate(BaseModel):
        codigo: str
        
    class CupomUpdate(BaseModel):
        codigo: Optional[str] = None
        
    class CupomResponse(BaseModel):
        id: int
        codigo: str
        desconto_percentual: Optional[float] = None
        desconto_valor: Optional[float] = None
        lista_nome: str = ""
        evento_nome: str = ""
        
        class Config:
            from_attributes = True
        
    # Dashboard schemas
    class DashboardResumo(BaseModel):
        total_eventos: int = 0
        total_usuarios: int = 0
        total_checkins: int = 0
        receita_total: float = 0.0
        
    class RankingPromoter(BaseModel):
        id: int
        nome: str
        total_vendas: float = 0.0
        
    class DashboardAvancado(BaseModel):
        total_eventos: int = 0
        total_vendas: int = 0
        total_checkins: int = 0
        receita_total: float = 0.0
        taxa_conversao: float = 0.0
        vendas_hoje: int = 0
        vendas_semana: int = 0
        vendas_mes: int = 0
        receita_hoje: float = 0.0
        receita_semana: float = 0.0
        receita_mes: float = 0.0
        checkins_hoje: int = 0
        checkins_semana: int = 0
        taxa_presenca: float = 0.0
        fila_espera: int = 0
        cortesias: int = 0
        inadimplentes: int = 0
        aniversariantes_mes: int = 0
        consumo_medio: float = 0.0
        
    class FiltrosDashboard(BaseModel):
        data_inicio: Optional[datetime] = None
        data_fim: Optional[datetime] = None
        evento_id: Optional[int] = None
        
    class RankingPromoterAvancado(BaseModel):
        id: int
        nome: str
        total_vendas: float = 0.0
        total_clientes: int = 0
        
    class DadosGrafico(BaseModel):
        labels: list = []
        datasets: list = []
        
    class RankingPromoterLista(BaseModel):
        id: int
        nome: str
        total_vendas: float = 0.0
        posicao: int = 1
        
    # Relatórios schemas
    class RelatorioVendas(BaseModel):
        evento_id: int
        nome_evento: str
        total_vendas: int = 0
        receita_total: float = 0.0
        vendas_por_lista: list = []
        vendas_por_promoter: list = []
        
    # Gamificação schemas
    class ConquistaBase(BaseModel):
        nome: str
        descricao: str
        tipo: str = "vendas"
        criterio_valor: int = 1
        badge_nivel: str = "bronze"
        icone: Optional[str] = None
        
    class ConquistaCreate(ConquistaBase):
        pass
        
    class Conquista(ConquistaBase):
        id: int
        ativa: bool = True
        criado_em: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class PromoterConquistaResponse(BaseModel):
        id: int
        conquista_nome: str
        conquista_descricao: str
        badge_nivel: str
        
        class Config:
            from_attributes = True
            
    class MetricaPromoterResponse(BaseModel):
        promoter_id: int
        promoter_nome: str
        evento_id: Optional[int] = None
        evento_nome: Optional[str] = None
        periodo_inicio: Optional[datetime] = None
        periodo_fim: Optional[datetime] = None
        total_vendas: int = 0
        receita_gerada: float = 0.0
        total_convidados: int = 0
        total_presentes: int = 0
        taxa_presenca: float = 0.0
        taxa_conversao: float = 0.0
        crescimento_vendas: float = 0.0
        posicao_vendas: Optional[int] = None
        posicao_presenca: Optional[int] = None
        posicao_geral: Optional[int] = None
        badge_atual: str = "bronze"
        conquistas_recentes: list = []
        
        class Config:
            from_attributes = True
            
    class RankingGamificado(BaseModel):
        promoter_id: int
        nome_promoter: str
        avatar_url: Optional[str] = None
        badge_principal: str = "bronze"
        nivel_experiencia: int = 1
        total_vendas: int = 0
        receita_gerada: float = 0.0
        taxa_presenca: float = 0.0
        taxa_conversao: float = 0.0
        crescimento_mensal: float = 0.0
        posicao_atual: int = 1
        posicao_anterior: Optional[int] = None
        conquistas_total: int = 0
        conquistas_mes: int = 0
        eventos_ativos: int = 0
        streak_vendas: int = 0
        pontuacao_total: int = 0
        
    class DashboardGamificacao(BaseModel):
        ranking_geral: list = []
        conquistas_recentes: list = []
        metricas_periodo: dict = {}
        badges_disponiveis: list = []
        alertas_gamificacao: list = []
        estatisticas_gerais: dict = {}
        
    class FiltrosRanking(BaseModel):
        evento_id: Optional[int] = None
        periodo_inicio: Optional[datetime] = None
        periodo_fim: Optional[datetime] = None
        badge_nivel: Optional[str] = None
        tipo_ranking: Optional[str] = "geral"
        limit: int = 20
        
    # PDV schemas
    class ProdutoBase(BaseModel):
        nome: str
        descricao: Optional[str] = None
        preco: float = 0.0
        codigo_barras: Optional[str] = None
        estoque_atual: int = 0
        
    class ProdutoCreate(ProdutoBase):
        evento_id: int
        
    class Produto(ProdutoBase):
        id: int
        evento_id: int = 0
        
        class Config:
            from_attributes = True
            
    class ComandaBase(BaseModel):
        numero_comanda: str
        cpf_cliente: Optional[str] = None
        
    class ComandaCreate(ComandaBase):
        evento_id: int
        
    class Comanda(ComandaBase):
        id: int
        saldo: float = 0.0
        
        class Config:
            from_attributes = True
            
    class VendaPDVBase(BaseModel):
        valor_total: float = 0.0
        
    class VendaPDVCreate(VendaPDVBase):
        comanda_id: int
        
    class VendaPDV(VendaPDVBase):
        id: int
        
        class Config:
            from_attributes = True
            
    class RecargaComandaBase(BaseModel):
        valor: float = 0.0
        
    class RecargaComandaCreate(RecargaComandaBase):
        comanda_id: int
        
    class RecargaComanda(RecargaComandaBase):
        id: int
        
        class Config:
            from_attributes = True
            
    class CaixaPDVBase(BaseModel):
        valor_inicial: float = 0.0
        
    class CaixaPDVCreate(CaixaPDVBase):
        evento_id: int
        
    class CaixaPDV(CaixaPDVBase):
        id: int
        
        class Config:
            from_attributes = True
            
    class RelatorioVendasPDV(BaseModel):
        total_vendas: float = 0.0
        total_produtos: int = 0
        
    class DashboardPDV(BaseModel):
        vendas_hoje: int = 0
        valor_vendas_hoje: float = 0.0
        produtos_em_falta: int = 0
        comandas_ativas: int = 0
        caixas_abertos: int = 0
        vendas_por_hora: list = []
        produtos_mais_vendidos: list = []
        alertas: list = []
    
    # MEEP Schemas
    class ClienteEventoBase(BaseModel):
        cpf: str
        nome_completo: str
        nome_social: Optional[str] = None
        data_nascimento: Optional[datetime] = None
        nome_mae: Optional[str] = None
        telefone: Optional[str] = None
        email: Optional[str] = None
        status: str = "ativo"
        
    class ClienteEventoCreate(ClienteEventoBase):
        pass
        
    class ClienteEventoResponse(ClienteEventoBase):
        id: int
        criado_em: Optional[datetime] = None
        atualizado_em: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class ValidacaoAcessoBase(BaseModel):
        evento_id: int
        cliente_id: Optional[int] = None
        cpf_hash: str
        qr_code_data: str
        cpf_digits: str
        ip_address: Optional[str] = None
        user_agent: Optional[str] = None
        sucesso: bool = False
        motivo_falha: Optional[str] = None
        latitude: Optional[float] = None
        longitude: Optional[float] = None
        device_info: Optional[str] = None
        
    class ValidacaoAcessoResponse(ValidacaoAcessoBase):
        id: int
        timestamp_validacao: Optional[datetime] = None
        criado_em: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class EquipamentoEventoBase(BaseModel):
        evento_id: int
        nome: str
        tipo: str
        ip_address: str
        mac_address: Optional[str] = None
        status: str = "offline"
        configuracao: Optional[str] = None
        localizacao: Optional[str] = None
        responsavel_id: Optional[int] = None
        heartbeat_interval: int = 30
        
    class EquipamentoEventoCreate(EquipamentoEventoBase):
        pass
        
    class EquipamentoEventoResponse(EquipamentoEventoBase):
        id: int
        ultima_atividade: Optional[datetime] = None
        criado_em: Optional[datetime] = None
        atualizado_em: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class PrevisaoIABase(BaseModel):
        evento_id: int
        tipo_previsao: str
        dados_entrada: str
        resultado_previsao: str
        confiabilidade: Optional[float] = None
        aplicada: bool = False
        feedback_real: Optional[str] = None
        precisao_real: Optional[float] = None
        
    class PrevisaoIAResponse(PrevisaoIABase):
        id: int
        timestamp_previsao: Optional[datetime] = None
        criado_em: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class AnalyticsMEEPBase(BaseModel):
        evento_id: int
        metrica: str
        valor: Optional[float] = None
        valor_anterior: Optional[float] = None
        percentual_mudanca: Optional[float] = None
        periodo: Optional[str] = None
        dados_detalhados: Optional[str] = None
        alertas: Optional[str] = None
        
    class AnalyticsMEEPResponse(AnalyticsMEEPBase):
        id: int
        timestamp_coleta: Optional[datetime] = None
        criado_em: Optional[datetime] = None
        
        class Config:
            from_attributes = True
            
    class LogSegurancaMEEPBase(BaseModel):
        evento_id: Optional[int] = None
        tipo_evento: str
        gravidade: str = "info"
        ip_address: Optional[str] = None
        user_agent: Optional[str] = None
        dados_evento: str
        usuario_id: Optional[int] = None
        resolvido: bool = False
        
    class LogSegurancaMEEPResponse(LogSegurancaMEEPBase):
        id: int
        timestamp_evento: Optional[datetime] = None
        criado_em: Optional[datetime] = None
        
        class Config:
            from_attributes = True

# Re-export para compatibilidade
__all__ = [
    "Token",
    "TokenData", 
    "LoginRequest",
    "UsuarioBase",
    "UsuarioCreate", 
    "UsuarioRegister",
    "Usuario",
    "EventoBase",
    "EventoCreate",
    "Evento", 
    "EventoDetalhado",
    "EventoFiltros",
    "PromoterEventoCreate",
    "PromoterEventoResponse",
    "Empresa",
    "EmpresaCreate",
    "EmpresaUpdate",
    "Lista",
    "ListaCreate",
    "ListaUpdate",
    "ListaDetalhada",
    "DashboardListas",
    "Convidado",
    "ConvidadoCreate",
    "ConvidadoUpdate",
    "ConvidadoImport",
    "Transacao",
    "TransacaoCreate",
    "TransacaoUpdate",
    "Checkin",
    "CheckinCreate",
    "CheckinUpdate",
    "Cupom",
    "CupomCreate",
    "CupomUpdate",
    "CupomResponse",
    "DashboardResumo",
    "RankingPromoter",
    "DashboardAvancado",
    "FiltrosDashboard",
    "RankingPromoterAvancado",
    "DadosGrafico",
    "RankingPromoterLista",
    "RelatorioVendas",
    "ProdutoBase",
    "ProdutoCreate", 
    "Produto",
    "ComandaBase",
    "ComandaCreate",
    "Comanda",
    "VendaPDVBase",
    "VendaPDVCreate",
    "VendaPDV",
    "RecargaComandaBase",
    "RecargaComandaCreate",
    "RecargaComanda",
    "CaixaPDVBase",
    "CaixaPDVCreate",
    "CaixaPDV",
    "RelatorioVendasPDV",
    "DashboardPDV",
    "ConquistaBase",
    "ConquistaCreate",
    "Conquista",
    "PromoterConquistaResponse",
    "MetricaPromoterResponse",
    "RankingGamificado",
    "DashboardGamificacao",
    "FiltrosRanking",
    # MEEP Schemas
    "ClienteEventoBase",
    "ClienteEventoCreate",
    "ClienteEventoResponse",
    "ValidacaoAcessoBase",
    "ValidacaoAcessoResponse",
    "EquipamentoEventoBase",
    "EquipamentoEventoCreate",
    "EquipamentoEventoResponse",
    "PrevisaoIABase",
    "PrevisaoIAResponse",
    "AnalyticsMEEPBase",
    "AnalyticsMEEPResponse",
    "LogSegurancaMEEPBase",
    "LogSegurancaMEEPResponse",
]
