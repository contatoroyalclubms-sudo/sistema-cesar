"""
Autenticação COMPLETAMENTE sem Redis ou cache
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
import os

# NÃO IMPORTAR NADA QUE POSSA USAR REDIS
from app.database import get_db
from app.models import Usuario
from passlib.context import CryptContext

router = APIRouter()

# Configurações locais
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing local
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    cpf: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: dict

def verificar_senha_local(senha_plain: str, senha_hash: str) -> bool:
    """Verificar senha localmente sem cache"""
    try:
        return pwd_context.verify(senha_plain, senha_hash)
    except:
        return False

def create_access_token_local(data: dict, expires_delta: timedelta = None):
    """Criar token localmente"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
def login_no_redis(request: LoginRequest, db: Session = Depends(get_db)):
    """Login completamente sem Redis"""
    print(f"🔍 [NO_REDIS] Login attempt for CPF: {request.cpf}")
    
    try:
        # Limpar CPF
        cpf_limpo = request.cpf.replace(".", "").replace("-", "").strip()
        print(f"✅ [NO_REDIS] CPF cleaned: {cpf_limpo}")
        
        # Buscar usuário diretamente no banco
        usuario = db.query(Usuario).filter(Usuario.cpf == cpf_limpo).first()
        
        if not usuario:
            print(f"❌ [NO_REDIS] User not found: {cpf_limpo}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CPF ou senha incorretos"
            )
        
        print(f"✅ [NO_REDIS] User found: {usuario.nome}")
        
        # Verificar senha localmente
        if not verificar_senha_local(request.senha, usuario.senha_hash):
            print(f"❌ [NO_REDIS] Invalid password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CPF ou senha incorretos"
            )
        
        print(f"✅ [NO_REDIS] Password verified")
        
        # Verificar se usuário está ativo
        if usuario.ativo is False:
            print(f"❌ [NO_REDIS] User inactive: {cpf_limpo}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        print(f"✅ [NO_REDIS] User is active")
        
        # Criar token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token_local(
            data={"sub": str(usuario.id), "cpf": usuario.cpf},
            expires_delta=access_token_expires
        )
        
        print(f"✅ [NO_REDIS] Token created")
        
        # Atualizar último login
        usuario.ultimo_login = datetime.utcnow()
        db.commit()
        print(f"✅ [NO_REDIS] Last login updated")
        
        # Criar dados do usuário
        usuario_data = {
            "id": usuario.id,
            "nome": usuario.nome,
            "cpf": usuario.cpf,
            "email": usuario.email,
            "telefone": usuario.telefone,
            "tipo": usuario.tipo or "admin",
            "ativo": usuario.ativo if usuario.ativo is not None else True,
            "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None,
            "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None
        }
        
        print(f"✅ [NO_REDIS] User data created: {list(usuario_data.keys())}")
        
        # Retornar resposta
        response = {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": usuario_data
        }
        
        print(f"✅ [NO_REDIS] Login successful for {usuario.nome}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [NO_REDIS] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/test")
def test_endpoint():
    """Endpoint de teste"""
    return {"status": "ok", "message": "Auth NO_REDIS working"}