#!/usr/bin/env python3
"""
AUTO-DEPLOY MIGRATION FOR RAILWAY
Executes automatically during Railway deployment to remove tipo_usuario column
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def is_railway_environment():
    """Check if running in Railway environment"""
    return bool(os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'))

def run_migration():
    """Run the production migration"""
    logger.info("🚂 Railway Auto-Deploy Migration Starting")
    
    if not is_railway_environment():
        logger.info("🏠 Not in Railway environment - skipping migration")
        return True
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.warning("⚠️ DATABASE_URL not found - skipping migration")
        return True
    
    try:
        # Execute the production migration
        result = subprocess.run([
            sys.executable, 
            '/app/migrate_production_railway.py'
        ], capture_output=True, text=True, timeout=300)
        
        logger.info("📋 Migration Output:")
        logger.info(result.stdout)
        
        if result.stderr:
            logger.warning("⚠️ Migration Warnings:")
            logger.warning(result.stderr)
        
        if result.returncode == 0:
            logger.info("✅ Migration completed successfully")
            return True
        else:
            logger.error(f"❌ Migration failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("⏰ Migration timed out")
        return False
    except Exception as e:
        logger.error(f"💥 Migration error: {e}")
        return False

def start_application():
    """Start the main application"""
    logger.info("🚀 Starting FastAPI application")
    
    port = os.getenv('PORT', '8000')
    
    # Start uvicorn
    cmd = [
        'uvicorn', 
        'app.main:app', 
        '--host', '0.0.0.0', 
        '--port', port,
        '--access-log'
    ]
    
    logger.info(f"🔥 Executing: {' '.join(cmd)}")
    
    # This will not return - replaces current process
    os.execvp(cmd[0], cmd)

def main():
    """Main deployment function"""
    logger.info("🚂 RAILWAY AUTO-DEPLOYMENT WITH MIGRATION")
    logger.info("=" * 50)
    
    # Step 1: Run migration if needed
    migration_success = run_migration()
    
    if not migration_success:
        logger.error("❌ Migration failed - stopping deployment")
        sys.exit(1)
    
    # Step 2: Start application
    logger.info("🎉 Migration completed - starting application")
    start_application()

if __name__ == "__main__":
    main()
