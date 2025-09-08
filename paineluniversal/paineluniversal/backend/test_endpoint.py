#!/usr/bin/env python3
"""
Endpoint temporário para testar schema corrigido
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()

# Schema corrigido para teste
class UsuarioCompleto(BaseModel):
    id: int
    cpf: str
    nome: str
    email: str
    telefone: Optional[str] = None
    tipo: str  # Usar string em vez de enum para funcionar
    ativo: bool
    ultimo_login: Optional[datetime] = None
    criado_em: datetime
    
    class Config:
        from_attributes = True

@app.get("/test-user-schema")
async def test_user_schema(db: Session = Depends(get_db)):
    """Endpoint para testar schema corrigido"""
    
    usuario = db.query(Usuario).filter(Usuario.cpf == "06601206156").first()
    
    if not usuario:
        return {"error": "Usuário não encontrado"}
    
    # Criar dict manualmente para garantir todos os campos
    user_data = {
        "id": usuario.id,
        "cpf": usuario.cpf,
        "nome": usuario.nome,
        "email": usuario.email,
        "telefone": usuario.telefone,
        "tipo": usuario.tipo.value if usuario.tipo else None,
        "ativo": usuario.ativo,
        "ultimo_login": usuario.ultimo_login,
        "criado_em": usuario.criado_em
    }
    
    return {
        "status": "success",
        "message": "Schema corrigido funcionando",
        "user_data": user_data,
        "fields_present": {
            "cpf": user_data["cpf"] is not None,
            "tipo": user_data["tipo"] is not None,
            "all_fields": len([k for k, v in user_data.items() if v is not None])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
