#!/usr/bin/env python3
"""
Migração PostgreSQL de Produção - Versão com Retry Automático
ATENÇÃO: Este script modifica o banco de produção no Railway
"""
import asyncio
import asyncpg
import os
from datetime import datetime
import sys
import time

async def test_connection_with_retry(database_url, max_retries=5):
    """Testa conexão com retry automático"""
    for attempt in range(max_retries):
        try:
            print(f"🔌 Tentativa {attempt + 1}/{max_retries} de conexão...")
            conn = await asyncpg.connect(database_url, timeout=30)
            print("✅ Conectado com sucesso!")
            return conn
        except Exception as e:
            print(f"❌ Falha na tentativa {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5  # 5s, 10s, 15s, 20s, 25s
                print(f"⏳ Aguardando {wait_time}s antes da próxima tentativa...")
                await asyncio.sleep(wait_time)
            else:
                print("🚨 Todas as tentativas de conexão falharam!")
                return None

async def migrate_postgres_production_with_retry():
    """
    Remove evento_id da tabela produtos no PostgreSQL de produção com retry
    """
    print("🚀 MIGRAÇÃO POSTGRESQL DE PRODUÇÃO - COM RETRY")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este script irá modificar o banco de produção!")
    print("=" * 60)
    
    # URL do PostgreSQL do Railway
    database_url = "postgresql://postgres:JpkrvsDWYnGKGsQMbTojhbEOjPUzxCCS@junction.proxy.rlwy.net:33986/railway"
    
    # Tentar conectar com retry
    conn = await test_connection_with_retry(database_url)
    if not conn:
        print("💀 Impossível conectar ao PostgreSQL após várias tentativas")
        return False
    
    try:
        # 1. Verificar se a coluna evento_id existe
        print("\n🔍 Verificando estrutura atual...")
        check_column = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'produtos' 
                AND column_name = 'evento_id'
            )
        """)
        
        if not check_column:
            print("✅ Coluna evento_id já foi removida do PostgreSQL!")
            return True
            
        print("⚠️ Coluna evento_id encontrada. Iniciando migração...")
        
        # Verificar quantos produtos existem
        count_produtos = await conn.fetchval("SELECT COUNT(*) FROM produtos")
        print(f"📊 Total de produtos a migrar: {count_produtos}")
        
        # 2. Backup dos dados atuais
        print("\n📦 Fazendo backup dos produtos...")
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar tabela de backup
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS produtos_backup_{backup_timestamp} AS 
            SELECT * FROM produtos
        """)
        
        backup_count = await conn.fetchval(f"SELECT COUNT(*) FROM produtos_backup_{backup_timestamp}")
        print(f"✅ Backup criado: produtos_backup_{backup_timestamp} ({backup_count} registros)")
        
        # 3. Iniciar transação atômica
        print("\n🔄 Iniciando migração atômica...")
        async with conn.transaction():
            # Criar nova tabela sem evento_id
            print("📋 Criando nova estrutura da tabela...")
            await conn.execute("""
                CREATE TABLE produtos_new (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    descricao TEXT,
                    tipo VARCHAR(50) NOT NULL,
                    preco DECIMAL(10,2) NOT NULL,
                    codigo_interno VARCHAR(100),
                    estoque_atual INTEGER DEFAULT 0,
                    estoque_minimo INTEGER DEFAULT 0,
                    estoque_maximo INTEGER DEFAULT 0,
                    controla_estoque BOOLEAN DEFAULT true,
                    status VARCHAR(20) DEFAULT 'ATIVO',
                    categoria VARCHAR(100),
                    imagem_url TEXT,
                    empresa_id INTEGER,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copiar dados (excluindo evento_id)
            print("📊 Copiando dados...")
            await conn.execute("""
                INSERT INTO produtos_new (
                    id, nome, descricao, tipo, preco, codigo_interno,
                    estoque_atual, estoque_minimo, estoque_maximo,
                    controla_estoque, status, categoria, imagem_url,
                    empresa_id, criado_em, atualizado_em
                )
                SELECT 
                    id, nome, descricao, tipo, preco, codigo_interno,
                    estoque_atual, estoque_minimo, estoque_maximo,
                    controla_estoque, status, categoria, imagem_url,
                    empresa_id, criado_em, atualizado_em
                FROM produtos
            """)
            
            # Verificar se todos os dados foram copiados
            new_count = await conn.fetchval("SELECT COUNT(*) FROM produtos_new")
            if new_count != count_produtos:
                raise Exception(f"Erro na cópia: {new_count} != {count_produtos}")
            
            print(f"✅ {new_count} produtos copiados com sucesso")
            
            # Renomear tabelas atomicamente
            print("🔄 Aplicando mudanças...")
            await conn.execute("ALTER TABLE produtos RENAME TO produtos_old")
            await conn.execute("ALTER TABLE produtos_new RENAME TO produtos")
            
            # Recriar índices e constraints
            print("📈 Recriando índices...")
            await conn.execute("CREATE INDEX idx_produtos_categoria ON produtos(categoria)")
            await conn.execute("CREATE INDEX idx_produtos_tipo ON produtos(tipo)")
            await conn.execute("CREATE INDEX idx_produtos_status ON produtos(status)")
            await conn.execute("CREATE INDEX idx_produtos_empresa_id ON produtos(empresa_id)")
            
            # Recriar sequence se necessário
            await conn.execute("SELECT setval('produtos_id_seq', COALESCE((SELECT MAX(id) FROM produtos), 1))")
            
        print("✅ Migração atômica concluída!")
        
        # 4. Validação final
        print("\n🧪 Validando migração...")
        
        # Verificar se evento_id foi removido
        final_check = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'produtos' 
                AND column_name = 'evento_id'
            )
        """)
        
        if final_check:
            raise Exception("ERRO: evento_id ainda existe após migração!")
        
        # Verificar contagem
        final_count = await conn.fetchval("SELECT COUNT(*) FROM produtos")
        if final_count != count_produtos:
            raise Exception(f"ERRO: Contagem incorreta após migração: {final_count} != {count_produtos}")
        
        # Verificar se tabela está funcionando
        sample = await conn.fetchrow("SELECT id, nome, tipo FROM produtos LIMIT 1")
        if sample:
            print(f"✅ Tabela funcionando: ID {sample['id']}, Nome: {sample['nome']}")
        
        print("\n🎉 MIGRAÇÃO POSTGRESQL CONCLUÍDA COM SUCESSO!")
        print(f"✅ Coluna evento_id removida da tabela produtos")
        print(f"📊 {final_count} produtos migrados")
        print(f"💾 Backup disponível: produtos_backup_{backup_timestamp}")
        
        # Limpar tabela antiga após sucesso
        print("\n🧹 Removendo tabela antiga...")
        await conn.execute("DROP TABLE produtos_old")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na migração: {e}")
        print("🔄 Tentando rollback...")
        try:
            # Tentar restaurar se algo deu errado
            await conn.execute("DROP TABLE IF EXISTS produtos_new")
            print("✅ Rollback concluído")
        except:
            print("⚠️ Problema no rollback - verifique manualmente")
        return False
        
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando migração PostgreSQL com retry automático...")
    success = asyncio.run(migrate_postgres_production_with_retry())
    
    if success:
        print("\n🎉 SUCESSO! PostgreSQL de produção atualizado")
    else:
        print("\n❌ FALHA na migração")
        sys.exit(1)
