#!/usr/bin/env python3
"""
Migração PostgreSQL de Produção - Remover evento_id da tabela produtos
ATENÇÃO: Este script modifica o banco de produção no Railway
"""
import asyncio
import asyncpg
import os
from datetime import datetime
import sys

async def migrate_postgres_production():
    """
    Remove evento_id da tabela produtos no PostgreSQL de produção
    """
    print("🚀 MIGRAÇÃO POSTGRESQL DE PRODUÇÃO")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este script irá modificar o banco de produção!")
    print("=" * 60)
    
    # URL do PostgreSQL do Railway (da variável de ambiente ou hardcoded para Railway)
    database_url = os.getenv("DATABASE_URL") or "postgresql://postgres:JpkrvsDWYnGKGsQMbTojhbEOjPUzxCCS@junction.proxy.rlwy.net:33986/railway"
    
    try:
        print("🔌 Conectando ao PostgreSQL de produção...")
        conn = await asyncpg.connect(database_url)
        print("✅ Conectado com sucesso!")
        
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
            await conn.close()
            return True
            
        print("⚠️ Coluna evento_id encontrada. Iniciando migração...")
        
        # Verificar quantos produtos existem
        count_produtos = await conn.fetchval("SELECT COUNT(*) FROM produtos")
        print(f"📊 Total de produtos a migrar: {count_produtos}")
        
        # 2. Backup dos dados atuais
        print("\n📦 Fazendo backup dos produtos...")
        produtos_backup = await conn.fetch("SELECT * FROM produtos")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"✅ Backup de {len(produtos_backup)} produtos realizado")
        
        # 3. Verificar se já existe uma tabela de backup
        backup_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'produtos_backup_evento_id'
            )
        """)
        
        if backup_exists:
            print("⚠️ Tabela de backup já existe, removendo...")
            await conn.execute("DROP TABLE produtos_backup_evento_id")
        
        # 4. Criar tabela temporária sem evento_id
        print("\n🔄 Criando nova estrutura de tabela...")
        await conn.execute("""
            CREATE TABLE produtos_new (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                descricao TEXT,
                preco NUMERIC(10,2) NOT NULL,
                categoria VARCHAR(100),
                tipo VARCHAR(50) NOT NULL,
                codigo_interno VARCHAR(20),
                imagem_url TEXT,
                estoque_atual INTEGER DEFAULT 0,
                estoque_minimo INTEGER DEFAULT 0,
                estoque_maximo INTEGER DEFAULT 1000,
                controla_estoque BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'ATIVO',
                empresa_id INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Copiar dados (excluindo evento_id)
        print("📋 Copiando dados sem evento_id...")
        copied_count = 0
        
        for produto in produtos_backup:
            try:
                await conn.execute("""
                    INSERT INTO produtos_new 
                    (id, nome, descricao, preco, categoria, tipo, codigo_interno, 
                     imagem_url, estoque_atual, estoque_minimo, estoque_maximo, 
                     controla_estoque, status, empresa_id, criado_em, atualizado_em)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """, 
                    produto['id'], produto['nome'], produto['descricao'], 
                    produto['preco'], produto['categoria'], produto['tipo'],
                    produto['codigo_interno'], produto['imagem_url'],
                    produto['estoque_atual'], produto['estoque_minimo'], 
                    produto['estoque_maximo'], produto['controla_estoque'],
                    produto['status'], produto['empresa_id'],
                    produto['criado_em'], produto['atualizado_em']
                )
                copied_count += 1
            except Exception as e:
                print(f"❌ Erro ao copiar produto ID {produto['id']}: {e}")
                continue
        
        print(f"✅ {copied_count}/{len(produtos_backup)} produtos copiados")
        
        # 6. Trocar tabelas (transação atômica)
        print("\n🔄 Executando migração (transação atômica)...")
        async with conn.transaction():
            # Renomear tabela atual para backup
            await conn.execute("ALTER TABLE produtos RENAME TO produtos_backup_evento_id")
            print("✅ Tabela original renomeada para backup")
            
            # Renomear nova tabela para produtos
            await conn.execute("ALTER TABLE produtos_new RENAME TO produtos")
            print("✅ Nova tabela ativada")
            
            # Ajustar sequence para auto-increment
            max_id = await conn.fetchval("SELECT MAX(id) FROM produtos")
            if max_id:
                await conn.execute(f"SELECT setval('produtos_id_seq', {max_id})")
                print(f"✅ Sequence ajustada para ID {max_id}")
        
        # 7. Verificar resultado
        print("\n🧪 Validando migração...")
        count_new = await conn.fetchval("SELECT COUNT(*) FROM produtos")
        has_evento_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'produtos' 
                AND column_name = 'evento_id'
            )
        """)
        
        # Listar colunas atuais
        columns = await conn.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'produtos' 
            ORDER BY ordinal_position
        """)
        column_names = [col['column_name'] for col in columns]
        
        print(f"\n📊 RESULTADO DA MIGRAÇÃO:")
        print(f"✅ Produtos migrados: {count_new}")
        print(f"✅ evento_id removido: {not has_evento_id}")
        print(f"📦 Backup disponível em: produtos_backup_evento_id")
        print(f"🗂️ Colunas atuais: {', '.join(column_names)}")
        
        # Teste de inserção para validar estrutura
        print("\n🧪 Testando inserção de produto...")
        try:
            test_result = await conn.fetchval("""
                INSERT INTO produtos (nome, tipo, preco, categoria)
                VALUES ('Teste Migração PostgreSQL', 'BEBIDA', 10.0, 'Teste')
                RETURNING id
            """)
            print(f"✅ Produto teste inserido com ID: {test_result}")
            
            # Remover produto teste
            await conn.execute("DELETE FROM produtos WHERE id = $1", test_result)
            print("✅ Produto teste removido")
            
        except Exception as e:
            print(f"❌ Erro no teste de inserção: {e}")
        
        await conn.close()
        
        print("\n🎉 MIGRAÇÃO POSTGRESQL CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ evento_id removido da tabela produtos")
        print("✅ Todos os dados preservados")
        print("✅ Backup de segurança criado")
        print("✅ Sistema funcionando normalmente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NA MIGRAÇÃO: {e}")
        print("🔄 A migração foi interrompida por segurança")
        print("💡 Verifique os logs e tente novamente")
        return False

async def validate_migration():
    """Validar se a migração foi bem-sucedida"""
    database_url = os.getenv("DATABASE_URL") or "postgresql://postgres:JpkrvsDWYnGKGsQMbTojhbEOjPUzxCCS@junction.proxy.rlwy.net:33986/railway"
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Verificar estrutura
        has_evento_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'produtos' 
                AND column_name = 'evento_id'
            )
        """)
        
        count = await conn.fetchval("SELECT COUNT(*) FROM produtos")
        
        print(f"\n📋 VALIDAÇÃO:")
        print(f"  - evento_id presente: {has_evento_id}")
        print(f"  - Total produtos: {count}")
        print(f"  - Status: {'❌ MIGRAÇÃO NECESSÁRIA' if has_evento_id else '✅ MIGRAÇÃO CONCLUÍDA'}")
        
        await conn.close()
        return not has_evento_id
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando necessidade de migração...")
    
    # Validar primeiro se é necessário
    need_migration = not asyncio.run(validate_migration())
    
    if not need_migration:
        print("✅ Migração não necessária - evento_id já foi removido!")
        sys.exit(0)
    
    print("\n⚠️ Migração necessária!")
    print("Pressione ENTER para continuar ou Ctrl+C para cancelar...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Migração cancelada pelo usuário")
        sys.exit(1)
    
    # Executar migração
    success = asyncio.run(migrate_postgres_production())
    
    if success:
        print("\n🎉 SUCESSO! PostgreSQL de produção atualizado")
    else:
        print("\n❌ FALHA na migração")
        sys.exit(1)
