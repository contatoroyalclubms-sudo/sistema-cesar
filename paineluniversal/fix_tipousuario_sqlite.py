#!/usr/bin/env python3
"""
Script para converter TipoUsuario de Enum para String no SQLite
Remove conflitos de enum
"""

import os
import sys
import sqlite3
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def get_database_path():
    """Obter caminho do banco SQLite"""
    # Procurar arquivos .db no diretório atual
    db_files = []
    for file in os.listdir('.'):
        if file.endswith('.db'):
            db_files.append(file)
    
    if db_files:
        db_path = db_files[0]  # Usar o primeiro encontrado
        logger.info(f"📂 Banco SQLite encontrado: {db_path}")
        return f"sqlite:///{db_path}"
    else:
        logger.error("❌ Nenhum arquivo .db encontrado")
        return None

def test_connection(database_url):
    """Testa conexão com o banco"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT sqlite_version();"))
            version = result.fetchone()[0]
            logger.info(f"✅ Conexão bem-sucedida: SQLite {version}")
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
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='usuarios_backup_enum';
            """))
            
            if result.fetchone():
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

def convert_tipousuario_to_string_sqlite(engine):
    """Converte coluna tipo_usuario de enum para string no SQLite"""
    try:
        with engine.connect() as connection:
            logger.info("🔄 Convertendo tipo_usuario para string...")
            
            # SQLite não suporta ALTER COLUMN diretamente, então vamos recriar a tabela
            
            # Passo 1: Criar nova tabela com estrutura corrigida
            logger.info("📋 Criando nova estrutura da tabela...")
            connection.execute(text("""
                CREATE TABLE usuarios_new (
                    id INTEGER PRIMARY KEY,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    telefone VARCHAR(20),
                    senha_hash VARCHAR(255) NOT NULL,
                    tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('admin', 'promoter', 'cliente')),
                    ativo BOOLEAN DEFAULT 1,
                    ultimo_login DATETIME,
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em DATETIME
                );
            """))
            
            # Passo 2: Copiar dados convertendo o campo tipo
            logger.info("📊 Copiando dados com conversão...")
            connection.execute(text("""
                INSERT INTO usuarios_new (
                    id, cpf, nome, email, telefone, senha_hash, 
                    tipo_usuario, ativo, ultimo_login, criado_em, atualizado_em
                )
                SELECT 
                    id, cpf, nome, email, telefone, senha_hash,
                    CASE 
                        WHEN tipo = 'admin' OR tipo = 'ADMIN' THEN 'admin'
                        WHEN tipo = 'promoter' OR tipo = 'PROMOTER' THEN 'promoter'
                        WHEN tipo = 'cliente' OR tipo = 'CLIENTE' THEN 'cliente'
                        ELSE 'cliente'
                    END as tipo_usuario,
                    ativo, ultimo_login, criado_em, atualizado_em
                FROM usuarios;
            """))
            
            # Passo 3: Verificar se todos os dados foram copiados
            result_old = connection.execute(text("SELECT COUNT(*) FROM usuarios;"))
            result_new = connection.execute(text("SELECT COUNT(*) FROM usuarios_new;"))
            count_old = result_old.fetchone()[0]
            count_new = result_new.fetchone()[0]
            
            if count_old != count_new:
                logger.error(f"❌ Erro na cópia: {count_old} registros originais, {count_new} copiados")
                raise Exception("Falha na conversão de dados")
            
            # Passo 4: Remover tabela original e renomear nova
            logger.info("🔄 Substituindo tabela original...")
            connection.execute(text("DROP TABLE usuarios;"))
            connection.execute(text("ALTER TABLE usuarios_new RENAME TO usuarios;"))
            
            # Passo 5: Recriar índices
            logger.info("🔗 Recriando índices...")
            connection.execute(text("CREATE UNIQUE INDEX idx_usuarios_cpf ON usuarios(cpf);"))
            connection.execute(text("CREATE UNIQUE INDEX idx_usuarios_email ON usuarios(email);"))
            connection.execute(text("CREATE INDEX idx_usuarios_id ON usuarios(id);"))
            
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
                PRAGMA table_info(usuarios);
            """))
            
            columns = result.fetchall()
            logger.info("📋 Estrutura da tabela usuarios:")
            for col in columns:
                if col[1] == 'tipo_usuario':
                    logger.info(f"  - {col[1]}: {col[2]} (nullable: {not col[3]})")
            
            # Verifica dados
            result = connection.execute(text("""
                SELECT tipo_usuario, COUNT(*) 
                FROM usuarios 
                GROUP BY tipo_usuario;
            """))
            
            logger.info("📊 Distribuição dos tipos de usuário:")
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]} usuários")
            
            # Verifica se todos os valores são válidos
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM usuarios 
                WHERE tipo_usuario NOT IN ('admin', 'promoter', 'cliente');
            """))
            
            invalid_count = result.fetchone()[0]
            if invalid_count > 0:
                logger.warning(f"⚠️ {invalid_count} registros com tipo_usuario inválido")
            else:
                logger.info("✅ Todos os valores são válidos")
            
            logger.info("✅ Verificação concluída!")
            
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {e}")
        raise

def main():
    """Função principal"""
    logger.info("🚀 Iniciando conversão TipoUsuario: Enum → String (SQLite)")
    
    # Obter caminho do banco
    db_url = get_database_path()
    if not db_url:
        return False
    
    # Testar conexão
    if not test_connection(db_url):
        return False
    
    try:
        # Criar engine
        engine = create_engine(db_url)
        
        # Executar migração
        backup_usuarios_table(engine)
        convert_tipousuario_to_string_sqlite(engine)
        verify_conversion(engine)
        
        logger.info("🎉 Migração concluída com sucesso!")
        logger.info("📝 Agora você pode atualizar o modelo SQLAlchemy para usar String(20)")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Erro crítico: {e}")
        logger.info("🔄 Para reverter, execute: DROP TABLE usuarios; ALTER TABLE usuarios_backup_enum RENAME TO usuarios;")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
