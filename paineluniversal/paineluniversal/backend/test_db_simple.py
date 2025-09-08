#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, engine
from app.models import Base, Usuario, Produto
from sqlalchemy.orm import sessionmaker

def test_simple_queries():
    """Teste simples das queries básicas"""
    print("🔍 Testando conexão simples com banco...")
    
    try:
        # Criar sessão
        db = SessionLocal()
        
        # Teste 1: Query simples de usuários
        print("1. Testando query de usuários...")
        usuario_count = db.query(Usuario).count()
        print(f"   ✅ Usuários encontrados: {usuario_count}")
        
        # Teste 2: Query simples de produtos
        print("2. Testando query de produtos...")
        produto_count = db.query(Produto).count()
        print(f"   ✅ Produtos encontrados: {produto_count}")
        
        # Teste 3: Buscar usuário específico
        print("3. Testando busca por CPF...")
        usuario = db.query(Usuario).filter(Usuario.cpf.like("%156%")).first()
        if usuario:
            print(f"   ✅ Usuário encontrado: {usuario.nome}")
        else:
            print("   ⚠️ Usuário não encontrado")
        
        db.close()
        print("✅ Todos os testes básicos passaram!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_queries()
