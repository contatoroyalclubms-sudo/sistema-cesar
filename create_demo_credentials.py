#!/usr/bin/env python3
"""
Criar credenciais de demonstração no banco de dados
Admin: CPF 000.000.000-00 / Senha 0000
Promoter: CPF 111.111.111-11 / Senha promoter123
"""

import sys
import os
import asyncio
import hashlib
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Usuario, Base
from passlib.context import CryptContext

# Configuração do banco
DATABASE_URL = "sqlite:///./backend/eventos.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Contexto para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash da senha"""
    return pwd_context.hash(password)

def hash_cpf(cpf: str) -> str:
    """Hash do CPF para segurança"""
    # Remover formatação do CPF
    cpf_clean = cpf.replace(".", "").replace("-", "")
    salt = "test_salt_for_hashing"
    return hashlib.sha256(f"{cpf_clean}{salt}".encode()).hexdigest()

def create_demo_users():
    """Criar usuários de demonstração"""
    print("[SETUP] Criando credenciais de demonstracao...")
    
    # Criar tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Dados dos usuários
        users_data = [
            {
                "nome": "Admin Demo",
                "email": "admin@demo.com",
                "cpf": "00000000000",  # CPF sem formatação
                "cpf_display": "000.000.000-00",
                "senha": "0000",
                "tipo": "admin",
                "ativo": True
            },
            {
                "nome": "Promoter Demo", 
                "email": "promoter@demo.com",
                "cpf": "11111111111",  # CPF sem formatação
                "cpf_display": "111.111.111-11",
                "senha": "promoter123",
                "tipo": "promoter",
                "ativo": True
            }
        ]
        
        for user_data in users_data:
            # Verificar se usuário já existe
            existing_user = db.query(Usuario).filter(
                Usuario.cpf == hash_cpf(user_data["cpf"])
            ).first()
            
            if existing_user:
                print(f"[INFO] Usuario {user_data['nome']} ja existe, atualizando senha...")
                # Atualizar senha
                existing_user.senha_hash = hash_password(user_data["senha"])
                existing_user.nome = user_data["nome"]
                existing_user.email = user_data["email"]
                existing_user.tipo = user_data["tipo"]
                existing_user.ativo = user_data["ativo"]
                db.commit()
                print(f"[OK] Senha atualizada para {user_data['nome']}")
            else:
                # Criar novo usuário
                new_user = Usuario(
                    nome=user_data["nome"],
                    email=user_data["email"],
                    cpf=hash_cpf(user_data["cpf"]),
                    senha_hash=hash_password(user_data["senha"]),
                    tipo=user_data["tipo"],
                    ativo=user_data["ativo"]
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                print(f"[OK] Usuario criado: {user_data['nome']}")
                print(f"   CPF: {user_data['cpf_display']}")
                print(f"   Senha: {user_data['senha']}")
                print(f"   Email: {user_data['email']}")
                print(f"   Tipo: {user_data['tipo']}")
        
        print("\n" + "="*60)
        print("CREDENCIAIS DE DEMONSTRAÇÃO CRIADAS COM SUCESSO!")
        print("="*60)
        print("\n[ADMIN]:")
        print("   CPF: 000.000.000-00")
        print("   Senha: 0000")
        print("   Email: admin@demo.com")
        print("\n[PROMOTER]:")
        print("   CPF: 111.111.111-11")
        print("   Senha: promoter123")
        print("   Email: promoter@demo.com")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro ao criar usuarios: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def test_login():
    """Testar login com as credenciais criadas"""
    print("\n[TEST] Testando login com credenciais...")
    
    import httpx
    
    credentials_to_test = [
        {"cpf": "00000000000", "senha": "0000", "tipo": "Admin"},
        {"cpf": "11111111111", "senha": "promoter123", "tipo": "Promoter"}
    ]
    
    try:
        async with httpx.AsyncClient() as client:
            for cred in credentials_to_test:
                # Testar login via CPF
                response = await client.post(
                    "http://localhost:8000/api/auth/login",
                    json={"cpf": cred["cpf"], "senha": cred["senha"]}
                )
                
                if response.status_code == 200:
                    print(f"[OK] Login {cred['tipo']}: FUNCIONANDO")
                    data = response.json()
                    if "access_token" in data:
                        print(f"   Token recebido: {data['access_token'][:30]}...")
                else:
                    # Tentar com email também
                    email = "admin@demo.com" if cred["tipo"] == "Admin" else "promoter@demo.com"
                    response = await client.post(
                        "http://localhost:8000/api/auth/login",
                        json={"email": email, "senha": cred["senha"]}
                    )
                    
                    if response.status_code == 200:
                        print(f"[OK] Login {cred['tipo']} via email: FUNCIONANDO")
                    else:
                        print(f"[AVISO] Login {cred['tipo']}: HTTP {response.status_code}")
                        
    except Exception as e:
        print(f"[AVISO] Erro ao testar login: {e}")
        print("   (Certifique-se de que o backend está rodando)")

def main():
    """Função principal"""
    # Criar usuários
    success = create_demo_users()
    
    if success:
        # Testar login
        asyncio.run(test_login())
        
        print("\n[SUCESSO] SETUP COMPLETO!")
        print("Use estas credenciais para acessar o sistema:")
        print("   Admin: 000.000.000-00 / 0000")
        print("   Promoter: 111.111.111-11 / promoter123")
    else:
        print("\n[ERRO] Falha na criacao das credenciais")

if __name__ == "__main__":
    main()