#!/usr/bin/env python3
"""
Configurar usuarios de demonstracao no banco de dados
Admin: CPF 000.000.000-00 / Senha 0000
Promoter: CPF 111.111.111-11 / Senha promoter123
"""

import sqlite3
import hashlib
from passlib.context import CryptContext

# Contexto para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash da senha"""
    return pwd_context.hash(password)

def hash_cpf(cpf: str) -> str:
    """Hash do CPF para seguranca"""
    cpf_clean = cpf.replace(".", "").replace("-", "")
    salt = "test_salt_for_hashing"
    return hashlib.sha256(f"{cpf_clean}{salt}".encode()).hexdigest()

def setup_demo_users():
    """Configurar usuarios de demonstracao"""
    print("[SETUP] Configurando usuarios de demonstracao...")
    
    # Conectar ao banco SQLite
    conn = sqlite3.connect('backend/eventos.db')
    cursor = conn.cursor()
    
    # Dados dos usuarios
    users = [
        {
            "nome": "Admin Demo",
            "email": "admin@demo.com",
            "cpf": "00000000000",
            "cpf_display": "000.000.000-00",
            "senha": "0000",
            "tipo": "admin"
        },
        {
            "nome": "Promoter Demo",
            "email": "promoter@demo.com", 
            "cpf": "11111111111",
            "cpf_display": "111.111.111-11",
            "senha": "promoter123",
            "tipo": "promoter"
        }
    ]
    
    try:
        for user_data in users:
            cpf_hash = hash_cpf(user_data["cpf"])
            senha_hash = hash_password(user_data["senha"])
            
            # Verificar se usuario existe pelo CPF
            cursor.execute("SELECT id FROM usuarios WHERE cpf = ?", (cpf_hash,))
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar usuario existente
                cursor.execute("""
                    UPDATE usuarios 
                    SET nome = ?, email = ?, senha_hash = ?, tipo = ?, ativo = 1
                    WHERE cpf = ?
                """, (user_data["nome"], user_data["email"], senha_hash, user_data["tipo"], cpf_hash))
                print(f"[UPDATE] Usuario {user_data['nome']} atualizado")
            else:
                # Verificar se email ja existe
                cursor.execute("SELECT id FROM usuarios WHERE email = ?", (user_data["email"],))
                email_exists = cursor.fetchone()
                
                if email_exists:
                    # Atualizar por email
                    cursor.execute("""
                        UPDATE usuarios 
                        SET nome = ?, cpf = ?, senha_hash = ?, tipo = ?, ativo = 1
                        WHERE email = ?
                    """, (user_data["nome"], cpf_hash, senha_hash, user_data["tipo"], user_data["email"]))
                    print(f"[UPDATE] Usuario {user_data['nome']} atualizado via email")
                else:
                    # Criar novo usuario
                    cursor.execute("""
                        INSERT INTO usuarios (nome, email, cpf, senha_hash, tipo, ativo)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (user_data["nome"], user_data["email"], cpf_hash, senha_hash, user_data["tipo"]))
                    print(f"[CREATE] Usuario {user_data['nome']} criado")
            
            print(f"         CPF: {user_data['cpf_display']}")
            print(f"         Senha: {user_data['senha']}")
            print(f"         Email: {user_data['email']}")
            print(f"         Tipo: {user_data['tipo']}")
            print()
        
        conn.commit()
        
        print("="*60)
        print("CREDENCIAIS DE DEMONSTRACAO CONFIGURADAS!")
        print("="*60)
        print("\n[ADMIN]:")
        print("  CPF: 000.000.000-00")
        print("  Senha: 0000")
        print("  Email: admin@demo.com")
        print("\n[PROMOTER]:")
        print("  CPF: 111.111.111-11")
        print("  Senha: promoter123")
        print("  Email: promoter@demo.com")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Falha ao configurar usuarios: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    setup_demo_users()