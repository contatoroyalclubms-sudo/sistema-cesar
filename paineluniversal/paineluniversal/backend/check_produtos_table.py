"""
Script para verificar a estrutura da tabela produtos no banco de dados
"""
import os
import sys
sys.path.append(os.getcwd())
from app.database import get_db
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

def check_produtos_table():
    # Conectar ao banco
    db = next(get_db())
    
    # Verificar estrutura da tabela produtos
    inspector = inspect(db.bind)
    columns = inspector.get_columns('produtos')
    
    print('=== ESTRUTURA DA TABELA PRODUTOS ===')
    for col in columns:
        nullable = 'NULL' if col['nullable'] else 'NOT NULL'
        print(f'{col["name"]}: {col["type"]} {nullable}')
    
    # Verificar se evento_id existe
    evento_id_exists = any(col['name'] == 'evento_id' for col in columns)
    print(f'\n=== CAMPO evento_id EXISTE: {evento_id_exists} ===')
    
    if evento_id_exists:
        evento_id_col = next(col for col in columns if col['name'] == 'evento_id')
        nullable_status = "NOT NULL" if not evento_id_col['nullable'] else "NULL" 
        print(f'evento_id: {evento_id_col["type"]} {nullable_status}')
    
    db.close()

if __name__ == "__main__":
    check_produtos_table()
