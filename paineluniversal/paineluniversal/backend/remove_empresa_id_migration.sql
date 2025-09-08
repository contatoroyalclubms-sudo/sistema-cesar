-- Migração para remover completamente a coluna empresa_id da tabela usuarios
-- Para PostgreSQL

BEGIN;

-- Verificar estrutura atual
SELECT 
    column_name, 
    is_nullable, 
    data_type,
    column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'empresa_id';

-- Remover constraint de foreign key primeiro
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS usuarios_empresa_id_fkey;

-- Remover a coluna empresa_id
ALTER TABLE usuarios DROP COLUMN IF EXISTS empresa_id;

-- Verificar que a coluna foi removida
SELECT 
    column_name, 
    is_nullable, 
    data_type,
    column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'empresa_id';

-- Listar colunas restantes da tabela usuarios
SELECT 
    column_name, 
    is_nullable, 
    data_type,
    column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios'
ORDER BY ordinal_position;

COMMIT;