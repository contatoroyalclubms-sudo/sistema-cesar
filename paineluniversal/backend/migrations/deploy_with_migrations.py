#!/usr/bin/env python3
"""
Auto-deployment script for Railway
Executes database migrations before starting the backend service
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy_migrations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeploymentMigrations:
    def __init__(self):
        self.migrations_path = "/app/backend/migrations"
        self.python_executable = sys.executable
        
    def check_environment(self):
        """Check if we're in Railway environment"""
        railway_env = os.getenv('RAILWAY_ENVIRONMENT')
        database_url = os.getenv('DATABASE_URL')
        
        logger.info(f"🚂 Railway Environment: {railway_env or 'local'}")
        logger.info(f"🗄️  Database URL configured: {'Yes' if database_url else 'No'}")
        
        if not database_url:
            logger.warning("⚠️  DATABASE_URL not found. Skipping migrations.")
            return False
            
        return True
    
    def run_migration(self, migration_file):
        """Run a specific migration file"""
        migration_path = os.path.join(self.migrations_path, migration_file)
        
        if not os.path.exists(migration_path):
            logger.warning(f"⚠️  Migration file not found: {migration_path}")
            return False
        
        try:
            logger.info(f"🔄 Running migration: {migration_file}")
            
            # Execute migration
            result = subprocess.run(
                [self.python_executable, migration_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Migration {migration_file} completed successfully")
                logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Migration {migration_file} failed")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Migration {migration_file} timed out")
            return False
        except Exception as e:
            logger.error(f"💥 Error running migration {migration_file}: {e}")
            return False
    
    def execute_all_migrations(self):
        """Execute all pending migrations"""
        logger.info("🎯 Starting deployment migrations")
        
        # List of migrations to run in order
        migrations = [
            "remove_tipo_usuario_column.py"
        ]
        
        success_count = 0
        total_count = len(migrations)
        
        for migration in migrations:
            if self.run_migration(migration):
                success_count += 1
            else:
                logger.error(f"❌ Migration {migration} failed. Stopping deployment.")
                return False
        
        logger.info(f"📊 Migrations completed: {success_count}/{total_count}")
        return success_count == total_count
    
    def start_backend_service(self):
        """Start the backend service after migrations"""
        try:
            logger.info("🚀 Starting backend service")
            
            # Change to backend directory
            os.chdir("/app/backend")
            
            # Start uvicorn
            cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000")]
            
            logger.info(f"🔥 Executing: {' '.join(cmd)}")
            
            # Execute the command (this will not return)
            os.execvp(cmd[0], cmd)
            
        except Exception as e:
            logger.error(f"💥 Failed to start backend service: {e}")
            sys.exit(1)

def main():
    """Main deployment function"""
    logger.info("=" * 60)
    logger.info("🚂 RAILWAY AUTO-DEPLOYMENT WITH MIGRATIONS")
    logger.info("=" * 60)
    
    deployment = DeploymentMigrations()
    
    # Check environment
    if not deployment.check_environment():
        logger.info("ℹ️  Skipping migrations, starting service directly")
        deployment.start_backend_service()
        return
    
    # Execute migrations
    if deployment.execute_all_migrations():
        logger.info("✅ All migrations completed successfully")
    else:
        logger.error("❌ Some migrations failed. Service startup aborted.")
        sys.exit(1)
    
    # Start backend service
    deployment.start_backend_service()

if __name__ == "__main__":
    main()
