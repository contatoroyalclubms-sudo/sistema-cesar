#!/usr/bin/env python3
"""
Teste de conexão com novo usuário
"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_new_credentials():
    """Testa com novas credenciais"""
    print("🔍 Testando conexão com painel_user...")
    
    try:
        import psycopg2
        from sqlalchemy import create_engine, text
        
        # Teste direto
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="paineluniversal",
            user="painel_user",
            password="painel123"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, current_database();")
        result = cursor.fetchone()
        print(f"✅ Conectado como: {result[0]} no banco: {result[1]}")
        cursor.close()
        conn.close()
        
        # Teste SQLAlchemy
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test;"))
            test_result = result.fetchone()
            print(f"✅ SQLAlchemy funcionando: {test_result[0]}")
        
        print("🎉 Conexão PostgreSQL configurada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_new_credentials()
    sys.exit(0 if success else 1)
