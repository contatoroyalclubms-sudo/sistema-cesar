-- Migração para permitir empresa_id NULL na tabela usuarios
-- Este script remove a constraint NOT NULL da coluna empresa_id

-- Alterar a coluna empresa_id para permitir NULL
ALTER TABLE usuarios ALTER COLUMN empresa_id DROP NOT NULL;

-- Verificar se a alteração foi aplicada corretamente
SELECT 
    column_name, 
    is_nullable, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'usuarios' AND column_name = 'empresa_id';