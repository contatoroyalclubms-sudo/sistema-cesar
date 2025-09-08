"""
Script para verificar e corrigir o enum tipousuario no PostgreSQL
Este script vai verificar os valores atuais do enum e corrigi-los se necessário
"""

import os
import sys
import asyncpg
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_and_fix_enum():
    try:
        # Conectar com Railway PostgreSQL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            database_url = "postgresql+asyncpg://postgres:fVjXLCuAPuwsBwvgJMOqYgKMRTkQNBdV@centerbeam.proxy.rlwy.net:31175/railway"
        
        # Converter para asyncpg format
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        print("🔍 Conectando ao PostgreSQL...")
        engine = create_async_engine(asyncpg_url)
        
        async with engine.begin() as conn:
            print("✅ Conectado ao banco!")
            
            # 1. Verificar se o enum tipousuario existe
            result = await conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'tipousuario'
                )
                ORDER BY enumsortorder;
            """))
            
            enum_values = [row[0] for row in result.fetchall()]
            print(f"📋 Valores atuais do enum tipousuario: {enum_values}")
            
            # 2. Verificar valores esperados
            expected_values = ['admin', 'promoter', 'cliente']
            print(f"🎯 Valores esperados: {expected_values}")
            
            # 3. Identificar diferenças
            missing_values = set(expected_values) - set(enum_values)
            extra_values = set(enum_values) - set(expected_values)
            
            if missing_values:
                print(f"❌ Valores faltando no enum: {missing_values}")
                
                # Adicionar valores faltando
                for value in missing_values:
                    print(f"➕ Adicionando valor: {value}")
                    await conn.execute(text(f"ALTER TYPE tipousuario ADD VALUE '{value}'"))
                    print(f"✅ Valor '{value}' adicionado")
                    
            if extra_values:
                print(f"⚠️ Valores extras no enum (não serão removidos): {extra_values}")
                
            if not missing_values and not extra_values:
                print("✅ Enum tipousuario está correto!")
                
            # 4. Verificar se conseguimos inserir um usuário de teste
            print("\n🧪 Testando inserção de valores...")
            for value in expected_values:
                try:
                    # Apenas verificar se o valor é aceito
                    await conn.execute(text(f"SELECT '{value}'::tipousuario"))
                    print(f"✅ Valor '{value}' aceito pelo enum")
                except Exception as e:
                    print(f"❌ Erro com valor '{value}': {e}")
                    
            print("\n🎉 Verificação concluída!")
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        print(f"Tipo do erro: {type(e)}")
        
        # Se enum não existe, criar
        if "does not exist" in str(e) or "relation" in str(e):
            print("📝 Enum tipousuario não existe, criando...")
            try:
                async with engine.begin() as conn:
                    await conn.execute(text("CREATE TYPE tipousuario AS ENUM ('admin', 'promoter', 'cliente')"))
                    print("✅ Enum tipousuario criado com sucesso!")
            except Exception as create_error:
                print(f"❌ Erro ao criar enum: {create_error}")
                
    finally:
        if 'engine' in locals():
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_and_fix_enum())
