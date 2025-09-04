#!/usr/bin/env python3
"""
Migration: Remove tipo_usuario column from usuarios table
Date: 2025-08-30
Author: AI Assistant
Description: Remove redundant tipo_usuario column from usuarios table safely
"""

import os
import sys
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_remove_tipo_usuario.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TipoUsuarioColumnRemoval:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.connection = None
        self.migration_executed = False
        
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.connection.autocommit = False
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def check_column_exists(self):
        """Check if tipo_usuario column exists in usuarios table"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios' 
                    AND column_name = 'tipo_usuario'
                """)
                result = cursor.fetchone()
                exists = result is not None
                logger.info(f"📋 Column tipo_usuario exists: {exists}")
                return exists
        except Exception as e:
            logger.error(f"❌ Error checking column existence: {e}")
            return False
    
    def backup_tipo_usuario_data(self):
        """Backup tipo_usuario data before removal"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, cpf, nome, tipo, tipo_usuario, criado_em
                    FROM usuarios 
                    WHERE tipo_usuario IS NOT NULL
                """)
                backup_data = cursor.fetchall()
                
                # Save backup to file
                backup_filename = f"backup_tipo_usuario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_filename, 'w') as f:
                    json.dump([dict(row) for row in backup_data], f, indent=2, default=str)
                
                logger.info(f"💾 Backup saved to {backup_filename} ({len(backup_data)} records)")
                return backup_filename
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return None
    
    def verify_data_consistency(self):
        """Verify that tipo and tipo_usuario have consistent data"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check for conflicts between tipo and tipo_usuario
                cursor.execute("""
                    SELECT COUNT(*) as conflicts
                    FROM usuarios 
                    WHERE tipo != tipo_usuario 
                    AND tipo_usuario IS NOT NULL
                """)
                conflicts = cursor.fetchone()['conflicts']
                
                if conflicts > 0:
                    logger.warning(f"⚠️  Found {conflicts} conflicts between tipo and tipo_usuario")
                    
                    # Log conflicts for review
                    cursor.execute("""
                        SELECT id, cpf, nome, tipo, tipo_usuario
                        FROM usuarios 
                        WHERE tipo != tipo_usuario 
                        AND tipo_usuario IS NOT NULL
                    """)
                    conflict_data = cursor.fetchall()
                    
                    for row in conflict_data:
                        logger.warning(f"   Conflict: User {row['id']} ({row['cpf']}) - tipo='{row['tipo']}', tipo_usuario='{row['tipo_usuario']}'")
                    
                    return False
                else:
                    logger.info("✅ No data conflicts found between tipo and tipo_usuario")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Error verifying data consistency: {e}")
            return False
    
    def remove_tipo_usuario_column(self):
        """Remove the tipo_usuario column from usuarios table"""
        try:
            with self.connection.cursor() as cursor:
                # Remove the column
                cursor.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS tipo_usuario")
                logger.info("🗑️  Successfully removed tipo_usuario column")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error removing column: {e}")
            return False
    
    def verify_removal(self):
        """Verify that the column was successfully removed"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios' 
                    AND column_name = 'tipo_usuario'
                """)
                result = cursor.fetchone()
                
                if result is None:
                    logger.info("✅ Column tipo_usuario successfully removed")
                    return True
                else:
                    logger.error("❌ Column tipo_usuario still exists after removal attempt")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error verifying removal: {e}")
            return False
    
    def log_migration_completion(self):
        """Log the completion of migration"""
        completion_log = {
            "migration": "remove_tipo_usuario_column",
            "timestamp": datetime.now().isoformat(),
            "status": "completed" if self.migration_executed else "failed",
            "database_url": self.database_url.split('@')[1] if '@' in self.database_url else "hidden"
        }
        
        logger.info(f"📝 Migration log: {json.dumps(completion_log, indent=2)}")
        
        # Also save to file
        with open('migration_completion.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {json.dumps(completion_log)}\\n")
    
    def execute_migration(self):
        """Execute the complete migration process"""
        logger.info("🚀 Starting tipo_usuario column removal migration")
        
        try:
            # Step 1: Connect to database
            if not self.connect_database():
                return False
            
            # Step 2: Check if column exists
            if not self.check_column_exists():
                logger.info("ℹ️  Column tipo_usuario does not exist. Migration not needed.")
                return True
            
            # Step 3: Verify data consistency
            if not self.verify_data_consistency():
                logger.error("❌ Data inconsistency found. Migration aborted for safety.")
                return False
            
            # Step 4: Create backup
            backup_file = self.backup_tipo_usuario_data()
            if not backup_file:
                logger.error("❌ Backup failed. Migration aborted for safety.")
                return False
            
            # Step 5: Begin transaction
            logger.info("🔄 Starting database transaction")
            
            # Step 6: Remove column
            if not self.remove_tipo_usuario_column():
                self.connection.rollback()
                logger.error("❌ Column removal failed. Transaction rolled back.")
                return False
            
            # Step 7: Verify removal
            if not self.verify_removal():
                self.connection.rollback()
                logger.error("❌ Column removal verification failed. Transaction rolled back.")
                return False
            
            # Step 8: Commit transaction
            self.connection.commit()
            logger.info("✅ Transaction committed successfully")
            
            self.migration_executed = True
            logger.info("🎉 Migration completed successfully!")
            return True
            
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"❌ Migration failed with error: {e}")
            return False
            
        finally:
            if self.connection:
                self.connection.close()
            self.log_migration_completion()

def main():
    """Main function to execute migration"""
    logger.info("=" * 60)
    logger.info("🎯 MIGRATION: Remove tipo_usuario column from usuarios table")
    logger.info("=" * 60)
    
    try:
        migration = TipoUsuarioColumnRemoval()
        success = migration.execute_migration()
        
        if success:
            logger.info("✅ Migration completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
