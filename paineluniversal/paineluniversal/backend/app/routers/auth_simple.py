"""
Rota de autenticação simplificada sem cache para testes E2E
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import os

from app.database import get_db
from app.models import Usuario
from app.auth_functions import verificar_senha

router = APIRouter()

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class LoginRequest(BaseModel):
    cpf: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: dict

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login simplificado sem cache para testes E2E"""
    
    # Desabilitar validadores que usam cache
    import os
    os.environ["DISABLE_REDIS"] = "true"
    
    # Limpar CPF
    cpf_limpo = request.cpf.replace(".", "").replace("-", "").strip()
    
    # Buscar usuário
    usuario = db.query(Usuario).filter(Usuario.cpf == cpf_limpo).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos"
        )
    
    # Verificar senha
    if not verificar_senha(request.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos"
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(usuario.id), "cpf": usuario.cpf},
        expires_delta=access_token_expires
    )
    
    # Retornar token e dados do usuário
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "cpf": usuario.cpf,
            "email": usuario.email,
            "tipo": usuario.tipo,
            "tipo_usuario": usuario.tipo,  # Compatibilidade
            "ativo": usuario.ativo
        }
    }