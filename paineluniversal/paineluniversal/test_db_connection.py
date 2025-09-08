import psycopg2
import sys

DATABASE_URL = "postgresql://postgres:CeGUGoTyinOaBRILNgPCApbJpcfcVETf@hopper.proxy.rlwy.net:57200/railway"

print("🔍 Testando conexão com PostgreSQL...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Conexão estabelecida!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"📊 Versão do PostgreSQL: {version[0]}")
    
    # Verificar se a tabela eventos existe
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'eventos'
        );
    """)
    
    eventos_exists = cur.fetchone()[0]
    print(f"🎫 Tabela eventos existe: {eventos_exists}")
    
    if eventos_exists:
        # Verificar estrutura da coluna empresa_id
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'eventos' AND column_name = 'empresa_id'
        """)
        
        result = cur.fetchone()
        if result:
            col_name, data_type, is_nullable = result
            print(f"📋 {col_name}: {data_type} - {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
        else:
            print("⚠️ Coluna empresa_id não encontrada")
    
    conn.close()
    print("✅ Teste de conexão concluído!")
    
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    sys.exit(1)
