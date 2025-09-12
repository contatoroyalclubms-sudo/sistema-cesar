#!/usr/bin/env python3
"""
Setup Admin - Cria usuário admin com credenciais do .env
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório ao path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal, engine
from app.models import Base, Usuario
from sqlalchemy.exc import IntegrityError
import logging
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin():
    """Criar usuário admin com credenciais do ambiente"""
    
    # Pegar credenciais do ambiente ou usar padrão
    email = os.getenv("INITIAL_ADMIN_EMAIL", "toretomal@icloud.com")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "Sup3rSenha!123")
    cpf = os.getenv("INITIAL_ADMIN_CPF", "00000000000")
    name = os.getenv("INITIAL_ADMIN_NAME", "Admin Master")
    
    print("\n" + "="*60)
    print("    SETUP ADMIN - PAINEL UNIVERSAL")
    print("="*60)
    
    # Criar tabelas se não existirem
    print("\n[1] Criando tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("    [OK] Tabelas criadas/verificadas")
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Verificar se já existe
        existing = db.query(Usuario).filter(
            (Usuario.email == email) | (Usuario.cpf == cpf)
        ).first()
        
        if existing:
            print(f"\n[2] Usuário já existe:")
            print(f"    Email: {existing.email}")
            print(f"    CPF: {existing.cpf}")
            print(f"    Role: {existing.role}")
            
            # Perguntar se quer atualizar a senha
            response = input("\n    Deseja atualizar a senha? (s/n): ")
            if response.lower() == 's':
                existing.senha = hash_password(password)
                db.commit()
                print("    [OK] Senha atualizada com sucesso!")
            
            return existing
        
        # Criar novo admin
        print(f"\n[2] Criando novo usuário admin...")
        admin = Usuario(
            nome=name,
            email=email,
            cpf=cpf,
            senha=hash_password(password),
            role="admin",
            ativo=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"    [OK] Admin criado com sucesso!")
        print(f"    ID: {admin.id}")
        print(f"    Nome: {admin.nome}")
        print(f"    Email: {admin.email}")
        print(f"    CPF: {admin.cpf}")
        print(f"    Role: {admin.role}")
        
        return admin
        
    except IntegrityError as e:
        db.rollback()
        print(f"\n[ERRO] Conflito de dados: {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] Falha ao criar admin: {e}")
        return None
    finally:
        db.close()

def test_login():
    """Testar login do admin"""
    print("\n[3] Testando login...")
    
    email = os.getenv("INITIAL_ADMIN_EMAIL", "toretomal@icloud.com")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "Sup3rSenha!123")
    
    import httpx
    
    try:
        # Testar com CPF (sistema usa CPF)
        response = httpx.post(
            "http://localhost:8000/api/auth/login",
            json={
                "cpf": "00000000000",
                "senha": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    [OK] Login com CPF funcionou!")
            print(f"    Token: {data.get('access_token', '')[:50]}...")
            return True
        else:
            print(f"    [ERRO] Login falhou: {response.status_code}")
            print(f"    Resposta: {response.text}")
            
    except httpx.ConnectError:
        print("    [AVISO] Servidor nao esta rodando na porta 8000")
        print("    Execute: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"    [ERRO] Erro no teste: {e}")
    
    return False

def main():
    """Executar setup completo"""
    
    print("\n[CONFIG] Configuracao atual:")
    print(f"   Email: {os.getenv('INITIAL_ADMIN_EMAIL', 'toretomal@icloud.com')}")
    print(f"   Senha: {'*' * len(os.getenv('INITIAL_ADMIN_PASSWORD', 'Sup3rSenha!123'))}")
    print(f"   CPF: {os.getenv('INITIAL_ADMIN_CPF', '00000000000')}")
    print(f"   Nome: {os.getenv('INITIAL_ADMIN_NAME', 'Admin Master')}")
    
    # Criar admin
    admin = create_admin()
    
    if admin:
        # Testar login
        test_login()
        
        print("\n" + "="*60)
        print("    [OK] SETUP COMPLETO!")
        print("="*60)
        print("\n[PROXIMOS PASSOS]:")
        print("   1. Iniciar servidor: uvicorn app.main:app --reload")
        print("   2. Acessar Swagger: http://localhost:8000/docs")
        print("   3. Login no frontend: http://localhost:5174")
        print("\n[CREDENCIAIS]:")
        print(f"   CPF: 00000000000")
        print(f"   Senha: {os.getenv('INITIAL_ADMIN_PASSWORD', 'Sup3rSenha!123')}")
        print("\n")
    else:
        print("\n[ERRO] Setup falhou. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()