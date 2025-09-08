#!/usr/bin/env python3
"""
Manual migration executor for tipo_usuario column removal
Use this script to manually execute the migration locally or for testing
"""

import os
import sys
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Execute migration manually"""
    logger.info("=" * 60)
    logger.info("🔧 MANUAL MIGRATION EXECUTOR")
    logger.info("=" * 60)
    
    # Check environment (PostgreSQL or SQLite)
    database_url = os.getenv('DATABASE_URL')
    is_local = not database_url
    
    if is_local:
        logger.info("🏠 Executando em ambiente local (SQLite)")
        logger.info("💡 Para PostgreSQL, defina DATABASE_URL")
        
        # Executar correção definitiva para SQLite
        try:
            # Ir para diretório raiz do projeto
            import os
            os.chdir('..')  # Sair de backend/migrations para raiz
            os.chdir('..')  # Sair de backend para raiz
            
            # Importar e executar correção definitiva
            sys.path.append('.')
            
            logger.info("� Executando correção definitiva para SQLite...")
            
            # Executar o script de correção principal
            import subprocess
            result = subprocess.run([
                sys.executable, 'remove_tipo_usuario_definitivo.py'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Correção executada com sucesso!")
                logger.info(result.stdout)
                sys.exit(0)
            else:
                logger.error("❌ Correção falhou!")
                logger.error(result.stderr)
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"💥 Erro na correção local: {e}")
            sys.exit(1)
    else:
        logger.info("☁️ Executando em ambiente PostgreSQL")
        
        # Execute the PostgreSQL migration
        try:
            from remove_tipo_usuario_column import TipoUsuarioColumnRemoval
            
            migration = TipoUsuarioColumnRemoval()
            success = migration.execute_migration()
            
            if success:
                logger.info("🎉 Migration executed successfully!")
                
                # Run validation
                logger.info("🔍 Running validation...")
                from validate_migration import MigrationValidator
                
                validator = MigrationValidator()
                validation_success = validator.run_validation()
                
                if validation_success:
                    logger.info("✅ Migration and validation completed successfully!")
                    sys.exit(0)
                else:
                    logger.error("❌ Migration completed but validation failed!")
                    sys.exit(1)
            else:
                logger.error("❌ Migration failed!")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"💥 Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
