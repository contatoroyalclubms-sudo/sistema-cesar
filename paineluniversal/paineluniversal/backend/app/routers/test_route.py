"""
Rota de teste para debug
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.auth_functions import verificar_senha, gerar_hash_senha
from pydantic import BaseModel

router = APIRouter()

class TestLogin(BaseModel):
    cpf: str
    senha: str

@router.post("/test-login")
def test_login(data: TestLogin, db: Session = Depends(get_db)):
    """Teste de login sem nenhuma dependência externa"""
    try:
        # Buscar usuário
        usuario = db.query(Usuario).filter(Usuario.cpf == data.cpf).first()
        
        if not usuario:
            return {"success": False, "message": "User not found", "cpf": data.cpf}
        
        # Verificar senha
        senha_ok = verificar_senha(data.senha, usuario.senha_hash)
        
        return {
            "success": senha_ok,
            "user_found": True,
            "user_name": usuario.nome,
            "user_type": usuario.tipo,
            "user_active": usuario.ativo,
            "password_match": senha_ok
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    """Teste de conexão com banco"""
    try:
        count = db.query(Usuario).count()
        return {"success": True, "user_count": count}
    except Exception as e:
        return {"success": False, "error": str(e)}