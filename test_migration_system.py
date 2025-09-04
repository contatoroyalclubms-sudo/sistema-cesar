#!/usr/bin/env python3
"""
Teste local do sistema de migração automática
Valida se as migrações funcionam corretamente antes do deploy
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o backend ao path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("migration_test")

def test_database_connection():
    """Testa conexão com o banco de dados"""
    try:
        from app.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.scalar() == 1
            logger.info("✅ Conexão com banco OK")
            return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False

def test_enum_tipousuario():
    """Testa se o enum tipousuario está funcionando"""
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Testar valores do enum
            for value in ['admin', 'promoter', 'cliente']:
                result = conn.execute(text(f"SELECT '{value}'::tipousuario"))
                assert result.scalar() == value
                logger.info(f"✅ Enum value '{value}' funcionando")
            
            logger.info("✅ Enum tipousuario totalmente funcional")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro no enum tipousuario: {e}")
        return False

def test_user_creation():
    """Testa criação de usuário admin via models"""
    try:
        from app.database import get_db
        from app.models import Usuario, TipoUsuario
        from app.auth import gerar_hash_senha
        
        db = next(get_db())
        
        # Verificar se pode criar usuário admin
        test_user = Usuario(
            cpf="00000000001",
            nome="Test Admin",
            email="test@admin.com", 
            senha_hash=gerar_hash_senha("test123"),
            tipo=TipoUsuario.ADMIN
        )
        
        # Tentar adicionar (não commit para não persistir)
        db.add(test_user)
        db.flush()  # Valida sem commit
        
        assert test_user.tipo == TipoUsuario.ADMIN
        logger.info("✅ Criação de usuário admin funcional")
        
        db.rollback()  # Desfazer
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na criação de usuário: {e}")
        return False

def test_auto_migration():
    """Testa o sistema de migração automática"""
    try:
        from app.migrations.auto_migrate import AutoMigration
        
        migration = AutoMigration()
        
        # Testar verificação do enum
        enum_ok = migration.check_tipousuario_enum()
        logger.info(f"📋 Status do enum: {'OK' if enum_ok else 'Needs fix'}")
        
        # Se precisar de correção, testar correção
        if not enum_ok:
            logger.info("🔧 Testando correção do enum...")
            migration.fix_tipousuario_enum()
            
            # Validar correção
            if migration.validate_tipousuario_enum():
                logger.info("✅ Correção do enum funcionando")
            else:
                raise Exception("Correção do enum falhou")
        
        # Testar verificação da tabela produtos  
        produtos_ok = not migration.check_evento_id_exists()
        logger.info(f"📋 Status da tabela produtos: {'OK' if produtos_ok else 'Needs migration'}")
        
        logger.info("✅ Sistema de migração automática validado")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no sistema de migração: {e}")
        return False

def main():
    """Executa todos os testes"""
    logger.info("🧪 Iniciando testes de migração...")
    logger.info("=" * 60)
    
    tests = [
        ("Conexão com Banco", test_database_connection),
        ("Enum TipoUsuario", test_enum_tipousuario), 
        ("Criação de Usuário", test_user_creation),
        ("Sistema de Migração", test_auto_migration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name}: PASSOU")
            else:
                logger.error(f"❌ {test_name}: FALHOU")
        except Exception as e:
            logger.error(f"💥 {test_name}: ERRO - {e}")
            results.append((test_name, False))
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO DOS TESTES:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para deploy.")
        return True
    else:
        logger.error("❌ ALGUNS TESTES FALHARAM! Verificar problemas antes do deploy.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
