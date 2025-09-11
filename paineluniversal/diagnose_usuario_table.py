#!/usr/bin/env python3
"""
Diagnóstico da tabela usuarios no PostgreSQL de produção
Para resolver o erro: column usuarios.tipo_usuario does not exist
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import sys

def diagnose_usuarios_table():
    """
    Diagnostica a estrutura atual da tabela usuarios no PostgreSQL
    """
    print("🔍 DIAGNÓSTICO DA TABELA USUARIOS")
    print("=" * 50)
    
    # URLs possíveis do Railway (testando ambas)
    urls = [
        "postgresql://postgres:CeGUGoTyinOaBRILNgPCApbJpcfcVETf@hopper.proxy.rlwy.net:57200/railway",
        "postgresql://postgres:JpkrvsDWYnGKGsQMbTojhbEOjPUzxCCS@junction.proxy.rlwy.net:33986/railway"
    ]
    
    connection = None
    cursor = None
    
    for i, db_url in enumerate(urls, 1):
        try:
            print(f"🔌 Tentando conexão {i}/2...")
            connection = psycopg2.connect(db_url, connect_timeout=30)
            connection.autocommit = True
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            print(f"✅ Conectado com sucesso na URL {i}!")
            break
        except Exception as e:
            print(f"❌ Falha na URL {i}: {e}")
            if i == len(urls):
                print("💀 Todas as URLs falharam")
                return False
    
    try:
        # 1. Verificar se a tabela usuarios existe
        print("\n🏗️ Verificando existência da tabela usuarios...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        if not table_exists:
            print("❌ ERRO: Tabela 'usuarios' não existe!")
            return False
        
        print("✅ Tabela 'usuarios' existe")
        
        # 2. Verificar estrutura completa da tabela usuarios
        print("\n📋 Estrutura da tabela usuarios:")
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\nColunas encontradas:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  - {col['column_name']}: {col['data_type']}{max_len} {nullable} {default}")
        
        # 3. Verificar especificamente a coluna tipo_usuario
        print("\n🎯 Verificando coluna 'tipo_usuario'...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'usuarios' 
                AND column_name = 'tipo_usuario'
            )
        """)
        
        tipo_usuario_exists = cursor.fetchone()[0]
        
        if tipo_usuario_exists:
            print("✅ Coluna 'tipo_usuario' EXISTE")
            
            # Verificar tipo da coluna
            cursor.execute("""
                SELECT 
                    data_type, 
                    udt_name,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' 
                AND column_name = 'tipo_usuario'
            """)
            
            col_info = cursor.fetchone()
            print(f"  - Tipo: {col_info['data_type']}")
            print(f"  - UDT: {col_info['udt_name']}")
            print(f"  - Nullable: {col_info['is_nullable']}")
            print(f"  - Default: {col_info['column_default']}")
            print(f"  - Max Length: {col_info['character_maximum_length']}")
            
            # Se for enum, verificar valores possíveis
            if col_info['data_type'] == 'USER-DEFINED':
                print("\n🔍 Verificando valores do enum...")
                try:
                    cursor.execute("""
                        SELECT enumlabel 
                        FROM pg_enum 
                        WHERE enumtypid = (
                            SELECT oid 
                            FROM pg_type 
                            WHERE typname = %s
                        )
                        ORDER BY enumsortorder
                    """, (col_info['udt_name'],))
                    
                    enum_values = cursor.fetchall()
                    print(f"  - Valores do enum {col_info['udt_name']}:")
                    for val in enum_values:
                        print(f"    * {val['enumlabel']}")
                except Exception as e:
                    print(f"  - Erro ao verificar enum: {e}")
            
        else:
            print("❌ Coluna 'tipo_usuario' NÃO EXISTE")
            print("⚠️  ESTE É O PROBLEMA! A coluna precisa ser criada.")
        
        # 4. Verificar quantos usuários existem
        print("\n👥 Estatísticas da tabela usuarios:")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_users = cursor.fetchone()[0]
        print(f"  - Total de usuários: {total_users}")
        
        if total_users > 0:
            # Verificar alguns usuários de exemplo
            cursor.execute("SELECT id, cpf, nome, ativo FROM usuarios LIMIT 3")
            sample_users = cursor.fetchall()
            print("  - Usuários de exemplo:")
            for user in sample_users:
                cpf_masked = f"{user['cpf'][:3]}***{user['cpf'][-3:]}" if user['cpf'] else "N/A"
                print(f"    * ID {user['id']}: {user['nome']} (CPF: {cpf_masked}) - Ativo: {user['ativo']}")
        
        # 5. Verificar se existem enums relacionados
        print("\n🎭 Verificando enums relacionados a tipo de usuário...")
        cursor.execute("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e' 
            AND typname LIKE '%tipo%usuario%'
            OR typname LIKE '%user%type%'
            ORDER BY typname
        """)
        
        related_enums = cursor.fetchall()
        if related_enums:
            print("  - Enums relacionados encontrados:")
            for enum_type in related_enums:
                print(f"    * {enum_type['typname']}")
        else:
            print("  - Nenhum enum relacionado encontrado")
        
        # 6. Resumo do diagnóstico
        print("\n" + "="*50)
        print("📊 RESUMO DO DIAGNÓSTICO")
        print("="*50)
        
        if not tipo_usuario_exists:
            print("🚨 PROBLEMA IDENTIFICADO:")
            print("   - A coluna 'tipo_usuario' não existe na tabela 'usuarios'")
            print("   - O modelo Python espera esta coluna como String(20)")
            print("   - SQLAlchemy falha ao tentar fazer SELECT incluindo esta coluna")
            print("\n💡 SOLUÇÃO NECESSÁRIA:")
            print("   - Executar migração para ADICIONAR coluna 'tipo_usuario'")
            print("   - Definir valores padrão para usuários existentes")
            print("   - Configurar coluna como NOT NULL após popular dados")
        else:
            print("✅ Coluna 'tipo_usuario' existe")
            print("⚠️  Verificar se o tipo/formato está correto")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO no diagnóstico: {e}")
        return False
        
    finally:
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            print("\n🔌 Conexão fechada")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico da tabela usuarios...")
    success = diagnose_usuarios_table()
    
    if success:
        print("\n🎉 Diagnóstico concluído!")
    else:
        print("\n❌ Falha no diagnóstico")
        sys.exit(1)
