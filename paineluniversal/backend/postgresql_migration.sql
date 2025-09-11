-- Migração PostgreSQL para remover constraint NOT NULL da coluna empresa_id
-- Este script permite que usuários sejam criados sem empresa vinculada

BEGIN;

-- Verificar estrutura atual da tabela
SELECT 
    column_name, 
    is_nullable, 
    data_type,
    column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'empresa_id';

-- Remover constraint NOT NULL da coluna empresa_id
ALTER TABLE usuarios ALTER COLUMN empresa_id DROP NOT NULL;

-- Verificar se a alteração foi aplicada
SELECT 
    column_name, 
    is_nullable, 
    data_type,
    column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'empresa_id';

-- Confirmar que existem constraints de foreign key
SELECT
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE 
    tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'usuarios'
    AND kcu.column_name = 'empresa_id';

COMMIT;