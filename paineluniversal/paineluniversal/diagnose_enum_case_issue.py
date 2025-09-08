#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problema de case mismatch no enum tipousuario
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def diagnose_enum_issue():
    """Diagnostica o problema do enum tipousuario"""
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
            
            # 1. Verificar valores atuais do enum
            print("\n🔍 DIAGNÓSTICO DO ENUM TIPOUSUARIO:")
            print("=" * 50)
            
            result = conn.execute(text("""
                SELECT enumlabel, enumsortorder
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ORDER BY enumsortorder
            """))
            
            enum_values = result.fetchall()
            print(f"📋 Valores atuais no banco:")
            for i, (value, order) in enumerate(enum_values, 1):
                print(f"   {i}. '{value}' (ordem: {order})")
            
            # 2. Verificar definição do enum no código Python
            print(f"\n🐍 Valores esperados no código Python:")
            print(f"   1. 'admin' (TipoUsuario.ADMIN)")
            print(f"   2. 'promoter' (TipoUsuario.PROMOTER)")
            print(f"   3. 'cliente' (TipoUsuario.CLIENTE)")
            
            # 3. Identificar discrepância
            expected_values = ['admin', 'promoter', 'cliente']
            actual_values = [value for value, _ in enum_values]
            
            print(f"\n🔍 ANÁLISE DE DISCREPÂNCIA:")
            print("=" * 50)
            
            case_mismatch = False
            missing_values = []
            extra_values = []
            
            for expected in expected_values:
                if expected not in actual_values:
                    # Verificar se existe em maiúsculo
                    if expected.upper() in actual_values:
                        case_mismatch = True
                        print(f"⚠️ Case mismatch: esperado '{expected}', encontrado '{expected.upper()}'")
                    else:
                        missing_values.append(expected)
                        print(f"❌ Valor faltando: '{expected}'")
            
            for actual in actual_values:
                if actual.lower() not in expected_values:
                    extra_values.append(actual)
                    print(f"➕ Valor extra: '{actual}'")
            
            # 4. Testar valores atuais
            print(f"\n🧪 TESTE DOS VALORES ATUAIS:")
            print("=" * 50)
            
            test_values = ['admin', 'ADMIN', 'promoter', 'PROMOTER', 'cliente', 'CLIENTE']
            
            for value in test_values:
                try:
                    conn.execute(text(f"SELECT '{value}'::tipousuario"))
                    print(f"✅ '{value}' - ACEITO")
                except Exception as e:
                    print(f"❌ '{value}' - REJEITADO: {str(e)}")
            
            # 5. Verificar usuários existentes
            print(f"\n👥 USUÁRIOS EXISTENTES:")
            print("=" * 50)
            
            try:
                result = conn.execute(text("SELECT tipo, COUNT(*) FROM usuarios GROUP BY tipo"))
                user_types = result.fetchall()
                
                if user_types:
                    for tipo, count in user_types:
                        print(f"   {tipo}: {count} usuário(s)")
                else:
                    print("   Nenhum usuário encontrado")
                    
            except Exception as e:
                print(f"   Erro ao consultar usuários: {e}")
            
            # 6. Propor solução
            print(f"\n💡 PROPOSTA DE SOLUÇÃO:")
            print("=" * 50)
            
            if case_mismatch:
                print("🎯 PROBLEMA IDENTIFICADO: Case mismatch")
                print("   - Banco tem valores em UPPERCASE")
                print("   - Código Python espera lowercase")
                print("   - Solução: Adicionar valores em lowercase")
                print("")
                print("🔧 AÇÕES RECOMENDADAS:")
                print("   1. Adicionar valores lowercase ao enum")
                print("   2. Manter valores UPPERCASE para compatibilidade")
                print("   3. Atualizar registros existentes para lowercase")
                
                # Mostrar SQL de correção
                print(f"\n📝 SQL DE CORREÇÃO:")
                print("=" * 30)
                correction_sql = """
                -- Adicionar valores em lowercase
                ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'admin';
                ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'promoter';
                ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'cliente';
                
                -- Atualizar usuários existentes (se necessário)
                UPDATE usuarios SET tipo = 'admin' WHERE tipo = 'ADMIN';
                UPDATE usuarios SET tipo = 'promoter' WHERE tipo = 'PROMOTER';
                UPDATE usuarios SET tipo = 'cliente' WHERE tipo = 'CLIENTE';
                """
                print(correction_sql)
                
            elif missing_values:
                print("🎯 PROBLEMA IDENTIFICADO: Valores faltando")
                print(f"   - Valores faltando: {missing_values}")
                
            else:
                print("✅ Enum parece estar correto")
                print("   - Problema pode ser em outro lugar")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        return False

def fix_enum_case_mismatch():
    """Corrige o problema de case mismatch do enum"""
    try:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
            
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            
        print(f"🔧 Iniciando correção do enum...")
        engine = create_engine(database_url)
        
        with engine.begin() as conn:
            print("✅ Conectado para correção!")
            
            # Adicionar valores em lowercase
            correction_sql = """
            -- Adicionar valores em lowercase se não existirem
            DO $$
            BEGIN
                -- admin
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'admin' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ) THEN
                    ALTER TYPE tipousuario ADD VALUE 'admin';
                    RAISE NOTICE 'Valor admin adicionado';
                END IF;
                
                -- promoter
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'promoter' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ) THEN
                    ALTER TYPE tipousuario ADD VALUE 'promoter';
                    RAISE NOTICE 'Valor promoter adicionado';
                END IF;
                
                -- cliente
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'cliente' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ) THEN
                    ALTER TYPE tipousuario ADD VALUE 'cliente';
                    RAISE NOTICE 'Valor cliente adicionado';
                END IF;
            END $$;
            """
            
            conn.execute(text(correction_sql))
            print("✅ Valores lowercase adicionados")
            
            # Atualizar usuários existentes se necessário
            update_sql = """
            -- Atualizar usuários para usar valores lowercase
            UPDATE usuarios SET tipo = 'admin' WHERE tipo = 'ADMIN';
            UPDATE usuarios SET tipo = 'promoter' WHERE tipo = 'PROMOTER';  
            UPDATE usuarios SET tipo = 'cliente' WHERE tipo = 'CLIENTE';
            """
            
            result = conn.execute(text(update_sql))
            print("✅ Usuários atualizados para lowercase")
            
            # Verificar resultado
            result = conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
                ORDER BY enumsortorder
            """))
            
            final_values = [row[0] for row in result.fetchall()]
            print(f"✅ Valores finais do enum: {final_values}")
            
            # Testar valores
            test_values = ['admin', 'promoter', 'cliente']
            for value in test_values:
                try:
                    conn.execute(text(f"SELECT '{value}'::tipousuario"))
                    print(f"✅ Teste '{value}': OK")
                except Exception as e:
                    print(f"❌ Teste '{value}': FALHOU - {e}")
                    return False
            
            print("🎉 Correção concluída com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO E CORREÇÃO DO ENUM TIPOUSUARIO")
    print("=" * 60)
    
    # Primeiro diagnosticar
    print("\n🔍 FASE 1: DIAGNÓSTICO")
    print("-" * 30)
    success = diagnose_enum_issue()
    
    if success:
        print("\n🔧 FASE 2: CORREÇÃO")
        print("-" * 30)
        fix_success = fix_enum_case_mismatch()
        
        if fix_success:
            print("\n✅ DIAGNÓSTICO E CORREÇÃO CONCLUÍDOS!")
            print("🎯 O registro de usuários admin deve funcionar agora.")
        else:
            print("\n❌ CORREÇÃO FALHOU!")
    else:
        print("\n❌ DIAGNÓSTICO FALHOU!")
