"""
Funções de autenticação do sistema
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from .database import get_db, settings
from .models import Usuario

# Configurações de segurança
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"

def gerar_hash_senha(senha: str) -> str:
    """Gerar hash da senha usando bcrypt"""
    return pwd_context.hash(senha)

def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    """Verificar se a senha está correta"""
    return pwd_context.verify(senha_plain, senha_hash)

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Criar token JWT de acesso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def autenticar_usuario(cpf: str, senha: str, db: Session) -> Optional[Usuario]:
    """Autenticar usuário por CPF e senha"""
    usuario = db.query(Usuario).filter(Usuario.cpf == cpf).first()
    if not usuario:
        return None
    if not verificar_senha(senha, usuario.senha_hash):
        return None
    return usuario

def obter_usuario_atual(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Usuario:
    """Obter usuário atual através do token JWT"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cpf_or_id: str = payload.get("sub")
        if cpf_or_id is None:
            raise credentials_exception
            
        print(f"🔍 JWT sub value: {cpf_or_id} (tipo: {type(cpf_or_id)})")
        
        # Tentar buscar por CPF primeiro
        usuario = db.query(Usuario).filter(Usuario.cpf == cpf_or_id).first()
        if usuario:
            print(f"✅ Usuário encontrado por CPF: {usuario.nome}")
            return usuario
            
        # Se não encontrou por CPF, tentar por ID (fallback)
        try:
            user_id = int(cpf_or_id)
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            if usuario:
                print(f"✅ Usuário encontrado por ID: {usuario.nome}")
                return usuario
        except ValueError:
            pass  # Não é um número, continuar com erro
            
        print(f"❌ Usuário não encontrado: {cpf_or_id}")
        raise credentials_exception
        
    except JWTError as e:
        print(f"❌ Erro JWT: {e}")
        raise credentials_exception

def validar_cpf_basico(cpf: str) -> bool:
    """Validação básica de CPF (apenas formato)"""
    if not cpf:
        return False
    
    # Remover caracteres não numéricos
    cpf_numbers = ''.join(filter(str.isdigit, cpf))
    
    # Verificar se tem 11 dígitos
    if len(cpf_numbers) != 11:
        return False
    
    # Verificar se não são todos os dígitos iguais
    if cpf_numbers == cpf_numbers[0] * 11:
        return False
    
    return True

def verificar_permissao_admin(usuario_atual: Usuario = Depends(obter_usuario_atual)) -> Usuario:
    """Verificar se o usuário tem permissão de administrador"""
    if usuario_atual.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: permissão de administrador necessária"
        )
    return usuario_atual

def verificar_permissao_promoter(usuario_atual: Usuario = Depends(obter_usuario_atual)) -> Usuario:
    """Verificar se o usuário tem permissão de promoter ou admin"""
    if usuario_atual.tipo not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: permissão de promoter ou admin necessária"
        )
    return usuario_atual

def get_user_tipo(usuario: Usuario) -> str:
    """Helper function para obter tipo do usuário de forma consistente"""
    return str(usuario.tipo)
