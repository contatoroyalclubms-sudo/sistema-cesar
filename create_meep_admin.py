#!/usr/bin/env python3
"""
Create admin user with credentials: admin@meep.com / admin123
"""

import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    """Hash da senha com bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_meep_admin():
    """Create admin user for testing"""
    print("[CREATE] Creating admin@meep.com user...")
    
    conn = sqlite3.connect('backend/eventos.db')
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", ("admin@meep.com",))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing user
            cursor.execute("""
                UPDATE usuarios 
                SET cpf = ?, nome = ?, senha_hash = ?, tipo = ?, ativo = ?
                WHERE email = ?
            """, (
                "99999999999",  # Unique CPF for this admin
                "Admin MEEP",
                hash_password("admin123"),
                "admin",
                1,
                "admin@meep.com"
            ))
            print("[UPDATE] Admin user updated")
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO usuarios (cpf, nome, email, senha_hash, tipo, ativo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "99999999999",  # Unique CPF
                "Admin MEEP",
                "admin@meep.com",
                hash_password("admin123"),
                "admin",
                1
            ))
            print("[CREATE] Admin user created")
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT cpf, nome, email, tipo FROM usuarios WHERE email = ?", ("admin@meep.com",))
        user = cursor.fetchone()
        
        print("\n" + "="*70)
        print("ADMIN USER CREATED SUCCESSFULLY:")
        print("="*70)
        print(f"Email: {user[2]}")
        print(f"Password: admin123")
        print(f"CPF: {user[0]}")
        print(f"Name: {user[1]}")
        print(f"Type: {user[3]}")
        print("="*70)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_meep_admin()