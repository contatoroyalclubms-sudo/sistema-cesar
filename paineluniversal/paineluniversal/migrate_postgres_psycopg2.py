#!/usr/bin/env python3
"""
Migração PostgreSQL usando psycopg2 ao invés de asyncpg
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import sys

def migrate_postgres_with_psycopg2():
    """
    Remove evento_id da tabela produtos usando psycopg2
    """
    print("🚀 MIGRAÇÃO POSTGRESQL COM PSYCOPG2")
    print("=" * 50)
    
    # URL do PostgreSQL do Railway
    db_config = {
        'host': 'junction.proxy.rlwy.net',
        'port': 33986,
        'database': 'railway',
        'user': 'postgres',
        'password': 'JpkrvsDWYnGKGsQMbTojhbEOjPUzxCCS',
        'connect_timeout': 30
    }
    
    try:
        print("🔌 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conectado com sucesso!")
        
        # 1. Verificar se a coluna evento_id existe
        print("\n🔍 Verificando estrutura atual...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'produtos' 
                AND column_name = 'evento_id'
            )
        """)
        
        column_exists = cursor.fetchone()[0]
        
        if not column_exists:
            print("✅ Coluna evento_id já foi removida do PostgreSQL!")
            return True
            
        print("⚠️ Coluna evento_id encontrada. Iniciando migração...")
        
        # Verificar quantos produtos existem
        cursor.execute("SELECT COUNT(*) FROM produtos")
        count_produtos = cursor.fetchone()[0]
        print(f"📊 Total de produtos a migrar: {count_produtos}")
        
        # 2. Fazer backup
        print("\n📦 Fazendo backup dos produtos...")
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_table = f"produtos_backup_{backup_timestamp}"
        
        cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM produtos")
        print(f"✅ Backup criado: {backup_table}")
        
        # 3. Iniciar transação
        print("\n🔄 Iniciando migração...")
        
        # Remover a coluna evento_id
        cursor.execute("ALTER TABLE produtos DROP COLUMN IF EXISTS evento_id")
        print("✅ Coluna evento_id removida")
        
        # Recriar índices
        print("📈 Recriando índices...")
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)",
            "CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo)",
            "CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status)",
            "CREATE INDEX IF NOT EXISTS idx_produtos_empresa_id ON produtos(empresa_id)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        # 4. Validação
        print("\n🧪 Validando migração...")
        
        # Verificar se evento_id foi removido
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'produtos' 
                AND column_name = 'evento_id'
            )
        """)
        
        still_exists = cursor.fetchone()[0]
        if still_exists:
            raise Exception("ERRO: evento_id ainda existe após migração!")
        
        # Verificar contagem
        cursor.execute("SELECT COUNT(*) FROM produtos")
        final_count = cursor.fetchone()[0]
        if final_count != count_produtos:
            raise Exception(f"ERRO: Contagem incorreta: {final_count} != {count_produtos}")
        
        # Verificar se tabela está funcionando
        cursor.execute("SELECT id, nome, tipo FROM produtos LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"✅ Tabela funcionando: ID {sample['id']}, Nome: {sample['nome']}")
        
        # Commit das mudanças
        conn.commit()
        
        print("\n🎉 MIGRAÇÃO POSTGRESQL CONCLUÍDA COM SUCESSO!")
        print(f"✅ Coluna evento_id removida da tabela produtos")
        print(f"📊 {final_count} produtos preservados")
        print(f"💾 Backup disponível: {backup_table}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na migração: {e}")
        try:
            conn.rollback()
            print("🔄 Rollback executado")
        except:
            print("⚠️ Problema no rollback")
        return False
        
    finally:
        try:
            cursor.close()
            conn.close()
            print("🔌 Conexão fechada")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Iniciando migração PostgreSQL com psycopg2...")
    success = migrate_postgres_with_psycopg2()
    
    if success:
        print("\n🎉 SUCESSO! PostgreSQL de produção atualizado")
    else:
        print("\n❌ FALHA na migração")
        sys.exit(1)
