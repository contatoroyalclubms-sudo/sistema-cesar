"""
Migração para criar tabelas de BI e Split de Pagamentos
Executa criação de tabelas necessárias para as novas funcionalidades
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adicionar path do backend
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from app.database import engine, get_db, Base
    from app.routers.split import SplitConfiguracao, SplitRegra, SplitTransacao
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    # Continuar com configuração manual
    from sqlalchemy import create_engine
    
    # Usar DATABASE_URL ou fallback para SQLite
    database_url = os.getenv("DATABASE_URL", "sqlite:///./backend/eventos.db")
    engine = create_engine(database_url)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_bi_split_tables():
    """
    Criar tabelas para BI e Split de Pagamentos
    """
    try:
        logger.info("🔧 Iniciando criação de tabelas BI e Split...")
        
        # Criar tabelas usando SQLAlchemy
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        with engine.connect() as conn:
            # Verificar tabelas Split
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'split_%'"))
            split_tables = result.fetchall()
            
            logger.info(f"📊 Tabelas Split criadas: {[table[0] for table in split_tables]}")
            
            # Criar dados de exemplo para Split (opcional)
            create_example_split_config(conn)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        return False

def create_example_split_config(conn):
    """
    Criar configuração de exemplo para Split
    """
    try:
        logger.info("📝 Criando configuração de exemplo...")
        
        # Verificar se já existe configuração
        result = conn.execute(text("SELECT COUNT(*) FROM split_configuracoes"))
        count = result.scalar()
        
        if count == 0:
            # Inserir configuração de exemplo
            conn.execute(text("""
                INSERT INTO split_configuracoes (nome, ativo, created_at)
                VALUES ('Configuração Padrão', 1, datetime('now'))
            """))
            
            # Pegar ID da configuração criada
            result = conn.execute(text("SELECT last_insert_rowid()"))
            config_id = result.scalar()
            
            # Inserir regras de exemplo
            conn.execute(text("""
                INSERT INTO split_regras (configuracao_id, destinatario, tipo, valor, created_at)
                VALUES 
                (?, 'Organizador Principal', 'percentual', 60.0, datetime('now')),
                (?, 'Equipe Técnica', 'percentual', 25.0, datetime('now')),
                (?, 'Taxa Administrativa', 'percentual', 10.0, datetime('now')),
                (?, 'Fundo de Reserva', 'percentual', 5.0, datetime('now'))
            """), (config_id, config_id, config_id, config_id))
            
            conn.commit()
            logger.info("✅ Configuração de exemplo criada!")
        else:
            logger.info("ℹ️ Configuração já existe, pulando criação de exemplo")
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar configuração de exemplo: {e}")

def verify_database_connection():
    """
    Verificar conexão com banco de dados
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Conexão com banco de dados confirmada")
            return True
    except Exception as e:
        logger.error(f"❌ Erro de conexão com banco: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando migração BI e Split de Pagamentos...")
    
    # Verificar conexão
    if not verify_database_connection():
        sys.exit(1)
    
    # Criar tabelas
    if create_bi_split_tables():
        logger.info("🎉 Migração concluída com sucesso!")
        print("\n✅ MIGRAÇÃO CONCLUÍDA")
        print("📊 Tabelas BI e Split de Pagamentos criadas")
        print("🔗 Endpoints disponíveis:")
        print("  - GET /api/bi/metricas-tempo-real")
        print("  - GET /api/bi/graficos-dados")
        print("  - POST /api/split/configuracoes/")
        print("  - POST /api/split/calcular/")
        print("  - GET /docs - Documentação completa")
    else:
        logger.error("❌ Falha na migração")
        sys.exit(1)
