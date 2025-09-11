
"""
Migração automática para corrigir enum tipousuario no PostgreSQL
Este script roda automaticamente no Railway durante o deploy
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def run_enum_migration():
    """Executa a migração do enum tipousuario"""
    try:
        # Usar a variável de ambiente do Railway
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
            
        # Converter para formato correto se necessário
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            
        print(f"🔗 Conectando ao banco...")
        engine = create_engine(database_url)
        
        with engine.begin() as conn:
            print("✅ Conectado ao PostgreSQL!")
            
            # Verificar e corrigir enum tipousuario
            migration_sql = """
            -- Criar enum se não existir
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipousuario') THEN
                    CREATE TYPE tipousuario AS ENUM ('admin', 'promoter', 'cliente');
                    RAISE NOTICE 'Enum tipousuario criado';
                END IF;
            END $$;
            
            -- Adicionar valores que podem estar faltando
            DO $$
            DECLARE
                enum_exists boolean;
            BEGIN
                -- Verificar se admin existe
                SELECT EXISTS(
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'admin' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ) INTO enum_exists;
                
                IF NOT enum_exists THEN
                    ALTER TYPE tipousuario ADD VALUE 'admin';
                    RAISE NOTICE 'Valor admin adicionado';
                END IF;
                
                -- Verificar se promoter existe
                SELECT EXISTS(
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'promoter' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ) INTO enum_exists;
                
                IF NOT enum_exists THEN
                    ALTER TYPE tipousuario ADD VALUE 'promoter';
                    RAISE NOTICE 'Valor promoter adicionado';
                END IF;
                
                -- Verificar se cliente existe
                SELECT EXISTS(
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'cliente' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ) INTO enum_exists;
                
                IF NOT enum_exists THEN
                    ALTER TYPE tipousuario ADD VALUE 'cliente';
                    RAISE NOTICE 'Valor cliente adicionado';
                END IF;
            END $$;
            """
            
            conn.execute(text(migration_sql))
            print("✅ Migração de enum executada com sucesso!")
            
            # Verificar valores finais
            result = conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ORDER BY enumsortorder;
            """))
            
            values = [row[0] for row in result.fetchall()]
            print(f"📋 Valores finais do enum: {values}")
            
            # Testar valores
            for value in ['admin', 'promoter', 'cliente']:
                try:
                    conn.execute(text(f"SELECT '{value}'::tipousuario"))
                    print(f"✅ Valor '{value}' aceito pelo enum")
                except Exception as e:
                    print(f"❌ Erro com valor '{value}': {e}")
                    return False
                    
            return True
            
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

if __name__ == "__main__":
    success = run_enum_migration()
    if success:
        print("🎉 Migração concluída com sucesso!")
        sys.exit(0)
    else:
        print("❌ Migração falhou")
        sys.exit(1)
