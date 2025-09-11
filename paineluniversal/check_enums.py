#!/usr/bin/env python3
"""
Verificar enums no PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_enums():
    """Verificar todos os enums do PostgreSQL"""
    print("🔍 VERIFICANDO ENUMS DO POSTGRESQL")
    print("=" * 50)
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from backend.app.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Verificar enums disponíveis
        enums_query = db.execute(text("""
            SELECT t.typname, e.enumlabel
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            ORDER BY t.typname, e.enumsortorder;
        """)).fetchall()
        
        if enums_query:
            print("📋 ENUMS ENCONTRADOS:")
            current_enum = None
            for enum_type, enum_value in enums_query:
                if enum_type != current_enum:
                    print(f"\n🏷️ {enum_type}:")
                    current_enum = enum_type
                print(f"   • {enum_value}")
        else:
            print("⚠️ Nenhum enum encontrado")
        
        # Verificar estrutura da tabela produtos
        print(f"\n🏪 ESTRUTURA DA TABELA PRODUTOS:")
        produtos_schema = db.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'produtos'
            ORDER BY ordinal_position;
        """)).fetchall()
        
        for col_name, data_type, udt_name in produtos_schema:
            print(f"   {col_name}: {data_type} ({udt_name})")
        
        # Verificar valores atuais na tabela produtos
        print(f"\n📊 VALORES ATUAIS DOS PRODUTOS:")
        produtos_values = db.execute(text("""
            SELECT nome, tipo_usuario, status
            FROM produtos 
            LIMIT 10;
        """)).fetchall()
        
        for nome, tipo_usuario, status in produtos_values:
            print(f"   • {nome}: tipo={tipo_usuario}, status={status}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_enums()
