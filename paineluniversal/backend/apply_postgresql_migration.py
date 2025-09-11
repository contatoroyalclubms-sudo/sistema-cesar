#!/usr/bin/env python3
"""
Script para aplicar migração PostgreSQL que remove constraint NOT NULL de empresa_id
"""
import os
from sqlalchemy import create_engine, text
from app.database import settings

def apply_postgresql_migration():
    """Aplica a migração PostgreSQL usando SQLAlchemy"""
    
    sql_file = "postgresql_migration.sql"
    
    if not os.path.exists(sql_file):
        print(f"Arquivo {sql_file} nao encontrado")
        return False
    
    try:
        # Ler o conteúdo do arquivo SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("=== Aplicando migracao PostgreSQL ===")
        print(f"Database URL: {settings.database_url}")
        
        # Criar engine para PostgreSQL
        engine = create_engine(settings.database_url)
        
        # Executar a migração
        with engine.begin() as conn:
            # Dividir comandos e executar um por vez
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
            
            for i, command in enumerate(commands):
                if command.upper() in ['BEGIN', 'COMMIT']:
                    continue  # Pular BEGIN/COMMIT pois já estamos em transação
                    
                if command:
                    print(f"Executando comando {i+1}...")
                    result = conn.execute(text(command))
                    
                    # Se for um SELECT, mostrar resultados
                    if command.upper().strip().startswith('SELECT'):
                        try:
                            rows = result.fetchall()
                            if rows:
                                print("Resultado:")
                                for row in rows:
                                    print(f"  {row}")
                        except:
                            pass
        
        print("=== Migracao aplicada com sucesso! ===")
        return True
        
    except Exception as e:
        print(f"Erro ao aplicar migracao: {e}")
        return False

if __name__ == "__main__":
    apply_postgresql_migration()