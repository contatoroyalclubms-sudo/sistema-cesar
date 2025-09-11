-- CORREÇÃO CRÍTICA: Adicionar coluna tipo_usuario no PostgreSQL
-- Execute este SQL diretamente no console do Railway

-- 1. Verificar se a tabela usuarios existe
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
ORDER BY ordinal_position;

-- 2. Se a coluna tipo_usuario NÃO existir, execute isto:
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS tipo_usuario VARCHAR(20) DEFAULT 'cliente';

-- 3. Atualizar usuários existentes
UPDATE usuarios 
SET tipo_usuario = 'cliente' 
WHERE tipo_usuario IS NULL;

-- 4. Tornar a coluna NOT NULL
ALTER TABLE usuarios 
ALTER COLUMN tipo_usuario SET NOT NULL;

-- 5. Teste final - esta query deve funcionar agora
SELECT 
    id, 
    cpf, 
    nome, 
    tipo_usuario 
FROM usuarios 
LIMIT 5;

-- 6. Verificar que a estrutura está correta
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default 
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND column_name = 'tipo_usuario';
