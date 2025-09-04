#!/usr/bin/env python3

import sys
import os

# Adicionar o diretório backend ao path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.database import SessionLocal
from sqlalchemy import text

def verificar_estrutura_permissoes():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'permissoes' ORDER BY ordinal_position"))
        print("Estrutura da tabela 'permissoes':")
        print("=" * 60)
        print(f"{'Column':20} {'Type':20} {'Nullable':10}")
        print("-" * 60)
        for row in result:
            print(f"{row[0]:20} {row[1]:20} {row[2]:10}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_estrutura_permissoes()
