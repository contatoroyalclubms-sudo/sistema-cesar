# Schemas package
from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime, date, timezone
from typing import Optional, List
from decimal import Decimal

# Schemas básicos para auth
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    cpf: Optional[str] = None

class LoginRequest(BaseModel):
    cpf: str
    senha: str

# Schemas básicos para usuários
class UsuarioBase(BaseModel):
    nome: str
    email: str
    cpf: str
    telefone: Optional[str] = None
    tipo_usuario: str = "cliente"
    
class UsuarioCreate(UsuarioBase):
    senha: str
    
class UsuarioUpdate(UsuarioBase):
    senha: Optional[str] = None
    
class UsuarioRegister(BaseModel):
    nome: str
    email: str
    cpf: str
    telefone: Optional[str] = None
    senha: str
    tipo_usuario: Optional[str] = "cliente"
    
class Usuario(UsuarioBase):
    id: int
    ativo: bool = True
    
    class Config:
        from_attributes = True

# Schemas básicos para eventos
class EventoBase(BaseModel):
    nome: str
    local: str
    data_evento: datetime
    endereco: Optional[str] = None
    limite_idade: Optional[int] = None
    capacidade_maxima: Optional[int] = None
    
class EventoCreate(EventoBase):
    pass
    
class Evento(EventoBase):
    id: int
    ativo: bool = True
    
    class Config:
        from_attributes = True
        
class EventoDetalhado(Evento):
    total_vendas: int = 0
    receita_total: float = 0.0
    
class EventoFiltros(BaseModel):
    nome: Optional[str] = None

# Outros schemas básicos necessários
class PromoterEventoCreate(BaseModel):
    evento_id: int
    
class PromoterEventoResponse(BaseModel):
    id: int
    evento_id: int

# Schemas para empresas
class EmpresaBase(BaseModel):
    nome: str
    
class EmpresaCreate(EmpresaBase):
    pass
    
class Empresa(EmpresaBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para listas
class ListaBase(BaseModel):
    nome: str
    
class ListaCreate(ListaBase):
    pass
    
class Lista(ListaBase):
    id: int
    evento_id: int
    
    class Config:
        from_attributes = True

# Schemas para transações
class TransacaoBase(BaseModel):
    valor: float
    
class TransacaoCreate(TransacaoBase):
    pass
    
class Transacao(TransacaoBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para checkins
class CheckinBase(BaseModel):
    data_checkin: datetime
    
class CheckinCreate(CheckinBase):
    pass
    
class Checkin(CheckinBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para dashboard
class DashboardResumo(BaseModel):
    total_eventos: int = 0
    total_usuarios: int = 0
    total_checkins: int = 0
    receita_total: float = 0.0

# Schemas para cupons
class CupomBase(BaseModel):
    codigo: str
    
class CupomCreate(CupomBase):
    pass
    
class Cupom(CupomBase):
    id: int
    
    class Config:
        from_attributes = True

# Export essentials
__all__ = [
    "Token", "TokenData", "LoginRequest",
    "UsuarioBase", "UsuarioCreate", "UsuarioUpdate", "UsuarioRegister", "Usuario",
    "EventoBase", "EventoCreate", "Evento", "EventoDetalhado", "EventoFiltros",
    "PromoterEventoCreate", "PromoterEventoResponse",
    "EmpresaBase", "EmpresaCreate", "Empresa",
    "ListaBase", "ListaCreate", "Lista", 
    "TransacaoBase", "TransacaoCreate", "Transacao",
    "CheckinBase", "CheckinCreate", "Checkin",
    "DashboardResumo",
    "CupomBase", "CupomCreate", "Cupom"
]
