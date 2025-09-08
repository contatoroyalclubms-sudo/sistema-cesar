#!/usr/bin/env python
"""
Script simples para criar tabelas de impressoras usando SQLAlchemy
"""

import os
import sys
import logging

# Adicionar o diretório do backend ao path
backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'app')
sys.path.insert(0, backend_path)

# Agora importar
import database
import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Criar todas as tabelas do sistema"""
    try:
        logger.info("🚀 Criando tabelas do sistema de impressoras...")
        
        # Criar todas as tabelas definidas nos models
        models.Base.metadata.create_all(bind=database.engine)
        
        logger.info("✅ Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        from sqlalchemy import inspect
        inspector = inspect(database.engine)
        tabelas = inspector.get_table_names()
        
        tabelas_printer = [t for t in tabelas if 'print' in t.lower() or 'impressora' in t.lower()]
        
        if tabelas_printer:
            logger.info(f"📋 Tabelas de impressora encontradas: {', '.join(tabelas_printer)}")
        else:
            logger.info("📋 Verificando todas as tabelas...")
            logger.info(f"Total de tabelas: {len(tabelas)}")
            for tabela in tabelas:
                logger.info(f"  - {tabela}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        sys.exit(1)
