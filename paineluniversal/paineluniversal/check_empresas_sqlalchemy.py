#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from sqlalchemy import text

def check_empresas_columns():
    """Verifica colunas da tabela empresas usando SQLAlchemy"""
    
    db = next(get_db())
    
    try:
        print("🔍 Verificando estrutura da tabela 'empresas':")
        print("=" * 50)
        
        # Verificar colunas
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='empresas' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        
        if columns:
            print("📋 Colunas encontradas:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("❌ Tabela 'empresas' não encontrada")
            
        # Verificar dados
        count_result = db.execute(text("SELECT COUNT(*) FROM empresas"))
        count = count_result.fetchone()[0]
        print(f"\n📊 Total de registros: {count}")
        
    except Exception as e:
        print(f"💥 Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_empresas_columns()
