#!/usr/bin/env python3
"""
Validation script for tipo_usuario column removal
Verifies that the migration was executed successfully
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
        logging.FileHandler('migration_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationValidator:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.connection = None
        
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def validate_column_removed(self):
        """Validate that tipo_usuario column was removed"""
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
                    logger.info("✅ VALIDATION PASSED: tipo_usuario column successfully removed")
                    return True
                else:
                    logger.error("❌ VALIDATION FAILED: tipo_usuario column still exists")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error validating column removal: {e}")
            return False
    
    def validate_tipo_column_exists(self):
        """Validate that tipo column still exists and is functional"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios' 
                    AND column_name = 'tipo'
                """)
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"✅ VALIDATION PASSED: tipo column exists ({result['data_type']}, nullable: {result['is_nullable']})")
                    return True
                else:
                    logger.error("❌ VALIDATION FAILED: tipo column does not exist")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error validating tipo column: {e}")
            return False
    
    def validate_user_data_integrity(self):
        """Validate that user data is still intact"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total_users,
                           COUNT(CASE WHEN tipo = 'admin' THEN 1 END) as admin_users,
                           COUNT(CASE WHEN tipo = 'cliente' THEN 1 END) as cliente_users,
                           COUNT(CASE WHEN tipo = 'promoter' THEN 1 END) as promoter_users
                    FROM usuarios
                """)
                result = cursor.fetchone()
                
                logger.info(f"📊 User data integrity:")
                logger.info(f"   Total users: {result['total_users']}")
                logger.info(f"   Admin users: {result['admin_users']}")
                logger.info(f"   Cliente users: {result['cliente_users']}")
                logger.info(f"   Promoter users: {result['promoter_users']}")
                
                if result['total_users'] > 0:
                    logger.info("✅ VALIDATION PASSED: User data integrity maintained")
                    return True
                else:
                    logger.warning("⚠️  No users found in database")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error validating user data integrity: {e}")
            return False
    
    def validate_application_compatibility(self):
        """Test basic application compatibility after migration"""
        try:
            # Try to import the Usuario model
            sys.path.append('/app/backend')
            from app.models import Usuario
            logger.info("✅ VALIDATION PASSED: Usuario model import successful")
            
            # Test basic model functionality
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, cpf, nome, tipo FROM usuarios LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"✅ VALIDATION PASSED: Basic model query successful")
                    logger.info(f"   Sample user: {result['nome']} (tipo: {result['tipo']})")
                    return True
                else:
                    logger.warning("⚠️  No users found for compatibility test")
                    return True  # Not a failure, just empty database
                    
        except Exception as e:
            logger.error(f"❌ Error validating application compatibility: {e}")
            return False
    
    def generate_validation_report(self, results):
        """Generate a detailed validation report"""
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "database_url": self.database_url.split('@')[1] if '@' in self.database_url else "hidden",
            "tests": results,
            "overall_status": "PASSED" if all(results.values()) else "FAILED",
            "summary": {
                "total_tests": len(results),
                "passed_tests": sum(1 for result in results.values() if result),
                "failed_tests": sum(1 for result in results.values() if not result)
            }
        }
        
        logger.info("📋 VALIDATION REPORT:")
        logger.info(json.dumps(report, indent=2))
        
        # Save report to file
        with open('migration_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_validation(self):
        """Run all validation tests"""
        logger.info("🔍 Starting migration validation")
        
        try:
            # Connect to database
            if not self.connect_database():
                return False
            
            # Run validation tests
            results = {
                "column_removed": self.validate_column_removed(),
                "tipo_column_exists": self.validate_tipo_column_exists(),
                "user_data_integrity": self.validate_user_data_integrity(),
                "application_compatibility": self.validate_application_compatibility()
            }
            
            # Generate report
            report = self.generate_validation_report(results)
            
            if report["overall_status"] == "PASSED":
                logger.info("🎉 ALL VALIDATIONS PASSED! Migration successful.")
                return True
            else:
                logger.error(f"❌ VALIDATION FAILED! {report['summary']['failed_tests']} tests failed.")
                return False
                
        except Exception as e:
            logger.error(f"💥 Validation error: {e}")
            return False
            
        finally:
            if self.connection:
                self.connection.close()

def main():
    """Main validation function"""
    logger.info("=" * 60)
    logger.info("🔍 MIGRATION VALIDATION: tipo_usuario column removal")
    logger.info("=" * 60)
    
    try:
        validator = MigrationValidator()
        success = validator.run_validation()
        
        if success:
            logger.info("✅ Validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
