#!/usr/bin/env python3
"""
Script para aplicar migração que remove constraint NOT NULL de empresa_id
"""
import os
from sqlalchemy import text
from app.database import engine

def apply_migration():
    """Aplica a migração para permitir empresa_id NULL"""
    
    sql_file = "fix_empresa_id_constraint.sql"
    
    if not os.path.exists(sql_file):
        print(f"Arquivo {sql_file} nao encontrado")
        return False
    
    try:
        # Ler o conteúdo do arquivo SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("Aplicando migracao...")
        
        # Executar a migração
        with engine.begin() as conn:
            # Dividir por comandos (separados por ;)
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            for i, command in enumerate(commands):
                if command:
                    print(f"Executando comando {i+1}...")
                    result = conn.execute(text(command))
                    
                    # Se for um SELECT, mostrar resultados
                    if command.upper().startswith('SELECT'):
                        rows = result.fetchall()
                        if rows:
                            print("Resultado:")
                            for row in rows:
                                print(f"  {row}")
        
        print("Migracao aplicada com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao aplicar migracao: {e}")
        return False

if __name__ == "__main__":
    apply_migration()