#!/usr/bin/env python3
"""
Inicializa o banco de dados PostgreSQL na Railway.
"""
import os
import sys

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import engine
    from app.models import Base
    
    print("🗄️ Criando tabelas no PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
    print("ℹ️ As tabelas serão criadas automaticamente na primeira requisição.")
    sys.exit(0)  # Não falha o deploy, apenas continua