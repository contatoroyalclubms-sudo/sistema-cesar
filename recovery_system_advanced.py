#!/usr/bin/env python3
"""
🛡️ SISTEMA DE RECOVERY AVANÇADO PARA PAINELUNIVERSAL
Implementa múltiplas estratégias de conexão e recuperação automática
Preserva funcionalidades existentes com zero downtime
"""

import os
import sys
import time
import asyncio
import logging
import asyncpg
import psycopg2
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from app.migrations.auto_migrate import AutoMigration, DeployMonitoring
    EXISTING_SYSTEM_AVAILABLE = True
except ImportError:
    EXISTING_SYSTEM_AVAILABLE = False

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration_recovery.log')
    ]
)

logger = logging.getLogger("recovery_system")

@dataclass
class ConnectionAttempt:
    """Representa uma tentativa de conexão"""
    strategy: str
    url: str
    success: bool
    duration: float
    error: Optional[str] = None

@dataclass
class MigrationResult:
    """Resultado de uma migração"""
    strategy: str
    success: bool
    duration: float
    operations_completed: List[str]
    errors: List[str]

class ConnectionStrategy:
    """Estratégias de conexão com PostgreSQL"""
    
    @staticmethod
    def get_railway_urls() -> List[str]:
        """Obtém URLs do Railway de diferentes fontes"""
        urls = []
        
        # URL principal do ambiente
        main_url = os.getenv("DATABASE_URL")
        if main_url:
            urls.append(main_url)
        
        # URLs alternativas conhecidas (mascaradas para segurança)
        alternative_urls = [
            os.getenv("POSTGRES_URL"),
            os.getenv("DATABASE_PRIVATE_URL"),
            os.getenv("DATABASE_PUBLIC_URL"),
        ]
        
        # Filtrar URLs válidas
        urls.extend([url for url in alternative_urls if url])
        
        # Normalizar URLs postgres:// -> postgresql://
        normalized_urls = []
        for url in urls:
            if url.startswith("postgres://"):
                normalized_urls.append(url.replace("postgres://", "postgresql://", 1))
            else:
                normalized_urls.append(url)
        
        return list(set(normalized_urls))  # Remove duplicatas
    
    @staticmethod
    async def try_asyncpg_connection(url: str, timeout: int = 30) -> ConnectionAttempt:
        """Tenta conexão com asyncpg"""
        start_time = time.time()
        
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(url),
                timeout=timeout
            )
            await conn.close()
            
            duration = time.time() - start_time
            logger.info(f"✅ asyncpg conexão bem-sucedida em {duration:.2f}s")
            
            return ConnectionAttempt(
                strategy="asyncpg",
                url=url[:50] + "...",  # Mascarar URL
                success=True,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.warning(f"❌ asyncpg falhou em {duration:.2f}s: {e}")
            
            return ConnectionAttempt(
                strategy="asyncpg",
                url=url[:50] + "...",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    @staticmethod
    def try_psycopg2_connection(url: str, timeout: int = 30) -> ConnectionAttempt:
        """Tenta conexão com psycopg2"""
        start_time = time.time()
        
        try:
            conn = psycopg2.connect(url, connect_timeout=timeout)
            conn.close()
            
            duration = time.time() - start_time
            logger.info(f"✅ psycopg2 conexão bem-sucedida em {duration:.2f}s")
            
            return ConnectionAttempt(
                strategy="psycopg2",
                url=url[:50] + "...",
                success=True,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.warning(f"❌ psycopg2 falhou em {duration:.2f}s: {e}")
            
            return ConnectionAttempt(
                strategy="psycopg2",
                url=url[:50] + "...",
                success=False,
                duration=duration,
                error=str(e)
            )

class RecoverySystem:
    """Sistema de recuperação automática com múltiplas estratégias"""
    
    def __init__(self):
        self.logger = logging.getLogger("recovery")
        self.connection_attempts: List[ConnectionAttempt] = []
        self.migration_results: List[MigrationResult] = []
        
    async def test_all_connections(self) -> Optional[str]:
        """Testa todas as estratégias de conexão disponíveis"""
        self.logger.info("🔍 Testando conectividade PostgreSQL...")
        
        urls = ConnectionStrategy.get_railway_urls()
        if not urls:
            self.logger.error("❌ Nenhuma URL de banco encontrada")
            return None
        
        self.logger.info(f"📋 Testando {len(urls)} URL(s) de conexão")
        
        for url in urls:
            # Testar asyncpg
            attempt = await ConnectionStrategy.try_asyncpg_connection(url)
            self.connection_attempts.append(attempt)
            
            if attempt.success:
                self.logger.info(f"✅ Conexão bem-sucedida: {attempt.strategy}")
                return url
            
            # Testar psycopg2
            attempt = ConnectionStrategy.try_psycopg2_connection(url)
            self.connection_attempts.append(attempt)
            
            if attempt.success:
                self.logger.info(f"✅ Conexão bem-sucedida: {attempt.strategy}")
                return url
            
            # Delay entre tentativas
            await asyncio.sleep(2)
        
        self.logger.error("❌ Todas as tentativas de conexão falharam")
        return None
    
    def use_existing_auto_migration(self) -> bool:
        """Usa o sistema de auto-migração existente"""
        if not EXISTING_SYSTEM_AVAILABLE:
            self.logger.warning("⚠️ Sistema de auto-migração não disponível")
            return False
        
        try:
            self.logger.info("🔧 Usando sistema de auto-migração existente...")
            
            # Usar o sistema existente que já é robusto
            from app.migrations.auto_migrate import run_auto_migration
            
            success = run_auto_migration()
            
            if success:
                self.logger.info("✅ Migração automática bem-sucedida")
                return True
            else:
                self.logger.error("❌ Migração automática falhou")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro no sistema de auto-migração: {e}")
            return False
    
    def generate_manual_sql_script(self) -> str:
        """Gera script SQL para execução manual no Railway Console"""
        sql_script = """
-- 🛠️ SCRIPT DE RECOVERY MANUAL - RAILWAY CONSOLE
-- Execute este script diretamente no Railway PostgreSQL Console

BEGIN;

-- 1. CORREÇÃO ENUM TIPOUSUARIO
DO $$
BEGIN
    -- Criar enum se não existir
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipousuario') THEN
        CREATE TYPE tipousuario AS ENUM ('admin', 'promoter', 'cliente');
        RAISE NOTICE 'Enum tipousuario criado';
    END IF;
    
    -- Adicionar valores lowercase se necessário
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'admin';
        RAISE NOTICE 'Valor admin adicionado';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Valor admin já existe';
    END;
    
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'promoter';
        RAISE NOTICE 'Valor promoter adicionado';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Valor promoter já existe';
    END;
    
    BEGIN
        ALTER TYPE tipousuario ADD VALUE IF NOT EXISTS 'cliente';
        RAISE NOTICE 'Valor cliente adicionado';
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Valor cliente já existe';
    END;
END $$;

-- 2. CORRIGIR USUÁRIOS COM CASE MISMATCH
UPDATE usuarios SET tipo = 'admin' WHERE tipo = 'ADMIN';
UPDATE usuarios SET tipo = 'promoter' WHERE tipo = 'PROMOTER';
UPDATE usuarios SET tipo = 'cliente' WHERE tipo = 'CLIENTE';

-- 3. MIGRAÇÃO TABELA PRODUTOS (SE NECESSÁRIO)
DO $$
BEGIN
    -- Verificar se evento_id existe
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'produtos' AND column_name = 'evento_id'
    ) THEN
        RAISE NOTICE 'Coluna evento_id encontrada, removendo...';
        
        -- Backup
        EXECUTE 'CREATE TABLE produtos_backup_' || TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS') || ' AS SELECT * FROM produtos';
        RAISE NOTICE 'Backup criado';
        
        -- Remover coluna
        ALTER TABLE produtos DROP COLUMN evento_id;
        RAISE NOTICE 'Coluna evento_id removida';
        
        -- Recriar índices
        CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);
        CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo);
        CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status);
        
        RAISE NOTICE 'Índices recriados';
    ELSE
        RAISE NOTICE 'Coluna evento_id não encontrada, migração não necessária';
    END IF;
END $$;

-- 4. VALIDAÇÃO
SELECT 'ENUM_VALUES' as tipo, enumlabel as valor 
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipousuario')
ORDER BY enumsortorder;

SELECT 'PRODUTOS_COUNT' as tipo, COUNT(*) as valor FROM produtos;

SELECT 'USUARIOS_TIPOS' as tipo, tipo, COUNT(*) as valor 
FROM usuarios 
GROUP BY tipo;

COMMIT;

-- ✅ SCRIPT CONCLUÍDO
SELECT '✅ RECOVERY MANUAL CONCLUÍDO COM SUCESSO' as status;
"""
        return sql_script
    
    async def run_comprehensive_recovery(self) -> bool:
        """Executa recovery abrangente com múltiplas estratégias"""
        self.logger.info("🚀 Iniciando recovery abrangente do sistema...")
        
        start_time = time.time()
        
        # Estratégia 1: Testar conectividade
        working_url = await self.test_all_connections()
        
        if working_url:
            self.logger.info("✅ Conectividade PostgreSQL funcionando")
            
            # Estratégia 2: Usar sistema existente (preferencial)
            if self.use_existing_auto_migration():
                duration = time.time() - start_time
                self.logger.info(f"🎉 Recovery bem-sucedido em {duration:.2f}s")
                return True
        
        # Estratégia 3: Fallback para script manual
        self.logger.warning("⚠️ Conectividade falhou, gerando script manual...")
        
        script = self.generate_manual_sql_script()
        script_path = "railway_manual_recovery.sql"
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        self.logger.info(f"📝 Script manual gerado: {script_path}")
        self.logger.info("🔧 Execute o script no Railway Console para recovery manual")
        
        return False
    
    def generate_recovery_report(self) -> str:
        """Gera relatório detalhado do recovery"""
        report = f"""
# 📊 RELATÓRIO DE RECOVERY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 TENTATIVAS DE CONEXÃO
"""
        
        for attempt in self.connection_attempts:
            status = "✅" if attempt.success else "❌"
            report += f"- {status} {attempt.strategy}: {attempt.duration:.2f}s"
            if attempt.error:
                report += f" (Erro: {attempt.error[:100]}...)"
            report += "\n"
        
        report += f"""
## 📈 RESULTADOS DE MIGRAÇÃO
"""
        
        for result in self.migration_results:
            status = "✅" if result.success else "❌"
            report += f"- {status} {result.strategy}: {result.duration:.2f}s\n"
            if result.operations_completed:
                report += f"  Operações: {', '.join(result.operations_completed)}\n"
            if result.errors:
                report += f"  Erros: {', '.join(result.errors)}\n"
        
        return report

def main():
    """Executa recovery do sistema"""
    print("🛡️ SISTEMA DE RECOVERY PAINELUNIVERSAL")
    print("=" * 50)
    
    recovery = RecoverySystem()
    
    try:
        # Executar recovery
        success = asyncio.run(recovery.run_comprehensive_recovery())
        
        # Gerar relatório
        report = recovery.generate_recovery_report()
        
        with open("recovery_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        if success:
            print("✅ RECOVERY CONCLUÍDO COM SUCESSO!")
            print("📊 Relatório: recovery_report.md")
            return 0
        else:
            print("⚠️ RECOVERY PARCIAL - Script manual gerado")
            print("📝 Execute railway_manual_recovery.sql no Railway Console")
            print("📊 Relatório: recovery_report.md")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Erro fatal no recovery: {e}")
        print(f"❌ ERRO FATAL: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
