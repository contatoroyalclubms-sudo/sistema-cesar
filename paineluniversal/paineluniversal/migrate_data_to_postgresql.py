#!/usr/bin/env python3
"""
Migração de dados SQLite para PostgreSQL
Transfere todos os dados existentes mantendo integridade
"""
import os
import sys
import sqlite3
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def migrate_data():
    """Migra dados do SQLite para PostgreSQL"""
    print("📦 MIGRAÇÃO DE DADOS SQLite → PostgreSQL")
    print("=" * 60)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Conectar ao SQLite
        sqlite_path = "paineluniversal.db"
        if not os.path.exists(sqlite_path):
            print(f"❌ Arquivo SQLite não encontrado: {sqlite_path}")
            return False
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Conectar ao PostgreSQL
        pg_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="paineluniversal",
            user="painel_user",
            password="painel123"
        )
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
        
        # Obter lista de tabelas do SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        print(f"📋 Tabelas encontradas no SQLite: {len(tables)}")
        
        migrated_count = 0
        
        for table_name in tables:
            if table_name.startswith('sqlite_'):
                continue
                
            print(f"\n🔄 Migrando tabela: {table_name}")
            
            # Contar registros no SQLite
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = sqlite_cursor.fetchone()[0]
            
            if count == 0:
                print(f"  ⏭️ Tabela vazia, pulando...")
                continue
            
            print(f"  📊 {count} registros encontrados")
            
            try:
                # Verificar se tabela existe no PostgreSQL
                pg_cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table_name,))
                
                if not pg_cursor.fetchone()[0]:
                    print(f"  ⚠️ Tabela {table_name} não existe no PostgreSQL, pulando...")
                    continue
                
                # Obter dados do SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table_name}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    continue
                
                # Obter colunas da primeira linha
                columns = list(rows[0].keys())
                
                # Verificar colunas no PostgreSQL
                pg_cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                
                pg_columns = [row[0] for row in pg_cursor.fetchall()]
                
                # Filtrar colunas que existem em ambos
                valid_columns = [col for col in columns if col in pg_columns]
                
                if not valid_columns:
                    print(f"  ❌ Nenhuma coluna compatível encontrada")
                    continue
                
                print(f"  📄 Colunas: {', '.join(valid_columns)}")
                
                # Preparar insert
                placeholders = ', '.join(['%s'] * len(valid_columns))
                insert_sql = f"""
                    INSERT INTO {table_name} ({', '.join(valid_columns)}) 
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """
                
                # Migrar dados
                migrated_rows = 0
                for row in rows:
                    try:
                        values = [row[col] for col in valid_columns]
                        pg_cursor.execute(insert_sql, values)
                        migrated_rows += 1
                    except Exception as e:
                        print(f"    ⚠️ Erro na linha: {e}")
                        continue
                
                pg_conn.commit()
                print(f"  ✅ {migrated_rows}/{count} registros migrados")
                migrated_count += 1
                
            except Exception as e:
                print(f"  ❌ Erro na tabela {table_name}: {e}")
                pg_conn.rollback()
                continue
        
        sqlite_conn.close()
        pg_conn.close()
        
        print(f"\n🎉 Migração concluída!")
        print(f"📊 {migrated_count} tabelas migradas com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verifica a migração comparando contadores"""
    print("\n🔍 VERIFICAÇÃO DA MIGRAÇÃO")
    print("=" * 40)
    
    try:
        import psycopg2
        
        # SQLite
        sqlite_conn = sqlite3.connect("paineluniversal.db")
        sqlite_cursor = sqlite_conn.cursor()
        
        # PostgreSQL
        pg_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="paineluniversal",
            user="painel_user",
            password="painel123"
        )
        pg_cursor = pg_conn.cursor()
        
        # Comparar tabelas principais
        important_tables = ['usuarios', 'eventos', 'empresas', 'produtos']
        
        for table in important_tables:
            try:
                # Contar SQLite
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # Contar PostgreSQL
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                pg_count = pg_cursor.fetchone()[0]
                
                status = "✅" if sqlite_count == pg_count else "⚠️"
                print(f"{status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
                
            except Exception as e:
                print(f"❌ {table}: Erro na verificação - {e}")
        
        sqlite_conn.close()
        pg_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Iniciando migração de dados...")
    
    success = migrate_data()
    if success:
        verify_migration()
        print("\n✅ Migração de dados concluída!")
    else:
        print("\n❌ Migração de dados falhou!")
    
    sys.exit(0 if success else 1)
