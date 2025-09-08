#!/usr/bin/env python3
"""Create SQLite database with all tables for development"""

import os
import sys
from sqlalchemy import create_engine, text
from app.database import settings, Base

def create_sqlite_database():
    """Create SQLite database with all tables"""
    
    # Remove arquivo SQLite existente se necessário
    db_file = "paineluniversal.db"
    if os.path.exists(db_file):
        print(f"Removendo banco existente: {db_file}")
        os.remove(db_file)
    
    # Criar engine
    print(f"Criando banco SQLite: {settings.database_url}")
    engine = create_engine(settings.database_url)
    
    # Importar todos os modelos para garantir que as tabelas sejam criadas
    from app import models
    
    # Criar todas as tabelas
    print("Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    
    # Adicionar dados de exemplo
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Verificar se já existem usuários
        existing_user = db.query(models.Usuario).filter(
            models.Usuario.email == "admin@paineluniversal.com"
        ).first()
        
        if not existing_user:
            print("Criando usuário admin padrão...")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            admin_user = models.Usuario(
                nome="Admin Universal",
                email="admin@paineluniversal.com",
                telefone="(11) 99999-9999",
                hashed_password=pwd_context.hash("admin123"),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            
            # Promoter de exemplo
            promoter_user = models.Usuario(
                nome="Promoter Teste",
                email="promoter@paineluniversal.com", 
                telefone="(11) 98888-8888",
                hashed_password=pwd_context.hash("promoter123"),
                role="promoter",
                is_active=True
            )
            db.add(promoter_user)
            
            db.commit()
            print("Usuários padrão criados!")
            print("Admin: admin@paineluniversal.com / admin123")
            print("Promoter: promoter@paineluniversal.com / promoter123")
        
        # Criar empresa de exemplo se não existir
        existing_empresa = db.query(models.Empresa).first()
        if not existing_empresa:
            print("Criando empresa de exemplo...")
            empresa = models.Empresa(
                nome="Empresa Universal",
                cnpj="12345678000123",
                telefone="(11) 3333-3333",
                email="contato@empresa.com",
                endereco="Rua Exemplo, 123"
            )
            db.add(empresa)
            db.commit()
            print("Empresa de exemplo criada!")
    
    print("\n✅ Banco SQLite criado com sucesso!")
    print(f"📁 Localização: {os.path.abspath(db_file)}")
    print("\n🚀 Para iniciar o servidor:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload --port 8000")
    print("\n🌐 URLs de acesso:")
    print("   API: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    create_sqlite_database()
