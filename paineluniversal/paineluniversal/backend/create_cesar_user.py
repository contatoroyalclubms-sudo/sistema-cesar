#!/usr/bin/env python3
"""
Script para criar o usuário César com CPF 06601206156
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Usuario
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session

def create_cesar_user():
    """Cria o usuário César com as credenciais especificadas"""
    
    db = next(get_db())
    
    try:
        # Verificar se já existe
        existing_user = db.query(Usuario).filter(Usuario.cpf == "06601206156").first()
        if existing_user:
            print(f"✅ Usuário já existe: {existing_user.nome}")
            return
        
        # Criar hash da senha
        senha_hash = generate_password_hash("101112")
        
        # Criar novo usuário
        novo_usuario = Usuario(
            cpf="06601206156",
            nome="César",
            email="rosemberg@gmail.com",
            telefone=None,
            senha_hash=senha_hash,
            tipo_usuario="admin",  # Fazer como ADMIN para ter acesso total
            ativo=True
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        print(f"✅ Usuário César criado com sucesso!")
        print(f"   ID: {novo_usuario.id}")
        print(f"   CPF: {novo_usuario.cpf}")
        print(f"   Nome: {novo_usuario.nome}")
        print(f"   Email: {novo_usuario.email}")
        print(f"   Tipo: {novo_usuario.tipo.value}")
        print(f"   Ativo: {novo_usuario.ativo}")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("👤 Criando usuário César...")
    create_cesar_user()
