#!/usr/bin/env python3
"""
Teste direto da criação de usuário no banco local
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import get_db
from app.models import Usuario, TipoUsuario
from app.auth import gerar_hash_senha
from sqlalchemy.orm import Session

def test_create_user_direct():
    """Testar criação de usuário diretamente no banco"""
    
    print("🧪 Testando criação de usuário diretamente no banco...")
    
    # Obter conexão com banco
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Dados do usuário
        cpf = "98765432100"
        nome = "Teste Direto"
        email = "teste.direto@example.com"
        senha = "senha123"
        
        # Verificar se já existe
        usuario_existente = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        if usuario_existente:
            print(f"ℹ️ Usuário já existe: {usuario_existente.nome}")
            return
            
        # Criar hash da senha
        senha_hash = gerar_hash_senha(senha)
        
        # Criar usuário
        novo_usuario = Usuario(
            cpf=cpf,
            nome=nome,
            email=email,
            telefone="11999999999",
            senha_hash=senha_hash,
            tipo=TipoUsuario.CLIENTE,
            ativo=True
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   ID: {novo_usuario.id}")
        print(f"   Nome: {novo_usuario.nome}")
        print(f"   CPF: {novo_usuario.cpf}")
        print(f"   Email: {novo_usuario.email}")
        print(f"   Tipo: {novo_usuario.tipo}")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_create_user_direct()
