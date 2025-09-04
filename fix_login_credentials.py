#!/usr/bin/env python3
"""
Corrigir problema de login - criar usuarios com senha simples
"""

import sqlite3
import hashlib
import bcrypt

def simple_hash_password(password: str) -> str:
    """Hash simples da senha com bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def hash_cpf(cpf: str) -> str:
    """Hash do CPF"""
    cpf_clean = cpf.replace(".", "").replace("-", "")
    salt = "test_salt_for_hashing"
    return hashlib.sha256(f"{cpf_clean}{salt}".encode()).hexdigest()

def fix_credentials():
    """Corrigir credenciais no banco"""
    print("[FIX] Corrigindo credenciais de login...")
    
    # Conectar ao banco
    conn = sqlite3.connect('backend/eventos.db')
    cursor = conn.cursor()
    
    try:
        # Primeiro, vamos verificar a estrutura da tabela
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        print("\n[INFO] Estrutura da tabela usuarios:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]}")
        
        # Deletar usuarios existentes com esses emails para recriar
        cursor.execute("DELETE FROM usuarios WHERE email IN ('admin@demo.com', 'promoter@demo.com')")
        print(f"\n[CLEAN] Removidos {cursor.rowcount} usuarios existentes")
        
        # Criar usuarios novos com senhas corretas
        users = [
            ("Admin Demo", "admin@demo.com", hash_cpf("00000000000"), simple_hash_password("0000"), "admin"),
            ("Promoter Demo", "promoter@demo.com", hash_cpf("11111111111"), simple_hash_password("promoter123"), "promoter")
        ]
        
        for user in users:
            cursor.execute("""
                INSERT INTO usuarios (nome, email, cpf, senha_hash, tipo, ativo)
                VALUES (?, ?, ?, ?, ?, 1)
            """, user)
            print(f"[CREATE] Usuario {user[0]} criado")
        
        conn.commit()
        
        # Verificar usuarios criados
        cursor.execute("SELECT nome, email, tipo FROM usuarios WHERE email IN ('admin@demo.com', 'promoter@demo.com')")
        users = cursor.fetchall()
        
        print("\n" + "="*60)
        print("USUARIOS CONFIGURADOS:")
        print("="*60)
        for user in users:
            print(f"\nNome: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Tipo: {user[2]}")
            if "Admin" in user[0]:
                print("CPF: 000.000.000-00")
                print("Senha: 0000")
            else:
                print("CPF: 111.111.111-11")
                print("Senha: promoter123")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"[ERRO] {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_credentials()