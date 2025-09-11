#!/usr/bin/env python
"""
Script para iniciar o servidor de desenvolvimento com configurações SQLite
"""

import os
import sys
import uvicorn

# Configurar ambiente para desenvolvimento
os.environ["DATABASE_URL"] = "sqlite:///./paineluniversal.db"
os.environ["CORS_DEVELOPMENT"] = "true"

if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO SERVIDOR DE DESENVOLVIMENTO")
    print("=" * 60)
    print("")
    print("Configuracoes:")
    print("  - Database: SQLite (paineluniversal.db)")
    print("  - CORS: Permissivo (desenvolvimento)")
    print("  - URL: http://localhost:8000")
    print("  - Docs: http://localhost:8000/docs")
    print("")
    print("=" * 60)
    
    # Iniciar servidor
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )