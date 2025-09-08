#!/usr/bin/env python3
"""
Debug do login - verificar se usuário existe e criar se necessário
"""

import sys
import os
sys.path.append('backend')

from backend.app.database import get_db, engine
from backend.app.models import Usuario
from sqlalchemy.orm import Session
import bcrypt

def verificar_criar_usuario():
    """Verificar se o usuário de teste existe, criar se necessário"""
    db = next(get_db())
    
    cpf = "06601206154"
    print(f"🔍 Verificando usuário com CPF: {cpf}")
    
    # Verificar se usuário existe
    usuario = db.query(Usuario).filter(Usuario.cpf == cpf).first()
    
    if usuario:
        print(f"✅ Usuário encontrado: {usuario.nome} - Tipo: {usuario.tipo_usuario}")
        print(f"📧 Email: {usuario.email}")
        print(f"🔑 Hash senha: {usuario.senha_hash[:20]}...")
        
        # Testar hash da senha
        senha_teste = "101112"
        if bcrypt.checkpw(senha_teste.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
            print("✅ Senha correta!")
        else:
            print("❌ Senha incorreta, atualizando...")
            # Atualizar senha
            novo_hash = bcrypt.hashpw(senha_teste.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            usuario.senha_hash = novo_hash
            db.commit()
            print("✅ Senha atualizada!")
    else:
        print("❌ Usuário não encontrado, criando...")
        
        # Criar usuário
        senha_hash = bcrypt.hashpw("101112".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        novo_usuario = Usuario(
            nome="Cesar Teste",
            email="cesar@teste.com", 
            cpf=cpf,
            senha_hash=senha_hash,
            tipo_usuario="ADMIN",
            ativo=True
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        print(f"✅ Usuário criado: {novo_usuario.nome} (ID: {novo_usuario.id})")
    
    db.close()

if __name__ == "__main__":
    print("🔧 Debug do sistema de login...")
    verificar_criar_usuario()
    print("✅ Debug concluído!")
