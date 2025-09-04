#!/usr/bin/env python3
"""
Script para regenerar as tabelas e limpar possíveis problemas de metadados
"""
import sys
import os

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine
from app.models import Base
from sqlalchemy import MetaData

def rebuild_metadata():
    """Regenera os metadados das tabelas"""
    print("🔄 Regenerando metadados das tabelas...")
    
    try:
        # Limpar metadados existentes
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        print(f"Tabelas detectadas: {list(metadata.tables.keys())}")
        
        # Recriar metadados usando os modelos
        print("Criando metadados dos modelos...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Metadados regenerados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao regenerar metadados: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    rebuild_metadata()
