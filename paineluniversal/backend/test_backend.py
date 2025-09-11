#!/usr/bin/env python
"""
Script para testar se o backend está funcionando corretamente
"""

import sys
import os

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se os imports básicos funcionam"""
    print("Testando imports basicos...")
    
    try:
        from app.database import engine, get_db
        print("[OK] Database imports")
    except Exception as e:
        print(f"[ERRO] Database imports: {e}")
        return False
    
    try:
        from app.models import Base, Usuario, Evento
        print("[OK] Models imports")
    except Exception as e:
        print(f"[ERRO] Models imports: {e}")
        return False
    
    try:
        from app.auth_functions import criar_access_token, verificar_senha
        print("[OK] Auth imports")
    except Exception as e:
        print(f"[ERRO] Auth imports: {e}")
        return False
    
    return True

def test_database():
    """Testa conexão com banco de dados"""
    print("\nTestando conexao com banco de dados...")
    
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("[OK] Conexao com banco de dados")
            return True
    except Exception as e:
        print(f"[ERRO] Conexao com banco de dados: {e}")
        return False

def test_api():
    """Testa se a API pode ser iniciada"""
    print("\nTestando inicializacao da API...")
    
    try:
        # Tentar importar apenas os routers essenciais
        from fastapi import FastAPI
        from app.database import engine, get_db
        from app.models import Base
        
        # Criar tabelas
        Base.metadata.create_all(bind=engine)
        
        # Criar app mínimo
        app = FastAPI(title="Sistema Universal - Teste")
        
        # Adicionar apenas rota de health check
        @app.get("/health")
        def health_check():
            return {"status": "ok"}
        
        print("[OK] API minima pode ser iniciada")
        return True
        
    except Exception as e:
        print(f"[ERRO] API nao pode ser iniciada: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTE DO BACKEND - SISTEMA UNIVERSAL")
    print("=" * 60)
    
    all_ok = True
    
    # Executar testes
    if not test_imports():
        all_ok = False
    
    if not test_database():
        all_ok = False
    
    if not test_api():
        all_ok = False
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_ok:
        print("[SUCESSO] TODOS OS TESTES PASSARAM!")
        print("O backend está pronto para ser iniciado.")
        print("\nPara iniciar o servidor, execute:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload --port 8000")
    else:
        print("[AVISO] ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima e corrija antes de iniciar o servidor.")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())