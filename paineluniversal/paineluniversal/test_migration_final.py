#!/usr/bin/env python3
"""
Teste final do sistema antes do deploy
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_migration_system():
    """Testa se o sistema de migração está funcionando"""
    logger.info("🧪 Testando sistema de migração automática...")
    
    try:
        # Testar imports básicos
        import sqlalchemy
        import fastapi
        logger.info("✅ Dependências básicas OK")
        
        # Testar se consegue importar o sistema de migração
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        
        from app.migrations.auto_migrate import AutoMigration, run_auto_migration
        logger.info("✅ Sistema de migração importado com sucesso")
        
        # Testar se consegue importar do main
        from app.main import app
        logger.info("✅ Main.py importado com sucesso")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def test_file_structure():
    """Verifica estrutura de arquivos necessária"""
    logger.info("📁 Verificando estrutura de arquivos...")
    
    required_files = [
        "backend/app/main.py",
        "backend/app/migrations/__init__.py", 
        "backend/app/migrations/auto_migrate.py",
        "backend/requirements.txt",
        "Dockerfile.backend"
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            logger.info(f"✅ {file_path}")
        else:
            logger.error(f"❌ {file_path} não encontrado")
            all_good = False
    
    return all_good

def main():
    """Executa verificação final"""
    logger.info("🚀 VERIFICAÇÃO FINAL - MIGRAÇÃO AUTOMÁTICA")
    logger.info("=" * 60)
    
    tests = [
        test_file_structure,
        test_migration_system
    ]
    
    success = True
    for test in tests:
        try:
            if not test():
                success = False
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            success = False
    
    if success:
        logger.info("🎉 VERIFICAÇÃO PASSOU!")
        logger.info("✅ Sistema pronto para deploy com migração automática")
    else:
        logger.error("❌ VERIFICAÇÃO FALHOU!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
