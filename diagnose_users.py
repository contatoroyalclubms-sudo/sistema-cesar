#!/usr/bin/env python3
"""
Script para diagnosticar usuários no banco de dados
"""

import sqlite3
import sys
from pathlib import Path

def diagnose_users():
    """Diagnostica estado dos usuários no banco"""
    db_path = Path("eventos.db")
    
    if not db_path.exists():
        print("❌ Banco de dados 'eventos.db' não encontrado!")
        return
    
    print(f"✅ Banco encontrado: {db_path.absolute()}")
    
    try:
        conn = sqlite3.connect('eventos.db')
        cursor = conn.cursor()
        
        # Verificar se tabela usuarios existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Tabela 'usuarios' não existe!")
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📋 Tabelas existentes: {[t[0] for t in tables]}")
            
        else:
            print("✅ Tabela 'usuarios' existe")
            
            # Contar usuários
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            print(f"👥 Total de usuários: {count}")
            
            if count > 0:
                # Listar usuários existentes
                cursor.execute("SELECT cpf, nome, tipo_usuario FROM usuarios LIMIT 10")
                users = cursor.fetchall()
                print("\n📋 Usuários encontrados:")
                for user in users:
                    print(f"  CPF: {user[0]}, Nome: {user[1]}, Tipo: {user[2]}")
                    
                # Verificar se usuário específico existe
                cursor.execute("SELECT cpf, nome, tipo_usuario FROM usuarios WHERE cpf = ?", ("06601206154",))
                specific_user = cursor.fetchone()
                if specific_user:
                    print(f"\n✅ Usuário 06601206154 encontrado: {specific_user}")
                else:
                    print(f"\n❌ Usuário 06601206154 NÃO encontrado")
                    
            else:
                print("❌ Nenhum usuário encontrado na tabela!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")

if __name__ == "__main__":
    diagnose_users()
