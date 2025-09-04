#!/usr/bin/env python3
"""
Correção definitiva do login - armazenar CPF sem hash para demonstração
"""

import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    """Hash da senha com bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def final_fix():
    """Corrigir definitivamente o problema de login"""
    print("[FIX] Aplicando correção definitiva de login...")
    
    conn = sqlite3.connect('backend/eventos.db')
    cursor = conn.cursor()
    
    try:
        # Limpar usuários de demo anteriores
        cursor.execute("DELETE FROM usuarios WHERE email IN ('admin@demo.com', 'promoter@demo.com')")
        
        # Criar usuários com CPF direto (sem hash) para demonstração
        admin_data = (
            "00000000000",  # CPF direto sem hash
            "Admin Demo",
            "admin@demo.com",
            None,  # telefone
            hash_password("0000"),  # senha com hash
            "admin",
            1,  # ativo
            None,  # ultimo_login
            None   # atualizado_em
        )
        
        promoter_data = (
            "11111111111",  # CPF direto sem hash
            "Promoter Demo",
            "promoter@demo.com",
            None,  # telefone
            hash_password("promoter123"),  # senha com hash
            "promoter",
            1,  # ativo
            None,  # ultimo_login
            None   # atualizado_em
        )
        
        # Inserir admin
        cursor.execute("""
            INSERT INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo, ativo, ultimo_login, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, admin_data)
        print("[OK] Admin criado")
        
        # Inserir promoter
        cursor.execute("""
            INSERT INTO usuarios (cpf, nome, email, telefone, senha_hash, tipo, ativo, ultimo_login, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, promoter_data)
        print("[OK] Promoter criado")
        
        conn.commit()
        
        # Verificar
        cursor.execute("SELECT cpf, nome, email, tipo FROM usuarios WHERE email IN ('admin@demo.com', 'promoter@demo.com')")
        users = cursor.fetchall()
        
        print("\n" + "="*60)
        print("CREDENCIAIS FINAIS CONFIGURADAS:")
        print("="*60)
        for user in users:
            print(f"\nCPF no banco: {user[0]}")
            print(f"Nome: {user[1]}")
            print(f"Email: {user[2]}")
            print(f"Tipo: {user[3]}")
            if "Admin" in user[1]:
                print("Login com: CPF=00000000000 Senha=0000")
            else:
                print("Login com: CPF=11111111111 Senha=promoter123")
        print("="*60)
        
        print("\n[INFO] Usuarios prontos para login!")
        print("[INFO] Use CPF sem pontos ou tracos")
        
    except Exception as e:
        print(f"[ERRO] {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    final_fix()