#!/usr/bin/env python3
"""
Script otimizado para inicialização do backend em produção
"""
import os
import sys
import uvicorn
import logging

# Importar app para verificar se tudo está funcionando
try:
    from app.main import app
    logger = logging.getLogger(__name__)
    logger.info("✅ Aplicação importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar aplicação: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def start_server():
    """Iniciar servidor backend"""
    try:
        logger.info("🚀 Iniciando Sistema Universal - Backend...")
        logger.info("📧 Modo: TESTE (emails no console)")
        logger.info("🔧 Configurações carregadas")
        
        # Configurações do servidor
        config = {
            "app": "app.main:app",
            "host": "0.0.0.0",
            "port": int(os.getenv("PORT", 8000)),
            "log_level": "info",
            "access_log": True
        }
        
        # Em produção, não usar reload
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PRODUCTION"):
            logger.info("🌐 Modo: PRODUÇÃO")
            config["reload"] = False
        else:
            logger.info("🛠️  Modo: DESENVOLVIMENTO")
            config["reload"] = True
        
        # Iniciar servidor
        uvicorn.run(**config)
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
