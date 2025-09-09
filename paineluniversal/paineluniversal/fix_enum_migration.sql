-- Migração SQL para corrigir o enum tipousuario no PostgreSQL
-- Este script garante que o enum tenha os valores corretos

BEGIN;

-- 1. Verificar se o enum tipousuario existe
DO $$
BEGIN
    -- Verificar se o tipo existe
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipousuario') THEN
        -- Se não existe, criar com os valores corretos
        CREATE TYPE tipousuario AS ENUM ('admin', 'promoter', 'cliente');
        RAISE NOTICE 'Enum tipousuario criado com valores: admin, promoter, cliente';
    ELSE
        RAISE NOTICE 'Enum tipousuario já existe';
    END IF;
END $$;

-- 2. Adicionar valores que podem estar faltando
DO $$
BEGIN
    -- Tentar adicionar 'admin' se não existir
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'admin';
        RAISE NOTICE 'Valor admin adicionado ao enum';
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE 'Valor admin já existe no enum';
        WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao adicionar admin: %', SQLERRM;
    END;
    
    -- Tentar adicionar 'promoter' se não existir  
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'promoter';
        RAISE NOTICE 'Valor promoter adicionado ao enum';
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE 'Valor promoter já existe no enum';
        WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao adicionar promoter: %', SQLERRM;
    END;
    
    -- Tentar adicionar 'cliente' se não existir
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'cliente';
        RAISE NOTICE 'Valor cliente adicionado ao enum';
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE NOTICE 'Valor cliente já existe no enum';
        WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao adicionar cliente: %', SQLERRM;
    END;
END $$;

-- 3. Mostrar valores atuais do enum
SELECT 'Valores atuais do enum tipousuario:' as info;
SELECT enumlabel as valores_enum
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
ORDER BY enumsortorder;

-- 4. Testar se os valores funcionam
SELECT 'Testando valores do enum:' as info;
SELECT 'admin'::tipousuario as teste_admin;
SELECT 'promoter'::tipousuario as teste_promoter;  
SELECT 'cliente'::tipousuario as teste_cliente;

-- 5. Verificar se a coluna usuarios.tipo usa o enum correto
SELECT 
    column_name,
    data_type,
    udt_name,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND column_name = 'tipo';

COMMIT;

-- Log final
SELECT 'MIGRAÇÃO CONCLUÍDA: Enum tipousuario corrigido com valores: admin, promoter, cliente' as resultado;
