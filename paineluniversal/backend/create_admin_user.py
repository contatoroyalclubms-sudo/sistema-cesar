#!/usr/bin/env python3
"""
Script para criar usuário admin inicial no sistema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, get_db
from app.models import Usuario, Base
from app.auth import gerar_hash_senha
from sqlalchemy.orm import Session

def create_admin_user():
    """Criar usuário admin inicial"""
    
    # Garantir que as tabelas existem
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    try:
        # Verificar se já existe admin
        admin_exists = db.query(Usuario).filter(Usuario.tipo == "admin").first()
        if admin_exists:
            print(f"AVISO: Usuario admin ja existe: {admin_exists.nome} ({admin_exists.cpf})")
            return
        
        # Criar usuário admin padrão
        admin_user = Usuario(
            cpf="000.000.000-11",  # CPF fake mas válido para testes
            nome="Administrador Sistema",
            email="admin@paineluniversal.com",
            telefone="(11) 99999-9999",
            senha_hash=gerar_hash_senha("admin123"),
            tipo="admin",
            ativo=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("OK - Usuario admin criado com sucesso!")
        print(f"   Nome: {admin_user.nome}")
        print(f"   CPF: {admin_user.cpf}")
        print(f"   Email: {admin_user.email}")
        print(f"   Senha: admin123")
        print(f"   Tipo: {admin_user.tipo.value}")
        print(f"   ID: {admin_user.id}")
        
    except Exception as e:
        print(f"ERRO ao criar usuario admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()