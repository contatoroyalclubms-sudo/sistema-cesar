"""
Script para criar tabela de categorias de produtos
Execute este script uma vez para criar a estrutura no banco PostgreSQL
"""

from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def criar_tabela_categorias_produtos():
    """SQL para criar tabela categorias_produtos"""
    
    sql_create_table = """
    CREATE TABLE IF NOT EXISTS categorias_produtos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        descricao TEXT,
        cor VARCHAR(7) DEFAULT '#3b82f6',
        ativo BOOLEAN DEFAULT true,
        evento_id INTEGER NOT NULL REFERENCES eventos(id),
        empresa_id INTEGER REFERENCES empresas(id),
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    sql_create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_categorias_produtos_id ON categorias_produtos(id);
    CREATE INDEX IF NOT EXISTS idx_categorias_produtos_nome ON categorias_produtos(nome);
    CREATE INDEX IF NOT EXISTS idx_categorias_produtos_evento_id ON categorias_produtos(evento_id);
    CREATE INDEX IF NOT EXISTS idx_categorias_produtos_ativo ON categorias_produtos(ativo);
    """
    
    sql_alter_produtos = """
    -- Adicionar coluna categoria_id na tabela produtos se não existir
    DO $$ 
    BEGIN 
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'produtos' AND column_name = 'categoria_id'
        ) THEN
            ALTER TABLE produtos ADD COLUMN categoria_id INTEGER REFERENCES categorias_produtos(id);
            CREATE INDEX IF NOT EXISTS idx_produtos_categoria_id ON produtos(categoria_id);
        END IF;
    END $$;
    """
    
    sql_insert_categorias_default = """
    -- Inserir categorias padrão se não existir nenhuma
    INSERT INTO categorias_produtos (nome, descricao, cor, evento_id, empresa_id)
    SELECT 
        'Bebidas', 
        'Bebidas alcoólicas e não alcoólicas', 
        '#10B981',
        e.id,
        e.empresa_id
    FROM eventos e 
    WHERE NOT EXISTS (
        SELECT 1 FROM categorias_produtos cp WHERE cp.evento_id = e.id
    )
    LIMIT 5;  -- Limitar para não criar muitas categorias
    
    INSERT INTO categorias_produtos (nome, descricao, cor, evento_id, empresa_id)
    SELECT 
        'Comidas', 
        'Pratos principais e petiscos', 
        '#F59E0B',
        e.id,
        e.empresa_id
    FROM eventos e 
    WHERE NOT EXISTS (
        SELECT 1 FROM categorias_produtos cp WHERE cp.evento_id = e.id AND cp.nome = 'Comidas'
    )
    LIMIT 5;
    
    INSERT INTO categorias_produtos (nome, descricao, cor, evento_id, empresa_id)
    SELECT 
        'Sobremesas', 
        'Doces e sobremesas', 
        '#EF4444',
        e.id,
        e.empresa_id
    FROM eventos e 
    WHERE NOT EXISTS (
        SELECT 1 FROM categorias_produtos cp WHERE cp.evento_id = e.id AND cp.nome = 'Sobremesas'
    )
    LIMIT 5;
    """
    
    return [
        sql_create_table,
        sql_create_indexes, 
        sql_alter_produtos,
        sql_insert_categorias_default
    ]

async def executar_migracoes_produtos(db):
    """Executar todas as migrações necessárias para produtos"""
    try:
        sqls = criar_tabela_categorias_produtos()
        
        for i, sql in enumerate(sqls):
            logger.info(f"Executando migração {i+1}/{len(sqls)}...")
            db.execute(text(sql))
            db.commit()
            logger.info(f"Migração {i+1} concluída com sucesso")
        
        logger.info("Todas as migrações de produtos foram executadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao executar migrações: {str(e)}")
        db.rollback()
        return False

# Função utilitária para executar via endpoint
def get_migration_sql():
    """Retorna SQL para execução manual"""
    sqls = criar_tabela_categorias_produtos()
    return "\n\n".join(sqls)
