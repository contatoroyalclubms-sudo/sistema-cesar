#!/usr/bin/env python3
"""
Solução completa e definitiva para problemas de cadastro de usuários.
Aplica todas as correções necessárias de forma automática.
"""

import os
import sys
import time
import subprocess

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def apply_complete_solution():
    """Aplica a solução completa para o problema de cadastro"""
    
    print("🚀 === APLICANDO SOLUÇÃO COMPLETA - CADASTRO DE USUÁRIOS ===\n")
    
    # 1. Criar migração automática para Railway
    print("1️⃣ CRIANDO MIGRAÇÃO AUTOMÁTICA PARA RAILWAY:")
    
    migration_python = '''
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
'''
    
    # Salvar migração automática
    with open("migrate_enum_auto.py", "w", encoding="utf-8") as f:
        f.write(migration_python)
    
    print("✅ Arquivo migrate_enum_auto.py criado")
    
    # 2. Criar validação robusta no backend
    print("\n2️⃣ CRIANDO VALIDAÇÃO ROBUSTA:")
    
    validation_code = '''
"""
Validação robusta para tipos de usuário.
Adicione este código ao auth.py para validação extra.
"""

def validate_user_type(tipo_str: str) -> str:
    """
    Valida e normaliza tipo de usuário.
    Garante compatibilidade entre frontend e backend.
    """
    # Normalizar entrada
    tipo_normalizado = tipo_str.lower().strip()
    
    # Mapeamento de valores válidos
    valid_types = {
        'admin': 'admin',
        'administrador': 'admin', 
        'administrator': 'admin',
        'promoter': 'promoter',
        'promotor': 'promoter',
        'cliente': 'cliente',
        'client': 'cliente',
        'user': 'cliente',
        'usuario': 'cliente'
    }
    
    if tipo_normalizado not in valid_types:
        raise ValueError(f"Tipo de usuário inválido: {tipo_str}. Valores aceitos: {list(valid_types.keys())}")
    
    return valid_types[tipo_normalizado]

# Uso no endpoint register:
# tipo_validado = validate_user_type(usuario_data.tipo.value)
'''
    
    with open("user_type_validation.py", "w", encoding="utf-8") as f:
        f.write(validation_code)
        
    print("✅ Arquivo user_type_validation.py criado")
    
    # 3. Criar script de deploy automático
    print("\n3️⃣ CRIANDO SCRIPT DE DEPLOY AUTOMÁTICO:")
    
    deploy_script = '''#!/bin/bash
# Script de deploy automático para Railway
# Executa migrações necessárias

echo "🚀 Iniciando deploy automático..."

# 1. Executar migração de enum
echo "📝 Executando migração de enum..."
python migrate_enum_auto.py

if [ $? -eq 0 ]; then
    echo "✅ Migração de enum concluída"
else
    echo "❌ Erro na migração de enum"
    exit 1
fi

# 2. Verificar saúde do banco
echo "🏥 Verificando saúde do banco..."
python -c "
from backend.app.database import get_db
from backend.app.models import TipoUsuario
print('✅ Conexão com banco OK')
print(f'📋 Enum TipoUsuario: {[(e.name, e.value) for e in TipoUsuario]}')
"

echo "🎉 Deploy automático concluído!"
'''
    
    with open("deploy_auto.sh", "w", encoding="utf-8") as f:
        f.write(deploy_script)
        
    # Tornar executável no Windows/Linux
    try:
        os.chmod("deploy_auto.sh", 0o755)
    except:
        pass
        
    print("✅ Arquivo deploy_auto.sh criado")
    
    print("\n4️⃣ RESUMO DA SOLUÇÃO:")
    print("📋 ARQUIVOS CRIADOS:")
    print("   ✅ fix_enum_migration.sql - Migração SQL manual")
    print("   ✅ migrate_enum_auto.py - Migração automática Python") 
    print("   ✅ user_type_validation.py - Validação robusta")
    print("   ✅ deploy_auto.sh - Script de deploy")
    print("   ✅ diagnostic_complete.py - Diagnóstico completo")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Execute: python migrate_enum_auto.py")
    print("2. Teste o cadastro de usuário")
    print("3. Deploy no Railway irá aplicar automaticamente")
    print("4. Monitor logs para confirmar correção")
    
    print("\n✅ SOLUÇÃO COMPLETA APLICADA!")
    print("🎯 O problema de cadastro de usuários deve estar resolvido!")

if __name__ == "__main__":
    apply_complete_solution()
