#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal
from app.auth import autenticar_usuario

def test_auth():
    """Teste específico da função de autenticação"""
    print("🔐 Testando função de autenticação...")
    
    db = SessionLocal()
    
    try:
        # Teste com CPF que teve problema
        cpf = "06600031156"
        senha = "123456"  # senha de exemplo
        
        print(f"Tentando autenticar CPF: {cpf}")
        resultado = autenticar_usuario(cpf, senha, db)
        
        if resultado:
            print(f"✅ Autenticação bem-sucedida para: {resultado.nome}")
        else:
            print("❌ Falha na autenticação (credenciais inválidas)")
            
    except Exception as e:
        print(f"❌ Erro durante autenticação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auth()
