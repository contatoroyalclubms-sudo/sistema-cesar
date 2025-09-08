#!/usr/bin/env python3
"""
MIGRAÇÃO PARA PRODUÇÃO RAILWAY POSTGRESQL
Remove campo tipo_usuario da tabela usuarios em produção
"""

import os
import sys
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionMigrationPostgres:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.connection = None
        
    def connect_database(self):
        """Connect to Railway PostgreSQL database"""
        try:
            import psycopg2
            self.connection = psycopg2.connect(self.database_url)
            self.connection.autocommit = False
            logger.info("✅ Connected to Railway PostgreSQL database")
            return True
        except ImportError:
            logger.error("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
            return False
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def check_production_environment(self):
        """Verify we're in Railway production environment"""
        railway_env = os.getenv('RAILWAY_ENVIRONMENT')
        railway_project = os.getenv('RAILWAY_PROJECT_ID')
        
        logger.info(f"🚂 Railway Environment: {railway_env or 'not detected'}")
        logger.info(f"🚂 Railway Project: {railway_project or 'not detected'}")
        
        if not self.database_url.startswith('postgresql://'):
            logger.warning("⚠️ DATABASE_URL doesn't look like PostgreSQL")
        
        return True
    
    def check_tipo_usuario_exists(self):
        """Check if tipo_usuario column exists"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios' 
                    AND column_name = 'tipo_usuario'
                """)
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"📋 Column tipo_usuario found: {result[1]} (nullable: {result[2]})")
                    return True
                else:
                    logger.info("📋 Column tipo_usuario does not exist")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error checking column: {e}")
            return False
    
    def analyze_data_before_migration(self):
        """Analyze data before migration"""
        try:
            with self.connection.cursor() as cursor:
                # Count total users
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                total_users = cursor.fetchone()[0]
                
                # Check tipo distribution
                cursor.execute("""
                    SELECT tipo, COUNT(*) as count
                    FROM usuarios 
                    GROUP BY tipo
                    ORDER BY count DESC
                """)
                tipo_distribution = cursor.fetchall()
                
                # Check tipo_usuario distribution
                cursor.execute("""
                    SELECT tipo_usuario, COUNT(*) as count
                    FROM usuarios 
                    WHERE tipo_usuario IS NOT NULL
                    GROUP BY tipo_usuario
                    ORDER BY count DESC
                """)
                tipo_usuario_distribution = cursor.fetchall()
                
                # Check conflicts
                cursor.execute("""
                    SELECT COUNT(*) as conflicts
                    FROM usuarios 
                    WHERE tipo != tipo_usuario 
                    AND tipo_usuario IS NOT NULL
                """)
                conflicts = cursor.fetchone()[0]
                
                logger.info(f"📊 Data Analysis:")
                logger.info(f"   Total users: {total_users}")
                logger.info(f"   Tipo distribution: {tipo_distribution}")
                logger.info(f"   Tipo_usuario distribution: {tipo_usuario_distribution}")
                logger.info(f"   Conflicts between tipo and tipo_usuario: {conflicts}")
                
                # Save analysis
                analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "total_users": total_users,
                    "tipo_distribution": tipo_distribution,
                    "tipo_usuario_distribution": tipo_usuario_distribution,
                    "conflicts": conflicts
                }
                
                with open('pre_migration_analysis.json', 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                
                return conflicts == 0
                
        except Exception as e:
            logger.error(f"❌ Error analyzing data: {e}")
            return False
    
    def backup_tipo_usuario_data(self):
        """Create backup of tipo_usuario data"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, cpf, nome, email, tipo, tipo_usuario, criado_em
                    FROM usuarios 
                    ORDER BY id
                """)
                backup_data = cursor.fetchall()
                
                # Save backup
                backup_filename = f"usuarios_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                backup_records = []
                for row in backup_data:
                    backup_records.append({
                        "id": row[0],
                        "cpf": row[1],
                        "nome": row[2],
                        "email": row[3],
                        "tipo": row[4],
                        "tipo_usuario": row[5],
                        "criado_em": str(row[6]) if row[6] else None
                    })
                
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(backup_records, f, indent=2, ensure_ascii=False)
                
                logger.info(f"💾 Backup created: {backup_filename} ({len(backup_records)} records)")
                return backup_filename
                
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return None
    
    def execute_migration(self):
        """Execute the tipo_usuario column removal"""
        try:
            logger.info("🔄 Starting migration transaction...")
            
            with self.connection.cursor() as cursor:
                # Drop the column
                cursor.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS tipo_usuario")
                logger.info("🗑️ Column tipo_usuario dropped")
                
                # Verify it's gone
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
                    logger.error("❌ Column tipo_usuario still exists")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def verify_application_still_works(self):
        """Verify application functionality after migration"""
        try:
            with self.connection.cursor() as cursor:
                # Test basic queries that the app would use
                cursor.execute("""
                    SELECT id, cpf, nome, email, tipo, ativo
                    FROM usuarios 
                    WHERE ativo = true
                    LIMIT 5
                """)
                active_users = cursor.fetchall()
                
                cursor.execute("""
                    SELECT COUNT(*) as admin_count
                    FROM usuarios 
                    WHERE tipo = 'admin' AND ativo = true
                """)
                admin_count = cursor.fetchone()[0]
                
                logger.info(f"🧪 Post-migration verification:")
                logger.info(f"   Active users found: {len(active_users)}")
                logger.info(f"   Active admin users: {admin_count}")
                
                if admin_count > 0:
                    logger.info("✅ Application should work normally")
                    return True
                else:
                    logger.warning("⚠️ No admin users found - might need to create one")
                    return True  # Not critical failure
                    
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def create_migration_log(self, success):
        """Create detailed migration log"""
        log_entry = {
            "migration_name": "remove_tipo_usuario_column",
            "timestamp": datetime.now().isoformat(),
            "environment": "production_railway",
            "database_url": self.database_url.split('@')[1] if '@' in self.database_url else "hidden",
            "success": success,
            "railway_environment": os.getenv('RAILWAY_ENVIRONMENT'),
            "railway_project": os.getenv('RAILWAY_PROJECT_ID')
        }
        
        with open('migration_log.json', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"📝 Migration logged: {json.dumps(log_entry, indent=2)}")
    
    def run_production_migration(self):
        """Run complete production migration"""
        logger.info("🚀 STARTING PRODUCTION MIGRATION - Railway PostgreSQL")
        logger.info("=" * 60)
        
        try:
            # Step 1: Environment check
            logger.info("📋 Step 1: Checking production environment")
            if not self.check_production_environment():
                return False
            
            # Step 2: Database connection
            logger.info("📋 Step 2: Connecting to database")
            if not self.connect_database():
                return False
            
            # Step 3: Check if migration needed
            logger.info("📋 Step 3: Checking if migration is needed")
            if not self.check_tipo_usuario_exists():
                logger.info("✅ Migration not needed - column already removed")
                self.create_migration_log(True)
                return True
            
            # Step 4: Analyze data
            logger.info("📋 Step 4: Analyzing existing data")
            if not self.analyze_data_before_migration():
                logger.error("❌ Data analysis failed - aborting for safety")
                return False
            
            # Step 5: Create backup
            logger.info("📋 Step 5: Creating data backup")
            backup_file = self.backup_tipo_usuario_data()
            if not backup_file:
                logger.error("❌ Backup failed - aborting for safety")
                return False
            
            # Step 6: Execute migration
            logger.info("📋 Step 6: Executing migration")
            if not self.execute_migration():
                logger.error("❌ Migration failed - rolling back")
                self.connection.rollback()
                return False
            
            # Step 7: Verify app functionality
            logger.info("📋 Step 7: Verifying application functionality")
            if not self.verify_application_still_works():
                logger.error("❌ Post-migration verification failed")
                self.connection.rollback()
                return False
            
            # Step 8: Commit changes
            logger.info("📋 Step 8: Committing changes")
            self.connection.commit()
            logger.info("✅ Migration committed to database")
            
            self.create_migration_log(True)
            logger.info("🎉 PRODUCTION MIGRATION COMPLETED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            logger.error(f"💥 Fatal error: {e}")
            if self.connection:
                self.connection.rollback()
                logger.info("🔙 Changes rolled back")
            self.create_migration_log(False)
            return False
            
        finally:
            if self.connection:
                self.connection.close()
                logger.info("🔌 Database connection closed")

def main():
    """Main function for production migration"""
    logger.info("🎯 RAILWAY POSTGRESQL PRODUCTION MIGRATION")
    logger.info("This will remove the tipo_usuario column from usuarios table")
    logger.info("in your Railway PostgreSQL production database.")
    logger.info("=" * 60)
    
    try:
        migration = ProductionMigrationPostgres()
        success = migration.run_production_migration()
        
        if success:
            logger.info("✅ Production migration completed successfully!")
            logger.info("🔄 Your Railway app should automatically restart")
            logger.info("🧪 Test your application to ensure everything works")
            sys.exit(0)
        else:
            logger.error("❌ Production migration failed!")
            logger.error("💡 Check the logs above for details")
            logger.error("🔒 No changes were made to your database")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
