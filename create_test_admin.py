#!/usr/bin/env python3
"""
Criar usuário admin de teste para validação automática
"""
import sys
import os
import asyncio
import httpx
import hashlib

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import get_db
from app.models import Usuario
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_cpf(cpf: str) -> str:
    """Hash do CPF para segurança"""
    salt = "test_salt_for_hashing"
    return hashlib.sha256(f"{cpf}{salt}".encode()).hexdigest()

def hash_password(password: str) -> str:
    """Hash da senha"""
    return pwd_context.hash(password)

async def create_test_admin():
    """Criar usuário admin de teste"""
    print("🔧 Criando usuário admin de teste...")
    
    # Dados do usuário admin
    admin_data = {
        "nome": "Admin Teste",
        "email": "admin@teste.com", 
        "cpf": "11111111111",  # CPF de teste
        "senha": "admin123",
        "tipo": "admin",
        "ativo": True
    }
    
    try:
        # Tentar criar via API
        async with httpx.AsyncClient(timeout=10) as client:
            # Primeiro verificar se o servidor está rodando
            try:
                response = await client.get("http://localhost:8000/docs")
                print("✅ Backend está rodando")
            except Exception as e:
                print(f"❌ Backend não está acessível: {e}")
                return False
            
            # Criar usuário via API
            response = await client.post(
                "http://localhost:8000/api/auth/register", 
                json=admin_data
            )
            
            if response.status_code == 201:
                print("✅ Admin criado via API com sucesso")
                user_data = response.json()
                
                # Salvar credenciais para testes
                credentials = {
                    "email": admin_data["email"],
                    "senha": admin_data["senha"],
                    "cpf": admin_data["cpf"],
                    "id": user_data.get("id"),
                    "nome": admin_data["nome"],
                    "tipo": admin_data["tipo"]
                }
                
                with open("test_credentials.json", "w") as f:
                    json.dump(credentials, f, indent=2)
                
                print("💾 Credenciais salvas em test_credentials.json")
                return True
                
            elif response.status_code == 400:
                error_data = response.json()
                if "já existe" in error_data.get("detail", "").lower():
                    print("ℹ️ Usuário admin já existe")
                    # Salvar credenciais mesmo assim
                    credentials = {
                        "email": admin_data["email"],
                        "senha": admin_data["senha"], 
                        "cpf": admin_data["cpf"],
                        "nome": admin_data["nome"],
                        "tipo": admin_data["tipo"]
                    }
                    
                    with open("test_credentials.json", "w") as f:
                        json.dump(credentials, f, indent=2)
                    
                    return True
                else:
                    print(f"❌ Erro ao criar usuário: {error_data}")
                    return False
            else:
                print(f"❌ Erro API: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro na criação do usuário: {e}")
        return False

async def test_login():
    """Testar login com credenciais criadas"""
    print("\n🔑 Testando login...")
    
    try:
        with open("test_credentials.json", "r") as f:
            creds = json.load(f)
        
        async with httpx.AsyncClient() as client:
            login_data = {
                "email": creds["email"],
                "senha": creds["senha"]
            }
            
            response = await client.post(
                "http://localhost:8000/api/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                print("✅ Login funcionando!")
                print(f"   Token: {auth_data['access_token'][:50]}...")
                
                # Salvar token para testes
                creds["token"] = auth_data["access_token"]
                with open("test_credentials.json", "w") as f:
                    json.dump(creds, f, indent=2)
                
                return True
            else:
                print(f"❌ Erro no login: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return False

async def main():
    """Função principal"""
    print("🚀 Configurando usuário de teste para validação automática\n")
    
    # Criar usuário admin
    success = await create_test_admin()
    if not success:
        print("❌ Falha na criação do usuário")
        return
    
    # Aguardar um pouco para o banco processar
    await asyncio.sleep(1)
    
    # Testar login
    login_success = await test_login()
    if not login_success:
        print("❌ Falha no teste de login")
        return
    
    print("\n✅ SETUP COMPLETO!")
    print("📋 Credenciais de teste:")
    print("   Email: admin@teste.com")
    print("   Senha: admin123")
    print("   CPF: 11111111111")
    print("\n🎯 Sistema pronto para testes automatizados!")

if __name__ == "__main__":
    asyncio.run(main())