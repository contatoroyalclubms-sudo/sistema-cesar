#!/usr/bin/env python3
"""
Script para converter TipoUsuario de Enum para String no banco de dados
Remove conflitos de enum PostgreSQL
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# URLs de conexão
DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_URL = os.getenv("POSTGRES_URL")

def test_connection(database_url):
    """Testa conexão com o banco"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"✅ Conexão bem-sucedida: {version}")
            return True
    except Exception as e:
        logger.error(f"❌ Erro de conexão: {e}")
        return False

def backup_usuarios_table(engine):
    """Cria backup da tabela usuarios"""
    try:
        with engine.connect() as connection:
            # Verifica se backup já existe
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuarios_backup_enum'
                );
            """))
            
            if result.fetchone()[0]:
                logger.info("🔄 Backup já existe, removendo...")
                connection.execute(text("DROP TABLE usuarios_backup_enum;"))
                connection.commit()
            
            # Cria backup
            logger.info("💾 Criando backup da tabela usuarios...")
            connection.execute(text("""
                CREATE TABLE usuarios_backup_enum AS 
                SELECT * FROM usuarios;
            """))
            connection.commit()
            
            # Conta registros
            result = connection.execute(text("SELECT COUNT(*) FROM usuarios_backup_enum;"))
            count = result.fetchone()[0]
            logger.info(f"✅ Backup criado com {count} registros")
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup: {e}")
        raise

def drop_enum_type_if_exists(engine):
    """Remove o tipo enum existente"""
    try:
        with engine.connect() as connection:
            # Verifica se enum existe
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'tipousuario'
                );
            """))
            
            if result.fetchone()[0]:
                logger.info("🗑️ Removendo tipo enum tipousuario...")
                
                # Remove a constraint primeiro se existir
                connection.execute(text("""
                    ALTER TABLE usuarios 
                    DROP CONSTRAINT IF EXISTS usuarios_tipo_usuario_check;
                """))
                
                # Remove a coluna temporariamente
                connection.execute(text("""
                    ALTER TABLE usuarios 
                    DROP COLUMN IF EXISTS tipo_usuario_temp;
                """))
                
                connection.commit()
                logger.info("✅ Preparado para conversão")
            else:
                logger.info("ℹ️ Tipo enum não existe")
                
    except Exception as e:
        logger.error(f"❌ Erro ao preparar enum: {e}")
        raise

def convert_tipousuario_to_string(engine):
    """Converte coluna tipo_usuario de enum para string"""
    try:
        with engine.connect() as connection:
            logger.info("🔄 Convertendo tipo_usuario para string...")
            
            # Passo 1: Criar nova coluna string
            connection.execute(text("""
                ALTER TABLE usuarios 
                ADD COLUMN IF NOT EXISTS tipo_usuario_temp VARCHAR(20);
            """))
            
            # Passo 2: Copiar dados convertendo enum para string
            connection.execute(text("""
                UPDATE usuarios 
                SET tipo_usuario_temp = tipo_usuario::text;
            """))
            
            # Passo 3: Verificar se todos os dados foram copiados
            result = connection.execute(text("""
                SELECT COUNT(*) FROM usuarios 
                WHERE tipo_usuario_temp IS NULL;
            """))
            null_count = result.fetchone()[0]
            
            if null_count > 0:
                logger.error(f"❌ {null_count} registros com tipo_usuario_temp NULL")
                raise Exception("Falha na conversão de dados")
            
            # Passo 4: Remover coluna enum original
            connection.execute(text("""
                ALTER TABLE usuarios 
                DROP COLUMN tipo_usuario;
            """))
            
            # Passo 5: Renomear coluna temporária
            connection.execute(text("""
                ALTER TABLE usuarios 
                RENAME COLUMN tipo_usuario_temp TO tipo_usuario;
            """))
            
            # Passo 6: Adicionar constraint CHECK para validação
            connection.execute(text("""
                ALTER TABLE usuarios 
                ADD CONSTRAINT usuarios_tipo_usuario_check 
                CHECK (tipo_usuario IN ('admin', 'promoter', 'cliente'));
            """))
            
            # Passo 7: Adicionar NOT NULL se necessário
            connection.execute(text("""
                ALTER TABLE usuarios 
                ALTER COLUMN tipo_usuario SET NOT NULL;
            """))
            
            connection.commit()
            logger.info("✅ Conversão concluída com sucesso!")
            
    except Exception as e:
        logger.error(f"❌ Erro na conversão: {e}")
        raise

def verify_conversion(engine):
    """Verifica se a conversão foi bem-sucedida"""
    try:
        with engine.connect() as connection:
            # Verifica estrutura da coluna
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' AND column_name = 'tipo_usuario';
            """))
            
            column_info = result.fetchone()
            if column_info:
                logger.info(f"📋 Coluna tipo_usuario: {dict(column_info)}")
            
            # Verifica dados
            result = connection.execute(text("""
                SELECT tipo_usuario, COUNT(*) 
                FROM usuarios 
                GROUP BY tipo_usuario;
            """))
            
            logger.info("📊 Distribuição dos tipos de usuário:")
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]} usuários")
            
            # Verifica constraints
            result = connection.execute(text("""
                SELECT constraint_name, check_clause
                FROM information_schema.check_constraints 
                WHERE constraint_schema = 'public' 
                AND constraint_name LIKE '%tipo_usuario%';
            """))
            
            constraints = result.fetchall()
            if constraints:
                logger.info("🔒 Constraints ativos:")
                for constraint in constraints:
                    logger.info(f"  - {constraint[0]}: {constraint[1]}")
            
            logger.info("✅ Verificação concluída!")
            
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {e}")
        raise

def cleanup_enum_type(engine):
    """Remove o tipo enum do banco se ainda existir"""
    try:
        with engine.connect() as connection:
            # Verifica se ainda existe
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'tipousuario'
                );
            """))
            
            if result.fetchone()[0]:
                logger.info("🗑️ Removendo tipo enum restante...")
                connection.execute(text("DROP TYPE tipousuario;"))
                connection.commit()
                logger.info("✅ Tipo enum removido")
            else:
                logger.info("ℹ️ Tipo enum já removido")
                
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível remover tipo enum: {e}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando conversão TipoUsuario: Enum → String")
    
    # Escolher URL de conexão
    db_url = POSTGRES_URL or DATABASE_URL
    if not db_url:
        logger.error("❌ Nenhuma URL de banco configurada")
        return False
    
    logger.info(f"🔗 Conectando ao banco: {db_url.split('@')[1] if '@' in db_url else 'local'}")
    
    # Testar conexão
    if not test_connection(db_url):
        return False
    
    try:
        # Criar engine
        engine = create_engine(db_url)
        
        # Executar migração
        backup_usuarios_table(engine)
        drop_enum_type_if_exists(engine)
        convert_tipousuario_to_string(engine)
        verify_conversion(engine)
        cleanup_enum_type(engine)
        
        logger.info("🎉 Migração concluída com sucesso!")
        logger.info("📝 Agora você pode atualizar o modelo SQLAlchemy para usar String(20)")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Erro crítico: {e}")
        logger.info("🔄 Para reverter, execute: ALTER TABLE usuarios DROP COLUMN tipo_usuario; ALTER TABLE usuarios RENAME COLUMN tipo_usuario_temp TO tipo_usuario;")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
