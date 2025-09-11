#!/usr/bin/env python3
"""
DEPLOY FINAL PARA PRODUÇÃO RAILWAY
Script para aplicar a migração de remoção do tipo_usuario em produção
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_git_status():
    """Verificar status do git"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            logger.info("📝 Arquivos modificados encontrados:")
            logger.info(result.stdout)
            return True
        else:
            logger.info("✅ Working directory limpo")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao verificar git: {e}")
        return False

def commit_and_push():
    """Fazer commit e push das alterações"""
    try:
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit
        commit_message = f"feat: Remove campo tipo_usuario da tabela usuarios - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        logger.info("✅ Código enviado para o Railway")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro no git: {e}")
        return False

def main():
    """Deploy principal"""
    logger.info("🚀 DEPLOY FINAL - REMOÇÃO tipo_usuario EM PRODUÇÃO")
    logger.info("=" * 60)
    logger.info("Este script irá:")
    logger.info("1. Verificar mudanças no git")
    logger.info("2. Fazer commit e push para Railway")
    logger.info("3. Railway executará a migração automaticamente")
    logger.info("4. Verificar se deploy foi bem-sucedido")
    
    # Verificar mudanças
    has_changes = check_git_status()
    
    if has_changes:
        resposta = input("\n❓ Fazer commit e deploy das mudanças? (s/N): ").lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            logger.info("❌ Deploy cancelado")
            return False
        
        # Commit e push
        if not commit_and_push():
            return False
    else:
        logger.info("ℹ️ Nenhuma mudança para fazer deploy")
    
    logger.info("\n🎯 PRÓXIMOS PASSOS APÓS O DEPLOY:")
    logger.info("1. 🔍 Monitore os logs do Railway para ver a migração")
    logger.info("2. 🧪 Teste o login na aplicação")
    logger.info("3. 📊 Verifique se não há erros relacionados a tipo_usuario")
    logger.info("4. ✅ Se tudo funcionar, a migração foi bem-sucedida!")
    
    logger.info("\n📋 ALTERNATIVA - MIGRAÇÃO MANUAL:")
    logger.info("Se preferir executar manualmente no Railway Console:")
    logger.info("1. Abra o Railway Console (PostgreSQL)")
    logger.info("2. Execute o arquivo: railway_console_migration.sql")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n✅ Deploy iniciado com sucesso!")
        logger.info("🚂 Railway executará a migração automaticamente")
        sys.exit(0)
    else:
        logger.error("\n❌ Deploy falhou!")
        sys.exit(1)
