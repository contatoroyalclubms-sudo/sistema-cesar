#!/usr/bin/env python3
"""
Script de teste para rotas KDS/Mesas
"""
import sys
import os
import requests
import json
from datetime import datetime

# Configure UTF-8 encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_backend_health():
    """Teste de saúde do backend"""
    try:
        # Primeiro verifica se o backend está rodando
        response = requests.get('http://localhost:8000', timeout=5)
        print(f"Backend está rodando (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("Backend não está rodando em localhost:8000")
        return False
    except Exception as e:
        print(f"Erro ao conectar no backend: {e}")
        return False

def test_database_tables():
    """Teste das tabelas no banco"""
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Verifica se as tabelas KDS/Mesas existem (PostgreSQL)
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' AND (tablename LIKE '%kds%' OR tablename LIKE '%mesa%')"))
            tables = result.fetchall()
            table_names = [t[0] for t in tables]
            
            # Se não encontrar nenhuma, tenta SQLite
            if not table_names:
                try:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%kds%' OR name LIKE '%mesa%')"))
                    tables = result.fetchall()
                    table_names = [t[0] for t in tables]
                except:
                    pass
            
            print("Tabelas KDS/Mesas encontradas:")
            for table in table_names:
                print(f"  {table}")
                
            # Verifica estrutura específica
            if 'estacoes_kds' in table_names:
                result = conn.execute(text("PRAGMA table_info(estacoes_kds)"))
                columns = result.fetchall()
                print(f"  Colunas estacoes_kds: {len(columns)} colunas")
                
            if 'mesas_evento' in table_names:
                result = conn.execute(text("PRAGMA table_info(mesas_evento)"))
                columns = result.fetchall()
                print(f"  Colunas mesas_evento: {len(columns)} colunas")
                
            return len(table_names) > 0
            
    except Exception as e:
        print(f"Erro ao verificar tabelas: {e}")
        return False

def test_router_imports():
    """Teste de importação dos routers"""
    try:
        from app.routers import kds, mesas
        from app.main import app
        
        print("Routers KDS/Mesas importados com sucesso")
        
        # Verifica se os routers estão registrados
        routes = [route.path for route in app.routes]
        kds_routes = [r for r in routes if '/api/kds' in r]
        mesas_routes = [r for r in routes if '/api/mesas' in r]
        
        print(f"  Rotas KDS encontradas: {len(kds_routes)}")
        print(f"  Rotas Mesas encontradas: {len(mesas_routes)}")
        
        return len(kds_routes) > 0 and len(mesas_routes) > 0
        
    except Exception as e:
        print(f"Erro ao importar routers: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE DAS ROTAS KDS/MESAS")
    print("=" * 60)
    
    results = []
    
    print("\n1. Teste de importação dos routers:")
    results.append(test_router_imports())
    
    print("\n2. Teste das tabelas do banco:")
    results.append(test_database_tables())
    
    print("\n3. Teste de conectividade do backend:")
    results.append(test_backend_health())
    
    print("\n" + "=" * 60)
    print("RESULTADO DOS TESTES")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Testes aprovados: {passed}/{total}")
    
    if passed == total:
        print("Todos os testes passaram! Sistema KDS/Mesas está funcional.")
    else:
        print("Alguns testes falharam. Verifique os detalhes acima.")
    
    return passed == total

if __name__ == "__main__":
    main()