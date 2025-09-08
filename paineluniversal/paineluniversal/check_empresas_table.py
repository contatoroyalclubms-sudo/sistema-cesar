#!/usr/bin/env python3

import psycopg2

def check_empresas_table():
    """Verifica a estrutura real da tabela empresas"""
    
    try:
        conn = psycopg2.connect('postgresql://postgres:JQmcvz2Y*m4jY6Lg@localhost:5432/eventos_db')
        cur = conn.cursor()
        
        print("🔍 Verificando estrutura da tabela 'empresas':")
        print("=" * 50)
        
        # Listar colunas
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name='empresas' 
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        
        if columns:
            print("📋 Colunas encontradas:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
        else:
            print("❌ Tabela 'empresas' não encontrada ou sem colunas")
            
        # Verificar se há dados
        cur.execute("SELECT COUNT(*) FROM empresas;")
        count = cur.fetchone()[0]
        print(f"\n📊 Total de registros: {count}")
        
        if count > 0:
            cur.execute("SELECT * FROM empresas LIMIT 1;")
            sample = cur.fetchone()
            if sample:
                print("\n📝 Exemplo de registro:")
                print(f"  ID: {sample[0]}")
                if len(sample) > 1:
                    print(f"  Nome: {sample[1]}")
                if len(sample) > 2:
                    print(f"  CNPJ: {sample[2]}")
                
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"💥 Erro ao verificar tabela: {e}")

if __name__ == "__main__":
    check_empresas_table()
