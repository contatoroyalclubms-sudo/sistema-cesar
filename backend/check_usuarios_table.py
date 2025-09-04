#!/usr/bin/env python3
"""
Script para verificar a estrutura atual da tabela usuarios
"""

from sqlalchemy import create_engine, text
from app.database import settings

def check_usuarios_table():
    """Verifica a estrutura da tabela usuarios"""
    
    engine = create_engine(settings.database_url)
    
    with engine.connect() as connection:
        try:
            # Verificar estrutura da tabela
            result = connection.execute(text("PRAGMA table_info(usuarios);"))
            columns = result.fetchall()
            
            print("📋 Estrutura atual da tabela usuarios:")
            print("-" * 60)
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                nullable = "NOT NULL" if notnull else "NULL"
                print(f"{name:20} | {type_:15} | {nullable:10} | PK: {bool(pk)}")
            
            print("\n" + "=" * 60)
            
            # Verificar se há usuários sem empresa
            result = connection.execute(text("""
                SELECT COUNT(*) as total,
                       COUNT(empresa_id) as com_empresa,
                       COUNT(*) - COUNT(empresa_id) as sem_empresa
                FROM usuarios;
            """))
            stats = result.fetchone()
            
            print("📊 Estatísticas de usuários:")
            print(f"Total de usuários: {stats[0]}")
            print(f"Com empresa: {stats[1]}")
            print(f"Sem empresa: {stats[2]}")
            
            if stats[2] > 0:
                print("\n✅ Tabela já permite usuários sem empresa!")
            else:
                print("\n⚠️  Todos os usuários estão vinculados a uma empresa")
                
        except Exception as e:
            print(f"❌ Erro ao verificar tabela: {e}")

if __name__ == "__main__":
    check_usuarios_table()
