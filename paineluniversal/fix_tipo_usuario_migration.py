#!/usr/bin/env python3
"""
Migração crítica para corrigir erro de login: adicionar coluna tipo_usuario
ERRO: column usuarios.tipo_usuario does not exist
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import sys

def fix_tipo_usuario_column():
    """
    Corrige o problema da coluna tipo_usuario na tabela usuarios
    """
    print("🚨 MIGRAÇÃO CRÍTICA: CORRIGIR COLUNA TIPO_USUARIO")
    print("=" * 60)
    
    # Tentar múltiplas formas de obter a URL do banco
    db_urls = []
    
    # 1. Variável de ambiente (Railway padrão)
    if os.getenv('DATABASE_URL'):
        db_urls.append(os.getenv('DATABASE_URL'))
        print(f"✅ DATABASE_URL encontrada")
    
    # 2. URLs conhecidas do Railway (fallback)
    fallback_urls = [
        "postgresql://postgres:CeGUGoTyinOaBRILNgPCApbJpcfcVETf@hopper.proxy.rlwy.net:57200/railway",
        "postgresql://postgres:JpkrvsDWYnGKGsQMbTojhbEOjPUzxCCS@junction.proxy.rlwy.net:33986/railway",
        "postgresql://postgres:pMdaVzNweSSlSxmNEqGEIWQPyWZdHgPz@autorack.proxy.rlwy.net:44103/railway"
    ]
    
    db_urls.extend(fallback_urls)
    
    if not db_urls:
        print("❌ Nenhuma URL de banco configurada")
        return False
    
    connection = None
    cursor = None
    
    # Tentar conexão com cada URL
    for i, db_url in enumerate(db_urls, 1):
        try:
            print(f"🔌 Tentativa {i}/{len(db_urls)}...")
            connection = psycopg2.connect(db_url, connect_timeout=15)
            connection.autocommit = False  # Usar transações
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            print(f"✅ Conectado com sucesso!")
            break
        except Exception as e:
            print(f"❌ Falha: {str(e)[:100]}...")
            if i == len(db_urls):
                print("💀 Todas as conexões falharam")
                return False
    
    try:
        # 1. Verificar se a tabela usuarios existe
        print("\n🏗️ Verificando tabela usuarios...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios'
            )
        """)
        
        if not cursor.fetchone()[0]:
            print("❌ ERRO: Tabela 'usuarios' não existe!")
            return False
        
        print("✅ Tabela 'usuarios' encontrada")
        
        # 2. Verificar se a coluna tipo_usuario existe
        print("\n🎯 Verificando coluna tipo_usuario...")
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                udt_name,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            AND column_name = 'tipo_usuario'
        """)
        
        col_info = cursor.fetchone()
        
        if col_info:
            print(f"✅ Coluna existe: {col_info['data_type']} ({col_info['udt_name']})")
            
            # Se for enum, converter para VARCHAR
            if col_info['data_type'] == 'USER-DEFINED':
                print("🔄 Convertendo enum para VARCHAR...")
                
                # Criar coluna temporária
                cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo_usuario_temp VARCHAR(20)")
                
                # Mapear valores do enum para strings
                cursor.execute("""
                    UPDATE usuarios 
                    SET tipo_usuario_temp = CASE 
                        WHEN tipo_usuario::text = 'ADMIN' THEN 'admin'
                        WHEN tipo_usuario::text = 'PROMOTER' THEN 'promoter'
                        WHEN tipo_usuario::text = 'CLIENTE' THEN 'cliente'
                        ELSE 'cliente'
                    END
                """)
                
                # Remover coluna antiga
                cursor.execute("ALTER TABLE usuarios DROP COLUMN tipo_usuario")
                
                # Renomear coluna temporária
                cursor.execute("ALTER TABLE usuarios RENAME COLUMN tipo_usuario_temp TO tipo_usuario")
                
                print("✅ Enum convertido para VARCHAR")
            
            elif col_info['data_type'] != 'character varying':
                print(f"🔄 Convertendo {col_info['data_type']} para VARCHAR...")
                cursor.execute("ALTER TABLE usuarios ALTER COLUMN tipo_usuario TYPE VARCHAR(20)")
                print("✅ Tipo convertido")
            else:
                print("✅ Coluna já é VARCHAR")
                
        else:
            print("❌ Coluna tipo_usuario NÃO EXISTE - criando...")
            
            # Verificar quantos usuários existem
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            user_count = cursor.fetchone()[0]
            print(f"📊 {user_count} usuários encontrados")
            
            # Adicionar coluna com valor padrão
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN tipo_usuario VARCHAR(20) DEFAULT 'cliente'
            """)
            
            # Atualizar todos os usuários existentes
            cursor.execute("UPDATE usuarios SET tipo_usuario = 'cliente' WHERE tipo_usuario IS NULL")
            
            print("✅ Coluna tipo_usuario criada")
        
        # 3. Garantir que a coluna é NOT NULL
        print("\n🔒 Configurando restrições...")
        
        # Verificar se há valores NULL
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"⚠️ {null_count} usuários com tipo_usuario NULL - corrigindo...")
            cursor.execute("UPDATE usuarios SET tipo_usuario = 'cliente' WHERE tipo_usuario IS NULL")
        
        # Tornar NOT NULL
        cursor.execute("ALTER TABLE usuarios ALTER COLUMN tipo_usuario SET NOT NULL")
        print("✅ Coluna configurada como NOT NULL")
        
        # 4. Verificar valores únicos
        print("\n📊 Verificando valores...")
        cursor.execute("""
            SELECT tipo_usuario, COUNT(*) as count 
            FROM usuarios 
            GROUP BY tipo_usuario 
            ORDER BY count DESC
        """)
        
        stats = cursor.fetchall()
        print("Distribuição de tipos de usuário:")
        for stat in stats:
            print(f"  - {stat['tipo_usuario']}: {stat['count']} usuários")
        
        # 5. Teste final - simular query que estava falhando
        print("\n🧪 Testando query que estava falhando...")
        cursor.execute("""
            SELECT 
                usuarios.id, 
                usuarios.cpf, 
                usuarios.nome,
                usuarios.tipo_usuario
            FROM usuarios 
            WHERE usuarios.cpf LIKE '066%' 
            LIMIT 1
        """)
        
        test_result = cursor.fetchone()
        if test_result:
            cpf_masked = f"{test_result['cpf'][:3]}***{test_result['cpf'][-3:]}"
            print(f"✅ Query funciona: ID {test_result['id']}, CPF {cpf_masked}, Tipo: {test_result['tipo_usuario']}")
        else:
            print("⚠️ Nenhum usuário com CPF 066* encontrado")
        
        # Commit das mudanças
        connection.commit()
        print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Coluna tipo_usuario está funcionando")
        print("✅ Sistema de login deve funcionar agora")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na migração: {e}")
        try:
            connection.rollback()
            print("🔄 Rollback executado")
        except:
            print("⚠️ Problema no rollback")
        return False
        
    finally:
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            print("🔌 Conexão fechada")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Iniciando correção crítica da coluna tipo_usuario...")
    success = fix_tipo_usuario_column()
    
    if success:
        print("\n🎉 SUCESSO! Erro de login deve estar resolvido")
        print("📝 Próximo passo: testar login em produção")
    else:
        print("\n❌ FALHA na migração")
        print("📝 Verificar logs e tentar novamente")
        sys.exit(1)
