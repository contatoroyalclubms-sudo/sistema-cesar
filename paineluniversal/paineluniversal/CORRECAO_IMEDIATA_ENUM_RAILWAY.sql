-- 🚨 CORREÇÃO IMEDIATA ENUM TIPOUSUARIO - RAILWAY CONSOLE
-- Execute este script DIRETAMENTE no Railway PostgreSQL Console
-- Resolve o problema: invalid input value for enum tipousuario: 'admin'

BEGIN;

-- 1. VERIFICAR ESTADO ATUAL DO ENUM
SELECT 'VALORES_ATUAIS_ENUM' as status, enumlabel as valor 
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
ORDER BY enumsortorder;

-- 2. ADICIONAR VALORES LOWERCASE (SEGURO - NÃO QUEBRA EXISTENTES)
DO $$
BEGIN
    -- Adicionar 'admin' se não existir
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'admin';
        RAISE NOTICE '✅ Valor admin adicionado ao enum tipousuario';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE '✓ Valor admin já existe';
    END;
    
    -- Adicionar 'promoter' se não existir  
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'promoter';
        RAISE NOTICE '✅ Valor promoter adicionado ao enum tipousuario';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE '✓ Valor promoter já existe';
    END;
    
    -- Adicionar 'cliente' se não existir
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'cliente';
        RAISE NOTICE '✅ Valor cliente adicionado ao enum tipousuario';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE '✓ Valor cliente já existe';
    END;
END $$;

-- 3. CORRIGIR USUÁRIOS EXISTENTES (UPPERCASE → lowercase)
UPDATE usuarios SET tipo = 'admin' WHERE tipo = 'ADMIN';
UPDATE usuarios SET tipo = 'promoter' WHERE tipo = 'PROMOTER'; 
UPDATE usuarios SET tipo = 'cliente' WHERE tipo = 'CLIENTE';

-- 4. VALIDAR CORREÇÃO
SELECT 'ENUM_CORRIGIDO' as status, enumlabel as valor 
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
ORDER BY enumsortorder;

-- 5. TESTAR CADA VALOR (GARANTIR FUNCIONAMENTO)
SELECT 'admin'::tipousuario as teste_admin;
SELECT 'promoter'::tipousuario as teste_promoter;
SELECT 'cliente'::tipousuario as teste_cliente;

-- 6. VERIFICAR USUÁRIOS ATUALIZADOS
SELECT 'USUARIOS_POR_TIPO' as status, tipo, COUNT(*) as quantidade
FROM usuarios 
GROUP BY tipo
ORDER BY tipo;

COMMIT;

-- ✅ CONFIRMAÇÃO DE SUCESSO
SELECT '🎉 ENUM TIPOUSUARIO CORRIGIDO - REGISTRO DE ADMIN DEVE FUNCIONAR' as resultado;
