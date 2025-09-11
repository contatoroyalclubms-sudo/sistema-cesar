"""
Servidor completo com autenticação funcional
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funções de autenticação
try:
    from app.auth_functions import (
        gerar_hash_senha,
        verificar_senha,
        criar_access_token,
        autenticar_usuario,
        obter_usuario_atual,
        validar_cpf_basico
    )
    from app.database import get_db, engine
    from app.models import Base, Usuario
    print("✅ Módulos de autenticação importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    # Fallback para funções simplificadas
    from passlib.context import CryptContext
    from jose import jwt
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "supersecretkey123"
    ALGORITHM = "HS256"
    
    def gerar_hash_senha(senha: str) -> str:
        return pwd_context.hash(senha)
    
    def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
        return pwd_context.verify(senha_plain, senha_hash)
    
    def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

# Criar tabelas se não existirem
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas do banco de dados verificadas/criadas")
except Exception as e:
    print(f"⚠️ Aviso ao criar tabelas: {e}")

app = FastAPI(title="Sistema Universal v5 - Backend Completo")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class LoginRequest(BaseModel):
    cpf: str
    senha: str

class RegisterRequest(BaseModel):
    cpf: str
    nome: str
    email: str
    telefone: str
    senha: str
    tipo: Optional[str] = "cliente"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# Rotas principais
@app.get("/")
async def root():
    return {
        "sistema": "Sistema Universal v5 - Backend Completo",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "auth": "/api/auth/login",
            "register": "/api/auth/register",
            "health": "/api/health",
            "user": "/api/auth/me"
        }
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "backend": "running",
        "version": "5.0",
        "timestamp": datetime.now().isoformat()
    }

# Rotas de autenticação
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint de login com CPF e senha"""
    try:
        # Limpar CPF
        cpf_clean = ''.join(filter(str.isdigit, request.cpf))
        
        # Buscar usuário
        usuario = db.query(Usuario).filter(Usuario.cpf == cpf_clean).first()
        
        if not usuario:
            # Criar usuário admin padrão se não existir nenhum usuário
            usuarios_count = db.query(Usuario).count()
            if usuarios_count == 0:
                print("📝 Criando usuário admin padrão...")
                admin = Usuario(
                    cpf="00000000000",
                    nome="Administrador",
                    email="admin@sistema.com",
                    telefone="11999999999",
                    senha_hash=gerar_hash_senha("admin123"),
                    tipo="admin"
                )
                db.add(admin)
                db.commit()
                
                # Se o login é para o admin padrão
                if cpf_clean == "00000000000" and request.senha == "admin123":
                    usuario = admin
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="CPF ou senha incorretos"
                    )
            else:
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
        access_token = criar_access_token(
            data={"sub": usuario.cpf},
            expires_delta=timedelta(hours=24)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": usuario.id,
                "cpf": usuario.cpf,
                "nome": usuario.nome,
                "email": usuario.email,
                "tipo": usuario.tipo
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Endpoint de registro de novo usuário"""
    try:
        # Limpar CPF
        cpf_clean = ''.join(filter(str.isdigit, request.cpf))
        
        # Verificar se CPF já existe
        if db.query(Usuario).filter(Usuario.cpf == cpf_clean).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
        
        # Criar novo usuário
        novo_usuario = Usuario(
            cpf=cpf_clean,
            nome=request.nome,
            email=request.email,
            telefone=request.telefone,
            senha_hash=gerar_hash_senha(request.senha),
            tipo=request.tipo
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        # Criar token
        access_token = criar_access_token(
            data={"sub": novo_usuario.cpf},
            expires_delta=timedelta(hours=24)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": novo_usuario.id,
                "cpf": novo_usuario.cpf,
                "nome": novo_usuario.nome,
                "email": novo_usuario.email,
                "tipo": novo_usuario.tipo
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erro no registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

@app.get("/api/auth/me")
async def get_current_user(usuario: Usuario = Depends(obter_usuario_atual)):
    """Retorna o usuário atual baseado no token"""
    return {
        "id": usuario.id,
        "cpf": usuario.cpf,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo": usuario.tipo
    }

@app.post("/api/auth/verify-token")
async def verify_token(usuario: Usuario = Depends(obter_usuario_atual)):
    """Verifica se o token é válido"""
    return {
        "valid": True,
        "user": {
            "id": usuario.id,
            "cpf": usuario.cpf,
            "nome": usuario.nome,
            "tipo": usuario.tipo
        }
    }

# Rotas de teste para debug
@app.get("/api/test")
async def test():
    return {"message": "API funcionando!", "timestamp": datetime.now().isoformat()}

@app.post("/api/test/echo")
async def echo(data: dict):
    return {"received": data, "timestamp": datetime.now().isoformat()}

# Criar usuário admin na inicialização
@app.on_event("startup")
async def startup_event():
    """Criar usuário admin padrão se não existir"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Verificar se existe algum usuário admin
        admin = db.query(Usuario).filter(Usuario.tipo == "admin").first()
        if not admin:
            print("📝 Criando usuário admin padrão...")
            admin = Usuario(
                cpf="00000000000",
                nome="Administrador Sistema",
                email="admin@sistema.com",
                telefone="11999999999",
                senha_hash=gerar_hash_senha("admin123"),
                tipo="admin"
            )
            db.add(admin)
            
            # Criar também um usuário de teste
            test_user = Usuario(
                cpf="11111111111",
                nome="Usuário Teste",
                email="teste@sistema.com",
                telefone="11888888888",
                senha_hash=gerar_hash_senha("teste123"),
                tipo="cliente"
            )
            db.add(test_user)
            
            db.commit()
            print("✅ Usuários padrão criados:")
            print("   Admin: CPF: 00000000000, Senha: admin123")
            print("   Teste: CPF: 11111111111, Senha: teste123")
        else:
            print("✅ Usuário admin já existe")
    except Exception as e:
        print(f"⚠️ Erro ao verificar/criar usuários: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 SISTEMA UNIVERSAL V5 - BACKEND COMPLETO")
    print("="*60)
    print("📍 Servidor rodando em: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("🔐 Login padrão: CPF: 00000000000, Senha: admin123")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)