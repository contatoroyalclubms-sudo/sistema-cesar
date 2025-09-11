#!/usr/bin/env python3
"""
Migração de dados SQLite para PostgreSQL - Versão corrigida
"""
import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def migrate_data_fixed():
    """Migra dados com melhor tratamento de erros"""
    print("📦 MIGRAÇÃO DE DADOS SQLite → PostgreSQL (Corrigida)")
    print("=" * 60)
    
    try:
        import psycopg2
        
        # Conectar ao SQLite
        sqlite_path = "paineluniversal.db"
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
        pg_cursor = pg_conn.cursor()
        
        # Tabelas com dados para migrar
        tables_to_migrate = ['empresas', 'usuarios', 'produtos']
        
        for table_name in tables_to_migrate:
            print(f"\n🔄 Migrando tabela: {table_name}")
            
            # Contar registros no SQLite
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = sqlite_cursor.fetchone()[0]
            
            if count == 0:
                print(f"  ⏭️ Tabela vazia, pulando...")
                continue
                
            print(f"  📊 {count} registros encontrados")
            
            # Obter estrutura da tabela no PostgreSQL
            pg_cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            pg_columns_info = pg_cursor.fetchall()
            pg_columns = [col[0] for col in pg_columns_info]
            
            print(f"  📄 Colunas PostgreSQL: {', '.join(pg_columns)}")
            
            # Obter todos os dados do SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            migrated_rows = 0
            
            for row in rows:
                try:
                    # Converter row para dict
                    row_dict = dict(row)
                    
                    # Filtrar colunas que existem no PostgreSQL
                    filtered_data = {k: v for k, v in row_dict.items() if k in pg_columns}
                    
                    if not filtered_data:
                        print(f"    ⚠️ Nenhuma coluna compatível para linha")
                        continue
                    
                    # Preparar insert
                    columns = list(filtered_data.keys())
                    values = list(filtered_data.values())
                    placeholders = ', '.join(['%s'] * len(values))
                    
                    insert_sql = f"""
                        INSERT INTO {table_name} ({', '.join(columns)}) 
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """
                    
                    pg_cursor.execute(insert_sql, values)
                    migrated_rows += 1
                    
                except Exception as e:
                    print(f"    ⚠️ Erro na linha: {str(e)[:100]}...")
                    continue
            
            pg_conn.commit()
            print(f"  ✅ {migrated_rows}/{count} registros migrados")
        
        # Verificar resultados
        print(f"\n🔍 VERIFICAÇÃO FINAL:")
        for table in tables_to_migrate:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cursor.fetchone()[0]
            print(f"  📊 {table}: {pg_count} registros no PostgreSQL")
        
        sqlite_conn.close()
        pg_conn.close()
        
        print(f"\n🎉 Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_data_fixed()
