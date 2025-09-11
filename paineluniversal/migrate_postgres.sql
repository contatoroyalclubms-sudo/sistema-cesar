-- Script SQL para executar diretamente no PostgreSQL via psql
-- ATENÇÃO: Este script remove a coluna evento_id da tabela produtos

-- 1. Verificar se a coluna existe
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'produtos' 
        AND column_name = 'evento_id'
    ) THEN
        RAISE NOTICE 'Coluna evento_id encontrada. Iniciando migração...';
        
        -- 2. Criar backup
        EXECUTE 'CREATE TABLE produtos_backup_' || TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS') || ' AS SELECT * FROM produtos';
        RAISE NOTICE 'Backup criado com sucesso';
        
        -- 3. Remover coluna evento_id
        ALTER TABLE produtos DROP COLUMN IF EXISTS evento_id;
        RAISE NOTICE 'Coluna evento_id removida com sucesso';
        
        -- 4. Recriar índices se necessário
        CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);
        CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo);
        CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status);
        CREATE INDEX IF NOT EXISTS idx_produtos_empresa_id ON produtos(empresa_id);
        
        RAISE NOTICE 'Migração concluída com sucesso!';
    ELSE
        RAISE NOTICE 'Coluna evento_id já foi removida!';
    END IF;
END $$;
