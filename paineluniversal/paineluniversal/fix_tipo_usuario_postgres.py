#!/usr/bin/env python3
"""
Script para corrigir o campo tipo_usuario no PostgreSQL de produção
Atualiza tipo_usuario para ser igual ao campo tipo (em minúsculo)
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def fix_tipo_usuario_postgres():
    """Corrigir tipo_usuario no PostgreSQL de produção"""
    
    # URL do PostgreSQL (Railway)
    postgres_url = "postgresql://postgres:EjGldKWRbqmfhPFvDqUAqgWkNzGCAbJB@postgres.railway.internal:5432/railway"
    
    try:
        print("🔧 Conectando ao PostgreSQL de produção...")
        conn = psycopg2.connect(postgres_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar estado atual
        print("\n📋 Estado atual dos usuários:")
        cursor.execute("""
            SELECT id, cpf, nome, tipo, tipo_usuario 
            FROM usuarios 
            ORDER BY id
        """)
        
        usuarios = cursor.fetchall()
        for user in usuarios:
            print(f"  ID {user['id']}: {user['nome']} - tipo='{user['tipo']}' tipo_usuario='{user['tipo_usuario']}'")
        
        # Atualizar tipo_usuario para ser igual ao tipo (em minúsculo)
        print("\n🔄 Atualizando tipo_usuario...")
        cursor.execute("""
            UPDATE usuarios 
            SET tipo_usuario = LOWER(tipo)
            WHERE tipo IS NOT NULL AND tipo != ''
        """)
        
        rows_updated = cursor.rowcount
        print(f"✅ {rows_updated} usuários atualizados!")
        
        # Verificar resultado
        print("\n📋 Estado após atualização:")
        cursor.execute("""
            SELECT id, cpf, nome, tipo, tipo_usuario 
            FROM usuarios 
            ORDER BY id
        """)
        
        usuarios_updated = cursor.fetchall()
        for user in usuarios_updated:
            print(f"  ID {user['id']}: {user['nome']} - tipo='{user['tipo']}' tipo_usuario='{user['tipo_usuario']}'")
        
        # Confirmar mudanças
        conn.commit()
        print("\n🎉 Atualização confirmada no banco!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_tipo_usuario_postgres()
