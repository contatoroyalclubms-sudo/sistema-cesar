#!/usr/bin/env python3
"""
Resetar e criar usuarios de demonstracao corretos
"""

import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    """Hash da senha com bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def reset_and_create():
    """Resetar e criar usuarios"""
    print("[RESET] Limpando e recriando usuarios...")
    
    conn = sqlite3.connect('backend/eventos.db')
    cursor = conn.cursor()
    
    try:
        # Primeiro, vamos ver todos os usuarios existentes
        cursor.execute("SELECT id, cpf, nome, email FROM usuarios")
        existing = cursor.fetchall()
        print(f"\n[INFO] Usuarios existentes: {len(existing)}")
        
        # Limpar TODOS os usuarios para comecar do zero
        cursor.execute("DELETE FROM usuarios")
        print(f"[CLEAN] Removidos {cursor.rowcount} usuarios")
        
        # Criar usuario admin
        cursor.execute("""
            INSERT INTO usuarios (cpf, nome, email, senha_hash, tipo, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "00000000000",  # CPF sem pontos/tracos
            "Admin Demo",
            "admin@demo.com",
            hash_password("0000"),
            "admin",
            1
        ))
        print("[CREATE] Admin criado - CPF: 00000000000, Senha: 0000")
        
        # Criar usuario promoter
        cursor.execute("""
            INSERT INTO usuarios (cpf, nome, email, senha_hash, tipo, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "11111111111",  # CPF sem pontos/tracos
            "Promoter Demo",
            "promoter@demo.com",
            hash_password("promoter123"),
            "promoter",
            1
        ))
        print("[CREATE] Promoter criado - CPF: 11111111111, Senha: promoter123")
        
        conn.commit()
        
        # Verificar resultado
        cursor.execute("SELECT cpf, nome, email, tipo FROM usuarios")
        final_users = cursor.fetchall()
        
        print("\n" + "="*70)
        print("USUARIOS CRIADOS COM SUCESSO:")
        print("="*70)
        for user in final_users:
            print(f"\nCPF: {user[0]}")
            print(f"Nome: {user[1]}")
            print(f"Email: {user[2]}")
            print(f"Tipo: {user[3]}")
        
        print("\n" + "="*70)
        print("CREDENCIAIS PARA LOGIN:")
        print("="*70)
        print("\nADMIN:")
        print("  CPF: 00000000000 (sem pontos/tracos)")
        print("  Senha: 0000")
        print("\nPROMOTER:")
        print("  CPF: 11111111111 (sem pontos/tracos)")
        print("  Senha: promoter123")
        print("="*70)
        
    except Exception as e:
        print(f"[ERRO] {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_and_create()