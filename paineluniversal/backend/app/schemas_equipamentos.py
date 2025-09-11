"""
Schemas Pydantic para sistema de equipamentos e QR readers
Sistema de Gestão de Eventos - Universal v5
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class LeitorQRCodeBase(BaseModel):
    codigo_equipamento: str = Field(..., min_length=1, max_length=20)
    nome: str = Field(..., min_length=1, max_length=100)
    tipo_leitor: Optional[str] = Field(None, max_length=50)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    numero_serie: Optional[str] = Field(None, max_length=100)
    
    # Conectividade
    tipo_conexao: Optional[str] = Field(None, max_length=50)
    endereco_ip: Optional[str] = Field(None, max_length=45)
    porta_comunicacao: Optional[int] = Field(None, ge=1, le=65535)
    endereco_mac: Optional[str] = Field(None, max_length=17)
    
    # Configurações de leitura
    sensibilidade: int = Field(3, ge=1, le=5)
    timeout_leitura: int = Field(5000, ge=1000, le=30000)
    formato_suportado: Optional[str] = Field(None, max_length=200)
    modo_operacao: str = Field("continuo", max_length=20)
    
    # Calibração e qualidade
    resolucao_minima: int = Field(640, ge=320)
    qualidade_imagem: int = Field(80, ge=1, le=100)
    zoom_automatico: bool = Field(True)
    foco_automatico: bool = Field(True)
    compensacao_luz: bool = Field(True)
    
    # Status operacional
    status: str = Field("inativo", max_length=20)
    versao_firmware: Optional[str] = Field(None, max_length=20)
    temperatura_operacao: Optional[float] = Field(None)
    nivel_bateria: Optional[int] = Field(None, ge=0, le=100)
    
    # Localização
    localizacao: Optional[str] = Field(None, max_length=100)
    ponto_acesso_id: Optional[int] = Field(None)
    evento_id: Optional[int] = Field(None)
    empresa_id: Optional[int] = Field(None)
    
    # Configurações avançadas
    filtro_duplicatas: bool = Field(True)
    tempo_filtro_duplicata: int = Field(3000, ge=1000, le=10000)
    validacao_formato: bool = Field(True)
    log_detalhado: bool = Field(False)

    @validator('endereco_mac')
    def validate_mac_address(cls, v):
        if v and len(v) == 17:
            # Formato XX:XX:XX:XX:XX:XX
            if not all(c in '0123456789ABCDEFabcdef:' for c in v):
                raise ValueError('Endereço MAC inválido')
        return v

class LeitorQRCodeCreate(LeitorQRCodeBase):
    pass

class LeitorQRCodeUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo_leitor: Optional[str] = Field(None, max_length=50)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)
    localizacao: Optional[str] = Field(None, max_length=100)
    sensibilidade: Optional[int] = Field(None, ge=1, le=5)
    timeout_leitura: Optional[int] = Field(None, ge=1000, le=30000)
    ponto_acesso_id: Optional[int] = Field(None)

class LeitorQRCode(LeitorQRCodeBase):
    id: int
    total_leituras: int = 0
    leituras_sucesso: int = 0
    leituras_erro: int = 0
    tempo_medio_leitura: float = 0.0
    ultimo_heartbeat: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    criado_por: Optional[int] = None

    class Config:
        from_attributes = True


class PontoAcessoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    codigo: str = Field(..., min_length=1, max_length=20)
    tipo_ponto: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = Field(None)
    capacidade_maxima: Optional[int] = Field(None, ge=1)
    
    # Localização física
    localizacao_descricao: Optional[str] = Field(None, max_length=200)
    coordenadas_gps: Optional[str] = Field(None, max_length=50)
    andar: Optional[str] = Field(None, max_length=10)
    setor: Optional[str] = Field(None, max_length=50)
    
    # Configurações operacionais
    ativo: bool = Field(True)
    requer_validacao: bool = Field(True)
    permite_reentrada: bool = Field(False)
    horario_abertura: Optional[time] = Field(None)
    horario_fechamento: Optional[time] = Field(None)
    
    # Configurações de segurança
    nivel_seguranca: str = Field("normal", max_length=20)
    log_todas_tentativas: bool = Field(True)
    alerta_capacidade: bool = Field(True)
    percentual_alerta: int = Field(90, ge=50, le=100)
    
    evento_id: Optional[int] = Field(None)
    empresa_id: Optional[int] = Field(None)

class PontoAcessoCreate(PontoAcessoBase):
    pass

class PontoAcessoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo_ponto: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = Field(None)
    capacidade_maxima: Optional[int] = Field(None, ge=1)
    ativo: Optional[bool] = Field(None)
    permite_reentrada: Optional[bool] = Field(None)
    nivel_seguranca: Optional[str] = Field(None, max_length=20)

class PontoAcesso(PontoAcessoBase):
    id: int
    contagem_atual: int = 0
    total_entradas: int = 0
    total_saidas: int = 0
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class HistoricoLeituraQRBase(BaseModel):
    codigo_lido: str = Field(..., min_length=1)
    codigo_decodificado: Optional[str] = Field(None)
    formato_codigo: Optional[str] = Field(None, max_length=50)
    qualidade_leitura: Optional[int] = Field(None, ge=1, le=100)
    
    # Resultado da validação
    valido: bool = Field(False)
    tipo_validacao: Optional[str] = Field(None, max_length=50)
    resultado_validacao: Optional[str] = Field(None, max_length=20)
    motivo_rejeicao: Optional[str] = Field(None, max_length=200)
    
    # Contexto da leitura
    leitor_id: int = Field(...)
    ponto_acesso_id: Optional[int] = Field(None)
    operador_id: Optional[int] = Field(None)
    
    # Dados do participante
    participante_cpf: Optional[str] = Field(None, max_length=14)
    participante_nome: Optional[str] = Field(None, max_length=100)
    participante_tipo: Optional[str] = Field(None, max_length=50)
    
    # Dados do ingresso/credencial
    ingresso_id: Optional[int] = Field(None)
    credencial_id: Optional[int] = Field(None)
    lista_id: Optional[int] = Field(None)
    
    # Metadados técnicos
    tempo_leitura: Optional[int] = Field(None)
    tentativas: int = Field(1, ge=1)
    posicao_qr_imagem: Optional[str] = Field(None, max_length=50)
    
    # Informações do dispositivo
    endereco_ip: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    sessao_id: Optional[str] = Field(None, max_length=100)
    
    # Dados de geolocalização
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    precisao_localizacao: Optional[float] = Field(None)
    
    evento_id: Optional[int] = Field(None)
    empresa_id: Optional[int] = Field(None)

class HistoricoLeituraQRCreate(HistoricoLeituraQRBase):
    pass

class HistoricoLeituraQR(HistoricoLeituraQRBase):
    id: int
    timestamp_leitura: datetime

    class Config:
        from_attributes = True


class MovimentacaoAcessoBase(BaseModel):
    tipo_movimento: str = Field(..., max_length=20)
    cpf_participante: str = Field(..., max_length=14)
    nome_participante: Optional[str] = Field(None, max_length=100)
    tipo_participante: Optional[str] = Field(None, max_length=50)
    
    ponto_acesso_id: int = Field(...)
    leitura_qr_id: Optional[int] = Field(None)
    
    # Dados do acesso
    credencial_utilizada: Optional[str] = Field(None, max_length=50)
    primeira_entrada: bool = Field(False)
    tempo_permanencia: Optional[int] = Field(None)
    
    # Validação e segurança
    validacao_adicional: Optional[str] = Field(None, max_length=100)
    nivel_confianca: int = Field(100, ge=0, le=100)
    sinalizadores: Optional[str] = Field(None)  # JSON
    
    evento_id: Optional[int] = Field(None)
    empresa_id: Optional[int] = Field(None)

    @validator('tipo_movimento')
    def validate_tipo_movimento(cls, v):
        allowed_types = ['entrada', 'saida']
        if v not in allowed_types:
            raise ValueError(f'Tipo movimento deve ser um de: {allowed_types}')
        return v

class MovimentacaoAcessoCreate(MovimentacaoAcessoBase):
    pass

class MovimentacaoAcesso(MovimentacaoAcessoBase):
    id: int
    data_hora: datetime

    class Config:
        from_attributes = True


class ConfiguracaoEquipamentoBase(BaseModel):
    tipo_equipamento: str = Field(..., max_length=50)
    nome_configuracao: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = Field(None)
    
    # Configuração (JSON flexível)
    parametros_json: Optional[str] = Field(None)
    template_configuracao: Optional[str] = Field(None)
    
    # Aplicabilidade
    marca_equipamento: Optional[str] = Field(None, max_length=50)
    modelo_equipamento: Optional[str] = Field(None, max_length=50)
    versao_firmware_min: Optional[str] = Field(None, max_length=20)
    versao_firmware_max: Optional[str] = Field(None, max_length=20)
    
    # Status
    ativo: bool = Field(True)
    configuracao_padrao: bool = Field(False)
    
    # Versionamento
    versao: str = Field("1.0", max_length=10)
    configuracao_pai_id: Optional[int] = Field(None)
    
    evento_id: Optional[int] = Field(None)
    empresa_id: Optional[int] = Field(None)

class ConfiguracaoEquipamentoCreate(ConfiguracaoEquipamentoBase):
    pass

class ConfiguracaoEquipamentoUpdate(BaseModel):
    nome_configuracao: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(None)
    parametros_json: Optional[str] = Field(None)
    ativo: Optional[bool] = Field(None)
    configuracao_padrao: Optional[bool] = Field(None)

class ConfiguracaoEquipamento(ConfiguracaoEquipamentoBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    criado_por: Optional[int] = None

    class Config:
        from_attributes = True


# Schemas para estatísticas e relatórios

class EstatisticasLeitorQR(BaseModel):
    leitor_id: int
    nome_leitor: str
    total_leituras_hoje: int
    total_leituras_semana: int
    total_leituras_mes: int
    taxa_sucesso: float
    tempo_medio_leitura: float
    ultimo_status: str
    ultima_atividade: Optional[datetime]

class EstatisticasPontoAcesso(BaseModel):
    ponto_id: int
    nome_ponto: str
    total_entradas_hoje: int
    total_saidas_hoje: int
    ocupacao_atual: int
    capacidade_maxima: int
    percentual_ocupacao: float
    pico_ocupacao_dia: int
    horario_pico: Optional[str]

class RelatorioMovimentacao(BaseModel):
    periodo_inicio: datetime
    periodo_fim: datetime
    total_movimentacoes: int
    total_entradas: int
    total_saidas: int
    ocupacao_media: float
    pontos_mais_ativos: List[Dict[str, Any]]
    horarios_pico: List[Dict[str, Any]]

class StatusSistemaEquipamentos(BaseModel):
    total_leitores: int
    leitores_ativos: int
    leitores_inativos: int
    leitores_manutencao: int
    total_pontos_acesso: int
    pontos_ativos: int
    ocupacao_total: int
    alertas_capacidade: int
    ultima_verificacao: datetime

# Schemas para operações em lote

class LoteConfiguracao(BaseModel):
    equipamentos_ids: List[int]
    configuracao_id: int
    aplicar_imediatamente: bool = Field(True)

class ResultadoLote(BaseModel):
    total_equipamentos: int
    sucessos: int
    falhas: int
    detalhes: List[Dict[str, Any]]