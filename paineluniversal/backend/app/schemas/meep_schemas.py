from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class MEEPEventoBase(BaseModel):
    meep_id: str
    nome: str
    data_inicio: datetime
    data_fim: datetime
    local: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

class MEEPEventoCreate(MEEPEventoBase):
    evento_id: Optional[int] = None
    dados_completos: Optional[Dict[str, Any]] = None

class MEEPEventoResponse(MEEPEventoBase):
    id: int
    evento_id: Optional[int]
    total_inscritos: int
    total_presentes: int
    total_vendas: float
    taxa_conversao: float
    ultima_sincronizacao: datetime
    sincronizado: bool
    
    class Config:
        from_attributes = True

class MEEPParticipanteBase(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=11)
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    
    @validator('cpf')
    def validate_cpf(cls, v):
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf

class MEEPSyncRequest(BaseModel):
    force: bool = False
    evento_ids: Optional[List[int]] = None

class MEEPSyncResponse(BaseModel):
    status: str
    eventos_sincronizados: int
    participantes_sincronizados: int
    erros: List[str] = []
    tempo_execucao: float
