"""
Script simples para verificar e corrigir o enum tipousuario no PostgreSQL
Usando psycopg2 que já está instalado no projeto
"""

import os
import sys
import traceback

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.app.database import get_db
    from backend.app.models import TipoUsuario
    from sqlalchemy import text
    import psycopg2
    
    print("🔍 Verificando enum tipousuario no PostgreSQL...")
    
    # Conectar diretamente com psycopg2
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:CeGUGoTyinOaBRILNgPCApbJpcfcVETf@hopper.proxy.rlwy.net:57200/railway")
    
    # Remover qualquer prefixo sqlalchemy
    if database_url.startswith("postgresql+"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://")
    
    print(f"📡 Conectando ao banco...")
    
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    
    print("✅ Conectado ao PostgreSQL!")
    
    # 1. Verificar se o enum tipousuario existe
    cur.execute("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (
            SELECT oid 
            FROM pg_type 
            WHERE typname = 'tipousuario'
        )
        ORDER BY enumsortorder;
    """)
    
    enum_values = [row[0] for row in cur.fetchall()]
    print(f"📋 Valores atuais do enum tipousuario: {enum_values}")
    
    # 2. Verificar valores esperados (do Python)
    expected_values = ['admin', 'promoter', 'cliente']
    print(f"🎯 Valores esperados (Python TipoUsuario): {expected_values}")
    print(f"🐍 Enum Python atual: {[(e.name, e.value) for e in TipoUsuario]}")
    
    # 3. Identificar diferenças
    missing_values = set(expected_values) - set(enum_values)
    extra_values = set(enum_values) - set(expected_values)
    
    if missing_values:
        print(f"❌ Valores faltando no enum PostgreSQL: {missing_values}")
        
        # Adicionar valores faltando
        for value in missing_values:
            print(f"➕ Adicionando valor: {value}")
            cur.execute(f"ALTER TYPE tipousuario ADD VALUE '{value}'")
            print(f"✅ Valor '{value}' adicionado")
            
        conn.commit()
        print("💾 Alterações commitadas!")
            
    if extra_values:
        print(f"⚠️ Valores extras no enum PostgreSQL: {extra_values}")
        print("ℹ️ Valores extras não serão removidos para manter compatibilidade")
        
    if not missing_values and not extra_values:
        print("✅ Enum tipousuario está correto!")
        
    # 4. Testar se os valores funcionam
    print("\n🧪 Testando valores do enum...")
    for value in expected_values:
        try:
            cur.execute(f"SELECT %s::tipousuario", (value,))
            result = cur.fetchone()[0]
            print(f"✅ Valor '{value}' aceito → '{result}'")
        except Exception as e:
            print(f"❌ Erro com valor '{value}': {e}")
            
    # 5. Verificar valores finais
    cur.execute("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (
            SELECT oid 
            FROM pg_type 
            WHERE typname = 'tipousuario'
        )
        ORDER BY enumsortorder;
    """)
    
    final_values = [row[0] for row in cur.fetchall()]
    print(f"\n📋 Valores finais do enum tipousuario: {final_values}")
    
    print("\n🎉 Verificação e correção concluídas!")
    print("🚀 Agora o registro de usuários deve funcionar!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print(f"🔍 Tipo do erro: {type(e)}")
    print("\n📋 Traceback completo:")
    traceback.print_exc()
    
    # Se enum não existe, criar
    if "does not exist" in str(e) or "relation" in str(e):
        print("\n📝 Tentando criar enum tipousuario...")
        try:
            cur.execute("CREATE TYPE tipousuario AS ENUM ('admin', 'promoter', 'cliente')")
            conn.commit()
            print("✅ Enum tipousuario criado com sucesso!")
        except Exception as create_error:
            print(f"❌ Erro ao criar enum: {create_error}")
    
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
