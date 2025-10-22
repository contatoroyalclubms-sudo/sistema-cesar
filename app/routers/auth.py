from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt
import hashlib

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])
security = HTTPBearer()

# Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@meep.com.br",
                "senha": "password123"
            }
        }
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    meta: Optional[dict] = None

# Configuração JWT (em produção, usar variáveis de ambiente)
SECRET_KEY = "nip-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

@router.post("/login", response_model=TokenResponse, status_code=200)
async def auth_login(credentials: LoginRequest):
    """
    Realizar login e obter token JWT
    
    - **email**: Email do usuário (ex: admin@meep.com.br)
    - **senha**: Senha do usuário
    
    Retorna token JWT válido por 1 hora.
    """
    # Validação simples (em produção, usar hash bcrypt e banco de dados)
    valid_users = {
        "admin@meep.com.br": "admin123",
        "user@nip.com.br": "user123"
    }
    
    if credentials.email not in valid_users or valid_users[credentials.email] != credentials.senha:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Gerar token JWT
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": credentials.email,
        "exp": expire,
        "iat": now,
        "type": "access_token"
    }
    
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=APIResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obter informações do usuário atual via token JWT
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        return APIResponse(
            status="success",
            message="Usuário autenticado",
            data={
                "email": email,
                "authenticated": True,
                "token_expires": payload.get("exp")
            }
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
