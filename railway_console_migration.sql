-- SCRIPT SQL PARA RAILWAY CONSOLE
-- Execute este script no Railway PostgreSQL Console para remover tipo_usuario

-- 1. Verificar estrutura atual da tabela usuarios
\d usuarios;

-- 2. Verificar se tipo_usuario existe
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND column_name IN ('tipo', 'tipo_usuario')
ORDER BY column_name;

-- 3. Verificar dados antes da migração
SELECT 
    COUNT(*) as total_usuarios,
    COUNT(CASE WHEN tipo = 'admin' THEN 1 END) as admins,
    COUNT(CASE WHEN tipo = 'cliente' THEN 1 END) as clientes,
    COUNT(CASE WHEN tipo_usuario IS NOT NULL THEN 1 END) as com_tipo_usuario
FROM usuarios;

-- 4. Verificar conflitos entre tipo e tipo_usuario
SELECT COUNT(*) as conflitos
FROM usuarios 
WHERE tipo != tipo_usuario 
AND tipo_usuario IS NOT NULL;

-- 5. Backup dos dados (opcional - crie uma tabela temporária)
CREATE TABLE usuarios_backup_tipo_usuario AS 
SELECT id, cpf, nome, email, tipo, tipo_usuario, criado_em
FROM usuarios;

-- 6. EXECUTAR A MIGRAÇÃO - REMOVER A COLUNA
BEGIN;

-- Remover a coluna tipo_usuario
ALTER TABLE usuarios DROP COLUMN IF EXISTS tipo_usuario;

-- Verificar que foi removida
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND column_name = 'tipo_usuario';

-- Se não retornar nenhuma linha, a coluna foi removida com sucesso

-- Verificar estrutura final
\d usuarios;

-- Verificar que os dados estão íntegros
SELECT COUNT(*) as total_usuarios_apos_migracao FROM usuarios;

-- Se tudo estiver OK, COMMIT
COMMIT;

-- 7. Limpeza (opcional) - remover tabela de backup após confirmar que tudo funciona
-- DROP TABLE usuarios_backup_tipo_usuario;

-- 8. Testar funcionalidade básica
SELECT id, cpf, nome, tipo, ativo 
FROM usuarios 
WHERE ativo = true 
LIMIT 5;

-- RESULTADO ESPERADO:
-- ✅ Coluna tipo_usuario removida
-- ✅ Coluna tipo mantida e funcionando
-- ✅ Todos os dados de usuários preservados
-- ✅ Aplicação funciona normalmente
