#!/usr/bin/env python3
"""
MIGRAÇÃO POSTGRESQL: Remover coluna tipo_usuario da tabela usuarios

🎯 OBJETIVO: Finalizar migração removendo coluna redundante do PostgreSQL de produção
- O código já foi atualizado para usar apenas 'tipo'
- Agora precisa remover a coluna 'tipo_usuario' do banco PostgreSQL

⚠️ ATENÇÃO: Execute apenas após confirmar que o código está funcionando
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLTipoUsuarioMigration:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.database_url:
            logger.error("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
            raise ValueError("DATABASE_URL é obrigatória para migração PostgreSQL")
        
        # Converter postgres:// para postgresql:// se necessário
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        self.engine = create_engine(self.database_url, pool_pre_ping=True, pool_recycle=300)

    def diagnose_postgresql_state(self):
        """Diagnosticar estado atual do PostgreSQL"""
        logger.info("🔍 Diagnosticando estado do PostgreSQL...")
        
        try:
            with self.engine.connect() as conn:
                # Verificar se tabela usuarios existe
                inspector = inspect(self.engine)
                tables = inspector.get_table_names()
                
                if 'usuarios' not in tables:
                    logger.error("❌ Tabela 'usuarios' não encontrada")
                    return False
                
                # Verificar colunas da tabela usuarios
                columns = inspector.get_columns('usuarios')
                column_names = [col['name'] for col in columns]
                
                has_tipo = 'tipo' in column_names
                has_tipo_usuario = 'tipo_usuario' in column_names
                
                logger.info(f"📊 Coluna 'tipo' existe: {has_tipo}")
                logger.info(f"📊 Coluna 'tipo_usuario' existe: {has_tipo_usuario}")
                
                if not has_tipo:
                    logger.error("❌ Coluna 'tipo' não encontrada - migração impossível")
                    return False
                
                if not has_tipo_usuario:
                    logger.info("✅ Coluna 'tipo_usuario' já foi removida - migração desnecessária")
                    return "already_migrated"
                
                # Verificar inconsistências de dados
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN tipo != tipo_usuario THEN 1 ELSE 0 END) as inconsistentes,
                        SUM(CASE WHEN tipo IS NULL THEN 1 ELSE 0 END) as tipo_null,
                        SUM(CASE WHEN tipo_usuario IS NULL THEN 1 ELSE 0 END) as tipo_usuario_null
                    FROM usuarios
                """))
                
                stats = result.fetchone()
                logger.info(f"📊 Total de usuários: {stats.total}")
                logger.info(f"⚠️ Registros inconsistentes (tipo != tipo_usuario): {stats.inconsistentes}")
                logger.info(f"❌ Registros com tipo NULL: {stats.tipo_null}")
                logger.info(f"❌ Registros com tipo_usuario NULL: {stats.tipo_usuario_null}")
                
                # Verificar distribuição de tipos
                result = conn.execute(text("""
                    SELECT tipo, COUNT(*) as count
                    FROM usuarios 
                    GROUP BY tipo 
                    ORDER BY count DESC
                """))
                
                logger.info("📊 Distribuição de tipos:")
                for row in result.fetchall():
                    logger.info(f"   {row.tipo}: {row.count} usuários")
                
                # Se há inconsistências, mostrar exemplos
                if stats.inconsistentes > 0:
                    result = conn.execute(text("""
                        SELECT id, nome, email, tipo, tipo_usuario 
                        FROM usuarios 
                        WHERE tipo != tipo_usuario 
                        LIMIT 5
                    """))
                    
                    logger.warning("🔍 Exemplos de inconsistências encontradas:")
                    for row in result.fetchall():
                        logger.warning(f"   ID {row.id}: {row.nome} - tipo='{row.tipo}' vs tipo_usuario='{row.tipo_usuario}'")
                
                return {
                    "total": stats.total,
                    "inconsistentes": stats.inconsistentes,
                    "tipo_null": stats.tipo_null,
                    "tipo_usuario_null": stats.tipo_usuario_null
                }
                
        except Exception as e:
            logger.error(f"❌ Erro no diagnóstico: {e}")
            return False

    def sync_data_before_removal(self):
        """Sincronizar dados antes de remover coluna"""
        logger.info("🔧 Sincronizando dados antes da remoção...")
        
        try:
            with self.engine.begin() as trans:
                conn = trans.connection
                
                # Estratégia 1: Sincronizar tipo = tipo_usuario onde há diferença
                logger.info("1️⃣ Sincronizando tipo = tipo_usuario...")
                result = conn.execute(text("""
                    UPDATE usuarios 
                    SET tipo = tipo_usuario 
                    WHERE tipo != tipo_usuario OR tipo IS NULL
                """))
                sync_count = result.rowcount
                logger.info(f"✅ {sync_count} registros sincronizados")
                
                # Estratégia 2: Corrigir valores NULL em tipo
                logger.info("2️⃣ Corrigindo valores NULL...")
                result = conn.execute(text("""
                    UPDATE usuarios 
                    SET tipo = 'cliente' 
                    WHERE tipo IS NULL
                """))
                null_fixes = result.rowcount
                logger.info(f"✅ {null_fixes} registros com tipo NULL corrigidos")
                
                # Estratégia 3: Normalizar valores (lowercase, trim)
                logger.info("3️⃣ Normalizando valores...")
                result = conn.execute(text("""
                    UPDATE usuarios 
                    SET tipo = LOWER(TRIM(tipo))
                    WHERE tipo IS NOT NULL
                """))
                normalized = result.rowcount
                logger.info(f"✅ {normalized} registros normalizados")
                
                # Validação final
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM usuarios 
                    WHERE tipo IS NULL OR tipo NOT IN ('admin', 'promoter', 'cliente')
                """))
                invalid_count = result.scalar()
                
                if invalid_count > 0:
                    logger.warning(f"⚠️ {invalid_count} registros ainda têm valores inválidos")
                    
                    # Mostrar valores inválidos
                    result = conn.execute(text("""
                        SELECT DISTINCT tipo, COUNT(*) 
                        FROM usuarios 
                        WHERE tipo NOT IN ('admin', 'promoter', 'cliente')
                        GROUP BY tipo
                    """))
                    
                    for row in result.fetchall():
                        logger.warning(f"   Valor inválido: '{row.tipo}' ({row.count} usuários)")
                    
                    # Corrigir valores inválidos para 'cliente'
                    result = conn.execute(text("""
                        UPDATE usuarios 
                        SET tipo = 'cliente' 
                        WHERE tipo NOT IN ('admin', 'promoter', 'cliente')
                    """))
                    fixed_invalid = result.rowcount
                    logger.info(f"✅ {fixed_invalid} valores inválidos corrigidos para 'cliente'")
                
                logger.info("✅ Sincronização de dados concluída")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro na sincronização: {e}")
            return False

    def create_postgresql_backup(self):
        """Criar backup da tabela usuarios antes da migração"""
        logger.info("💾 Criando backup da tabela usuarios...")
        
        try:
            with self.engine.begin() as trans:
                conn = trans.connection
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_table = f"usuarios_backup_tipo_usuario_{timestamp}"
                
                # Criar tabela de backup
                conn.execute(text(f"""
                    CREATE TABLE {backup_table} AS 
                    SELECT * FROM usuarios
                """))
                
                # Verificar backup
                result = conn.execute(text(f"SELECT COUNT(*) FROM {backup_table}"))
                backup_count = result.scalar()
                
                logger.info(f"✅ Backup criado: {backup_table} ({backup_count} registros)")
                return backup_table
                
        except Exception as e:
            logger.error(f"❌ Erro no backup: {e}")
            return None

    def remove_tipo_usuario_column(self):
        """Remover a coluna tipo_usuario da tabela usuarios"""
        logger.info("🗑️ Removendo coluna tipo_usuario...")
        
        try:
            with self.engine.begin() as trans:
                conn = trans.connection
                
                # PostgreSQL suporta DROP COLUMN diretamente
                conn.execute(text("ALTER TABLE usuarios DROP COLUMN tipo_usuario"))
                
                logger.info("✅ Coluna tipo_usuario removida com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover coluna: {e}")
            return False

    def validate_postgresql_migration(self):
        """Validar que a migração PostgreSQL foi bem-sucedida"""
        logger.info("✅ Validando migração PostgreSQL...")
        
        try:
            with self.engine.connect() as conn:
                # Verificar se coluna foi removida
                inspector = inspect(self.engine)
                columns = inspector.get_columns('usuarios')
                column_names = [col['name'] for col in columns]
                
                if 'tipo_usuario' in column_names:
                    logger.error("❌ Coluna tipo_usuario ainda existe")
                    return False
                
                if 'tipo' not in column_names:
                    logger.error("❌ Coluna tipo não existe")
                    return False
                
                logger.info("✅ Estrutura da tabela correta")
                
                # Verificar integridade dos dados
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN tipo = 'admin' THEN 1 END) as admins,
                        COUNT(CASE WHEN tipo = 'promoter' THEN 1 END) as promoters,
                        COUNT(CASE WHEN tipo = 'cliente' THEN 1 END) as clientes,
                        COUNT(CASE WHEN tipo IS NULL THEN 1 END) as nulls
                    FROM usuarios
                """))
                
                stats = result.fetchone()
                logger.info(f"📊 Validação de dados:")
                logger.info(f"   Total: {stats.total}")
                logger.info(f"   Admins: {stats.admins}")
                logger.info(f"   Promoters: {stats.promoters}")
                logger.info(f"   Clientes: {stats.clientes}")
                logger.info(f"   NULLs: {stats.nulls}")
                
                if stats.nulls > 0:
                    logger.error(f"❌ {stats.nulls} registros com tipo NULL")
                    return False
                
                # Testar consulta típica de autenticação
                result = conn.execute(text("""
                    SELECT id, nome, email, tipo 
                    FROM usuarios 
                    WHERE tipo = 'admin' 
                    LIMIT 1
                """))
                
                admin_user = result.fetchone()
                if admin_user:
                    logger.info(f"✅ Consulta de autenticação funcionando: Admin {admin_user.nome} encontrado")
                else:
                    logger.warning("⚠️ Nenhum usuário admin encontrado")
                
                logger.info("✅ Validação PostgreSQL concluída com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return False

    def run_postgresql_migration(self):
        """Executar migração completa do PostgreSQL"""
        logger.info("🚀 INICIANDO MIGRAÇÃO POSTGRESQL")
        logger.info("=" * 60)
        logger.info("🎯 Removendo coluna tipo_usuario da tabela usuarios")
        logger.info("=" * 60)
        
        # 1. Diagnóstico
        diagnosis = self.diagnose_postgresql_state()
        if diagnosis == "already_migrated":
            logger.info("✅ Migração PostgreSQL já foi aplicada")
            return True
        elif not diagnosis:
            logger.error("❌ Diagnóstico falhou - abortando")
            return False
        
        # 2. Criar backup
        backup_table = self.create_postgresql_backup()
        if not backup_table:
            logger.error("❌ Falha no backup - abortando migração")
            return False
        
        # 3. Sincronizar dados
        if not self.sync_data_before_removal():
            logger.error("❌ Falha na sincronização - abortando")
            return False
        
        # 4. Remover coluna
        if not self.remove_tipo_usuario_column():
            logger.error("❌ Falha na remoção da coluna")
            return False
        
        # 5. Validar
        if not self.validate_postgresql_migration():
            logger.error("❌ Validação falhou")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 MIGRAÇÃO POSTGRESQL CONCLUÍDA!")
        logger.info("✅ Coluna tipo_usuario removida do PostgreSQL")
        logger.info("✅ Dados validados e íntegros")
        logger.info("✅ Sistema funcionando apenas com campo 'tipo'")
        logger.info(f"💾 Backup disponível: {backup_table}")
        logger.info("=" * 60)
        
        return True

def main():
    """Ponto de entrada principal"""
    try:
        migration = PostgreSQLTipoUsuarioMigration()
        success = migration.run_postgresql_migration()
        return success
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
