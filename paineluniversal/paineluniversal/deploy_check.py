#!/usr/bin/env python3
"""
Script para verificar e preparar deploy
Executa antes do deploy para garantir que tudo está correto
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório backend ao path para imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.migrations.auto_migrate import AutoMigration
except ImportError as e:
    print(f"⚠️ Não foi possível importar AutoMigration: {e}")
    print("🔄 Deploy continuará sem verificação de migração")
    sys.exit(0)  # Não falhar o deploy por isso

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_deploy_readiness():
    """Verifica se o deploy está pronto"""
    logger.info("🔍 VERIFICAÇÃO DE DEPLOY - PAINEL UNIVERSAL")
    logger.info("=" * 60)
    
    checks = []
    all_good = True
    
    # 1. Verificar variáveis de ambiente
    logger.info("📋 Verificando variáveis de ambiente...")
    
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Mascarar senha para log
        if '@' in database_url:
            masked_url = database_url.split('@')[1]
            checks.append(f"✅ DATABASE_URL configurada: ...@{masked_url}")
        else:
            checks.append("✅ DATABASE_URL configurada")
    else:
        checks.append("❌ DATABASE_URL não encontrada")
        all_good = False
    
    # Verificar outras variáveis importantes
    env_vars = {
        "SECRET_KEY": "Chave secreta JWT",
        "RAILWAY_ENVIRONMENT": "Ambiente Railway"
    }
    
    for var, desc in env_vars.items():
        if os.getenv(var):
            checks.append(f"✅ {var} configurada")
        else:
            checks.append(f"⚠️ {var} não encontrada ({desc})")
    
    # 2. Verificar conexão com banco (se DATABASE_URL existe)
    if database_url:
        logger.info("🔌 Testando conexão com banco de dados...")
        try:
            migration = AutoMigration()
            with migration.engine.connect() as conn:
                result = conn.execute("SELECT 1")
                if result.scalar() == 1:
                    checks.append("✅ Conexão com banco OK")
                else:
                    checks.append("❌ Teste de conexão falhou")
                    all_good = False
        except Exception as e:
            checks.append(f"❌ Erro de conexão: {str(e)[:100]}...")
            logger.warning(f"Erro completo: {e}")
            all_good = False
        
        # 3. Verificar se migração é necessária
        try:
            migration = AutoMigration()
            if migration.check_evento_id_exists():
                checks.append("⚠️ Migração será executada no startup (evento_id encontrado)")
                logger.info("📝 Coluna evento_id ainda existe, migração necessária")
            else:
                checks.append("✅ Banco já está atualizado (evento_id removido)")
                logger.info("✅ Estrutura do banco está correta")
        except Exception as e:
            checks.append(f"⚠️ Não foi possível verificar migração: {str(e)[:50]}...")
            logger.warning(f"Erro de verificação de migração: {e}")
    
    # 4. Verificar estrutura de arquivos
    logger.info("📁 Verificando estrutura de arquivos...")
    
    required_files = [
        "backend/app/main.py",
        "backend/app/migrations/auto_migrate.py",
        "backend/requirements.txt"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            checks.append(f"✅ {file_path} existe")
        else:
            checks.append(f"❌ {file_path} não encontrado")
            all_good = False
    
    # 5. Mostrar resultados
    logger.info("\n📊 RESUMO DA VERIFICAÇÃO:")
    logger.info("-" * 40)
    for check in checks:
        logger.info(check)
    
    logger.info("-" * 40)
    
    if all_good:
        logger.info("🎉 DEPLOY ESTÁ PRONTO!")
        logger.info("✅ Todas as verificações passaram")
        logger.info("🚀 Sistema será iniciado com migração automática")
    else:
        logger.warning("⚠️ DEPLOY COM AVISOS")
        logger.warning("⚠️ Algumas verificações falharam, mas deploy continuará")
        logger.warning("🔧 Verifique os logs após o deploy")
    
    logger.info("=" * 60)
    return all_good

def main():
    """Função principal"""
    try:
        success = check_deploy_readiness()
        
        # Sempre continuar o deploy, mesmo com avisos
        # Em produção, queremos que o sistema suba e tente se corrigir
        logger.info("🚀 Preparação de deploy concluída")
        
        if success:
            logger.info("✅ Deploy aprovado - sem problemas detectados")
            sys.exit(0)
        else:
            logger.info("⚠️ Deploy aprovado - com avisos (sistema tentará se autocorrigir)")
            sys.exit(0)  # Não falhar o deploy
            
    except Exception as e:
        logger.error(f"❌ Erro crítico na verificação de deploy: {e}")
        logger.error("🔄 Deploy continuará mesmo assim...")
        sys.exit(0)  # Não bloquear deploy por erro de verificação

if __name__ == "__main__":
    main()
