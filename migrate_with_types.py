#!/usr/bin/env python3
"""
Migração de dados com conversão de tipos
"""
import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def convert_value(value, column_name, data_type):
    """Converte valores entre SQLite e PostgreSQL"""
    if value is None:
        return None
    
    # Conversão de boolean
    if data_type == 'boolean':
        return bool(value) if isinstance(value, int) else value
    
    # Conversão de timestamp/datetime
    if 'timestamp' in data_type.lower() or 'datetime' in data_type.lower():
        return value  # SQLAlchemy já converte automaticamente
    
    return value

def migrate_with_type_conversion():
    """Migra dados com conversão de tipos apropriada"""
    print("📦 MIGRAÇÃO COM CONVERSÃO DE TIPOS")
    print("=" * 50)
    
    try:
        import psycopg2
        
        # Conectar bancos
        sqlite_conn = sqlite3.connect("paineluniversal.db")
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        pg_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="paineluniversal",
            user="painel_user",
            password="painel123"
        )
        pg_cursor = pg_conn.cursor()
        
        # Definir mapeamento de colunas boolean
        boolean_columns = {
            'empresas': ['ativa'],
            'usuarios': ['ativo'],
            'produtos': ['controla_estoque']
        }
        
        tables_to_migrate = ['empresas', 'usuarios', 'produtos']
        
        for table_name in tables_to_migrate:
            print(f"\n🔄 Migrando: {table_name}")
            
            # Obter dados do SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  ⏭️ Tabela vazia")
                continue
            
            print(f"  📊 {len(rows)} registros")
            
            # Obter estrutura PostgreSQL
            pg_cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            pg_columns_info = {col[0]: col[1] for col in pg_cursor.fetchall()}
            
            migrated = 0
            
            for row in rows:
                try:
                    row_dict = dict(row)
                    
                    # Filtrar e converter valores
                    converted_data = {}
                    for col, value in row_dict.items():
                        if col in pg_columns_info:
                            data_type = pg_columns_info[col]
                            converted_value = convert_value(value, col, data_type)
                            converted_data[col] = converted_value
                    
                    if not converted_data:
                        continue
                    
                    # Inserir dados
                    columns = list(converted_data.keys())
                    values = list(converted_data.values())
                    placeholders = ', '.join(['%s'] * len(values))
                    
                    insert_sql = f"""
                        INSERT INTO {table_name} ({', '.join(columns)}) 
                        VALUES ({placeholders})
                        ON CONFLICT (id) DO UPDATE SET
                        {', '.join([f'{col} = EXCLUDED.{col}' for col in columns if col != 'id'])}
                    """
                    
                    pg_cursor.execute(insert_sql, values)
                    migrated += 1
                    
                except Exception as e:
                    print(f"    ⚠️ Erro: {str(e)[:80]}...")
                    pg_conn.rollback()
                    continue
            
            pg_conn.commit()
            print(f"  ✅ {migrated} registros migrados")
        
        # Verificação final
        print(f"\n🔍 VERIFICAÇÃO:")
        for table in tables_to_migrate:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = pg_cursor.fetchone()[0]
            print(f"  📊 {table}: {count} registros")
        
        sqlite_conn.close()
        pg_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_with_type_conversion()
